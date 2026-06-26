"""Provider interfaces for Phase 5 Agentic Runtime agents."""

import os
from dataclasses import dataclass
from typing import Literal, Optional

from pydantic import BaseModel, Field

from llm_runtime.providers import (
    OPENAI_MODEL_ENV_VAR,
    DEFAULT_OPENAI_MODEL,
    LLM_ENABLED_ENV_VAR,
    OpenAIProviderError,
    call_openai_structured,
    load_local_env,
    load_runtime_notes,
)

from .contracts import (
    EventProposal,
    ItemProposal,
    NarrationProposal,
    NPCProposal,
    OpenActionProposal,
    RuleAdjudicationProposal,
    RuleCheckProposal,
    TemporaryContentProposal,
    TurnDirectorProposal,
)
from .context_pack import build_context_pack
from .event_agent import propose_events
from .intent_agent import propose_open_action
from .item_agent import propose_items
from .memory_curator import curate_memory
from .memory_retriever import retrieve_memory
from .narrator_agent import narrate_turn
from .npc_agent import propose_npcs
from .rule_arbiter_agent import propose_rule_adjudication
from .scene_agent import propose_temporary_scene


AGENTIC_LLM_ENABLED_ENV_VAR = "PANTHEON_USE_AGENTIC_LLM"
AGENTIC_FULL_LLM_ENABLED_ENV_VAR = "PANTHEON_AGENTIC_FULL_LLM"
AGENTIC_TURN_DIRECTOR_ENV_VAR = "PANTHEON_AGENTIC_TURN_DIRECTOR"
CREATIVE_GM_ENABLED_ENV_VAR = "PANTHEON_CREATIVE_GM_MODE"
WORLD_RISK_TYPES = frozenset(
    ("violence", "social", "stealth", "theft", "escape", "occult", "travel", "high_risk")
)


class OpenActionOutput(BaseModel):
    raw_text: str
    action_summary: str
    primary_goal: str
    secondary_goals: list[str] = Field(default_factory=list)
    method: str = ""
    targets: list[str] = Field(default_factory=list)
    player_assumptions: list[str] = Field(default_factory=list)
    requested_effects: list[str] = Field(default_factory=list)
    confidence: float = 0.75
    source: str = "llm-intent-agent"


class NPCOutput(BaseModel):
    name: str
    role: str
    description: str
    visible_knowledge: list[str] = Field(default_factory=list)
    attitude: str = "neutral"
    short_term_goal: str = ""
    authority_level: str = "temporary"
    claimed_facts: list[str] = Field(default_factory=list)
    claimed_state_changes: list[str] = Field(default_factory=list)
    claimed_new_clues: list[str] = Field(default_factory=list)
    source: str = "llm-npc-agent"


class SceneOutput(BaseModel):
    content_type: str = "world_scene"
    title: str
    description: str
    authority_level: str = "temporary"
    related_targets: list[str] = Field(default_factory=list)
    claimed_state_changes: list[str] = Field(default_factory=list)
    claimed_new_clues: list[str] = Field(default_factory=list)
    source: str = "llm-scene-agent"


class EventOutput(BaseModel):
    event_type: str
    summary: str
    hooks: list[str] = Field(default_factory=list)
    involved_npcs: list[str] = Field(default_factory=list)
    authority_level: str = "temporary"
    claimed_facts: list[str] = Field(default_factory=list)
    claimed_state_changes: list[str] = Field(default_factory=list)
    claimed_new_clues: list[str] = Field(default_factory=list)
    source: str = "llm-event-agent"


class ItemOutput(BaseModel):
    name: str
    description: str
    possible_uses: list[str] = Field(default_factory=list)
    risk_tags: list[str] = Field(default_factory=list)
    authority_level: str = "temporary"
    claimed_inventory_changes: list[str] = Field(default_factory=list)
    claimed_state_changes: list[str] = Field(default_factory=list)
    claimed_new_clues: list[str] = Field(default_factory=list)
    source: str = "llm-item-agent"


class AgenticNarrationOutput(BaseModel):
    text: str
    claimed_effects: list[str] = Field(default_factory=list)
    source: str = "llm-agentic-narrator"


class WorldBundleOutput(BaseModel):
    scene: SceneOutput
    npc: NPCOutput
    event: EventOutput
    item: ItemOutput
    narration: AgenticNarrationOutput


class RuleCheckOutput(BaseModel):
    check_type: str
    stat: Optional[Literal["strength", "agility", "intelligence", "faith"]] = None
    dc: Optional[int] = None
    reason: str = ""


class RuleBridgeActionOutput(BaseModel):
    intent: str
    target: Optional[str] = None
    item: Optional[str] = None
    requires_check: bool = False
    check_stat: Optional[Literal["strength", "agility", "intelligence", "faith"]] = None
    difficulty: Optional[int] = None
    risk_type: Optional[
        Literal["violence", "social", "stealth", "theft", "escape", "occult", "travel", "high_risk"]
    ] = None
    target_profile: str = ""
    possible_blockers: list[str] = Field(default_factory=list)
    success_consequence: str = ""
    failure_consequence: str = ""
    raw_text: str
    open_method: str = ""
    open_primary_goal: str = ""
    open_requested_effects: list[str] = Field(default_factory=list)
    player_assumptions: list[str] = Field(default_factory=list)
    location_intent: Optional[Literal["stay", "local_move", "leave_scene", "travel_request"]] = None
    scene_focus: Optional[str] = None
    travel_destination: Optional[str] = None


class RuleAdjudicationOutput(BaseModel):
    action_type: str
    main_goal: str
    secondary_goals: list[str] = Field(default_factory=list)
    required_checks: list[RuleCheckOutput] = Field(default_factory=list)
    allowed_effects: list[str] = Field(default_factory=list)
    conditional_effects: list[str] = Field(default_factory=list)
    denied_effects: list[str] = Field(default_factory=list)
    bridge_action: RuleBridgeActionOutput
    reasoning_summary: str = ""
    source: str = "llm-rule-arbiter"


class TurnDirectorOutput(BaseModel):
    open_action: OpenActionOutput
    adjudication: RuleAdjudicationOutput
    scene: SceneOutput
    npc: NPCOutput
    event: EventOutput
    item: ItemOutput
    narration: AgenticNarrationOutput


class CreativeGMOutput(BaseModel):
    narration_text: str
    success_narration_text: Optional[str] = None
    failure_narration_text: Optional[str] = None
    intent_summary: str
    primary_goal: str
    method: str = ""
    targets: list[str] = Field(default_factory=list)
    player_assumptions: list[str] = Field(default_factory=list)
    requested_effects: list[str] = Field(default_factory=list)
    requires_check: bool = False
    risk_type: Optional[
        Literal["violence", "social", "stealth", "theft", "escape", "occult", "travel", "high_risk"]
    ] = None
    check_stat: Optional[Literal["strength", "agility", "intelligence", "faith"]] = None
    difficulty: Optional[int] = None
    target_profile: str = ""
    possible_blockers: list[str] = Field(default_factory=list)
    success_consequence: str = ""
    failure_consequence: str = ""
    location_intent: Optional[Literal["stay", "local_move", "leave_scene", "travel_request"]] = None
    scene_focus: Optional[str] = None
    travel_destination: Optional[str] = None
    scene_note: str = ""
    npc_notes: list[str] = Field(default_factory=list)
    event_notes: list[str] = Field(default_factory=list)
    item_notes: list[str] = Field(default_factory=list)
    denied_effects: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class AgenticProviders:
    memory_retriever: "MemoryRetrieverProvider"
    intent_agent: "IntentAgentProvider"
    scene_agent: "SceneAgentProvider"
    npc_agent: "NPCAgentProvider"
    event_agent: "EventAgentProvider"
    item_agent: "ItemAgentProvider"
    rule_arbiter: "RuleArbiterProvider"
    memory_curator: "MemoryCuratorProvider"
    narrator_agent: "NarratorAgentProvider"
    turn_director: Optional["TurnDirectorProvider"] = None
    world_bundle: Optional["WorldBundleProvider"] = None
    llm_enabled: bool = False
    model: Optional[str] = None
    reason: str = "Local agentic providers enabled."

    def to_dict(self):
        return {
            "memory_retriever": self.memory_retriever.provider_name,
            "intent_agent": self.intent_agent.provider_name,
            "scene_agent": self.scene_agent.provider_name,
            "npc_agent": self.npc_agent.provider_name,
            "event_agent": self.event_agent.provider_name,
            "item_agent": self.item_agent.provider_name,
            "rule_arbiter": self.rule_arbiter.provider_name,
            "memory_curator": self.memory_curator.provider_name,
            "narrator_agent": self.narrator_agent.provider_name,
            "turn_director": self.turn_director.provider_name if self.turn_director else None,
            "world_bundle": self.world_bundle.provider_name if self.world_bundle else None,
            "llm_enabled": self.llm_enabled,
            "model": self.model,
            "reason": self.reason,
        }


class MemoryRetrieverProvider:
    provider_name = "base-memory-retriever"

    def retrieve_memory(self, state, user_text):
        raise NotImplementedError


class IntentAgentProvider:
    provider_name = "base-intent-agent"

    def propose_open_action(self, user_text, state, memory_retrieval=None):
        raise NotImplementedError


class SceneAgentProvider:
    provider_name = "base-scene-agent"

    def propose_temporary_content(self, state, open_action, memory_retrieval=None):
        raise NotImplementedError


class NPCAgentProvider:
    provider_name = "base-npc-agent"

    def propose_npcs(self, state, open_action, memory_retrieval=None):
        raise NotImplementedError


class EventAgentProvider:
    provider_name = "base-event-agent"

    def propose_events(self, state, open_action, memory_retrieval=None, npcs=()):
        raise NotImplementedError


class ItemAgentProvider:
    provider_name = "base-item-agent"

    def propose_items(self, state, open_action, memory_retrieval=None):
        raise NotImplementedError


class RuleArbiterProvider:
    provider_name = "base-rule-arbiter"

    def propose_rule_adjudication(self, state, open_action):
        raise NotImplementedError


class MemoryCuratorProvider:
    provider_name = "base-memory-curator"

    def curate_memory(self, open_action, adjudication, commit):
        raise NotImplementedError


class NarratorAgentProvider:
    provider_name = "base-narrator-agent"

    def narrate_turn(
        self,
        state,
        memory_retrieval,
        open_action,
        temporary_content,
        adjudication,
        commit,
        memory_candidates=(),
        npc_proposals=(),
        event_proposals=(),
        item_proposals=(),
    ):
        raise NotImplementedError


class WorldBundleProvider:
    provider_name = "base-world-bundle"

    def propose_world_bundle(
        self,
        state,
        memory_retrieval,
        open_action,
        temporary_content,
        adjudication,
        commit,
        memory_candidates=(),
    ):
        raise NotImplementedError


class TurnDirectorProvider:
    provider_name = "base-turn-director"

    def propose_turn(self, state, user_text, memory_retrieval=None):
        raise NotImplementedError


class LocalMemoryRetrieverProvider(MemoryRetrieverProvider):
    provider_name = "local-memory-retriever"

    def retrieve_memory(self, state, user_text):
        return retrieve_memory(state, user_text)


class LocalIntentAgentProvider(IntentAgentProvider):
    provider_name = "local-intent-agent"

    def propose_open_action(self, user_text, state, memory_retrieval=None):
        return propose_open_action(user_text, state, memory_retrieval)


class OpenAIIntentAgentProvider(IntentAgentProvider):
    provider_name = "openai-intent-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_open_action(self, user_text, state, memory_retrieval=None):
        payload = {
            "user_text": user_text,
            "public_state": state.to_public_dict(),
            "memory_retrieval": memory_retrieval.to_dict() if memory_retrieval else {},
            "context_pack": build_context_pack(
                state,
                user_text=user_text,
                memory_retrieval=memory_retrieval,
            ),
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="open_action",
            payload=payload,
            output_model=OpenActionOutput,
        )
        data.setdefault("raw_text", user_text)
        data["source"] = self.provider_name
        try:
            return OpenActionProposal(**data)
        except TypeError as exc:
            raise OpenAIProviderError(f"OpenAI open action payload was invalid: {exc}") from exc


class LocalSceneAgentProvider(SceneAgentProvider):
    provider_name = "local-scene-agent"

    def propose_temporary_content(self, state, open_action, memory_retrieval=None):
        return (propose_temporary_scene(state, open_action, memory_retrieval),)


class LocalNPCAgentProvider(NPCAgentProvider):
    provider_name = "local-npc-agent"

    def propose_npcs(self, state, open_action, memory_retrieval=None):
        return propose_npcs(state, open_action, memory_retrieval)


class OpenAINPCAgentProvider(NPCAgentProvider):
    provider_name = "openai-npc-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_npcs(self, state, open_action, memory_retrieval=None):
        payload = {
            "public_state": state.to_public_dict(),
            "open_action": open_action.to_dict(),
            "memory_retrieval": memory_retrieval.to_dict() if memory_retrieval else {},
            "context_pack": build_context_pack(
                state,
                user_text=open_action.raw_text,
                memory_retrieval=memory_retrieval,
                open_action=open_action,
            ),
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="npc_agent",
            payload=payload,
            output_model=NPCOutput,
        )
        data["source"] = self.provider_name
        try:
            return (NPCProposal(**data),)
        except TypeError as exc:
            raise OpenAIProviderError(f"OpenAI NPC payload was invalid: {exc}") from exc


class LocalEventAgentProvider(EventAgentProvider):
    provider_name = "local-event-agent"

    def propose_events(self, state, open_action, memory_retrieval=None, npcs=()):
        return propose_events(state, open_action, memory_retrieval, npcs=npcs)


class OpenAIEventAgentProvider(EventAgentProvider):
    provider_name = "openai-event-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_events(self, state, open_action, memory_retrieval=None, npcs=()):
        payload = {
            "public_state": state.to_public_dict(),
            "open_action": open_action.to_dict(),
            "memory_retrieval": memory_retrieval.to_dict() if memory_retrieval else {},
            "npcs": [npc.to_dict() for npc in npcs],
            "context_pack": build_context_pack(
                state,
                user_text=open_action.raw_text,
                memory_retrieval=memory_retrieval,
                open_action=open_action,
            ),
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="event_agent",
            payload=payload,
            output_model=EventOutput,
        )
        data["source"] = self.provider_name
        try:
            return (EventProposal(**data),)
        except TypeError as exc:
            raise OpenAIProviderError(f"OpenAI event payload was invalid: {exc}") from exc


class LocalItemAgentProvider(ItemAgentProvider):
    provider_name = "local-item-agent"

    def propose_items(self, state, open_action, memory_retrieval=None):
        return propose_items(state, open_action, memory_retrieval)


class OpenAIItemAgentProvider(ItemAgentProvider):
    provider_name = "openai-item-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_items(self, state, open_action, memory_retrieval=None):
        payload = {
            "public_state": state.to_public_dict(),
            "open_action": open_action.to_dict(),
            "memory_retrieval": memory_retrieval.to_dict() if memory_retrieval else {},
            "context_pack": build_context_pack(
                state,
                user_text=open_action.raw_text,
                memory_retrieval=memory_retrieval,
                open_action=open_action,
            ),
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="item_agent",
            payload=payload,
            output_model=ItemOutput,
        )
        data["source"] = self.provider_name
        try:
            return (ItemProposal(**data),)
        except TypeError as exc:
            raise OpenAIProviderError(f"OpenAI item payload was invalid: {exc}") from exc


class LocalRuleArbiterProvider(RuleArbiterProvider):
    provider_name = "local-rule-arbiter"

    def propose_rule_adjudication(self, state, open_action):
        return propose_rule_adjudication(state, open_action)


class OpenAIRuleArbiterProvider(RuleArbiterProvider):
    provider_name = "openai-rule-arbiter-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_rule_adjudication(self, state, open_action):
        local_baseline = propose_rule_adjudication(state, open_action)
        payload = {
            "public_state": state.to_public_dict(),
            "open_action": open_action.to_dict(),
            "local_baseline": local_baseline.to_dict(),
            "context_pack": build_context_pack(
                state,
                user_text=open_action.raw_text,
                open_action=open_action,
            ),
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="rule_arbiter",
            payload=payload,
            output_model=RuleAdjudicationOutput,
        )
        data["source"] = self.provider_name
        try:
            data = normalize_rule_adjudication_payload(data, fallback=local_baseline)
            data["required_checks"] = tuple(
                RuleCheckProposal(**check) for check in data.get("required_checks", [])
            )
            return RuleAdjudicationProposal(**data)
        except TypeError as exc:
            raise OpenAIProviderError(f"OpenAI rule arbiter payload was invalid: {exc}") from exc


class LocalMemoryCuratorProvider(MemoryCuratorProvider):
    provider_name = "local-memory-curator"

    def curate_memory(self, open_action, adjudication, commit):
        return curate_memory(open_action, adjudication, commit)


class LocalNarratorAgentProvider(NarratorAgentProvider):
    provider_name = "local-narrator-agent"

    def narrate_turn(
        self,
        state,
        memory_retrieval,
        open_action,
        temporary_content,
        adjudication,
        commit,
        memory_candidates=(),
        npc_proposals=(),
        event_proposals=(),
        item_proposals=(),
    ):
        return narrate_turn(
            open_action,
            temporary_content,
            commit,
            memory_candidates,
            npc_proposals=npc_proposals,
            event_proposals=event_proposals,
            item_proposals=item_proposals,
        )


class OpenAINarratorAgentProvider(NarratorAgentProvider):
    provider_name = "openai-narrator-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def narrate_turn(
        self,
        state,
        memory_retrieval,
        open_action,
        temporary_content,
        adjudication,
        commit,
        memory_candidates=(),
        npc_proposals=(),
        event_proposals=(),
        item_proposals=(),
    ):
        payload = {
            "public_state": state.to_public_dict(),
            "memory_retrieval": memory_retrieval.to_dict() if memory_retrieval else {},
            "open_action": open_action.to_dict(),
            "temporary_content": [content.to_dict() for content in temporary_content],
            "npcs": [npc.to_dict() for npc in npc_proposals],
            "events": [event.to_dict() for event in event_proposals],
            "items": [item.to_dict() for item in item_proposals],
            "adjudication": adjudication.to_dict(),
            "commit": commit.to_dict(),
            "memory_candidates": [candidate.to_dict() for candidate in memory_candidates],
            "context_pack": build_context_pack(
                state,
                user_text=open_action.raw_text,
                memory_retrieval=memory_retrieval,
                open_action=open_action,
                temporary_content=temporary_content,
                adjudication=adjudication,
                commit=commit,
            ),
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="agentic_narrator",
            payload=payload,
            output_model=AgenticNarrationOutput,
        )
        data["source"] = self.provider_name
        try:
            return NarrationProposal(**data)
        except TypeError as exc:
            raise OpenAIProviderError(f"OpenAI agentic narration payload was invalid: {exc}") from exc


class OpenAIWorldBundleProvider(WorldBundleProvider):
    provider_name = "openai-world-bundle-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_world_bundle(
        self,
        state,
        memory_retrieval,
        open_action,
        temporary_content,
        adjudication,
        commit,
        memory_candidates=(),
    ):
        payload = {
            "public_state": state.to_public_dict(),
            "memory_retrieval": memory_retrieval.to_dict() if memory_retrieval else {},
            "open_action": open_action.to_dict(),
            "temporary_content": [content.to_dict() for content in temporary_content],
            "adjudication": adjudication.to_dict(),
            "commit": commit.to_dict(),
            "memory_candidates": [candidate.to_dict() for candidate in memory_candidates],
            "context_pack": build_context_pack(
                state,
                user_text=open_action.raw_text,
                memory_retrieval=memory_retrieval,
                open_action=open_action,
                temporary_content=temporary_content,
                adjudication=adjudication,
                commit=commit,
            ),
            "runtime_notes": load_runtime_notes(),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="world_bundle",
            payload=payload,
            output_model=WorldBundleOutput,
        )
        try:
            scene_payload = dict(data["scene"])
            npc_payload = dict(data["npc"])
            event_payload = dict(data["event"])
            item_payload = dict(data["item"])
            narration_payload = dict(data["narration"])
            scene_payload["source"] = "openai-world-bundle-scene"
            npc_payload["source"] = "openai-world-bundle-npc"
            event_payload["source"] = "openai-world-bundle-event"
            item_payload["source"] = "openai-world-bundle-item"
            narration_payload["source"] = "openai-world-bundle-narrator"
            return (
                (TemporaryContentProposal(**scene_payload),),
                (NPCProposal(**npc_payload),),
                (EventProposal(**event_payload),),
                (ItemProposal(**item_payload),),
                NarrationProposal(**narration_payload),
            )
        except (KeyError, TypeError) as exc:
            raise OpenAIProviderError(f"OpenAI world bundle payload was invalid: {exc}") from exc


class OpenAITurnDirectorProvider(TurnDirectorProvider):
    provider_name = "openai-turn-director-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_turn(self, state, user_text, memory_retrieval=None):
        local_open_action = propose_open_action(user_text, state, memory_retrieval)
        local_adjudication = propose_rule_adjudication(state, local_open_action)
        payload = {
            "user_text": user_text,
            "local_baseline": {
                "open_action": local_open_action.to_dict(),
                "adjudication": local_adjudication.to_dict(),
            },
            "context_pack": build_context_pack(
                state,
                user_text=user_text,
                memory_retrieval=memory_retrieval,
                open_action=local_open_action,
                adjudication=local_adjudication,
                lore_card_limit=3,
            ),
            "runtime_notes": load_runtime_notes(limit=1000),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="turn_director",
            payload=payload,
            output_model=TurnDirectorOutput,
        )
        try:
            open_action_payload = dict(data["open_action"])
            adjudication_payload = dict(data["adjudication"])
            scene_payload = dict(data["scene"])
            npc_payload = dict(data["npc"])
            event_payload = dict(data["event"])
            item_payload = dict(data["item"])
            narration_payload = dict(data["narration"])

            open_action_payload.setdefault("raw_text", user_text)
            open_action_payload["source"] = "openai-turn-director-intent"
            adjudication_payload["source"] = "openai-turn-director-rule-arbiter"
            scene_payload["source"] = "openai-turn-director-scene"
            npc_payload["source"] = "openai-turn-director-npc"
            event_payload["source"] = "openai-turn-director-event"
            item_payload["source"] = "openai-turn-director-item"
            narration_payload["source"] = "openai-turn-director-narrator"

            adjudication_payload = normalize_rule_adjudication_payload(
                adjudication_payload,
                fallback=local_adjudication,
            )
            adjudication_payload["required_checks"] = tuple(
                RuleCheckProposal(**check)
                for check in adjudication_payload.get("required_checks", [])
            )

            return TurnDirectorProposal(
                open_action=OpenActionProposal(**open_action_payload),
                adjudication=RuleAdjudicationProposal(**adjudication_payload),
                temporary_content=(TemporaryContentProposal(**scene_payload),),
                npcs=(NPCProposal(**npc_payload),),
                events=(EventProposal(**event_payload),),
                items=(ItemProposal(**item_payload),),
                narration=NarrationProposal(**narration_payload),
                source=self.provider_name,
            )
        except (KeyError, TypeError) as exc:
            raise OpenAIProviderError(f"OpenAI turn director payload was invalid: {exc}") from exc


class OpenAICreativeGMProvider(TurnDirectorProvider):
    provider_name = "openai-creative-gm-agent"

    def __init__(self, model=None, client=None, api_key=None):
        load_local_env()
        self.model = model or os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
        self.client = client
        self.api_key = api_key

    def propose_turn(self, state, user_text, memory_retrieval=None):
        local_open_action = propose_open_action(user_text, state, memory_retrieval)
        local_adjudication = propose_rule_adjudication(state, local_open_action)
        payload = {
            "user_text": user_text,
            "public_state": state.to_public_dict(),
            "local_baseline": {
                "open_action": local_open_action.to_dict(),
                "adjudication": local_adjudication.to_dict(),
            },
            "context_pack": build_context_pack(
                state,
                user_text=user_text,
                memory_retrieval=memory_retrieval,
                open_action=local_open_action,
                adjudication=local_adjudication,
                lore_card_limit=5,
            ),
            "runtime_notes": load_runtime_notes(limit=1600),
        }
        data = call_openai_structured(
            client=self.client,
            api_key=self.api_key,
            model=self.model,
            prompt_name="creative_gm",
            payload=payload,
            output_model=CreativeGMOutput,
        )
        try:
            return build_creative_gm_turn(
                data,
                user_text=user_text,
                local_open_action=local_open_action,
                local_adjudication=local_adjudication,
            )
        except (KeyError, TypeError) as exc:
            raise OpenAIProviderError(f"OpenAI creative GM payload was invalid: {exc}") from exc


def build_creative_gm_turn(data, user_text, local_open_action, local_adjudication):
    open_action = OpenActionProposal(
        raw_text=user_text,
        action_summary=data.get("intent_summary") or local_open_action.action_summary,
        primary_goal=data.get("primary_goal") or local_open_action.primary_goal,
        method=data.get("method") or local_open_action.method,
        targets=tuple(data.get("targets", []) or local_open_action.targets),
        player_assumptions=tuple(data.get("player_assumptions", [])),
        requested_effects=tuple(data.get("requested_effects", [])),
        confidence=0.85,
        source="openai-creative-gm-intent",
    )
    adjudication_payload = build_creative_gm_adjudication_payload(
        data,
        user_text,
        local_adjudication,
    )
    adjudication_payload = normalize_rule_adjudication_payload(
        adjudication_payload,
        fallback=local_adjudication,
    )
    adjudication_payload["required_checks"] = tuple(
        RuleCheckProposal(**check)
        for check in adjudication_payload.get("required_checks", [])
    )

    scene_note = data.get("scene_note") or "主持人根据当前地点、行动和记忆生成这一回合的自由场景。"
    temporary_content = (
        TemporaryContentProposal(
            content_type="creative_gm_scene",
            title="本回合场景",
            description=scene_note,
            authority_level="temporary",
            related_targets=tuple(data.get("targets", [])),
            source="openai-creative-gm-scene",
        ),
    )
    npcs = tuple(
        NPCProposal(
            name=split_sidecar_note(note, f"现场人物 {index}")[0],
            role="creative_gm_npc",
            description=split_sidecar_note(note, f"现场人物 {index}")[1],
            authority_level="temporary",
            source="openai-creative-gm-npc",
        )
        for index, note in enumerate(data.get("npc_notes", [])[:2], start=1)
        if note.strip()
    )
    events = tuple(
        EventProposal(
            event_type="creative_gm_event",
            summary=note,
            authority_level="temporary",
            source="openai-creative-gm-event",
        )
        for note in data.get("event_notes", [])[:2]
        if note.strip()
    )
    items = tuple(
        ItemProposal(
            name=split_sidecar_note(note, f"现场物件 {index}")[0],
            description=split_sidecar_note(note, f"现场物件 {index}")[1],
            authority_level="temporary",
            source="openai-creative-gm-item",
        )
        for index, note in enumerate(data.get("item_notes", [])[:2], start=1)
        if note.strip()
    )
    narration = NarrationProposal(
        text=data["narration_text"],
        claimed_effects=(),
        source="openai-creative-gm-narrator",
    )

    return TurnDirectorProposal(
        open_action=open_action,
        adjudication=RuleAdjudicationProposal(**adjudication_payload),
        temporary_content=temporary_content,
        npcs=npcs,
        events=events,
        items=items,
        narration=narration,
        success_narration=optional_creative_narration(
            data.get("success_narration_text"),
            "openai-creative-gm-success-narrator",
        ),
        failure_narration=optional_creative_narration(
            data.get("failure_narration_text"),
            "openai-creative-gm-failure-narrator",
        ),
        source="openai-creative-gm-agent",
    )


def split_sidecar_note(note, fallback_name):
    """Extract a readable label from compact LLM sidecar notes.

    The label is for internal structured proposals only. It must not force
    player-facing narration into numbered system-ish names.
    """
    clean_note = " ".join(str(note).strip().split())
    if not clean_note:
        return fallback_name, ""
    for separator in ("：", ":"):
        if separator in clean_note:
            raw_name, raw_description = clean_note.split(separator, 1)
            name = raw_name.strip(" ；;，,。")
            description = raw_description.strip()
            if name and len(name) <= 24 and description:
                return name, description
    return fallback_name, clean_note


def build_creative_gm_adjudication_payload(data, user_text, local_adjudication):
    requires_check = bool(data.get("requires_check"))
    risk_type = data.get("risk_type")
    check_stat = data.get("check_stat")
    difficulty = data.get("difficulty")
    allowed_effects = [
        "temporary_scene",
        "temporary_npc",
        "temporary_event",
        "temporary_item",
        "attempt_recorded",
    ]
    if requires_check:
        allowed_effects.extend(("world_check", "suspicion_change"))

    denied_effects = list(
        dict.fromkeys(
            [
                "unearned_reward",
                "unearned_secret",
                "unearned_clue",
                "unconfirmed_death",
                "unconfirmed_permanent_injury",
                *(data.get("denied_effects") or []),
            ]
        )
    )
    checks = []
    if requires_check and check_stat and difficulty is not None:
        checks.append(
            {
                "check_type": risk_type or "high_risk",
                "stat": check_stat,
                "dc": difficulty,
                "reason": data.get("failure_consequence")
                or data.get("success_consequence")
                or "Creative GM marked this action as risky.",
            }
        )

    return {
        "action_type": "world_action",
        "main_goal": data.get("primary_goal") or local_adjudication.main_goal,
        "secondary_goals": [],
        "required_checks": checks,
        "allowed_effects": allowed_effects,
        "conditional_effects": [],
        "denied_effects": denied_effects,
        "bridge_action": {
            "intent": "world_action",
            "target": first_present(*(data.get("targets") or [])),
            "item": None,
            "requires_check": requires_check,
            "check_stat": check_stat,
            "difficulty": difficulty,
            "risk_type": risk_type,
            "target_profile": data.get("target_profile", ""),
            "possible_blockers": data.get("possible_blockers", []),
            "success_consequence": data.get("success_consequence", ""),
            "failure_consequence": data.get("failure_consequence", ""),
            "raw_text": user_text,
            "open_method": data.get("method", ""),
            "open_primary_goal": data.get("primary_goal", ""),
            "open_requested_effects": data.get("requested_effects", []),
            "player_assumptions": data.get("player_assumptions", []),
            "location_intent": data.get("location_intent"),
            "scene_focus": data.get("scene_focus"),
            "travel_destination": data.get("travel_destination"),
        },
        "reasoning_summary": "Creative GM sidecar adjudication.",
        "source": "openai-creative-gm-rule-arbiter",
    }


def optional_creative_narration(text, source):
    if not text or not text.strip():
        return None
    return NarrationProposal(text=text, claimed_effects=(), source=source)


def normalize_rule_adjudication_payload(payload, fallback=None):
    payload = dict(payload)
    bridge = dict(payload.get("bridge_action") or {})
    checks = [dict(check) for check in payload.get("required_checks", [])]
    fallback_bridge = dict(getattr(fallback, "bridge_action", {}) or {})
    fallback_checks = tuple(getattr(fallback, "required_checks", ()) or ())
    fallback_check = fallback_checks[0] if fallback_checks else None

    if bridge.get("requires_check"):
        if not bridge.get("risk_type"):
            bridge["risk_type"] = normalize_world_risk_type(
                first_present(
                    first_check_value(checks, "check_type"),
                    getattr(fallback_check, "check_type", None),
                    fallback_bridge.get("risk_type"),
                )
            )
        if not bridge.get("check_stat"):
            bridge["check_stat"] = first_present(
                first_check_value(checks, "stat"),
                getattr(fallback_check, "stat", None),
                fallback_bridge.get("check_stat"),
            )
        if bridge.get("difficulty") is None:
            bridge["difficulty"] = first_present(
                first_check_value(checks, "dc"),
                getattr(fallback_check, "dc", None),
                fallback_bridge.get("difficulty"),
            )
        if not checks and bridge.get("check_stat") and bridge.get("difficulty") is not None:
            checks.append(
                {
                    "check_type": bridge["risk_type"],
                    "stat": bridge["check_stat"],
                    "dc": bridge["difficulty"],
                    "reason": bridge.get("failure_consequence")
                    or bridge.get("success_consequence")
                    or "LLM proposed a risky action but omitted the explicit check entry.",
                }
            )

    payload["bridge_action"] = bridge
    payload["required_checks"] = checks
    return payload


def normalize_world_risk_type(value):
    if value in WORLD_RISK_TYPES:
        return value
    return "high_risk"


def first_check_value(checks, key):
    if not checks:
        return None
    return checks[0].get(key)


def first_present(*values):
    for value in values:
        if value is not None and value != "":
            return value
    return None


def build_agentic_providers_from_env():
    load_local_env()
    local_providers = build_local_agentic_providers()
    if not is_agentic_llm_enabled():
        return local_providers

    if not os.getenv("OPENAI_API_KEY"):
        return AgenticProviders(
            **base_provider_kwargs(local_providers),
            llm_enabled=False,
            model=None,
            reason="OPENAI_API_KEY is missing; using local Agentic Runtime providers.",
        )

    model = os.getenv(OPENAI_MODEL_ENV_VAR, DEFAULT_OPENAI_MODEL)
    full_llm = is_agentic_full_llm_enabled()
    creative_gm = is_creative_gm_enabled()
    use_turn_director = is_agentic_turn_director_enabled()
    if creative_gm and not full_llm:
        return AgenticProviders(
            memory_retriever=local_providers.memory_retriever,
            intent_agent=local_providers.intent_agent,
            scene_agent=local_providers.scene_agent,
            npc_agent=local_providers.npc_agent,
            event_agent=local_providers.event_agent,
            item_agent=local_providers.item_agent,
            rule_arbiter=local_providers.rule_arbiter,
            memory_curator=local_providers.memory_curator,
            narrator_agent=local_providers.narrator_agent,
            turn_director=OpenAICreativeGMProvider(model=model),
            world_bundle=None,
            llm_enabled=True,
            model=model,
            reason=agentic_llm_reason(full_llm, use_turn_director, creative_gm),
        )

    if use_turn_director and not full_llm:
        return AgenticProviders(
            memory_retriever=local_providers.memory_retriever,
            intent_agent=local_providers.intent_agent,
            scene_agent=local_providers.scene_agent,
            npc_agent=local_providers.npc_agent,
            event_agent=local_providers.event_agent,
            item_agent=local_providers.item_agent,
            rule_arbiter=local_providers.rule_arbiter,
            memory_curator=local_providers.memory_curator,
            narrator_agent=local_providers.narrator_agent,
            turn_director=OpenAITurnDirectorProvider(model=model),
            world_bundle=None,
            llm_enabled=True,
            model=model,
            reason=agentic_llm_reason(full_llm, use_turn_director),
        )

    return AgenticProviders(
        memory_retriever=local_providers.memory_retriever,
        intent_agent=OpenAIIntentAgentProvider(model=model),
        scene_agent=local_providers.scene_agent,
        npc_agent=OpenAINPCAgentProvider(model=model) if full_llm else local_providers.npc_agent,
        event_agent=OpenAIEventAgentProvider(model=model) if full_llm else local_providers.event_agent,
        item_agent=OpenAIItemAgentProvider(model=model) if full_llm else local_providers.item_agent,
        rule_arbiter=OpenAIRuleArbiterProvider(model=model),
        memory_curator=local_providers.memory_curator,
        narrator_agent=OpenAINarratorAgentProvider(model=model),
        turn_director=None,
        world_bundle=None if full_llm else OpenAIWorldBundleProvider(model=model),
        llm_enabled=True,
        model=model,
        reason=agentic_llm_reason(full_llm, use_turn_director),
    )


def build_local_agentic_providers():
    return AgenticProviders(
        memory_retriever=LocalMemoryRetrieverProvider(),
        intent_agent=LocalIntentAgentProvider(),
        scene_agent=LocalSceneAgentProvider(),
        npc_agent=LocalNPCAgentProvider(),
        event_agent=LocalEventAgentProvider(),
        item_agent=LocalItemAgentProvider(),
        rule_arbiter=LocalRuleArbiterProvider(),
        memory_curator=LocalMemoryCuratorProvider(),
        narrator_agent=LocalNarratorAgentProvider(),
        turn_director=None,
        world_bundle=None,
        llm_enabled=False,
        model=None,
        reason="Local Agentic Runtime providers enabled.",
    )


def base_provider_kwargs(providers):
    return {
        "memory_retriever": providers.memory_retriever,
        "intent_agent": providers.intent_agent,
        "scene_agent": providers.scene_agent,
        "npc_agent": providers.npc_agent,
        "event_agent": providers.event_agent,
        "item_agent": providers.item_agent,
        "rule_arbiter": providers.rule_arbiter,
        "memory_curator": providers.memory_curator,
        "narrator_agent": providers.narrator_agent,
        "turn_director": providers.turn_director,
        "world_bundle": providers.world_bundle,
    }


def is_agentic_llm_enabled():
    load_local_env()
    return os.getenv(AGENTIC_LLM_ENABLED_ENV_VAR, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def is_agentic_full_llm_enabled():
    load_local_env()
    return os.getenv(AGENTIC_FULL_LLM_ENABLED_ENV_VAR, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def is_agentic_turn_director_enabled():
    load_local_env()
    raw_value = os.getenv(AGENTIC_TURN_DIRECTOR_ENV_VAR, "1").strip().lower()
    return raw_value not in {"0", "false", "no", "off"}


def is_creative_gm_enabled():
    load_local_env()
    raw_value = os.getenv(CREATIVE_GM_ENABLED_ENV_VAR, "0").strip().lower()
    return raw_value in {"1", "true", "yes", "on"}


def agentic_llm_reason(full_llm, use_turn_director=False, creative_gm=False):
    if creative_gm and not full_llm:
        return (
            "OpenAI Creative GM mode enabled: one LLM call owns the player-facing "
            "imagination while local memory, validation, dice, and state commit stay authoritative."
        )
    if use_turn_director and not full_llm:
        return (
            "OpenAI Turn Director agent enabled for low-latency live play; "
            "memory, validation, state commit, and fallback providers stay local."
        )
    if full_llm:
        return (
            "OpenAI Intent/RuleArbiter/NPC/Event/Item/Narrator agents enabled; "
            "memory and commit use local providers."
        )
    return (
        "OpenAI Intent, Rule Arbiter, and World Bundle agents enabled; "
        "memory and commit use local providers."
    )
