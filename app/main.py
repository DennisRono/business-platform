from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from business_platform.core.config import settings
from business_platform.core.exceptions import register_exception_handlers
from business_platform.core.logging import configure_logging, get_logger
from business_platform.middleware.audit import AuditMiddleware
from business_platform.middleware.permission_checker import PermissionCheckerMiddleware
from business_platform.middleware.rate_limit import RateLimitMiddleware
from business_platform.middleware.security_headers import SecurityHeadersMiddleware

_STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging(debug=settings.DEBUG)
    logger = get_logger("app.main")
    logger.info("Starting %s (env=%s)", settings.PROJECT_NAME, settings.ENVIRONMENT)
    yield
    logger.info("Shutting down %s", settings.PROJECT_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        # Serve interactive docs at /docs via the RapiDoc explorer (below);
        # keep Swagger/ReDoc available too for convenience.
        docs_url="/swagger",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(PermissionCheckerMiddleware)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    if _STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

    @app.get("/health", tags=["meta"], summary="Liveness probe")
    async def health() -> JSONResponse:
        return JSONResponse({"status": "ok", "service": settings.PROJECT_NAME})

    @app.get("/docs", include_in_schema=False)
    async def rapidoc() -> FileResponse:
        return FileResponse(str(_STATIC_DIR / "docs.html"))

    @app.get("/", tags=["meta"], summary="Service metadata")
    async def root() -> JSONResponse:
        return JSONResponse(
            {
                "service": settings.PROJECT_NAME,
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
                "docs": "/docs",
                "openapi": "/openapi.json",
                "api_prefix": settings.API_V1_PREFIX,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=settings.DEBUG,
    )
