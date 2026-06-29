"""Fixed story text for 神座纪元 v8.7.0.

Later, an LLM can replace or enrich this module, but it should still receive
rule results from rule_engine instead of deciding core state changes itself.
"""

from .data import (
    CLUE_DESCRIPTIONS,
    CORE_TRUTH_CLUES,
    HELP_TEXT,
    LOCATIONS,
    MAIN_OBJECTIVE,
    PROJECT_ENGLISH_NAME,
    PROJECT_INTERNAL_MILESTONE,
    PROJECT_NAME,
    PROJECT_STAGE,
    PROJECT_VERSION,
    STAT_NAMES,
)
from .items import item_affordances_for
from .progression import ATTRIBUTE_LABELS, advancement_options_for
from .scenarios import (
    WORLD_GAME_MODE,
    available_exits_for_state,
    current_scene_focus_for_state,
    describe_origin_city,
    game_mode_for_state,
    location_description_for_state,
    objective_for_state,
)


def render_title():
    return f"""============================================================
{PROJECT_NAME} / {PROJECT_ENGLISH_NAME} - v{PROJECT_VERSION} {PROJECT_INTERNAL_MILESTONE} {PROJECT_STAGE}
CLI Tutorial + Agentic World Mode
============================================================"""


def render_opening(character, game_mode=None):
    mode = game_mode or character.flags.get("game_mode")
    if mode == WORLD_GAME_MODE:
        origin_city = character.flags.get("origin_city", character.current_location)
        city_title = character.flags.get("origin_city_title", "")
        city_title_text = f"，“{city_title}”" if city_title else ""
        profile = character.flags.get("opening_profile") or {}
        suggested_actions = profile.get("suggested_actions") or (
            "观察附近人群，寻找第一个异常反应",
            "找一个愿意开口的人打听传闻",
            "前往本地教会或公共机构询问消息",
        )
        action_lines = "\n".join(f"- {action}" for action in suggested_actions[:4])
        return f"""
【开场】

世界尽头立着虚无之壁。现有文明无法越过边界，壁外是无尽虚空，也是外神低语传来的方向。

北大陆的蒸汽、铁路、报纸、银行和大学把现代秩序撑得很亮；八神教会、隐秘结社、旧贵族、商会寡头、军方和黑市则在阴影里争夺解释世界的权力。

汽笛声从雾和煤烟之间穿过，报童的叫卖、马车的轮声、教堂远处的钟声一层层压进清晨。你不是旁观者，你已经被卷到了第一处缝隙旁边。

你是{profile.get("identity_summary", character.name)}
职业：{character.class_name}。{profile.get("class_context", "")}
{profile.get("faith_context", f"你信仰{character.god}。")}
{profile.get("faith_sign", "")}
{profile.get("resource_context", "")}

此刻，你站在{origin_city}{city_title_text}。
{profile.get("city_context", describe_origin_city(character.flags.get("origin_country_id"), origin_city))}

【第一幕】
当前具体场景：{profile.get("scene_focus", character.flags.get("current_scene_focus") or f"{origin_city}的开放街区")}。
{profile.get("opening_incident", "一条没有来源的传闻穿过人群，像火星落进干草。")}
{profile.get("first_hook", "你来到这里并非偶然。某个细节正在等待你先开口。")}

你没有被固定剧情推着走。你可以顺着眼前的异常追下去，也可以绕开它，去找教会、码头、报社、市场、大学、车站或任何你觉得合理的入口。

可以直接对主持人说你要做什么，例如：
{action_lines}

输入“状态”查看角色状态，输入“帮助”查看基础命令。
"""

    return f"""
浓雾像潮水一样漫过铁门。
{character.name}，一名信仰{character.god}的{character.class_name}，踏入废弃的雾中修道院。

这里不会有大模型替你改写命运。
骰子、规则、状态和线索会决定你能否离开。
输入“帮助”可以查看行动示例。
"""


def render_status(state):
    player = state.player
    location = state.current_location
    inventory = ", ".join(player.inventory) if player.inventory else "空"
    clues = ", ".join(player.clues) if player.clues else "暂无"
    exits = ", ".join(available_exits_for_state(state)) or "由 Agent 根据当前行动临时生成"
    attributes = render_attribute_summary(player)
    class_skills = format_name_list(player.progression_skills)
    talents = format_name_list(player.talents)
    prayers = format_name_list(player.prayers)
    item_affordances = render_item_affordance_summary(player)
    advancement = render_advancement_summary(player)

    return f"""
------------------------------------------------------------
第 {state.turn + 1} 轮 | 位置：{location}
{location_description_for_state(state)}
可前往：{exits}

HP {player.hp}/{player.max_hp} | SAN {player.san}/{player.max_san} | Suspicion {player.suspicion} | Corruption {player.corruption}
职业等级 {player.class_level} | 信仰等级 {player.faith_level} | 神秘阶位 {player.ascension_rank} | Favor {player.favor} | Revelation {player.revelation}
六属性：{attributes}
职业技能：{class_skills}
信仰天赋：{talents}
祷告：{prayers}
可用道具：{item_affordances}
晋升状态：{advancement}
背包：{inventory}
线索：{clues}
------------------------------------------------------------"""


def render_attribute_summary(player):
    parts = []
    for key in ("physique", "agility", "insight", "knowledge", "will", "communion"):
        label = ATTRIBUTE_LABELS.get(key, key)
        parts.append(f"{label} {player.attributes.get(key, 10)}")
    return " / ".join(parts)


def render_item_affordance_summary(player):
    affordances = item_affordances_for(player)
    if not affordances:
        return "暂无"
    parts = []
    for item in affordances[:4]:
        category = {
            "ordinary": "普通",
            "consumable": "消耗",
            "relic": "遗物",
            "cursed": "诅咒",
        }.get(item["category"], item["category"])
        parts.append(f"{item['name']}[{category}]")
    if len(affordances) > 4:
        parts.append(f"另 {len(affordances) - 4} 件")
    return "，".join(parts)


def render_advancement_summary(player):
    options = advancement_options_for(player)
    ready = [option["label"] for option in options if option["can_advance"]]
    if ready:
        return "可晋升：" + "，".join(ready)
    blocked = options[0]["denied_reasons"] if options else []
    if blocked:
        return "暂不可晋升，主要缺口：" + "，".join(blocked[:2])
    return "暂不可晋升"


def format_name_list(names):
    return "，".join(names) if names else "暂无"


def render_result(result):
    lines = []

    if result["roll"]:
        lines.append(render_roll_line(result["roll"]))

    lines.extend(result["messages"])

    if result["state_changes"]:
        lines.append("状态变化：")
        for change in result["state_changes"]:
            lines.append(f"- {change}")

    if result["new_clues"]:
        lines.append("新增线索：")
        for clue in result["new_clues"]:
            lines.append(f"- {clue}：{CLUE_DESCRIPTIONS.get(clue, '')}")

    return "\n".join(lines)


def render_mechanical_summary(result):
    lines = []

    if result.get("roll"):
        lines.append(render_roll_line(result["roll"]))

    if result.get("state_changes"):
        lines.append("状态变化：" + "；".join(result["state_changes"]))

    if result.get("new_clues"):
        lines.append("新增线索：" + "，".join(result["new_clues"]))

    return "\n".join(lines)


def render_roll_line(roll):
    stat_name = roll.get("attribute_label") or STAT_NAMES.get(roll["stat"], roll["stat"])
    outcome = roll.get("outcome_label") or ("成功" if roll["success"] else "失败")
    modifier_label = roll.get("modifier_label", "修正")
    if "attribute_value" in roll:
        stat_text = f"{stat_name}({roll['attribute_value']}/{roll['stat_value']:+d})"
    else:
        stat_text = f"{stat_name}({roll['stat_value']})"
    extras = []
    if roll.get("risk_label"):
        extras.append(f"风险：{roll['risk_label']}")
    if "margin" in roll:
        extras.append(f"差值：{roll['margin']:+d}")
    if roll.get("attribute_profile"):
        profile = roll["attribute_profile"]
        extras.append(
            "属性："
            f"{profile.get('primary_label', profile.get('primary_attribute', '属性'))}"
            f" {profile.get('primary_value')} "
            f"{profile.get('modifier', 0):+d}"
        )
    if roll.get("skill_bonuses"):
        skill_text = "，".join(
            f"{skill['name']} +{skill['bonus']}" for skill in roll["skill_bonuses"]
        )
        extras.append(f"技能：{skill_text}")
    if roll.get("talent_bonuses"):
        talent_text = "，".join(
            f"{talent['name']} +{talent['bonus']}" for talent in roll["talent_bonuses"]
        )
        extras.append(f"天赋：{talent_text}")
    if roll.get("prayer_bonuses"):
        prayer_text = "，".join(
            f"{prayer['name']} +{prayer['bonus']}" for prayer in roll["prayer_bonuses"]
        )
        extras.append(f"祷告：{prayer_text}")
    if roll.get("item_bonuses"):
        item_text = "，".join(
            f"{item['name']} +{item['bonus']}" for item in roll["item_bonuses"]
        )
        extras.append(f"道具：{item_text}")
    if roll.get("consumed_items"):
        extras.append(f"消耗：{'，'.join(roll['consumed_items'])}")
    extra_text = f"｜{'｜'.join(extras)}" if extras else ""
    return (
        f"检定：d20({roll['d20']}) + {stat_text} "
        f"+ {modifier_label}({roll['modifier']:+d}) = {roll['total']} / DC {roll['dc']} -> {outcome}"
        f"{extra_text}"
    )


def render_ending(state):
    return f"""
============================================================
结局：{state.ending_id}
{state.ending_text}
============================================================"""


def render_help():
    return HELP_TEXT


def render_goal(state):
    if game_mode_for_state(state) == WORLD_GAME_MODE:
        return f"""当前目标：
{objective_for_state(state, MAIN_OBJECTIVE)}

当前阶段重点：
- 用自然语言描述你想做的事；
- 系统会生成场景、NPC、事件和物件；
- 检查 validator 是否阻止越权线索、道具、状态和永久事实；
- 通过日志确认哪些行动被真正记录。"""

    core_count = len(CORE_TRUTH_CLUES.intersection(state.player.clues))
    return f"""当前目标：
{objective_for_state(state, MAIN_OBJECTIVE)}

核心线索进度：{core_count}/{len(CORE_TRUTH_CLUES)}
揭露真相需要至少 4 个核心线索。
危险阈值：SAN <= 0 或 Corruption >= 5 会触发深渊污染结局。"""


def render_clues(state):
    if not state.player.clues:
        return "当前线索：暂无。建议从门口脚印、前厅圣徽或旧档案室开始调查。"

    lines = ["当前线索："]
    for clue in state.player.clues:
        marker = "核心" if clue in CORE_TRUTH_CLUES else "普通"
        description = CLUE_DESCRIPTIONS.get(clue, "")
        lines.append(f"- [{marker}] {clue}：{description}")

    core_count = len(CORE_TRUTH_CLUES.intersection(state.player.clues))
    lines.append(f"核心线索进度：{core_count}/{len(CORE_TRUTH_CLUES)}")
    return "\n".join(lines)


def render_map(state):
    if game_mode_for_state(state) == WORLD_GAME_MODE:
        return f"""地图：
当前模式：开放世界模式
当前位置：{state.current_location}

开放世界模式暂时不使用固定修道院地图，也不提前写死每个地点、NPC、道具或事件。
你可以用自然语言描述行动；系统会生成可互动内容，并判断哪些内容能被记录为事实。"""

    lines = ["地图："]
    for location, exits in LOCATIONS.items():
        markers = []
        if location == state.current_location:
            markers.append("当前位置")
        if location in state.visited_locations:
            markers.append("已到达")
        else:
            markers.append("未探索")

        marker_text = "][".join(markers)
        lines.append(f"- [{marker_text}] {location} -> {', '.join(exits)}")

    current_exits = ", ".join(LOCATIONS.get(state.current_location, []))
    lines.append(f"当前可前往：{current_exits}")
    return "\n".join(lines)


def render_log(state, limit=5):
    if not state.event_log:
        return "行动日志：暂无。进行一次行动后，这里会记录最近发生的事件。"

    recent_events = state.event_log[-limit:]
    start_index = len(state.event_log) - len(recent_events) + 1
    lines = [f"行动日志（最近 {len(recent_events)} 条 / 共 {len(state.event_log)} 条）："]

    for index, event in enumerate(recent_events, start=start_index):
        lines.append(f"{index}. {event}")

    return "\n".join(lines)
