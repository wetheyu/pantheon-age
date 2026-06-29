import unittest

from llm_runtime.actions import (
    build_keyword_action_candidate,
    resolve_action_candidate,
    validate_action_candidate,
)
from llm_runtime.contracts import ActionCandidate
from llm_runtime.providers import KeywordActionCandidateProvider, OpenAIActionCandidateProvider


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

    def parse(self, **_kwargs):
        return FakeOpenAIResponse(self.payload)


class FakeOpenAIClient:
    def __init__(self, payload):
        self.responses = FakeOpenAIResponses(payload)


class LLMRuntimeActionCandidateTests(unittest.TestCase):
    def test_keyword_candidate_wraps_existing_parser(self):
        candidate = build_keyword_action_candidate("前往祈祷大厅", "前厅")

        self.assertEqual(candidate.intent, "move")
        self.assertEqual(candidate.target, "祈祷大厅")
        self.assertEqual(candidate.source, "keyword")

    def test_valid_candidate_resolves_to_rule_engine_action(self):
        candidate = ActionCandidate(
            intent="move",
            target="祈祷大厅",
            method="沿着墙边慢慢靠近祈祷大厅",
            desired_outcome="进入大厅但尽量不发出声音",
            risk_tags=["noise", "time"],
            skill_tags=["move", "stealth"],
            assumptions=["大厅里可能有人"],
            confidence=0.9,
            raw_text="去大厅",
            source="test",
        )

        result = resolve_action_candidate("去大厅", "前厅", candidate=candidate)

        self.assertFalse(result.used_fallback)
        self.assertTrue(result.validation.is_valid)
        self.assertEqual(result.action["intent"], "move")
        self.assertEqual(result.action["target"], "祈祷大厅")
        self.assertEqual(result.action["method"], "沿着墙边慢慢靠近祈祷大厅")
        self.assertEqual(result.action["desired_outcome"], "进入大厅但尽量不发出声音")
        self.assertEqual(result.action["risk_tags"], ["noise", "time"])
        self.assertEqual(result.action["skill_tags"], ["move", "stealth"])
        self.assertEqual(result.action["assumptions"], ["大厅里可能有人"])
        self.assertFalse(result.action["requires_check"])

    def test_check_intent_gets_check_metadata(self):
        candidate = ActionCandidate(intent="attack", confidence=0.8, source="test")

        result = resolve_action_candidate("攻击黑影", "前厅", candidate=candidate)

        self.assertEqual(result.action["check_stat"], "physique")
        self.assertEqual(result.action["difficulty"], 14)
        self.assertTrue(result.action["requires_check"])

    def test_unknown_intent_falls_back_to_keyword_parser(self):
        candidate = ActionCandidate(intent="teleport", target="地下墓室", source="test")

        result = resolve_action_candidate("前往祈祷大厅", "前厅", candidate=candidate)

        self.assertTrue(result.used_fallback)
        self.assertFalse(result.validation.is_valid)
        self.assertEqual(result.action["intent"], "move")
        self.assertEqual(result.action["target"], "祈祷大厅")

    def test_move_target_can_be_generated_location_candidate(self):
        candidate = ActionCandidate(intent="move", target="不存在的王宫", source="test")

        validation = validate_action_candidate(candidate)

        self.assertTrue(validation.is_valid)

    def test_non_move_target_can_be_temporary_npc_or_object(self):
        candidate = ActionCandidate(intent="talk", target="无名老人", source="test")

        validation = validate_action_candidate(candidate)

        self.assertTrue(validation.is_valid)

    def test_item_can_be_generated_candidate(self):
        candidate = ActionCandidate(intent="use_item", item="不存在的神器", source="test")

        validation = validate_action_candidate(candidate)

        self.assertTrue(validation.is_valid)

    def test_confidence_must_be_between_zero_and_one(self):
        candidate = ActionCandidate(intent="talk", confidence=1.5, source="test")

        validation = validate_action_candidate(candidate)

        self.assertFalse(validation.is_valid)
        self.assertIn("between 0 and 1", validation.errors[0])

    def test_unknown_semantic_tag_is_rejected(self):
        candidate = ActionCandidate(
            intent="talk",
            risk_tags=["mind_control"],
            skill_tags=["social"],
            source="test",
        )

        validation = validate_action_candidate(candidate)

        self.assertFalse(validation.is_valid)
        self.assertIn("Unsupported risk tag: mind_control", validation.errors)

    def test_resolver_drops_unsupported_non_core_tags_without_fallback(self):
        candidate = ActionCandidate(
            intent="move",
            target="前厅",
            method="跳向前厅",
            risk_tags=["fall"],
            skill_tags=["acrobatics"],
            confidence=0.84,
            raw_text="跳向前厅",
            source="openai-action",
        )

        result = resolve_action_candidate("跳向前厅", "修道院门口", candidate=candidate)

        self.assertFalse(result.used_fallback)
        self.assertTrue(result.validation.is_valid)
        self.assertEqual(result.action["intent"], "move")
        self.assertEqual(result.action["target"], "前厅")
        self.assertEqual(result.action["skill_tags"], [])
        self.assertEqual(result.action["risk_tags"], [])
        self.assertIn("Ignored unsupported skill tag", result.candidate.assumptions[0])

    def test_resolver_rejects_unsupported_core_intent(self):
        candidate = ActionCandidate(
            intent="jump",
            target="前厅",
            method="跳向前厅",
            confidence=0.84,
            raw_text="跳向前厅",
            source="bad-provider",
        )

        result = resolve_action_candidate("跳向前厅", "修道院门口", candidate=candidate)

        self.assertTrue(result.used_fallback)
        self.assertFalse(result.validation.is_valid)
        self.assertIn("Unsupported action intent: jump", result.validation.errors)

    def test_keyword_provider_resolves_without_llm(self):
        provider = KeywordActionCandidateProvider()

        result = resolve_action_candidate("喝下镇静", "前厅", provider=provider)

        self.assertFalse(result.used_fallback)
        self.assertEqual(result.action["intent"], "use_item")
        self.assertEqual(result.action["item"], "镇静药剂")

    def test_openai_action_provider_can_feed_resolver(self):
        provider = OpenAIActionCandidateProvider(
            model="test-model",
            client=FakeOpenAIClient(
                {
                    "intent": "stealth",
                    "target": "档案柜",
                    "item": None,
                    "method": "贴着墙影绕到档案柜后方",
                    "desired_outcome": "不惊动任何东西地靠近",
                    "risk_tags": ["noise", "suspicion"],
                    "skill_tags": ["stealth"],
                    "assumptions": ["前厅里可能还有东西在听"],
                    "confidence": 0.9,
                    "raw_text": "悄悄靠近档案柜",
                    "source": "llm",
                }
            ),
        )

        result = resolve_action_candidate("悄悄靠近档案柜", "前厅", provider=provider)

        self.assertFalse(result.used_fallback)
        self.assertEqual(result.action["intent"], "stealth")
        self.assertEqual(result.action["target"], "档案柜")
        self.assertEqual(result.action["skill_tags"], ["stealth"])


if __name__ == "__main__":
    unittest.main()
