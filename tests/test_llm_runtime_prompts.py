import tempfile
import unittest
from pathlib import Path

from llm_runtime.prompts import (
    PromptNotFoundError,
    list_prompt_names,
    load_prompt,
    normalize_prompt_name,
)


class LLMRuntimePromptTests(unittest.TestCase):
    def test_load_narrator_prompt(self):
        prompt = load_prompt("narrator")

        self.assertIn("Narrator", prompt)
        self.assertIn("NarrationProposal", prompt)
        self.assertIn("claimed_new_clues", prompt)
        self.assertIn("mutate `GameState`", prompt)
        self.assertIn("contradict `rule_result`", prompt)

    def test_load_action_candidate_prompt(self):
        prompt = load_prompt("action_candidate")

        self.assertIn("Action Candidate Agent", prompt)
        self.assertIn("ActionCandidate", prompt)
        self.assertIn("Supported Intents", prompt)
        self.assertIn("Python validator", prompt)

    def test_load_scene_event_prompt(self):
        prompt = load_prompt("scene_event")

        self.assertIn("Scene And Event Proposal Agent", prompt)
        self.assertIn("SceneProposal", prompt)
        self.assertIn("EventProposal", prompt)
        self.assertIn("Authority Levels", prompt)

    def test_load_open_generation_prompt(self):
        prompt = load_prompt("open_generation")

        self.assertIn("Open Generation Proposal Agent", prompt)
        self.assertIn("content_type", prompt)
        self.assertIn("relationship", prompt)
        self.assertIn("Python validator", prompt)

    def test_list_prompt_names_includes_runtime_prompts(self):
        self.assertIn("narrator", list_prompt_names())
        self.assertIn("action_candidate", list_prompt_names())
        self.assertIn("scene_event", list_prompt_names())
        self.assertIn("open_generation", list_prompt_names())

    def test_normalize_prompt_name_accepts_plain_or_markdown_name(self):
        self.assertEqual(normalize_prompt_name("narrator"), "narrator.md")
        self.assertEqual(normalize_prompt_name("narrator.md"), "narrator.md")

    def test_normalize_prompt_name_rejects_path_separators(self):
        with self.assertRaises(ValueError):
            normalize_prompt_name("../secret")

    def test_missing_prompt_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(PromptNotFoundError):
                load_prompt("missing", prompt_root=Path(temp_dir))


if __name__ == "__main__":
    unittest.main()
