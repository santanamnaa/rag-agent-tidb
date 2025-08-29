#!/usr/bin/env python3
import uvicorn
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_agent.config import AppConfig
from rag_agent.embedding import Embedder
from rag_agent.retriever import search_top_k
from rag_agent.memory import ensure_session, add_message, get_recent_messages
import requests
import uuid
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response


class ChatRequest(BaseModel):
	query: str
	k: int = 5
	session_id: str | None = None


class ChatResponse(BaseModel):
	answer: str
	sources: list


def call_ollama(base_url: str, model: str, prompt: str) -> str:
	try:
		resp = requests.post(
			f"{base_url}/api/generate",
			json={"model": model, "prompt": prompt, "stream": False},
			timeout=600,
		)
		resp.raise_for_status()
		data = resp.json()
		return data.get("response") or data.get("message", {}).get("content", "")
	except requests.RequestException as e:
		raise HTTPException(status_code=502, detail=f"LLM request failed: {e}")


# Sentry init (no-op if DSN missing)
_dsn = os.getenv("SENTRY_DSN")
if _dsn:
	sentry_sdk.init(dsn=_dsn, integrations=[FastApiIntegration()])

app = FastAPI(title="RAG Agent API", version="0.1.0")
# Prometheus metrics
REQUESTS_TOTAL = Counter("rag_requests_total", "Total requests", ["endpoint"])
CHATS_TOTAL = Counter("rag_chats_total", "Total chat requests")


# Allow local dev frontend by default, can override with ALLOWED_ORIGINS="http://a:5173,http://b:5173"
_default_allowed = ["http://localhost:5173", "http://127.0.0.1:5173"]
_env_allowed = os.getenv("ALLOWED_ORIGINS", "").strip()
_allowed = [o.strip() for o in _env_allowed.split(",") if o.strip()] or _default_allowed
app.add_middleware(
	CORSMiddleware,
	allow_origins=_allowed,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# Lazy-init heavy components
_config: AppConfig | None = None
_embedder: Embedder | None = None


def get_services() -> tuple[AppConfig, Embedder]:
	global _config, _embedder
	if _config is None:
		_config = AppConfig()
	if _embedder is None:
		_embedder = Embedder(_config)
	return _config, _embedder


@app.get("/health")
def health() -> dict:
	return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
	data = generate_latest()
	return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
	REQUESTS_TOTAL.labels(endpoint="chat").inc()
	config, embedder = get_services()
	# session handling
	session_id = req.session_id or uuid.uuid4().hex
	ensure_session(config, session_id)
	history = get_recent_messages(config, session_id, limit=10)
	# persist user question
	add_message(config, session_id, 'user', req.query)
	results = search_top_k(config, embedder, req.query, k=req.k)
	context = "\n\n".join([r[0] for r in results])
	history_text = "\n".join([f"{role}: {content}" for role, content in history])
	prompt = (
		"You are a helpful assistant. Use the following context to answer the user's question.\n\n"
		+ "Context:\n"
		+ context
		+ "\n\nConversation so far (most recent last):\n"
		+ history_text
		+ "\n\nQuestion: "
		+ req.query
		+ "\nAnswer in Bahasa Indonesia if the question is Indonesian."
	)
	answer = call_ollama(config.llm.base_url, config.llm.model_name, prompt)
	# persist assistant answer
	add_message(config, session_id, 'assistant', answer)
	sources = [
		{"text": r[0], "distance": r[1], "source": r[2], "chunk_index": r[3]} for r in results
	]
	logger.bind(session_id=session_id).info("answered query")
	CHATS_TOTAL.inc()
	return ChatResponse(answer=answer, sources=sources)


if __name__ == "__main__":
	uvicorn.run("scripts.api:app", host="0.0.0.0", port=8000, reload=True)


