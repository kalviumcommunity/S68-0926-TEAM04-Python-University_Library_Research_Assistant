"""Tests for PDF discovery and extraction."""

from pathlib import Path

import fitz

from rag.ingestion.extractor import ExtractedPage, extract_pdf
from rag.ingestion.loader import discover_pdf_files


def create_pdf(path: Path, pages: list[str]) -> None:
    """Create a small PDF fixture for extraction tests."""
    document = fitz.open()
    for text in pages:
        page = document.new_page()
        page.insert_text((72, 72), text)
    document.save(path)
    document.close()


def test_discover_pdf_files_returns_only_pdfs(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    create_pdf(raw_dir / "paper.PDF", ["content"])
    (raw_dir / "notes.txt").write_text("not a PDF", encoding="utf-8")
    (raw_dir / "subdirectory").mkdir()

    assert discover_pdf_files(raw_dir) == [raw_dir / "paper.PDF"]


def test_discover_pdf_files_handles_missing_directory(tmp_path: Path) -> None:
    assert discover_pdf_files(tmp_path / "missing") == []


def test_discover_pdf_files_handles_empty_directory(tmp_path: Path) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    assert discover_pdf_files(raw_dir) == []


def test_extract_pdf_preserves_document_id_and_page_numbers(tmp_path: Path) -> None:
    pdf_path = tmp_path / "research-paper.pdf"
    create_pdf(pdf_path, ["First page", "Second page"])

    result = extract_pdf(pdf_path)

    assert result == [
        ExtractedPage("research-paper", 1, "First page\n"),
        ExtractedPage("research-paper", 2, "Second page\n"),
    ]


def test_extract_pdf_retains_empty_pages(tmp_path: Path) -> None:
    pdf_path = tmp_path / "with-empty-page.pdf"
    create_pdf(pdf_path, ["Visible text", ""])

    result = extract_pdf(pdf_path)

    assert len(result) == 2
    assert result[1] == ExtractedPage("with-empty-page", 2, "")


def test_extract_pdf_handles_invalid_pdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "invalid.pdf"
    pdf_path.write_text("not a real PDF", encoding="utf-8")

    assert extract_pdf(pdf_path) == []
