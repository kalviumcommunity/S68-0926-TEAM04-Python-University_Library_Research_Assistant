"""Configurable, traceable text chunking."""

from dataclasses import dataclass
import re
from typing import Iterable

from rag.ingestion.cleaner import clean_text
from rag.ingestion.extractor import ExtractedPage
from rag.ingestion.metadata import DocumentMetadata, build_content_metadata


@dataclass(frozen=True)
class ChunkingConfig:
    """Controls chunk size and overlap in characters."""

    max_chars: int = 1200
    overlap_chars: int = 150

    def __post_init__(self) -> None:
        if self.max_chars <= 0:
            raise ValueError("max_chars must be greater than zero")
        if self.overlap_chars < 0 or self.overlap_chars >= self.max_chars:
            raise ValueError("overlap_chars must be between zero and max_chars")


@dataclass(frozen=True)
class TextChunk:
    """A chunk that remains traceable to its source page and document."""

    chunk_id: str
    document_id: str
    text: str
    page: int
    section: str | None
    metadata: dict[str, object]


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text) if part.strip()]


def _split_long_sentence(sentence: str, max_chars: int) -> list[str]:
    return [
        sentence[start : start + max_chars].strip()
        for start in range(0, len(sentence), max_chars)
    ]


def _overlap_text(text: str, overlap_chars: int) -> str:
    """Return complete trailing sentences when they fit the overlap budget."""
    sentences = _sentences(text)
    if sentences and len(sentences[-1]) <= overlap_chars:
        return sentences[-1]
    return ""


def _chunk_text(text: str, config: ChunkingConfig) -> list[str]:
    chunks: list[str] = []
    current = ""

    for sentence in _sentences(text):
        pieces = (
            _split_long_sentence(sentence, config.max_chars)
            if len(sentence) > config.max_chars
            else [sentence]
        )
        for piece in pieces:
            candidate = f"{current} {piece}".strip()
            if current and len(candidate) > config.max_chars:
                chunks.append(current)
                overlap = _overlap_text(current, config.overlap_chars)
                current = f"{overlap} {piece}".strip() if overlap else piece
            else:
                current = candidate

    if current:
        chunks.append(current)
    return chunks


def chunk_pages(
    pages: Iterable[ExtractedPage],
    document: DocumentMetadata | None = None,
    section: str | None = None,
    config: ChunkingConfig | None = None,
) -> list[TextChunk]:
    """Clean and chunk extracted pages while preserving source metadata."""
    chunking_config = config or ChunkingConfig()
    chunks: list[TextChunk] = []

    for page in pages:
        cleaned = clean_text(page.text)
        if not cleaned:
            continue
        document_metadata = document or DocumentMetadata(document_id=page.document_id)
        for page_chunk_number, text in enumerate(
            _chunk_text(cleaned, chunking_config), start=1
        ):
            chunk_id = f"{page.document_id}-p{page.page}-c{page_chunk_number}"
            chunks.append(
                TextChunk(
                    chunk_id=chunk_id,
                    document_id=page.document_id,
                    text=text,
                    page=page.page,
                    section=section,
                    metadata=build_content_metadata(
                        document_metadata,
                        page=page.page,
                        section=section,
                    ),
                )
            )
    return chunks
