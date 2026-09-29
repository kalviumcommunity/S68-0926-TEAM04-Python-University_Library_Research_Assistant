"""Read-only access to the processed document catalog for Streamlit."""

import json
from dataclasses import dataclass
from pathlib import Path

from rag.ingestion.metadata import DocumentMetadata, load_document_metadata


@dataclass(frozen=True)
class LibraryDocument:
    """Document metadata plus an optional processed-text excerpt."""

    metadata: DocumentMetadata
    excerpt: str | None = None


def load_library_documents(
    metadata_path: str | Path = "data/document_metadata.csv",
    chunks_path: str | Path = "data/processed/chunks.jsonl",
) -> list[LibraryDocument]:
    """Load real document metadata and excerpts from processed chunks."""
    metadata = load_document_metadata(metadata_path)
    excerpts: dict[str, str] = {}
    chunks_file = Path(chunks_path)
    if chunks_file.is_file():
        with chunks_file.open(encoding="utf-8") as source:
            for line in source:
                record = json.loads(line)
                document_id = record["document_id"]
                if document_id not in excerpts and record.get("text"):
                    excerpts[document_id] = record["text"]

    return [
        LibraryDocument(document, excerpts.get(document_id))
        for document_id, document in sorted(metadata.items())
    ]


def search_library_documents(
    documents: list[LibraryDocument],
    query: str,
) -> list[LibraryDocument]:
    """Filter documents using metadata and excerpt text."""
    terms = query.lower().split()
    if not terms:
        return documents

    def matches(document: LibraryDocument) -> bool:
        metadata = document.metadata
        searchable = " ".join(
            value or ""
            for value in (
                metadata.document_id,
                metadata.title,
                metadata.author,
                metadata.document_type,
                metadata.subject,
                document.excerpt,
            )
        ).lower()
        return all(term in searchable for term in terms)

    return [document for document in documents if matches(document)]
