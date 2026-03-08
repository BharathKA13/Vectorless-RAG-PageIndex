"""
Entrypoint for the Document Intelligence – PageIndex (Vectorless RAG) API.

Run with:
    uvicorn app.main:app --reload
"""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.router import router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Document Intelligence – PageIndex API",
    description=(
        "Vectorless RAG pipeline powered by PageIndex document trees and "
        "OpenAI LLMs.  Upload a PDF, let PageIndex build a hierarchical "
        "tree, then query the document with natural language."
    ),
    version="1.0.0",
)

# ── API routes ───────────────────────────────────────────────────
app.include_router(router)

# ── Serve static assets (CSS / JS) ──────────────────────────────
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# ── Serve the SPA on root ────────────────────────────────────────
@app.get("/", tags=["ui"])
async def serve_ui():
    return FileResponse(str(BASE_DIR / "static" / "index.html"))


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "message": "Document Intelligence API is running."}
