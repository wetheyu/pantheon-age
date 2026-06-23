import sys
from pathlib import Path
import warnings
import unittest

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*")

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from phase2_api.main import app
from phase2_api.services.session_store import clear_sessions


class Phase2ApiTests(unittest.TestCase):
    def setUp(self):
        clear_sessions()
        self.client = TestClient(app)

    def test_health_endpoint(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["project"], "Pantheon Age")

    def test_classes_endpoint(self):
        response = self.client.get("/classes")

        self.assertEqual(response.status_code, 200)
        class_ids = {item["class_id"] for item in response.json()["classes"]}
        self.assertIn("warrior", class_ids)
        self.assertIn("mage", class_ids)

    def test_locations_endpoint(self):
        response = self.client.get("/locations")

        self.assertEqual(response.status_code, 200)
        locations = {item["name"]: item for item in response.json()["locations"]}
        self.assertIn("修道院门口", locations)
        self.assertEqual(locations["修道院门口"]["exits"], ["前厅"])

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
        self.assertIn("浓雾像潮水一样漫过铁门", payload["opening_text"])

        action_response = self.client.post(
            f"/games/{game_id}/actions",
            json={"text": "进入前厅"},
        )

        self.assertEqual(action_response.status_code, 200)
        action_payload = action_response.json()["response"]
        self.assertEqual(action_payload["kind"], "action")
        self.assertTrue(action_payload["consumes_turn"])
        self.assertEqual(action_payload["state"]["current_location"], "前厅")
        self.assertEqual(action_payload["state"]["turn"], 1)

    def test_get_game_not_found(self):
        response = self.client.get("/games/missing")

        self.assertEqual(response.status_code, 404)
        self.assertIn("Game not found", response.json()["detail"])

    def test_invalid_character_config(self):
        response = self.client.post(
            "/games",
            json={"name": "阿洛", "class_id": "unknown", "god": "死亡之神"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Unknown class_id", response.json()["detail"])


if __name__ == "__main__":
    unittest.main()
