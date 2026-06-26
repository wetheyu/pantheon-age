import os
import unittest

from llm_runtime.providers import load_local_env

from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase1_cli.scenarios import configure_character_for_game_mode
from agentic_runtime.orchestrator import run_agentic_turn


load_local_env()


@unittest.skipUnless(
    os.getenv("PANTHEON_RUN_LIVE_LLM_TESTS") == "1"
    and os.getenv("PANTHEON_USE_AGENTIC_LLM") == "1"
    and os.getenv("OPENAI_API_KEY"),
    "Set PANTHEON_RUN_LIVE_LLM_TESTS=1, PANTHEON_USE_AGENTIC_LLM=1, and OPENAI_API_KEY to run live Agentic Runtime tests.",
)
class LiveAgenticRuntimeTests(unittest.TestCase):
    def test_live_agentic_runtime_returns_player_facing_narration(self):
        character = build_character("测试员", "rogue", "隐秘之神")
        configure_character_for_game_mode(character, "world", "albion", "格兰威克")
        state = GameState(character)

        result = run_agentic_turn(state, "我观察街角的人群，寻找一个可能知道异常传闻的人")

        self.assertTrue(result.providers.get("llm_enabled"))
        self.assertIn(result.runtime_trace.branch, {"creative_gm", "turn_director"})
        self.assertGreater(result.runtime_trace.total_ms, 0)
        self.assertTrue(result.narration.text.strip())
        self.assertNotIn("validator", result.narration.text.lower())
        self.assertNotIn("rule_result", result.narration.text.lower())
        self.assertIn("commit", result.validations)
        self.assertTrue(result.validations["commit"].is_valid)


if __name__ == "__main__":
    unittest.main()
