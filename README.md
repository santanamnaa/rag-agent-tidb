# RAG Agent with TiDB Cloud and DeepSeek (Ollama)

This project is a minimal Retrieval-Augmented Generation (RAG) agent that stores document chunks and 1024‑dim embeddings in TiDB Cloud (`VECTOR(1024)`), retrieves the most relevant chunks via cosine similarity, and prompts a local LLM (DeepSeek via Ollama) to answer user questions grounded in your data. It includes scripts to initialize the schema, ingest a CSV knowledge base, and run a chat query end‑to‑end.

## Prerequisites

- Python 3.9+
- TiDB Cloud Serverless (5GB free)
- Ollama running locally with a DeepSeek model (`deepseek-llm:latest`)

## Setup

1. Copy env

```bash
cp .env.example .env
# Fill TIDB_HOST, TIDB_USER, TIDB_PASSWORD, TIDB_DATABASE
```

2. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .[full]
```

3. Initialize schema

```bash
python scripts/init_db.py
```

## Ingest CSV

CSV must include a `text` column. Optional `id` or `source` columns.

```bash
python scripts/ingest_csv.py data/knowledge.csv --text_col text --id_col id --source_col source
```

## Run the model (first-time warm-up)

Ensure the model is downloaded and responsive, then Ctrl+C to exit:

```bash
ollama run deepseek-llm:latest
```

## Ask a question (CLI)

```bash
python scripts/chat.py "Apa itu TiDB Cloud?"
```

## Run API server (FastAPI)

```bash
uvicorn scripts.api:app --host 0.0.0.0 --port 8000 --reload
```

Environment:

- `ALLOWED_ORIGINS`: comma-separated origins for CORS. Default: `http://localhost:5173,http://127.0.0.1:5173`.
- `SENTRY_DSN`: optional; enable error reporting if set.

Endpoints:

- `GET /health` → `{ "status": "ok" }`
- `GET /metrics` → Prometheus exposition format
- `POST /chat` → body `{ "query": string, "k"?: number, "session_id"?: string }` returns `{ answer, sources }`

Example:

```bash
curl -X POST http://localhost:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"query":"Apa itu TiDB Cloud?","k":5,"session_id":"abc123"}'
```

## Run Frontend (Vite + React)

```bash
cd frontend
npm install
npm run dev
```

- API base defaults to `http://localhost:8000`. Override via `frontend/.env`:

```env
VITE_API_BASE=http://localhost:8000
```

- The UI persists a `session_id` in `localStorage` to enable multi-turn memory using TiDB tables `chat_sessions` and `chat_messages`.

## Docker

Build and run with Compose:

```bash
docker compose up --build
```

Images/targets:

- API: multi-stage `Dockerfile` target `api` (exposes 8000)
- Frontend: `frontend` (Nginx serving built assets on 5173 via compose)

Compose uses environment variables for TiDB connection and optional `SENTRY_DSN`.

## Notes

- Embeddings use `BAAI/bge-m3` with 1024 dims; TiDB column is `VECTOR(1024)`.
- Retrieval orders by cosine distance using `VEC_COSINE_DISTANCE`.
- If your TiDB version supports vector indexes, uncomment the index DDL in `rag_agent/schema.py`.
