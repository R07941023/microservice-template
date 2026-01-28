"""Data models for LLM orchestrator service."""

from typing import Optional

from pydantic import BaseModel


class User(BaseModel):
    """User information extracted from JWT token."""

    name: Optional[str] = None
    email: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request payload."""

    prompt: str
    model: str = "gemini"
