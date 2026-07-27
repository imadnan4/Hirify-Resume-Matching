from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import candidates, jobs, matching, resumes
from app.core.config import settings
from app.core.database import init_db
from app.models import Base  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Frontend-first backend for Hirify resume/job matching",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    )

    @app.get("/")
    def root():
        return {"message": "Hirify API is running", "version": settings.app_version}

    @app.get("/health")
    def health():
        return {"status": "healthy", "message": "API is running"}

    app.include_router(resumes.router, prefix=f"{settings.api_prefix}/resumes", tags=["Resumes"])
    app.include_router(jobs.router, prefix=f"{settings.api_prefix}/jobs", tags=["Jobs"])
    app.include_router(candidates.router, prefix=f"{settings.api_prefix}/candidates", tags=["Candidates"])
    app.include_router(matching.router, prefix=f"{settings.api_prefix}/matching", tags=["Matching"])
    return app


app = create_app()
