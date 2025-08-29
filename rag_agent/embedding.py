from typing import List
from sentence_transformers import SentenceTransformer
from .config import AppConfig


class Embedder:
	def __init__(self, config: AppConfig) -> None:
		self.config = config
		self.model = SentenceTransformer(self.config.embedding.model_name)

	def embed_texts(self, texts: List[str]) -> List[List[float]]:
		embeddings = self.model.encode(texts, normalize_embeddings=True)
		return [e.tolist() for e in embeddings]

	def embed_text(self, text: str) -> List[float]:
		return self.embed_texts([text])[0]
