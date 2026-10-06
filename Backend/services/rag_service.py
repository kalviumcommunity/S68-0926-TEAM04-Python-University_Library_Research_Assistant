"""Backend-facing semantic retrieval service."""

import re
from pathlib import Path
from typing import Any

from rag.embeddings.embedder import Embedder
from rag.retrieval.models import RetrievedChunk
from rag.vectorstore.chroma_store import ChromaStore


class RAGServiceUnavailable(Exception):
    """Raised when the semantic index or embedding service is unavailable."""


class RAGService:
    def __init__(
        self,
        persist_directory: str | Path = "data/vectorstore",
        similarity_threshold: float = 0.40,
    ) -> None:
        self.store = ChromaStore(persist_directory)
        self.embedder = Embedder()
        self.similarity_threshold = similarity_threshold

    def retrieve(
        self,
        question: str,
        filters: dict[str, Any] | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        try:
            query_embedding = self.embedder.embed_query(question)
            # Retrieve a wider semantic candidate set before removing
            # bibliography/reference chunks that often score highly on generic
            # RAG terminology.
            chunks = self.store.search(query_embedding, max(top_k * 4, 20), filters)
        except (RuntimeError, ValueError, OSError, KeyError) as exc:
            raise RAGServiceUnavailable(str(exc)) from exc
        threshold = self.similarity_threshold
        if filters and filters.get("document_id"):
            # A document-scoped query searches a smaller candidate set, so a
            # lower calibrated cutoff is appropriate while remaining explicit.
            threshold = min(threshold, 0.25)
        meaningful_chunks = [
            chunk
            for chunk in chunks
            if chunk.score >= threshold and not _looks_like_references(chunk.text)
        ]
        return [chunk.as_dict() for chunk in meaningful_chunks[:top_k]]


def _looks_like_references(text: str) -> bool:
    """Reject bibliography-heavy chunks as answer evidence."""
    normalized = text.lower().strip()
    citation_count = len(re.findall(r"\[\d+\]", text))
    return (
        normalized.startswith(("references", "bibliography"))
        or citation_count >= 4
        or normalized.count("arxiv preprint") >= 2
    )
