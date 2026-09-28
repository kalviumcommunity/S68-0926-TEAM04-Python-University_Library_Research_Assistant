from fastapi import APIRouter  # type: ignore[import-not-found]

from schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    return ChatResponse(
        answer="RAG and LLM integration is not implemented yet.",
        citations=[],
    )