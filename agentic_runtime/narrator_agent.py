"""Narrator Agent baseline."""

from phase1_cli.story import render_result

from .contracts import NarrationProposal


def narrate_turn(
    open_action,
    temporary_content,
    commit,
    memory_candidates=(),
    npc_proposals=(),
    event_proposals=(),
    item_proposals=(),
):
    if commit.rule_result.get("intent") == "world_action":
        return narrate_world_slice(
            open_action,
            temporary_content,
            commit,
            memory_candidates,
            npc_proposals,
            event_proposals,
            item_proposals,
        )

    base_text = render_result(commit.rule_result)
    scene_text = "\n".join(content.description for content in temporary_content)
    npc_text = "\n".join(f"{npc.name}：{npc.description}" for npc in npc_proposals)
    event_text = "\n".join(event.summary for event in event_proposals)
    item_text = "\n".join(f"{item.name}：{item.description}" for item in item_proposals)
    text_parts = []
    if scene_text:
        text_parts.append(scene_text)
    if npc_text:
        text_parts.append(npc_text)
    if event_text:
        text_parts.append(event_text)
    if item_text:
        text_parts.append(item_text)
    text_parts.append(base_text)

    return NarrationProposal(
        text="\n".join(part for part in text_parts if part),
        claimed_effects=commit.committed_effects,
    )


def narrate_world_slice(
    open_action,
    temporary_content,
    commit,
    memory_candidates=(),
    npc_proposals=(),
    event_proposals=(),
    item_proposals=(),
):
    sections = []

    if temporary_content:
        sections.append(" ".join(content.description for content in temporary_content))
    else:
        sections.append("你照着自己的打算开始行动。")

    if npc_proposals:
        npc_lines = []
        for npc in npc_proposals:
            npc_lines.append(f"{npc.name}在附近停下脚步。{npc.description}")
        sections.append(" ".join(npc_lines))

    if event_proposals:
        sections.append(" ".join(event.summary for event in event_proposals))

    if item_proposals:
        item_lines = []
        for item in item_proposals:
            use_text = "你可以继续观察它，也可以把它带入下一次询问。"
            item_lines.append(f"你注意到{item.name}。{item.description}{use_text}")
        sections.append(" ".join(item_lines))

    sections.append(f"你选择：{open_action.raw_text}")

    if commit.rule_result.get("risk_type") == "violence":
        blockers = commit.rule_result.get("possible_blockers") or ()
        if blockers:
            sections.append("可能介入的压力：" + "、".join(blockers) + "。")
        if commit.rule_result.get("messages"):
            sections.append(" ".join(commit.rule_result["messages"]))
        if commit.rule_result.get("success"):
            sections.append("你的动作抢到了短暂优势，但这只确认了危险冲突升级和现场压力。")
        else:
            sections.append("你的动作没能达成预期，现场压力立刻反扑回来。")
        sections.append("目标退场、永久伤害和更深后果都还需要后续裁定。")
    elif commit.committed_effects:
        sections.append("这不是确凿线索，但已经足够成为下一步追查的起点。")
    else:
        sections.append("这次行动暂时没有形成可靠记录。")

    persisted = [candidate.content for candidate in memory_candidates if candidate.should_persist]
    if persisted:
        sections.append("你记住了此刻的细节。")

    return NarrationProposal(
        text="\n".join(part for part in sections if part),
        claimed_effects=commit.committed_effects,
    )
