"""Traceability metadata shared by ingestion and chunking."""

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DocumentMetadata:
    """Known metadata for one source document.

    Optional values remain ``None`` when the source does not provide them.
    """

    document_id: str
    title: str | None = None
    author: str | None = None
    document_type: str | None = None
    year: int | None = None
    subject: str | None = None
    source_url: str | None = None


def build_content_metadata(
    document: DocumentMetadata,
    page: int,
    section: str | None = None,
) -> dict[str, Any]:
    """Build traceability metadata for page-level or chunk-level content."""
    values: dict[str, Any] = asdict(document)
    values["page"] = page
    values["section"] = section
    return values
