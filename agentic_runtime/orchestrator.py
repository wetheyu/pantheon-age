"""Phase 5 Agentic Runtime orchestrator."""

from time import perf_counter

from llm_runtime.providers import OpenAIProviderError

from .contracts import AgenticTurnResult, NarrationProposal, RuntimeStep, RuntimeTrace
from .providers import (
    LocalIntentAgentProvider,
    LocalEventAgentProvider,
    LocalItemAgentProvider,
    LocalNPCAgentProvider,
    LocalNarratorAgentProvider,
    LocalRuleArbiterProvider,
    build_agentic_providers_from_env,
)
from .memory_store import commit_memory_candidates
from .state_commit import commit_adjudication
from .validators import (
    validate_event_proposal,
    validate_item_proposal,
    validate_memory_candidate,
    validate_npc_proposal,
    validate_narration_proposal,
    validate_open_action,
    validate_rule_adjudication,
    validate_state_commit,
    validate_temporary_content,
)


class RuntimeTracer:
    def __init__(self):
        self.started_at = perf_counter()
        self.branch = "unknown"
        self.steps = []

    def set_branch(self, branch):
        self.branch = branch

    def measure(self, name, func, *args, **kwargs):
        step_started_at = perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed_ms = round((perf_counter() - step_started_at) * 1000, 2)
            self.steps.append(RuntimeStep(name=name, elapsed_ms=elapsed_ms))

    def to_trace(self):
        total_ms = round((perf_counter() - self.started_at) * 1000, 2)
        return RuntimeTrace(
            branch=self.branch,
            total_ms=total_ms,
            steps=tuple(self.steps),
        )


def run_agentic_turn(state, user_text, providers=None):
    tracer = RuntimeTracer()
    providers = providers or build_agentic_providers_from_env()
    memory_retrieval = tracer.measure(
        "memory_retrieval",
        providers.memory_retriever.retrieve_memory,
        state,
        user_text,
    )
    runtime_errors = []

    if providers.turn_director:
        directed_result = run_turn_director_path(
            state,
            user_text,
            providers,
            memory_retrieval,
            runtime_errors,
            tracer,
        )
        if directed_result is not None:
            return directed_result
        tracer.set_branch("turn_director_fallback_local")
    else:
        tracer.set_branch(branch_for_manual_path(providers))

    try:
        open_action = tracer.measure(
            "intent_agent",
            providers.intent_agent.propose_open_action,
            user_text,
            state,
            memory_retrieval,
        )
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        open_action = tracer.measure(
            "intent_agent_fallback",
            LocalIntentAgentProvider().propose_open_action,
            user_text,
            state,
            memory_retrieval,
        )

    try:
        adjudication = tracer.measure(
            "rule_arbiter",
            providers.rule_arbiter.propose_rule_adjudication,
            state,
            open_action,
        )
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        adjudication = tracer.measure(
            "rule_arbiter_fallback",
            LocalRuleArbiterProvider().propose_rule_adjudication,
            state,
            open_action,
        )

    validations = {
        "open_action": validate_open_action(open_action),
    }
    adjudication_validation = validate_rule_adjudication(adjudication)
    validations["adjudication"] = adjudication_validation
    if not adjudication_validation.is_valid:
        runtime_errors.append(
            "Rule arbiter proposal failed validation: " + "; ".join(adjudication_validation.errors)
        )
        adjudication = LocalRuleArbiterProvider().propose_rule_adjudication(state, open_action)
        validations["adjudication_fallback"] = validate_rule_adjudication(adjudication)

    commit = tracer.measure("state_commit", commit_adjudication, state, adjudication)
    validations["commit"] = validate_state_commit(commit)

    temporary_content = tracer.measure(
        "scene_agent",
        providers.scene_agent.propose_temporary_content,
        state,
        open_action,
        memory_retrieval,
    )
    valid_temporary_content = []
    for index, content in enumerate(temporary_content):
        validation = validate_temporary_content(content)
        validations[f"temporary_content_{index}"] = validation
        if validation.is_valid:
            valid_temporary_content.append(content)

    memory_candidates = tracer.measure(
        "memory_curator",
        providers.memory_curator.curate_memory,
        open_action,
        adjudication,
        commit,
    )
    valid_memory_candidates = []
    for index, candidate in enumerate(memory_candidates):
        validation = validate_memory_candidate(candidate)
        validations[f"memory_candidate_{index}"] = validation
        if validation.is_valid:
            valid_memory_candidates.append(candidate)

    memory_records = tracer.measure(
        "memory_commit",
        commit_memory_candidates,
        state,
        valid_memory_candidates,
    )

    bundle_scenes = bundle_npcs = bundle_events = bundle_items = ()
    bundle_narration = None
    if providers.world_bundle:
        try:
            (
                bundle_scenes,
                bundle_npcs,
                bundle_events,
                bundle_items,
                bundle_narration,
            ) = tracer.measure(
                "world_bundle",
                providers.world_bundle.propose_world_bundle,
                state,
                memory_retrieval,
                open_action,
                tuple(valid_temporary_content),
                adjudication,
                commit,
                memory_candidates,
            )
        except OpenAIProviderError as exc:
            runtime_errors.append(str(exc))

    if bundle_scenes:
        valid_bundle_scenes = []
        for index, content in enumerate(bundle_scenes):
            validation = validate_temporary_content(content)
            validations[f"bundle_scene_{index}"] = validation
            if validation.is_valid:
                valid_bundle_scenes.append(content)
        if valid_bundle_scenes:
            valid_temporary_content = valid_bundle_scenes

    if bundle_npcs or bundle_events or bundle_items:
        npc_proposals = bundle_npcs
        event_proposals = bundle_events
        item_proposals = bundle_items
    else:
        npc_proposals, event_proposals, item_proposals = tracer.measure(
            "separate_world_content",
            generate_separate_world_content,
            providers,
            state,
            open_action,
            memory_retrieval,
            runtime_errors,
        )

    valid_npcs = validate_npcs(npc_proposals, validations)
    valid_events = validate_events(event_proposals, validations)
    valid_items = validate_items(item_proposals, validations)

    if providers.world_bundle and npc_proposals and not valid_npcs:
        fallback_npcs = LocalNPCAgentProvider().propose_npcs(state, open_action, memory_retrieval)
        valid_npcs = validate_npcs(fallback_npcs, validations, prefix="npc_fallback")
    if providers.world_bundle and event_proposals and not valid_events:
        fallback_events = LocalEventAgentProvider().propose_events(
            state,
            open_action,
            memory_retrieval,
            npcs=tuple(valid_npcs),
        )
        valid_events = validate_events(fallback_events, validations, prefix="event_fallback")
    if providers.world_bundle and item_proposals and not valid_items:
        fallback_items = LocalItemAgentProvider().propose_items(state, open_action, memory_retrieval)
        valid_items = validate_items(fallback_items, validations, prefix="item_fallback")

    narration = bundle_narration
    if narration is None:
        narration = tracer.measure(
            "narrator",
            narrate_with_provider,
            providers,
            state,
            memory_retrieval,
            open_action,
            tuple(valid_temporary_content),
            adjudication,
            commit,
            memory_candidates,
            tuple(valid_npcs),
            tuple(valid_events),
            tuple(valid_items),
            runtime_errors,
        )

    narration_validation = validate_narration_proposal(narration, commit)
    validations["narration"] = narration_validation
    if not narration_validation.is_valid:
        runtime_errors.extend(narration_validation.errors)
        narration = LocalNarratorAgentProvider().narrate_turn(
            state,
            memory_retrieval,
            open_action,
            tuple(valid_temporary_content),
            adjudication,
            commit,
            memory_candidates,
            npc_proposals=tuple(valid_npcs),
            event_proposals=tuple(valid_events),
            item_proposals=tuple(valid_items),
        )
        validations["narration_fallback"] = validate_narration_proposal(narration, commit)

    return AgenticTurnResult(
        providers=providers.to_dict(),
        errors=tuple(runtime_errors),
        memory_retrieval=memory_retrieval,
        open_action=open_action,
        temporary_content=tuple(valid_temporary_content),
        npcs=tuple(valid_npcs),
        events=tuple(valid_events),
        items=tuple(valid_items),
        adjudication=adjudication,
        validations=validations,
        commit=commit,
        memory_candidates=memory_candidates,
        memory_records=memory_records,
        narration=narration,
        runtime_trace=tracer.to_trace(),
    )


def branch_for_manual_path(providers):
    if not providers.llm_enabled:
        return "local"
    if providers.world_bundle:
        return "legacy_world_bundle"
    return "full_multi_agent"


def run_turn_director_path(state, user_text, providers, memory_retrieval, runtime_errors, tracer):
    branch = branch_for_director_provider(providers.turn_director)
    tracer.set_branch(branch)
    try:
        directed_turn = tracer.measure(
            f"{branch}_provider",
            providers.turn_director.propose_turn,
            state,
            user_text,
            memory_retrieval,
        )
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        return None

    open_action = directed_turn.open_action
    adjudication = directed_turn.adjudication
    validations = {
        "open_action": validate_open_action(open_action),
    }
    if not validations["open_action"].is_valid:
        runtime_errors.append(
            "Turn Director open action failed validation: "
            + "; ".join(validations["open_action"].errors)
        )
        return None

    adjudication_validation = validate_rule_adjudication(adjudication)
    validations["adjudication"] = adjudication_validation
    if not adjudication_validation.is_valid:
        runtime_errors.append(
            "Turn Director adjudication failed validation: "
            + "; ".join(adjudication_validation.errors)
        )
        return None

    valid_temporary_content = validate_or_fallback_temporary_content(
        directed_turn.temporary_content,
        providers,
        state,
        open_action,
        memory_retrieval,
        validations,
    )
    valid_npcs = validate_or_fallback_npcs(
        directed_turn.npcs,
        state,
        open_action,
        memory_retrieval,
        validations,
    )
    valid_events = validate_or_fallback_events(
        directed_turn.events,
        state,
        open_action,
        memory_retrieval,
        valid_npcs,
        validations,
    )
    valid_items = validate_or_fallback_items(
        directed_turn.items,
        state,
        open_action,
        memory_retrieval,
        validations,
    )

    commit = tracer.measure("state_commit", commit_adjudication, state, adjudication)
    validations["commit"] = validate_state_commit(commit)

    memory_candidates = tracer.measure(
        "memory_curator",
        providers.memory_curator.curate_memory,
        open_action,
        adjudication,
        commit,
    )
    valid_memory_candidates = []
    for index, candidate in enumerate(memory_candidates):
        validation = validate_memory_candidate(candidate)
        validations[f"memory_candidate_{index}"] = validation
        if validation.is_valid:
            valid_memory_candidates.append(candidate)

    memory_records = tracer.measure(
        "memory_commit",
        commit_memory_candidates,
        state,
        valid_memory_candidates,
    )

    if branch == "creative_gm" and commit.rule_result.get("feasibility", {}).get("blocked"):
        narration = build_creative_gm_safety_fallback(
            open_action,
            commit,
            tuple(valid_npcs),
            tuple(valid_events),
            tuple(valid_items),
        )
    else:
        narration = directed_turn.narration_for_commit(commit)
    narration_validation = validate_narration_proposal(narration, commit)
    validations["narration"] = narration_validation
    if not narration_validation.is_valid:
        runtime_errors.extend(narration_validation.errors)
        if branch == "creative_gm":
            narration = build_creative_gm_safety_fallback(
                open_action,
                commit,
                tuple(valid_npcs),
                tuple(valid_events),
                tuple(valid_items),
            )
        else:
            narration = LocalNarratorAgentProvider().narrate_turn(
                state,
                memory_retrieval,
                open_action,
                tuple(valid_temporary_content),
                adjudication,
                commit,
                memory_candidates,
                npc_proposals=tuple(valid_npcs),
                event_proposals=tuple(valid_events),
                item_proposals=tuple(valid_items),
            )
        validations["narration_fallback"] = validate_narration_proposal(narration, commit)

    return AgenticTurnResult(
        providers=providers.to_dict(),
        errors=tuple(runtime_errors),
        memory_retrieval=memory_retrieval,
        open_action=open_action,
        temporary_content=tuple(valid_temporary_content),
        npcs=tuple(valid_npcs),
        events=tuple(valid_events),
        items=tuple(valid_items),
        adjudication=adjudication,
        validations=validations,
        commit=commit,
        memory_candidates=memory_candidates,
        memory_records=memory_records,
        narration=narration,
        runtime_trace=tracer.to_trace(),
    )


def branch_for_director_provider(provider):
    if getattr(provider, "provider_name", "") == "openai-creative-gm-agent":
        return "creative_gm"
    return "turn_director"


def build_creative_gm_safety_fallback(open_action, commit, npcs=(), events=(), items=()):
    """Keep Creative GM fallback player-facing instead of exposing sidecar labels."""
    rule_result = commit.rule_result
    paragraphs = []
    location_intent = rule_result.get("location_intent")
    scene_after = rule_result.get("scene_focus_after")
    location_after = rule_result.get("location_after")
    feasibility = rule_result.get("feasibility")

    if feasibility and feasibility.get("blocked"):
        resource = feasibility.get("player_resource", {})
        paragraphs.append(f"你当然可以提出这个念头：{open_action.raw_text}。")
        paragraphs.append(
            f"但现实没有被一句话改写。{feasibility.get('reason', '')}"
            f"以你现在的资源处境（{resource.get('wealth_label', '未知')}）来说，"
            "这不能直接变成成交、产权、钥匙或资产。"
        )
        paths = feasibility.get("suggested_paths", ())[:3]
        if paths:
            paragraphs.append("它仍然可以变成一条可玩的路线：" + "；".join(paths) + "。")
        return NarrationProposal(
            text="\n\n".join(paragraph for paragraph in paragraphs if paragraph),
            claimed_effects=(),
            source="creative-gm-safety-fallback",
        )

    if location_intent == "local_move" and scene_after:
        paragraphs.append(f"你顺着自己的打算离开原本停留的位置，转入{scene_after}。")
    elif location_intent == "travel_request":
        destination = rule_result.get("travel_destination") or "远方"
        paragraphs.append(f"你把目的地指向{destination}，但真正启程前，还需要路线、身份和交通工具。")
    elif location_after:
        paragraphs.append(f"你仍在{location_after}，开始落实这个念头：{open_action.raw_text}。")
    else:
        paragraphs.append(f"你开始落实这个念头：{open_action.raw_text}。")

    for npc in npcs[:2]:
        detail = clean_player_facing_sentence(npc.description)
        if npc.name and not npc.name.startswith(("现场人物", "叙事人物")):
            paragraphs.append(join_subject_and_detail(npc.name, detail))
        else:
            paragraphs.append(detail)

    for event in events[:2]:
        paragraphs.append(clean_player_facing_sentence(event.summary))

    for item in items[:1]:
        detail = clean_player_facing_sentence(item.description)
        if item.name and not item.name.startswith(("现场物件", "可疑物件")):
            paragraphs.append(join_subject_and_detail(f"你注意到{item.name}", detail))
        else:
            paragraphs.append(f"你注意到一处值得继续观察的细节：{detail}")

    roll = rule_result.get("roll")
    if roll:
        paragraphs.append(
            "这一步需要判定："
            f"d20={roll.get('base_roll')}，修正={roll.get('modifier')}，"
            f"总计={roll.get('total')}，DC={roll.get('dc')}。"
        )
        if rule_result.get("success"):
            paragraphs.append("结果偏向你这边，但它只打开机会，不会替你直接拿走全部答案。")
        else:
            paragraphs.append("结果没有站在你这边，现场压力随之变重，但事情还没有结束。")
    else:
        paragraphs.append("局势没有立刻给出最终答案，但已经抛出了可以继续追问、观察或利用的线头。")

    return NarrationProposal(
        text="\n\n".join(paragraph for paragraph in paragraphs if paragraph),
        claimed_effects=(),
        source="creative-gm-safety-fallback",
    )


def clean_player_facing_sentence(text):
    clean_text = " ".join(str(text).strip().split())
    clean_text = clean_text.replace("玩家", "你")
    if not clean_text:
        return ""
    if clean_text[-1] not in "。.!！？":
        clean_text += "。"
    return clean_text


def join_subject_and_detail(subject, detail):
    if not detail:
        return subject
    if detail.startswith(subject):
        return detail
    if detail[0] in "，。；：、,.!?！？":
        return f"{subject}{detail}"
    return f"{subject}：{detail}"


def validate_or_fallback_temporary_content(
    temporary_content,
    providers,
    state,
    open_action,
    memory_retrieval,
    validations,
):
    valid_content = []
    for index, content in enumerate(temporary_content):
        validation = validate_temporary_content(content)
        validations[f"temporary_content_{index}"] = validation
        if validation.is_valid:
            valid_content.append(content)
    if valid_content:
        return valid_content

    fallback_content = providers.scene_agent.propose_temporary_content(
        state,
        open_action,
        memory_retrieval,
    )
    for index, content in enumerate(fallback_content):
        validation = validate_temporary_content(content)
        validations[f"temporary_content_fallback_{index}"] = validation
        if validation.is_valid:
            valid_content.append(content)
    return valid_content


def validate_or_fallback_npcs(npc_proposals, state, open_action, memory_retrieval, validations):
    valid_npcs = validate_npcs(npc_proposals, validations)
    if valid_npcs:
        return valid_npcs
    fallback_npcs = LocalNPCAgentProvider().propose_npcs(state, open_action, memory_retrieval)
    return validate_npcs(fallback_npcs, validations, prefix="npc_fallback")


def validate_or_fallback_events(
    event_proposals,
    state,
    open_action,
    memory_retrieval,
    valid_npcs,
    validations,
):
    valid_events = validate_events(event_proposals, validations)
    if valid_events:
        return valid_events
    fallback_events = LocalEventAgentProvider().propose_events(
        state,
        open_action,
        memory_retrieval,
        npcs=tuple(valid_npcs),
    )
    return validate_events(fallback_events, validations, prefix="event_fallback")


def validate_or_fallback_items(item_proposals, state, open_action, memory_retrieval, validations):
    valid_items = validate_items(item_proposals, validations)
    if valid_items:
        return valid_items
    fallback_items = LocalItemAgentProvider().propose_items(state, open_action, memory_retrieval)
    return validate_items(fallback_items, validations, prefix="item_fallback")


def generate_separate_world_content(providers, state, open_action, memory_retrieval, runtime_errors):
    try:
        npc_proposals = providers.npc_agent.propose_npcs(state, open_action, memory_retrieval)
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        npc_proposals = LocalNPCAgentProvider().propose_npcs(state, open_action, memory_retrieval)

    try:
        event_proposals = providers.event_agent.propose_events(
            state,
            open_action,
            memory_retrieval,
            npcs=npc_proposals,
        )
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        event_proposals = LocalEventAgentProvider().propose_events(
            state,
            open_action,
            memory_retrieval,
            npcs=npc_proposals,
        )

    try:
        item_proposals = providers.item_agent.propose_items(state, open_action, memory_retrieval)
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        item_proposals = LocalItemAgentProvider().propose_items(state, open_action, memory_retrieval)

    return npc_proposals, event_proposals, item_proposals


def validate_npcs(npc_proposals, validations, prefix="npc"):
    valid_npcs = []
    for index, npc in enumerate(npc_proposals):
        validation = validate_npc_proposal(npc)
        validations[f"{prefix}_{index}"] = validation
        if validation.is_valid:
            valid_npcs.append(npc)
    return valid_npcs


def validate_events(event_proposals, validations, prefix="event"):
    valid_events = []
    for index, event in enumerate(event_proposals):
        validation = validate_event_proposal(event)
        validations[f"{prefix}_{index}"] = validation
        if validation.is_valid:
            valid_events.append(event)
    return valid_events


def validate_items(item_proposals, validations, prefix="item"):
    valid_items = []
    for index, item in enumerate(item_proposals):
        validation = validate_item_proposal(item)
        validations[f"{prefix}_{index}"] = validation
        if validation.is_valid:
            valid_items.append(item)
    return valid_items


def narrate_with_provider(
    providers,
    state,
    memory_retrieval,
    open_action,
    temporary_content,
    adjudication,
    commit,
    memory_candidates,
    valid_npcs,
    valid_events,
    valid_items,
    runtime_errors,
):
    try:
        return providers.narrator_agent.narrate_turn(
            state,
            memory_retrieval,
            open_action,
            temporary_content,
            adjudication,
            commit,
            memory_candidates,
            npc_proposals=valid_npcs,
            event_proposals=valid_events,
            item_proposals=valid_items,
        )
    except OpenAIProviderError as exc:
        runtime_errors.append(str(exc))
        return LocalNarratorAgentProvider().narrate_turn(
            state,
            memory_retrieval,
            open_action,
            temporary_content,
            adjudication,
            commit,
            memory_candidates,
            npc_proposals=valid_npcs,
            event_proposals=valid_events,
            item_proposals=valid_items,
        )
