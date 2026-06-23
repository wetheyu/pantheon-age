"""Fixed story text for 神座纪元 v2.1.

Later, an LLM can replace or enrich this module, but it should still receive
rule results from rule_engine instead of deciding core state changes itself.
"""

from .data import (
    CLUE_DESCRIPTIONS,
    CORE_TRUTH_CLUES,
    HELP_TEXT,
    LOCATION_DESCRIPTIONS,
    LOCATIONS,
    MAIN_OBJECTIVE,
    PROJECT_ENGLISH_NAME,
    PROJECT_INTERNAL_MILESTONE,
    PROJECT_NAME,
    PROJECT_STAGE,
    PROJECT_VERSION,
    STAT_NAMES,
)


def render_title():
    return f"""============================================================
{PROJECT_NAME} / {PROJECT_ENGLISH_NAME} - v{PROJECT_VERSION} {PROJECT_INTERNAL_MILESTONE} {PROJECT_STAGE}
雾中修道院 / Mist Abbey
============================================================"""


def render_opening(character):
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
    exits = ", ".join(LOCATIONS[location])

    return f"""
------------------------------------------------------------
第 {state.turn + 1} 轮 | 位置：{location}
{LOCATION_DESCRIPTIONS[location]}
可前往：{exits}

HP {player.hp}/{player.max_hp} | SAN {player.san}/{player.max_san} | Suspicion {player.suspicion} | Corruption {player.corruption}
背包：{inventory}
线索：{clues}
------------------------------------------------------------"""


def render_result(result):
    lines = []

    if result["roll"]:
        roll = result["roll"]
        stat_name = STAT_NAMES.get(roll["stat"], roll["stat"])
        outcome = "成功" if roll["success"] else "失败"
        lines.append(
            f"检定：d20({roll['d20']}) + {stat_name}({roll['stat_value']}) "
            f"+ 修正({roll['modifier']:+d}) = {roll['total']} / DC {roll['dc']} -> {outcome}"
        )

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


def render_ending(state):
    return f"""
============================================================
结局：{state.ending_id}
{state.ending_text}
============================================================"""


def render_help():
    return HELP_TEXT


def render_goal(state):
    core_count = len(CORE_TRUTH_CLUES.intersection(state.player.clues))
    return f"""当前目标：
{MAIN_OBJECTIVE}

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

    current_exits = ", ".join(LOCATIONS[state.current_location])
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
