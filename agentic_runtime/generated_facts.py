"""Validated generated fact commit helpers for Phase 6."""

from .contracts import GeneratedFactProposal, MemoryCandidate
from .memory_store import commit_memory_candidates
from .validators import validate_generated_fact_proposal, validate_memory_candidate


FACT_TYPE_MEMORY_TYPES = {
    "npc": "player_memory",
    "location": "location_memory",
    "rumor": "quest_memory",
    "event": "world_event_memory",
    "organization": "quest_memory",
    "relationship": "faction_memory",
    "item": "quest_memory",
    "secret": "secret_memory",
}


def commit_generated_fact_proposals(state, proposals, commit):
    """Persist generated facts only after explicit validation and conversion.

    Temporary NPC/Event/Item proposals do not become truth by existing. A caller
    must build GeneratedFactProposal objects, then this function validates them
    against the committed rule result before converting them to memory records.
    """
    memory_candidates = []
    for proposal in proposals:
        validation = validate_generated_fact_proposal(proposal, commit)
        if not validation.is_valid:
            continue

        candidate = generated_fact_to_memory_candidate(proposal, commit)
        candidate_validation = validate_memory_candidate(candidate)
        if candidate_validation.is_valid:
            memory_candidates.append(candidate)

    return commit_memory_candidates(state, tuple(memory_candidates))


def generated_fact_to_memory_candidate(proposal, commit):
    source_event = proposal.source_event or f"turn_{commit.rule_result.get('turn', 0)}"
    return MemoryCandidate(
        memory_type=memory_type_for_generated_fact(proposal),
        subject=proposal.subject,
        content=content_with_evidence(proposal),
        authority_level=proposal.authority_level,
        visibility=proposal.visibility,
        should_persist=True,
        source_event=source_event,
        confidence=proposal.confidence,
        source="generated-fact-commit",
    )


def memory_type_for_generated_fact(proposal):
    if proposal.fact_type == "npc" and proposal.visibility == "npc_known":
        return "npc_memory"
    return FACT_TYPE_MEMORY_TYPES.get(proposal.fact_type, "quest_memory")


def content_with_evidence(proposal):
    if not proposal.evidence:
        return proposal.content
    return f"{proposal.content}（依据：{'；'.join(proposal.evidence)}）"
