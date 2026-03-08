"""
Document service – handles file persistence and PageIndex submission / polling.

This mirrors notebook cells 1, 3, and 4 of 02_vectorless.ipynb.
"""

import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

from pageindex import PageIndexClient
import pageindex.utils as pi_utils

from app.core.config import settings


class PageIndexSubmitError(Exception):
    """Raised when PageIndex rejects a document submission."""
    pass


class DocumentService:
    """Thin wrapper around PageIndex SDK + local file storage."""

    def __init__(self) -> None:
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.pi_client = PageIndexClient(api_key=settings.PAGEINDEX_API_KEY)

        # In-memory registry: doc_id → {"filename": str, "tree": dict | None}
        self._registry: Dict[str, Dict[str, Any]] = {}

    # ── 1. Save uploaded file to disk & submit to PageIndex ──────────────
    async def submit_document(self, filename: str, file_bytes: bytes) -> str:
        """Persist the PDF locally and submit it to PageIndex.

        Returns the doc_id issued by PageIndex.
        """
        file_path = self.upload_dir / filename
        file_path.write_bytes(file_bytes)

        try:
            result = self.pi_client.submit_document(str(file_path))
        except Exception as e:
            raise PageIndexSubmitError(str(e)) from e

        doc_id: str = result["doc_id"]
        self._registry[doc_id] = {"filename": filename, "tree": None}
        return doc_id

    # ── 2. Poll until the document tree is ready ─────────────────────────
    def wait_for_tree(self, doc_id: str) -> Dict[str, Any]:
        """Block until PageIndex has finished processing and return the tree.

        Exactly mirrors the polling loop in notebook cell 4.
        """
        max_wait = settings.MAX_WAIT_SECONDS
        interval = settings.POLL_INTERVAL
        start = time.time()

        while time.time() - start < max_wait:
            if self.pi_client.is_retrieval_ready(doc_id):
                tree = self.pi_client.get_tree(doc_id, node_summary=True)["result"]
                if doc_id in self._registry:
                    self._registry[doc_id]["tree"] = tree
                else:
                    self._registry[doc_id] = {"filename": "unknown", "tree": tree}
                return tree
            time.sleep(interval)

        raise TimeoutError(
            f"PageIndex did not finish processing doc_id={doc_id} "
            f"within {max_wait} seconds."
        )

    # ── 3. Check readiness without blocking ──────────────────────────────
    def is_ready(self, doc_id: str) -> bool:
        return self.pi_client.is_retrieval_ready(doc_id)

    # ── 4. Get cached tree or fetch on-demand ────────────────────────────
    def get_tree(self, doc_id: str) -> Dict[str, Any]:
        """Return the document tree. If not cached, block-fetch it."""
        entry = self._registry.get(doc_id)
        if entry and entry.get("tree"):
            return entry["tree"]
        return self.wait_for_tree(doc_id)

    # ── 5. List submitted documents ──────────────────────────────────────
    def list_documents(self) -> List[Dict[str, str]]:
        return [
            {"doc_id": did, "filename": info["filename"]}
            for did, info in self._registry.items()
        ]


# Module-level singleton
document_service = DocumentService()
