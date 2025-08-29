import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def env(name: str, default: str = "") -> str:
	value = os.getenv(name, default)
	if value is None:
		return default
	return value


@dataclass(frozen=True)
class TiDBConfig:
	host: str = env("TIDB_HOST")
	port: int = int(env("TIDB_PORT", "4000"))
	user: str = env("TIDB_USER")
	password: str = env("TIDB_PASSWORD")
	database: str = env("TIDB_DATABASE", "rag_db")
	ssl_mode: str = env("TIDB_SSL_MODE", "VERIFY_IDENTITY")


@dataclass(frozen=True)
class EmbeddingConfig:
	model_name: str = env("EMBEDDING_MODEL", "BAAI/bge-m3")
	dimension: int = int(env("EMBEDDING_DIM", "1024"))


@dataclass(frozen=True)
class LLMConfig:
	model_name: str = env("OLLAMA_MODEL", "deepseek-r1:latest")
	base_url: str = env("OLLAMA_HOST", "http://localhost:11434")


@dataclass(frozen=True)
class AppConfig:
	tidb: TiDBConfig = TiDBConfig()
	embedding: EmbeddingConfig = EmbeddingConfig()
	llm: LLMConfig = LLMConfig()
