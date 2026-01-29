"""Configuration settings for LLM orchestrator service."""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM settings
    default_chat_model: str = "gemini/gemini-2.5-flash"
    system_prompt: str = (
        "You are a helpful assistant. "
        "Use the following context to answer the user's question."
    )

    # External service settings
    mcp_token: Optional[str] = None
    mcp_host: Optional[str] = None
    litellm_host: Optional[str] = None

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
