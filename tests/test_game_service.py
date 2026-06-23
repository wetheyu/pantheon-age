import sys
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from phase1_cli.character import build_character
from phase1_cli.game_service import handle_player_input
from phase1_cli.game_state import GameState


class GameServiceTests(unittest.TestCase):
    def make_state(self):
        return GameState(build_character("阿洛", "warrior", "死亡之神"))

    def test_view_command_does_not_consume_turn(self):
        state = self.make_state()

        response = handle_player_input(state, "地图")

        self.assertEqual(response.kind, "map")
        self.assertFalse(response.consumes_turn)
        self.assertEqual(state.turn, 0)
        self.assertIn("当前位置", response.text)

    def test_action_command_consumes_turn_and_updates_state(self):
        state = self.make_state()

        response = handle_player_input(state, "进入前厅")

        self.assertEqual(response.kind, "action")
        self.assertTrue(response.consumes_turn)
        self.assertEqual(state.turn, 1)
        self.assertEqual(state.current_location, "前厅")
        self.assertIn("你从修道院门口来到前厅", response.text)
        self.assertIn("前厅", state.visited_locations)

    def test_service_response_exports_api_ready_dict(self):
        state = self.make_state()

        response = handle_player_input(state, "状态")
        payload = response.to_dict()

        self.assertEqual(payload["kind"], "status")
        self.assertIn("state", payload)
        self.assertEqual(payload["state"]["current_location"], "修道院门口")
        self.assertEqual(payload["state"]["available_exits"], ["前厅"])
        self.assertEqual(payload["state"]["player"]["name"], "阿洛")

    def test_save_load_and_quit_are_session_signals(self):
        state = self.make_state()

        save_response = handle_player_input(state, "存档")
        load_response = handle_player_input(state, "读档")
        quit_response = handle_player_input(state, "退出")

        self.assertTrue(save_response.should_save)
        self.assertTrue(load_response.should_load)
        self.assertTrue(quit_response.should_exit)
        self.assertEqual(state.turn, 0)

    def test_empty_input_does_not_consume_turn(self):
        state = self.make_state()

        response = handle_player_input(state, "   ")

        self.assertEqual(response.kind, "empty")
        self.assertFalse(response.consumes_turn)
        self.assertEqual(state.turn, 0)


if __name__ == "__main__":
    unittest.main()
