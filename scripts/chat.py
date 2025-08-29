#!/usr/bin/env python3
import argparse
import json
import requests
from rag_agent.config import AppConfig
from rag_agent.embedding import Embedder
from rag_agent.retriever import search_top_k


def call_ollama(base_url: str, model: str, prompt: str) -> str:
    resp = requests.post(
        f"{base_url}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=600,
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("response") or data.get("message", {}).get("content", "")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("query")
	parser.add_argument("--k", type=int, default=5)
	args = parser.parse_args()

	config = AppConfig()
	embedder = Embedder(config)
	results = search_top_k(config, embedder, args.query, k=args.k)
	context = "\n\n".join([r[0] for r in results])
	prompt = (
		"You are a helpful assistant. Use the following context to answer the user's question.\n\n" +
		"Context:\n" + context + "\n\nQuestion: " + args.query + "\nAnswer in Bahasa Indonesia if the question is Indonesian."
	)
	answer = call_ollama(config.llm.base_url, config.llm.model_name, prompt)
	print(answer)
