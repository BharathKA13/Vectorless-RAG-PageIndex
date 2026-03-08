# Vectorless RAG with PageIndex

A **vector-database-free** Retrieval-Augmented Generation (RAG) system powered by [PageIndex](https://pageindex.ai) and OpenAI. Instead of chunking documents into embeddings, this approach uses PageIndex's document tree structure for intelligent, structure-aware retrieval.

## How It Works

1. **Upload** a PDF document to PageIndex
2. **PageIndex** builds a hierarchical tree of the document (sections, subsections, summaries)
3. An **LLM navigates the tree** to find relevant nodes for a given query
4. The text from those nodes is used as **context** for answer generation

No vector database. No embedding model. No chunking strategy to tune.

## Project Structure

```
├── app/
│   ├── api/routes/          # FastAPI route handlers
│   ├── core/config.py       # Settings via pydantic-settings
│   ├── schemas/             # Request/response models
│   ├── services/            # Business logic (document + inference)
│   ├── static/              # Web UI (HTML/CSS/JS)
│   └── utils/               # Notebook adapter utilities
├── notebooks/
│   ├── 01.ipynb             # End-to-end RAG walkthrough
│   └── 02_vectorless.ipynb  # Vectorless RAG demo
├── tests/                   # Pytest test suite
├── requirements.txt
└── .env.example             # Template for required env vars
```

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/BharathKA13/Vectorless-RAG-PageIndex.git
cd Vectorless-RAG-PageIndex
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and add your real API keys:
- **`PAGEINDEX_API_KEY`** — get one at [dash.pageindex.ai/api-keys](https://dash.pageindex.ai/api-keys)
- **`OPENAI_API_KEY`** — get one at [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 3. Run the API server

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) for the web UI, or [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the Swagger docs.

### 4. Try the notebooks

```bash
jupyter notebook notebooks/
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/documents/upload` | Upload a PDF document |
| `GET` | `/api/documents/{doc_id}/status` | Check processing status |
| `GET` | `/api/documents/{doc_id}/tree` | Get document tree structure |
| `POST` | `/api/inference/query` | Ask a question about a document |

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

MIT