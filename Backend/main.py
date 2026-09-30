from fastapi import FastAPI

from Backend.routes.chat import router as chat_router
from Backend.routes.health import router as health_router


app = FastAPI(
    title="University Library Research Assistant API",
    description="Backend API for the University Library Research Assistant",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(chat_router)