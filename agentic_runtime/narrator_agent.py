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

    feasibility = commit.rule_result.get("feasibility")
    if feasibility and feasibility.get("blocked"):
        return narrate_feasibility_block(open_action, commit, feasibility)

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
            use_text = "它可以成为继续观察、追问或误导他人的话题。"
            item_lines.append(f"你注意到{item.name}。{item.description}{use_text}")
        sections.append(" ".join(item_lines))

    sections.append(f"你的行动很明确：{open_action.raw_text}")

    if commit.rule_result.get("risk_type") == "violence":
        blockers = commit.rule_result.get("possible_blockers") or ()
        if blockers:
            sections.append("你能感觉到周围的压力正在靠近：" + "、".join(blockers) + "。")
        if commit.rule_result.get("messages"):
            sections.append(" ".join(commit.rule_result["messages"]))
        if commit.rule_result.get("success"):
            sections.append("你抢到了一瞬间的主动权，足以改变对峙的姿态，却还不足以把一切写成定局。")
        else:
            sections.append("你的动作没能达成预期，场面立刻反压回来，目光、脚步和喊声都开始聚向你。")
    elif commit.committed_effects:
        location_note = render_location_continuity_note(commit.rule_result)
        if location_note:
            sections.append(location_note)
        sections.append("这还谈不上结论，却已经足够把你推向下一次追问。")
    else:
        sections.append("眼下还没有决定性的发现，但现场的沉默本身也值得记住。")

    persisted = [candidate.content for candidate in memory_candidates if candidate.should_persist]
    if persisted:
        sections.append("你把几个关键细节压进心里，准备在合适的时候再拿出来对照。")

    return NarrationProposal(
        text="\n\n".join(part for part in sections if part),
        claimed_effects=commit.committed_effects,
    )


def narrate_feasibility_block(open_action, commit, feasibility):
    resource = feasibility.get("player_resource", {})
    paths = feasibility.get("suggested_paths", ())
    path_text = "\n".join(f"- {path}" for path in paths[:3])
    text = (
        f"你可以提出这个打算：{open_action.raw_text}。\n\n"
        f"但现实没有因为一句话让路。{feasibility.get('reason', '')}"
        f"以你现在的资源处境（{resource.get('wealth_label', '未知')}）来说，"
        "这一步不能直接变成成交、产权、钥匙或资产。\n\n"
        "它可以变成一条可玩的路线：\n"
        f"{path_text}\n\n"
        "如果你愿意，下一步可以从打听价格、找担保人、调查产权纠纷或伪装成买家开始。"
    )
    return NarrationProposal(
        text=text,
        claimed_effects=commit.committed_effects,
        source="local-narrator-agent",
    )


def render_location_continuity_note(rule_result):
    location_intent = rule_result.get("location_intent")
    if location_intent == "local_move":
        return f"场景转到{rule_result.get('scene_focus_after')}，但你仍在{rule_result.get('location_after')}。"
    if location_intent == "leave_scene":
        return f"你离开{rule_result.get('scene_focus_before')}，回到{rule_result.get('scene_focus_after')}附近。"
    if location_intent == "travel_request":
        destination = rule_result.get("travel_destination") or "远方"
        return (
            f"{destination}已经成为明确目的地，但这一步只是筹备路线和交通；"
            f"你仍在{rule_result.get('location_after')}。"
        )
    return ""
