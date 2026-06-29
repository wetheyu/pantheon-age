"""Rule Arbiter Agent baseline.

The arbiter proposes how an open player action can be adjudicated. It keeps the
open proposal intact, then creates a bridge action only at the rule boundary so
Phase 1's deterministic engine can still execute the current demo scenario.
"""

from phase1_cli.data import LOCATIONS
from phase1_cli.intent_parser import CHECK_DEFAULTS, parse_intent
from phase1_cli.scenarios import is_world_mode_state

from .contracts import RuleAdjudicationProposal, RuleCheckProposal


def propose_rule_adjudication(state, open_action):
    bridge_action = build_bridge_action(state, open_action)
    checks = build_required_checks(bridge_action)
    allowed_effects = allowed_effects_for(bridge_action["intent"])
    conditional_effects = tuple(effect for effect in open_action.requested_effects if effect not in allowed_effects)

    return RuleAdjudicationProposal(
        action_type=bridge_action["intent"],
        main_goal=open_action.primary_goal,
        secondary_goals=open_action.secondary_goals,
        required_checks=checks,
        allowed_effects=allowed_effects,
        conditional_effects=conditional_effects,
        denied_effects=("unearned_reward", "unearned_secret", "unearned_clue"),
        bridge_action=bridge_action,
        reasoning_summary=build_reasoning_summary(bridge_action),
    )


def build_bridge_action(state, open_action):
    if is_world_mode_state(state):
        return build_world_mode_bridge_action(state, open_action)

    bridge_action = parse_intent(open_action.raw_text, state.current_location)
    target = bridge_action.get("target") or first_target(open_action)

    if bridge_action["intent"] == "unknown" and is_reachable_location(state.current_location, target):
        bridge_action = {
            **bridge_action,
            "intent": "move",
            "target": target,
            "requires_check": False,
            "check_stat": None,
            "difficulty": None,
        }

    if bridge_action.get("target") is None and target:
        bridge_action = {**bridge_action, "target": target}

    bridge_action["open_method"] = open_action.method
    bridge_action["open_primary_goal"] = open_action.primary_goal
    bridge_action["open_requested_effects"] = list(open_action.requested_effects)
    bridge_action["player_assumptions"] = list(open_action.player_assumptions)
    return bridge_action


def build_world_mode_bridge_action(state, open_action):
    target = first_target(open_action) or state.current_location
    risk_check = infer_world_risk_check(open_action)
    return {
        "intent": "world_action",
        "target": target,
        "item": None,
        "requires_check": risk_check["requires_check"],
        "check_stat": risk_check["check_stat"],
        "check_attribute": risk_check["check_stat"],
        "difficulty": risk_check["difficulty"],
        "risk_type": risk_check["risk_type"],
        "target_profile": risk_check["target_profile"],
        "possible_blockers": list(risk_check["possible_blockers"]),
        "success_consequence": risk_check["success_consequence"],
        "failure_consequence": risk_check["failure_consequence"],
        "raw_text": open_action.raw_text,
        "open_method": open_action.method,
        "open_primary_goal": open_action.primary_goal,
        "open_requested_effects": list(open_action.requested_effects),
        "player_assumptions": list(open_action.player_assumptions),
    }


def first_target(open_action):
    if not open_action.targets:
        return None
    return open_action.targets[0]


def is_reachable_location(current_location, target):
    if not target:
        return False
    return target in LOCATIONS.get(current_location, [])


def build_required_checks(bridge_action):
    if bridge_action["intent"] == "world_action" and bridge_action.get("requires_check"):
        return (
            RuleCheckProposal(
                check_type=bridge_action.get("risk_type") or "world_action",
                stat=bridge_action.get("check_stat"),
                dc=bridge_action.get("difficulty"),
                reason="开放世界中的高风险行动需要检定，不能由叙事直接确认结果。",
            ),
        )

    check_stat, difficulty = CHECK_DEFAULTS.get(bridge_action["intent"], (None, None))
    if check_stat is None:
        return ()
    return (
        RuleCheckProposal(
            check_type=bridge_action["intent"],
            stat=check_stat,
            dc=difficulty,
            reason="当前 deterministic rule engine 需要这个检定。",
        ),
    )


def allowed_effects_for(intent):
    effects = {
        "move": ("location_change",),
        "investigate": ("possible_clue", "minor_observation"),
        "analyze": ("occult_interpretation", "possible_clue"),
        "attack": ("combat_resolution",),
        "pray": ("faith_response",),
        "rest": ("recovery",),
        "use_item": ("item_use",),
        "stealth": ("reduced_suspicion",),
        "talk": ("npc_response",),
        "world_action": (
            "temporary_scene",
            "temporary_npc",
            "temporary_event",
            "temporary_item",
            "attempt_recorded",
            "world_check",
            "suspicion_change",
            "scene_focus_change",
            "travel_request",
        ),
        "unknown": ("attempt_recorded",),
    }
    return effects.get(intent, ("attempt_recorded",))


def infer_world_risk_check(open_action):
    text = " ".join(
        (
            open_action.raw_text,
            open_action.primary_goal,
            open_action.method,
            " ".join(open_action.requested_effects),
        )
    ).lower()

    if contains_any(
        text,
        (
            "杀",
            "刺杀",
            "暗杀",
            "杀死",
            "攻击",
            "袭击",
            "砍",
            "刺",
            "射击",
            "开枪",
            "处决",
            "殴打",
            "combat",
            "kill",
            "death",
            "murder",
            "attack",
        ),
    ):
        method_text = f"{open_action.raw_text} {open_action.method}".lower()
        stat = "agility" if contains_any(method_text, ("偷袭", "暗杀", "背刺", "潜行", "ambush", "stealth")) else "physique"
        return {
            "requires_check": True,
            "check_stat": stat,
            "difficulty": 16,
            "risk_type": "violence",
            "target_profile": "unknown_target",
            "possible_blockers": ("witnesses", "local_authorities"),
            "success_consequence": "你取得短暂优势，但现场会出现目击、阻拦或警报压力。",
            "failure_consequence": "行动失控，目标或旁观者可能反抗，附近秩序力量会更快介入。",
        }

    if contains_any(
        text,
        (
            "偷",
            "偷走",
            "偷取",
            "盗",
            "扒",
            "开锁",
            "撬锁",
            "撬开",
            "pickpocket",
            "steal",
            "lockpick",
            "theft",
        ),
    ):
        return {
            "requires_check": True,
            "check_stat": "agility",
            "difficulty": 16,
            "risk_type": "theft",
            "target_profile": "guarded_property",
            "possible_blockers": ("owner_notice", "nearby_witnesses", "local_patrol"),
            "success_consequence": "你拿到一个短暂窗口，可以接近目标物或制造转移注意的机会。",
            "failure_consequence": "目标物没有顺利到手，周围视线和本地治安压力开始向你集中。",
        }

    if contains_any(
        text,
        (
            "潜入",
            "潜行",
            "躲",
            "隐藏",
            "尾随",
            "跟踪",
            "翻墙",
            "溜进",
            "避开",
            "stealth",
            "sneak",
            "hide",
            "shadow",
        ),
    ):
        return {
            "requires_check": True,
            "check_stat": "agility",
            "difficulty": 15,
            "risk_type": "stealth",
            "target_profile": "watched_area",
            "possible_blockers": ("suspicious_bystander", "locked_route", "patrol_route"),
            "success_consequence": "你避开了最明显的目光，获得继续接近或观察的机会。",
            "failure_consequence": "你的动作留下了痕迹，有人开始意识到这里多了一个不该出现的人。",
        }

    if contains_any(
        text,
        (
            "威胁",
            "逼问",
            "恐吓",
            "胁迫",
            "贿赂",
            "说服",
            "套话",
            "欺骗",
            "撒谎",
            "交涉",
            "persuade",
            "threaten",
            "coerce",
            "bribe",
            "deceive",
        ),
    ):
        return {
            "requires_check": True,
            "check_stat": "insight",
            "difficulty": 14,
            "risk_type": "social",
            "target_profile": "social_target",
            "possible_blockers": ("public_attention", "target_resistance", "reputation_risk"),
            "success_consequence": "对方的态度出现裂缝，你获得继续施压、套话或转入交易的余地。",
            "failure_consequence": "对方没有被你推动，反而开始戒备你的身份和目的。",
        }

    if contains_any(
        text,
        (
            "仪式",
            "祈祷",
            "祷告",
            "咒文",
            "魔法",
            "符号",
            "污染",
            "深渊",
            "梦境",
            "占卜",
            "召唤",
            "净化",
            "ritual",
            "occult",
            "magic",
            "abyss",
            "dream",
        ),
    ):
        stat = "communion" if contains_any(text, ("祈祷", "祷告", "净化", "pray", "purify")) else "knowledge"
        return {
            "requires_check": True,
            "check_stat": stat,
            "difficulty": 17,
            "risk_type": "occult",
            "target_profile": "occult_pressure",
            "possible_blockers": ("mental_backlash", "ritual_contamination", "unverified_symbol"),
            "success_consequence": "你短暂稳住了异常压力，能够继续观察它的边界而不立刻被吞没。",
            "failure_consequence": "异常反向压迫你的感知，理智、信仰或身体都可能付出代价。",
        }

    if contains_any(
        text,
        (
            "逃跑",
            "逃离",
            "摆脱",
            "甩开",
            "躲开追捕",
            "逃出",
            "escape",
            "flee",
        ),
    ):
        return {
            "requires_check": True,
            "check_stat": "agility",
            "difficulty": 15,
            "risk_type": "escape",
            "target_profile": "active_pressure",
            "possible_blockers": ("blocked_exit", "pursuer", "crowded_route"),
            "success_consequence": "你抓住一条可用路线，暂时拉开距离。",
            "failure_consequence": "退路变得更窄，追逐者或现场压力逼近了你。",
        }

    return {
        "requires_check": False,
        "check_stat": None,
        "difficulty": None,
        "risk_type": None,
        "target_profile": "",
        "possible_blockers": (),
        "success_consequence": "",
        "failure_consequence": "",
    }


def contains_any(text, keywords):
    return any(keyword in text for keyword in keywords)


def build_reasoning_summary(bridge_action):
    if bridge_action["intent"] == "unknown":
        return "Agent 保留了玩家开放行动，但当前 demo rule engine 暂无可执行映射。"
    if bridge_action["intent"] == "world_action":
        return "Agent 在 world-mode 中保留开放行动，不把它硬塞进修道院教程地图。"
    return "Agent 将开放行动转换为当前 deterministic rule engine 可执行的桥接行动。"
