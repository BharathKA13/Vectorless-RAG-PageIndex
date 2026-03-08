"""
Central API router – registers all sub-routers with their prefixes.
"""

from fastapi import APIRouter
from app.api.routes import documents, inference

router = APIRouter(prefix="/api/v1")

router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(inference.router, prefix="/inference", tags=["inference"])
