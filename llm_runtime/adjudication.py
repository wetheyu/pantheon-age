"""Generic adjudication requests for semantic action candidates."""

from phase1_cli.data import DIFFICULTY, STAT_NAMES

from .contracts import ActionCandidate, AdjudicationRequest, AdjudicationResult, AdjudicationValidation


SUPPORTED_SKILL_TAGS = frozenset(
    {
        "attack",
        "analyze",
        "craft",
        "deceive",
        "force",
        "investigate",
        "lore",
        "medicine",
        "move",
        "perception",
        "pray",
        "ritual",
        "social",
        "stealth",
        "survival",
        "talk",
        "track",
        "travel",
        "use_item",
    }
)

SUPPORTED_RISK_TAGS = frozenset(
    {
        "combat",
        "corruption",
        "deception",
        "hp_loss",
        "noise",
        "resource",
        "san_loss",
        "social",
        "suspicion",
        "time",
        "travel",
        "unknown",
    }
)

SUPPORTED_COST_TAGS = frozenset(
    {
        "consume_item",
        "corruption_gain",
        "hp_loss",
        "lost_time",
        "noise",
        "san_loss",
        "suspicion_gain",
    }
)

INTENT_ADJUDICATION_DEFAULTS = {
    "move": {
        "check_type": "travel",
        "requires_check": False,
        "primary_stat": None,
        "difficulty": None,
        "skill_tags": ("travel", "move"),
        "risk_tags": ("time",),
        "possible_costs": ("lost_time",),
    },
    "investigate": {
        "check_type": "investigation",
        "requires_check": True,
        "primary_stat": "intelligence",
        "difficulty": DIFFICULTY["normal"],
        "skill_tags": ("investigate", "perception"),
        "risk_tags": ("time",),
        "possible_costs": ("lost_time",),
    },
    "analyze": {
        "check_type": "occult_analysis",
        "requires_check": True,
        "primary_stat": "intelligence",
        "difficulty": DIFFICULTY["normal"],
        "skill_tags": ("analyze", "lore"),
        "risk_tags": ("san_loss", "corruption"),
        "possible_costs": ("san_loss", "corruption_gain"),
    },
    "attack": {
        "check_type": "combat",
        "requires_check": True,
        "primary_stat": "strength",
        "difficulty": DIFFICULTY["normal"],
        "skill_tags": ("attack",),
        "risk_tags": ("combat", "hp_loss"),
        "possible_costs": ("hp_loss",),
    },
    "pray": {
        "check_type": "faith",
        "requires_check": True,
        "primary_stat": "faith",
        "difficulty": DIFFICULTY["normal"],
        "skill_tags": ("pray", "ritual"),
        "risk_tags": ("san_loss",),
        "possible_costs": ("san_loss",),
    },
    "rest": {
        "check_type": "recovery",
        "requires_check": False,
        "primary_stat": None,
        "difficulty": None,
        "skill_tags": (),
        "risk_tags": ("time",),
        "possible_costs": ("lost_time",),
    },
    "use_item": {
        "check_type": "item_use",
        "requires_check": False,
        "primary_stat": None,
        "difficulty": None,
        "skill_tags": ("use_item",),
        "risk_tags": ("resource",),
        "possible_costs": ("consume_item",),
    },
    "stealth": {
        "check_type": "stealth",
        "requires_check": True,
        "primary_stat": "agility",
        "difficulty": DIFFICULTY["normal"],
        "skill_tags": ("stealth",),
        "risk_tags": ("suspicion", "noise"),
        "possible_costs": ("suspicion_gain", "noise"),
    },
    "talk": {
        "check_type": "social",
        "requires_check": True,
        "primary_stat": "intelligence",
        "difficulty": DIFFICULTY["normal"],
        "skill_tags": ("talk", "social"),
        "risk_tags": ("social", "suspicion"),
        "possible_costs": ("suspicion_gain",),
    },
    "unknown": {
        "check_type": "unknown",
        "requires_check": False,
        "primary_stat": None,
        "difficulty": None,
        "skill_tags": (),
        "risk_tags": ("unknown",),
        "possible_costs": (),
    },
}


def build_adjudication_request(candidate):
    defaults = INTENT_ADJUDICATION_DEFAULTS.get(candidate.intent, INTENT_ADJUDICATION_DEFAULTS["unknown"])
    skill_tags = merge_tags(defaults["skill_tags"], candidate.skill_tags)
    risk_tags = merge_tags(defaults["risk_tags"], candidate.risk_tags)
    possible_costs = merge_tags(defaults["possible_costs"], costs_from_risks(risk_tags))

    return AdjudicationRequest(
        intent=candidate.intent,
        check_type=defaults["check_type"],
        requires_check=defaults["requires_check"],
        primary_stat=defaults["primary_stat"],
        difficulty=defaults["difficulty"],
        target=candidate.target,
        item=candidate.item,
        method=candidate.method,
        desired_outcome=candidate.desired_outcome,
        risk_tags=risk_tags,
        skill_tags=skill_tags,
        assumptions=candidate.assumptions,
        possible_costs=possible_costs,
        source=candidate.source,
    )


def adjudicate_candidate(candidate):
    request = build_adjudication_request(candidate)
    return AdjudicationResult(
        request=request,
        validation=validate_adjudication_request(request),
    )


def validate_adjudication_request(request):
    errors = []

    if request.check_type not in {data["check_type"] for data in INTENT_ADJUDICATION_DEFAULTS.values()}:
        errors.append(f"Unsupported check type: {request.check_type}")

    if request.primary_stat is not None and request.primary_stat not in STAT_NAMES:
        errors.append(f"Unsupported primary stat: {request.primary_stat}")

    if request.difficulty is not None and (not isinstance(request.difficulty, int) or request.difficulty < 0):
        errors.append("Difficulty must be a non-negative integer or None.")

    errors.extend(validate_tags("skill", request.skill_tags, SUPPORTED_SKILL_TAGS))
    errors.extend(validate_tags("risk", request.risk_tags, SUPPORTED_RISK_TAGS))
    errors.extend(validate_tags("cost", request.possible_costs, SUPPORTED_COST_TAGS))

    return AdjudicationValidation(is_valid=not errors, errors=tuple(errors))


def validate_semantic_tags(candidate):
    errors = []
    errors.extend(validate_tags("skill", candidate.skill_tags, SUPPORTED_SKILL_TAGS))
    errors.extend(validate_tags("risk", candidate.risk_tags, SUPPORTED_RISK_TAGS))
    return errors


def validate_tags(label, tags, supported_tags):
    errors = []
    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            errors.append(f"Empty {label} tag.")
        elif tag not in supported_tags:
            errors.append(f"Unsupported {label} tag: {tag}")
    return errors


def merge_tags(*tag_groups):
    merged = []
    for tags in tag_groups:
        for tag in tags:
            if tag not in merged:
                merged.append(tag)
    return tuple(merged)


def costs_from_risks(risk_tags):
    costs = []
    risk_cost_map = {
        "combat": ("hp_loss",),
        "corruption": ("corruption_gain",),
        "deception": ("suspicion_gain",),
        "hp_loss": ("hp_loss",),
        "noise": ("noise",),
        "resource": ("consume_item",),
        "san_loss": ("san_loss",),
        "suspicion": ("suspicion_gain",),
        "time": ("lost_time",),
        "travel": ("lost_time",),
    }
    for risk_tag in risk_tags:
        for cost in risk_cost_map.get(risk_tag, ()):
            if cost not in costs:
                costs.append(cost)
    return tuple(costs)
