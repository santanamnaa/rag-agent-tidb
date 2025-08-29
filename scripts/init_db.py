#!/usr/bin/env python3
from rag_agent.config import AppConfig
from rag_agent.schema import init_schema

if __name__ == "__main__":
	config = AppConfig()
	init_schema(config)
	print("Schema initialized.")
