"""Traceability metadata shared by ingestion and chunking."""

from dataclasses import asdict, dataclass
import csv
from pathlib import Path
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


def load_document_metadata(metadata_path: str | Path) -> dict[str, DocumentMetadata]:
    """Load verified document metadata from the project CSV."""
    path = Path(metadata_path)
    with path.open(newline="", encoding="utf-8") as metadata_file:
        return {
            row["document_id"]: DocumentMetadata(
                document_id=row["document_id"],
                title=row["title"] or None,
                document_type=row["document_type"] or None,
                author=row["author"] or None,
                year=int(row["year"]) if row["year"] else None,
                subject=row["subject"] or None,
                source_url=row["source_url"] or None,
            )
            for row in csv.DictReader(metadata_file)
        }


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
