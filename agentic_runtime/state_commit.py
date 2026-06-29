"""State commit layer for Phase 5 Agentic Runtime."""

from phase1_cli.rule_engine import (
    apply_rule,
    change_corruption,
    change_san,
    change_suspicion,
    change_hp,
    roll_check,
    sum_modifiers,
)
from phase1_cli.items import (
    activate_items_for_check,
    detect_direct_item_use,
    item_definition_for,
)
from phase1_cli.progression import (
    apply_advancement,
    detect_advancement_request,
    evaluate_advancement,
    matching_class_skill_bonuses,
    matching_faith_talent_bonuses,
    matching_prayer_bonuses,
    normalize_check_attribute,
    world_attribute_profile_for,
)
from phase1_cli.scenarios import (
    current_scene_focus_for_state,
    default_scene_focus,
    find_world_city_in_text,
    is_world_city_name,
    is_world_mode_state,
    set_current_scene_focus,
)

from .contracts import StateCommitProposal
from .feasibility import evaluate_world_feasibility


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
    advancement_type = detect_advancement_request(rule_action)
    if advancement_type:
        return commit_world_advancement_action(state, rule_action, adjudication, advancement_type)

    direct_item_name = detect_direct_item_use(rule_action, state.player)
    if direct_item_name:
        return commit_world_direct_item_use_action(state, rule_action, adjudication, direct_item_name)

    feasibility = evaluate_world_feasibility(state, rule_action)
    if feasibility["blocked"]:
        return commit_world_feasibility_block(state, rule_action, adjudication, feasibility)

    scene_before, scene_after, scene_changed, location_decision = apply_world_scene_focus(
        state,
        rule_action,
    )
    if rule_action.get("requires_check"):
        return commit_world_checked_action(
            state,
            rule_action,
            adjudication,
            scene_before=scene_before,
            scene_after=scene_after,
            scene_changed=scene_changed,
            location_decision=location_decision,
        )

    message = build_world_action_message(state, rule_action, scene_before, scene_after, location_decision)
    rule_result = {
        "turn": state.turn,
        "intent": "world_action",
        "raw_text": rule_action["raw_text"],
        "location_before": state.current_location,
        "location_after": state.current_location,
        "scene_focus_before": scene_before,
        "scene_focus_after": scene_after,
        "messages": [message],
        "state_changes": [],
        "new_clues": [],
        "roll": None,
        "success": True,
        "ending": None,
        "location_intent": location_decision["type"],
        "travel_destination": location_decision.get("travel_destination"),
    }
    state.add_event(message)

    effects = ["world_attempt_recorded"]
    if scene_changed:
        effects.append("scene_focus_change")
    if location_decision["type"] == "travel_request":
        effects.append("travel_request_recorded")

    return StateCommitProposal(
        committed=True,
        rule_action=rule_action,
        rule_result=rule_result,
        committed_effects=tuple(effects),
        rejected_effects=tuple(
            dict.fromkeys(
                (
                    *adjudication.denied_effects,
                    *location_decision.get("rejected_effects", ()),
                )
            )
        ),
    )


def commit_world_direct_item_use_action(state, rule_action, adjudication, item_name):
    scene_focus = current_scene_focus_for_state(state)
    definition = item_definition_for(item_name)
    rule_result = {
        "turn": state.turn,
        "intent": "world_action",
        "raw_text": rule_action["raw_text"],
        "location_before": state.current_location,
        "location_after": state.current_location,
        "scene_focus_before": scene_focus,
        "scene_focus_after": scene_focus,
        "messages": [f"你使用了「{item_name}」。"],
        "state_changes": [],
        "new_clues": [],
        "roll": None,
        "success": True,
        "ending": None,
        "location_intent": "stay",
        "travel_destination": None,
        "item_use": {
            "name": item_name,
            "category": definition["category"],
            "direct_use": dict(definition.get("direct_use", {})),
        },
    }
    apply_direct_item_effects(state, rule_result, item_name, definition)
    if definition["consumable"] and state.player.remove_item(item_name):
        rule_result["state_changes"].append(f"消耗道具：{item_name}")

    state.add_event("; ".join([*rule_result["messages"], *rule_result["state_changes"]]))
    effects = ["world_attempt_recorded", "item_use_committed"]
    if definition["consumable"]:
        effects.append("item_consumed")
    if rule_result["state_changes"]:
        effects.append("state_changed_by_item")

    return StateCommitProposal(
        committed=True,
        rule_action=rule_action,
        rule_result=rule_result,
        committed_effects=tuple(effects),
        rejected_effects=adjudication.denied_effects,
    )


def apply_direct_item_effects(state, result, item_name, definition):
    direct_use = definition.get("direct_use", {})
    if not direct_use:
        result["messages"].append("这个道具暂时没有可直接提交的效果。")
        return

    alchemist_bonus = 1 if state.player.class_id == "alchemist" else 0
    if direct_use.get("hp"):
        amount = direct_use["hp"] + (direct_use.get("alchemist_hp_bonus", 0) * alchemist_bonus)
        change_hp(state, amount, result, f"使用{item_name}")
    if direct_use.get("san"):
        amount = direct_use["san"] + (direct_use.get("alchemist_san_bonus", 0) * alchemist_bonus)
        change_san(state, amount, result, f"使用{item_name}")
    if direct_use.get("corruption"):
        change_corruption(state, direct_use["corruption"], result, f"使用{item_name}")


def commit_world_advancement_action(state, rule_action, adjudication, advancement_type):
    evaluation = evaluate_advancement(state.player, advancement_type)
    if not evaluation["can_advance"]:
        message = build_world_advancement_denied_message(rule_action, evaluation)
        rule_result = {
            "turn": state.turn,
            "intent": "world_action",
            "raw_text": rule_action["raw_text"],
            "location_before": state.current_location,
            "location_after": state.current_location,
            "scene_focus_before": current_scene_focus_for_state(state),
            "scene_focus_after": current_scene_focus_for_state(state),
            "messages": [message],
            "state_changes": [],
            "new_clues": [],
            "roll": None,
            "success": False,
            "ending": None,
            "location_intent": "stay",
            "travel_destination": None,
            "advancement": evaluation,
        }
        state.add_event(message)
        return StateCommitProposal(
            committed=True,
            rule_action=rule_action,
            rule_result=rule_result,
            committed_effects=("world_attempt_recorded", "advancement_denied"),
            rejected_effects=(
                *adjudication.denied_effects,
                "unearned_advancement",
                "unearned_level_change",
                "unearned_attribute_change",
            ),
        )

    evaluation = apply_advancement(state.player, advancement_type)
    message = build_world_advancement_success_message(rule_action, evaluation)
    rule_result = {
        "turn": state.turn,
        "intent": "world_action",
        "raw_text": rule_action["raw_text"],
        "location_before": state.current_location,
        "location_after": state.current_location,
        "scene_focus_before": current_scene_focus_for_state(state),
        "scene_focus_after": current_scene_focus_for_state(state),
        "messages": [message],
        "state_changes": list(evaluation.get("state_changes", [])),
        "new_clues": [],
        "roll": None,
        "success": True,
        "ending": None,
        "location_intent": "stay",
        "travel_destination": None,
        "advancement": evaluation,
    }
    state.add_event("; ".join([message, *rule_result["state_changes"]]))
    return StateCommitProposal(
        committed=True,
        rule_action=rule_action,
        rule_result=rule_result,
        committed_effects=(
            "world_attempt_recorded",
            "advancement_committed",
            f"advancement_{advancement_type}",
        ),
        rejected_effects=adjudication.denied_effects,
    )


def build_world_advancement_denied_message(rule_action, evaluation):
    missing = [
        format_advancement_requirement(requirement)
        for requirement in evaluation["requirements"]
        if not requirement["ok"]
    ]
    missing_text = "；".join(missing) if missing else "条件尚未满足"
    return (
        f"你尝试推进「{evaluation['label']}」，但这不是一句愿望就能完成的成长。"
        f"当前缺少：{missing_text}。"
    )


def build_world_advancement_success_message(rule_action, evaluation):
    costs = format_advancement_costs(evaluation.get("costs", {}))
    rewards = format_advancement_rewards(evaluation.get("rewards", []))
    cost_text = f"代价：{costs}。" if costs else ""
    reward_text = f"结果：{rewards}。" if rewards else ""
    return (
        f"你完成了「{evaluation['label']}」。"
        f"{cost_text}{reward_text}"
        "这次成长已经写入你的结构化状态。"
    )


def format_advancement_requirement(requirement):
    return (
        f"{requirement['field']} {requirement['current']}/"
        f"{requirement['required']}"
    )


def format_advancement_costs(costs):
    labels = {
        "revelation": "Revelation",
        "favor": "Favor",
    }
    return "，".join(f"{labels.get(key, key)} -{value}" for key, value in costs.items())


def format_advancement_rewards(rewards):
    parts = []
    for reward in rewards:
        if reward["type"] == "level":
            parts.append(f"{reward['field']} -> {reward['value']}")
        elif reward["type"] == "attribute":
            parts.append(f"{reward['label']} +{reward['value']}")
        elif reward["type"] == "resource":
            parts.append(f"{reward['field']} +{reward['value']}")
        elif reward["type"] == "burden":
            parts.append(f"新增代价：{reward['value']}")
    return "，".join(parts)


def commit_world_feasibility_block(state, rule_action, adjudication, feasibility):
    scene_focus = current_scene_focus_for_state(state)
    message = build_world_feasibility_block_message(state, rule_action, feasibility)
    rule_result = {
        "turn": state.turn,
        "intent": "world_action",
        "raw_text": rule_action["raw_text"],
        "location_before": state.current_location,
        "location_after": state.current_location,
        "scene_focus_before": scene_focus,
        "scene_focus_after": scene_focus,
        "messages": [message],
        "state_changes": [],
        "new_clues": [],
        "roll": None,
        "success": False,
        "ending": None,
        "location_intent": "stay",
        "travel_destination": None,
        "feasibility": feasibility,
    }
    state.add_event(message)

    return StateCommitProposal(
        committed=True,
        rule_action=rule_action,
        rule_result=rule_result,
        committed_effects=("world_attempt_recorded", "feasibility_blocked"),
        rejected_effects=tuple(
            dict.fromkeys(
                (
                    *adjudication.denied_effects,
                    *feasibility.get("denied_effects", ()),
                )
            )
        ),
    )


def build_world_feasibility_block_message(state, rule_action, feasibility):
    asset = feasibility.get("asset") or "这个目标"
    paths = "；".join(feasibility.get("suggested_paths", ())[:3])
    return (
        f"你不能凭当前资源直接完成「{rule_action['raw_text']}」。"
        f"{feasibility['reason']}可行的下一步包括：{paths}。"
    )


def commit_world_checked_action(
    state,
    rule_action,
    adjudication,
    scene_before=None,
    scene_after=None,
    scene_changed=False,
    location_decision=None,
):
    scene_before = scene_before or current_scene_focus_for_state(state)
    scene_after = scene_after or current_scene_focus_for_state(state)
    location_decision = location_decision or {"type": "stay", "rejected_effects": ()}
    risk_type = rule_action.get("risk_type") or "high_risk"
    attribute = normalize_check_attribute(rule_action.get("check_attribute") or rule_action.get("check_stat") or "agility", risk_type)
    rule_action["check_stat"] = attribute
    rule_action["check_attribute"] = attribute
    dc = rule_action.get("difficulty") or 14
    modifier = world_check_modifier(state, attribute, risk_type, rule_action)
    check = annotate_world_check(
        roll_check(state, attribute, dc, modifier, "行动修正"),
        risk_type,
        rule_action,
    )
    effects = [
        "world_attempt_recorded",
        "world_check_success" if check["success"] else "world_check_failed",
        f"world_check_{check['outcome_level']}",
    ]
    if scene_changed:
        effects.append("scene_focus_change")

    result = {
        "turn": state.turn,
        "intent": "world_action",
        "raw_text": rule_action["raw_text"],
        "location_before": state.current_location,
        "location_after": state.current_location,
        "scene_focus_before": scene_before,
        "scene_focus_after": scene_after,
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
        "location_intent": location_decision["type"],
        "travel_destination": location_decision.get("travel_destination"),
        "check_context": build_check_context(check, risk_type, rule_action),
    }
    apply_favor_spend_result(result, rule_action, effects)
    apply_item_spend_result(result, rule_action, effects)

    if risk_type == "violence":
        commit_world_violence_result(state, result, check, effects)
    elif risk_type == "social":
        commit_world_social_result(state, result, check, effects)
    elif risk_type in {"stealth", "theft", "escape"}:
        commit_world_mobility_result(state, result, check, effects)
    elif risk_type == "occult":
        commit_world_occult_result(state, result, check, effects)
    else:
        commit_generic_world_check_result(state, result, check, effects)

    apply_faith_context_pressure(state, result, rule_action, effects)

    state.add_event("; ".join(result["messages"]))
    return StateCommitProposal(
        committed=True,
        rule_action=rule_action,
        rule_result=result,
        committed_effects=tuple(effects),
        rejected_effects=(
            *adjudication.denied_effects,
            *location_decision.get("rejected_effects", ()),
            "unconfirmed_death",
            "unconfirmed_permanent_injury",
        ),
    )


def world_check_modifier(state, attribute, risk_type, rule_action=None):
    attribute = normalize_check_attribute(attribute, risk_type)
    if risk_type == "violence":
        base_modifier = sum_modifiers(state.player, ["attack_bonus", "direct_combat_penalty", "combat_penalty"])
    elif risk_type == "social":
        base_modifier = sum_modifiers(state.player, ["deceive_bonus", "lore_bonus"])
    elif risk_type == "theft":
        base_modifier = sum_modifiers(state.player, ["stealth_bonus", "lockpick_bonus", "deceive_bonus"])
    elif risk_type == "occult":
        if attribute in {"communion", "will"}:
            base_modifier = sum_modifiers(state.player, ["pray_bonus", "purify_bonus"])
        else:
            base_modifier = sum_modifiers(state.player, ["analyze_bonus", "ritual_bonus", "lore_bonus", "identify_bonus"])
    elif attribute == "agility":
        base_modifier = sum_modifiers(state.player, ["stealth_bonus", "escape_bonus"])
    else:
        base_modifier = 0

    attribute_profile = world_attribute_profile_for(state.player, risk_type, attribute)
    attribute_modifier = attribute_profile["modifier"]
    skill_bonuses = matching_class_skill_bonuses(state.player, risk_type, attribute, rule_action)
    talent_bonuses = matching_faith_talent_bonuses(state.player, risk_type, attribute, rule_action)
    prayer_bonuses, blocked_prayers = activate_prayers_for_check(
        state.player,
        risk_type,
        attribute,
        rule_action,
    )
    item_bonuses, consumed_items = activate_items_for_check(
        state.player,
        risk_type,
        attribute,
        rule_action,
    )
    if rule_action is not None:
        rule_action["check_stat"] = attribute
        rule_action["check_attribute"] = attribute
        rule_action["attribute_profile"] = attribute_profile
        rule_action["attribute_modifier"] = attribute_modifier
        rule_action["skill_bonuses"] = skill_bonuses
        rule_action["talent_bonuses"] = talent_bonuses
        rule_action["prayer_bonuses"] = prayer_bonuses
        rule_action["blocked_prayers"] = blocked_prayers
        rule_action["item_bonuses"] = item_bonuses
        rule_action["consumed_items"] = consumed_items
    return (
        base_modifier
        + attribute_modifier
        + sum(item["bonus"] for item in skill_bonuses)
        + sum(item["bonus"] for item in talent_bonuses)
        + sum(item["bonus"] for item in prayer_bonuses)
        + sum(item["bonus"] for item in item_bonuses)
    )


def activate_prayers_for_check(player, risk_type, attribute, rule_action=None):
    attribute = normalize_check_attribute(attribute, risk_type)
    prayer_candidates = matching_prayer_bonuses(player, risk_type, attribute, rule_action)
    if not prayer_candidates:
        return [], []

    active_prayers = []
    blocked_prayers = []
    favor_available = player.favor
    for prayer in prayer_candidates:
        cost = prayer["favor_cost"]
        if favor_available >= cost:
            favor_available -= cost
            active_prayers.append(prayer)
        else:
            blocked_prayers.append(
                {
                    "name": prayer["name"],
                    "favor_cost": cost,
                    "reason": "favor_not_enough",
                }
            )

    spent = player.favor - favor_available
    if spent:
        player.favor = favor_available
        if rule_action is not None:
            rule_action["favor_spent"] = spent
            rule_action["favor_spent_for"] = [prayer["name"] for prayer in active_prayers]

    return active_prayers, blocked_prayers


def apply_favor_spend_result(result, rule_action, effects):
    spent = rule_action.get("favor_spent", 0)
    if spent:
        prayers = "、".join(rule_action.get("favor_spent_for", [])) or "祷告"
        result["state_changes"].append(f"Favor -{spent}（祷告：{prayers}）")
        effects.append("favor_spent")
        effects.append("prayer_invoked")

    blocked_prayers = rule_action.get("blocked_prayers", [])
    if blocked_prayers:
        names = "、".join(prayer["name"] for prayer in blocked_prayers)
        result["messages"].append(f"你试图回应「{names}」，但当前神眷不足，祷词没有形成稳定力量。")
        effects.append("prayer_unavailable")


def apply_item_spend_result(result, rule_action, effects):
    item_bonuses = rule_action.get("item_bonuses", [])
    if item_bonuses:
        effects.append("item_effect_applied")

    consumed_items = rule_action.get("consumed_items", [])
    for item_name in consumed_items:
        result["state_changes"].append(f"消耗道具：{item_name}")
    if consumed_items:
        effects.append("item_consumed")


def apply_faith_context_pressure(state, result, rule_action, effects):
    if not rule_action.get("prayer_bonuses"):
        return

    faith_status = faith_status_for_player(state.player)
    if faith_status == "hostile":
        change_suspicion(state, 2, result, "敌对信仰祷告暴露风险")
        effects.append("hostile_faith_pressure")
    elif faith_status == "restricted":
        change_suspicion(state, 1, result, "受限信仰公开祷告风险")
        effects.append("restricted_faith_pressure")
    elif faith_status in {"dominant", "friendly"}:
        effects.append("local_faith_context_support")


def faith_status_for_player(player):
    context = player.flags.get("origin_church_context") or {}
    church_name = god_church_for_player(player)
    if church_name in context.get("dominant", []):
        return "dominant"
    if church_name in context.get("friendly", []):
        return "friendly"
    if church_name in context.get("restricted", []):
        return "restricted"
    if church_name in context.get("hostile", []):
        return "hostile"
    return "unknown"


def god_church_for_player(player):
    church_map = {
        "海洋之神": "潮汐圣会",
        "真理之神": "白塔院",
        "战争之神": "铁血教团",
        "审判之神": "审判庭",
        "丰饶之神": "蔷薇圣庭",
        "死亡之神": "安魂教团",
        "隐秘之神": "夜幕修会",
        "深渊之神": "密仪会",
    }
    return church_map.get(player.god, "")


def commit_world_violence_result(state, result, check, effects):
    outcome = check["outcome_level"]
    if outcome == "full_success":
        effects.append("violent_attempt_advantage")
        result["messages"].append(
            result.get("success_consequence")
            or "你取得明显优势，目标被迫后退，周围人的反应慢了半拍。"
        )
        result["messages"].append("这不是击杀确认，而是一次足以改写对峙姿态的压制。")
        change_suspicion(state, 2, result, "高风险暴力行动")
    elif outcome == "partial_success":
        effects.append("violent_attempt_advantage")
        consequence = result.get("success_consequence") or "你取得短暂优势，但现场会出现目击、阻拦或警报压力。"
        result["messages"].append(consequence)
        result["messages"].append("对方仍在场，致命后果尚未发生，真正的收场还取决于接下来的选择。")
        change_suspicion(state, 2, result, "高风险暴力行动")
    elif outcome == "costly_failure":
        effects.append("violent_attempt_escalated")
        result["messages"].append("你的动作被挡开或避开，但你还保住了一点退路。")
        result["messages"].append("现场已经被惊动，对方和旁观者都开始重新判断你。")
        change_suspicion(state, 2, result, "暴力行动暴露")
    else:
        effects.append("violent_attempt_escalated")
        consequence = result.get("failure_consequence") or "你的暴力行动没有达成预期，局面被推向更危险的对抗。"
        result["messages"].append(consequence)
        result["messages"].append("对方没有被解决，现场反而开始向更难控制的方向倾斜。")
        change_suspicion(state, 3, result, "失控的暴力行动")


def commit_world_social_result(state, result, check, effects):
    outcome = check["outcome_level"]
    if outcome == "full_success":
        effects.append("social_leverage_gained")
        result["messages"].append(
            result.get("success_consequence")
            or "对方明显动摇，给了你继续追问或提出条件的空间。"
        )
    elif outcome == "partial_success":
        effects.append("social_opening_gained")
        result["messages"].append(
            result.get("success_consequence")
            or "对方没有完全相信你，但态度出现裂缝。"
        )
    elif outcome == "costly_failure":
        effects.append("social_pressure_increased")
        result["messages"].append("你的话没有完全奏效，对方开始谨慎衡量你的身份和目的。")
        change_suspicion(state, 1, result, "社交施压引发戒备")
    else:
        effects.append("social_attempt_backfired")
        result["messages"].append(
            result.get("failure_consequence")
            or "对方彻底收紧态度，周围人也注意到这场交涉不太正常。"
        )
        change_suspicion(state, 2, result, "社交行动失控")


def commit_world_mobility_result(state, result, check, effects):
    outcome = check["outcome_level"]
    risk_type = result.get("risk_type")
    if outcome == "full_success":
        effects.append(f"{risk_type}_clean_opening")
        result["messages"].append(
            result.get("success_consequence")
            or "你干净地避开了主要阻碍，获得继续推进的机会。"
        )
    elif outcome == "partial_success":
        effects.append(f"{risk_type}_opening_with_pressure")
        result["messages"].append(
            result.get("success_consequence")
            or "你获得了机会，但现场压力仍然贴在身后。"
        )
        change_suspicion(state, 1, result, "行动留下轻微痕迹")
    elif outcome == "costly_failure":
        effects.append(f"{risk_type}_trace_left")
        result["messages"].append(
            result.get("failure_consequence")
            or "你没能完全避开阻碍，还留下了足以被追问的痕迹。"
        )
        change_suspicion(state, 2, result, "行动痕迹暴露")
    else:
        effects.append(f"{risk_type}_attempt_exposed")
        result["messages"].append(
            result.get("failure_consequence")
            or "行动暴露得太明显，现场压力迅速向你收拢。"
        )
        change_suspicion(state, 3, result, "行动严重暴露")


def commit_world_occult_result(state, result, check, effects):
    outcome = check["outcome_level"]
    if outcome == "full_success":
        effects.append("occult_pressure_contained")
        result["messages"].append(
            result.get("success_consequence")
            or "你稳住了异常的边界，短暂看清它如何影响现实。"
        )
    elif outcome == "partial_success":
        effects.append("occult_contact_survived")
        result["messages"].append(
            result.get("success_consequence")
            or "你勉强承受住异常压力，但它留下了尚未解释的回声。"
        )
    elif outcome == "costly_failure":
        effects.append("occult_backlash")
        result["messages"].append(
            result.get("failure_consequence")
            or "异常反向压迫你的感知，你不得不后退一步。"
        )
        change_san(state, -1, result, "神秘学反噬")
    else:
        effects.append("occult_backlash_severe")
        result["messages"].append(
            result.get("failure_consequence")
            or "异常穿过你的防线，带来更深的寒意和污染感。"
        )
        change_san(state, -2, result, "严重神秘学反噬")
        change_corruption(state, 1, result, "异常污染残留")


def commit_generic_world_check_result(state, result, check, effects):
    if check["outcome_level"] == "full_success":
        effects.append("high_risk_attempt_strong_advantage")
        result["messages"].append("你的高风险行动取得明显优势，但真正的成果还需要继续推进。")
    elif check["success"]:
        effects.append("high_risk_attempt_advantage")
        result["messages"].append("你的高风险行动取得了短暂优势，但真正的成果还需要继续推进。")
    elif check["outcome_level"] == "costly_failure":
        effects.append("high_risk_attempt_pressure")
        result["messages"].append("你的高风险行动没有达成预期，但仍保留了一点调整空间。")
    else:
        effects.append("high_risk_attempt_failed")
        result["messages"].append("你的高风险行动没能达成预期，局面出现新的压力。")


RISK_LABELS = {
    "violence": "暴力",
    "social": "社交施压",
    "stealth": "潜行",
    "theft": "偷窃/开锁",
    "escape": "逃脱",
    "occult": "神秘学",
    "travel": "旅行",
    "high_risk": "高风险",
}

OUTCOME_LABELS = {
    "full_success": "完全成功",
    "partial_success": "小成功",
    "costly_failure": "险败",
    "hard_failure": "严重失败",
}


def annotate_world_check(check, risk_type, rule_action):
    margin = check["total"] - check["dc"]
    if check["d20"] == 1:
        check["success"] = False
        outcome_level = "hard_failure"
    elif check["d20"] == 20:
        check["success"] = True
        outcome_level = "full_success"
    elif margin >= 8:
        outcome_level = "full_success"
    elif check["success"]:
        outcome_level = "partial_success"
    elif margin <= -8:
        outcome_level = "hard_failure"
    else:
        outcome_level = "costly_failure"

    check["margin"] = margin
    check["risk_type"] = risk_type
    check["risk_label"] = RISK_LABELS.get(risk_type, "高风险")
    check["outcome_level"] = outcome_level
    check["outcome_label"] = OUTCOME_LABELS[outcome_level]
    check["reason"] = rule_action.get("open_primary_goal") or rule_action.get("raw_text", "")
    check["check_attribute"] = rule_action.get("check_attribute") or check.get("attribute")
    check["attribute_profile"] = dict(rule_action.get("attribute_profile", {}))
    check["attribute_modifier"] = rule_action.get("attribute_modifier", 0)
    check["skill_bonuses"] = list(rule_action.get("skill_bonuses", []))
    check["talent_bonuses"] = list(rule_action.get("talent_bonuses", []))
    check["prayer_bonuses"] = list(rule_action.get("prayer_bonuses", []))
    check["blocked_prayers"] = list(rule_action.get("blocked_prayers", []))
    check["item_bonuses"] = list(rule_action.get("item_bonuses", []))
    check["consumed_items"] = list(rule_action.get("consumed_items", []))
    return check


def build_check_context(check, risk_type, rule_action):
    return {
        "risk_type": risk_type,
        "risk_label": check.get("risk_label"),
        "outcome_level": check.get("outcome_level"),
        "outcome_label": check.get("outcome_label"),
        "margin": check.get("margin"),
        "target_profile": rule_action.get("target_profile", ""),
        "possible_blockers": list(rule_action.get("possible_blockers", [])),
        "reason": check.get("reason", ""),
        "check_attribute": check.get("check_attribute"),
        "attribute_profile": dict(check.get("attribute_profile", {})),
        "attribute_modifier": check.get("attribute_modifier", 0),
        "skill_bonuses": list(check.get("skill_bonuses", [])),
        "talent_bonuses": list(check.get("talent_bonuses", [])),
        "prayer_bonuses": list(check.get("prayer_bonuses", [])),
        "blocked_prayers": list(check.get("blocked_prayers", [])),
        "item_bonuses": list(check.get("item_bonuses", [])),
        "consumed_items": list(check.get("consumed_items", [])),
    }


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


WORLD_SCENE_MOVE_KEYWORDS = (
    "前往",
    "进入",
    "走向",
    "走到",
    "去",
    "回到",
    "返回",
    "赶往",
    "抵达",
    "靠近",
)

WORLD_SCENE_LEAVE_KEYWORDS = (
    "离开",
    "退出",
    "走出",
    "离去",
    "出来",
)

WORLD_TRAVEL_KEYWORDS = (
    "乘船",
    "坐船",
    "搭船",
    "乘火车",
    "坐火车",
    "搭火车",
    "乘车",
    "坐车",
    "搭车",
    "远行",
    "出城",
    "跨城",
    "瞬移",
    "传送",
    "直接到",
    "直接去",
    "立刻到",
    "立刻去",
)

WORLD_SCENE_LOCATION_MARKERS = (
    "街",
    "区",
    "路",
    "港",
    "码头",
    "港口",
    "市场",
    "报社",
    "教会",
    "教堂",
    "礼拜堂",
    "车站",
    "大学",
    "学院",
    "图书馆",
    "酒馆",
    "旅店",
    "银行",
    "广场",
    "仓库",
    "海关",
    "警署",
    "医院",
    "大厅",
    "前厅",
    "小巷",
    "巷",
    "俱乐部",
    "沙龙",
    "工厂",
    "车间",
    "研究所",
    "博物馆",
    "王宫",
    "宫",
    "桥",
    "河岸",
    "海岸",
)


def apply_world_scene_focus(state, rule_action):
    scene_before = current_scene_focus_for_state(state)
    location_decision = classify_world_location_decision(state, rule_action)
    target = location_decision.get("scene_focus")
    if not target:
        return scene_before, scene_before, False, location_decision

    scene_after = set_current_scene_focus(state, target)
    return scene_before, scene_after, scene_after != scene_before, location_decision


def classify_world_location_decision(state, rule_action):
    raw_text = str(rule_action.get("raw_text", ""))
    target = str(rule_action.get("target") or "").strip()
    travel_destination = infer_travel_destination(state, raw_text, target)
    if travel_destination:
        return {
            "type": "travel_request",
            "scene_focus": f"前往{travel_destination}的出行准备",
            "travel_destination": travel_destination,
            "rejected_effects": ("unconfirmed_city_travel", "unconfirmed_location_change"),
        }

    if has_explicit_scene_leave(raw_text):
        return {
            "type": "leave_scene",
            "scene_focus": default_scene_focus(state.current_location),
            "rejected_effects": (),
        }

    scene_focus = infer_requested_scene_focus(state, rule_action)
    if scene_focus:
        return {
            "type": "local_move",
            "scene_focus": scene_focus,
            "rejected_effects": (),
        }

    return {"type": "stay", "rejected_effects": ()}


def infer_travel_destination(state, raw_text, target):
    target_city = target if is_world_city_name(target) else None
    text_city = find_world_city_in_text(raw_text)
    destination = target_city or text_city
    if not destination or destination == state.current_location:
        return None
    if target_city or has_cross_city_travel_intent(raw_text, destination):
        return destination
    return None


def has_cross_city_travel_intent(raw_text, destination):
    return (
        contains_any(raw_text, (*WORLD_TRAVEL_KEYWORDS, *WORLD_SCENE_MOVE_KEYWORDS))
        or f"到{destination}" in raw_text
        or f"去{destination}" in raw_text
        or f"抵达{destination}" in raw_text
        or f"前往{destination}" in raw_text
    )


def infer_requested_scene_focus(state, rule_action):
    raw_text = str(rule_action.get("raw_text", ""))
    target = str(rule_action.get("target") or "").strip()
    if not has_explicit_scene_movement(raw_text):
        return None

    candidate = normalize_scene_focus_candidate(target)
    if candidate and not looks_like_scene_focus(candidate):
        candidate = ""
    if not candidate:
        candidate = extract_scene_focus_from_text(raw_text)
    if not candidate:
        return None
    if candidate == state.current_location:
        return None
    if not looks_like_scene_focus(candidate):
        return None
    return candidate


def has_explicit_scene_movement(text):
    return any(keyword in text for keyword in WORLD_SCENE_MOVE_KEYWORDS)


def has_explicit_scene_leave(text):
    return any(keyword in text for keyword in WORLD_SCENE_LEAVE_KEYWORDS)


def normalize_scene_focus_candidate(value):
    candidate = str(value or "").strip(" \t\n\r，。；;,.、\"'“”‘’")
    for separator in ("询问", "打听", "寻找", "观察", "调查", "见", "找", "交谈", "谈话", "看看", "查看"):
        if separator in candidate:
            candidate = candidate.split(separator, 1)[0]
    candidate = candidate.strip(" \t\n\r的到向在")
    if not candidate or len(candidate) > 24:
        return ""
    if candidate in {"附近", "周围", "这里", "那里", "某处", "别人", "人", "水手", "守卫", "陌生人"}:
        return ""
    return candidate


def extract_scene_focus_from_text(text):
    for keyword in WORLD_SCENE_MOVE_KEYWORDS:
        if keyword not in text:
            continue
        _, _, tail = text.partition(keyword)
        tail = tail.strip(" \t\n\r，。；;,.、")
        for separator in ("，", "。", "；", ";", ",", "并", "然后", "再", "去找", "寻找", "打听", "询问", "观察", "调查"):
            if separator in tail:
                tail = tail.split(separator, 1)[0]
        tail = tail.strip(" \t\n\r的到向在")
        candidate = normalize_scene_focus_candidate(tail)
        if candidate:
            return candidate
    return ""


def looks_like_scene_focus(candidate):
    return any(marker in candidate for marker in WORLD_SCENE_LOCATION_MARKERS)


def contains_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def build_world_action_message(state, rule_action, scene_before, scene_after, location_decision):
    location_type = location_decision["type"]
    raw_text = rule_action["raw_text"]
    if location_type == "travel_request":
        destination = location_decision.get("travel_destination", "远方")
        return (
            f"你在{state.current_location}开始筹备前往{destination}：{raw_text}。"
            f"这一步只确认出行准备；你还没有离开{state.current_location}。"
        )
    if location_type == "leave_scene":
        return f"你离开{scene_before}，回到{scene_after}附近继续行动：{raw_text}。"
    if location_type == "local_move":
        return f"你把行动推进到{state.current_location} / {scene_after}：{raw_text}。"
    return f"你留在{state.current_location} / {scene_after}继续行动：{raw_text}。"
