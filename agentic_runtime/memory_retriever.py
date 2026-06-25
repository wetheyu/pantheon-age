"""Local memory retrieval for the Phase 5 baseline."""

from phase1_cli.scenarios import is_world_mode_state, location_description_for_state

from .contracts import MemoryRetrievalResult
from .memory_store import memory_bucket_records


def retrieve_memory(state, user_text, recent_event_limit=5, memory_record_limit=5):
    player_known = []
    if state.player.clues:
        player_known.append("已知线索：" + "、".join(sorted(state.player.clues)))
    if state.player.inventory:
        player_known.append("背包物品：" + "、".join(state.player.inventory))
    if is_world_mode_state(state):
        origin = state.player.flags
        player_known.append(
            "出身身份："
            f"{origin.get('origin_country_formal_name', '未知国家')} / "
            f"{origin.get('origin_identity', '未知身份')}，"
            f"民族：{origin.get('origin_ethnicity', origin.get('origin_identity', '未知民族'))}，"
            f"开局城市：{origin.get('origin_city', state.current_location)}，"
            f"开局身份：{origin.get('background_name', '未知身份')}"
        )
        background_description = origin.get("background_description")
        if background_description:
            player_known.append("身份说明：" + background_description)
        church_context = origin.get("origin_church_context") or {}
        if church_context:
            player_known.append(
                "本地宗教合法性："
                f"主导/国教：{format_context_items(church_context.get('dominant'))}；"
                f"合法公开：{format_context_items(church_context.get('friendly'))}；"
                f"受限/异端风险：{format_context_items(church_context.get('restricted'))}；"
                f"敌对异教/邪教：{format_context_items(church_context.get('hostile'))}"
            )

    player_known.extend(
        format_memory_records(
            memory_bucket_records(state, "player_known")[-memory_record_limit:],
            "玩家长期记忆",
        )
    )
    player_known.extend(
        format_memory_records(
            memory_bucket_records(state, "quest")[-memory_record_limit:],
            "任务长期记忆",
        )
    )

    location_context = [
        f"当前位置：{state.current_location}",
        location_description_for_state(state),
    ]
    location_context.extend(
        format_memory_records(
            memory_bucket_records(state, "location")[-memory_record_limit:],
            "地点长期记忆",
        )
    )
    recent_events = tuple(state.event_log[-recent_event_limit:])
    hidden_context = tuple(
        format_memory_records(
            memory_bucket_records(state, "npc_known")[-memory_record_limit:],
            "NPC隐藏记忆",
        )
        + format_memory_records(
            memory_bucket_records(state, "secret")[-memory_record_limit:],
            "系统秘密记忆",
        )
    )

    return MemoryRetrievalResult(
        player_known=tuple(player_known),
        location_context=tuple(location_context),
        recent_events=recent_events,
        hidden_context=hidden_context,
        source="local-memory-store",
    )


def format_context_items(items):
    if not items:
        return "无"
    return "、".join(items)


def format_memory_records(records, label):
    return [f"{label}：{record.subject} -> {record.content}" for record in records]
