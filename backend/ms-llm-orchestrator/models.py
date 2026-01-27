from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

class ChatRequest(BaseModel):
    prompt: str
    model: str = 'gemini'

