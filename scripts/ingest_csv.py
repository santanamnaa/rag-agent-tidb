#!/usr/bin/env python3
import argparse
from rag_agent.config import AppConfig
from rag_agent.ingest import ingest_csv

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("csv_path")
	parser.add_argument("--text_col", default="text")
	parser.add_argument("--id_col", default="id")
	parser.add_argument("--source_col", default=None)
	args = parser.parse_args()

	config = AppConfig()
	ingest_csv(config, args.csv_path, text_col=args.text_col, id_col=args.id_col, source_col=args.source_col)
	print("CSV ingested.")
