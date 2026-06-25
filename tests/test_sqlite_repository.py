import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentic_runtime.contracts import MemoryCandidate
from agentic_runtime.memory_store import commit_memory_candidates
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

    def test_save_persists_agentic_memory_records_to_queryable_table(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="quest_memory",
                    subject="海关仓库",
                    content="玩家发现海关仓库登记簿存在异常盐渍。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_1",
                ),
            ),
        )

        self.repository.save("game-1", state)
        records = self.repository.list_memory_records("game-1")

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].bucket, "quest")
        self.assertEqual(records[0].subject, "海关仓库")
        self.assertIn("异常盐渍", records[0].content)

    def test_memory_records_default_query_hides_system_secret_memory(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="secret_memory",
                    subject="幕后黑手",
                    content="某位贵族正在暗中供奉欲望母神。",
                    authority_level="secret",
                    visibility="system_secret",
                    should_persist=True,
                    source_event="turn_2",
                ),
            ),
        )

        self.repository.save("game-1", state)

        self.assertEqual(self.repository.list_memory_records("game-1"), ())
        hidden_records = self.repository.list_memory_records("game-1", include_hidden=True)
        self.assertEqual(len(hidden_records), 1)
        self.assertEqual(hidden_records[0].bucket, "secret")
        self.assertIn("欲望母神", hidden_records[0].content)

    def test_get_hydrates_state_memory_from_memory_table(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="location_memory",
                    subject="维拉尔码头",
                    content="码头工人提到夜里有无灯船靠岸。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_3",
                ),
            ),
        )

        self.repository.save("game-1", state)
        loaded = self.repository.get("game-1")

        self.assertIn("location", loaded.agentic_memory)
        self.assertEqual(len(loaded.agentic_memory["location"]), 1)
        self.assertIn("无灯船", loaded.agentic_memory["location"][0]["content"])

    def test_list_memory_records_can_filter_by_bucket(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="player_memory",
                    subject="玩家身份",
                    content="玩家以报社记者身份行动。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_1",
                ),
                MemoryCandidate(
                    memory_type="location_memory",
                    subject="卢塞恩报社",
                    content="报社夜班编辑注意到异常来稿。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_1",
                ),
            ),
        )

        self.repository.save("game-1", state)
        location_records = self.repository.list_memory_records("game-1", bucket="location")

        self.assertEqual(len(location_records), 1)
        self.assertEqual(location_records[0].subject, "卢塞恩报社")

    def test_list_memory_records_returns_none_for_missing_game(self):
        self.assertIsNone(self.repository.list_memory_records("missing"))

    def test_delete_game_session(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        state.add_event("测试事件")
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="quest_memory",
                    subject="测试记忆",
                    content="这条记忆应随会话删除。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_1",
                ),
            ),
        )
        self.repository.save("game-1", state)

        self.assertTrue(self.repository.delete("game-1"))
        self.assertIsNone(self.repository.get("game-1"))
        self.assertIsNone(self.repository.list_events("game-1"))
        self.assertIsNone(self.repository.list_memory_records("game-1"))
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
