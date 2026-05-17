import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.database import Base, engine
from app.exceptions import AppException
from app.middleware import RequestIDMiddleware, RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.models import Document, DocumentChunk, Conversation
from app.services.vector_store_service import get_chroma_client


def _setup_logging():
    try:
        from pythonjsonlogger import jsonlogger
        handler = logging.StreamHandler()
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            timestamp=True,
        )
        handler.setFormatter(formatter)
        logging.basicConfig(
            level=logging.DEBUG if settings.DEBUG else logging.INFO,
            handlers=[handler],
            force=True,
        )
    except ImportError:
        logging.basicConfig(
            level=logging.DEBUG if settings.DEBUG else logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


_setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    logger.info("Initializing ChromaDB...")
    get_chroma_client()
    logger.info("Startup complete")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.message, "data": None},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal server error", "data": None},
    )
