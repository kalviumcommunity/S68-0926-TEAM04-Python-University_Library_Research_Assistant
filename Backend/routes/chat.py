import re

from fastapi import APIRouter, HTTPException, status

from Backend.schemas.chat import ChatRequest, ChatResponse
from Backend.services.rag_service import (
    RAGService,
    RAGServiceUnavailable,
)

router = APIRouter()

rag_service = RAGService()


def _answer_from_evidence(evidence: list[dict]) -> str:
    """Select the strongest semantic evidence, breaking ties by prose quality."""
    def quality(chunk: dict) -> tuple[float, int]:
        text = chunk.get("text", "")
        reference_count = len(re.findall(r"\[\d+\]", text))
        starts_like_references = int(
            text.lower().lstrip().startswith(("references", "bibliography"))
        )
        return (
            float(chunk.get("score", 0.0)),
            -(reference_count + (starts_like_references * 10)),
        )

    return max(evidence, key=quality)["text"]


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

        return ChatResponse(
            answer=_answer_from_evidence(evidence),
            citations=[
                {
                    "citation_id": index,
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
                for index, chunk in enumerate(evidence, start=1)
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