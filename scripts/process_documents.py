"""Run the local extraction, cleaning, metadata, and chunking pipeline."""

import argparse
import csv
import json
from pathlib import Path

from rag.chunking.chunker import ChunkingConfig, chunk_pages
from rag.ingestion.extractor import extract_pdf
from rag.ingestion.loader import discover_pdf_files
from rag.ingestion.metadata import DocumentMetadata


def load_metadata(metadata_path: Path) -> dict[str, DocumentMetadata]:
    """Load known document metadata without filling unknown values."""
    with metadata_path.open(newline="", encoding="utf-8") as metadata_file:
        return {
            row["document_id"]: DocumentMetadata(
                document_id=row["document_id"],
                title=row["title"] or None,
                document_type=row["document_type"] or None,
                author=row["author"] or None,
                year=int(row["year"]) if row["year"] else None,
                subject=row["subject"] or None,
                source_url=row["source_url"] or None,
            )
            for row in csv.DictReader(metadata_file)
        }


def process_documents(
    raw_dir: Path,
    metadata_path: Path,
    output_path: Path,
    config: ChunkingConfig | None = None,
) -> int:
    """Process every raw PDF and write traceable chunks as JSON Lines."""
    metadata = load_metadata(metadata_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chunk_count = 0

    with output_path.open("w", encoding="utf-8") as output_file:
        for pdf_path in discover_pdf_files(raw_dir):
            pages = extract_pdf(pdf_path)
            document_id = pdf_path.stem
            document = metadata.get(document_id, DocumentMetadata(document_id))
            for chunk in chunk_pages(pages, document=document, config=config):
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
                chunk_count += 1

    return chunk_count


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
