"""Safe observability payloads for Agentic Runtime turns.

This module turns the full internal runtime result into a compact trace that is
safe to expose through API debug responses. It intentionally avoids prompt text,
raw LLM payloads, API keys, and hidden memory.
"""


OBSERVABILITY_SCHEMA_VERSION = "10.1"


def build_agentic_observability_payload(result):
    trace = result.runtime_trace.to_dict()
    steps = trace.get("steps", [])
    validations = result.validations
    failed_validations = [
        {
            "name": name,
            "errors": list(validation.errors),
        }
        for name, validation in validations.items()
        if not validation.is_valid
    ]
    commit = result.commit
    rule_result = commit.rule_result or {}

    return {
        "schema_version": OBSERVABILITY_SCHEMA_VERSION,
        "runtime_phase": "phase5-agentic-runtime",
        "trace": {
            "branch": trace.get("branch"),
            "total_ms": trace.get("total_ms"),
            "steps": steps,
            "slowest_step": slowest_step(steps),
        },
        "providers": safe_provider_summary(result.providers),
        "fallbacks": {
            "error_count": len(result.errors),
            "errors": list(result.errors),
        },
        "validations": {
            "total": len(validations),
            "failed": failed_validations,
            "failed_count": len(failed_validations),
        },
        "commit": {
            "committed": commit.committed,
            "committed_effects": list(commit.committed_effects),
            "rejected_effects": list(commit.rejected_effects),
            "action_type": result.adjudication.action_type,
            "rule_intent": rule_result.get("intent"),
            "location_before": rule_result.get("location_before"),
            "location_after": rule_result.get("location_after"),
            "scene_focus_before": rule_result.get("scene_focus_before"),
            "scene_focus_after": rule_result.get("scene_focus_after"),
            "roll": compact_roll(rule_result.get("roll")),
            "state_change_count": len(rule_result.get("state_changes", [])),
            "new_clue_count": len(rule_result.get("new_clues", [])),
        },
        "memory": {
            "retrieval_source": result.memory_retrieval.source,
            "player_known_count": len(result.memory_retrieval.player_known),
            "location_context_count": len(result.memory_retrieval.location_context),
            "recent_event_count": len(result.memory_retrieval.recent_events),
            "secret_context_count": len(result.memory_retrieval.hidden_context),
            "candidate_count": len(result.memory_candidates),
            "written_record_count": len(result.memory_records),
            "written_buckets": count_records_by_bucket(result.memory_records),
        },
        "generated_content": {
            "temporary_content_count": len(result.temporary_content),
            "npc_count": len(result.npcs),
            "event_count": len(result.events),
            "item_count": len(result.items),
        },
        "narration": {
            "source": result.narration.source,
            "length": len(result.narration.text),
            "claimed_effect_count": len(result.narration.claimed_effects),
        },
    }


def slowest_step(steps):
    if not steps:
        return None
    return max(steps, key=lambda step: step.get("elapsed_ms", 0))


def safe_provider_summary(providers):
    return {
        "llm_enabled": providers.get("llm_enabled"),
        "model": providers.get("model"),
        "reason": providers.get("reason"),
        "memory_retriever": providers.get("memory_retriever"),
        "intent_agent": providers.get("intent_agent"),
        "rule_arbiter": providers.get("rule_arbiter"),
        "turn_director": providers.get("turn_director"),
        "world_bundle": providers.get("world_bundle"),
        "narrator_agent": providers.get("narrator_agent"),
    }


def compact_roll(roll):
    if not roll:
        return None
    return {
        "base_roll": roll.get("base_roll"),
        "modifier": roll.get("modifier"),
        "total": roll.get("total"),
        "dc": roll.get("dc"),
        "success": roll.get("success"),
        "outcome_label": roll.get("outcome_label"),
        "risk_label": roll.get("risk_label"),
    }


def count_records_by_bucket(records):
    counts = {}
    for record in records:
        counts[record.bucket] = counts.get(record.bucket, 0) + 1
    return counts
