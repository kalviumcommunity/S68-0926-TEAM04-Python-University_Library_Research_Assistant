"""Backend-facing semantic retrieval service."""

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
        similarity_threshold: float = 0.35,
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
            chunks = self.store.search(query_embedding, top_k, filters)
        except (RuntimeError, ValueError, OSError, KeyError) as exc:
            raise RAGServiceUnavailable(str(exc)) from exc
        return [
            chunk.as_dict()
            for chunk in chunks
            if chunk.score >= self.similarity_threshold
        ]
