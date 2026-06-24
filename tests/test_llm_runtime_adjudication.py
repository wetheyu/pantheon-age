import unittest

from llm_runtime.adjudication import adjudicate_candidate, build_adjudication_request
from llm_runtime.contracts import ActionCandidate, AdjudicationRequest
from llm_runtime.adjudication import validate_adjudication_request


class LLMRuntimeAdjudicationTests(unittest.TestCase):
    def test_social_candidate_preserves_method_and_risks(self):
        candidate = ActionCandidate(
            intent="talk",
            target="无名老人",
            method="把圣徽藏进袖口，伪装成普通旅人后试探询问",
            desired_outcome="了解昨晚钟楼是否响过",
            risk_tags=["deception", "suspicion"],
            skill_tags=["stealth", "talk"],
            assumptions=["老人可能听过钟声"],
            source="test",
        )

        request = build_adjudication_request(candidate)

        self.assertEqual(request.check_type, "social")
        self.assertTrue(request.requires_check)
        self.assertEqual(request.primary_stat, "intelligence")
        self.assertEqual(request.difficulty, 14)
        self.assertEqual(request.method, "把圣徽藏进袖口，伪装成普通旅人后试探询问")
        self.assertEqual(request.desired_outcome, "了解昨晚钟楼是否响过")
        self.assertIn("social", request.skill_tags)
        self.assertIn("stealth", request.skill_tags)
        self.assertIn("deception", request.risk_tags)
        self.assertIn("suspicion_gain", request.possible_costs)
        self.assertEqual(request.assumptions, ("老人可能听过钟声",))

    def test_attack_candidate_builds_combat_adjudication(self):
        candidate = ActionCandidate(intent="attack", method="用旧长剑逼退黑影", source="test")

        result = adjudicate_candidate(candidate)

        self.assertTrue(result.validation.is_valid)
        self.assertEqual(result.request.check_type, "combat")
        self.assertEqual(result.request.primary_stat, "strength")
        self.assertIn("hp_loss", result.request.possible_costs)

    def test_move_candidate_does_not_require_check_by_default(self):
        candidate = ActionCandidate(intent="move", target="祈祷大厅", source="test")

        result = adjudicate_candidate(candidate)

        self.assertTrue(result.validation.is_valid)
        self.assertFalse(result.request.requires_check)
        self.assertIsNone(result.request.primary_stat)
        self.assertIsNone(result.request.difficulty)

    def test_unknown_candidate_becomes_unknown_adjudication(self):
        candidate = ActionCandidate(intent="unknown", method="做一件系统暂时无法理解的事", source="test")

        result = adjudicate_candidate(candidate)

        self.assertTrue(result.validation.is_valid)
        self.assertEqual(result.request.check_type, "unknown")
        self.assertIn("unknown", result.request.risk_tags)

    def test_invalid_adjudication_request_rejects_bad_tags(self):
        request = AdjudicationRequest(
            intent="talk",
            check_type="social",
            requires_check=True,
            primary_stat="intelligence",
            difficulty=14,
            skill_tags=["social"],
            risk_tags=["mind_control"],
            possible_costs=["suspicion_gain"],
        )

        validation = validate_adjudication_request(request)

        self.assertFalse(validation.is_valid)
        self.assertIn("Unsupported risk tag: mind_control", validation.errors)


if __name__ == "__main__":
    unittest.main()
