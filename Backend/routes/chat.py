from fastapi import APIRouter, HTTPException, status

from Backend.schemas.chat import ChatRequest, ChatResponse
from Backend.services.rag_service import (
    RAGService,
    RAGServiceUnavailable,
)

router = APIRouter()

rag_service = RAGService()


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
            )

        return ChatResponse(
            answer=evidence[0]["text"],
            citations=[
                {
                    "document_id": chunk["document_id"],
                    "title": chunk["metadata"].get("title")
                    or chunk["document_id"],
                    "excerpt": chunk.get("text"),
                    "page": chunk.get("page"),
                    "section": chunk.get("section"),
                    "metadata": chunk["metadata"],
                }
                for chunk in evidence
            ],
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