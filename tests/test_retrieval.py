"""Tests for typed retrieval and the persistent vector store."""

from pathlib import Path

from rag.retrieval.models import RetrievedChunk, RetrievalFilters
from rag.vectorstore.chroma_store import ChromaStore


def test_retrieved_chunk_preserves_metadata_and_score() -> None:
    chunk = RetrievedChunk.from_chunk(
        {
            "chunk_id": "doc-p1-c1",
            "document_id": "doc",
            "text": "Evidence",
            "page": 1,
            "section": None,
            "metadata": {"title": "Paper", "author": "Author"},
        },
        0.87,
    )

    assert chunk.as_dict()["metadata"]["author"] == "Author"
    assert chunk.score == 0.87
    assert RetrievalFilters(year=2024).as_dict() == {"year": 2024}


def test_chroma_store_is_repeatable_and_returns_traceable_chunks(tmp_path: Path) -> None:
    store = ChromaStore(tmp_path / "index", collection_name="test_chunks")
    chunks = [
        {
            "chunk_id": "doc-p1-c1",
            "document_id": "doc",
            "text": "retrieval augmented generation",
            "page": 1,
            "section": None,
            "metadata": {"title": "Paper", "year": 2024},
        }
    ]
    embedding = [[1.0, 0.0, 0.0]]

    assert store.build_index(chunks, embedding) == 1
    assert store.build_index(chunks, embedding) == 1
    assert store.count() == 1
    result = store.search(embedding[0])
    assert result[0].chunk_id == "doc-p1-c1"
    assert result[0].page == 1
