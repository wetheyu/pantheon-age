"""Relationship and faction memory helpers for Phase 6."""

from dataclasses import dataclass, field

from .contracts import MemoryCandidate
from .memory_store import commit_memory_candidates
from .world_relations import NationRelationSignal, validate_relation_signal


RELATION_MEMORY_TYPES = (
    "nation",
    "church_legality",
    "faction_pressure",
    "npc_attitude",
)

RELATION_MEMORY_DIMENSIONS = (
    "political",
    "trade",
    "military",
    "religious",
    "public_opinion",
    "intelligence",
    "legality",
    "attitude",
    "trust",
    "pressure",
)

RELATION_MEMORY_VISIBILITIES = ("public", "rumor", "secret")


@dataclass(frozen=True)
class RelationshipMemorySignal:
    relation_type: str
    subject_a: str
    subject_b: str
    summary: str
    dimension: str = "political"
    delta: int = 0
    visibility: str = "public"
    evidence: tuple[str, ...] = field(default_factory=tuple)
    source_event: str = ""
    confidence: float = 0.7
    source: str = "relationship-memory"

    def __post_init__(self):
        object.__setattr__(self, "evidence", tuple(self.evidence))

    def to_dict(self):
        return {
            "relation_type": self.relation_type,
            "subject_a": self.subject_a,
            "subject_b": self.subject_b,
            "summary": self.summary,
            "dimension": self.dimension,
            "delta": self.delta,
            "visibility": self.visibility,
            "evidence": list(self.evidence),
            "source_event": self.source_event,
            "confidence": self.confidence,
            "source": self.source,
        }


def validate_relationship_memory_signal(signal):
    errors = []
    if signal.relation_type not in RELATION_MEMORY_TYPES:
        errors.append(f"unsupported relation_type: {signal.relation_type}")
    if signal.dimension not in RELATION_MEMORY_DIMENSIONS:
        errors.append(f"unsupported dimension: {signal.dimension}")
    if signal.visibility not in RELATION_MEMORY_VISIBILITIES:
        errors.append(f"unsupported visibility: {signal.visibility}")
    if signal.delta < -5 or signal.delta > 5:
        errors.append("delta must be between -5 and 5")
    if not signal.subject_a.strip():
        errors.append("subject_a is required")
    if not signal.subject_b.strip():
        errors.append("subject_b is required")
    if signal.subject_a == signal.subject_b:
        errors.append("subject_a and subject_b must be different")
    if not signal.summary.strip():
        errors.append("summary is required")
    if not signal.evidence:
        errors.append("relationship memory must include evidence")
    if not isinstance(signal.confidence, (int, float)):
        errors.append("confidence must be numeric")
    elif signal.confidence < 0 or signal.confidence > 1:
        errors.append("confidence must be between 0 and 1")
    if signal.source.startswith(("openai-", "llm-")):
        errors.append("relationship memory cannot come directly from a raw LLM provider")
    return tuple(errors)


def commit_relationship_memory_signals(state, signals):
    candidates = []
    for signal in signals:
        if validate_relationship_memory_signal(signal):
            continue
        candidates.append(relationship_signal_to_memory_candidate(signal))
    return commit_memory_candidates(state, tuple(candidates))


def relationship_signal_to_memory_candidate(signal):
    secret = signal.visibility == "secret"
    return MemoryCandidate(
        memory_type="secret_memory" if secret else "faction_memory",
        subject=relationship_subject(signal),
        content=relationship_content(signal),
        authority_level="secret" if secret else "persistent",
        visibility="system_secret" if secret else "player_known",
        should_persist=True,
        source_event=signal.source_event,
        confidence=signal.confidence,
        source="relationship-memory",
    )


def nation_relation_signal_to_memory_signal(signal, source_event=""):
    visibility = "secret" if signal.visibility == "secret" else signal.visibility
    return RelationshipMemorySignal(
        relation_type="nation",
        subject_a=signal.country_a,
        subject_b=signal.country_b,
        summary=signal.summary,
        dimension=signal.dimension,
        delta=signal.delta,
        visibility=visibility,
        evidence=signal.evidence,
        source_event=source_event,
        confidence=0.7 if signal.visibility == "public" else 0.55,
        source="relationship-memory",
    )


def commit_nation_relation_signals(state, signals, source_event=""):
    relationship_signals = []
    for signal in signals:
        if validate_relation_signal(signal):
            continue
        relationship_signals.append(
            nation_relation_signal_to_memory_signal(signal, source_event=source_event)
        )
    return commit_relationship_memory_signals(state, tuple(relationship_signals))


def relationship_subject(signal):
    return f"{signal.relation_type}:{signal.subject_a}<->{signal.subject_b}"


def relationship_content(signal):
    direction = "改善" if signal.delta > 0 else "恶化" if signal.delta < 0 else "变化"
    evidence = "；".join(signal.evidence)
    return (
        f"{signal.subject_a} 与 {signal.subject_b} 的{signal.dimension}关系出现{direction}"
        f"（delta={signal.delta}）：{signal.summary}（依据：{evidence}）"
    )
