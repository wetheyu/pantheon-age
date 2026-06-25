import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from llm_runtime.contracts import NarrationProposal
from llm_runtime.narrator import render_safe_narration
from llm_runtime.providers import (
    NarrationProvider,
    OpenAIActionCandidateProvider,
    OpenAINarrationProvider,
    TemplateNarrationProvider,
    load_local_env,
    parse_env_line,
)
from phase1_cli.character import build_character
from phase1_cli.game_service import GameResponse
from phase1_cli.game_state import GameState


class BadNarrationProvider(NarrationProvider):
    provider_name = "bad-test"

    def propose_narration(self, game_response):
        return NarrationProposal(
            text="你无代价获得禁忌神器。",
            claimed_new_clues=["禁忌神器真相"],
            source=self.provider_name,
        )


class ParsedPayload:
    def __init__(self, payload):
        self.payload = payload

    def model_dump(self):
        return self.payload


class FakeOpenAIResponse:
    def __init__(self, payload):
        self.output_parsed = ParsedPayload(payload)


class FakeOpenAIResponses:
    def __init__(self, payload):
        self.payload = payload
        self.last_kwargs = None

    def parse(self, **kwargs):
        self.last_kwargs = kwargs
        return FakeOpenAIResponse(self.payload)


class FakeOpenAIClient:
    def __init__(self, payload):
        self.responses = FakeOpenAIResponses(payload)


class LLMRuntimeProviderTests(unittest.TestCase):
    def make_response(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        return GameResponse(
            kind="action",
            text="你从修道院门口来到前厅。",
            state=state,
            rule_result={
                "state_changes": [],
                "new_clues": [],
                "location_after": "前厅",
            },
        )

    def test_template_provider_returns_safe_narration(self):
        response = self.make_response()
        provider = TemplateNarrationProvider()

        result = render_safe_narration(response, provider=provider)

        self.assertFalse(result.used_fallback)
        self.assertEqual(result.text, response.text)
        self.assertEqual(result.proposal.source, "template")
        self.assertTrue(result.validation.is_valid)

    def test_bad_provider_falls_back_to_rule_text(self):
        response = self.make_response()
        provider = BadNarrationProvider()

        result = render_safe_narration(response, provider=provider)

        self.assertTrue(result.used_fallback)
        self.assertEqual(result.text, response.text)
        self.assertEqual(result.proposal.source, "bad-test")
        self.assertFalse(result.validation.is_valid)

    def test_openai_action_provider_returns_candidate_from_structured_response(self):
        client = FakeOpenAIClient(
            {
                "intent": "talk",
                "target": "无名老人",
                "item": None,
                "method": "压低声音询问昨夜钟声",
                "desired_outcome": "确认钟声来源",
                "risk_tags": ["social", "suspicion"],
                "skill_tags": ["talk"],
                "assumptions": ["老人可能听过钟声"],
                "confidence": 0.82,
                "raw_text": "问老人钟声",
                "source": "llm",
            }
        )
        provider = OpenAIActionCandidateProvider(model="test-model", client=client)

        candidate = provider.propose_action_candidate("问老人钟声", "前厅")

        self.assertEqual(candidate.intent, "talk")
        self.assertEqual(candidate.target, "无名老人")
        self.assertEqual(candidate.source, "openai-action")
        self.assertEqual(client.responses.last_kwargs["model"], "test-model")

    def test_openai_narration_provider_returns_proposal_from_structured_response(self):
        client = FakeOpenAIClient(
            {
                "text": "前厅的尘埃在你靴边散开，破碎长椅像退潮后的残骸。",
                "claimed_state_changes": [],
                "claimed_new_clues": [],
                "claimed_location_after": "前厅",
                "source": "llm",
            }
        )
        provider = OpenAINarrationProvider(model="test-model", client=client)

        proposal = provider.propose_narration(self.make_response())

        self.assertIn("前厅", proposal.text)
        self.assertEqual(proposal.claimed_location_after, "前厅")
        self.assertEqual(proposal.source, "openai")

    def test_parse_env_line_supports_quotes_and_export(self):
        self.assertEqual(parse_env_line("OPENAI_API_KEY='sk-test'"), ("OPENAI_API_KEY", "sk-test"))
        self.assertEqual(parse_env_line('export PANTHEON_USE_LLM="1"'), ("PANTHEON_USE_LLM", "1"))
        self.assertIsNone(parse_env_line("# comment"))
        self.assertIsNone(parse_env_line("not-an-env-line"))

    def test_load_local_env_does_not_override_existing_values(self):
        with TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "\n".join(
                    [
                        "OPENAI_API_KEY=from-file",
                        "PANTHEON_USE_LLM=1",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict(
                "os.environ",
                {"OPENAI_API_KEY": "from-shell"},
                clear=True,
            ):
                load_local_env(env_path)

                import os

                self.assertEqual(os.environ["OPENAI_API_KEY"], "from-shell")
                self.assertEqual(os.environ["PANTHEON_USE_LLM"], "1")


if __name__ == "__main__":
    unittest.main()
