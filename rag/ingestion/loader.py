"""Discover PDF documents in the raw document directory."""

from pathlib import Path


def discover_pdf_files(raw_dir: str | Path = "data/raw") -> list[Path]:
    """Return PDF files directly inside ``raw_dir`` in deterministic order.

    Missing directories, empty directories, and unrelated files produce an
    empty list rather than an exception.
    """
    directory = Path(raw_dir)
    if not directory.is_dir():
        return []

    return sorted(
        (
            path
            for path in directory.iterdir()
            if path.is_file() and path.suffix.lower() == ".pdf"
        ),
        key=lambda path: path.name.lower(),
    )
