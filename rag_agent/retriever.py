import json
from typing import List, Tuple
from .db import create_connection, fetchall
from .config import AppConfig
from .embedding import Embedder


def search_top_k(config: AppConfig, embedder: Embedder, query: str, k: int = 5) -> List[Tuple[str, float, str, int]]:
	query_vec = embedder.embed_text(query)
	conn = create_connection(config)
	try:
		rows = fetchall(
			conn,
			"""
			SELECT text,
			/* distance: smaller is more similar */
			VEC_COSINE_DISTANCE(text_vec, CAST(%s AS VECTOR(1024))) AS distance,
			source,
			chunk_index
			FROM documents
			ORDER BY distance ASC
			LIMIT %s
			""",
			(params := (json.dumps(query_vec), k)),
		)
		# rows: List[Tuple[text, distance, source, chunk_index]]
		return rows
	finally:
		conn.close()
