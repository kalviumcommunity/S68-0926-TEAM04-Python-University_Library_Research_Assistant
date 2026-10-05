import json
import re
from pathlib import Path
from typing import Any


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "which",
    "with",
}


class RAGServiceUnavailable(Exception):
    """Raised when the RAG service is not available."""
    pass


class RAGService:
    def __init__(self, chunks_path: str | Path = "data/processed/chunks.jsonl") -> None:
        self.chunks_path = Path(chunks_path)

    def retrieve(
        self,
        question: str,
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Return simple lexical evidence from the processed RAG chunks.

        This is a deterministic integration bridge until embeddings/vector
        retrieval are supplied by the RAG pipeline.
        """
        if not self.chunks_path.is_file():
            raise RAGServiceUnavailable(
                f"Processed chunks file not found: {self.chunks_path}"
            )

        terms = {
            term
            for term in re.findall(r"[a-z0-9]+", question.lower())
            if term not in STOPWORDS
        }
        if not terms:
            return []

        minimum_matches = 2 if len(terms) > 1 else 1
        matches: list[tuple[int, dict[str, Any]]] = []
        with self.chunks_path.open(encoding="utf-8") as chunks_file:
            for line in chunks_file:
                chunk = json.loads(line)
                metadata = chunk.get("metadata", {})
                if not self._matches_filters(metadata, filters):
                    continue
                text_terms = set(
                    re.findall(r"[a-z0-9]+", chunk.get("text", "").lower())
                )
                searchable_metadata = " ".join(
                    str(metadata.get(field) or "")
                    for field in ("title", "subject", "document_type")
                )
                metadata_terms = set(
                    re.findall(r"[a-z0-9]+", searchable_metadata.lower())
                )
                text_matches = terms & text_terms
                metadata_matches = terms & metadata_terms
                score = len(text_matches) + (2 * len(metadata_matches))
                if len(text_matches | metadata_matches) >= minimum_matches:
                    matches.append((score, chunk))

        matches.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in matches[:5]]

    @staticmethod
    def _matches_filters(
        metadata: dict[str, Any],
        filters: dict[str, Any],
    ) -> bool:
        return all(
            not value or metadata.get(key) == value
            for key, value in filters.items()
        )