"""Build the local semantic index from processed chunks."""

import json
from pathlib import Path

from rag.embeddings.embedder import Embedder
from rag.vectorstore.chroma_store import ChromaStore


CHUNKS_PATH = Path("data/processed/chunks.jsonl")


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict]:
    if not path.is_file():
        raise FileNotFoundError(f"Chunks file not found: {path}")
    chunks: list[dict] = []
    with path.open(encoding="utf-8") as chunks_file:
        for line_number, line in enumerate(chunks_file, start=1):
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Malformed JSON on line {line_number}.") from exc
            if not isinstance(chunk, dict) or not str(chunk.get("text") or "").strip():
                raise ValueError(f"Chunk on line {line_number} has empty text.")
            if not chunk.get("chunk_id") or not chunk.get("document_id"):
                raise ValueError(f"Chunk on line {line_number} has invalid identity.")
            chunks.append(chunk)
    return chunks


def build_index() -> int:
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks")
    embeddings = Embedder().embed_documents([chunk["text"] for chunk in chunks])
    print(f"Embedded {len(embeddings)} chunks")
    indexed = ChromaStore().build_index(chunks, embeddings)
    print(f"Indexed {indexed} chunks")
    return indexed


if __name__ == "__main__":
    build_index()
