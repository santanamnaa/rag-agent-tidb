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

## Ask a question

```bash
python scripts/chat.py "Apa itu TiDB Cloud?"
```

## Notes

- Embeddings use `BAAI/bge-m3` with 1024 dims; TiDB column is `VECTOR(1024)`.
- Retrieval orders by cosine distance using `VEC_COSINE_DISTANCE`.
- If your TiDB version supports vector indexes, uncomment the index DDL in `rag_agent/schema.py`.
