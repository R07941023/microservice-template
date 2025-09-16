from fastapi import FastAPI, Header, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
import asyncpg
import logging
import asyncio

from utils.auth import decode_jwt_from_header
from models import ChatRequest, User
from config import settings
from services.llm_client import LLMClient
from services.rag_service import RAGService

# --- App State ---

class AppState:
    db_pool: asyncpg.Pool = None
    llm_client: LLMClient = None
    rag_service: RAGService = None
    maplestory_user_id: int = None

app_state = AppState()

# --- Logging ---

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- App Initialization ---

app = FastAPI()

@app.on_event("startup")
async def startup():
    logger.info("Starting up application...")
    try:
        # Initialize LLM Client
        app_state.llm_client = LLMClient(
            host=settings.ollama_endpoint, 
            embedding_model=settings.embedding_model
        )
        logger.info(f"Ollama client initialized for endpoint: {settings.ollama_endpoint}")

        # Initialize Database Pool
        app_state.db_pool = await asyncpg.create_pool(settings.postgres_uri)
        logger.info("Database connection pool created successfully.")

        # Initialize RAG Service
        app_state.rag_service = RAGService(app_state.db_pool, app_state.llm_client)
        logger.info("RAG service initialized.")

        # Get default user ID
        async with app_state.db_pool.acquire() as connection:
            user_row = await connection.fetchrow("SELECT id FROM users WHERE username = $1", settings.maplestory_user_name)
            if user_row:
                app_state.maplestory_user_id = user_row['id']
                logger.info(f"Found user '{settings.maplestory_user_name}' with id: {app_state.maplestory_user_id}")
            else:
                logger.warning(f"Default user '{settings.maplestory_user_name}' not found.")

    except Exception as e:
        logger.error(f"Failed during startup: {e}", exc_info=True)
        # Optionally, re-raise or handle to prevent app from starting in a bad state
        raise

@app.on_event("shutdown")
async def shutdown():
    if app_state.db_pool:
        await app_state.db_pool.close()
        logger.info("Database connection pool closed.")

# --- Dependencies ---

def get_rag_service() -> RAGService:
    return app_state.rag_service

async def get_current_user(authorization: str | None = Header(default=None)) -> User:
    _, user_email = decode_jwt_from_header(authorization)
    async with app_state.db_pool.acquire() as connection:
        async with connection.transaction():
            result = await connection.fetchrow(
                "INSERT INTO users (username) VALUES ($1) ON CONFLICT (username) DO UPDATE SET username=EXCLUDED.username RETURNING id;", 
                user_email
            )
            user_id = result['id']
    return User(id=user_id, email=user_email)

# --- Stream Generator ---

async def stream_chat_generator(
    prompt: str, 
    model: str, 
    user: User, 
    background_tasks: BackgroundTasks,
    rag_service: RAGService
):
    response_chunks = []
    try:
        # 1. Retrieve RAG context
        maple_context, history_context = await asyncio.gather(
            rag_service.retrieve_rag_context(prompt, app_state.maplestory_user_id),
            rag_service.retrieve_rag_context(prompt, user.id)
        )

        # 2. Construct messages for the LLM
        messages = [
            {
                'role': 'system',
                'content': f"""You are a helpful assistant. Use the following context to answer the user's question.
                    --- DATABASE CONTEXT ---
                    {maple_context}
                    --- END DATABASE CONTEXT ---
                    --- HISTORY CONTEXT ---
                    {history_context}
                    --- END HISTORY CONTEXT ---"""
            },
            {'role': 'user', 'content': prompt}
        ]
        logger.info(messages)

        
        # 3. Stream response from LLM
        logger.info(f"Streaming response for user {user.id} using model: {model}")
        llm_stream = rag_service.llm_client.stream_chat(model=model, messages=messages)
        
        async for chunk in llm_stream:
            response_chunks.append(chunk)
            yield chunk
            await asyncio.sleep(0)

    except Exception as e:
        error_message = f"Error during chat generation: {e}"
        logger.error(error_message, exc_info=True)
        yield f"Error: An unexpected error occurred."
    finally:
        # 4. Save chat history in the background
        full_response = "".join(response_chunks)
        if full_response:
            background_tasks.add_task(rag_service.save_chat_history, user.id, prompt, full_response)

# --- API Endpoints ---

@app.post("/stream-chat")
async def stream_chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service)
):
    """API endpoint to stream chat responses from Ollama, with RAG."""
    generator = stream_chat_generator(
        prompt=request.prompt, 
        model=request.model or settings.default_chat_model, 
        user=user, 
        background_tasks=background_tasks,
        rag_service=rag_service
    )
    return StreamingResponse(generator, media_type="text/plain")