"""Configuration settings for LLM orchestrator service."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM settings
    default_chat_model: str = "gemini/gemini-2.5-flash"
    system_prompt_template: str = (
        "You are a helpful Maplestory assistant.\n\n"
        "{memories_section}"
        "{relations_section}"
    )

    # External service settings
    mcp_token: Optional[str] = None
    mcp_host: Optional[str] = None
    litellm_host: Optional[str] = None

    # mem0 models
    mem0_llm_model: str = "gemini/gemini-2.5-flash"
    mem0_embedder_model: str = "gemini-embedding-001"
    mem0_embedding_dims: int = 1536

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
