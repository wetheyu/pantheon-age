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
        candidates.append(
            MemoryCandidate(
                memory_type="quest_memory",
                subject="committed_effects",
                content="; ".join(commit.committed_effects),
                authority_level="persistent",
                visibility="player_known",
                should_persist=True,
                source_event=f"turn_{commit.rule_result.get('turn')}",
            )
        )

    return tuple(candidates)
