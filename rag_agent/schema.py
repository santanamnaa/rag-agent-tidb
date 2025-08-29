from typing import Optional
from .db import create_connection, create_server_connection, execute
from .config import AppConfig

DDL = r"""
CREATE TABLE IF NOT EXISTS documents (
id BIGINT PRIMARY KEY AUTO_INCREMENT,
source VARCHAR(255) NOT NULL,
chunk_index INT NOT NULL,
text TEXT NOT NULL,
text_vec VECTOR(1024) NOT NULL
);
-- Optional vector index (if supported by your TiDB version)
-- CREATE VECTOR INDEX vec_idx_text_vec ON documents (text_vec) USING HNSW WITH (M=16, EF_CONSTRUCTION=200) DISTANCE COSINE;

CREATE TABLE IF NOT EXISTS chat_sessions (
id BIGINT PRIMARY KEY AUTO_INCREMENT,
session_id VARCHAR(64) NOT NULL UNIQUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_messages (
id BIGINT PRIMARY KEY AUTO_INCREMENT,
session_id VARCHAR(64) NOT NULL,
role ENUM('user','assistant') NOT NULL,
content TEXT NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
INDEX idx_session_created (session_id, created_at),
FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
);
"""


def init_schema(config: AppConfig) -> None:
	# Create database first using a server-level connection
	server_conn = create_server_connection(config)
	try:
		execute(server_conn, f"CREATE DATABASE IF NOT EXISTS {config.tidb.database};")
	finally:
		server_conn.close()

	# Then create tables within the database
	conn = create_connection(config)
	try:
		sql = DDL.format(db=config.tidb.database)
		# Execute multi-statement DDL sequentially to avoid MySQL "commands out of sync"
		for stmt in sql.split(";"):
			stmt = stmt.strip()
			if not stmt:
				continue
			execute(conn, stmt + ";")
	finally:
		conn.close()
