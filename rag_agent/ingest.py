import json
from typing import List
import pandas as pd
from .config import AppConfig
from .db import create_connection, execute
from .embedding import Embedder


def chunk_text(text: str, max_tokens: int = 400) -> List[str]:
	# naive splitter by sentences/periods; replace with tokenizer if needed
	parts: List[str] = []
	buf: List[str] = []
	for sentence in text.split('.'):
		s = (sentence.strip() + '.').strip()
		if not s:
			continue
		buf.append(s)
		if sum(len(x.split()) for x in buf) >= max_tokens:
			parts.append(' '.join(buf))
			buf = []
	if buf:
		parts.append(' '.join(buf))
	return parts


def ingest_csv(config: AppConfig, csv_path: str, text_col: str = 'text', id_col: str = 'id', source_col: str = None) -> None:
	conn = create_connection(config)
	embedder = Embedder(config)
	try:
		df = pd.read_csv(csv_path)
		for _, row in df.iterrows():
			source = str(row[source_col]) if source_col and source_col in df.columns else str(row.get(id_col, 'csv'))
			chunks = chunk_text(str(row[text_col]))
			embs = embedder.embed_texts(chunks)
			for idx, (chunk, emb) in enumerate(zip(chunks, embs)):
				execute(
					conn,
					"INSERT INTO documents (source, chunk_index, text, text_vec) VALUES (%s, %s, %s, CAST(%s AS VECTOR(1024)))",
					(source, idx, chunk, json.dumps(emb)),
				)
	finally:
		conn.close()
