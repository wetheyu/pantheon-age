"""SQLite-backed repositories for Phase 3 persistence."""

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

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
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot save game session: {error}") from error

    def get(self, game_id):
        try:
            with self._connection() as connection:
                row = connection.execute(
                    "SELECT state_json FROM game_sessions WHERE game_id = ?",
                    (game_id,),
                ).fetchone()
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot read game session: {error}") from error

        if row is None:
            return None

        return _deserialize_state(row["state_json"])

    def list(self):
        try:
            with self._connection() as connection:
                rows = connection.execute(
                    "SELECT game_id, state_json FROM game_sessions ORDER BY created_at, game_id"
                ).fetchall()
        except sqlite3.Error as error:
            raise PersistenceError(f"Cannot list game sessions: {error}") from error

        sessions = []
        for row in rows:
            sessions.append((row["game_id"], _deserialize_state(row["state_json"])))
        return sessions

    def delete(self, game_id):
        try:
            with self._connection() as connection:
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
