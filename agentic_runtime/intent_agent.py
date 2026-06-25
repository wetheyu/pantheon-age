"""Intent Agent baseline.

This local agent keeps player intent open and descriptive. It may use the old
parser as a bridge signal, but it does not expose the old intent enum as the
primary representation.
"""

from phase1_cli.intent_parser import parse_intent

from .contracts import OpenActionProposal


def propose_open_action(user_text, state, memory_retrieval=None):
    raw_text = user_text.strip()
    bridge_action = parse_intent(raw_text, state.current_location)
    target = bridge_action.get("target") or infer_text_target(raw_text)
    requested_effects = infer_requested_effects(bridge_action)

    targets = (target,) if target else ()
    player_assumptions = infer_player_assumptions(raw_text)

    return OpenActionProposal(
        raw_text=raw_text,
        action_summary=f"玩家尝试：{raw_text}",
        primary_goal=build_primary_goal(raw_text, target),
        secondary_goals=(),
        method=raw_text,
        targets=targets,
        player_assumptions=player_assumptions,
        requested_effects=requested_effects,
        confidence=0.75 if bridge_action["intent"] == "unknown" else 0.95,
    )


def build_primary_goal(raw_text, target):
    if target:
        return f"围绕「{target}」执行行动"
    return raw_text or "未说明行动目标"


def infer_requested_effects(bridge_action):
    intent = bridge_action["intent"]
    effect_map = {
        "move": ("location_change",),
        "investigate": ("minor_observation", "possible_clue"),
        "analyze": ("occult_interpretation",),
        "attack": ("combat_resolution",),
        "pray": ("faith_response",),
        "rest": ("recovery",),
        "use_item": ("item_use",),
        "stealth": ("reduced_suspicion",),
        "talk": ("npc_response",),
        "unknown": ("open_attempt",),
    }
    return effect_map.get(intent, ("open_attempt",))


def infer_player_assumptions(raw_text):
    markers = ("可能", "应该", "我觉得", "怀疑", "猜")
    if any(marker in raw_text for marker in markers):
        return (raw_text,)
    return ()


def infer_text_target(raw_text):
    separators = ("去", "到", "向", "进入", "调查", "询问", "攻击", "使用")
    for separator in separators:
        if separator in raw_text:
            tail = raw_text.split(separator, 1)[1].strip()
            if tail:
                return tail
    return None
