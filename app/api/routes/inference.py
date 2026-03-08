"""
Inference route – accepts a query + doc_id and returns an LLM-generated answer.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.inference import InferenceRequest, InferenceResponse
from app.services.inference_service import perform_inference

router = APIRouter()


@router.post("/query", response_model=InferenceResponse)
async def query_document(request: InferenceRequest):
    """Run the full vectorless RAG pipeline:

    1. Retrieve the document tree from PageIndex.
    2. Ask the LLM to identify relevant tree nodes.
    3. Assemble context from those nodes.
    4. Ask the LLM to answer the question.
    """
    try:
        result = await perform_inference(request.doc_id, request.query)
        return InferenceResponse(**result)
    except TimeoutError as e:
        raise HTTPException(status_code=408, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
