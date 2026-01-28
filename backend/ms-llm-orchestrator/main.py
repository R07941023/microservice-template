"""LLM orchestrator microservice for chat streaming with LangChain agents."""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langfuse.langchain import CallbackHandler

from config import settings
from models import ChatRequest, User
from utils.auth import verify_jwt_from_header
from utils.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppState:
    """Application state container for shared resources."""

    langchain_agent: object = None
    langfuse_handler: CallbackHandler = None


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan.

    Sets up Langfuse handler, MCP client with tools, and LangChain agent on startup.
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
        # 1. Initialize Langfuse
        app_state.langfuse_handler = CallbackHandler()
        logger.info("Langfuse CallbackHandler initialized.")

        # 2. Initialize MCP Client and Tools
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

        # 3. Initialize LLM
        llm = ChatOpenAI(
            openai_api_base=settings.litellm_host,
            temperature=0,
            model=settings.default_chat_model,
            streaming=True
        )
        app_state.langchain_agent = create_agent(
            llm,
            tools=tools,
            system_prompt=settings.system_prompt
        )
        logger.info("LangChain LangGraph Agent initialized.")

    except Exception as e:
        logger.error("Failed during startup: %s", e, exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)


async def get_current_user(authorization: str | None = Header(default=None)) -> User:
    """
    Verify JWT and extract current user from authorization header.

    Args:
        authorization: JWT authorization header value.

    Returns:
        User object with name and email from JWT claims.

    Raises:
        HTTPException: 401 if token is invalid or missing.
    """
    token_data = verify_jwt_from_header(
        authorization,
        jwks_url=settings.jwks_url,
        issuer=settings.keycloak_realm_url,
        audience=settings.jwt_audience,
    )

    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    return User(
        name=token_data.get("name") or token_data.get("preferred_username"),
        email=token_data.get("email"),
    )

async def stream_chat_generator(
    prompt: str,
    model: str,
    user: User,
    background_tasks: BackgroundTasks
):
    """
    Stream chat responses using LangGraph agent.

    Uses astream with stream_mode="messages" to get tokens.

    Args:
        prompt: User's chat prompt.
        model: LLM model name to use.
        user: Current authenticated user.
        background_tasks: FastAPI background tasks.

    Yields:
        str: Streamed message content tokens.
    """
    try:
        input_data = {"messages": [HumanMessage(content=prompt)]}
        logger.info("Streaming for user %s via LangGraph messages mode.", user.name)
        async for message, metadata in app_state.langchain_agent.astream(
            input_data,
            config={"callbacks": [app_state.langfuse_handler]},
            stream_mode="messages"
        ):
            if metadata.get("langgraph_node") == "model":
                yield str(message.content)
                await asyncio.sleep(0)

    except Exception as e:
        logger.error("Error during chat generation: %s", e, exc_info=True)
        yield "\n[Error]: streaming!"

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