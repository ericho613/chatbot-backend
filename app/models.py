from typing import Literal, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class GenerationConfig(BaseModel):
    max_tokens: int = Field(default=1000, ge=1, le=8192)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    stream: bool = False
    generation_config: GenerationConfig = GenerationConfig()


class ChatResponse(BaseModel):
    success: bool
    model: str
    response: str


class RagRequest(BaseModel):
    query: str
    stream: bool = False
    top_k: int = Field(default=5, ge=1, le=20)
    generation_config: GenerationConfig = GenerationConfig()


class RagResponse(BaseModel):
    success: bool
    model: str
    response: str
    retrieved_chunks: list[str]


class SummaryResponse(BaseModel):
    success: bool
    model: str
    summary: str
    filename: Optional[str] = None


class CitationResponse(BaseModel):
    success: bool
    model: str
    citation_style: str
    citation: str
    filename: Optional[str] = None


class UploadResponse(BaseModel):
    success: bool
    message: str
    filename: str
    chunks_indexed: int
    citation: str
    vector_backend: str


class TokenRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"