from typing import Any


class RAGServiceUnavailable(Exception):
    """Raised when the RAG service is not available."""
    pass


class RAGService:
    def retrieve(
        self,
        question: str,
        filters: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Interface for Person 1's RAG system.

        The actual retrieval implementation will be
        connected later.
        """

        raise RAGServiceUnavailable(
            "RAG service is not available yet."
        )