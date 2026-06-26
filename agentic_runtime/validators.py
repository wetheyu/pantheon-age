"""Validators for Phase 5 Agentic Runtime proposals."""

import re

from phase1_cli.data import BASE_STATS
from phase1_cli.intent_parser import INTENT_PRIORITY

from .contracts import (
    AUTHORITY_LEVELS,
    GENERATED_FACT_TYPES,
    MEMORY_TYPES,
    VISIBILITY_LEVELS,
    ValidationResult,
)


SUPPORTED_BRIDGE_INTENTS = frozenset((*INTENT_PRIORITY, "unknown", "world_action"))
ALLOWED_WORLD_RISK_TYPES = frozenset(
    ("violence", "social", "stealth", "theft", "escape", "occult", "travel", "high_risk")
)
MIN_WORLD_DC = 8
MAX_WORLD_DC = 24
UNCOMMITTED_DEATH_PATTERNS = (
    "杀死",
    "杀了",
    "被你击杀",
    "被你杀",
    "当场死亡",
    "确认死亡",
    "已经死亡",
    "目标死亡",
    "对方死亡",
    "他死亡",
    "她死亡",
    "目标死了",
    "对方死了",
    "目标就死了",
    "对方就死了",
    "他死了",
    "她死了",
    "毙命",
    "断气",
    "当场身亡",
    "一命呜呼",
    "倒在血泊",
    "重重倒下",
)
UNEXPECTED_NARRATION_SCRIPT_RE = re.compile(r"[\u0590-\u05ff\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]")
EXCESSIVE_BLANK_LINES_RE = re.compile(r"\n\s*\n\s*\n\s*\n")
CONFIRMED_ACQUISITION_PATTERNS = (
    "买下了",
    "购买了",
    "购得",
    "成交了",
    "交易完成",
    "拿到钥匙",
    "拿到了钥匙",
    "获得钥匙",
    "拿到房契",
    "签下房契",
    "获得房契",
    "拿到地契",
    "签下地契",
    "获得地契",
    "获得产权",
    "产权归你",
    "产权属于你",
    "归你所有",
    "属于你",
    "成为你的",
    "成了你的",
)


def validate_open_action(open_action):
    errors = []
    if not open_action.raw_text.strip():
        errors.append("Open action raw_text is empty.")
    if not open_action.primary_goal.strip():
        errors.append("Open action primary_goal is empty.")
    if not isinstance(open_action.confidence, (int, float)):
        errors.append("Open action confidence must be numeric.")
    elif open_action.confidence < 0 or open_action.confidence > 1:
        errors.append("Open action confidence must be between 0 and 1.")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_temporary_content(content):
    errors = []
    if content.authority_level not in {"flavor", "temporary"}:
        errors.append(f"Temporary content cannot use authority level: {content.authority_level}")
    if content.claimed_state_changes:
        errors.append("Temporary content cannot claim state changes.")
    if content.claimed_new_clues:
        errors.append("Temporary content cannot grant clues.")
    if not content.description.strip():
        errors.append("Temporary content description is empty.")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_npc_proposal(npc):
    errors = []
    errors.extend(validate_temporary_authority("NPC", npc))
    if not npc.name.strip():
        errors.append("NPC name is empty.")
    if not npc.description.strip():
        errors.append("NPC description is empty.")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_event_proposal(event):
    errors = []
    errors.extend(validate_temporary_authority("Event", event))
    if not event.event_type.strip():
        errors.append("Event type is empty.")
    if not event.summary.strip():
        errors.append("Event summary is empty.")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_item_proposal(item):
    errors = []
    if item.authority_level not in {"flavor", "temporary"}:
        errors.append(f"Item cannot use authority level: {item.authority_level}")
    if item.claimed_inventory_changes:
        errors.append("Item proposal cannot claim inventory changes.")
    if item.claimed_state_changes:
        errors.append("Item proposal cannot claim state changes.")
    if item.claimed_new_clues:
        errors.append("Item proposal cannot grant clues.")
    if not item.name.strip():
        errors.append("Item name is empty.")
    if not item.description.strip():
        errors.append("Item description is empty.")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_temporary_authority(label, proposal):
    errors = []
    if proposal.authority_level not in {"flavor", "temporary"}:
        errors.append(f"{label} cannot use authority level: {proposal.authority_level}")
    if proposal.claimed_facts:
        errors.append(f"{label} proposal cannot claim persistent facts.")
    if proposal.claimed_state_changes:
        errors.append(f"{label} proposal cannot claim state changes.")
    if proposal.claimed_new_clues:
        errors.append(f"{label} proposal cannot grant clues.")
    return errors


def validate_rule_adjudication(adjudication):
    errors = []
    if adjudication.action_type not in SUPPORTED_BRIDGE_INTENTS:
        errors.append(f"Unsupported bridge intent: {adjudication.action_type}")
    if adjudication.bridge_action.get("intent") != adjudication.action_type:
        errors.append("Bridge action intent does not match adjudication action_type.")
    for check in adjudication.required_checks:
        if check.stat is not None and check.stat not in BASE_STATS:
            errors.append(f"Unsupported rule check stat: {check.stat}")
        if check.dc is not None and (not isinstance(check.dc, int) or check.dc < 0):
            errors.append("Rule check dc must be a non-negative integer or None.")
    if adjudication.action_type == "world_action":
        errors.extend(validate_world_adjudication(adjudication))
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_world_adjudication(adjudication):
    errors = []
    bridge = adjudication.bridge_action
    requires_check = bool(bridge.get("requires_check"))
    risk_type = bridge.get("risk_type")
    check_stat = bridge.get("check_stat")
    difficulty = bridge.get("difficulty")

    if requires_check:
        if risk_type not in ALLOWED_WORLD_RISK_TYPES:
            errors.append(f"Unsupported world risk_type: {risk_type}")
        if check_stat not in BASE_STATS:
            errors.append(f"Unsupported world check_stat: {check_stat}")
        if not isinstance(difficulty, int):
            errors.append("World difficulty must be an integer when a check is required.")
        elif difficulty < MIN_WORLD_DC or difficulty > MAX_WORLD_DC:
            errors.append(f"World difficulty must be between {MIN_WORLD_DC} and {MAX_WORLD_DC}.")
        if not adjudication.required_checks:
            errors.append("World action with requires_check must include required_checks.")

    for effect in adjudication.allowed_effects:
        if effect in {"target_death", "target_killed"} or effect.startswith(("death:", "killed:")):
            errors.append("Rule adjudication cannot allow death effects in world-mode baseline.")
        if effect in {"location_change", "city_change"} or effect.startswith(("travel_to:", "city:")):
            errors.append("Rule adjudication cannot directly allow city/location changes in world-mode baseline.")

    consequence_text = " ".join(
        str(bridge.get(key, ""))
        for key in ("success_consequence", "failure_consequence")
    )
    if contains_uncommitted_death_text(consequence_text):
        errors.append("Rule adjudication consequence cannot confirm death or killing.")

    blockers = bridge.get("possible_blockers", [])
    if blockers is not None and not isinstance(blockers, list):
        errors.append("possible_blockers must be a list.")

    return errors


def validate_state_commit(commit):
    errors = []
    if not isinstance(commit.rule_action, dict):
        errors.append("State commit rule_action must be a dict.")
    if not isinstance(commit.rule_result, dict):
        errors.append("State commit rule_result must be a dict.")
    if commit.rule_action.get("intent") not in SUPPORTED_BRIDGE_INTENTS:
        errors.append(f"Unsupported committed intent: {commit.rule_action.get('intent')}")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_memory_candidate(candidate):
    errors = []
    if candidate.memory_type not in MEMORY_TYPES:
        errors.append(f"Unsupported memory type: {candidate.memory_type}")
    if candidate.authority_level not in AUTHORITY_LEVELS:
        errors.append(f"Unsupported authority level: {candidate.authority_level}")
    if candidate.visibility not in VISIBILITY_LEVELS:
        errors.append(f"Unsupported visibility: {candidate.visibility}")
    if not candidate.subject.strip():
        errors.append("Memory subject is empty.")
    if not candidate.content.strip():
        errors.append("Memory content is empty.")
    if candidate.should_persist:
        if candidate.authority_level in {"flavor", "temporary"}:
            errors.append("Temporary or flavor memory cannot persist.")
        if candidate.source.startswith(("llm-", "openai-")):
            errors.append("Persistent memory cannot come directly from a raw LLM provider.")
        if candidate.memory_type == "secret_memory" and candidate.visibility != "system_secret":
            errors.append("Secret memory must use system_secret visibility.")
        if candidate.visibility == "system_secret" and candidate.memory_type != "secret_memory":
            errors.append("system_secret visibility must use secret_memory type.")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_generated_fact_proposal(proposal, commit=None):
    errors = []
    if proposal.fact_type not in GENERATED_FACT_TYPES:
        errors.append(f"Unsupported generated fact type: {proposal.fact_type}")
    if proposal.authority_level not in {"persistent", "secret"}:
        errors.append("Generated facts must use persistent or secret authority.")
    if proposal.visibility not in VISIBILITY_LEVELS:
        errors.append(f"Unsupported generated fact visibility: {proposal.visibility}")
    if not proposal.subject.strip():
        errors.append("Generated fact subject is empty.")
    if not proposal.content.strip():
        errors.append("Generated fact content is empty.")
    if not proposal.evidence:
        errors.append("Generated fact must include evidence.")
    if not isinstance(proposal.confidence, (int, float)):
        errors.append("Generated fact confidence must be numeric.")
    elif proposal.confidence < 0 or proposal.confidence > 1:
        errors.append("Generated fact confidence must be between 0 and 1.")
    if proposal.source.startswith(("llm-", "openai-")):
        errors.append("Generated fact cannot come directly from a raw LLM provider.")
    if proposal.fact_type == "secret" and proposal.visibility != "system_secret":
        errors.append("Secret generated facts must use system_secret visibility.")
    if proposal.visibility == "system_secret" and proposal.fact_type != "secret":
        errors.append("system_secret visibility must use secret generated fact type.")
    if contains_uncommitted_death_text(proposal.content):
        committed = set(commit.committed_effects) if commit else set()
        if not any(effect in committed for effect in ("target_death", "target_killed")):
            errors.append("Generated fact cannot confirm death without committed death authority.")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def validate_narration_proposal(narration, commit):
    errors = []
    if not narration.text.strip():
        errors.append("Narration text is empty.")
    if contains_unexpected_narration_script(narration.text):
        errors.append("Narration contains unexpected non-Chinese script characters.")
    if has_excessive_blank_lines(narration.text):
        errors.append("Narration contains excessive blank lines.")
    committed = set(commit.committed_effects)
    claimed = set(narration.claimed_effects)
    extra = sorted(claimed - committed)
    if extra:
        errors.append("Narration claimed uncommitted effects: " + ", ".join(extra))
    if claims_uncommitted_death(narration.text, commit):
        errors.append("Narration confirmed death or killing without committed death authority.")
    if claims_blocked_acquisition(narration.text, commit):
        errors.append("Narration confirmed blocked acquisition despite feasibility gate.")
    return ValidationResult(is_valid=not errors, errors=tuple(errors))


def contains_unexpected_narration_script(text):
    return bool(UNEXPECTED_NARRATION_SCRIPT_RE.search(text))


def has_excessive_blank_lines(text):
    return bool(EXCESSIVE_BLANK_LINES_RE.search(text))


def claims_uncommitted_death(text, commit):
    committed = set(commit.committed_effects)
    if any(effect in committed for effect in ("target_death", "target_killed")):
        return False
    if any(effect.startswith(("death:", "killed:")) for effect in committed):
        return False

    raw_text = str(commit.rule_action.get("raw_text", "")).strip()
    check_text = text
    if raw_text:
        check_text = check_text.replace(raw_text, "")

    return contains_uncommitted_death_text(check_text)


def contains_uncommitted_death_text(text):
    normalized_text = str(text)
    for harmless_phrase in (
        "没有尸体",
        "无尸体",
        "不见尸体",
        "找不到尸体",
        "没有遗体",
        "无遗体",
        "死亡之神",
        "死亡教会",
    ):
        normalized_text = normalized_text.replace(harmless_phrase, "")
    return any(pattern in normalized_text for pattern in UNCOMMITTED_DEATH_PATTERNS)


def claims_blocked_acquisition(text, commit):
    feasibility = commit.rule_result.get("feasibility") or {}
    if not feasibility.get("blocked"):
        return False
    if "unconfirmed_property_acquisition" not in set(commit.rejected_effects):
        return False
    return any(
        contains_non_negated_pattern(text, pattern)
        for pattern in CONFIRMED_ACQUISITION_PATTERNS
    )


def contains_non_negated_pattern(text, pattern):
    start = 0
    while True:
        index = text.find(pattern, start)
        if index < 0:
            return False
        prefix = text[max(0, index - 10):index]
        if not any(marker in prefix for marker in ("不", "不能", "无法", "没有", "尚未", "不会", "不可能")):
            return True
        start = index + len(pattern)
