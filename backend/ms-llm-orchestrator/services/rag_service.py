import logging
import json
import asyncpg
from typing import List

from .llm_client import LLMClient

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, db_pool: asyncpg.Pool, llm_client: LLMClient):
        self.db_pool = db_pool
        self.llm_client = llm_client

    async def retrieve_rag_context(self, prompt: str, user_id: int) -> str:
        """
        Generates embeddings for the prompt and retrieves relevant context from the 
        PostgreSQL database using vector similarity search.
        """
        if not self.db_pool or not self.llm_client:
            logger.warning("Database pool or LLM client not available, skipping RAG retrieval.")
            return ""

        try:
            query_embedding = await self.llm_client.generate_embedding(prompt)

            async with self.db_pool.acquire() as connection:
                sql_query = """
                    SELECT d.content, e.embedding <=> $1::vector AS similarity
                    FROM embeddings e
                    JOIN documents d ON e.document_id = d.id
                    WHERE e.user_id = $2
                    ORDER BY similarity ASC
                    LIMIT 3;
                """
                rows = await connection.fetch(sql_query, json.dumps(query_embedding), user_id)

                if not rows:
                    logger.info(f"No RAG context found for prompt: '{prompt}', user_id: {user_id}")
                    return ""

                return ",".join([row['content'] for row in rows])

        except Exception as e:
            logger.error(f"Error during RAG retrieval for user_id {user_id}: {e}", exc_info=True)
            return ""

    async def save_chat_history(self, user_id: int, prompt: str, response: str):
        """Saves the chat prompt and response to the database with its embedding."""
        if not self.db_pool or not self.llm_client:
            logger.warning("Database pool or LLM client not available, skipping history save.")
            return

        try:
            full_content = f"User query: {prompt}\nLLM response: {response}"
            embedding = await self.llm_client.generate_embedding(full_content)

            async with self.db_pool.acquire() as connection:
                async with connection.transaction():
                    result = await connection.fetchrow(
                        """INSERT INTO documents (content, user_id) VALUES ($1, $2) RETURNING id;""",
                        full_content, user_id
                    )
                    document_id = result['id']

                    await connection.execute(
                        """INSERT INTO embeddings (document_id, user_id, embedding) VALUES ($1, $2, $3);""",
                        document_id, user_id, json.dumps(embedding)
                    )
            logger.info(f"Successfully saved chat history for user_id: {user_id}")

        except Exception as e:
            logger.error(f"Error saving chat history for user_id {user_id}: {e}", exc_info=True)
