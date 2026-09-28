"""Tests for the complete document ingestion pipeline."""

from pathlib import Path

import fitz

from rag.chunking.chunker import ChunkingConfig
from rag.ingestion.metadata import DocumentMetadata
from rag.ingestion.pipeline import ingest_document, ingest_documents


def create_pdf(path: Path, pages: list[str]) -> None:
    """Create a small PDF fixture."""
    document = fitz.open()
    for text in pages:
        page = document.new_page()
        if text:
            page.insert_text((72, 72), text)
    document.save(path)
    document.close()


def test_ingest_document_preserves_page_and_metadata(tmp_path: Path) -> None:
    pdf_path = tmp_path / "paper.pdf"
    create_pdf(pdf_path, ["First page."])
    metadata = DocumentMetadata(
        document_id="paper",
        title="Verified title",
        author="Verified author",
    )

    chunks = ingest_document(pdf_path, document=metadata)

    assert len(chunks) == 1
    assert chunks[0].chunk_id == "paper-p1-c1"
    assert chunks[0].document_id == "paper"
    assert chunks[0].page == 1
    assert chunks[0].metadata["title"] == "Verified title"
    assert chunks[0].text == "First page."


def test_ingest_documents_processes_multiple_pdfs_and_empty_pages(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    create_pdf(raw_dir / "one.pdf", ["One."])
    create_pdf(raw_dir / "two.pdf", ["", "Two."])

    chunks = ingest_documents(raw_dir)

    assert {chunk.document_id for chunk in chunks} == {"one", "two"}
    assert {chunk.page for chunk in chunks} == {1, 2}
    assert len({chunk.chunk_id for chunk in chunks}) == len(chunks)


def test_ingest_documents_skips_corrupt_and_unsupported_files(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "broken.pdf").write_text("not a PDF", encoding="utf-8")
    (raw_dir / "notes.txt").write_text("not supported", encoding="utf-8")

    assert ingest_documents(raw_dir) == []


def test_ingest_document_uses_configurable_chunking(tmp_path: Path) -> None:
    pdf_path = tmp_path / "paper.pdf"
    create_pdf(pdf_path, ["One. Two. Three."])

    chunks = ingest_document(
        pdf_path,
        config=ChunkingConfig(max_chars=10, overlap_chars=0),
    )

    assert len(chunks) > 1
    assert all(len(chunk.text) <= 10 for chunk in chunks)
