"""Structured contracts for LLM runtime proposals."""

from dataclasses import dataclass, field
from typing import Optional


AUTHORITY_LEVELS = ("flavor", "temporary", "persistent", "mechanical", "secret")
GENERATED_CONTENT_TYPES = (
    "location",
    "npc",
    "item",
    "relationship",
    "team",
    "organization",
    "event",
    "rumor",
    "route",
    "quest_hook",
    "object",
    "scene_detail",
)


@dataclass(frozen=True)
class NarrationProposal:
    """A candidate narration that may come from an LLM later."""

    text: str
    claimed_state_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_new_clues: tuple[str, ...] = field(default_factory=tuple)
    claimed_location_after: Optional[str] = None
    source: str = "template"

    def __post_init__(self):
        object.__setattr__(self, "claimed_state_changes", tuple(self.claimed_state_changes))
        object.__setattr__(self, "claimed_new_clues", tuple(self.claimed_new_clues))

    def to_dict(self):
        return {
            "text": self.text,
            "claimed_state_changes": list(self.claimed_state_changes),
            "claimed_new_clues": list(self.claimed_new_clues),
            "claimed_location_after": self.claimed_location_after,
            "source": self.source,
        }


@dataclass(frozen=True)
class SceneProposal:
    """A candidate local scene proposed by an LLM or local provider."""

    title: str
    description: str
    location: Optional[str] = None
    sensory_details: tuple[str, ...] = field(default_factory=tuple)
    npcs: tuple[str, ...] = field(default_factory=tuple)
    interactable_objects: tuple[str, ...] = field(default_factory=tuple)
    authority_level: str = "temporary"
    claimed_facts: tuple[str, ...] = field(default_factory=tuple)
    claimed_state_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_new_clues: tuple[str, ...] = field(default_factory=tuple)
    claimed_location_after: Optional[str] = None
    source: str = "template"

    def __post_init__(self):
        object.__setattr__(self, "sensory_details", tuple(self.sensory_details))
        object.__setattr__(self, "npcs", tuple(self.npcs))
        object.__setattr__(self, "interactable_objects", tuple(self.interactable_objects))
        object.__setattr__(self, "claimed_facts", tuple(self.claimed_facts))
        object.__setattr__(self, "claimed_state_changes", tuple(self.claimed_state_changes))
        object.__setattr__(self, "claimed_new_clues", tuple(self.claimed_new_clues))

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "sensory_details": list(self.sensory_details),
            "npcs": list(self.npcs),
            "interactable_objects": list(self.interactable_objects),
            "authority_level": self.authority_level,
            "claimed_facts": list(self.claimed_facts),
            "claimed_state_changes": list(self.claimed_state_changes),
            "claimed_new_clues": list(self.claimed_new_clues),
            "claimed_location_after": self.claimed_location_after,
            "source": self.source,
        }


@dataclass(frozen=True)
class EventProposal:
    """A candidate local event proposed by an LLM or local provider."""

    event_type: str
    summary: str
    location: Optional[str] = None
    hooks: tuple[str, ...] = field(default_factory=tuple)
    involved_npcs: tuple[str, ...] = field(default_factory=tuple)
    authority_level: str = "temporary"
    claimed_facts: tuple[str, ...] = field(default_factory=tuple)
    claimed_state_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_new_clues: tuple[str, ...] = field(default_factory=tuple)
    claimed_location_after: Optional[str] = None
    source: str = "template"

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
            "location": self.location,
            "hooks": list(self.hooks),
            "involved_npcs": list(self.involved_npcs),
            "authority_level": self.authority_level,
            "claimed_facts": list(self.claimed_facts),
            "claimed_state_changes": list(self.claimed_state_changes),
            "claimed_new_clues": list(self.claimed_new_clues),
            "claimed_location_after": self.claimed_location_after,
            "source": self.source,
        }


@dataclass(frozen=True)
class GeneratedContentProposal:
    """A general proposal for open-ended LLM-generated content."""

    content_type: str
    name: str
    description: str
    authority_level: str = "temporary"
    tags: tuple[str, ...] = field(default_factory=tuple)
    related_entities: tuple[str, ...] = field(default_factory=tuple)
    temporary_relationships: tuple[str, ...] = field(default_factory=tuple)
    claimed_facts: tuple[str, ...] = field(default_factory=tuple)
    claimed_state_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_new_clues: tuple[str, ...] = field(default_factory=tuple)
    claimed_inventory_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_relationship_changes: tuple[str, ...] = field(default_factory=tuple)
    claimed_faction_changes: tuple[str, ...] = field(default_factory=tuple)
    source: str = "template"

    def __post_init__(self):
        object.__setattr__(self, "tags", tuple(self.tags))
        object.__setattr__(self, "related_entities", tuple(self.related_entities))
        object.__setattr__(self, "temporary_relationships", tuple(self.temporary_relationships))
        object.__setattr__(self, "claimed_facts", tuple(self.claimed_facts))
        object.__setattr__(self, "claimed_state_changes", tuple(self.claimed_state_changes))
        object.__setattr__(self, "claimed_new_clues", tuple(self.claimed_new_clues))
        object.__setattr__(self, "claimed_inventory_changes", tuple(self.claimed_inventory_changes))
        object.__setattr__(self, "claimed_relationship_changes", tuple(self.claimed_relationship_changes))
        object.__setattr__(self, "claimed_faction_changes", tuple(self.claimed_faction_changes))

    def to_dict(self):
        return {
            "content_type": self.content_type,
            "name": self.name,
            "description": self.description,
            "authority_level": self.authority_level,
            "tags": list(self.tags),
            "related_entities": list(self.related_entities),
            "temporary_relationships": list(self.temporary_relationships),
            "claimed_facts": list(self.claimed_facts),
            "claimed_state_changes": list(self.claimed_state_changes),
            "claimed_new_clues": list(self.claimed_new_clues),
            "claimed_inventory_changes": list(self.claimed_inventory_changes),
            "claimed_relationship_changes": list(self.claimed_relationship_changes),
            "claimed_faction_changes": list(self.claimed_faction_changes),
            "source": self.source,
        }


@dataclass(frozen=True)
class ProposalValidation:
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
class ActionCandidate:
    """A candidate structured action proposed from player text."""

    intent: str
    target: Optional[str] = None
    item: Optional[str] = None
    method: str = ""
    desired_outcome: str = ""
    risk_tags: tuple[str, ...] = field(default_factory=tuple)
    skill_tags: tuple[str, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    confidence: float = 1.0
    raw_text: str = ""
    source: str = "keyword"

    def __post_init__(self):
        object.__setattr__(self, "risk_tags", tuple(self.risk_tags))
        object.__setattr__(self, "skill_tags", tuple(self.skill_tags))
        object.__setattr__(self, "assumptions", tuple(self.assumptions))

    def to_dict(self):
        return {
            "intent": self.intent,
            "target": self.target,
            "item": self.item,
            "method": self.method,
            "desired_outcome": self.desired_outcome,
            "risk_tags": list(self.risk_tags),
            "skill_tags": list(self.skill_tags),
            "assumptions": list(self.assumptions),
            "confidence": self.confidence,
            "raw_text": self.raw_text,
            "source": self.source,
        }


@dataclass(frozen=True)
class ActionCandidateValidation:
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
class ActionCandidateResult:
    action: dict
    candidate: ActionCandidate
    validation: ActionCandidateValidation
    used_fallback: bool = False

    def to_dict(self):
        return {
            "action": self.action,
            "candidate": self.candidate.to_dict(),
            "validation": self.validation.to_dict(),
            "used_fallback": self.used_fallback,
        }


@dataclass(frozen=True)
class AdjudicationRequest:
    """A generic request for deterministic rule adjudication."""

    intent: str
    check_type: str
    requires_check: bool
    primary_stat: Optional[str] = None
    difficulty: Optional[int] = None
    target: Optional[str] = None
    item: Optional[str] = None
    method: str = ""
    desired_outcome: str = ""
    risk_tags: tuple[str, ...] = field(default_factory=tuple)
    skill_tags: tuple[str, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    possible_costs: tuple[str, ...] = field(default_factory=tuple)
    source: str = "candidate"

    def __post_init__(self):
        object.__setattr__(self, "risk_tags", tuple(self.risk_tags))
        object.__setattr__(self, "skill_tags", tuple(self.skill_tags))
        object.__setattr__(self, "assumptions", tuple(self.assumptions))
        object.__setattr__(self, "possible_costs", tuple(self.possible_costs))

    def to_dict(self):
        return {
            "intent": self.intent,
            "check_type": self.check_type,
            "requires_check": self.requires_check,
            "primary_stat": self.primary_stat,
            "difficulty": self.difficulty,
            "target": self.target,
            "item": self.item,
            "method": self.method,
            "desired_outcome": self.desired_outcome,
            "risk_tags": list(self.risk_tags),
            "skill_tags": list(self.skill_tags),
            "assumptions": list(self.assumptions),
            "possible_costs": list(self.possible_costs),
            "source": self.source,
        }


@dataclass(frozen=True)
class AdjudicationValidation:
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
class AdjudicationResult:
    request: AdjudicationRequest
    validation: AdjudicationValidation

    def to_dict(self):
        return {
            "request": self.request.to_dict(),
            "validation": self.validation.to_dict(),
        }


@dataclass(frozen=True)
class NarrationValidation:
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
class NarrationResult:
    text: str
    proposal: NarrationProposal
    validation: NarrationValidation
    used_fallback: bool = False

    def to_dict(self):
        return {
            "text": self.text,
            "proposal": self.proposal.to_dict(),
            "validation": self.validation.to_dict(),
            "used_fallback": self.used_fallback,
        }
