import ollama
from typing import AsyncGenerator, List, Dict

class LLMClient:
    def __init__(self, host: str, embedding_model: str):
        self.client = ollama.AsyncClient(host=host)
        self.embedding_model = embedding_model

    async def generate_embedding(self, prompt: str) -> List[float]:
        """Generates embeddings for a given prompt."""
        resp = await self.client.embeddings(
            model=self.embedding_model,
            prompt=prompt
        )
        return resp["embedding"]

    async def stream_chat(
        self, model: str, messages: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        """Streams a chat response from the LLM."""
        async for part in await self.client.chat(
            model=model,
            messages=messages,
            stream=True
        ):
            chunk = part['message']['content']
            yield chunk
