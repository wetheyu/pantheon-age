import unittest

from llm_runtime.contracts import EventProposal, GeneratedContentProposal, SceneProposal
from llm_runtime.proposals import (
    validate_event_proposal,
    validate_generated_content_proposal,
    validate_scene_proposal,
)


class LLMRuntimeProposalTests(unittest.TestCase):
    def test_temporary_scene_proposal_is_valid(self):
        proposal = SceneProposal(
            title="前厅的灰尘",
            description="破碎长椅之间漂着细灰，像有人刚刚走过。",
            location="前厅",
            sensory_details=["潮湿木板声"],
            npcs=["无名老人"],
            authority_level="temporary",
            source="test",
        )

        validation = validate_scene_proposal(proposal)

        self.assertTrue(validation.is_valid)
        self.assertEqual(validation.errors, ())

    def test_flavor_event_proposal_is_valid(self):
        proposal = EventProposal(
            event_type="rumor",
            summary="有人说钟楼在无人敲击时响过三次。",
            location="前厅",
            hooks=["询问目击者", "检查钟楼"],
            authority_level="flavor",
            source="test",
        )

        validation = validate_event_proposal(proposal)

        self.assertTrue(validation.is_valid)

    def test_scene_allows_generated_location_candidate(self):
        proposal = SceneProposal(
            title="不存在的王宫",
            description="一座不该出现的王宫。",
            location="不存在的王宫",
            source="test",
        )

        validation = validate_scene_proposal(proposal)

        self.assertTrue(validation.is_valid)

    def test_scene_rejects_persistent_claims(self):
        proposal = SceneProposal(
            title="新教会总部",
            description="这里被宣布为新的教会总部。",
            location="前厅",
            authority_level="persistent",
            claimed_facts=["前厅现在是新教会总部"],
            source="test",
        )

        validation = validate_scene_proposal(proposal)

        self.assertFalse(validation.is_valid)
        self.assertTrue(any("persistent facts" in error for error in validation.errors))
        self.assertTrue(any("persistent" in error for error in validation.errors))

    def test_event_rejects_mechanical_claims(self):
        proposal = EventProposal(
            event_type="reward",
            summary="一个陌生人把神器交给你。",
            location="前厅",
            authority_level="mechanical",
            claimed_state_changes=["HP +10"],
            claimed_new_clues=["神器真相"],
            claimed_location_after="地下墓室",
            source="test",
        )

        validation = validate_event_proposal(proposal)

        self.assertFalse(validation.is_valid)
        self.assertTrue(any("mechanical" in error for error in validation.errors))
        self.assertTrue(any("state changes" in error for error in validation.errors))
        self.assertTrue(any("grant clues" in error for error in validation.errors))
        self.assertTrue(any("move the player" in error for error in validation.errors))

    def test_empty_scene_text_is_rejected(self):
        proposal = SceneProposal(title="", description="", location="前厅", source="test")

        validation = validate_scene_proposal(proposal)

        self.assertFalse(validation.is_valid)
        self.assertIn("Scene title is empty.", validation.errors)
        self.assertIn("Scene description is empty.", validation.errors)

    def test_empty_event_text_is_rejected(self):
        proposal = EventProposal(event_type="", summary="", location="前厅", source="test")

        validation = validate_event_proposal(proposal)

        self.assertFalse(validation.is_valid)
        self.assertIn("Event type is empty.", validation.errors)
        self.assertIn("Event summary is empty.", validation.errors)

    def test_generated_npc_can_be_temporary(self):
        proposal = GeneratedContentProposal(
            content_type="npc",
            name="灰围巾的码头书记员",
            description="他在潮湿账簿旁反复擦拭手指。",
            authority_level="temporary",
            tags=["dock", "rumor_source"],
            related_entities=["维拉尔"],
            temporary_relationships=["他害怕港口巡夜人"],
            source="test",
        )

        validation = validate_generated_content_proposal(proposal)

        self.assertTrue(validation.is_valid)

    def test_generated_item_can_be_temporary_object(self):
        proposal = GeneratedContentProposal(
            content_type="item",
            name="裂纹铜怀表",
            description="一枚停在午夜十二点的怀表。",
            authority_level="flavor",
            tags=["object", "occult_hint"],
            source="test",
        )

        validation = validate_generated_content_proposal(proposal)

        self.assertTrue(validation.is_valid)

    def test_generated_content_rejects_mechanical_or_persistent_claims(self):
        proposal = GeneratedContentProposal(
            content_type="team",
            name="午夜调查小队",
            description="一支刚刚成立的长期队伍。",
            authority_level="persistent",
            claimed_facts=["午夜调查小队成为长期组织"],
            claimed_inventory_changes=["获得裂纹铜怀表"],
            claimed_relationship_changes=["书记员成为永久盟友"],
            claimed_faction_changes=["潮汐圣会信任 +1"],
            source="test",
        )

        validation = validate_generated_content_proposal(proposal)

        self.assertFalse(validation.is_valid)
        self.assertTrue(any("persistent facts" in error for error in validation.errors))
        self.assertTrue(any("inventory" in error for error in validation.errors))
        self.assertTrue(any("relationship" in error for error in validation.errors))
        self.assertTrue(any("faction" in error for error in validation.errors))

    def test_generated_content_rejects_unknown_type(self):
        proposal = GeneratedContentProposal(
            content_type="god",
            name="第九神",
            description="不该被随意生成的神明。",
            source="test",
        )

        validation = validate_generated_content_proposal(proposal)

        self.assertFalse(validation.is_valid)
        self.assertIn("Unsupported generated content type: god", validation.errors)


if __name__ == "__main__":
    unittest.main()
