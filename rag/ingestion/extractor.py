"""Page-level text extraction for PDF documents."""

from dataclasses import dataclass
import logging
from pathlib import Path

import fitz

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExtractedPage:
    """Text extracted from one page of a source document."""

    document_id: str
    page: int
    text: str


def extract_pdf(pdf_path: str | Path) -> list[ExtractedPage]:
    """Extract text from each page of a PDF.

    Page numbering is one-based and empty pages are retained with empty text.
    Invalid or unreadable PDFs are reported through logging and return no
    fabricated results.
    """
    path = Path(pdf_path)
    document_id = path.stem
    extracted_pages: list[ExtractedPage] = []

    try:
        with fitz.open(path) as document:
            for page_number, page in enumerate(document, start=1):
                extracted_pages.append(
                    ExtractedPage(
                        document_id=document_id,
                        page=page_number,
                        text=page.get_text("text"),
                    )
                )
    except (OSError, RuntimeError, fitz.FileDataError) as error:
        LOGGER.warning("Could not extract PDF %s: %s", path, error)
        return []

    return extracted_pages
