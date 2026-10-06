import re
from collections.abc import Iterable

from fastapi import APIRouter, HTTPException, status

from Backend.schemas.chat import ChatRequest, ChatResponse
from Backend.services.rag_service import (
    RAGService,
    RAGServiceUnavailable,
)

router = APIRouter()

rag_service = RAGService()


_STOP_WORDS = {
    "a", "an", "and", "are", "be", "does", "for", "how", "in", "is",
    "of", "on", "the", "to", "what", "which", "with",
}
_DEFINITION_RE = re.compile(
    r"\bwhat\s+(?:is|are)|\bwhat\s+does\b|\bdefine\b|\bmeaning\s+of\b",
    re.IGNORECASE,
)


def _answer_from_evidence(
    question: str,
    evidence: list[dict],
) -> tuple[str, set[int]]:
    """Build a concise extractive answer from the most relevant evidence sentences."""
    question_terms = {
        term
        for term in re.findall(r"[a-z0-9]+", question.lower())
        if term not in _STOP_WORDS and len(term) > 2
    }
    candidates: list[tuple[float, int, str]] = []
    for chunk_index, chunk in enumerate(evidence):
        semantic_score = float(chunk.get("score", 0.0))
        chunk_text = str(chunk.get("text", ""))
        abstract_bonus = (
            0.12
            if re.search(r"\babstract\b", chunk_text[:250], re.IGNORECASE)
            else 0.0
        )
        for sentence in _sentences(chunk.get("text", "")):
            sentence_terms = set(re.findall(r"[a-z0-9]+", sentence.lower()))
            overlap = len(question_terms & sentence_terms)
            if overlap == 0:
                continue
            reference_count = len(re.findall(r"\[\d+\]", sentence))
            if reference_count >= 3:
                continue
            definition_bonus = 0.0
            if _DEFINITION_RE.search(question):
                cue_pattern = (
                    r"\b(?:is a|is an|means|refers to|called|designed to|"
                    r"consists of|introduce)\b"
                )
                if re.search(cue_pattern, sentence, re.IGNORECASE):
                    definition_bonus += 0.04
                for term in question_terms:
                    escaped_term = re.escape(term)
                    if re.search(
                        rf"(?:\b{escaped_term}\b.{{0,20}}{cue_pattern}|"
                        rf"{cue_pattern}.{{0,20}}\b{escaped_term}\b)",
                        sentence,
                        re.IGNORECASE,
                    ):
                        definition_bonus += 0.18
                        break
                if question_terms and question_terms <= sentence_terms:
                    definition_bonus += 0.08
                if re.search(
                    r"\b(?:table|appendix|ablation|results?)\b",
                    sentence,
                    re.IGNORECASE,
                ):
                    definition_bonus -= 0.08
            candidates.append(
                (
                    semantic_score + min(overlap, 4) * 0.035
                    + abstract_bonus
                    + definition_bonus
                    - reference_count * 0.02,
                    chunk_index,
                    sentence.strip(),
                )
            )

    if not candidates:
        return str(evidence[0].get("text", "")).strip(), {0}

    candidates.sort(key=lambda item: (item[0], -item[1]), reverse=True)
    selected: list[str] = []
    if _DEFINITION_RE.search(question):
        primary_document = evidence[0].get("document_id")
        same_document = [
            item
            for item in candidates
            if evidence[item[1]].get("document_id") == primary_document
        ]
        if same_document:
            candidates = same_document
        top_chunk = [item for item in candidates if item[1] == 0]
        if top_chunk:
            candidates = top_chunk
    primary_chunk = candidates[0][1]
    primary_candidates = [
        item for item in candidates if item[1] == primary_chunk
    ]
    for _, _, sentence in primary_candidates[:3]:
        selected.append(sentence)
    return " ".join(selected), {primary_chunk}


def _sentences(text: str) -> Iterable[str]:
    """Split extracted PDF prose without treating decimal points as boundaries."""
    abstract_match = re.search(r"\babstract\b", text[:250], re.IGNORECASE)
    if abstract_match:
        text = text[abstract_match.end():]
    for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", text):
        if len(sentence.strip()) >= 35:
            cleaned = _clean_sentence(sentence)
            if len(cleaned) >= 35:
                yield cleaned


def _clean_sentence(sentence: str) -> str:
    """Remove common PDF figure labels and uppercase section headings."""
    cleaned = re.sub(
        r"^Figure\s+\d+\s*:\s*[^.]+\.\s*",
        "",
        sentence.strip(),
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"^[A-Z][A-Z\s&:-]{5,}\s+(?=(?:In|The|A|This)\b)",
        "",
        cleaned,
    )
    return cleaned.strip()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        evidence = rag_service.retrieve(
            request.question,
            request.filters,
        )

        if not evidence:
            return ChatResponse(
                answer="No supporting evidence was found in the library documents.",
                citations=[],
                has_evidence=False,
            )

        answer, used_chunks = _answer_from_evidence(request.question, evidence)
        return ChatResponse(
            answer=answer,
            citations=[
                {
                    "citation_id": index + 1,
                    "chunk_id": chunk.get("chunk_id"),
                    "document_id": chunk["document_id"],
                    "title": chunk["metadata"].get("title")
                    or chunk["document_id"],
                    "author": chunk["metadata"].get("author"),
                    "excerpt": chunk.get("text"),
                    "page": chunk.get("page"),
                    "section": chunk.get("section"),
                    "source_url": chunk["metadata"].get("source_url"),
                    "score": chunk.get("score"),
                    "metadata": chunk["metadata"],
                }
                for index, chunk in enumerate(evidence)
                if index in used_chunks
            ],
            has_evidence=True,
        )

    except RAGServiceUnavailable as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected backend error occurred.",
        )