from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    email: str

class ChatRequest(BaseModel):
    prompt: str
    model: str = 'gpt-oss:20b'

class Document(BaseModel):
    id: int
    content: str
    user_id: int

class Embedding(BaseModel):
    id: int
    document_id: int
    user_id: int
    embedding: list[float]
