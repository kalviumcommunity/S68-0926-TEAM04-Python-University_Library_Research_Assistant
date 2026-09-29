from dataclasses import dataclass


@dataclass
class BaseModel:
    """Minimal local model base used when the optional Pydantic dependency is unavailable."""

    pass


class Document(BaseModel):
    document_id: str
    title: str
    document_type: str | None = None
    author: str | None = None
    year: int | None = None