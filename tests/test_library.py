"""Tests for the local document repository frontend helpers."""

import json
from pathlib import Path

from frontend.utils.library import load_library_documents, search_library_documents


def test_load_library_documents_uses_metadata_and_real_chunk_excerpt(
    tmp_path: Path,
) -> None:
    metadata_path = tmp_path / "metadata.csv"
    metadata_path.write_text(
        "document_id,title,document_type,author,year,subject,source_url\n"
        "doc-1,Known paper,research_paper,Author,2024,NLP,\n",
        encoding="utf-8",
    )
    chunks_path = tmp_path / "chunks.jsonl"
    chunks_path.write_text(
        json.dumps({"document_id": "doc-1", "text": "Evidence excerpt"}) + "\n",
        encoding="utf-8",
    )

    documents = load_library_documents(metadata_path, chunks_path)

    assert len(documents) == 1
    assert documents[0].metadata.document_id == "doc-1"
    assert documents[0].excerpt == "Evidence excerpt"


def test_search_library_documents_matches_real_fields() -> None:
    metadata_path = Path("data/document_metadata.csv")
    documents = load_library_documents(metadata_path, Path("missing.jsonl"))

    results = search_library_documents(documents, "knowledge intensive")

    assert [document.metadata.document_id for document in results] == [
        "knowledge_intensive_nlp.pdf"
    ]


def test_search_library_documents_returns_no_results_for_unknown_query() -> None:
    documents = load_library_documents(
        Path("data/document_metadata.csv"),
        Path("missing.jsonl"),
    )

    assert search_library_documents(documents, "not in library") == []
