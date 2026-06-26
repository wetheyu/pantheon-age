import sys
from pathlib import Path
import tempfile
import warnings
import unittest

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*")

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from phase2_api.main import app
from phase2_api.services.session_store import clear_sessions, configure_storage


class Phase2ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.sqlite3"
        configure_storage(self.db_path)
        clear_sessions()
        self.client = TestClient(app)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["project"], "Pantheon Age")

    def test_cors_allows_local_web_ui(self):
        response = self.client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5173")

    def test_classes_endpoint(self):
        response = self.client.get("/classes")

        self.assertEqual(response.status_code, 200)
        class_ids = {item["class_id"] for item in response.json()["classes"]}
        self.assertIn("warrior", class_ids)
        self.assertIn("mage", class_ids)

    def test_gods_endpoint(self):
        response = self.client.get("/gods")

        self.assertEqual(response.status_code, 200)
        gods = response.json()["gods"]
        self.assertIn("死亡之神", gods)
        self.assertIn("隐秘之神", gods)

    def test_locations_endpoint(self):
        response = self.client.get("/locations")

        self.assertEqual(response.status_code, 200)
        locations = {item["name"]: item for item in response.json()["locations"]}
        self.assertIn("修道院门口", locations)
        self.assertEqual(locations["修道院门口"]["exits"], ["前厅"])

    def test_origins_endpoint(self):
        response = self.client.get("/origins")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        country_ids = {item["country_id"] for item in payload["countries"]}
        background_ids = {item["background_id"] for item in payload["backgrounds"]}
        self.assertIn("albion", country_ids)
        self.assertIn("lumiere", country_ids)
        self.assertIn("investigative_reporter", background_ids)
        self.assertIn("dock_scribe", background_ids)

    def test_create_character(self):
        response = self.client.post(
            "/characters",
            json={"name": "阿洛", "class_id": "warrior", "god": "死亡之神"},
        )

        self.assertEqual(response.status_code, 200)
        character = response.json()["character"]
        self.assertEqual(character["name"], "阿洛")
        self.assertEqual(character["class_id"], "warrior")
        self.assertEqual(character["god"], "死亡之神")

    def test_create_game_and_submit_action(self):
        create_response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "warrior", "god": "死亡之神"},
        )

        self.assertEqual(create_response.status_code, 200)
        payload = create_response.json()
        game_id = payload["game_id"]
        self.assertEqual(payload["state"]["current_location"], "修道院门口")
        self.assertEqual(payload["game_mode"], "tutorial")
        self.assertEqual(payload["setup"]["game_mode"], "tutorial")
        self.assertIn("浓雾像潮水一样漫过铁门", payload["opening_text"])

        action_response = self.client.post(
            f"/games/{game_id}/actions",
            json={"text": "进入前厅"},
        )

        self.assertEqual(action_response.status_code, 200)
        api_payload = action_response.json()
        action_payload = api_payload["response"]
        self.assertEqual(action_payload["kind"], "action")
        self.assertTrue(action_payload["consumes_turn"])
        self.assertEqual(action_payload["state"]["current_location"], "前厅")
        self.assertEqual(action_payload["state"]["turn"], 1)
        self.assertEqual(api_payload["story"], action_payload["text"])
        self.assertEqual(api_payload["state"]["current_location"], "前厅")
        self.assertEqual(api_payload["mechanics"]["kind"], "action")
        self.assertIsNone(api_payload["debug"])

        read_response = self.client.get(f"/games/{game_id}")
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.json()["state"]["current_location"], "前厅")
        self.assertEqual(read_response.json()["state"]["turn"], 1)

        events_response = self.client.get(f"/games/{game_id}/events")
        self.assertEqual(events_response.status_code, 200)
        events = events_response.json()["events"]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_index"], 0)
        self.assertIn("你从修道院门口来到前厅", events[0]["text"])

    def test_create_world_game_with_origin_contract(self):
        response = self.client.post(
            "/games",
            json={
                "name": "伊芙",
                "class_id": "mage",
                "god": "真理之神",
                "game_mode": "world",
                "origin_country_id": "lumiere",
                "origin_city": "维拉尔",
                "background_id": "dock_scribe",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        state = payload["state"]
        setup = payload["setup"]
        self.assertEqual(payload["game_mode"], "world")
        self.assertEqual(state["game_mode"], "world")
        self.assertTrue(state["is_world_mode"])
        self.assertEqual(state["current_location"], "维拉尔")
        self.assertEqual(setup["origin"]["country_id"], "lumiere")
        self.assertEqual(setup["origin"]["city"], "维拉尔")
        self.assertEqual(setup["origin"]["background_id"], "dock_scribe")
        self.assertIn("维拉尔", payload["opening_text"])
        self.assertIn("港口书记员", payload["opening_text"])

    def test_action_response_can_include_debug(self):
        create_response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "warrior", "god": "死亡之神"},
        )

        self.assertEqual(create_response.status_code, 200)
        game_id = create_response.json()["game_id"]

        response = self.client.post(
            f"/games/{game_id}/actions",
            json={"text": "进入前厅", "include_debug": True},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIsNotNone(payload["debug"])
        self.assertIn("rule_result", payload["debug"])
        self.assertIn("action", payload["debug"])

    def test_game_events_is_empty_for_new_session(self):
        create_response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "warrior", "god": "死亡之神"},
        )

        self.assertEqual(create_response.status_code, 200)
        game_id = create_response.json()["game_id"]

        events_response = self.client.get(f"/games/{game_id}/events")

        self.assertEqual(events_response.status_code, 200)
        self.assertEqual(events_response.json()["events"], [])

    def test_game_events_not_found(self):
        response = self.client.get("/games/missing/events")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Game not found", response.json()["detail"])

    def test_list_games_is_empty_without_sessions(self):
        response = self.client.get("/games")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["games"], [])

    def test_list_games_shows_session_summary(self):
        create_response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "warrior", "god": "死亡之神"},
        )

        self.assertEqual(create_response.status_code, 200)
        game_id = create_response.json()["game_id"]

        response = self.client.get("/games")

        self.assertEqual(response.status_code, 200)
        games = response.json()["games"]
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0]["game_id"], game_id)
        self.assertEqual(games[0]["player_name"], "阿洛")
        self.assertEqual(games[0]["class_id"], "warrior")
        self.assertEqual(games[0]["current_location"], "修道院门口")
        self.assertEqual(games[0]["turn"], 0)
        self.assertFalse(games[0]["is_game_over"])

    def test_delete_game_removes_session(self):
        create_response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "warrior", "god": "死亡之神"},
        )

        self.assertEqual(create_response.status_code, 200)
        game_id = create_response.json()["game_id"]

        delete_response = self.client.delete(f"/games/{game_id}")

        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(delete_response.json()["game_id"], game_id)
        self.assertTrue(delete_response.json()["deleted"])

        read_response = self.client.get(f"/games/{game_id}")
        self.assertEqual(read_response.status_code, 404)

        list_response = self.client.get("/games")
        self.assertEqual(list_response.json()["games"], [])

    def test_get_game_not_found(self):
        response = self.client.get("/games/missing")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Game not found", response.json()["detail"])

    def test_delete_game_not_found(self):
        response = self.client.delete("/games/missing")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Game not found", response.json()["detail"])

    def test_empty_action_text_is_rejected(self):
        create_response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "warrior", "god": "死亡之神"},
        )

        self.assertEqual(create_response.status_code, 200)
        game_id = create_response.json()["game_id"]

        response = self.client.post(f"/games/{game_id}/actions", json={"text": ""})

        self.assertEqual(response.status_code, 422)

    def test_invalid_character_config(self):
        response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "unknown", "god": "死亡之神"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown class_id", response.json()["detail"])

    def test_invalid_god_config(self):
        response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "warrior", "god": "不存在的神"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown god", response.json()["detail"])

    def test_invalid_world_origin_config(self):
        response = self.client.post(
            "/games",
            json={
                "name": "阿洛",
                "class_id": "warrior",
                "god": "死亡之神",
                "game_mode": "world",
                "origin_country_id": "unknown",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown origin_country_id", response.json()["detail"])

    def test_openapi_schema_is_available(self):
        response = self.client.get("/openapi.json")

        self.assertEqual(response.status_code, 200)
        paths = response.json()["paths"]
        self.assertIn("/health", paths)
        self.assertIn("/gods", paths)
        self.assertIn("/origins", paths)
        self.assertIn("/games", paths)
        self.assertIn("/games/{game_id}/events", paths)


if __name__ == "__main__":
    unittest.main()
