import sys
from pathlib import Path
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from phase1_cli.character import build_character
from phase1_cli.game_service import handle_player_input
from phase1_cli.game_state import GameState
from phase1_cli.scenarios import (
    ORIGIN_CHURCH_RELATIONS,
    configure_character_for_game_mode,
    origin_country_ids,
)


class GameServiceTests(unittest.TestCase):
    def setUp(self):
        self.env_patch = patch.dict(
            "os.environ",
            {
                "PANTHEON_USE_LLM": "0",
                "PANTHEON_USE_AGENTIC_RUNTIME": "0",
            },
            clear=False,
        )
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()

    def make_state(self):
        return GameState(build_character("阿洛", "warrior", "死亡之神"))

    def make_world_state(self):
        character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(character, "world")
        return GameState(character)

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
        self.assertIsNotNone(response.llm_runtime)
        self.assertEqual(response.llm_runtime["action_candidate"]["candidate"]["source"], "keyword")
        self.assertEqual(response.llm_runtime["narration"]["proposal"]["source"], "template")

    def test_service_response_exports_api_ready_dict(self):
        state = self.make_state()

        response = handle_player_input(state, "状态")
        payload = response.to_dict()

        self.assertEqual(payload["kind"], "status")
        self.assertIn("state", payload)
        self.assertEqual(payload["state"]["current_location"], "修道院门口")
        self.assertEqual(payload["state"]["available_exits"], ["前厅"])
        self.assertEqual(payload["state"]["player"]["name"], "阿洛")

    def test_action_response_exports_llm_runtime_dict(self):
        state = self.make_state()

        response = handle_player_input(state, "调查脚印")
        payload = response.to_dict()

        self.assertIn("llm_runtime", payload)
        self.assertIn("action_candidate", payload["llm_runtime"])
        self.assertIn("adjudication", payload["llm_runtime"])
        self.assertIn("narration", payload["llm_runtime"])
        self.assertEqual(payload["llm_runtime"]["providers"]["action_provider"], "keyword")

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

    def test_agentic_runtime_can_be_enabled_for_action_flow(self):
        state = self.make_state()
        with patch.dict("os.environ", {"PANTHEON_USE_AGENTIC_RUNTIME": "1"}, clear=False):
            response = handle_player_input(state, "跳向前厅")

        self.assertEqual(response.kind, "action")
        self.assertEqual(state.current_location, "前厅")
        self.assertEqual(response.llm_runtime["phase"], "phase5-agentic-runtime")
        agentic = response.llm_runtime["agentic_runtime"]
        self.assertIn("跳向前厅", agentic["open_action"]["method"])
        self.assertEqual(agentic["adjudication"]["action_type"], "move")

    def test_world_mode_uses_agentic_runtime_without_env_flag(self):
        state = self.make_world_state()

        response = handle_player_input(state, "调查格兰威克金融街的异常钟声")

        self.assertEqual(response.kind, "action")
        self.assertEqual(response.llm_runtime["phase"], "phase5-agentic-runtime")
        self.assertEqual(state.current_location, "格兰威克")
        agentic = response.llm_runtime["agentic_runtime"]
        self.assertEqual(agentic["adjudication"]["action_type"], "world_action")
        self.assertEqual(agentic["commit"]["committed_effects"], ["world_attempt_recorded"])

    def test_world_mode_service_runs_complete_phase5_slice(self):
        state = self.make_world_state()

        first = handle_player_input(state, "调查格兰威克金融街的异常钟声")
        second = handle_player_input(state, "继续询问金融街钟声")

        first_agentic = first.llm_runtime["agentic_runtime"]
        second_agentic = second.llm_runtime["agentic_runtime"]
        first_payload = first.to_dict()

        self.assertNotIn("【格兰威克】", first.text)
        self.assertIn("城市的声响、人群和本地势力", first.text)
        self.assertIn("被你注意到的人", first.text)
        self.assertIn("你注意到", first.text)
        self.assertIn("下一步追查的起点", first.text)
        self.assertEqual(first_agentic["adjudication"]["action_type"], "world_action")
        self.assertEqual(first_agentic["commit"]["rule_result"]["new_clues"], [])
        self.assertEqual(first_agentic["commit"]["rule_result"]["state_changes"], [])
        self.assertEqual(len(first_agentic["memory_records"]), 2)
        self.assertEqual(len(state.agentic_memory["player_known"]), 2)
        self.assertEqual(len(state.agentic_memory["quest"]), 2)
        self.assertNotIn("hidden_context", first_agentic["memory_retrieval"])
        self.assertNotIn("agentic_memory", first_payload["state"])
        self.assertTrue(
            any("异常钟声" in item for item in second_agentic["memory_retrieval"]["player_known"])
        )

    def test_world_mode_violent_action_shows_roll_calculation(self):
        state = self.make_world_state()

        response = handle_player_input(state, "出手杀了他")

        self.assertEqual(response.kind, "action")
        self.assertIn("检定：d20(", response.text)
        self.assertIn("/ DC 16 ->", response.text)
        self.assertIn("状态变化：", response.text)
        self.assertIsNotNone(response.rule_result["roll"])
        self.assertGreater(state.player.suspicion, 0)

    def test_world_mode_origin_selection_sets_country_and_start_city(self):
        character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(character, "world", "lumiere", "维拉尔", None, "港口书记员")
        state = GameState(character)

        payload = state.to_public_dict()

        self.assertEqual(state.current_location, "维拉尔")
        self.assertEqual(payload["game_mode"], "world")
        self.assertTrue(payload["is_world_mode"])
        self.assertEqual(payload["player"]["origin"]["country"], "卢米埃")
        self.assertEqual(payload["player"]["origin"]["formal_name"], "卢米埃共和国")
        self.assertEqual(payload["player"]["origin"]["identity"], "卢米埃人")
        self.assertEqual(payload["player"]["origin"]["ethnicity"], "卢米埃人")
        self.assertEqual(payload["player"]["origin"]["city"], "维拉尔")
        self.assertEqual(payload["player"]["origin"]["background_name"], "港口书记员")
        self.assertIn("码头账簿", payload["player"]["origin"]["background_description"])
        self.assertEqual(payload["player"]["origin"]["church_context"]["dominant"], ["白塔院"])
        self.assertIn("密仪会", payload["player"]["origin"]["church_context"]["hostile"])

    def test_world_mode_origin_selection_supports_eight_countries(self):
        self.assertEqual(
            origin_country_ids(),
            [
                "albion",
                "lumiere",
                "wald",
                "ost",
                "isteria",
                "noctia",
                "selemia",
                "rosvia",
            ],
        )

    def test_world_mode_single_city_origin_can_start_in_selemia(self):
        character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(character, "world", "selemia", "萨莱姆")
        state = GameState(character)

        payload = state.to_public_dict()

        self.assertEqual(state.current_location, "萨莱姆")
        self.assertEqual(payload["player"]["origin"]["country"], "塞勒米亚")
        self.assertEqual(payload["player"]["origin"]["formal_name"], "塞勒米亚苏丹国")
        self.assertEqual(payload["player"]["origin"]["identity"], "塞勒米亚人")
        self.assertEqual(payload["player"]["origin"]["ethnicity"], "塞勒米亚人")
        self.assertEqual(payload["player"]["origin"]["church_context"]["dominant"], ["密仪会"])
        self.assertIn("白塔院", payload["player"]["origin"]["church_context"]["friendly"])
        self.assertIn("铁血教团", payload["player"]["origin"]["church_context"]["friendly"])
        self.assertIn("审判庭", payload["player"]["origin"]["church_context"]["friendly"])
        self.assertIn("夜幕修会", payload["player"]["origin"]["church_context"]["friendly"])
        self.assertNotIn("密仪会", payload["player"]["origin"]["church_context"]["hostile"])

    def test_origin_religion_context_balances_public_and_restricted_churches(self):
        albion_character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(albion_character, "world", "albion", "格兰威克")
        albion_context = GameState(albion_character).to_public_dict()["player"]["origin"]["church_context"]

        self.assertIn("审判庭", albion_context["friendly"])
        self.assertIn("白塔院", albion_context["restricted"])
        self.assertIn("夜幕修会", albion_context["friendly"])

        rosvia_character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(rosvia_character, "world", "rosvia", "维亚洛夫")
        rosvia_context = GameState(rosvia_character).to_public_dict()["player"]["origin"]["church_context"]

        self.assertIn("审判庭", rosvia_context["restricted"])
        self.assertIn("夜幕修会", rosvia_context["friendly"])

    def test_public_church_legality_distribution_stays_balanced(self):
        orthodox_churches = [
            "潮汐圣会",
            "白塔院",
            "铁血教团",
            "审判庭",
            "蔷薇圣庭",
            "安魂教团",
            "夜幕修会",
        ]
        public_counts = {church: 0 for church in orthodox_churches}
        for context in ORIGIN_CHURCH_RELATIONS.values():
            for church in set(context["dominant"] + context["friendly"]):
                if church in public_counts:
                    public_counts[church] += 1

        for church, count in public_counts.items():
            self.assertGreaterEqual(count, 4, church)
            self.assertLessEqual(count, 6, church)

    def test_ost_origin_can_choose_ethnicity(self):
        character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(character, "world", "ost", "卡洛维茨", "波西恩人")
        state = GameState(character)

        payload = state.to_public_dict()

        self.assertEqual(state.current_location, "卡洛维茨")
        self.assertEqual(payload["player"]["origin"]["country"], "奥斯特")
        self.assertEqual(payload["player"]["origin"]["identity"], "奥斯特人")
        self.assertEqual(payload["player"]["origin"]["ethnicity"], "波西恩人")
        self.assertEqual(payload["player"]["origin"]["church_context"]["dominant"], ["审判庭"])
        self.assertIn("密仪会", payload["player"]["origin"]["church_context"]["hostile"])


if __name__ == "__main__":
    unittest.main()
