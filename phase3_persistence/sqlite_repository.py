"""SQLite-backed repositories for Phase 3 persistence."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from agentic_runtime.contracts import MEMORY_BUCKETS, MemoryRecord
from phase1_cli.game_state import GameState

from .config import get_database_path
from .errors import PersistenceError


SNAPSHOT_VERSION = 1


class GameSessionRepository:
    """Persist API game sessions as JSON snapshots in SQLite."""

    def __init__(self, db_path=None):
        self.db_path = Path(get_database_path() if db_path is None else db_path)

    def _connect(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            connection.row_factory = sqlite3.Row
            self._ensure_schema(connection)
            return connection
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot open SQLite database: {error}") from error
        except Exception:
            if connection is not None:
                connection.close()
            raise

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _ensure_schema(self, connection):
        try:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS game_sessions (
                    game_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS game_events (
                    game_id TEXT NOT NULL,
                    event_index INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (game_id, event_index),
                    FOREIGN KEY (game_id) REFERENCES game_sessions(game_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS game_memories (
                    game_id TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    bucket TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    content TEXT NOT NULL,
                    authority_level TEXT NOT NULL,
                    visibility TEXT NOT NULL,
                    source_event TEXT NOT NULL DEFAULT '',
                    confidence REAL NOT NULL DEFAULT 1.0,
                    source TEXT NOT NULL DEFAULT 'memory-store',
                    created_at TEXT NOT NULL,
                    PRIMARY KEY (game_id, record_id),
                    FOREIGN KEY (game_id) REFERENCES game_sessions(game_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_game_memories_game_bucket
                ON game_memories (game_id, bucket)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_game_memories_game_visibility
                ON game_memories (game_id, visibility)
                """
            )
            connection.commit()
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot ensure SQLite schema: {error}") from error

    def save(self, game_id, state):
        now = _utc_now()
        payload = _serialize_state(state)
        try:
            with self._connection() as connection:
                connection.execute(
                    """
                    INSERT INTO game_sessions (game_id, state_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(game_id) DO UPDATE SET
                        state_json = excluded.state_json,
                        updated_at = excluded.updated_at
                    """,
                    (game_id, payload, now, now),
                )
                self._replace_events(connection, game_id, state.event_log, now)
                self._replace_memory_records(connection, game_id, state.agentic_memory, now)
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot save game session: {error}") from error

    def get(self, game_id):
        try:
            with self._connection() as connection:
                row = connection.execute(
                    "SELECT state_json FROM game_sessions WHERE game_id = ?",
                    (game_id,),
                ).fetchone()
                memory_rows = self._fetch_memory_rows(connection, game_id) if row else []
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot read game session: {error}") from error

        if row is None:
            return None

        state = _deserialize_state(row["state_json"])
        _hydrate_state_memory_from_rows(state, memory_rows)
        return state

    def list(self):
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    "SELECT game_id, state_json FROM game_sessions ORDER BY created_at, game_id"
                ).fetchall()
                memory_rows_by_game = {
                    row["game_id"]: self._fetch_memory_rows(connection, row["game_id"])
                    for row in rows
                }
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot list game sessions: {error}") from error

        sessions = []
        for row in rows:
            state = _deserialize_state(row["state_json"])
            _hydrate_state_memory_from_rows(state, memory_rows_by_game.get(row["game_id"], []))
            sessions.append((row["game_id"], state))
        return sessions

    def delete(self, game_id):
        try:
            with self._connection() as connection:
                connection.execute(
                    "DELETE FROM game_memories WHERE game_id = ?",
                    (game_id,),
                )
                connection.execute(
                    "DELETE FROM game_events WHERE game_id = ?",
                    (game_id,),
                )
                cursor = connection.execute(
                    "DELETE FROM game_sessions WHERE game_id = ?",
                    (game_id,),
                )
                return cursor.rowcount > 0
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot delete game session: {error}") from error

    def clear(self):
        try:
            with self._connection() as connection:
                connection.execute("DELETE FROM game_memories")
                connection.execute("DELETE FROM game_events")
                connection.execute("DELETE FROM game_sessions")
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot clear game sessions: {error}") from error

    def list_events(self, game_id):
        try:
            with self._connection() as connection:
                session_exists = connection.execute(
                    "SELECT 1 FROM game_sessions WHERE game_id = ?",
                    (game_id,),
                ).fetchone()
                if session_exists is None:
                    return None

                rows = connection.execute(
                    """
                    SELECT event_index, text
                    FROM game_events
                    WHERE game_id = ?
                    ORDER BY event_index
                    """,
                    (game_id,),
                ).fetchall()
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot list game events: {error}") from error

        return [
            {"event_index": row["event_index"], "text": row["text"]}
            for row in rows
        ]

    def list_memory_records(self, game_id, bucket=None, include_hidden=False):
        try:
            with self._connection() as connection:
                session_exists = connection.execute(
                    "SELECT 1 FROM game_sessions WHERE game_id = ?",
                    (game_id,),
                ).fetchone()
                if session_exists is None:
                    return None

                query = """
                    SELECT *
                    FROM game_memories
                    WHERE game_id = ?
                """
                parameters = [game_id]

                if bucket is not None:
                    query += " AND bucket = ?"
                    parameters.append(bucket)

                if not include_hidden:
                    query += " AND bucket != 'secret' AND visibility != 'system_secret'"

                query += " ORDER BY created_at, record_id"
                rows = connection.execute(query, parameters).fetchall()
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot list game memories: {error}") from error

        return tuple(_memory_record_from_row(row) for row in rows)

    def _replace_events(self, connection, game_id, event_log, created_at):
        connection.execute(
            "DELETE FROM game_events WHERE game_id = ?",
            (game_id,),
        )
        connection.executemany(
            """
            INSERT INTO game_events (game_id, event_index, text, created_at)
            VALUES (?, ?, ?, ?)
            """,
            [
                (game_id, event_index, text, created_at)
                for event_index, text in enumerate(event_log)
            ],
        )

    def _replace_memory_records(self, connection, game_id, agentic_memory, created_at):
        connection.execute(
            "DELETE FROM game_memories WHERE game_id = ?",
            (game_id,),
        )
        records = _memory_records_from_store(agentic_memory)
        connection.executemany(
            """
            INSERT INTO game_memories (
                game_id,
                record_id,
                bucket,
                memory_type,
                subject,
                content,
                authority_level,
                visibility,
                source_event,
                confidence,
                source,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    game_id,
                    record.record_id,
                    record.bucket,
                    record.memory_type,
                    record.subject,
                    record.content,
                    record.authority_level,
                    record.visibility,
                    record.source_event,
                    record.confidence,
                    record.source,
                    created_at,
                )
                for record in records
            ],
        )

    def _fetch_memory_rows(self, connection, game_id):
        return connection.execute(
            """
            SELECT *
            FROM game_memories
            WHERE game_id = ?
            ORDER BY created_at, record_id
            """,
            (game_id,),
        ).fetchall()


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _serialize_state(state):
    payload = {
        "snapshot_version": SNAPSHOT_VERSION,
        "state": state.to_dict(),
    }
    return json.dumps(payload, ensure_ascii=False)


def _deserialize_state(raw_state_json):
    try:
        payload = json.loads(raw_state_json)
    except json.JSONDecodeError as error:
        raise PersistenceError(f"Cannot decode game state JSON: {error}") from error

    if "snapshot_version" not in payload:
        state_data = payload
    else:
        snapshot_version = payload.get("snapshot_version")
        if snapshot_version != SNAPSHOT_VERSION:
            raise PersistenceError(
                f"Unsupported game state snapshot version: {snapshot_version}"
            )
        state_data = payload.get("state")

    if not isinstance(state_data, dict):
        raise PersistenceError("Persisted game state snapshot is not an object.")

    try:
        return GameState.from_dict(state_data)
    except (KeyError, TypeError, ValueError) as error:
        raise PersistenceError(f"Cannot rebuild game state: {error}") from error


def _memory_records_from_store(agentic_memory):
    if not isinstance(agentic_memory, dict):
        return ()

    records = []
    for bucket in MEMORY_BUCKETS:
        bucket_records = agentic_memory.get(bucket, [])
        if not isinstance(bucket_records, list):
            continue
        for raw_record in bucket_records:
            try:
                record = MemoryRecord.from_dict(raw_record)
            except (KeyError, TypeError, ValueError):
                continue
            records.append(record)
    return tuple(records)


def _memory_record_from_row(row):
    return MemoryRecord(
        record_id=row["record_id"],
        bucket=row["bucket"],
        memory_type=row["memory_type"],
        subject=row["subject"],
        content=row["content"],
        authority_level=row["authority_level"],
        visibility=row["visibility"],
        source_event=row["source_event"],
        confidence=row["confidence"],
        source=row["source"],
    )


def _hydrate_state_memory_from_rows(state, rows):
    if not rows:
        return

    state.agentic_memory = {bucket: [] for bucket in MEMORY_BUCKETS}
    for row in rows:
        record = _memory_record_from_row(row)
        if record.bucket not in state.agentic_memory:
            state.agentic_memory[record.bucket] = []
        state.agentic_memory[record.bucket].append(record.to_dict())
