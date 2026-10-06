"""Local ONNX embeddings supplied by Chroma's MiniLM model."""


class Embedder:
    """Load one local MiniLM embedding function and reuse it for all calls."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            try:
                from chromadb.utils.embedding_functions import (
                    DefaultEmbeddingFunction,
                )
            except ImportError as exc:
                raise RuntimeError(
                    "chromadb is required for semantic retrieval."
                ) from exc
            self._model = DefaultEmbeddingFunction()
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if any(not text or not text.strip() for text in texts):
            raise ValueError("Cannot embed empty document text.")
        return self._get_model()(texts)

    def embed_query(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Cannot embed an empty query.")
        return self.embed_documents([text])[0]
