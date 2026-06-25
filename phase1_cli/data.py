"""Static game data for 神座纪元 v6.0.0.

This file is intentionally plain dictionaries and lists. Later phases can move
the same data into JSON files, PostgreSQL rows, or a RAG knowledge base.
"""

PROJECT_NAME = "神座纪元"
PROJECT_ENGLISH_NAME = "Pantheon Age"
PROJECT_VERSION = "6.0.0"
PROJECT_INTERNAL_MILESTONE = "Phase 6"
PROJECT_STAGE = "World Knowledge And Persistent Memory"

BASE_STATS = {
    "strength": 5,
    "agility": 5,
    "intelligence": 5,
    "faith": 5,
}

BASE_HP = 20
BASE_SAN = 10

STAT_NAMES = {
    "strength": "力量",
    "agility": "敏捷",
    "intelligence": "智力",
    "faith": "信仰",
}

DIFFICULTY = {
    "easy": 10,
    "normal": 14,
    "hard": 18,
    "danger": 22,
}

GODS = [
    "海洋之神",
    "真理之神",
    "战争之神",
    "审判之神",
    "丰饶之神",
    "死亡之神",
    "隐秘之神",
    "深渊之神",
]

CLASSES = {
    "warrior": {
        "class_id": "warrior",
        "name": "骑士",
        "english_name": "Knight",
        "description": "擅长正面战斗、护卫、决斗礼仪和力量检定的职业。",
        "stat_bonus": {
            "strength": 3,
            "agility": 1,
            "intelligence": 0,
            "faith": 0,
        },
        "hp_bonus": 5,
        "san_bonus": 0,
        "starting_items": ["制式佩剑", "旧式手盾"],
        "skill_tags": ["attack", "guard", "force"],
        "rule_modifiers": {
            "attack_bonus": 2,
            "guard_bonus": 2,
            "force_bonus": 2,
            "lore_penalty": -1,
        },
    },
    "mage": {
        "class_id": "mage",
        "name": "法师",
        "english_name": "Mage",
        "description": "擅长魔法、仪式、异常解析和神秘知识的职业。",
        "stat_bonus": {
            "strength": 0,
            "agility": 0,
            "intelligence": 3,
            "faith": 1,
        },
        "hp_bonus": -2,
        "san_bonus": 1,
        "starting_items": ["破旧法术书", "仪式粉末"],
        "skill_tags": ["analyze", "ritual", "lore", "magic"],
        "rule_modifiers": {
            "analyze_bonus": 2,
            "ritual_bonus": 2,
            "lore_bonus": 2,
            "forbidden_knowledge_san_risk": 1,
        },
    },
    "rogue": {
        "class_id": "rogue",
        "name": "密探",
        "english_name": "Operative",
        "description": "擅长潜行、开锁、偷听、伪装和获取地下情报的职业。",
        "stat_bonus": {
            "strength": 0,
            "agility": 3,
            "intelligence": 1,
            "faith": 0,
        },
        "hp_bonus": 0,
        "san_bonus": 0,
        "starting_items": ["开锁工具", "假名证件"],
        "skill_tags": ["stealth", "lockpick", "deceive", "listen"],
        "rule_modifiers": {
            "stealth_bonus": 2,
            "lockpick_bonus": 2,
            "deceive_bonus": 2,
            "suspicion_risk": 1,
            "direct_combat_penalty": -1,
        },
    },
    "hunter": {
        "class_id": "hunter",
        "name": "游侠",
        "english_name": "Ranger",
        "description": "擅长追踪、侦察、生存、远程武器和陷阱识别的职业。",
        "stat_bonus": {
            "strength": 1,
            "agility": 2,
            "intelligence": 1,
            "faith": 0,
        },
        "hp_bonus": 2,
        "san_bonus": 0,
        "starting_items": ["猎刀", "简易陷阱"],
        "skill_tags": ["track", "survival", "trap_detect", "scout"],
        "rule_modifiers": {
            "track_bonus": 2,
            "survival_bonus": 2,
            "trap_detect_bonus": 2,
            "ritual_penalty": -1,
        },
    },
    "priest": {
        "class_id": "priest",
        "name": "牧师",
        "english_name": "Priest",
        "description": "擅长祈祷、治疗、净化、安魂和抵抗污染的职业。",
        "stat_bonus": {
            "strength": 0,
            "agility": 0,
            "intelligence": 1,
            "faith": 3,
        },
        "hp_bonus": 1,
        "san_bonus": 2,
        "starting_items": ["圣徽", "小瓶圣水"],
        "skill_tags": ["pray", "heal", "purify", "spirit"],
        "rule_modifiers": {
            "pray_bonus": 2,
            "heal_bonus": 2,
            "purify_bonus": 2,
            "corruption_resistance": 1,
            "deceive_penalty": -1,
        },
    },
    "alchemist": {
        "class_id": "alchemist",
        "name": "炼金术士",
        "english_name": "Alchemist",
        "description": "擅长药剂、鉴定、制作、毒素和道具使用的职业。",
        "stat_bonus": {
            "strength": 0,
            "agility": 1,
            "intelligence": 2,
            "faith": 1,
        },
        "hp_bonus": 0,
        "san_bonus": 0,
        "starting_items": ["止血药剂", "镇静药剂", "炼金工具包"],
        "skill_tags": ["use_item", "identify", "craft", "medicine", "poison"],
        "rule_modifiers": {
            "use_item_bonus": 2,
            "identify_bonus": 2,
            "craft_bonus": 2,
            "medicine_bonus": 1,
            "combat_penalty": -1,
        },
    },
}

LOCATIONS = {
    "修道院门口": ["前厅"],
    "前厅": ["修道院门口", "祈祷大厅", "旧档案室"],
    "祈祷大厅": ["前厅", "钟楼"],
    "旧档案室": ["前厅", "地下墓室"],
    "钟楼": ["祈祷大厅"],
    "地下墓室": ["旧档案室"],
}

LOCATION_DESCRIPTIONS = {
    "修道院门口": "浓雾封住了来路，铁门半开，泥地上似乎有杂乱的脚印。",
    "前厅": "前厅布满灰尘，破碎的长椅倒在两侧，墙上残留着旧日圣徽。",
    "祈祷大厅": "大厅中央的祭坛已经开裂，空气中有淡淡的蜡油和霉味。",
    "旧档案室": "档案柜倾倒在地，许多纸页被撕碎，角落里有被火烧过的痕迹。",
    "钟楼": "钟楼顶部悬着一口生锈的大钟，但它似乎并不需要人敲就会响起。",
    "地下墓室": "冰冷的墓室里排列着无名石棺，黑暗中仿佛有人在低语。",
}

LOCATION_ALIASES = {
    "修道院门口": "修道院门口",
    "门口": "修道院门口",
    "铁门": "修道院门口",
    "前厅": "前厅",
    "祈祷大厅": "祈祷大厅",
    "大厅": "祈祷大厅",
    "祭坛": "祈祷大厅",
    "旧档案室": "旧档案室",
    "档案室": "旧档案室",
    "档案柜": "旧档案室",
    "钟楼": "钟楼",
    "大钟": "钟楼",
    "地下墓室": "地下墓室",
    "墓室": "地下墓室",
    "石棺": "地下墓室",
}

CLUE_DESCRIPTIONS = {
    "泥泞脚印": "脚印从门口延伸向前厅，数量比失踪名单上的人更多。",
    "破损圣徽": "圣徽背面刻着被匆忙划掉的名字，像是某种集体誓约。",
    "被撕掉的档案页": "档案页记录了修道院曾长期收留迷雾中的失踪者。",
    "说谎时响起的钟声": "钟声似乎会回应谎言，像某种古老审判仪式。",
    "修女失踪名单": "名单上的修女并非同时失踪，而是按仪式日期逐个消失。",
    "地下墓室的亡者残响": "亡者低语提到：真正的门不在地上，而在钟声背后。",
    "深渊污染痕迹": "黑色痕迹不像血，更像从现实裂缝里渗出的梦魇。",
}

CORE_TRUTH_CLUES = {
    "被撕掉的档案页",
    "说谎时响起的钟声",
    "修女失踪名单",
    "地下墓室的亡者残响",
    "深渊污染痕迹",
}

MAIN_OBJECTIVE = "探索雾中修道院，收集至少 4 个核心线索，避免 SAN 归零或污染过高。"

ITEMS = {
    "制式佩剑": {
        "description": "旧军制式佩剑，剑身有磨痕，但仍适合近身战斗和正式决斗。",
        "consumable": False,
    },
    "旧式手盾": {
        "description": "边缘开裂的手盾，可以在近身冲突中提供一点安全感。",
        "consumable": False,
    },
    "破旧法术书": {
        "description": "写满批注的法术书，适合研究异常符号。",
        "consumable": False,
    },
    "仪式粉末": {
        "description": "可撒在地面显露短暂的仪式纹路。",
        "consumable": True,
    },
    "开锁工具": {
        "description": "一套细小工具，适合打开旧锁和卡死的抽屉。",
        "consumable": False,
    },
    "暗色斗篷": {
        "description": "在昏暗空间里能降低存在感。",
        "consumable": False,
    },
    "假名证件": {
        "description": "一份做旧的假名证件，适合应付粗略盘问，但经不起正式审查。",
        "consumable": False,
    },
    "猎刀": {
        "description": "短而可靠的猎刀，适合防身和切割绳索。",
        "consumable": False,
    },
    "简易陷阱": {
        "description": "临时陷阱材料，可以拖慢危险的黑影。",
        "consumable": True,
    },
    "圣徽": {
        "description": "神职者的圣徽，在祈祷和净化时很有用。",
        "consumable": False,
    },
    "小瓶圣水": {
        "description": "可短暂压制污染的圣水。",
        "consumable": True,
    },
    "止血药剂": {
        "description": "恢复 4 点 HP，炼金术士使用时额外恢复 1 点。",
        "consumable": True,
    },
    "镇静药剂": {
        "description": "恢复 2 点 SAN，炼金术士使用时额外恢复 1 点。",
        "consumable": True,
    },
    "炼金工具包": {
        "description": "鉴定异常物质和药剂时会派上用场。",
        "consumable": False,
    },
}

ITEM_ALIASES = {
    "制式佩剑": "制式佩剑",
    "佩剑": "制式佩剑",
    "旧长剑": "制式佩剑",
    "长剑": "制式佩剑",
    "剑": "制式佩剑",
    "旧式手盾": "旧式手盾",
    "手盾": "旧式手盾",
    "木盾": "旧式手盾",
    "盾": "旧式手盾",
    "破旧法术书": "破旧法术书",
    "法术书": "破旧法术书",
    "仪式粉末": "仪式粉末",
    "粉末": "仪式粉末",
    "开锁工具": "开锁工具",
    "工具": "开锁工具",
    "暗色斗篷": "暗色斗篷",
    "斗篷": "暗色斗篷",
    "假名证件": "假名证件",
    "证件": "假名证件",
    "假证": "假名证件",
    "猎刀": "猎刀",
    "简易陷阱": "简易陷阱",
    "陷阱": "简易陷阱",
    "圣徽": "圣徽",
    "小瓶圣水": "小瓶圣水",
    "圣水": "小瓶圣水",
    "止血药剂": "止血药剂",
    "止血": "止血药剂",
    "镇静药剂": "镇静药剂",
    "镇静": "镇静药剂",
    "炼金工具包": "炼金工具包",
}

INTENT_KEYWORDS = {
    "investigate": ["调查", "检查", "搜索", "查看", "寻找"],
    "move": ["去", "进入", "前往", "走向", "离开", "返回", "回到"],
    "attack": ["攻击", "砍", "打", "射击", "刺"],
    "pray": ["祈祷", "祷告", "向神明", "圣徽", "净化", "安魂"],
    "rest": ["休息", "睡", "恢复"],
    "use_item": ["使用", "喝下", "拿出", "服用"],
    "stealth": ["潜行", "悄悄", "偷听", "撬开", "开锁"],
    "talk": ["询问", "交谈", "说服", "对话"],
    "analyze": ["分析", "解读", "研究", "辨认", "鉴定"],
}

POLLUTION_KEYWORDS = ["黑色液体", "深渊", "污染", "黑色痕迹", "梦魇"]

ENDINGS = {
    "ordinary_escape": "你逃离了修道院，但真相仍被浓雾吞没。多年以后，你仍会在梦里听见那口钟。",
    "truth_revealed": "你拼凑出了修道院失踪案的真相：钟声、档案、名单与墓室低语共同指向一场失败的深渊仪式。",
    "abyss_corruption": "你听见了钟声背后的低语。雾从你的影子里升起，从此你再也无法离开雾中修道院。",
    "fallen": "你的意识沉入冰冷地面。雾中修道院没有杀死你，它只是把你留下了。",
}

HELP_TEXT = """支持的行动示例：
- 移动：进入前厅 / 前往旧档案室 / 返回修道院门口
- 调查：调查脚印 / 检查档案柜 / 搜索钟楼
- 分析：分析符文 / 鉴定黑色液体
- 战斗：攻击黑影
- 祈祷：向死亡之神祈祷 / 净化污染
- 潜行：悄悄撬开档案柜 / 偷听
- 道具：使用止血药剂 / 喝下镇静药剂 / 使用圣水
- 休息：休息一下
- 查看：目标 / 线索 / 地图 / 日志 / 状态
- 系统：帮助 / 存档 / 读档 / 退出
"""
