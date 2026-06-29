import os
import unittest

from llm_runtime.actions import resolve_action_candidate
from llm_runtime.providers import OpenAIActionCandidateProvider, load_local_env


load_local_env()


@unittest.skipUnless(
    os.getenv("PANTHEON_RUN_LIVE_LLM_TESTS") == "1" and os.getenv("OPENAI_API_KEY"),
    "Set PANTHEON_RUN_LIVE_LLM_TESTS=1 and OPENAI_API_KEY to run live LLM tests.",
)
class LiveOpenAIProviderTests(unittest.TestCase):
    def test_openai_understands_jump_toward_location_as_move(self):
        provider = OpenAIActionCandidateProvider(
            model=os.getenv("PANTHEON_OPENAI_MODEL", "gpt5.5")
        )

        result = resolve_action_candidate("跳向前厅", "修道院门口", provider=provider)

        self.assertFalse(result.used_fallback)
        self.assertTrue(result.validation.is_valid)
        self.assertEqual(result.action["intent"], "move")
        self.assertEqual(result.action["target"], "前厅")
        self.assertIn("跳向", result.action["method"])


if __name__ == "__main__":
    unittest.main()
