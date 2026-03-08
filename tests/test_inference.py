"""
Tests for the /api/v1/inference endpoints.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

FAKE_INFERENCE_RESULT = {
    "doc_id": "abc-123",
    "query": "What is the main finding?",
    "tree_search": {
        "thinking": "Node 1 covers results",
        "node_list": ["node_1"],
        "retrieved_nodes": [
            {
                "node_id": "node_1",
                "title": "Results",
                "page_index": 3,
                "text_preview": "The main finding is...",
            }
        ],
    },
    "context_preview": "The main finding is that...",
    "answer": "The main finding is that the approach improves accuracy by 15%.",
}


def test_query_success():
    """POST /inference/query should return a full inference result."""
    with patch(
        "app.api.routes.inference.perform_inference",
        new_callable=AsyncMock,
        return_value=FAKE_INFERENCE_RESULT,
    ):
        response = client.post(
            "/api/v1/inference/query",
            json={"doc_id": "abc-123", "query": "What is the main finding?"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["doc_id"] == "abc-123"
    assert data["answer"]
    assert len(data["tree_search"]["node_list"]) > 0


def test_query_missing_fields():
    """Omitting required fields should return 422."""
    response = client.post("/api/v1/inference/query", json={})
    assert response.status_code == 422
