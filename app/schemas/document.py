"""
Pydantic models for document-related request / response payloads.
"""

from pydantic import BaseModel
from typing import Optional, List, Any


# ── Response returned after a document is submitted ──
class DocumentSubmitResponse(BaseModel):
    doc_id: str
    filename: str
    message: str = "Document submitted to PageIndex for processing."


# ── Response returned when checking processing status ──
class DocumentStatusResponse(BaseModel):
    doc_id: str
    ready: bool


# ── Tree node (recursive) ──
class TreeNodeResponse(BaseModel):
    node_id: str
    title: Optional[str] = None
    summary: Optional[str] = None
    page_index: Optional[Any] = None
    children: Optional[List["TreeNodeResponse"]] = None

    model_config = {"from_attributes": True}


# ── Full tree response ──
class DocumentTreeResponse(BaseModel):
    doc_id: str
    tree: Any  # raw dict tree from PageIndex SDK


# ── Listing ──
class DocumentListItem(BaseModel):
    doc_id: str
    filename: str
