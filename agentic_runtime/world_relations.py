"""Dynamic nation relation contracts for the Phase 5 baseline.

Nation relations are not fixed canon. Agents may propose relation signals after
events, and a future memory/state layer can decide whether to persist them.
"""

from dataclasses import dataclass, field

from phase1_cli.scenarios import origin_country_ids


RELATION_DIMENSIONS = (
    "political",
    "trade",
    "military",
    "religious",
    "public_opinion",
    "intelligence",
)

RELATION_EVENT_TYPES = (
    "treaty",
    "trade_deal",
    "border_incident",
    "religious_dispute",
    "espionage",
    "sanction",
    "mediation",
    "war_crisis",
    "player_action",
    "world_event",
)

RELATION_VISIBILITY_LEVELS = ("public", "rumor", "secret")


@dataclass(frozen=True)
class NationRelationSignal:
    country_a: str
    country_b: str
    event_type: str
    summary: str
    dimension: str = "political"
    delta: int = 0
    visibility: str = "public"
    evidence: tuple[str, ...] = field(default_factory=tuple)
    source: str = "relation-agent"

    def __post_init__(self):
        object.__setattr__(self, "evidence", tuple(self.evidence))

    def to_dict(self):
        return {
            "country_a": self.country_a,
            "country_b": self.country_b,
            "event_type": self.event_type,
            "summary": self.summary,
            "dimension": self.dimension,
            "delta": self.delta,
            "visibility": self.visibility,
            "evidence": list(self.evidence),
            "source": self.source,
        }


@dataclass(frozen=True)
class NationRelationSnapshot:
    country_a: str
    country_b: str
    score: int = 0
    stance: str = "neutral"
    drivers: tuple[str, ...] = field(default_factory=tuple)
    recent_signals: tuple[NationRelationSignal, ...] = field(default_factory=tuple)
    confidence: float = 0.5

    def __post_init__(self):
        object.__setattr__(self, "drivers", tuple(self.drivers))
        object.__setattr__(self, "recent_signals", tuple(self.recent_signals))

    def to_dict(self):
        return {
            "country_a": self.country_a,
            "country_b": self.country_b,
            "score": self.score,
            "stance": self.stance,
            "drivers": list(self.drivers),
            "recent_signals": [signal.to_dict() for signal in self.recent_signals],
            "confidence": self.confidence,
        }


def validate_relation_signal(signal):
    errors = []
    valid_countries = set(origin_country_ids())
    if signal.country_a not in valid_countries:
        errors.append(f"unknown country_a: {signal.country_a}")
    if signal.country_b not in valid_countries:
        errors.append(f"unknown country_b: {signal.country_b}")
    if signal.country_a == signal.country_b:
        errors.append("country_a and country_b must be different")
    if signal.dimension not in RELATION_DIMENSIONS:
        errors.append(f"unknown dimension: {signal.dimension}")
    if signal.event_type not in RELATION_EVENT_TYPES:
        errors.append(f"unknown event_type: {signal.event_type}")
    if signal.visibility not in RELATION_VISIBILITY_LEVELS:
        errors.append(f"unknown visibility: {signal.visibility}")
    if signal.delta < -5 or signal.delta > 5:
        errors.append("delta must be between -5 and 5")
    if not signal.summary.strip():
        errors.append("summary is required")
    return tuple(errors)


def create_neutral_relation(country_a, country_b):
    return NationRelationSnapshot(
        country_a=country_a,
        country_b=country_b,
        score=0,
        stance="neutral",
        drivers=(),
        recent_signals=(),
        confidence=0.5,
    )


def apply_relation_signal(snapshot, signal, recent_limit=5):
    errors = validate_relation_signal(signal)
    if errors:
        return snapshot
    if set((snapshot.country_a, snapshot.country_b)) != set((signal.country_a, signal.country_b)):
        return snapshot

    score = clamp(snapshot.score + signal.delta, -100, 100)
    return NationRelationSnapshot(
        country_a=snapshot.country_a,
        country_b=snapshot.country_b,
        score=score,
        stance=stance_from_score(score),
        drivers=append_unique(snapshot.drivers, signal.dimension),
        recent_signals=(snapshot.recent_signals + (signal,))[-recent_limit:],
        confidence=max(snapshot.confidence, 0.6),
    )


def stance_from_score(score):
    if score <= -75:
        return "war_crisis"
    if score <= -40:
        return "hostile"
    if score <= -10:
        return "tense"
    if score < 10:
        return "neutral"
    if score < 40:
        return "cooperative"
    if score < 75:
        return "friendly"
    return "allied"


def clamp(value, low, high):
    return max(low, min(high, value))


def append_unique(items, item):
    if item in items:
        return tuple(items)
    return tuple(items) + (item,)
