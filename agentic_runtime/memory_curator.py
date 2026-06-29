"""Memory curation baseline for Phase 5."""

from .contracts import MemoryCandidate


def curate_memory(open_action, adjudication, commit):
    is_world_action = commit.rule_result.get("intent") == "world_action"
    candidates = [
        MemoryCandidate(
            memory_type="player_memory",
            subject="player_action",
            content=open_action.action_summary,
            authority_level="persistent" if is_world_action else "temporary",
            visibility="player_known",
            should_persist=is_world_action,
            source_event=f"turn_{commit.rule_result.get('turn')}",
        )
    ]

    for assumption in open_action.player_assumptions:
        candidates.append(
            MemoryCandidate(
                memory_type="temporary_scene_memory",
                subject="player_assumption",
                content=f"玩家猜测：{assumption}",
                authority_level="temporary",
                visibility="player_known",
                should_persist=False,
                source_event=f"turn_{commit.rule_result.get('turn')}",
            )
        )

    if commit.committed_effects:
        outcome_memory = build_public_outcome_memory(open_action, commit)
        if outcome_memory:
            candidates.append(
                MemoryCandidate(
                    memory_type="quest_memory",
                    subject="turn_outcome",
                    content=outcome_memory,
                    authority_level="persistent",
                    visibility="player_known",
                    should_persist=True,
                    source_event=f"turn_{commit.rule_result.get('turn')}",
                )
            )

    return tuple(candidates)


def build_public_outcome_memory(open_action, commit):
    """Convert internal effects into player-facing memory.

    Committed effect ids are useful for tests and observability, but they should
    never leak into the story as remembered facts.
    """
    effects = set(commit.committed_effects)
    rule_result = commit.rule_result or {}

    if "feasibility_blocked" in effects:
        return "这次行动被现实条件挡住，后续可以从询价、担保、融资或调查资源缺口入手。"

    if "travel_request_recorded" in effects:
        destination = rule_result.get("travel_destination") or "远方"
        return f"你把前往{destination}作为明确目标，但尚未真正离开当前城市。"

    if "advancement_committed" in effects:
        return "你完成了一次结构化成长，新的能力与代价已经写入角色状态。"

    if "advancement_denied" in effects:
        return "你尝试推进成长，但当前条件、资源或仪式准备尚未满足。"

    if any(effect.startswith("world_check_") for effect in effects):
        roll = rule_result.get("roll") or {}
        outcome = roll.get("outcome_label") or ("成功" if rule_result.get("success") else "失败")
        risk = roll.get("risk_label") or "高风险行动"
        if rule_result.get("success"):
            return f"你在一次{risk}中取得{outcome}，获得继续推进的机会。"
        return f"你在一次{risk}中遭遇{outcome}，现场压力随之上升。"

    if "scene_focus_change" in effects:
        scene = rule_result.get("scene_focus_after") or "新的现场"
        return f"你把行动重心转向{scene}。"

    return "这次行动留下了一个可继续追问、观察或利用的方向。"
