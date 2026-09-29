from fastapi import APIRouter  # type: ignore[import-not-found]

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok"}