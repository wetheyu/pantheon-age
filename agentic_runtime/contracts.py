"""Structured contracts for the Phase 5 Agentic Runtime."""

from dataclasses import dataclass, field
from typing import Optional


AUTHORITY_LEVELS = ("flavor", "temporary", "persistent", "mechanical", "secret")
MEMORY_TYPES = (
    "player_memory",
    "npc_memory",
    "location_memory",
    "faction_memory",
    "quest_memory",
    "world_event_memory",
    "temporary_scene_memory",
    "secret_memory",
)
VISIBILITY_LEVELS = ("player_known", "npc_known", "system_secret")
MEMORY_BUCKETS = ("player_known", "npc_known", "location", "quest", "faction", "secret")
GENERATED_FACT_TYPES = (
    "npc",
    "location",
    "rumor",
    "event",
    "organization",
    "relationship",
    "item",
    "secret",
)


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        object.__setattr__(self, "errors", tuple(self.errors))

    def to_dict(self):
        return {
            "is_valid": self.is_valid,
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class MemoryRetrievalResult:
    player_known: tuple[str, ...] = field(default_factory=tuple)
    location_context: tuple[str, ...] = field(default_factory=tuple)
    recent_events: tuple[str, ...] = field(default_factory=tuple)
    hidden_context: tuple[str, ...] = field(default_factory=tuple)
    source: str = "local-memory"

    def __post_init__(self):
        object.__setattr__(self, "player_known", tuple(self.player_known))
        object.__setattr__(self, "location_context", tuple(self.location_context))
        object.__setattr__(self, "recent_events", tuple(self.recent_events))
        object.__setattr__(self, "hidden_context", tuple(self.hidden_context))

    def to_dict(self, include_hidden=False):
        payload = {
            "player_known": list(self.player_known),
            "location_context": list(self.location_context),
            "recent_events": list(self.recent_events),
            "source": self.source,
        }
        if include_hidden:
            payload["hidden_context"] = list(self.hidden_context)
        return payload


@dataclass(frozen=True)
class OpenActionProposal:
    raw_text: str
    action_summary: str
    primary_goal: str
    secondary_goals: tuple[str, ...] = field(default_factory=tuple)
    method: str = ""
    targets: tuple[str, ...] = field(default_factory=tuple)
    player_assumptions: tuple[str, ...] = field(default_factory=tuple)
    requested_effects: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 1.0
    source: str = "local-intent-agent"

    def __post_init__(self):
        object.__setattr__(self, "secondary_goals", tuple(self.secondary_goals))
        object.__setattr__(self, "targets", tuple(self.targets))
        object.__setattr__(self, "player_assumptions", tuple(self.player_assumptions))
        object.__setattr__(self, "requested_effects", tuple(self.requested_effects))

    def to_dict(self):
        return {
            "raw_text": self.raw_text,
            "action_summary": self.action_summary,
            "primary_goal": self.primary_goal,
            "secondary_goals": list(self.secondary_goals),
            "method": self.method,
            "targets": list(self.targets),
            "player_assumptions": list(self.player_assumptions),
            "requested_effects": list(self.requested_effects),
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass(frozen=True)
class TemporaryContentProposal:
    content_type: str
    title: str
    description: str
    authority_level: str = "temporary"
    related_targets: tuple[str, ...] = field(default_factory=tuple)
    claimed_state_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_new_clues: tuple[str, ...] = field(default_factory=tuple)
    source: str = "local-scene-agent"

    def __post_init__(self):
        object.__setattr__(self, "related_targets", tuple(self.related_targets))
        object.__setattr__(self, "claimed_state_changes", tuple(self.claimed_state_changes))
        object.__setattr__(self, "claimed_new_clues", tuple(self.claimed_new_clues))

    def to_dict(self):
        return {
            "content_type": self.content_type,
            "title": self.title,
            "description": self.description,
            "authority_level": self.authority_level,
            "related_targets": list(self.related_targets),
            "claimed_state_changes": list(self.claimed_state_changes),
            "claimed_new_clues": list(self.claimed_new_clues),
            "source": self.source,
        }


@dataclass(frozen=True)
class NPCProposal:
    name: str
    role: str
    description: str
    visible_knowledge: tuple[str, ...] = field(default_factory=tuple)
    attitude: str = "neutral"
    short_term_goal: str = ""
    authority_level: str = "temporary"
    claimed_facts: tuple[str, ...] = field(default_factory=tuple)
    claimed_state_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_new_clues: tuple[str, ...] = field(default_factory=tuple)
    source: str = "local-npc-agent"

    def __post_init__(self):
        object.__setattr__(self, "visible_knowledge", tuple(self.visible_knowledge))
        object.__setattr__(self, "claimed_facts", tuple(self.claimed_facts))
        object.__setattr__(self, "claimed_state_changes", tuple(self.claimed_state_changes))
        object.__setattr__(self, "claimed_new_clues", tuple(self.claimed_new_clues))

    def to_dict(self):
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "visible_knowledge": list(self.visible_knowledge),
            "attitude": self.attitude,
            "short_term_goal": self.short_term_goal,
            "authority_level": self.authority_level,
            "claimed_facts": list(self.claimed_facts),
            "claimed_state_changes": list(self.claimed_state_changes),
            "claimed_new_clues": list(self.claimed_new_clues),
            "source": self.source,
        }


@dataclass(frozen=True)
class EventProposal:
    event_type: str
    summary: str
    hooks: tuple[str, ...] = field(default_factory=tuple)
    involved_npcs: tuple[str, ...] = field(default_factory=tuple)
    authority_level: str = "temporary"
    claimed_facts: tuple[str, ...] = field(default_factory=tuple)
    claimed_state_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_new_clues: tuple[str, ...] = field(default_factory=tuple)
    source: str = "local-event-agent"

    def __post_init__(self):
        object.__setattr__(self, "hooks", tuple(self.hooks))
        object.__setattr__(self, "involved_npcs", tuple(self.involved_npcs))
        object.__setattr__(self, "claimed_facts", tuple(self.claimed_facts))
        object.__setattr__(self, "claimed_state_changes", tuple(self.claimed_state_changes))
        object.__setattr__(self, "claimed_new_clues", tuple(self.claimed_new_clues))

    def to_dict(self):
        return {
            "event_type": self.event_type,
            "summary": self.summary,
            "hooks": list(self.hooks),
            "involved_npcs": list(self.involved_npcs),
            "authority_level": self.authority_level,
            "claimed_facts": list(self.claimed_facts),
            "claimed_state_changes": list(self.claimed_state_changes),
            "claimed_new_clues": list(self.claimed_new_clues),
            "source": self.source,
        }


@dataclass(frozen=True)
class ItemProposal:
    name: str
    description: str
    possible_uses: tuple[str, ...] = field(default_factory=tuple)
    risk_tags: tuple[str, ...] = field(default_factory=tuple)
    authority_level: str = "temporary"
    claimed_inventory_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_state_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_new_clues: tuple[str, ...] = field(default_factory=tuple)
    source: str = "local-item-agent"

    def __post_init__(self):
        object.__setattr__(self, "possible_uses", tuple(self.possible_uses))
        object.__setattr__(self, "risk_tags", tuple(self.risk_tags))
        object.__setattr__(self, "claimed_inventory_changes", tuple(self.claimed_inventory_changes))
        object.__setattr__(self, "claimed_state_changes", tuple(self.claimed_state_changes))
        object.__setattr__(self, "claimed_new_clues", tuple(self.claimed_new_clues))

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "possible_uses": list(self.possible_uses),
            "risk_tags": list(self.risk_tags),
            "authority_level": self.authority_level,
            "claimed_inventory_changes": list(self.claimed_inventory_changes),
            "claimed_state_changes": list(self.claimed_state_changes),
            "claimed_new_clues": list(self.claimed_new_clues),
            "source": self.source,
        }


@dataclass(frozen=True)
class RuleCheckProposal:
    check_type: str
    stat: Optional[str] = None
    dc: Optional[int] = None
    reason: str = ""

    def to_dict(self):
        return {
            "check_type": self.check_type,
            "stat": self.stat,
            "dc": self.dc,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class RuleAdjudicationProposal:
    action_type: str
    main_goal: str
    secondary_goals: tuple[str, ...] = field(default_factory=tuple)
    required_checks: tuple[RuleCheckProposal, ...] = field(default_factory=tuple)
    allowed_effects: tuple[str, ...] = field(default_factory=tuple)
    conditional_effects: tuple[str, ...] = field(default_factory=tuple)
    denied_effects: tuple[str, ...] = field(default_factory=tuple)
    bridge_action: dict = field(default_factory=dict)
    reasoning_summary: str = ""
    source: str = "local-rule-arbiter"

    def __post_init__(self):
        object.__setattr__(self, "secondary_goals", tuple(self.secondary_goals))
        object.__setattr__(self, "required_checks", tuple(self.required_checks))
        object.__setattr__(self, "allowed_effects", tuple(self.allowed_effects))
        object.__setattr__(self, "conditional_effects", tuple(self.conditional_effects))
        object.__setattr__(self, "denied_effects", tuple(self.denied_effects))

    def to_dict(self):
        return {
            "action_type": self.action_type,
            "main_goal": self.main_goal,
            "secondary_goals": list(self.secondary_goals),
            "required_checks": [check.to_dict() for check in self.required_checks],
            "allowed_effects": list(self.allowed_effects),
            "conditional_effects": list(self.conditional_effects),
            "denied_effects": list(self.denied_effects),
            "bridge_action": self.bridge_action,
            "reasoning_summary": self.reasoning_summary,
            "source": self.source,
        }


@dataclass(frozen=True)
class StateCommitProposal:
    committed: bool
    rule_action: dict
    rule_result: dict
    committed_effects: tuple[str, ...] = field(default_factory=tuple)
    rejected_effects: tuple[str, ...] = field(default_factory=tuple)
    source: str = "state-commit-layer"

    def __post_init__(self):
        object.__setattr__(self, "committed_effects", tuple(self.committed_effects))
        object.__setattr__(self, "rejected_effects", tuple(self.rejected_effects))

    def to_dict(self):
        return {
            "committed": self.committed,
            "rule_action": self.rule_action,
            "rule_result": self.rule_result,
            "committed_effects": list(self.committed_effects),
            "rejected_effects": list(self.rejected_effects),
            "source": self.source,
        }


@dataclass(frozen=True)
class MemoryCandidate:
    memory_type: str
    subject: str
    content: str
    authority_level: str = "temporary"
    visibility: str = "player_known"
    should_persist: bool = False
    source_event: str = ""
    confidence: float = 1.0
    source: str = "local-memory-curator"

    def to_dict(self):
        return {
            "memory_type": self.memory_type,
            "subject": self.subject,
            "content": self.content,
            "authority_level": self.authority_level,
            "visibility": self.visibility,
            "should_persist": self.should_persist,
            "source_event": self.source_event,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass(frozen=True)
class GeneratedFactProposal:
    fact_type: str
    subject: str
    content: str
    authority_level: str = "persistent"
    visibility: str = "player_known"
    evidence: tuple[str, ...] = field(default_factory=tuple)
    source_event: str = ""
    confidence: float = 1.0
    source: str = "generated-fact-commit"

    def __post_init__(self):
        object.__setattr__(self, "evidence", tuple(self.evidence))

    def to_dict(self):
        return {
            "fact_type": self.fact_type,
            "subject": self.subject,
            "content": self.content,
            "authority_level": self.authority_level,
            "visibility": self.visibility,
            "evidence": list(self.evidence),
            "source_event": self.source_event,
            "confidence": self.confidence,
            "source": self.source,
        }


@dataclass(frozen=True)
class MemoryRecord:
    record_id: str
    bucket: str
    memory_type: str
    subject: str
    content: str
    authority_level: str
    visibility: str
    source_event: str = ""
    confidence: float = 1.0
    source: str = "memory-store"

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "bucket": self.bucket,
            "memory_type": self.memory_type,
            "subject": self.subject,
            "content": self.content,
            "authority_level": self.authority_level,
            "visibility": self.visibility,
            "source_event": self.source_event,
            "confidence": self.confidence,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            record_id=data["record_id"],
            bucket=data["bucket"],
            memory_type=data["memory_type"],
            subject=data["subject"],
            content=data["content"],
            authority_level=data["authority_level"],
            visibility=data["visibility"],
            source_event=data.get("source_event", ""),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "memory-store"),
        )


@dataclass(frozen=True)
class NarrationProposal:
    text: str
    claimed_effects: tuple[str, ...] = field(default_factory=tuple)
    source: str = "local-narrator-agent"

    def __post_init__(self):
        object.__setattr__(self, "claimed_effects", tuple(self.claimed_effects))

    def to_dict(self):
        return {
            "text": self.text,
            "claimed_effects": list(self.claimed_effects),
            "source": self.source,
        }


@dataclass(frozen=True)
class TurnDirectorProposal:
    open_action: OpenActionProposal
    adjudication: RuleAdjudicationProposal
    temporary_content: tuple[TemporaryContentProposal, ...]
    npcs: tuple[NPCProposal, ...]
    events: tuple[EventProposal, ...]
    items: tuple[ItemProposal, ...]
    narration: NarrationProposal
    success_narration: Optional[NarrationProposal] = None
    failure_narration: Optional[NarrationProposal] = None
    source: str = "openai-turn-director-agent"

    def __post_init__(self):
        object.__setattr__(self, "temporary_content", tuple(self.temporary_content))
        object.__setattr__(self, "npcs", tuple(self.npcs))
        object.__setattr__(self, "events", tuple(self.events))
        object.__setattr__(self, "items", tuple(self.items))

    def narration_for_commit(self, commit):
        roll = commit.rule_result.get("roll")
        if not roll:
            return self.narration
        if commit.rule_result.get("success") and self.success_narration:
            return self.success_narration
        if not commit.rule_result.get("success") and self.failure_narration:
            return self.failure_narration
        return self.narration

    def to_dict(self):
        return {
            "open_action": self.open_action.to_dict(),
            "adjudication": self.adjudication.to_dict(),
            "temporary_content": [content.to_dict() for content in self.temporary_content],
            "npcs": [npc.to_dict() for npc in self.npcs],
            "events": [event.to_dict() for event in self.events],
            "items": [item.to_dict() for item in self.items],
            "narration": self.narration.to_dict(),
            "success_narration": (
                self.success_narration.to_dict() if self.success_narration else None
            ),
            "failure_narration": (
                self.failure_narration.to_dict() if self.failure_narration else None
            ),
            "source": self.source,
        }


@dataclass(frozen=True)
class AgenticTurnResult:
    providers: dict
    errors: tuple[str, ...]
    memory_retrieval: MemoryRetrievalResult
    open_action: OpenActionProposal
    temporary_content: tuple[TemporaryContentProposal, ...]
    npcs: tuple[NPCProposal, ...]
    events: tuple[EventProposal, ...]
    items: tuple[ItemProposal, ...]
    adjudication: RuleAdjudicationProposal
    validations: dict
    commit: StateCommitProposal
    memory_candidates: tuple[MemoryCandidate, ...]
    memory_records: tuple[MemoryRecord, ...]
    narration: NarrationProposal

    def __post_init__(self):
        object.__setattr__(self, "errors", tuple(self.errors))
        object.__setattr__(self, "temporary_content", tuple(self.temporary_content))
        object.__setattr__(self, "npcs", tuple(self.npcs))
        object.__setattr__(self, "events", tuple(self.events))
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "memory_candidates", tuple(self.memory_candidates))
        object.__setattr__(self, "memory_records", tuple(self.memory_records))

    def to_dict(self):
        return {
            "providers": self.providers,
            "errors": list(self.errors),
            "memory_retrieval": self.memory_retrieval.to_dict(),
            "open_action": self.open_action.to_dict(),
            "temporary_content": [content.to_dict() for content in self.temporary_content],
            "npcs": [npc.to_dict() for npc in self.npcs],
            "events": [event.to_dict() for event in self.events],
            "items": [item.to_dict() for item in self.items],
            "adjudication": self.adjudication.to_dict(),
            "validations": {
                key: value.to_dict() for key, value in self.validations.items()
            },
            "commit": self.commit.to_dict(),
            "memory_candidates": [candidate.to_dict() for candidate in self.memory_candidates],
            "memory_records": [record.to_dict() for record in self.memory_records],
            "narration": self.narration.to_dict(),
        }
