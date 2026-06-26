"""State commit layer for Phase 5 Agentic Runtime."""

from phase1_cli.rule_engine import (
    apply_rule,
    change_corruption,
    change_san,
    change_suspicion,
    roll_check,
    sum_modifiers,
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
    stat = rule_action.get("check_stat") or "agility"
    dc = rule_action.get("difficulty") or 14
    modifier = world_check_modifier(state, stat, risk_type)
    check = annotate_world_check(
        roll_check(state, stat, dc, modifier, "行动修正"),
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


def world_check_modifier(state, stat, risk_type):
    if risk_type == "violence":
        return sum_modifiers(state.player, ["attack_bonus", "direct_combat_penalty", "combat_penalty"])
    if risk_type == "social":
        return sum_modifiers(state.player, ["deceive_bonus", "lore_bonus"])
    if risk_type == "theft":
        return sum_modifiers(state.player, ["stealth_bonus", "lockpick_bonus", "deceive_bonus"])
    if risk_type == "occult":
        if stat == "faith":
            return sum_modifiers(state.player, ["pray_bonus", "purify_bonus"])
        return sum_modifiers(state.player, ["analyze_bonus", "ritual_bonus", "lore_bonus", "identify_bonus"])
    if stat == "agility":
        return sum_modifiers(state.player, ["stealth_bonus", "escape_bonus"])
    return 0


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
    if check["d20"] == 20 or margin >= 8:
        outcome_level = "full_success"
    elif check["success"]:
        outcome_level = "partial_success"
    elif check["d20"] == 1 or margin <= -8:
        outcome_level = "hard_failure"
    else:
        outcome_level = "costly_failure"

    check["margin"] = margin
    check["risk_type"] = risk_type
    check["risk_label"] = RISK_LABELS.get(risk_type, "高风险")
    check["outcome_level"] = outcome_level
    check["outcome_label"] = OUTCOME_LABELS[outcome_level]
    check["reason"] = rule_action.get("open_primary_goal") or rule_action.get("raw_text", "")
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
    if target_city or contains_any(raw_text, (*WORLD_TRAVEL_KEYWORDS, *WORLD_SCENE_MOVE_KEYWORDS)):
        return destination
    return None


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
