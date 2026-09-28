"""Small orchestration layer for the document ingestion pipeline."""

from pathlib import Path

from rag.chunking.chunker import ChunkingConfig, TextChunk, chunk_pages
from rag.ingestion.extractor import extract_pdf
from rag.ingestion.loader import discover_pdf_files
from rag.ingestion.metadata import DocumentMetadata


def ingest_document(
    pdf_path: str | Path,
    document: DocumentMetadata | None = None,
    config: ChunkingConfig | None = None,
) -> list[TextChunk]:
    """Extract, clean, attach metadata, and chunk one PDF."""
    path = Path(pdf_path)
    pages = extract_pdf(path)
    document_metadata = document or DocumentMetadata(document_id=path.stem)
    return chunk_pages(pages, document=document_metadata, config=config)


def ingest_documents(
    raw_dir: str | Path = "data/raw",
    metadata: dict[str, DocumentMetadata] | None = None,
    config: ChunkingConfig | None = None,
) -> list[TextChunk]:
    """Process every discoverable PDF in a directory into traceable chunks."""
    known_metadata = metadata or {}
    chunks: list[TextChunk] = []
    for pdf_path in discover_pdf_files(raw_dir):
        document = known_metadata.get(
            pdf_path.stem,
            DocumentMetadata(document_id=pdf_path.stem),
        )
        chunks.extend(ingest_document(pdf_path, document=document, config=config))
    return chunks
