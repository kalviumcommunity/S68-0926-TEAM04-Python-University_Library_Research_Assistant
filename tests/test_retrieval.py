"""Tests for typed retrieval and the persistent vector store."""

from pathlib import Path

from rag.retrieval.models import RetrievedChunk, RetrievalFilters
from rag.vectorstore.chroma_store import ChromaStore
from Backend.services.rag_service import RAGService


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


def test_real_corpus_transformer_query_excludes_weak_rag_chunk() -> None:
    results = RAGService().retrieve("What is the Transformer architecture?")

    assert results
    assert results[0]["document_id"] == "1706.03762v7"
    assert results[0]["metadata"]["title"] == "Attention Is All You Need"
    assert "Transformer" in results[0]["text"]
    assert all(chunk["score"] >= 0.40 for chunk in results)
    assert all(
        chunk["document_id"] != "knowledge_intensive_nlp.pdf"
        or chunk["score"] >= 0.40
        for chunk in results
    )


def test_real_corpus_required_questions() -> None:
    service = RAGService()
    cases = (
        (
            "What is retrieval augmented generation?",
            {"rag_survey.pdf", "2312.10997v5"},
        ),
        ("How does BERT use bidirectional context?", "1810.04805v2"),
        ("What is self-attention?", "1706.03762v7"),
    )

    for question, expected_document in cases:
        results = service.retrieve(question)
        assert results
        expected_document_ids = (
            expected_document
            if isinstance(expected_document, set)
            else {expected_document}
        )
        assert expected_document_ids & {
            result["document_id"] for result in results[:5]
        }


def test_real_corpus_unrelated_question_returns_no_evidence() -> None:
    assert RAGService().retrieve("What is the capital of France?") == []
