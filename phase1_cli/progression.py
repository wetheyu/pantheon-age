"""Progression defaults and compatibility helpers for Phase 8."""

DEFAULT_CLASS_LEVEL = 1
DEFAULT_FAITH_LEVEL = 1
DEFAULT_ASCENSION_RANK = 0
DEFAULT_REVELATION = 0
DEFAULT_DEVOTION = 0
DEFAULT_BURDENS = []
DEFAULT_PROGRESSION_FLAGS = {}

ATTRIBUTE_NAMES = (
    "physique",
    "agility",
    "insight",
    "knowledge",
    "will",
    "communion",
)

ATTRIBUTE_LABELS = {
    "physique": "体魄",
    "agility": "灵巧",
    "insight": "洞察",
    "knowledge": "知识",
    "will": "意志",
    "communion": "共鸣",
}

DEFAULT_ATTRIBUTES = {
    "physique": 10,
    "agility": 10,
    "insight": 10,
    "knowledge": 10,
    "will": 10,
    "communion": 10,
}

WORLD_CHECK_ATTRIBUTE_PROFILES = {
    ("violence", "strength"): {
        "primary_attribute": "physique",
        "secondary_attributes": ("will",),
        "label": "正面对抗",
    },
    ("violence", "agility"): {
        "primary_attribute": "agility",
        "secondary_attributes": ("insight",),
        "label": "机动暴力",
    },
    ("social", "intelligence"): {
        "primary_attribute": "insight",
        "secondary_attributes": ("knowledge", "will"),
        "label": "社交判断",
    },
    ("social", "faith"): {
        "primary_attribute": "will",
        "secondary_attributes": ("communion", "insight"),
        "label": "信仰施压",
    },
    ("stealth", "agility"): {
        "primary_attribute": "agility",
        "secondary_attributes": ("insight",),
        "label": "隐蔽行动",
    },
    ("theft", "agility"): {
        "primary_attribute": "agility",
        "secondary_attributes": ("insight", "knowledge"),
        "label": "盗取与开锁",
    },
    ("escape", "agility"): {
        "primary_attribute": "agility",
        "secondary_attributes": ("physique", "insight"),
        "label": "脱离追捕",
    },
    ("occult", "intelligence"): {
        "primary_attribute": "knowledge",
        "secondary_attributes": ("insight", "communion"),
        "label": "神秘解析",
    },
    ("occult", "faith"): {
        "primary_attribute": "communion",
        "secondary_attributes": ("will", "knowledge"),
        "label": "神秘承受",
    },
    ("travel", "agility"): {
        "primary_attribute": "agility",
        "secondary_attributes": ("insight", "physique"),
        "label": "旅行行动",
    },
    ("travel", "intelligence"): {
        "primary_attribute": "insight",
        "secondary_attributes": ("knowledge",),
        "label": "路线判断",
    },
    ("high_risk", "strength"): {
        "primary_attribute": "physique",
        "secondary_attributes": ("will",),
        "label": "高风险体能",
    },
    ("high_risk", "agility"): {
        "primary_attribute": "agility",
        "secondary_attributes": ("insight",),
        "label": "高风险身手",
    },
    ("high_risk", "intelligence"): {
        "primary_attribute": "insight",
        "secondary_attributes": ("knowledge",),
        "label": "高风险判断",
    },
    ("high_risk", "faith"): {
        "primary_attribute": "will",
        "secondary_attributes": ("communion",),
        "label": "高风险意志",
    },
}

CLASS_ADVANCEMENT_ATTRIBUTES = {
    "warrior": "physique",
    "mage": "knowledge",
    "rogue": "agility",
    "hunter": "insight",
    "priest": "will",
    "alchemist": "knowledge",
}

ADVANCEMENT_TYPES = {
    "class_level": {
        "label": "职业等级提升",
        "target_level": 2,
        "revelation_cost": 1,
    },
    "faith_level": {
        "label": "信仰等级提升",
        "target_level": 2,
        "revelation_cost": 1,
        "favor_cost": 1,
    },
    "ascension_rank": {
        "label": "神秘阶位晋升",
        "target_level": 1,
        "revelation_cost": 3,
        "favor_cost": 1,
        "required_class_level": 2,
        "required_faith_level": 2,
        "burden": "见证者烙印：你开始被异常秩序注意。",
    },
}

CLASS_STARTING_ATTRIBUTES = {
    "warrior": {
        "physique": 15,
        "agility": 10,
        "insight": 11,
        "knowledge": 9,
        "will": 14,
        "communion": 10,
    },
    "mage": {
        "physique": 8,
        "agility": 10,
        "insight": 12,
        "knowledge": 15,
        "will": 11,
        "communion": 14,
    },
    "rogue": {
        "physique": 10,
        "agility": 15,
        "insight": 14,
        "knowledge": 11,
        "will": 10,
        "communion": 9,
    },
    "hunter": {
        "physique": 12,
        "agility": 14,
        "insight": 14,
        "knowledge": 10,
        "will": 11,
        "communion": 9,
    },
    "priest": {
        "physique": 10,
        "agility": 9,
        "insight": 12,
        "knowledge": 11,
        "will": 15,
        "communion": 14,
    },
    "alchemist": {
        "physique": 9,
        "agility": 11,
        "insight": 14,
        "knowledge": 15,
        "will": 10,
        "communion": 11,
    },
}

CLASS_STARTING_SKILLS = {
    "warrior": ["正面战斗基础"],
    "mage": ["异常解析基础"],
    "rogue": ["潜行开锁基础"],
    "hunter": ["追踪侦察基础"],
    "priest": ["祷告仪式基础"],
    "alchemist": ["药剂鉴定基础"],
}

CLASS_SKILL_DEFINITIONS = {
    "正面战斗基础": {
        "class_id": "warrior",
        "description": "在正面对抗、护卫、压制和武器交锋中保持姿态。",
        "risk_types": ("violence",),
        "check_stats": ("strength",),
        "attribute_hints": ("physique", "will"),
        "keywords": ("战斗", "攻击", "护卫", "阻挡", "压制", "决斗", "守卫"),
        "bonus": 2,
    },
    "异常解析基础": {
        "class_id": "mage",
        "description": "阅读仪式、符号、异常现象和神秘学结构。",
        "risk_types": ("occult",),
        "check_stats": ("intelligence", "faith"),
        "attribute_hints": ("knowledge", "communion"),
        "keywords": ("异常", "仪式", "符号", "法术", "解析", "禁书", "神秘"),
        "bonus": 2,
    },
    "潜行开锁基础": {
        "class_id": "rogue",
        "description": "避开视线、处理锁具、伪装身份和无声接近目标。",
        "risk_types": ("stealth", "theft", "escape"),
        "check_stats": ("agility",),
        "attribute_hints": ("agility", "insight"),
        "keywords": ("潜行", "潜入", "开锁", "撬", "偷", "伪装", "尾随"),
        "bonus": 2,
    },
    "追踪侦察基础": {
        "class_id": "hunter",
        "description": "追踪痕迹、侦察路线、识别陷阱和在复杂地形中行动。",
        "risk_types": ("stealth", "escape", "high_risk", "travel"),
        "check_stats": ("agility", "intelligence"),
        "attribute_hints": ("agility", "insight"),
        "keywords": ("追踪", "侦察", "足迹", "陷阱", "路线", "埋伏", "野外"),
        "bonus": 2,
    },
    "祷告仪式基础": {
        "class_id": "priest",
        "description": "进行公开或私下祷告、净化、安魂和抵抗神秘压力。",
        "risk_types": ("occult", "social", "high_risk"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("will", "communion"),
        "keywords": ("祷告", "净化", "安魂", "祝福", "忏悔", "圣徽", "仪式"),
        "bonus": 2,
    },
    "药剂鉴定基础": {
        "class_id": "alchemist",
        "description": "鉴定药剂、毒素、材料和炼金器具，并做安全处理。",
        "risk_types": ("occult", "high_risk", "theft"),
        "check_stats": ("intelligence", "agility"),
        "attribute_hints": ("knowledge", "insight"),
        "keywords": ("药剂", "炼金", "鉴定", "毒", "材料", "调剂", "器具"),
        "bonus": 2,
    },
}

GOD_STARTING_TALENTS = {
    "海洋之神": ["潮汐感应"],
    "真理之神": ["证词敏感"],
    "战争之神": ["军势直觉"],
    "审判之神": ["誓言感知"],
    "丰饶之神": ["生命嗅觉"],
    "死亡之神": ["临终残响"],
    "隐秘之神": ["影中低语"],
    "深渊之神": ["深渊回声"],
}

GOD_STARTING_PRAYERS = {
    "海洋之神": ["平潮祷告"],
    "真理之神": ["白塔明证"],
    "战争之神": ["铁血号令"],
    "审判之神": ["审判钟声"],
    "丰饶之神": ["蔷薇复苏"],
    "死亡之神": ["安魂"],
    "隐秘之神": ["无声祈祷"],
    "深渊之神": ["深渊低语"],
}

GOD_TALENT_DEFINITIONS = {
    "潮汐感应": {
        "god": "海洋之神",
        "description": "感知潮汐、航线、沉船传闻和水域异常的细微变化。",
        "risk_types": ("travel", "occult", "high_risk"),
        "check_stats": ("intelligence", "faith", "agility"),
        "attribute_hints": ("insight", "communion"),
        "keywords": ("海", "潮", "水", "船", "港", "码头", "航线", "风暴", "沉船"),
        "bonus": 1,
    },
    "证词敏感": {
        "god": "真理之神",
        "description": "更容易察觉证词、记录、印章和公开声明里的裂缝。",
        "risk_types": ("social", "occult", "high_risk"),
        "check_stats": ("intelligence", "faith"),
        "attribute_hints": ("insight", "knowledge"),
        "keywords": ("证词", "谎言", "记录", "印章", "真相", "审问", "报纸", "档案"),
        "bonus": 1,
    },
    "军势直觉": {
        "god": "战争之神",
        "description": "感知队列、伏击、火力、士气和暴力升级的方向。",
        "risk_types": ("violence", "high_risk", "escape"),
        "check_stats": ("strength", "intelligence", "agility"),
        "attribute_hints": ("physique", "insight"),
        "keywords": ("军", "守卫", "队列", "伏击", "战斗", "士兵", "火力", "阵地"),
        "bonus": 1,
    },
    "誓言感知": {
        "god": "审判之神",
        "description": "面对契约、誓言、判决和法律秩序时，更容易发现违誓痕迹。",
        "risk_types": ("social", "occult", "high_risk"),
        "check_stats": ("intelligence", "faith"),
        "attribute_hints": ("will", "insight"),
        "keywords": ("誓言", "契约", "判决", "审判", "法庭", "证词", "通行证", "罪"),
        "bonus": 1,
    },
    "生命嗅觉": {
        "god": "丰饶之神",
        "description": "感知生命、病症、药草、过度生长和身体异常。",
        "risk_types": ("occult", "social", "high_risk"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("communion", "insight"),
        "keywords": ("生命", "疾病", "伤口", "血", "花", "药", "蔷薇", "生长", "腐烂"),
        "bonus": 1,
    },
    "临终残响": {
        "god": "死亡之神",
        "description": "在死亡现场、墓地、遗嘱和亡者痕迹旁听见残留秩序。",
        "risk_types": ("occult", "social", "high_risk"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("will", "communion"),
        "keywords": ("死亡", "亡者", "尸体", "墓", "遗嘱", "葬礼", "安魂", "死者"),
        "bonus": 1,
    },
    "影中低语": {
        "god": "隐秘之神",
        "description": "更容易察觉暗号、假身份、被隐藏的入口和沉默里的信息。",
        "risk_types": ("stealth", "theft", "social", "high_risk"),
        "check_stats": ("agility", "intelligence"),
        "attribute_hints": ("agility", "insight"),
        "keywords": ("秘密", "暗号", "隐藏", "假身份", "夜", "阴影", "档案", "无声"),
        "bonus": 1,
    },
    "深渊回声": {
        "god": "深渊之神",
        "description": "听见梦境、黑水、裂缝和禁忌知识里不该稳定存在的回声。",
        "risk_types": ("occult", "high_risk"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("communion", "knowledge"),
        "keywords": ("深渊", "梦", "黑水", "污染", "裂缝", "禁忌", "低语", "梦魇"),
        "bonus": 1,
    },
}

GOD_PRAYER_DEFINITIONS = {
    "平潮祷告": {
        "god": "海洋之神",
        "description": "请求潮汐短暂平稳，用于航行、水域异常和风暴压力。",
        "risk_types": ("travel", "occult", "high_risk"),
        "check_stats": ("faith", "intelligence", "agility"),
        "attribute_hints": ("communion", "insight"),
        "keywords": ("平潮祷告", "平潮", "潮汐", "风暴", "航线", "沉船", "海"),
        "bonus": 3,
        "favor_cost": 1,
    },
    "白塔明证": {
        "god": "真理之神",
        "description": "请求真理秩序照见证词和记录中的关键矛盾。",
        "risk_types": ("social", "occult", "high_risk"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("knowledge", "insight"),
        "keywords": ("白塔明证", "明证", "证词", "真相", "谎言", "记录", "档案"),
        "bonus": 3,
        "favor_cost": 1,
    },
    "铁血号令": {
        "god": "战争之神",
        "description": "请求战争秩序稳住士气、压制恐惧或把混乱推向可控对抗。",
        "risk_types": ("violence", "high_risk", "escape"),
        "check_stats": ("faith", "strength", "intelligence"),
        "attribute_hints": ("will", "physique"),
        "keywords": ("铁血号令", "号令", "战斗", "士气", "守卫", "军", "压制"),
        "bonus": 3,
        "favor_cost": 1,
    },
    "审判钟声": {
        "god": "审判之神",
        "description": "请求审判秩序压制混乱，让契约、罪责或回答变得沉重。",
        "risk_types": ("social", "occult", "high_risk"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("will", "insight"),
        "keywords": ("审判钟声", "钟声", "审判", "契约", "誓言", "罪", "判决"),
        "bonus": 3,
        "favor_cost": 1,
    },
    "蔷薇复苏": {
        "god": "丰饶之神",
        "description": "请求生命秩序稳定伤势、病症或过度生长的异常。",
        "risk_types": ("occult", "high_risk", "social"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("communion", "will"),
        "keywords": ("蔷薇复苏", "复苏", "蔷薇", "生命", "伤口", "疾病", "药"),
        "bonus": 3,
        "favor_cost": 1,
    },
    "安魂": {
        "god": "死亡之神",
        "description": "请求死亡秩序平复亡者、墓地、遗嘱或死亡现场的回响。",
        "risk_types": ("occult", "social", "high_risk"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("will", "communion"),
        "keywords": ("安魂", "死亡", "亡者", "墓", "遗嘱", "尸体", "葬礼"),
        "bonus": 3,
        "favor_cost": 1,
    },
    "无声祈祷": {
        "god": "隐秘之神",
        "description": "请求隐秘秩序降低存在感，遮住一次行动的边缘痕迹。",
        "risk_types": ("stealth", "theft", "escape", "high_risk"),
        "check_stats": ("faith", "agility", "intelligence"),
        "attribute_hints": ("agility", "insight"),
        "keywords": ("无声祈祷", "无声", "隐秘", "隐藏", "暗号", "假身份", "阴影"),
        "bonus": 3,
        "favor_cost": 1,
    },
    "深渊低语": {
        "god": "深渊之神",
        "description": "请求深渊回声短暂回应梦境、污染、黑水或禁忌裂缝。",
        "risk_types": ("occult", "high_risk"),
        "check_stats": ("faith", "intelligence"),
        "attribute_hints": ("communion", "knowledge"),
        "keywords": ("深渊低语", "低语", "深渊", "梦", "黑水", "污染", "裂缝"),
        "bonus": 3,
        "favor_cost": 1,
    },
}


def initial_progression_for(class_id, god):
    """Build a conservative Phase 8 progression baseline."""
    talents = list(GOD_STARTING_TALENTS.get(god, []))
    prayers = list(GOD_STARTING_PRAYERS.get(god, []))
    progression_skills = list(CLASS_STARTING_SKILLS.get(class_id, []))
    return {
        "class_level": DEFAULT_CLASS_LEVEL,
        "faith_level": DEFAULT_FAITH_LEVEL,
        "ascension_rank": DEFAULT_ASCENSION_RANK,
        "revelation": DEFAULT_REVELATION,
        "favor": starting_favor_for(god),
        "devotion": DEFAULT_DEVOTION,
        "progression_skills": progression_skills,
        "talents": talents,
        "prayers": prayers,
        "burdens": list(DEFAULT_BURDENS),
        "progression_flags": dict(DEFAULT_PROGRESSION_FLAGS),
    }


def initial_attributes_for(class_id):
    return dict(CLASS_STARTING_ATTRIBUTES.get(class_id, DEFAULT_ATTRIBUTES))


def starting_favor_for(god):
    return 1 if god else 0


def normalize_progression_payload(data, class_id, god):
    """Read progression from new or old saves and fill missing fields."""
    progression = initial_progression_for(class_id, god)
    if not data:
        return progression

    for key in (
        "class_level",
        "faith_level",
        "ascension_rank",
        "revelation",
        "favor",
        "devotion",
    ):
        progression[key] = normalize_int(data.get(key, progression[key]), progression[key])

    progression["progression_skills"] = normalize_list(
        data.get("progression_skills", progression["progression_skills"])
    )
    progression["talents"] = normalize_list(data.get("talents", progression["talents"]))
    progression["prayers"] = normalize_list(data.get("prayers", progression["prayers"]))
    progression["burdens"] = normalize_list(data.get("burdens", progression["burdens"]))
    progression["progression_flags"] = dict(
        data.get("progression_flags", progression["progression_flags"]) or {}
    )
    return progression


def normalize_attributes_payload(data, class_id):
    attributes = initial_attributes_for(class_id)
    if not data:
        return attributes
    for key in ATTRIBUTE_NAMES:
        attributes[key] = clamp_attribute(normalize_int(data.get(key, attributes[key]), attributes[key]))
    return attributes


def progression_to_dict(character):
    return {
        "class_level": character.class_level,
        "faith_level": character.faith_level,
        "ascension_rank": character.ascension_rank,
        "revelation": character.revelation,
        "favor": character.favor,
        "devotion": character.devotion,
        "progression_skills": list(character.progression_skills),
        "skill_affordances": skill_affordances_for(character),
        "talents": list(character.talents),
        "talent_affordances": talent_affordances_for(character),
        "prayers": list(character.prayers),
        "prayer_affordances": prayer_affordances_for(character),
        "advancement_options": advancement_options_for(character),
        "burdens": list(character.burdens),
        "progression_flags": dict(character.progression_flags),
    }


def skill_affordances_for(character):
    return [
        compact_skill_definition(definition)
        for definition in learned_class_skill_definitions(character)
    ]


def learned_class_skill_definitions(character):
    learned = set(character.progression_skills)
    definitions = []
    for skill_name in character.progression_skills:
        definition = CLASS_SKILL_DEFINITIONS.get(skill_name)
        if not definition:
            continue
        if definition["class_id"] != character.class_id:
            continue
        if skill_name not in learned:
            continue
        definitions.append({"name": skill_name, **definition})
    return definitions


def matching_class_skill_bonuses(character, risk_type, stat, rule_action=None):
    """Return learned class skills that can help this adjudicated check.

    The primary match is the broad adjudicated risk/stat, not a growing list of
    player-input keywords. Keywords only help borderline generic checks such as
    high_risk until Phase 8.4 moves checks fully onto the six-attribute model.
    """
    action_text = action_text_for_skill_match(rule_action or {})
    matches = []
    for definition in learned_class_skill_definitions(character):
        if class_skill_matches(definition, risk_type, stat, action_text):
            matches.append(
                {
                    "name": definition["name"],
                    "bonus": definition["bonus"],
                    "description": definition["description"],
                }
            )
    return matches


def detect_advancement_request(rule_action):
    text = action_text_for_skill_match(rule_action or {})
    if not contains_advancement_language(text):
        return None
    if contains_any(text, ("阶位", "神秘晋升", "仪式晋升", "超凡", "突破阶位", "见证者")):
        return "ascension_rank"
    if contains_any(text, ("信仰", "神恩", "神眷", "虔诚", "祷告晋升")):
        return "faith_level"
    if contains_any(text, ("职业", "训练", "技艺", "技能", "骑士", "法师", "密探", "游侠", "牧师", "炼金")):
        return "class_level"
    return "class_level"


def contains_advancement_language(text):
    return contains_any(text, ("晋升", "升级", "提升", "训练", "进阶", "变强", "突破阶位"))


def evaluate_advancement(character, advancement_type):
    config = ADVANCEMENT_TYPES.get(advancement_type)
    if not config:
        return {
            "type": advancement_type,
            "label": "未知成长",
            "can_advance": False,
            "requirements": [],
            "costs": {},
            "rewards": [],
            "denied_reasons": ("unsupported_advancement_type",),
        }

    requirements = advancement_requirements(character, advancement_type, config)
    denied_reasons = tuple(requirement["reason"] for requirement in requirements if not requirement["ok"])
    return {
        "type": advancement_type,
        "label": config["label"],
        "can_advance": not denied_reasons,
        "requirements": requirements,
        "costs": advancement_costs(config),
        "rewards": advancement_rewards(character, advancement_type, config),
        "denied_reasons": denied_reasons,
    }


def apply_advancement(character, advancement_type):
    evaluation = evaluate_advancement(character, advancement_type)
    if not evaluation["can_advance"]:
        return evaluation

    costs = evaluation["costs"]
    if costs.get("revelation"):
        character.revelation -= costs["revelation"]
    if costs.get("favor"):
        character.favor -= costs["favor"]

    state_changes = []
    if advancement_type == "class_level":
        before = character.class_level
        character.class_level = 2
        state_changes.append(f"职业等级 {before} -> {character.class_level}")
        attribute_name = CLASS_ADVANCEMENT_ATTRIBUTES.get(character.class_id, "insight")
        attribute_label = ATTRIBUTE_LABELS.get(attribute_name, attribute_name)
        before_attr = character.attributes.get(attribute_name, 10)
        character.attributes[attribute_name] = clamp_attribute(before_attr + 1)
        state_changes.append(f"{attribute_label} +1（职业训练）")
    elif advancement_type == "faith_level":
        before = character.faith_level
        character.faith_level = 2
        character.devotion += 1
        state_changes.append(f"信仰等级 {before} -> {character.faith_level}")
        state_changes.append("Devotion +1（信仰深化）")
    elif advancement_type == "ascension_rank":
        before = character.ascension_rank
        character.ascension_rank = 1
        burden = ADVANCEMENT_TYPES["ascension_rank"]["burden"]
        if burden not in character.burdens:
            character.burdens.append(burden)
        state_changes.append(f"神秘阶位 {before} -> {character.ascension_rank}")
        state_changes.append(f"新增代价：{burden}")

    if costs.get("revelation"):
        state_changes.append(f"Revelation -{costs['revelation']}（成长消耗）")
    if costs.get("favor"):
        state_changes.append(f"Favor -{costs['favor']}（仪式消耗）")

    character.progression_flags["last_advancement"] = {
        "type": advancement_type,
        "label": evaluation["label"],
        "target_level": ADVANCEMENT_TYPES[advancement_type]["target_level"],
    }
    evaluation["state_changes"] = state_changes
    evaluation["committed"] = True
    return evaluation


def advancement_options_for(character):
    return [
        compact_advancement_evaluation(evaluate_advancement(character, advancement_type))
        for advancement_type in ("class_level", "faith_level", "ascension_rank")
    ]


def compact_advancement_evaluation(evaluation):
    return {
        "type": evaluation["type"],
        "label": evaluation["label"],
        "can_advance": evaluation["can_advance"],
        "requirements": [dict(requirement) for requirement in evaluation["requirements"]],
        "costs": dict(evaluation["costs"]),
        "rewards": [dict(reward) for reward in evaluation["rewards"]],
        "denied_reasons": list(evaluation["denied_reasons"]),
    }


def advancement_requirements(character, advancement_type, config):
    requirements = []
    if advancement_type == "class_level":
        requirements.append(requirement("class_level", character.class_level, 1, character.class_level == 1, "already_at_or_above_demo_cap"))
    elif advancement_type == "faith_level":
        requirements.append(requirement("faith_level", character.faith_level, 1, character.faith_level == 1, "already_at_or_above_demo_cap"))
    elif advancement_type == "ascension_rank":
        requirements.append(requirement("ascension_rank", character.ascension_rank, 0, character.ascension_rank == 0, "already_ascended"))
        requirements.append(
            requirement(
                "class_level",
                character.class_level,
                config["required_class_level"],
                character.class_level >= config["required_class_level"],
                "class_level_too_low",
            )
        )
        requirements.append(
            requirement(
                "faith_level",
                character.faith_level,
                config["required_faith_level"],
                character.faith_level >= config["required_faith_level"],
                "faith_level_too_low",
            )
        )

    revelation_cost = config.get("revelation_cost", 0)
    if revelation_cost:
        requirements.append(
            requirement(
                "revelation",
                character.revelation,
                revelation_cost,
                character.revelation >= revelation_cost,
                "revelation_not_enough",
            )
        )

    favor_cost = config.get("favor_cost", 0)
    if favor_cost:
        requirements.append(
            requirement(
                "favor",
                character.favor,
                favor_cost,
                character.favor >= favor_cost,
                "favor_not_enough",
            )
        )
    return requirements


def requirement(field, current, required, ok, reason):
    return {
        "field": field,
        "current": current,
        "required": required,
        "ok": ok,
        "reason": reason,
    }


def advancement_costs(config):
    costs = {}
    if config.get("revelation_cost"):
        costs["revelation"] = config["revelation_cost"]
    if config.get("favor_cost"):
        costs["favor"] = config["favor_cost"]
    return costs


def advancement_rewards(character, advancement_type, config):
    if advancement_type == "class_level":
        attribute_name = CLASS_ADVANCEMENT_ATTRIBUTES.get(character.class_id, "insight")
        return [
            {
                "type": "level",
                "field": "class_level",
                "value": config["target_level"],
            },
            {
                "type": "attribute",
                "field": attribute_name,
                "label": ATTRIBUTE_LABELS.get(attribute_name, attribute_name),
                "value": 1,
            },
        ]
    if advancement_type == "faith_level":
        return [
            {
                "type": "level",
                "field": "faith_level",
                "value": config["target_level"],
            },
            {
                "type": "resource",
                "field": "devotion",
                "value": 1,
            },
        ]
    if advancement_type == "ascension_rank":
        return [
            {
                "type": "level",
                "field": "ascension_rank",
                "value": config["target_level"],
            },
            {
                "type": "burden",
                "value": config["burden"],
            },
        ]
    return []


def world_attribute_profile_for(character, risk_type, stat):
    profile = (
        WORLD_CHECK_ATTRIBUTE_PROFILES.get((risk_type, stat))
        or WORLD_CHECK_ATTRIBUTE_PROFILES.get(("high_risk", stat))
        or fallback_attribute_profile(stat)
    )
    primary = profile["primary_attribute"]
    value = clamp_attribute(normalize_int(character.attributes.get(primary, 10), 10))
    modifier = attribute_modifier(value)
    return {
        "label": profile["label"],
        "primary_attribute": primary,
        "primary_label": ATTRIBUTE_LABELS.get(primary, primary),
        "primary_value": value,
        "modifier": modifier,
        "secondary_attributes": list(profile.get("secondary_attributes", ())),
        "secondary_labels": [
            ATTRIBUTE_LABELS.get(attribute, attribute)
            for attribute in profile.get("secondary_attributes", ())
        ],
    }


def fallback_attribute_profile(stat):
    if stat == "strength":
        return {
            "primary_attribute": "physique",
            "secondary_attributes": ("will",),
            "label": "力量兼容检定",
        }
    if stat == "agility":
        return {
            "primary_attribute": "agility",
            "secondary_attributes": ("insight",),
            "label": "敏捷兼容检定",
        }
    if stat == "faith":
        return {
            "primary_attribute": "communion",
            "secondary_attributes": ("will",),
            "label": "信仰兼容检定",
        }
    return {
        "primary_attribute": "knowledge",
        "secondary_attributes": ("insight",),
        "label": "智力兼容检定",
    }


def attribute_modifier(value):
    value = clamp_attribute(normalize_int(value, 10))
    return (value - 10) // 2


def talent_affordances_for(character):
    return [
        compact_faith_definition(definition)
        for definition in learned_talent_definitions(character)
    ]


def prayer_affordances_for(character):
    return [
        compact_faith_definition(definition, include_cost=True)
        for definition in learned_prayer_definitions(character)
    ]


def learned_talent_definitions(character):
    return learned_faith_definitions(
        character.talents,
        character.god,
        GOD_TALENT_DEFINITIONS,
    )


def learned_prayer_definitions(character):
    return learned_faith_definitions(
        character.prayers,
        character.god,
        GOD_PRAYER_DEFINITIONS,
    )


def learned_faith_definitions(names, god, definition_map):
    definitions = []
    for name in names:
        definition = definition_map.get(name)
        if not definition:
            continue
        if definition["god"] != god:
            continue
        definitions.append({"name": name, **definition})
    return definitions


def matching_faith_talent_bonuses(character, risk_type, stat, rule_action=None):
    action_text = action_text_for_skill_match(rule_action or {})
    matches = []
    for definition in learned_talent_definitions(character):
        if faith_definition_matches(definition, risk_type, stat, action_text):
            matches.append(
                {
                    "name": definition["name"],
                    "bonus": definition["bonus"],
                    "description": definition["description"],
                }
            )
    return matches


def matching_prayer_bonuses(character, risk_type, stat, rule_action=None):
    action_text = action_text_for_skill_match(rule_action or {})
    matches = []
    for definition in learned_prayer_definitions(character):
        if not prayer_was_invoked(definition, character, action_text):
            continue
        if faith_definition_matches(definition, risk_type, stat, action_text):
            matches.append(
                {
                    "name": definition["name"],
                    "bonus": definition["bonus"],
                    "favor_cost": definition["favor_cost"],
                    "description": definition["description"],
                }
            )
    return matches


def faith_definition_matches(definition, risk_type, stat, action_text):
    risk_match = risk_type in definition["risk_types"]
    stat_match = not definition["check_stats"] or stat in definition["check_stats"]
    keyword_match = any(keyword in action_text for keyword in definition["keywords"])
    if risk_match and stat_match:
        return True
    if keyword_match and (risk_match or stat_match):
        return True
    return False


def contains_any(text, terms):
    return any(term in text for term in terms)


def prayer_was_invoked(definition, character, action_text):
    invocation_terms = (
        definition["name"],
        character.god,
        "祷告",
        "祈祷",
        "祈求",
        "呼唤",
        "念诵",
        "圣徽",
    )
    return any(term and term in action_text for term in invocation_terms)


def class_skill_matches(definition, risk_type, stat, action_text):
    risk_match = risk_type in definition["risk_types"]
    stat_match = not definition["check_stats"] or stat in definition["check_stats"]
    if risk_match and stat_match:
        return True

    keyword_match = any(keyword in action_text for keyword in definition["keywords"])
    if keyword_match and (risk_match or stat_match):
        return True

    return False


def action_text_for_skill_match(rule_action):
    parts = [
        rule_action.get("raw_text", ""),
        rule_action.get("target", ""),
        rule_action.get("method", ""),
        rule_action.get("open_primary_goal", ""),
        rule_action.get("target_profile", ""),
        rule_action.get("success_consequence", ""),
        rule_action.get("failure_consequence", ""),
        " ".join(rule_action.get("possible_blockers", []) or []),
    ]
    return " ".join(str(part) for part in parts if part)


def compact_skill_definition(definition):
    return {
        "name": definition["name"],
        "description": definition["description"],
        "bonus": definition["bonus"],
        "risk_types": list(definition["risk_types"]),
        "check_stats": list(definition["check_stats"]),
        "attribute_hints": list(definition["attribute_hints"]),
    }


def compact_faith_definition(definition, include_cost=False):
    compact = {
        "name": definition["name"],
        "god": definition["god"],
        "description": definition["description"],
        "bonus": definition["bonus"],
        "risk_types": list(definition["risk_types"]),
        "check_stats": list(definition["check_stats"]),
        "attribute_hints": list(definition["attribute_hints"]),
    }
    if include_cost:
        compact["favor_cost"] = definition["favor_cost"]
    return compact


def clamp_attribute(value):
    return max(1, min(22, value))


def normalize_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def normalize_list(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]
