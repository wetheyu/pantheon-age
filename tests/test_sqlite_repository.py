import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase3_persistence.config import DB_PATH_ENV_VAR
from phase3_persistence.errors import PersistenceError
from phase3_persistence.sqlite_repository import GameSessionRepository, SNAPSHOT_VERSION


class SQLiteRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        self.repository = GameSessionRepository(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_get_game_session(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.move_to("前厅")
        state.record_turn()

        self.repository.save("game-1", state)
        loaded = self.repository.get("game-1")

        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.player.name, "阿洛")
        self.assertEqual(loaded.current_location, "前厅")
        self.assertEqual(loaded.turn, 1)

    def test_repository_can_use_env_database_path(self):
        env_db_path = Path(self.temp_dir.name) / "env.sqlite3"

        with patch.dict(os.environ, {DB_PATH_ENV_VAR: str(env_db_path)}):
            repository = GameSessionRepository()
            state = GameState(build_character("阿洛", "warrior", "死亡之神"))
            repository.save("game-1", state)

        self.assertTrue(env_db_path.exists())

    def test_saved_snapshot_has_version_envelope(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))

        self.repository.save("game-1", state)

        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT state_json FROM game_sessions WHERE game_id = ?",
                ("game-1",),
            ).fetchone()

        payload = json.loads(row[0])
        self.assertEqual(payload["snapshot_version"], SNAPSHOT_VERSION)
        self.assertEqual(payload["state"]["player"]["name"], "阿洛")

    def test_list_game_sessions(self):
        first = GameState(build_character("阿洛", "warrior", "死亡之神"))
        second = GameState(build_character("莉娅", "mage", "真理之神"))

        self.repository.save("game-1", first)
        self.repository.save("game-2", second)

        sessions = self.repository.list()

        self.assertEqual([game_id for game_id, _state in sessions], ["game-1", "game-2"])
        self.assertEqual(sessions[0][1].player.name, "阿洛")
        self.assertEqual(sessions[1][1].player.name, "莉娅")

    def test_list_events_returns_persisted_event_log(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.add_event("第一条事件")
        state.add_event("第二条事件")

        self.repository.save("game-1", state)

        self.assertEqual(
            self.repository.list_events("game-1"),
            [
                {"event_index": 0, "text": "第一条事件"},
                {"event_index": 1, "text": "第二条事件"},
            ],
        )

    def test_save_replaces_event_log_snapshot(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.add_event("旧事件")
        self.repository.save("game-1", state)

        state.event_log = ["新事件"]
        self.repository.save("game-1", state)

        self.assertEqual(
            self.repository.list_events("game-1"),
            [{"event_index": 0, "text": "新事件"}],
        )

    def test_list_events_returns_none_for_missing_game(self):
        self.assertIsNone(self.repository.list_events("missing"))

    def test_delete_game_session(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.add_event("测试事件")
        self.repository.save("game-1", state)

        self.assertTrue(self.repository.delete("game-1"))
        self.assertIsNone(self.repository.get("game-1"))
        self.assertIsNone(self.repository.list_events("game-1"))
        self.assertFalse(self.repository.delete("game-1"))

    def test_corrupted_state_json_raises_persistence_error(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        self.repository.save("game-1", state)

        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                "UPDATE game_sessions SET state_json = ? WHERE game_id = ?",
                ("{bad json", "game-1"),
            )

        with self.assertRaises(PersistenceError):
            self.repository.get("game-1")


if __name__ == "__main__":
    unittest.main()
