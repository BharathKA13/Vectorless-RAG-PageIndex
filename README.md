# Vectorless RAG — Structure-Aware Retrieval Without Embeddings

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/OpenAI-GPT--4.1-412991?logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/PageIndex-Powered-4f46e5" />
  <img src="https://img.shields.io/badge/License-MIT-green" />
</p>

> **What if you could build a production RAG pipeline with zero vector infrastructure?**
>
> No Pinecone. No ChromaDB. No Weaviate. No embedding models. No chunking strategies to tune.
>
> This project replaces similarity search with **LLM-driven tree navigation** — the model reasons over a document's hierarchical structure to find exactly the right sections, then generates grounded answers.

---

## Why This Matters

Traditional RAG pipelines require significant infrastructure overhead:

| Traditional RAG | Vectorless RAG (this project) |
|:---|:---|
| Chunk documents → embed → store in vector DB | Upload PDF → PageIndex builds a document tree |
| Tune chunk size, overlap, embedding model | Zero chunking parameters to tune |
| Deploy & manage a vector database | No database infrastructure needed |
| Similarity search (often noisy) | LLM reasons over structure (precise) |
| Lost document structure | Preserves sections, hierarchy, page indices |

**Result:** Faster prototyping, lower infrastructure costs, and retrieval that understands *document structure* — not just token similarity.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Client (Web UI)                    │
│              Drag & Drop Upload · Query Interface       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP
┌────────────────────────▼─────────────────────────────────┐
│                    FastAPI Server                        │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐   │
│  │  Routes   │→│   Schemas    │→│     Services       │   │
│  │ /upload   │  │  Pydantic v2 │  │ DocumentService  │   │
│  │ /status   │  │  Validation  │  │ InferenceService │   │
│  │ /tree     │  └──────────────┘  └──────┬───────────┘   │
│  │ /query    │                           │               │
│  └──────────┘                            │               │
└──────────────────────────────────────────┼───────────────┘
                                           │
               ┌───────────────────────────┼───────────────┐
               │                           │               │
       ┌───────▼────────┐           ┌───────▼────────┐     │
       │   PageIndex    │           │     OpenAI     │     │
       │   • Parse PDF  │           │  • Tree Search │     │
       │   • Build Tree │           │  • Answer Gen  │     │
       │   • Summaries  │           │  (async calls) │     │
       └────────────────┘           └────────────────┘     │
               └───────────────────────────────────────────┘
```

### The Two-Stage Retrieval Pipeline

```
         ┌──────────────┐
         │  User Query   │
         └──────┬───────┘
                │
    ┌───────────▼────────────┐
    │  STAGE 1: Tree Search  │  LLM receives document tree (titles + summaries)
    │  "Which sections are   │  and reasons about which nodes contain the answer.
    │   relevant to this     │  Returns: thinking process + node_id list
    │   question?"           │
    └───────────┬────────────┘
                │
    ┌───────────▼────────────┐
    │  STAGE 2: Answer Gen   │  Full text from selected nodes is assembled
    │  "Answer based on      │  as context. LLM generates a grounded answer.
    │   this context."       │
    └───────────┬────────────┘
                │
    ┌───────────▼─────────────┐
    │     Structured Response │
    │  • Reasoning trace      │
    │  • Retrieved nodes      │
    │  • Context preview      │
    │  • Final answer         │
    └─────────────────────────┘
```

---

## Key Features

- **Zero-Vector Retrieval** — Tree-based document navigation replaces embedding + similarity search
- **Full-Stack Application** — FastAPI backend + responsive SPA frontend, no build step required
- **Async Pipeline** — Non-blocking OpenAI calls with `AsyncOpenAI` for production throughput
- **Interactive Notebooks** — Step-by-step RAG walkthroughs for experimentation and learning
- **Transparent Reasoning** — Every query returns the LLM's thinking process alongside the answer
- **Production Patterns** — Pydantic v2 schemas, `pydantic-settings` config, structured error handling, health checks
- **Test Suite** — Pytest tests with mocked external dependencies for fast, offline CI

---

## Quick Start

## API Reference

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/documents/upload` | Upload a PDF document for processing |
| `GET` | `/api/v1/documents/` | List all submitted documents |
| `GET` | `/api/v1/documents/{doc_id}/status` | Check processing readiness |
| `GET` | `/api/v1/documents/{doc_id}/tree` | Retrieve hierarchical document tree |

### Inference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/inference/query` | Run vectorless RAG query against a document |

<details>
<summary><b>Example: Query a Document</b></summary>

**Response:**
```json
{
  "doc_id": "abc123",
  "query": "What are the main contributions of this paper?",
  "reasoning": "The question asks about contributions, which is typically found in...",
  "node_list": [
    {"node_id": "1.1", "title": "Introduction", "page_index": 1},
    {"node_id": "1.2", "title": "Contributions", "page_index": 2}
  ],
  "context_preview": "In this paper, we present three key contributions...",
  "answer": "The paper presents three main contributions: ..."
}
```

</details>

---

---

## Project Structure

```
├── app/
│   ├── api/
│   │   ├── router.py              # Versioned API router (/api/v1)
│   │   └── routes/
│   │       ├── documents.py       # Upload, status, tree endpoints
│   │       └── inference.py       # RAG query endpoint
│   ├── core/
│   │   └── config.py              # pydantic-settings configuration
│   ├── schemas/
│   │   ├── document.py            # Request/response models for documents
│   │   └── inference.py           # Request/response models for inference
│   ├── services/
│   │   ├── document_service.py    # PageIndex SDK integration
│   │   └── inference_service.py   # Two-stage RAG pipeline
│   ├── static/                    # SPA frontend (HTML/CSS/JS)
│   ├── utils/
│   │   └── notebook_adapter.py    # Notebook ↔ service utilities
│   └── main.py                    # FastAPI app entrypoint
├── notebooks/                     # Interactive Jupyter demos
├── tests/                         # Pytest suite with mocked dependencies
├── requirements.txt
├── .env.example                   # Environment variable template
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **API Framework** | FastAPI with async/await |
| **Validation** | Pydantic v2 + pydantic-settings |
| **Document Intelligence** | PageIndex SDK (tree parsing, summaries) |
| **LLM** | OpenAI GPT-4.1 (configurable) |
| **Frontend** | Vanilla JS SPA — zero build dependencies |
| **Testing** | pytest + httpx TestClient |

---

## Running Tests

```bash
pytest tests/ -v
```

All external services (PageIndex, OpenAI) are mocked — tests run fast and offline.

---

## Configuration

All settings are managed via environment variables (see [`.env.example`](.env.example)):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PAGEINDEX_API_KEY` | Yes | — | PageIndex API key |
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `OPENAI_MODEL` | No | `gpt-4.1` | Chat model to use |
| `OPENAI_TEMPERATURE` | No | `0.0` | LLM temperature (0.0–2.0) |
| `UPLOAD_DIR` | No | `data` | Directory for uploaded PDFs |
| `POLL_INTERVAL` | No | `5` | Seconds between readiness polls |
| `MAX_WAIT_SECONDS` | No | `300` | Max wait for document processing |

---

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a PR.

## License

[MIT](LICENSE)
