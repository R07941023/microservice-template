import asyncpg
import logging
import asyncio
import os

from fastapi import FastAPI, Header, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse

from utils.auth import decode_jwt_from_header
from models import ChatRequest, User
from config import settings

from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# Langfuse for tracing
from langfuse.langchain import CallbackHandler

# --- App State ---

class AppState:
    langchain_agent: object = None 
    langfuse_handler: CallbackHandler = None

app_state = AppState()

# --- Logging ---

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Initialization ---

app = FastAPI()

# Load environment variables
MCP_TOKEN = os.getenv("MCP_TOKEN", None)

@app.on_event("startup")
async def startup():
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
                        "Authorization": f"Bearer {MCP_TOKEN}",
                        "Accept": "application/json"
                    }
                }
            }
        )
        tools = await client.get_tools()
        logger.info(f"MCP Client initialized. Tools: {[t.name for t in tools]}")

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
        logger.error(f"Failed during startup: {e}", exc_info=True)
        raise

# --- Dependencies ---

async def get_current_user(authorization: str | None = Header(default=None)) -> User:
    user_name, user_email = decode_jwt_from_header(authorization)
    return User(name=user_name, email=user_email)

# --- Stream Generator ---

async def stream_chat_generator(
    prompt: str, 
    model: str, 
    user: User, 
    background_tasks: BackgroundTasks
):
    """
    根據最新文件，使用 astream(stream_mode="messages") 來獲取 Token。
    """
    try:
        input_data = {"messages": [HumanMessage(content=prompt)]}
        logger.info(f"Streaming for user {user.name} via LangGraph 'messages' mode.")
        async for message, metadata in app_state.langchain_agent.astream(
            input_data, 
            config={"callbacks": [app_state.langfuse_handler]},
            stream_mode="messages"
        ):
            if metadata.get("langgraph_node") == "model": # model/tool
                yield str(message.content)
                await asyncio.sleep(0)

    except Exception as e:
        logger.error(f"Error during chat generation: {e}", exc_info=True)
        yield f"\n[Error]: streaming!"

# --- API Endpoints ---

@app.post("/stream-chat")
async def stream_chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
):
    """
    API endpoint to stream chat responses from LiteLLM.
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