"""LLM orchestrator microservice for chat streaming with LangChain agents."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler
from mem0 import Memory

from config import settings
from models import ChatRequest
from tools.memory import add_memory, build_mem0_client, build_system_prompt, get_user_id, search_memories
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
    model: str,
    user: User,
    background_tasks: BackgroundTasks
):
    """
    Stream chat responses using LangGraph agent.

    Searches mem0 long-term memory before streaming to inject relevant context,
    then saves the full conversation after streaming completes.

    Args:
        prompt: User's chat prompt.
        model: LLM model name to use.
        user: Current authenticated user.
        background_tasks: FastAPI background tasks.

    Yields:
        str: Streamed message content tokens.
    """
    user_id = get_user_id(user.name)
    search_result = await search_memories(app_state.memory_client, prompt, user_id)
    system_prompt = build_system_prompt(settings.system_prompt_template, search_result)

    input_data = {"messages": [SystemMessage(content=system_prompt), HumanMessage(content=prompt)]}
    logger.info("User %s streaming chat via LangGraph messages mode.", user.name)

    # Per-request handler so concurrent requests each get isolated Langfuse traces
    langfuse_handler = CallbackHandler()

    response_tokens: list[str] = []
    try:
        async for message, metadata in app_state.langchain_agent.astream(
            input_data,
            config={"callbacks": [langfuse_handler]},
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

    background_tasks.add_task(add_memory, app_state.memory_client, prompt, "".join(response_tokens), user_id)


@app.post("/stream-chat")
async def stream_chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """
    Stream chat responses from LangChain agent.

    Args:
        request: Chat request with prompt and optional model.
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
        model=request.model or settings.default_chat_model,
        user=user,
        background_tasks=background_tasks,
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
