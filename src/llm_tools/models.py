from pydantic import BaseModel


class Turn(BaseModel):
    turn_id: int
    prompt: str
    response: str
    metadata: dict | None = None


class ChatSession(BaseModel):
    source: str
    format: str
    turns: list[Turn]
    character_name: str | None = None
    metadata: dict | None = None


class MemoryChunk(BaseModel):
    chunk_id: int
    turn_ids: list[int]
    summary: str
    prompt_context: str
    metadata: dict | None = None


class SessionMemory(BaseModel):
    session_summary: str
    chunks: list[MemoryChunk]
    metadata: dict | None = None


class TextSummary(BaseModel):
    source: str
    summary: str
    n_chunks: int
    chunk_size: int
    chunk_overlap: int
    context: str | None = None
    metadata: dict | None = None
