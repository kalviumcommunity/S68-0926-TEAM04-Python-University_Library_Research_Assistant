"""A small, repeatable ChromaDB store for traceable chunks."""

from pathlib import Path
from typing import Any

from rag.retrieval.models import RetrievedChunk


class ChromaStore:
    """Persist embeddings and source metadata in a local Chroma collection."""

    def __init__(
        self,
        persist_directory: str | Path = "data/vectorstore",
        collection_name: str = "library_chunks",
    ) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("chromadb is required for semantic retrieval.") from exc
        self._client = chromadb.PersistentClient(path=str(persist_directory))
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            configuration={"hnsw": {"space": "cosine"}},
        )

    def build_index(
        self,
        chunks: list[dict[str, Any]],
        embeddings: list[list[float]],
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("Every chunk must have one embedding.")
        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, Any]] = []
        for chunk in chunks:
            chunk_id = str(chunk.get("chunk_id") or "")
            text = str(chunk.get("text") or "").strip()
            if not chunk_id or not text:
                raise ValueError("Chunks require non-empty chunk_id and text.")
            if chunk_id in ids:
                raise ValueError(f"Duplicate chunk_id: {chunk_id}")
            metadata = dict(chunk.get("metadata") or {})
            metadata.update(
                {
                    "document_id": str(chunk["document_id"]),
                    "chunk_id": chunk_id,
                    "page": chunk.get("page"),
                    "section": chunk.get("section") or "",
                }
            )
            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(_serializable_metadata(metadata))
        if ids:
            self._collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
        return len(ids)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        where = _build_where(filters or {})
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        chunks: list[RetrievedChunk] = []
        for text, metadata, distance in zip(documents, metadatas, distances):
            metadata = dict(metadata or {})
            chunk = {
                "chunk_id": metadata.pop("chunk_id"),
                "document_id": metadata.pop("document_id"),
                "text": text,
                "page": _optional_int(metadata.pop("page", None)),
                "section": metadata.pop("section", None) or None,
                "metadata": metadata,
            }
            chunks.append(RetrievedChunk.from_chunk(chunk, 1.0 - float(distance)))
        return chunks

    def count(self) -> int:
        return self._collection.count()

    def reset(self) -> None:
        self._client.delete_collection(self._collection.name)
        self._collection = self._client.get_or_create_collection(
            name=self._collection.name,
            configuration={"hnsw": {"space": "cosine"}},
        )


def _serializable_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        key: (value if isinstance(value, (str, int, float, bool)) else str(value or ""))
        for key, value in metadata.items()
        if value is not None
    }


def _build_where(filters: dict[str, Any]) -> dict[str, Any] | None:
    clauses = [
        {key: value}
        for key, value in filters.items()
        if value is not None and value != ""
    ]
    if not clauses:
        return None
    return clauses[0] if len(clauses) == 1 else {"$and": clauses}


def _optional_int(value: Any) -> int | None:
    return int(value) if value not in (None, "") else None
