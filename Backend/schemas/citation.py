# pyright: reportMissingImports=false
from typing import Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    citation_id: int | None = None
    chunk_id: str | None = None
    document_id: str
    title: str
    author: str | None = None
    excerpt: str | None = None
    page: int | None = None
    section: str | None = None
    source_url: str | None = None
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)