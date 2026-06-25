"""State commit layer for Phase 5 Agentic Runtime."""

from phase1_cli.rule_engine import apply_rule, change_suspicion, roll_check, sum_modifiers
from phase1_cli.scenarios import is_world_mode_state

from .contracts import StateCommitProposal


def commit_adjudication(state, adjudication):
    rule_action = dict(adjudication.bridge_action)
    if adjudication.action_type == "world_action" or is_world_mode_state(state):
        return commit_world_action(state, rule_action, adjudication)

    rule_result = apply_rule(state, rule_action)
    committed_effects = collect_committed_effects(rule_result)

    return StateCommitProposal(
        committed=True,
        rule_action=rule_action,
        rule_result=rule_result,
        committed_effects=committed_effects,
        rejected_effects=adjudication.denied_effects,
    )


def commit_world_action(state, rule_action, adjudication):
    state.record_turn()
    if rule_action.get("requires_check"):
        return commit_world_checked_action(state, rule_action, adjudication)

    message = (
        f"你在{state.current_location}展开行动：{rule_action['raw_text']}。"
        "这次开放行动已被记录，但不会自动改写地点、线索、背包或角色状态。"
    )
    rule_result = {
        "turn": state.turn,
        "intent": "world_action",
        "raw_text": rule_action["raw_text"],
        "location_before": state.current_location,
        "location_after": state.current_location,
        "messages": [message],
        "state_changes": [],
        "new_clues": [],
        "roll": None,
        "success": True,
        "ending": None,
    }
    state.add_event(message)

    return StateCommitProposal(
        committed=True,
        rule_action=rule_action,
        rule_result=rule_result,
        committed_effects=("world_attempt_recorded",),
        rejected_effects=adjudication.denied_effects,
    )


def commit_world_checked_action(state, rule_action, adjudication):
    risk_type = rule_action.get("risk_type") or "high_risk"
    stat = rule_action.get("check_stat") or "agility"
    dc = rule_action.get("difficulty") or 14
    modifier = world_check_modifier(state, stat, risk_type)
    check = roll_check(state, stat, dc, modifier, "行动修正")
    effects = ["world_attempt_recorded", "world_check_success" if check["success"] else "world_check_failed"]

    result = {
        "turn": state.turn,
        "intent": "world_action",
        "raw_text": rule_action["raw_text"],
        "location_before": state.current_location,
        "location_after": state.current_location,
        "messages": [],
        "state_changes": [],
        "new_clues": [],
        "roll": check,
        "success": check["success"],
        "ending": None,
        "risk_type": risk_type,
        "target_profile": rule_action.get("target_profile", ""),
        "possible_blockers": list(rule_action.get("possible_blockers", [])),
        "success_consequence": rule_action.get("success_consequence", ""),
        "failure_consequence": rule_action.get("failure_consequence", ""),
    }

    if risk_type == "violence":
        commit_world_violence_result(state, result, check, effects)
    else:
        commit_generic_world_check_result(result, check, effects)

    state.add_event("; ".join(result["messages"]))
    return StateCommitProposal(
        committed=True,
        rule_action=rule_action,
        rule_result=result,
        committed_effects=tuple(effects),
        rejected_effects=(
            *adjudication.denied_effects,
            "unconfirmed_death",
            "unconfirmed_permanent_injury",
        ),
    )


def world_check_modifier(state, stat, risk_type):
    if risk_type == "violence":
        return sum_modifiers(state.player, ["attack_bonus", "direct_combat_penalty", "combat_penalty"])
    if stat == "agility":
        return sum_modifiers(state.player, ["stealth_bonus", "escape_bonus"])
    return 0


def commit_world_violence_result(state, result, check, effects):
    if check["success"]:
        effects.append("violent_attempt_advantage")
        consequence = result.get("success_consequence") or "你取得短暂优势，但现场会出现目击、阻拦或警报压力。"
        result["messages"].append(consequence)
        result["messages"].append("系统没有确认死亡、永久伤害或目标退场。")
        change_suspicion(state, 2, result, "高风险暴力行动")
    else:
        effects.append("violent_attempt_escalated")
        consequence = result.get("failure_consequence") or "你的暴力行动没有达成预期，局面被推向更危险的对抗。"
        result["messages"].append(consequence)
        result["messages"].append("系统没有确认死亡、永久伤害或目标退场。")
        change_suspicion(state, 3, result, "失控的暴力行动")


def commit_generic_world_check_result(result, check, effects):
    if check["success"]:
        effects.append("high_risk_attempt_advantage")
        result["messages"].append("你的高风险行动取得了短暂优势，但还没有形成长期世界事实。")
    else:
        effects.append("high_risk_attempt_failed")
        result["messages"].append("你的高风险行动没能达成预期，局面出现新的压力。")


def collect_committed_effects(rule_result):
    effects = []
    if rule_result.get("location_after") != rule_result.get("location_before"):
        effects.append("location_change")
    if rule_result.get("state_changes"):
        effects.extend(rule_result["state_changes"])
    if rule_result.get("new_clues"):
        effects.extend(f"clue:{clue}" for clue in rule_result["new_clues"])
    if rule_result.get("ending"):
        effects.append(f"ending:{rule_result['ending']}")
    return tuple(effects)
