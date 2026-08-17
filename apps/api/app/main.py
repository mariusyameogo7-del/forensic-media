import os
import traceback
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from apps.api.app.core.config import settings
from apps.api.app.core.errors import AppError
from apps.api.app.api.v1.router import api_router

app = FastAPI(
    title="Plateforme africaine de vérification numérique - API",
    description="Backend d'analyse de provenance, d'intégrité et de contexte des médias numériques.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"[GLOBAL SERVER ERROR] {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": str(exc),
            "traceback": tb.splitlines()[-3:] if settings.DEBUG else [str(exc)],
        },
    )

# Include API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve Web UI at root
STATIC_FILE_PATH = Path(__file__).resolve().parent / "static" / "index.html"


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_root_ui():
    """Serves the interactive forensic verification web UI."""
    if STATIC_FILE_PATH.exists():
        return FileResponse(STATIC_FILE_PATH)
    return HTMLResponse("<h1>Forensic Media API is running.</h1><p>Visit <a href='/docs'>/docs</a></p>")
