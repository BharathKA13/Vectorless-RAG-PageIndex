"""
Document routes – upload, status, tree retrieval, listing.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

from app.schemas.document import (
    DocumentSubmitResponse,
    DocumentStatusResponse,
    DocumentTreeResponse,
    DocumentListItem,
)
from app.services.document_service import document_service, PageIndexSubmitError

router = APIRouter()


@router.post("/upload", response_model=DocumentSubmitResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF and submit it to PageIndex for processing."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        file_bytes = await file.read()
        doc_id = await document_service.submit_document(file.filename, file_bytes)
        return DocumentSubmitResponse(doc_id=doc_id, filename=file.filename)
    except PageIndexSubmitError as e:
        detail = str(e)
        if "Invalid" in detail or "corrupted" in detail or "PdfReadError" in detail:
            raise HTTPException(status_code=400, detail=f"Invalid PDF: {detail}")
        if "LimitReached" in detail:
            raise HTTPException(status_code=429, detail=f"PageIndex quota exceeded: {detail}")
        raise HTTPException(status_code=502, detail=f"PageIndex error: {detail}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}/status", response_model=DocumentStatusResponse)
async def check_status(doc_id: str):
    """Check whether PageIndex has finished processing the document."""
    try:
        ready = document_service.is_ready(doc_id)
        return DocumentStatusResponse(doc_id=doc_id, ready=ready)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{doc_id}/tree", response_model=DocumentTreeResponse)
async def get_tree(doc_id: str):
    """Retrieve the full document tree (blocks until ready)."""
    try:
        tree = document_service.get_tree(doc_id)
        return DocumentTreeResponse(doc_id=doc_id, tree=tree)
    except TimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[DocumentListItem])
async def list_documents():
    """List all submitted documents."""
    return document_service.list_documents()
