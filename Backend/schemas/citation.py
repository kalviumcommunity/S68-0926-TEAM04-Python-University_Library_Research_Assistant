# pyright: reportMissingImports=false
from typing import Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_id: str
    title: str
    excerpt: str | None = None
    page: int | None = None
    section: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)