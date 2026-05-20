"""mem0 long-term memory integration for the LLM orchestrator."""

import asyncio
import logging
import os

from mem0 import Memory

from config import Settings

logger = logging.getLogger(__name__)

def build_mem0_client(settings: Settings) -> Memory:
    """
    Build and return an initialized mem0 Memory client.

    Connection credentials are read from environment variables.
    Model settings come from application settings.

    Args:
        settings: Application settings instance.

    Returns:
        Initialized Memory client.
    """
    config = {
        "version": "v1.1",
        "vector_store": {
            "provider": "pgvector",
            "config": {
                "host": os.environ["PGVECTOR_HOST"],
                "port": int(os.environ["PGVECTOR_PORT"]),
                "dbname": os.environ["PGVECTOR_DBNAME"],
                "user": "postgres",
                "password": os.environ["POSTGRES_PASSWORD"],
                "collection_name": os.environ["PGVECTOR_COLLECTION"],
            },
        },
        "graph_store": {
            "provider": "neo4j",
            "config": {
                "url": os.environ["NEO4J_URL"],
                "username": os.environ["NEO4J_USERNAME"],
                "password": os.environ["NEO4J_PASSWORD"],
            },
        },
        "llm": {
            "provider": "openai",
            "config": {
                "model": settings.mem0_llm_model,
                "temperature": 0.2,
                "openai_base_url": settings.litellm_host,
            },
        },
        "embedder": {
            "provider": "gemini",
            "config": {
                "model": settings.mem0_embedder_model,
                "embedding_dims": settings.mem0_embedding_dims,
            },
        },
    }
    return Memory.from_config(config)



async def search_memories(client: Memory, query: str, session_id: str) -> dict:
    """
    Search mem0 for memories relevant to the query.

    Args:
        client: Initialized Memory client.
        query: Search query (typically the user's prompt).
        session_id: Frontend session identifier.

    Returns:
        Dict with 'memories' (list of str) and 'relations' (list of str).
        Both empty if search fails.
    """
    try:
        raw = await asyncio.to_thread(client.search, query, user_id=session_id)
        memories = [r["memory"] for r in raw.get("results", [])]
        relations = [
            f"{r['source']} {r['relationship']} {r['destination']}"
            for r in raw.get("relations", [])
        ]
        logger.info(
            "mem0 search returned %d memories, %d relations for session %s.",
            len(memories), len(relations), session_id,
        )
        return {"memories": memories, "relations": relations}
    except Exception as e:
        logger.error("mem0 search failed for session %s: %s", session_id, e, exc_info=True)
        return {"memories": [], "relations": []}


async def add_memory(client: Memory, prompt: str, response: str, session_id: str) -> None:
    """
    Persist a conversation turn to mem0 long-term memory.

    Args:
        client: Initialized Memory client.
        prompt: Original user prompt.
        response: Full assistant response text.
        session_id: Frontend session identifier.
    """
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response},
    ]
    await asyncio.to_thread(client.add, messages, user_id=session_id)
    logger.info("mem0 memory saved for session %s.", session_id)


def build_system_prompt(template: str, search_result: dict) -> str:
    """
    Render the system prompt template with memory and relation context.

    Args:
        template: System prompt template string with {memories_section}
                  and {relations_section} placeholders.
        search_result: Dict with 'memories' and 'relations' from search_memories.

    Returns:
        Rendered system prompt string.
    """
    memories = search_result.get("memories", [])
    relations = search_result.get("relations", [])

    memories_section = (
        "Relevant memories:\n" + "\n".join(f"- {m}" for m in memories) + "\n\n"
        if memories else ""
    )
    relations_section = (
        "Known relations:\n" + "\n".join(f"- {r}" for r in relations) + "\n\n"
        if relations else ""
    )

    return template.format(
        memories_section=memories_section,
        relations_section=relations_section,
    )
