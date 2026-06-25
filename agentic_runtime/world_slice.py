"""Helpers for the Phase 5 world-mode slice."""

from phase1_cli.scenarios import (
    current_scene_focus_for_state,
    is_world_mode_state,
    location_description_for_state,
)


def target_text(state, open_action):
    if open_action.targets:
        return "、".join(open_action.targets)
    if open_action.method:
        return open_action.method
    if open_action.raw_text:
        return open_action.raw_text
    return state.current_location


def city_label(state):
    scene_focus = current_scene_focus_for_state(state)
    title = state.player.flags.get("origin_city_title", "")
    if title and state.current_location == state.player.flags.get("origin_city"):
        return f"{state.current_location}（{title}） / {scene_focus}"
    return f"{state.current_location} / {scene_focus}"


def origin_line(state):
    flags = state.player.flags
    country = flags.get("origin_country_formal_name", "未知国家")
    identity = flags.get("origin_identity", "未知身份")
    ethnicity = flags.get("origin_ethnicity", identity)
    return f"{country} / {identity} / {ethnicity}"


def visible_memory_line(memory_retrieval):
    if not memory_retrieval:
        return "暂无可见长期记忆。"
    visible = tuple(memory_retrieval.player_known) + tuple(memory_retrieval.location_context)
    remembered = [item for item in visible if "长期记忆" in item]
    normalized = [normalize_visible_memory(item) for item in remembered]
    normalized = [item for item in normalized if item]
    if normalized:
        return "；".join(normalized[-2:])
    return "暂无可见长期记忆。"


def normalize_visible_memory(item):
    content = item.split("->", 1)[-1].strip()
    if not content or content == "world_attempt_recorded":
        return ""
    if content.startswith("玩家尝试："):
        return "你曾尝试：" + content.removeprefix("玩家尝试：").strip()
    return content


def city_description(state):
    return location_description_for_state(state)


def is_world_slice(state):
    return is_world_mode_state(state)
