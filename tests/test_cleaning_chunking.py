"""Tests for cleaning, metadata, and chunking."""

from rag.chunking.chunker import ChunkingConfig, chunk_pages
from rag.ingestion.cleaner import clean_text
from rag.ingestion.extractor import ExtractedPage
from rag.ingestion.metadata import DocumentMetadata, build_content_metadata


def test_clean_text_normalizes_whitespace_without_rewriting_content() -> None:
    assert clean_text("A short sentence.  Another sentence.") == (
        "A short sentence. Another sentence."
    )


def test_clean_text_repairs_wrapped_words_and_preserves_paragraphs() -> None:
    messy = "This is an inter-\n national study.\n\n\nThe second paragraph.\n"

    assert clean_text(messy) == "This is an international study.\n\nThe second paragraph."


def test_clean_text_handles_empty_text() -> None:
    assert clean_text("") == ""
    assert clean_text(" \n\t ") == ""


def test_build_content_metadata_keeps_unknown_values_unavailable() -> None:
    metadata = DocumentMetadata(document_id="doc-1")

    result = build_content_metadata(metadata, page=3)

    assert result == {
        "document_id": "doc-1",
        "title": None,
        "author": None,
        "document_type": None,
        "year": None,
        "subject": None,
        "source_url": None,
        "page": 3,
        "section": None,
    }


def test_chunk_pages_preserves_traceability_and_unique_ids() -> None:
    pages = [
        ExtractedPage("doc-1", 2, "First sentence. Second sentence."),
        ExtractedPage("doc-1", 3, "Third sentence."),
    ]
    document = DocumentMetadata(
        document_id="doc-1",
        title="Known title",
        author="Known author",
        document_type="thesis",
        year=2024,
        subject="History",
        source_url="https://example.edu/doc-1",
    )

    chunks = chunk_pages(pages, document=document, section="Introduction")

    assert [chunk.chunk_id for chunk in chunks] == ["doc-1-p2-c1", "doc-1-p3-c1"]
    assert chunks[0].document_id == "doc-1"
    assert chunks[0].page == 2
    assert chunks[0].section == "Introduction"
    assert chunks[0].metadata["author"] == "Known author"
    assert chunks[0].metadata["page"] == 2


def test_chunk_pages_supports_configurable_size_and_overlap() -> None:
    page = ExtractedPage("doc-1", 1, "One. Two. Three. Four.")
    config = ChunkingConfig(max_chars=15, overlap_chars=6)

    chunks = chunk_pages([page], config=config)

    assert [chunk.text for chunk in chunks] == [
        "One. Two.",
        "Two. Three.",
        "Three. Four.",
    ]


def test_chunk_pages_skips_empty_pages() -> None:
    assert chunk_pages([ExtractedPage("doc-1", 1, " \n ")]) == []
