"""FastAPI application entry point."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.interview import router as interview_router
from app.services.curriculum_service import curriculum_service
from app.rag.retriever import retriever
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("startup")
    # Load curriculum and build RAG index
    curriculum_service.load()
    retriever.build_index()
    logger.info("startup_complete", rag_ready=True)
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="Interview Intelligence Engine",
        description="Adaptive AI technical interviewer with curriculum-grounded RAG",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routes
    app.include_router(interview_router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "rag_ready": retriever._initialized}

    return app


app = create_app()
