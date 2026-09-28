from pydantic import BaseModel, Field  # type: ignore[import-not-found]

from .citation import Citation


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    filters: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]