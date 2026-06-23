"""Keyword-based intent parser.

The current CLI version does not use an LLM. The parser turns natural Chinese input into a
small dict that the rule engine can handle deterministically.
"""

from .data import INTENT_KEYWORDS, ITEM_ALIASES, LOCATION_ALIASES


CHECK_DEFAULTS = {
    "investigate": ("intelligence", 12),
    "attack": ("strength", 14),
    "pray": ("faith", 12),
    "stealth": ("agility", 14),
    "talk": ("intelligence", 12),
    "analyze": ("intelligence", 14),
}

INTENT_PRIORITY = [
    "use_item",
    "attack",
    "stealth",
    "analyze",
    "investigate",
    "pray",
    "rest",
    "talk",
    "move",
]


def parse_intent(text, current_location=""):
    raw_text = text.strip()
    target = extract_location(raw_text)
    item = extract_item(raw_text)
    intent = detect_intent(raw_text, target)

    if intent == "move" and not target:
        target = guess_return_target(raw_text, current_location)

    check_stat, difficulty = CHECK_DEFAULTS.get(intent, (None, None))

    return {
        "intent": intent,
        "target": target,
        "item": item,
        "requires_check": check_stat is not None,
        "check_stat": check_stat,
        "difficulty": difficulty,
        "raw_text": raw_text,
    }


def detect_intent(text, target=None):
    if target and has_move_keyword(text):
        return "move"

    for intent in INTENT_PRIORITY:
        for keyword in INTENT_KEYWORDS[intent]:
            if keyword in text:
                return intent
    return "unknown"


def has_move_keyword(text):
    return any(keyword in text for keyword in INTENT_KEYWORDS["move"])


def extract_location(text):
    aliases = sorted(LOCATION_ALIASES, key=len, reverse=True)
    for alias in aliases:
        if alias in text:
            return LOCATION_ALIASES[alias]
    return None


def extract_item(text):
    aliases = sorted(ITEM_ALIASES, key=len, reverse=True)
    for alias in aliases:
        if alias in text:
            return ITEM_ALIASES[alias]
    return None


def guess_return_target(text, current_location):
    if not any(word in text for word in ["离开", "返回", "回到", "回去"]):
        return None

    if current_location != "修道院门口":
        return "修道院门口"
    return None
