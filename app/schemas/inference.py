"""
Pydantic models for the inference (query → answer) workflow.
"""

from pydantic import BaseModel
from typing import List, Optional, Any


# ── Request body for /inference/query ──
class InferenceRequest(BaseModel):
    doc_id: str
    query: str


# ── A single retrieved node returned to the caller ──
class RetrievedNode(BaseModel):
    node_id: str
    title: Optional[str] = None
    page_index: Optional[Any] = None
    text_preview: Optional[str] = None   # first N chars of node text


# ── Tree-search reasoning step ──
class TreeSearchResult(BaseModel):
    thinking: str
    node_list: List[str]
    retrieved_nodes: List[RetrievedNode]


# ── Final response ──
class InferenceResponse(BaseModel):
    doc_id: str
    query: str
    tree_search: TreeSearchResult
    context_preview: str       # truncated relevant_content (first 1000 chars)
    answer: str
