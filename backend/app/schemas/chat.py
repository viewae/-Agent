from typing import Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    document_ids: Optional[list[int]] = None


class ChatSource(BaseModel):
    document_id: int
    filename: str
    chunk_index: int
    excerpt: str
    relevance: float


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[ChatSource] = []


class MessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: str


class SessionResponse(BaseModel):
    session_id: str
    first_query: str
    message_count: int
    created_at: str
