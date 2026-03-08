"""
Tests for the /api/v1/documents endpoints.
"""

import io
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ── Upload ───────────────────────────────────────────────────────────────
def test_upload_pdf_success():
    """Uploading a valid PDF should return 200 with a doc_id."""
    fake_doc_id = "abc-123"
    with patch(
        "app.services.document_service.document_service.submit_document",
        new_callable=AsyncMock,
        return_value=fake_doc_id,
    ):
        pdf_bytes = b"%PDF-1.4 fake content"
        response = client.post(
            "/api/v1/documents/upload",
            files={"file": ("test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["doc_id"] == fake_doc_id
    assert data["filename"] == "test.pdf"


def test_upload_non_pdf_rejected():
    """Non-PDF uploads should be rejected with 400."""
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert response.status_code == 400
    assert "PDF" in response.json()["detail"]


# ── Status ───────────────────────────────────────────────────────────────
def test_status_check():
    """GET /{doc_id}/status should reflect readiness."""
    with patch(
        "app.services.document_service.document_service.is_ready",
        return_value=True,
    ):
        response = client.get("/api/v1/documents/test-doc/status")

    assert response.status_code == 200
    assert response.json()["ready"] is True


# ── List ─────────────────────────────────────────────────────────────────
def test_list_documents():
    """GET /documents/ should return a list."""
    with patch(
        "app.services.document_service.document_service.list_documents",
        return_value=[{"doc_id": "d1", "filename": "a.pdf"}],
    ):
        response = client.get("/api/v1/documents/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
