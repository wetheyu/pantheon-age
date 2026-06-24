import unittest

from llm_runtime.contracts import NarrationProposal
from llm_runtime.narrator import (
    build_template_narration_proposal,
    render_safe_narration,
    validate_narration_proposal,
)
from phase1_cli.character import build_character
from phase1_cli.game_service import GameResponse
from phase1_cli.game_state import GameState


class LLMRuntimeNarratorTests(unittest.TestCase):
    def make_response(self):
        state = GameState(build_character("阿洛", "warrior", "死亡之神"))
        return GameResponse(
            kind="action",
            text="你从修道院门口来到前厅。",
            state=state,
            rule_result={
                "state_changes": ["SAN -1（令人不安的残缺记录）"],
                "new_clues": ["破损圣徽"],
                "location_after": "前厅",
            },
        )

    def test_template_narration_proposal_is_valid(self):
        response = self.make_response()
        proposal = build_template_narration_proposal(response)

        validation = validate_narration_proposal(response, proposal)

        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.errors, ())

    def test_valid_proposal_can_claim_rule_approved_facts(self):
        response = self.make_response()
        proposal = NarrationProposal(
            text="你抵达前厅，并注意到破损圣徽。",
            claimed_state_changes=["SAN -1（令人不安的残缺记录）"],
            claimed_new_clues=["破损圣徽"],
            claimed_location_after="前厅",
            source="test",
        )

        validation = validate_narration_proposal(response, proposal)

        self.assertTrue(validation.is_valid)

    def test_proposal_cannot_claim_unapproved_clue(self):
        response = self.make_response()
        proposal = NarrationProposal(
            text="你发现了不存在的核心真相。",
            claimed_new_clues=["不存在的核心真相"],
            source="test",
        )

        validation = validate_narration_proposal(response, proposal)

        self.assertFalse(validation.is_valid)
        self.assertIn("Unapproved clue claim", validation.errors[0])

    def test_proposal_cannot_claim_unapproved_location(self):
        response = self.make_response()
        proposal = NarrationProposal(
            text="你突然抵达地下墓室。",
            claimed_location_after="地下墓室",
            source="test",
        )

        validation = validate_narration_proposal(response, proposal)

        self.assertFalse(validation.is_valid)
        self.assertIn("Unapproved location claim", validation.errors[0])

    def test_invalid_proposal_falls_back_to_rule_text(self):
        response = self.make_response()

        def bad_proposer(_response):
            return NarrationProposal(
                text="你无代价获得神器。",
                claimed_new_clues=["神器真相"],
                source="bad-test",
            )

        result = render_safe_narration(response, proposer=bad_proposer)

        self.assertTrue(result.used_fallback)
        self.assertEqual(result.text, response.text)
        self.assertFalse(result.validation.is_valid)

    def test_empty_proposal_text_is_rejected(self):
        response = self.make_response()
        proposal = NarrationProposal(text="", source="test")

        validation = validate_narration_proposal(response, proposal)

        self.assertFalse(validation.is_valid)
        self.assertIn("Narration text is empty.", validation.errors)


if __name__ == "__main__":
    unittest.main()
