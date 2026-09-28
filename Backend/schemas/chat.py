from typing import Any

from pydantic import BaseModel, Field, field_validator

from .citation import Citation


class ChatRequest(BaseModel):
    question: str = Field(..., description="Academic question from the user")
    filters: dict[str, Any] = Field(default_factory=dict)

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Question cannot be empty")

        return value.strip()


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory=list)