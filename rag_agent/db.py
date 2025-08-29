import json
from typing import Any, List, Optional, Sequence, Tuple
import mysql.connector
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from .config import AppConfig


def create_connection(config: AppConfig) -> MySQLConnection:
	conn = mysql.connector.connect(
		host=config.tidb.host,
		port=config.tidb.port,
		user=config.tidb.user,
		password=config.tidb.password,
		database=config.tidb.database,
		ssl_ca=None,
	)
	return conn


def create_server_connection(config: AppConfig) -> MySQLConnection:
	"""Connect without selecting a database (for CREATE DATABASE)."""
	conn = mysql.connector.connect(
		host=config.tidb.host,
		port=config.tidb.port,
		user=config.tidb.user,
		password=config.tidb.password,
		ssl_ca=None,
	)
	return conn


def execute(conn: MySQLConnection, sql: str, params: Optional[Sequence[Any]] = None) -> None:
	with conn.cursor() as cur:
		cur.execute(sql, params or [])
	conn.commit()


def fetchall(conn: MySQLConnection, sql: str, params: Optional[Sequence[Any]] = None) -> List[Tuple]:
	with conn.cursor() as cur:
		cur.execute(sql, params or [])
		rows = cur.fetchall()
	return rows


def fetchone(conn: MySQLConnection, sql: str, params: Optional[Sequence[Any]] = None) -> Optional[Tuple]:
	with conn.cursor() as cur:
		cur.execute(sql, params or [])
		row = cur.fetchone()
	return row


def executemany(conn: MySQLConnection, sql: str, seq_of_params: Sequence[Sequence[Any]]) -> None:
	with conn.cursor() as cur:
		cur.executemany(sql, seq_of_params)
	conn.commit()
