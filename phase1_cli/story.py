"""Fixed story text for 神座纪元 v1.1.

Later, an LLM can replace or enrich this module, but it should still receive
rule results from rule_engine instead of deciding core state changes itself.
"""

from data import (
    CLUE_DESCRIPTIONS,
    HELP_TEXT,
    LOCATION_DESCRIPTIONS,
    LOCATIONS,
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
