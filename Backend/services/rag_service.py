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
        meaningful_chunks.sort(
            key=lambda chunk: _question_aware_score(question, chunk),
            reverse=True,
        )
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


_DEFINITION_RE = re.compile(
    r"\bwhat\s+(?:is|are)|\bwhat\s+does\b|\bdefine\b|\bmeaning\s+of\b",
    re.IGNORECASE,
)
_DEFINITION_CUES = (
    " is a ",
    " is an ",
    " refers to ",
    " called ",
    " designed to ",
    " we introduce ",
    " we propose ",
    " we present ",
    " consists of ",
)
_INCIDENTAL_CUES = (
    "table ",
    "appendix",
    "ablation",
    "implementation details",
    "results are presented",
    "hyperparameter",
)


def _question_aware_score(question: str, chunk: RetrievedChunk) -> float:
    """Rerank semantic candidates using generic question intent and text quality."""
    score = chunk.score
    if not _DEFINITION_RE.search(question):
        return score

    text = f" {chunk.text.lower()} "
    cue_count = sum(cue in text for cue in _DEFINITION_CUES)
    incidental_count = sum(cue in text for cue in _INCIDENTAL_CUES)
    return score + cue_count * 0.08 - incidental_count * 0.06
