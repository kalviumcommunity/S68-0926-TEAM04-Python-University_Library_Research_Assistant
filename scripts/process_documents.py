"""Run the local extraction, cleaning, metadata, and chunking pipeline."""

import argparse
import json
from pathlib import Path

from rag.chunking.chunker import ChunkingConfig
from rag.ingestion.metadata import load_document_metadata
from rag.ingestion.pipeline import ingest_documents


def process_documents(
    raw_dir: Path,
    metadata_path: Path,
    output_path: Path,
    config: ChunkingConfig | None = None,
) -> int:
    """Write the structured output of the ingestion pipeline as JSON Lines."""
    metadata = load_document_metadata(metadata_path)
    chunks = ingest_documents(raw_dir, metadata=metadata, config=config)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output_file:
        for chunk in chunks:
            output_file.write(
                json.dumps(
                    {
                        "chunk_id": chunk.chunk_id,
                        "document_id": chunk.document_id,
                        "text": chunk.text,
                        "page": chunk.page,
                        "section": chunk.section,
                        "metadata": chunk.metadata,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    return len(chunks)


def main() -> None:
    """Parse command-line options and process the raw document directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument(
        "--metadata",
        type=Path,
        default=Path("data/document_metadata.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/chunks.jsonl"),
    )
    parser.add_argument("--max-chars", type=int, default=1200)
    parser.add_argument("--overlap-chars", type=int, default=150)
    args = parser.parse_args()

    count = process_documents(
        args.raw_dir,
        args.metadata,
        args.output,
        ChunkingConfig(args.max_chars, args.overlap_chars),
    )
    print(f"Wrote {count} chunks to {args.output}")


if __name__ == "__main__":
    main()
