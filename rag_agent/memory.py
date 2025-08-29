from typing import List, Tuple
from .db import create_connection, execute, fetchall
from .config import AppConfig


def ensure_session(config: AppConfig, session_id: str) -> None:
	conn = create_connection(config)
	try:
		execute(
			conn,
			"""
			INSERT IGNORE INTO chat_sessions (session_id)
			VALUES (%s)
			""",
			(session_id,),
		)
	finally:
		conn.close()


def add_message(config: AppConfig, session_id: str, role: str, content: str) -> None:
	conn = create_connection(config)
	try:
		execute(
			conn,
			"""
			INSERT INTO chat_messages (session_id, role, content)
			VALUES (%s, %s, %s)
			""",
			(session_id, role, content),
		)
	finally:
		conn.close()


def get_recent_messages(config: AppConfig, session_id: str, limit: int = 10) -> List[Tuple[str, str]]:
	conn = create_connection(config)
	try:
		rows = fetchall(
			conn,
			"""
			SELECT role, content
			FROM chat_messages
			WHERE session_id = %s
			ORDER BY created_at DESC
			LIMIT %s
			""",
			(session_id, limit),
		)
		rows.reverse()
		return rows
	finally:
		conn.close()


