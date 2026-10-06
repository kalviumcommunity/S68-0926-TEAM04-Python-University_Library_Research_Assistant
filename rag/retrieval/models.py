"""Data models shared by vector retrieval and backend orchestration."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievalFilters:
    """Optional metadata filters supported by the retrieval layer."""

    document_id: str | None = None
    document_type: str | None = None
    year: int | None = None
    subject: str | None = None
    author: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class RetrievedChunk:
    """A traceable chunk returned by semantic retrieval."""

    chunk_id: str
    document_id: str
    text: str
    page: int | None
    section: str | None
    metadata: dict[str, Any]
    score: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "page": self.page,
            "section": self.section,
            "metadata": dict(self.metadata),
            "score": self.score,
        }

    @classmethod
    def from_chunk(cls, chunk: dict[str, Any], score: float) -> "RetrievedChunk":
        metadata = dict(chunk.get("metadata") or {})
        return cls(
            chunk_id=str(chunk["chunk_id"]),
            document_id=str(chunk["document_id"]),
            text=str(chunk["text"]),
            page=chunk.get("page"),
            section=chunk.get("section"),
            metadata=metadata,
            score=float(score),
        )
