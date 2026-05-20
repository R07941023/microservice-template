"""LLM orchestrator microservice for chat streaming with LangChain agents."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langfuse import get_client as get_langfuse_client
from langfuse.langchain import CallbackHandler
from mem0 import Memory

from config import settings
from models import ChatRequest
from tools.memory import add_memory, build_mem0_client, build_system_prompt, search_memories
from utils.auth import User, get_current_user
from utils.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppState:
    """Application state container for shared resources."""

    langchain_agent: object = None
    memory_client: Memory = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan.

    Sets up MCP client with tools, LangChain agent, and mem0 memory client on startup.
    Cleans up resources on shutdown.

    Args:
        app: FastAPI application instance.

    Yields:
        None after successful initialization.

    Raises:
        Exception: If any initialization step fails.
    """
    logger.info("Starting up application...")
    try:
        # 1. Initialize MCP Client and Tools
        client = MultiServerMCPClient(
            {
                "weather": {
                    "transport": "streamable_http",
                    "url": settings.mcp_host,
                    "headers": {
                        "Authorization": f"Bearer {settings.mcp_token}",
                        "Accept": "application/json"
                    }
                }
            }
        )
        tools = await client.get_tools()
        logger.info("MCP Client initialized. Tools: %s", [t.name for t in tools])

        # 2. Initialize LLM
        llm = ChatOpenAI(
            openai_api_base=settings.litellm_host,
            temperature=0,
            model=settings.default_chat_model,
            streaming=True
        )
        app_state.langchain_agent = create_agent(llm, tools=tools)
        logger.info("LangChain LangGraph Agent initialized.")

        # 3. Initialize mem0 Memory client
        app_state.memory_client = await asyncio.to_thread(build_mem0_client, settings)
        logger.info("mem0 Memory client initialized.")

    except Exception as e:
        logger.error("Failed during startup: %s", e, exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)


async def stream_chat_generator(
    prompt: str,
    user: User,
    background_tasks: BackgroundTasks,
    history: list = None,
    session_id: str = None,
):
    """
    Stream chat responses using LangGraph agent.

    Searches mem0 long-term memory before streaming to inject relevant context,
    then saves the full conversation after streaming completes.

    Args:
        prompt: User's chat prompt.
        user: Current authenticated user.
        background_tasks: FastAPI background tasks.
        history: Recent conversation turns to include as context.
        session_id: Frontend session ID for LangGraph thread and Langfuse session grouping.

    Yields:
        str: Streamed message content tokens.
    """
    search_result = await search_memories(app_state.memory_client, prompt, session_id)
    system_prompt = build_system_prompt(settings.system_prompt_template, search_result)

    _role_map = {"user": HumanMessage, "assistant": AIMessage}
    history_messages = [
        _role_map[msg.role](content=msg.content)
        for msg in (history or [])
        if msg.role in _role_map
    ]

    input_data = {"messages": [SystemMessage(content=system_prompt), *history_messages, HumanMessage(content=prompt)]}
    logger.info("User %s streaming chat via LangGraph messages mode.", user.name)

    langfuse_client = get_langfuse_client()
    response_tokens: list[str] = []

    with langfuse_client.start_as_current_span(name="stream-chat"):
        langfuse_client.update_current_trace(session_id=session_id, user_id=user.name)
        trace_id = langfuse_client.get_current_trace_id()
        langfuse_handler = CallbackHandler(trace_context={"trace_id": trace_id})

        try:
            async for message, metadata in app_state.langchain_agent.astream(
                input_data,
                config={
                    "configurable": {"thread_id": session_id},
                    "callbacks": [langfuse_handler],
                },
                stream_mode="messages"
            ):
                if metadata.get("langgraph_node") == "model":
                    token = str(message.content)
                    response_tokens.append(token)
                    yield token
                    await asyncio.sleep(0)

        except Exception as e:
            logger.error("Error during chat generation for user %s: %s", user.name, e, exc_info=True)
            yield "\n[Error]: streaming!"
            return

    background_tasks.add_task(add_memory, app_state.memory_client, prompt, "".join(response_tokens), session_id)


@app.post("/stream-chat")
async def stream_chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """
    Stream chat responses from LangChain agent.

    Args:
        request: Chat request with prompt.
        background_tasks: FastAPI background tasks.
        user: Current authenticated user from JWT.

    Returns:
        StreamingResponse with text/event-stream media type.
    """
    logger.info("User %s requesting stream-chat with prompt: %s...", user.name, request.prompt[:50])

    if not app_state.langchain_agent:
        return {"error": "Agent not initialized"}

    generator = stream_chat_generator(
        prompt=request.prompt,
        user=user,
        background_tasks=background_tasks,
        history=request.history,
        session_id=request.session_id,
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream"
    )


@app.get("/health/ready")
async def readiness() -> dict:
    """
    Readiness probe endpoint.

    Checks if LangChain agent is initialized.

    Returns:
        Status dict with dependency states.

    Raises:
        HTTPException: 503 if agent is not initialized.
    """
    if not app_state.langchain_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    return {
        "status": "ready",
        "agent": "initialized",
    }
