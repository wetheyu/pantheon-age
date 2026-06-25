"""Local memory store for Phase 5 Agentic Runtime."""

import hashlib

from .contracts import MEMORY_BUCKETS, MemoryRecord
from .validators import validate_memory_candidate


MEMORY_TYPE_BUCKETS = {
    "player_memory": "player_known",
    "npc_memory": "npc_known",
    "location_memory": "location",
    "quest_memory": "quest",
    "world_event_memory": "quest",
    "faction_memory": "quest",
    "secret_memory": "secret",
}


def commit_memory_candidates(state, candidates):
    """Persist validated memory candidates into the state's local memory store."""
    ensure_memory_store(state)
    committed_records = []
    known_ids = {
        record.get("record_id")
        for records in state.agentic_memory.values()
        for record in records
    }

    for candidate in candidates:
        if not candidate.should_persist:
            continue
        validation = validate_memory_candidate(candidate)
        if not validation.is_valid:
            continue

        record = build_memory_record(candidate)
        if record.record_id in known_ids:
            continue

        state.agentic_memory[record.bucket].append(record.to_dict())
        known_ids.add(record.record_id)
        committed_records.append(record)

    return tuple(committed_records)


def ensure_memory_store(state):
    if not hasattr(state, "agentic_memory") or state.agentic_memory is None:
        state.agentic_memory = {}

    for bucket in MEMORY_BUCKETS:
        state.agentic_memory.setdefault(bucket, [])

    return state.agentic_memory


def build_memory_record(candidate):
    bucket = bucket_for_candidate(candidate)
    return MemoryRecord(
        record_id=record_id_for_candidate(candidate, bucket),
        bucket=bucket,
        memory_type=candidate.memory_type,
        subject=candidate.subject,
        content=candidate.content,
        authority_level=candidate.authority_level,
        visibility=candidate.visibility,
        source_event=candidate.source_event,
        confidence=candidate.confidence,
        source=candidate.source,
    )


def bucket_for_candidate(candidate):
    if candidate.visibility == "system_secret" or candidate.memory_type == "secret_memory":
        return "secret"
    if candidate.visibility == "npc_known" or candidate.memory_type == "npc_memory":
        return "npc_known"
    return MEMORY_TYPE_BUCKETS.get(candidate.memory_type, "player_known")


def record_id_for_candidate(candidate, bucket):
    raw = "|".join(
        (
            bucket,
            candidate.memory_type,
            candidate.subject,
            candidate.content,
            candidate.source_event,
        )
    )
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def memory_bucket_records(state, bucket):
    ensure_memory_store(state)
    return tuple(MemoryRecord.from_dict(record) for record in state.agentic_memory[bucket])


def memory_store_summary(state):
    ensure_memory_store(state)
    return {bucket: len(state.agentic_memory[bucket]) for bucket in MEMORY_BUCKETS}
