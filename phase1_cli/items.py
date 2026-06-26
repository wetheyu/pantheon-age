"""Structured item rules for world-mode checks.

Inventory is still saved as a simple list of item names. This module gives
those names rule-facing meaning without changing the save format.
"""

from .data import ITEMS, ITEM_ALIASES
from .progression import action_text_for_skill_match


ITEM_RULE_DEFINITIONS = {
    "制式佩剑": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("violence",),
                "check_stats": ("strength",),
                "keywords": ("制式佩剑", "佩剑", "剑", "武器", "决斗"),
                "bonus": 1,
            }
        ],
    },
    "旧式手盾": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("violence", "escape", "high_risk"),
                "check_stats": ("strength", "agility"),
                "keywords": ("旧式手盾", "手盾", "盾", "格挡", "防御", "护住"),
                "bonus": 1,
            }
        ],
    },
    "破旧法术书": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("occult",),
                "check_stats": ("intelligence", "faith"),
                "keywords": ("破旧法术书", "法术书", "书", "符号", "仪式", "异常", "研究"),
                "bonus": 1,
            }
        ],
    },
    "仪式粉末": {
        "category": "consumable",
        "effects": [
            {
                "risk_types": ("occult", "high_risk"),
                "check_stats": ("intelligence", "faith"),
                "keywords": ("仪式粉末", "粉末", "撒", "显形", "仪式纹路"),
                "bonus": 2,
                "consume": True,
            }
        ],
    },
    "开锁工具": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("theft", "stealth"),
                "check_stats": ("agility",),
                "keywords": ("开锁工具", "开锁", "撬锁", "锁", "抽屉", "工具"),
                "bonus": 2,
            }
        ],
    },
    "假名证件": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("social", "stealth", "high_risk"),
                "check_stats": ("intelligence", "agility"),
                "keywords": ("假名证件", "证件", "假证", "身份", "伪装", "盘问"),
                "bonus": 1,
            }
        ],
    },
    "猎刀": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("violence", "escape", "travel"),
                "check_stats": ("strength", "agility"),
                "keywords": ("猎刀", "刀", "切割", "防身", "野外"),
                "bonus": 1,
            }
        ],
    },
    "简易陷阱": {
        "category": "consumable",
        "effects": [
            {
                "risk_types": ("violence", "escape", "high_risk"),
                "check_stats": ("agility", "intelligence"),
                "keywords": ("简易陷阱", "陷阱", "布置", "绊住", "拖慢"),
                "bonus": 2,
                "consume": True,
            }
        ],
    },
    "圣徽": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("occult", "social", "high_risk"),
                "check_stats": ("faith", "intelligence"),
                "keywords": ("圣徽", "祈祷", "祷告", "净化", "安魂", "教会"),
                "bonus": 1,
            }
        ],
    },
    "小瓶圣水": {
        "category": "consumable",
        "effects": [
            {
                "risk_types": ("occult", "high_risk"),
                "check_stats": ("faith", "intelligence"),
                "keywords": ("小瓶圣水", "圣水", "净化", "污染", "压制"),
                "bonus": 2,
                "consume": True,
            }
        ],
        "direct_use": {"corruption": -2, "san": 1},
    },
    "止血药剂": {
        "category": "consumable",
        "effects": [],
        "direct_use": {"hp": 4, "alchemist_hp_bonus": 1},
    },
    "镇静药剂": {
        "category": "consumable",
        "effects": [],
        "direct_use": {"san": 2, "alchemist_san_bonus": 1},
    },
    "炼金工具包": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("occult", "high_risk", "theft"),
                "check_stats": ("intelligence", "agility"),
                "keywords": ("炼金工具包", "炼金", "工具包", "药剂", "鉴定", "材料", "调剂"),
                "bonus": 2,
            }
        ],
    },
    "暗色斗篷": {
        "category": "ordinary",
        "effects": [
            {
                "risk_types": ("stealth", "escape"),
                "check_stats": ("agility",),
                "keywords": ("暗色斗篷", "斗篷", "隐藏", "潜行", "阴影"),
                "bonus": 1,
            }
        ],
    },
}


DIRECT_ITEM_USE_VERBS = (
    "使用",
    "用",
    "喝",
    "喝下",
    "服用",
    "拿出",
    "撒",
    "布置",
    "点燃",
)


def item_affordances_for(character):
    return [
        compact_item_definition(item_name)
        for item_name in character.inventory
        if item_name in ITEMS
    ]


def compact_item_definition(item_name):
    definition = item_definition_for(item_name)
    return {
        "name": item_name,
        "category": definition["category"],
        "description": definition["description"],
        "consumable": definition["consumable"],
        "effects": [compact_item_effect(effect) for effect in definition.get("effects", ())],
        "direct_use": dict(definition.get("direct_use", {})),
    }


def compact_item_effect(effect):
    return {
        "risk_types": list(effect.get("risk_types", ())),
        "check_stats": list(effect.get("check_stats", ())),
        "bonus": effect.get("bonus", 0),
        "consume": bool(effect.get("consume", False)),
    }


def item_definition_for(item_name):
    base = ITEMS.get(item_name, {})
    rule = ITEM_RULE_DEFINITIONS.get(item_name, {})
    return {
        "category": rule.get("category", "ordinary"),
        "description": base.get("description", ""),
        "consumable": bool(base.get("consumable", False)),
        "effects": list(rule.get("effects", ())),
        "direct_use": dict(rule.get("direct_use", {})),
    }


def activate_items_for_check(character, risk_type, stat, rule_action=None):
    action_text = action_text_for_skill_match(rule_action or {})
    active = []
    consumed = []
    for item_name in list(character.inventory):
        definition = item_definition_for(item_name)
        for effect in definition.get("effects", ()):
            if not item_effect_matches(item_name, effect, risk_type, stat, action_text):
                continue
            active.append(
                {
                    "name": item_name,
                    "category": definition["category"],
                    "bonus": effect.get("bonus", 0),
                    "description": definition["description"],
                    "consumed": bool(effect.get("consume", False)),
                }
            )
            if effect.get("consume") and character.remove_item(item_name):
                consumed.append(item_name)
            break
    return active, consumed


def item_effect_matches(item_name, effect, risk_type, stat, action_text):
    if risk_type not in effect.get("risk_types", ()):
        return False
    if effect.get("check_stats") and stat not in effect["check_stats"]:
        return False
    return item_was_invoked(item_name, effect, action_text)


def item_was_invoked(item_name, effect, action_text):
    if not action_text:
        return False
    terms = {item_name}
    for alias, canonical in ITEM_ALIASES.items():
        if canonical == item_name:
            terms.add(alias)
    return any(term and term in action_text for term in terms)


def detect_direct_item_use(rule_action, character):
    action_text = action_text_for_skill_match(rule_action or {})
    if not any(verb in action_text for verb in DIRECT_ITEM_USE_VERBS):
        return None
    for item_name in character.inventory:
        definition = item_definition_for(item_name)
        if not definition.get("direct_use"):
            continue
        if item_was_invoked(item_name, {"keywords": ()}, action_text):
            return item_name
    return None
