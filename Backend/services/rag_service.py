import json
from pathlib import Path
from typing import Any


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

        terms = set(question.lower().split())
        matches: list[tuple[int, dict[str, Any]]] = []
        with self.chunks_path.open(encoding="utf-8") as chunks_file:
            for line in chunks_file:
                chunk = json.loads(line)
                metadata = chunk.get("metadata", {})
                if not self._matches_filters(metadata, filters):
                    continue
                searchable = f"{chunk.get('text', '')} {metadata}".lower()
                score = sum(term in searchable for term in terms)
                if score:
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