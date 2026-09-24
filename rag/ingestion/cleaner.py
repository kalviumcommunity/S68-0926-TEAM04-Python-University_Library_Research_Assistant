"""Conservative cleanup for text extracted from PDFs."""

import re


def clean_text(text: str) -> str:
    """Remove common extraction artifacts without changing the meaning.

    Paragraph boundaries are preserved, while wrapped lines within a
    paragraph are joined with a single space. Empty or whitespace-only input
    produces an empty string.
    """
    if not text or not text.strip():
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", normalized)
    paragraphs: list[str] = []

    for paragraph in re.split(r"\n\s*\n+", normalized):
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in paragraph.split("\n")]
        paragraph_text = " ".join(line for line in lines if line)
        if paragraph_text:
            paragraphs.append(paragraph_text)

    return "\n\n".join(paragraphs)
