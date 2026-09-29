from fastapi import APIRouter, HTTPException, status

from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.rag_service import (
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

        return ChatResponse(
            answer="RAG evidence retrieved successfully.",
            citations=[],
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