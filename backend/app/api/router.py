from fastapi import APIRouter

from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.tasks import router as tasks_router

api_router = APIRouter()

api_router.include_router(documents_router)
api_router.include_router(chat_router)
api_router.include_router(tasks_router)


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}
