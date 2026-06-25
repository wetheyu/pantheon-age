import sys
from pathlib import Path
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from agentic_runtime.intent_agent import propose_open_action
from agentic_runtime.context_pack import build_context_pack, retrieve_relevant_lore_cards
from agentic_runtime.memory_store import (
    commit_memory_candidates,
    memory_bucket_records,
    memory_store_summary,
)
from agentic_runtime.memory_retriever import retrieve_memory
from agentic_runtime.orchestrator import run_agentic_turn
from agentic_runtime.providers import (
    AgenticProviders,
    OpenAIEventAgentProvider,
    OpenAIIntentAgentProvider,
    OpenAIItemAgentProvider,
    OpenAINarratorAgentProvider,
    OpenAINPCAgentProvider,
    OpenAIRuleArbiterProvider,
    OpenAITurnDirectorProvider,
    OpenAIWorldBundleProvider,
    build_agentic_providers_from_env,
    build_local_agentic_providers,
)
from agentic_runtime.rule_arbiter_agent import propose_rule_adjudication
from agentic_runtime.contracts import (
    EventProposal,
    ItemProposal,
    MemoryCandidate,
    NarrationProposal,
    NPCProposal,
    RuleAdjudicationProposal,
    RuleCheckProposal,
)
from agentic_runtime.validators import (
    validate_event_proposal,
    validate_item_proposal,
    validate_memory_candidate,
    validate_narration_proposal,
    validate_npc_proposal,
    validate_open_action,
    validate_rule_adjudication,
    validate_temporary_content,
)
from agentic_runtime.world_relations import (
    NationRelationSignal,
    apply_relation_signal,
    create_neutral_relation,
    validate_relation_signal,
)
from phase1_cli.character import build_character
from phase1_cli.game_state import GameState
from phase1_cli.scenarios import configure_character_for_game_mode


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


class AgenticRuntimeTests(unittest.TestCase):
    def make_state(self):
        return GameState(build_character("阿洛", "warrior", "死亡之神"))

    def make_world_state(self):
        character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(character, "world")
        return GameState(character)

    def make_lumiere_world_state(self):
        character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(character, "world", "lumiere", "维拉尔")
        return GameState(character)

    def make_rosvia_world_state(self):
        character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(character, "world", "rosvia", "维亚洛夫")
        return GameState(character)

    def make_ost_world_state(self):
        character = build_character("阿洛", "warrior", "死亡之神")
        configure_character_for_game_mode(character, "world", "ost", "卡洛维茨", "波西恩人")
        return GameState(character)

    def test_intent_agent_preserves_open_player_method(self):
        state = self.make_state()

        proposal = propose_open_action("跳向前厅", state)

        self.assertEqual(proposal.method, "跳向前厅")
        self.assertIn("前厅", proposal.targets)
        self.assertTrue(validate_open_action(proposal).is_valid)

    def test_rule_arbiter_bridges_reachable_target_without_keyword_patch(self):
        state = self.make_state()
        proposal = propose_open_action("跳向前厅", state)

        adjudication = propose_rule_adjudication(state, proposal)

        self.assertEqual(adjudication.action_type, "move")
        self.assertEqual(adjudication.bridge_action["target"], "前厅")
        self.assertTrue(validate_rule_adjudication(adjudication).is_valid)

    def test_agentic_turn_commits_to_state_and_keeps_trace(self):
        state = self.make_state()

        result = run_agentic_turn(state, "跳向前厅")

        self.assertEqual(state.current_location, "前厅")
        self.assertEqual(result.open_action.method, "跳向前厅")
        self.assertEqual(result.adjudication.action_type, "move")
        self.assertTrue(result.commit.committed)
        self.assertIn("location_change", result.commit.committed_effects)
        self.assertIn("你从修道院门口来到前厅", result.narration.text)
        self.assertEqual(result.providers["intent_agent"], "local-intent-agent")
        self.assertEqual(len(result.npcs), 1)
        self.assertEqual(len(result.events), 1)
        self.assertEqual(len(result.items), 1)
        self.assertEqual(len(result.memory_records), 1)
        self.assertEqual(result.memory_records[0].bucket, "quest")
        self.assertIn("无名见证者", result.narration.text)

    def test_world_mode_uses_world_action_without_tutorial_map_commit(self):
        state = self.make_world_state()

        result = run_agentic_turn(state, "调查格兰威克金融街的异常钟声")

        self.assertEqual(state.current_location, "格兰威克")
        self.assertEqual(result.adjudication.action_type, "world_action")
        self.assertEqual(result.commit.rule_result["intent"], "world_action")
        self.assertIn("world_attempt_recorded", result.commit.committed_effects)
        self.assertEqual(result.commit.rule_result["location_before"], "格兰威克")
        self.assertEqual(result.commit.rule_result["location_after"], "格兰威克")
        self.assertEqual(memory_store_summary(state)["quest"], 1)
        self.assertEqual(memory_store_summary(state)["player_known"], 1)
        self.assertEqual(len(result.npcs), 1)
        self.assertEqual(len(result.events), 1)
        self.assertEqual(len(result.items), 1)
        self.assertNotIn("【格兰威克】", result.narration.text)
        self.assertIn("城市的声响、人群和本地势力", result.narration.text)
        self.assertIn("被你注意到的人", result.narration.text)
        self.assertIn("你注意到", result.narration.text)
        self.assertIn("下一步追查的起点", result.narration.text)
        self.assertIn("被你注意到的人", result.npcs[0].name)
        self.assertEqual(result.items[0].claimed_inventory_changes, ())
        self.assertNotIn("雾吞掉了你的声音", result.narration.text)

    def test_world_slice_uses_visible_memory_without_confirming_rewards(self):
        state = self.make_world_state()
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="quest_memory",
                    subject="previous_world_action",
                    content="玩家已经调查过金融街异常钟声。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_1",
                ),
            ),
        )

        result = run_agentic_turn(state, "继续询问金融街钟声")

        self.assertIn("金融街异常钟声", result.temporary_content[0].description)
        self.assertEqual(result.commit.rule_result["new_clues"], [])
        self.assertEqual(result.commit.rule_result["state_changes"], [])
        self.assertEqual(state.current_location, "格兰威克")
        self.assertTrue(all(item.claimed_inventory_changes == () for item in result.items))

    def test_world_mode_memory_includes_origin_country_and_city(self):
        state = self.make_lumiere_world_state()

        memory = retrieve_memory(state, "调查海关仓库")

        self.assertEqual(state.current_location, "维拉尔")
        self.assertTrue(any("卢米埃共和国" in item for item in memory.player_known))
        self.assertTrue(any("维拉尔" in item for item in memory.location_context))

    def test_world_mode_memory_supports_other_important_country_origin(self):
        state = self.make_rosvia_world_state()

        memory = retrieve_memory(state, "调查旧圣像教堂")

        self.assertEqual(state.current_location, "维亚洛夫")
        self.assertTrue(any("罗斯维亚大公国" in item for item in memory.player_known))
        self.assertTrue(any("维亚洛夫" in item for item in memory.location_context))

    def test_world_mode_memory_includes_ost_ethnicity(self):
        state = self.make_ost_world_state()

        memory = retrieve_memory(state, "调查工厂区的机械异常")

        self.assertEqual(state.current_location, "卡洛维茨")
        self.assertTrue(any("奥斯特帝国" in item for item in memory.player_known))
        self.assertTrue(any("波西恩人" in item for item in memory.player_known))
        self.assertTrue(any("主导/国教：审判庭" in item for item in memory.player_known))
        self.assertTrue(any("敌对异教/邪教：密仪会、欲望母神邪教" in item for item in memory.player_known))

    def test_context_pack_retrieves_relevant_lore_cards(self):
        state = self.make_lumiere_world_state()
        memory = retrieve_memory(state, "我去码头询问海上异常")
        open_action = propose_open_action("我去码头询问海上异常", state, memory)

        context_pack = build_context_pack(
            state,
            user_text="我去码头询问海上异常",
            memory_retrieval=memory,
            open_action=open_action,
        )

        titles = [card["title"] for card in context_pack["relevant_lore_cards"]]

        self.assertLessEqual(len(context_pack["relevant_lore_cards"]), 6)
        self.assertTrue(any("卢米埃共和国" in title or "海洋之神" in title for title in titles))
        self.assertIn("generation_directives", context_pack)

    def test_relevant_lore_cards_are_ranked_without_full_document_dump(self):
        cards = retrieve_relevant_lore_cards("萨莱姆 密仪会 深渊 金门海峡", limit=3)

        titles = [card["title"] for card in cards]

        self.assertLessEqual(len(cards), 3)
        self.assertTrue(any("深渊之神" in title or "塞勒米亚" in title for title in titles))
        self.assertTrue(all(len(card["body"]) <= 930 for card in cards))

    def test_nation_relation_signal_can_update_dynamic_snapshot(self):
        snapshot = create_neutral_relation("albion", "selemia")
        signal = NationRelationSignal(
            country_a="albion",
            country_b="selemia",
            event_type="trade_deal",
            dimension="trade",
            delta=3,
            summary="双方签署金门海峡通行与保险赔付临时协定。",
            evidence=("金门海峡通行权", "阿尔比昂保险公司"),
        )

        self.assertEqual(validate_relation_signal(signal), ())

        updated = apply_relation_signal(snapshot, signal)

        self.assertEqual(updated.score, 3)
        self.assertEqual(updated.stance, "neutral")
        self.assertIn("trade", updated.drivers)
        self.assertEqual(updated.recent_signals[0].summary, signal.summary)

    def test_invalid_nation_relation_signal_is_rejected(self):
        signal = NationRelationSignal(
            country_a="albion",
            country_b="albion",
            event_type="miracle",
            dimension="unknown",
            delta=99,
            summary="",
        )

        errors = validate_relation_signal(signal)

        self.assertIn("country_a and country_b must be different", errors)
        self.assertIn("unknown event_type: miracle", errors)
        self.assertIn("unknown dimension: unknown", errors)
        self.assertIn("delta must be between -5 and 5", errors)
        self.assertIn("summary is required", errors)

    def test_temporary_scene_cannot_claim_state_changes(self):
        state = self.make_state()
        result = run_agentic_turn(state, "调查门口")

        validation = validate_temporary_content(result.temporary_content[0])

        self.assertTrue(validation.is_valid)
        self.assertEqual(result.temporary_content[0].authority_level, "temporary")

    def test_local_agentic_providers_can_drive_orchestrator(self):
        state = self.make_state()
        providers = build_local_agentic_providers()

        result = run_agentic_turn(state, "跳向前厅", providers=providers)

        self.assertEqual(result.providers["intent_agent"], "local-intent-agent")
        self.assertEqual(result.providers["npc_agent"], "local-npc-agent")
        self.assertEqual(result.providers["event_agent"], "local-event-agent")
        self.assertEqual(result.providers["item_agent"], "local-item-agent")
        self.assertEqual(result.adjudication.action_type, "move")
        self.assertEqual(state.current_location, "前厅")

    def test_default_agentic_llm_uses_turn_director_for_fast_creative_path(self):
        with patch.dict(
            "os.environ",
            {
                "PANTHEON_USE_AGENTIC_LLM": "1",
                "PANTHEON_AGENTIC_FULL_LLM": "0",
                "OPENAI_API_KEY": "test-key",
            },
            clear=False,
        ):
            providers = build_agentic_providers_from_env()

        self.assertEqual(providers.turn_director.provider_name, "openai-turn-director-agent")
        self.assertIsNone(providers.world_bundle)
        self.assertEqual(providers.intent_agent.provider_name, "local-intent-agent")
        self.assertEqual(providers.rule_arbiter.provider_name, "local-rule-arbiter")
        self.assertEqual(providers.npc_agent.provider_name, "local-npc-agent")
        self.assertEqual(providers.event_agent.provider_name, "local-event-agent")
        self.assertEqual(providers.item_agent.provider_name, "local-item-agent")

    def test_turn_director_can_be_disabled_for_legacy_multi_call_path(self):
        with patch.dict(
            "os.environ",
            {
                "PANTHEON_USE_AGENTIC_LLM": "1",
                "PANTHEON_AGENTIC_FULL_LLM": "0",
                "PANTHEON_AGENTIC_TURN_DIRECTOR": "0",
                "OPENAI_API_KEY": "test-key",
            },
            clear=False,
        ):
            providers = build_agentic_providers_from_env()

        self.assertIsNone(providers.turn_director)
        self.assertEqual(providers.intent_agent.provider_name, "openai-intent-agent")
        self.assertEqual(providers.rule_arbiter.provider_name, "openai-rule-arbiter-agent")
        self.assertEqual(providers.world_bundle.provider_name, "openai-world-bundle-agent")

    def test_openai_intent_agent_provider_returns_open_action_from_structured_response(self):
        state = self.make_state()
        client = FakeOpenAIClient(
            {
                "raw_text": "翻过长椅跳向前厅",
                "action_summary": "玩家翻过长椅跳向前厅。",
                "primary_goal": "到达前厅",
                "secondary_goals": ["动作迅速"],
                "method": "翻过长椅跳向前厅",
                "targets": ["前厅"],
                "player_assumptions": [],
                "requested_effects": ["location_change"],
                "confidence": 0.91,
                "source": "llm-intent-agent",
            }
        )
        provider = OpenAIIntentAgentProvider(model="test-model", client=client)

        proposal = provider.propose_open_action("翻过长椅跳向前厅", state)

        self.assertEqual(proposal.primary_goal, "到达前厅")
        self.assertEqual(proposal.source, "openai-intent-agent")
        self.assertIn("前厅", proposal.targets)
        self.assertEqual(client.responses.last_kwargs["model"], "test-model")
        self.assertEqual(client.responses.last_kwargs["text_format"].__name__, "OpenActionOutput")

    def test_openai_rule_arbiter_provider_returns_contextual_risk_adjudication(self):
        state = self.make_lumiere_world_state()
        memory = retrieve_memory(state, "刺杀巡逻守卫")
        open_action = propose_open_action("刺杀巡逻守卫", state, memory)
        client = FakeOpenAIClient(
            {
                "action_type": "world_action",
                "main_goal": "压制巡逻守卫",
                "secondary_goals": ["避免惊动更多人"],
                "required_checks": [
                    {
                        "check_type": "violence",
                        "stat": "agility",
                        "dc": 19,
                        "reason": "目标是巡逻守卫，且附近可能有同伴接应。",
                    }
                ],
                "allowed_effects": [
                    "temporary_scene",
                    "temporary_npc",
                    "temporary_event",
                    "temporary_item",
                    "attempt_recorded",
                    "world_check",
                    "suspicion_change",
                ],
                "conditional_effects": ["violent_attempt_advantage"],
                "denied_effects": [
                    "unearned_reward",
                    "unearned_secret",
                    "unearned_clue",
                    "unconfirmed_death",
                    "unconfirmed_permanent_injury",
                ],
                "bridge_action": {
                    "intent": "world_action",
                    "target": "巡逻守卫",
                    "item": None,
                    "requires_check": True,
                    "check_stat": "agility",
                    "difficulty": 19,
                    "risk_type": "violence",
                    "target_profile": "trained_guard",
                    "possible_blockers": ["nearby_patrol", "dock_witnesses"],
                    "success_consequence": "你取得短暂优势，但附近巡逻力量开始警觉。",
                    "failure_consequence": "守卫挡开你的动作，附近同伴立刻靠近。",
                    "raw_text": "刺杀巡逻守卫",
                    "open_method": "刺杀巡逻守卫",
                    "open_primary_goal": "压制巡逻守卫",
                    "open_requested_effects": ["combat_resolution"],
                    "player_assumptions": [],
                },
                "reasoning_summary": "巡逻守卫比普通路人更难对付，并有外部阻拦。",
                "source": "llm-rule-arbiter",
            }
        )
        provider = OpenAIRuleArbiterProvider(model="test-model", client=client)

        adjudication = provider.propose_rule_adjudication(state, open_action)

        self.assertEqual(adjudication.source, "openai-rule-arbiter-agent")
        self.assertEqual(adjudication.required_checks[0].dc, 19)
        self.assertEqual(adjudication.bridge_action["target_profile"], "trained_guard")
        self.assertIn("nearby_patrol", adjudication.bridge_action["possible_blockers"])
        self.assertTrue(validate_rule_adjudication(adjudication).is_valid)
        self.assertEqual(client.responses.last_kwargs["text_format"].__name__, "RuleAdjudicationOutput")

    def test_openai_world_agent_providers_return_temporary_candidates(self):
        state = self.make_lumiere_world_state()
        memory = retrieve_memory(state, "询问码头书记员")
        open_action = propose_open_action("询问码头书记员", state, memory)

        npc_client = FakeOpenAIClient(
            {
                "name": "灰围巾的码头书记员",
                "role": "临时证人",
                "description": "他站在湿账簿旁，像是不愿提起某艘船。",
                "visible_knowledge": ["他看见玩家靠近码头账簿。"],
                "attitude": "cautious",
                "short_term_goal": "避免被卷入港口麻烦。",
                "authority_level": "temporary",
                "claimed_facts": [],
                "claimed_state_changes": [],
                "claimed_new_clues": [],
            }
        )
        event_client = FakeOpenAIClient(
            {
                "event_type": "local_reaction",
                "summary": "仓库深处的煤气灯闪烁，人群短暂安静下来。",
                "hooks": ["观察人群反应。"],
                "involved_npcs": ["灰围巾的码头书记员"],
                "authority_level": "temporary",
                "claimed_facts": [],
                "claimed_state_changes": [],
                "claimed_new_clues": [],
            }
        )
        item_client = FakeOpenAIClient(
            {
                "name": "沾盐的铜票夹",
                "description": "它压在账簿边缘，夹缝里有细小盐粒。",
                "possible_uses": ["调查材质", "询问主人"],
                "risk_tags": ["unknown"],
                "authority_level": "temporary",
                "claimed_inventory_changes": [],
                "claimed_state_changes": [],
                "claimed_new_clues": [],
            }
        )

        npc = OpenAINPCAgentProvider(model="test-model", client=npc_client).propose_npcs(
            state,
            open_action,
            memory,
        )[0]
        event = OpenAIEventAgentProvider(model="test-model", client=event_client).propose_events(
            state,
            open_action,
            memory,
            npcs=(npc,),
        )[0]
        item = OpenAIItemAgentProvider(model="test-model", client=item_client).propose_items(
            state,
            open_action,
            memory,
        )[0]

        self.assertEqual(npc.source, "openai-npc-agent")
        self.assertEqual(event.source, "openai-event-agent")
        self.assertEqual(item.source, "openai-item-agent")
        self.assertTrue(validate_npc_proposal(npc).is_valid)
        self.assertTrue(validate_event_proposal(event).is_valid)
        self.assertTrue(validate_item_proposal(item).is_valid)
        self.assertEqual(npc_client.responses.last_kwargs["text_format"].__name__, "NPCOutput")
        self.assertEqual(event_client.responses.last_kwargs["text_format"].__name__, "EventOutput")
        self.assertEqual(item_client.responses.last_kwargs["text_format"].__name__, "ItemOutput")

    def test_openai_narrator_agent_provider_returns_player_facing_story(self):
        state = self.make_lumiere_world_state()
        local_result = run_agentic_turn(state, "询问码头水手")
        client = FakeOpenAIClient(
            {
                "text": "水手抬头看了你一眼，把声音压低：最近有船在无风时逆潮而行。码头边的人群忽然安静下来，像是都听见了某个不该出现的名字。",
                "claimed_effects": ["world_attempt_recorded"],
                "source": "llm-agentic-narrator",
            }
        )
        provider = OpenAINarratorAgentProvider(model="test-model", client=client)

        narration = provider.narrate_turn(
            state,
            local_result.memory_retrieval,
            local_result.open_action,
            local_result.temporary_content,
            local_result.adjudication,
            local_result.commit,
            local_result.memory_candidates,
            npc_proposals=local_result.npcs,
            event_proposals=local_result.events,
            item_proposals=local_result.items,
        )

        self.assertEqual(narration.source, "openai-narrator-agent")
        self.assertIn("水手抬头", narration.text)
        self.assertTrue(validate_narration_proposal(narration, local_result.commit).is_valid)
        self.assertEqual(client.responses.last_kwargs["text_format"].__name__, "AgenticNarrationOutput")

    def test_openai_world_bundle_provider_returns_categorized_content(self):
        state = self.make_lumiere_world_state()
        local_result = run_agentic_turn(state, "询问码头水手")
        client = FakeOpenAIClient(
            {
                "scene": {
                    "content_type": "world_scene",
                    "title": "码头边的低语",
                    "description": "潮湿石板路边，搬运工因为你的询问而压低声音。",
                    "authority_level": "temporary",
                    "related_targets": ["码头水手"],
                    "claimed_state_changes": [],
                    "claimed_new_clues": [],
                },
                "npc": {
                    "name": "压低帽檐的水手",
                    "role": "witness",
                    "description": "他把手搭在潮湿缆绳上，回答前先看了一眼码头尽头。",
                    "visible_knowledge": ["他听见玩家询问海上异常。"],
                    "attitude": "guarded",
                    "short_term_goal": "判断玩家是否可信。",
                    "authority_level": "temporary",
                    "claimed_facts": [],
                    "claimed_state_changes": [],
                    "claimed_new_clues": [],
                },
                "event": {
                    "event_type": "local_reaction",
                    "summary": "附近搬运工突然停止说笑，像是听见了不该被提起的船名。",
                    "hooks": ["可以追问船名。"],
                    "involved_npcs": ["压低帽檐的水手"],
                    "authority_level": "temporary",
                    "claimed_facts": [],
                    "claimed_state_changes": [],
                    "claimed_new_clues": [],
                },
                "item": {
                    "name": "沾盐的旧船票",
                    "description": "船票边缘卷曲，油墨被海水泡得发灰。",
                    "possible_uses": ["询问来源", "观察票面"],
                    "risk_tags": ["unknown"],
                    "authority_level": "temporary",
                    "claimed_inventory_changes": [],
                    "claimed_state_changes": [],
                    "claimed_new_clues": [],
                },
                "narration": {
                    "text": "水手听见你的问题后沉默了一会儿。码头边的风把他的外套吹得猎猎作响，他最终只说：最近有船在无灯的夜里回港。",
                    "claimed_effects": ["world_attempt_recorded"],
                    "source": "llm-world-bundle-narrator",
                },
            }
        )
        provider = OpenAIWorldBundleProvider(model="test-model", client=client)

        scenes, npcs, events, items, narration = provider.propose_world_bundle(
            state,
            local_result.memory_retrieval,
            local_result.open_action,
            local_result.temporary_content,
            local_result.adjudication,
            local_result.commit,
            local_result.memory_candidates,
        )

        self.assertEqual(scenes[0].source, "openai-world-bundle-scene")
        self.assertEqual(npcs[0].source, "openai-world-bundle-npc")
        self.assertEqual(events[0].source, "openai-world-bundle-event")
        self.assertEqual(items[0].source, "openai-world-bundle-item")
        self.assertEqual(narration.source, "openai-world-bundle-narrator")
        self.assertTrue(validate_temporary_content(scenes[0]).is_valid)
        self.assertTrue(validate_npc_proposal(npcs[0]).is_valid)
        self.assertTrue(validate_event_proposal(events[0]).is_valid)
        self.assertTrue(validate_item_proposal(items[0]).is_valid)
        self.assertTrue(validate_narration_proposal(narration, local_result.commit).is_valid)
        self.assertEqual(client.responses.last_kwargs["text_format"].__name__, "WorldBundleOutput")
        self.assertIn("context_pack", client.responses.last_kwargs["input"])

    def test_openai_turn_director_provider_drives_single_call_turn(self):
        state = self.make_lumiere_world_state()
        client = FakeOpenAIClient(
            {
                "open_action": {
                    "raw_text": "询问码头水手",
                    "action_summary": "玩家试图向码头水手打听海上异常。",
                    "primary_goal": "打听海上异常",
                    "secondary_goals": ["判断水手是否可信"],
                    "method": "上前询问码头水手",
                    "targets": ["码头水手", "海上异常"],
                    "player_assumptions": [],
                    "requested_effects": ["social_contact"],
                    "confidence": 0.9,
                },
                "adjudication": {
                    "action_type": "world_action",
                    "main_goal": "与码头水手建立交谈",
                    "secondary_goals": ["观察对方反应"],
                    "required_checks": [],
                    "allowed_effects": [
                        "temporary_scene",
                        "temporary_npc",
                        "temporary_event",
                        "temporary_item",
                        "attempt_recorded",
                    ],
                    "conditional_effects": [],
                    "denied_effects": [
                        "unearned_reward",
                        "unearned_secret",
                        "unearned_clue",
                        "unconfirmed_death",
                        "unconfirmed_permanent_injury",
                    ],
                    "bridge_action": {
                        "intent": "world_action",
                        "target": "码头水手",
                        "item": None,
                        "requires_check": False,
                        "check_stat": None,
                        "difficulty": None,
                        "risk_type": None,
                        "target_profile": "dock_sailor",
                        "possible_blockers": [],
                        "success_consequence": "",
                        "failure_consequence": "",
                        "raw_text": "询问码头水手",
                        "open_method": "上前询问码头水手",
                        "open_primary_goal": "打听海上异常",
                        "open_requested_effects": ["social_contact"],
                        "player_assumptions": [],
                    },
                    "reasoning_summary": "普通社交接触不需要检定，但不会自动授予线索。",
                },
                "scene": {
                    "content_type": "world_scene",
                    "title": "潮湿码头",
                    "description": "海盐味和煤烟味在码头棚架下混在一起，水手们说话时刻意压低声音。",
                    "authority_level": "temporary",
                    "related_targets": ["码头水手"],
                    "claimed_state_changes": [],
                    "claimed_new_clues": [],
                },
                "npc": {
                    "name": "灰帽水手",
                    "role": "临时信息提供者",
                    "description": "他用拇指摩挲着烟斗，回答前先看向仓库阴影。",
                    "visible_knowledge": ["他听见玩家询问海上异常。"],
                    "attitude": "cautious",
                    "short_term_goal": "判断玩家是否值得信任。",
                    "authority_level": "temporary",
                    "claimed_facts": [],
                    "claimed_state_changes": [],
                    "claimed_new_clues": [],
                },
                "event": {
                    "event_type": "local_reaction",
                    "summary": "附近搬运工短暂安静下来，像是不愿让这个话题扩散。",
                    "hooks": ["追问具体船名", "观察仓库阴影"],
                    "involved_npcs": ["灰帽水手"],
                    "authority_level": "temporary",
                    "claimed_facts": [],
                    "claimed_state_changes": [],
                    "claimed_new_clues": [],
                },
                "item": {
                    "name": "沾盐的旧船票",
                    "description": "旧船票压在木箱边缘，油墨被海风泡得发灰。",
                    "possible_uses": ["询问船票来源", "观察票面"],
                    "risk_tags": ["unknown"],
                    "authority_level": "temporary",
                    "claimed_inventory_changes": [],
                    "claimed_state_changes": [],
                    "claimed_new_clues": [],
                },
                "narration": {
                    "text": "码头的棚架低低压在头顶，海盐和煤烟让空气有种潮湿的苦味。\n\n灰帽水手听见你的问题，拇指在烟斗上停了一下。他没有立刻回答，只是往仓库阴影里瞥了一眼。\n\n附近搬运工的笑声短暂断开，又很快装作无事发生。\n\n你可以继续追问船名，也可以先观察他刚才看的方向。",
                    "claimed_effects": [],
                },
                "success_narration": {
                    "text": "水手的戒备略微松动，但他仍然没有把话说死。\n\n你抢到了一个继续追问的窗口。",
                    "claimed_effects": [],
                },
                "failure_narration": {
                    "text": "水手退后半步，语气变得僵硬。\n\n这个话题显然让周围的人更警惕了。",
                    "claimed_effects": [],
                },
            }
        )
        local = build_local_agentic_providers()
        providers = AgenticProviders(
            memory_retriever=local.memory_retriever,
            intent_agent=local.intent_agent,
            scene_agent=local.scene_agent,
            npc_agent=local.npc_agent,
            event_agent=local.event_agent,
            item_agent=local.item_agent,
            rule_arbiter=local.rule_arbiter,
            memory_curator=local.memory_curator,
            narrator_agent=local.narrator_agent,
            turn_director=OpenAITurnDirectorProvider(model="test-model", client=client),
            llm_enabled=True,
            model="test-model",
            reason="test turn director",
        )

        result = run_agentic_turn(state, "询问码头水手", providers=providers)

        self.assertEqual(result.providers["turn_director"], "openai-turn-director-agent")
        self.assertEqual(result.open_action.source, "openai-turn-director-intent")
        self.assertEqual(result.adjudication.source, "openai-turn-director-rule-arbiter")
        self.assertEqual(result.npcs[0].source, "openai-turn-director-npc")
        self.assertIn("灰帽水手", result.narration.text)
        self.assertEqual(result.errors, ())
        self.assertEqual(client.responses.last_kwargs["text_format"].__name__, "TurnDirectorOutput")
        self.assertIn("context_pack", client.responses.last_kwargs["input"])

    def test_world_agent_openai_failure_falls_back_per_agent(self):
        class FailingNPCAgent:
            provider_name = "failing-npc-agent"

            def propose_npcs(self, state, open_action, memory_retrieval=None):
                from llm_runtime.providers import OpenAIProviderError

                raise OpenAIProviderError("NPC provider unavailable.")

        class FailingEventAgent:
            provider_name = "failing-event-agent"

            def propose_events(self, state, open_action, memory_retrieval=None, npcs=()):
                from llm_runtime.providers import OpenAIProviderError

                raise OpenAIProviderError("Event provider unavailable.")

        class FailingItemAgent:
            provider_name = "failing-item-agent"

            def propose_items(self, state, open_action, memory_retrieval=None):
                from llm_runtime.providers import OpenAIProviderError

                raise OpenAIProviderError("Item provider unavailable.")

        state = self.make_world_state()
        local = build_local_agentic_providers()
        providers = AgenticProviders(
            memory_retriever=local.memory_retriever,
            intent_agent=local.intent_agent,
            scene_agent=local.scene_agent,
            npc_agent=FailingNPCAgent(),
            event_agent=FailingEventAgent(),
            item_agent=FailingItemAgent(),
            rule_arbiter=local.rule_arbiter,
            memory_curator=local.memory_curator,
            narrator_agent=local.narrator_agent,
            llm_enabled=True,
            model="test-model",
            reason="test failing world agents",
        )

        result = run_agentic_turn(state, "调查金融街的异常钟声", providers=providers)

        self.assertEqual(result.providers["npc_agent"], "failing-npc-agent")
        self.assertEqual(result.npcs[0].source, "local-npc-agent")
        self.assertEqual(result.events[0].source, "local-event-agent")
        self.assertEqual(result.items[0].source, "local-item-agent")
        self.assertEqual(len(result.errors), 3)
        self.assertTrue(any("NPC provider unavailable" in error for error in result.errors))

    def test_invalid_rule_arbiter_adjudication_falls_back_to_local(self):
        class InvalidRuleArbiter:
            provider_name = "invalid-rule-arbiter"

            def propose_rule_adjudication(self, state, open_action):
                return RuleAdjudicationProposal(
                    action_type="world_action",
                    main_goal="越权击杀目标",
                    required_checks=(
                        RuleCheckProposal(
                            check_type="violence",
                            stat="strength",
                            dc=99,
                            reason="不合理的超高 DC。",
                        ),
                    ),
                    allowed_effects=("target_death",),
                    denied_effects=(),
                    bridge_action={
                        "intent": "world_action",
                        "target": "目标",
                        "requires_check": True,
                        "check_stat": "strength",
                        "difficulty": 99,
                        "risk_type": "violence",
                        "target_profile": "unknown_target",
                        "possible_blockers": "not-a-list",
                        "success_consequence": "目标死了。",
                        "failure_consequence": "你失败了。",
                        "raw_text": open_action.raw_text,
                        "open_method": open_action.method,
                        "open_primary_goal": open_action.primary_goal,
                    },
                    reasoning_summary="这份裁定应该被 validator 拒绝。",
                    source="invalid-rule-arbiter",
                )

        state = self.make_world_state()
        local = build_local_agentic_providers()
        providers = AgenticProviders(
            memory_retriever=local.memory_retriever,
            intent_agent=local.intent_agent,
            scene_agent=local.scene_agent,
            npc_agent=local.npc_agent,
            event_agent=local.event_agent,
            item_agent=local.item_agent,
            rule_arbiter=InvalidRuleArbiter(),
            memory_curator=local.memory_curator,
            narrator_agent=local.narrator_agent,
            llm_enabled=True,
            model="test-model",
            reason="test invalid rule arbiter fallback",
        )

        result = run_agentic_turn(state, "出手杀了他", providers=providers)

        self.assertEqual(result.providers["rule_arbiter"], "invalid-rule-arbiter")
        self.assertFalse(result.validations["adjudication"].is_valid)
        self.assertTrue(result.validations["adjudication_fallback"].is_valid)
        self.assertEqual(result.adjudication.source, "local-rule-arbiter")
        self.assertEqual(result.commit.rule_result["roll"]["dc"], 16)
        self.assertIn("Rule arbiter proposal failed validation", result.errors[0])

    def test_memory_store_persists_only_validated_persistent_candidates(self):
        state = self.make_world_state()
        persistent = MemoryCandidate(
            memory_type="quest_memory",
            subject="committed_effects",
            content="world_attempt_recorded",
            authority_level="persistent",
            visibility="player_known",
            should_persist=True,
            source_event="turn_1",
        )
        temporary = MemoryCandidate(
            memory_type="player_memory",
            subject="player_action",
            content="玩家随口猜测码头有密道。",
            authority_level="temporary",
            visibility="player_known",
            should_persist=False,
            source_event="turn_1",
        )
        invalid = MemoryCandidate(
            memory_type="quest_memory",
            subject="raw_generation",
            content="模型随口说这里已经发现核心线索。",
            authority_level="persistent",
            visibility="player_known",
            should_persist=True,
            source_event="turn_1",
            source="openai-event-agent",
        )

        records = commit_memory_candidates(state, (persistent, temporary, invalid))

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].bucket, "quest")
        self.assertEqual(memory_store_summary(state)["quest"], 1)
        self.assertEqual(memory_store_summary(state)["player_known"], 0)
        self.assertIn("raw LLM provider", validate_memory_candidate(invalid).errors[0])

    def test_memory_store_separates_secret_memory(self):
        state = self.make_world_state()
        secret = MemoryCandidate(
            memory_type="secret_memory",
            subject="hidden_relation",
            content="某位 NPC 与夜幕修会有未公开联系。",
            authority_level="secret",
            visibility="system_secret",
            should_persist=True,
            source_event="turn_2",
        )

        records = commit_memory_candidates(state, (secret,))

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].bucket, "secret")
        self.assertEqual(memory_store_summary(state)["secret"], 1)
        self.assertEqual(memory_store_summary(state)["player_known"], 0)
        self.assertEqual(memory_bucket_records(state, "secret")[0].subject, "hidden_relation")

    def test_memory_retriever_reads_persisted_visible_memory(self):
        state = self.make_world_state()
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="quest_memory",
                    subject="dock_investigation",
                    content="玩家已经记录过码头钟声异常。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_1",
                ),
                MemoryCandidate(
                    memory_type="location_memory",
                    subject="格兰威克",
                    content="金融街附近近期出现异常钟声。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_1",
                ),
            ),
        )

        memory = retrieve_memory(state, "继续调查钟声")

        self.assertTrue(any("码头钟声异常" in item for item in memory.player_known))
        self.assertTrue(any("异常钟声" in item for item in memory.location_context))
        self.assertEqual(memory.source, "local-memory-store")

    def test_secret_memory_is_internal_not_serialized_or_narrated(self):
        state = self.make_world_state()
        secret_text = "某位书记员暗中效忠欲望母神。"
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="secret_memory",
                    subject="hidden_cult_link",
                    content=secret_text,
                    authority_level="secret",
                    visibility="system_secret",
                    should_persist=True,
                    source_event="turn_1",
                ),
            ),
        )

        result = run_agentic_turn(state, "询问码头书记员")
        payload = result.to_dict()

        self.assertTrue(any(secret_text in item for item in result.memory_retrieval.hidden_context))
        self.assertNotIn("hidden_context", payload["memory_retrieval"])
        self.assertNotIn(secret_text, result.narration.text)
        self.assertNotIn(secret_text, str(state.to_public_dict()))

    def test_agentic_memory_survives_state_dict_roundtrip(self):
        state = self.make_world_state()
        commit_memory_candidates(
            state,
            (
                MemoryCandidate(
                    memory_type="quest_memory",
                    subject="first_world_action",
                    content="玩家第一次调查了格兰威克金融街。",
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event="turn_1",
                ),
            ),
        )

        restored = GameState.from_dict(state.to_dict())
        memory = retrieve_memory(restored, "继续调查")

        self.assertEqual(memory_store_summary(restored)["quest"], 1)
        self.assertTrue(any("第一次调查" in item for item in memory.player_known))

    def test_npc_event_and_item_validators_reject_claimed_rewards(self):
        bad_npc = NPCProposal(
            name="知道真相的人",
            role="越权 NPC",
            description="他试图直接透露秘密。",
            claimed_new_clues=("核心秘密",),
        )
        bad_event = EventProposal(
            event_type="secret_reveal",
            summary="事件试图改写世界事实。",
            claimed_facts=("第九神明已降临",),
        )
        bad_item = ItemProposal(
            name="免费神器",
            description="试图直接进入背包。",
            claimed_inventory_changes=("add:免费神器",),
        )

        self.assertFalse(validate_npc_proposal(bad_npc).is_valid)
        self.assertFalse(validate_event_proposal(bad_event).is_valid)
        self.assertFalse(validate_item_proposal(bad_item).is_valid)

    def test_world_mode_violent_action_requires_roll_without_confirming_death(self):
        state = self.make_world_state()

        result = run_agentic_turn(state, "出手杀了他")

        self.assertEqual(result.adjudication.action_type, "world_action")
        self.assertTrue(result.adjudication.bridge_action["requires_check"])
        self.assertEqual(result.adjudication.bridge_action["risk_type"], "violence")
        self.assertIsNotNone(result.commit.rule_result["roll"])
        self.assertIn("world_attempt_recorded", result.commit.committed_effects)
        self.assertTrue(
            {"world_check_success", "world_check_failed"}.intersection(result.commit.committed_effects)
        )
        self.assertNotIn("target_death", result.commit.committed_effects)
        self.assertGreater(state.player.suspicion, 0)

    def test_narration_validator_rejects_uncommitted_death_claims(self):
        state = self.make_world_state()
        result = run_agentic_turn(state, "出手杀了他")
        bad_narration = NarrationProposal(
            text="你挥动武器直击守卫心口。他没有反应过来，便重重倒下。",
            claimed_effects=("world_attempt_recorded",),
            source="openai-world-bundle-narrator",
        )

        validation = validate_narration_proposal(bad_narration, result.commit)

        self.assertFalse(validation.is_valid)
        self.assertIn(
            "Narration confirmed death or killing without committed death authority.",
            validation.errors,
        )

    def test_narration_validator_allows_quoting_player_lethal_intent(self):
        state = self.make_world_state()
        result = run_agentic_turn(state, "出手杀了他")
        safe_narration = NarrationProposal(
            text="你选择：出手杀了他\n局势立刻绷紧，但最终结果还没有被规则确认。",
            claimed_effects=("world_attempt_recorded",),
            source="local-narrator-agent",
        )

        validation = validate_narration_proposal(safe_narration, result.commit)

        self.assertTrue(validation.is_valid)


if __name__ == "__main__":
    unittest.main()
