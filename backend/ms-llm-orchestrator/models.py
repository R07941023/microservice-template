"""Data models for LLM orchestrator service."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """Chat request payload."""

    prompt: str
    model: str = "gemini"
