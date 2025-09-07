from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import ollama
import asyncio
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://host.docker.internal:11434")

class ChatRequest(BaseModel):
    prompt: str
    model: str = 'gpt-oss:20b' # Default model, can be overridden by request

async def stream_chat_generator(prompt: str, model: str):
    """This async generator streams responses from the Ollama client."""
    try:
        # As per user request, using host.docker.internal to connect to Ollama on the host
        client = ollama.AsyncClient(host=ollama_endpoint)
        
        logger.info(f"Streaming response for prompt: '{prompt}' using model: {model}")
        
        async for part in await client.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=True
        ):
            chunk = part['message']['content']
            yield chunk
            await asyncio.sleep(0) # Allows other tasks to run

        logger.info(f"Finished streaming for prompt: '{prompt}'")

    except Exception as e:
        error_message = f"Error while streaming from Ollama: {e}"
        logger.error(error_message, exc_info=True)
        yield f"Error: {e}" # Yield an error message to the client

@app.post("/stream-chat")
async def stream_chat(request: ChatRequest):
    """API endpoint to stream chat responses from Ollama."""
    return StreamingResponse(
        stream_chat_generator(request.prompt, request.model),
        media_type="text/plain"
    )
