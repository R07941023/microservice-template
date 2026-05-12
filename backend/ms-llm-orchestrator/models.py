"""Data models for LLM orchestrator service."""

from pydantic import BaseModel


class HistoryMessage(BaseModel):
    """A single message in the conversation history."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request payload."""

    prompt: str
    model: str = "gemini"
    history: list[HistoryMessage] = []
    session_id: str
