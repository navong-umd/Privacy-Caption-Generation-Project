"""FastAPI application entry point for the research API.

Run:  uvicorn webapi.main:app --reload --port 8000
Docs: http://localhost:8000/docs   OpenAPI: http://localhost:8000/openapi.json
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from webapi import __version__
from webapi.config import ALLOWED_ORIGINS
from webapi.routes import router

app = FastAPI(
    title="Privacy Caption Generation — Research API",
    version=__version__,
    description=(
        "Read-only API over the committed pipeline artifacts (the blessed 7-app / "
        "10,721-PRCS corpus run). Every value is served from a real artifact; missing "
        "data is reported as such, never fabricated."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1024)

app.include_router(router)


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Never leak a stack trace to the client.
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Internal server error while reading research artifacts."},
    )
