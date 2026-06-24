"""Structured action candidate handling for Phase 4."""

from phase1_cli.intent_parser import CHECK_DEFAULTS, INTENT_PRIORITY, parse_intent

from .adjudication import SUPPORTED_RISK_TAGS, SUPPORTED_SKILL_TAGS, validate_semantic_tags
from .contracts import ActionCandidate, ActionCandidateResult, ActionCandidateValidation


SUPPORTED_ACTION_INTENTS = frozenset(INTENT_PRIORITY)


def build_keyword_action_candidate(user_text, current_location=""):
    """Wrap the existing deterministic parser result as an ActionCandidate."""
    action = parse_intent(user_text, current_location)
    return ActionCandidate(
        intent=action["intent"],
        target=action.get("target"),
        item=action.get("item"),
        method=raw_method_from_text(action["raw_text"]),
        desired_outcome="",
        confidence=1.0,
        raw_text=action["raw_text"],
        source="keyword",
    )


def validate_action_candidate(candidate):
    """Validate a proposed action before the rule engine can receive it."""
    errors = []

    if not isinstance(candidate.intent, str) or not candidate.intent.strip():
        errors.append("Action intent is empty.")
    elif candidate.intent not in SUPPORTED_ACTION_INTENTS:
        errors.append(f"Unsupported action intent: {candidate.intent}")

    if candidate.target is not None:
        if not isinstance(candidate.target, str) or not candidate.target.strip():
            errors.append("Action target is empty.")

    if candidate.item is not None:
        if not isinstance(candidate.item, str) or not candidate.item.strip():
            errors.append("Action item is empty.")

    if not isinstance(candidate.confidence, (int, float)):
        errors.append("Action confidence must be a number.")
    elif candidate.confidence < 0 or candidate.confidence > 1:
        errors.append("Action confidence must be between 0 and 1.")

    if candidate.method is not None and not isinstance(candidate.method, str):
        errors.append("Action method must be text.")

    if candidate.desired_outcome is not None and not isinstance(candidate.desired_outcome, str):
        errors.append("Action desired_outcome must be text.")

    if not isinstance(candidate.assumptions, tuple):
        errors.append("Action assumptions must be a tuple or list of text.")
    elif not all(isinstance(assumption, str) and assumption.strip() for assumption in candidate.assumptions):
        errors.append("Action assumptions must contain non-empty text.")

    errors.extend(validate_semantic_tags(candidate))

    return ActionCandidateValidation(is_valid=not errors, errors=tuple(errors))


def candidate_to_action(candidate, user_text):
    """Convert a valid candidate into the action dict accepted by rule_engine."""
    check_stat, difficulty = CHECK_DEFAULTS.get(candidate.intent, (None, None))
    return {
        "intent": candidate.intent,
        "target": candidate.target,
        "item": candidate.item,
        "method": candidate.method,
        "desired_outcome": candidate.desired_outcome,
        "risk_tags": list(candidate.risk_tags),
        "skill_tags": list(candidate.skill_tags),
        "assumptions": list(candidate.assumptions),
        "requires_check": check_stat is not None,
        "check_stat": check_stat,
        "difficulty": difficulty,
        "raw_text": user_text.strip(),
    }


def normalize_action_candidate(candidate):
    """Keep useful LLM understanding while trimming unsupported non-core tags."""
    skill_tags, skill_notes = normalize_tags(
        candidate.skill_tags,
        SUPPORTED_SKILL_TAGS,
        "skill",
    )
    risk_tags, risk_notes = normalize_tags(
        candidate.risk_tags,
        SUPPORTED_RISK_TAGS,
        "risk",
    )
    assumptions = tuple(candidate.assumptions) + tuple(skill_notes) + tuple(risk_notes)

    return ActionCandidate(
        intent=candidate.intent,
        target=candidate.target,
        item=candidate.item,
        method=candidate.method,
        desired_outcome=candidate.desired_outcome,
        risk_tags=risk_tags,
        skill_tags=skill_tags,
        assumptions=assumptions,
        confidence=candidate.confidence,
        raw_text=candidate.raw_text,
        source=candidate.source,
    )


def normalize_tags(tags, supported_tags, label):
    normalized = []
    notes = []
    for tag in tags:
        if not isinstance(tag, str):
            notes.append(f"Ignored non-text {label} tag from LLM: {tag}")
            continue

        key = tag.strip().lower()
        if not key:
            continue

        if key in supported_tags:
            if key not in normalized:
                normalized.append(key)
        else:
            notes.append(f"Ignored unsupported {label} tag from LLM: {tag}")
    return tuple(normalized), notes


def resolve_action_candidate(user_text, current_location="", candidate=None, provider=None):
    """Use a valid candidate or fall back to the deterministic keyword parser."""
    if provider is not None:
        candidate = provider.propose_action_candidate(user_text, current_location)
    elif candidate is None:
        candidate = build_keyword_action_candidate(user_text, current_location)

    candidate = normalize_action_candidate(candidate)
    validation = validate_action_candidate(candidate)
    if validation.is_valid:
        return ActionCandidateResult(
            action=candidate_to_action(candidate, user_text),
            candidate=candidate,
            validation=validation,
            used_fallback=False,
        )

    fallback_action = parse_intent(user_text, current_location)
    return ActionCandidateResult(
        action=fallback_action,
        candidate=candidate,
        validation=validation,
        used_fallback=True,
    )


def raw_method_from_text(raw_text):
    return raw_text.strip()
