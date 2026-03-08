"""
Inference service – tree search + answer generation using OpenAI.

This mirrors notebook cells 2, 5, 6, 7, and 8 of 02_vectorless.ipynb.
"""

import json
from typing import Any, Dict, List, Tuple

import openai
import pageindex.utils as pi_utils

from app.core.config import settings
from app.services.document_service import document_service


# ── LLM helper (exact copy from notebook cell 2) ────────────────────────
async def call_llm(prompt: str, model: str | None = None, temperature: float | None = None) -> str:
    """Call OpenAI chat completion and return the assistant's reply."""
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model=model or settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature if temperature is not None else settings.OPENAI_TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


# ── Tree search (notebook cell 5) ───────────────────────────────────────
async def search_tree(tree: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Use the LLM to identify relevant nodes in the document tree.

    Returns the parsed JSON with keys 'thinking' and 'node_list'.
    """
    tree_without_text = pi_utils.remove_fields(tree.copy(), fields=["text"])

    search_prompt = f"""
You are given a question and a tree structure of a document.
Each node contains a node id, node title, and a corresponding summary.
Your task is to find all nodes that are likely to contain the answer to the question.

Question: {query}

Document tree structure:
{json.dumps(tree_without_text, indent=2)}

Please reply in the following JSON format:
{{
    "thinking": "<Your thinking process on which nodes are relevant to the question>",
    "node_list": ["node_id_1", "node_id_2", ..., "node_id_n"]
}}
Directly return the final JSON structure. Do not output anything else.
"""

    raw = await call_llm(search_prompt)
    return json.loads(raw)


# ── Build context from retrieved nodes (cells 6 & 7) ────────────────────
def build_context(tree: Dict[str, Any], node_ids: List[str]) -> Tuple[str, List[Dict[str, Any]]]:
    """Return the concatenated text of retrieved nodes and their metadata.

    Returns (relevant_content, retrieved_nodes_info).
    """
    node_map = pi_utils.create_node_mapping(tree)
    retrieved_nodes_info: List[Dict[str, Any]] = []

    for nid in node_ids:
        node = node_map.get(nid)
        if node:
            retrieved_nodes_info.append({
                "node_id": node["node_id"],
                "title": node.get("title"),
                "page_index": node.get("page_index"),
                "text_preview": (node.get("text") or "")[:200],
            })

    relevant_content = "\n\n".join(
        node_map[nid]["text"] for nid in node_ids if nid in node_map
    )
    return relevant_content, retrieved_nodes_info


# ── Generate answer (notebook cell 8) ───────────────────────────────────
async def generate_answer(query: str, relevant_content: str) -> str:
    """Ask the LLM to answer the question using the retrieved context."""
    answer_prompt = f"""
Answer the question based on the context:

Question: {query}
Context: {relevant_content}

Provide a clear, concise answer based only on the context provided.
"""
    return await call_llm(answer_prompt)


# ── Public orchestrator (combines all steps) ─────────────────────────────
async def perform_inference(doc_id: str, query: str) -> Dict[str, Any]:
    """End-to-end inference: tree search → context retrieval → answer.

    Returns a dict ready to be serialised into InferenceResponse.
    """
    tree = document_service.get_tree(doc_id)

    # Step 1 – LLM tree search
    tree_search_json = await search_tree(tree, query)

    # Step 2 – Gather context
    node_ids = tree_search_json["node_list"]
    relevant_content, retrieved_nodes_info = build_context(tree, node_ids)

    # Step 3 – Generate answer
    answer = await generate_answer(query, relevant_content)

    return {
        "doc_id": doc_id,
        "query": query,
        "tree_search": {
            "thinking": tree_search_json["thinking"],
            "node_list": node_ids,
            "retrieved_nodes": retrieved_nodes_info,
        },
        "context_preview": relevant_content[:1000] + ("..." if len(relevant_content) > 1000 else ""),
        "answer": answer,
    }
