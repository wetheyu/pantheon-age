"""Safe narration proposal handling for Phase 4."""

from .contracts import NarrationProposal, NarrationResult, NarrationValidation


def build_template_narration_proposal(game_response):
    """Build a safe proposal from the existing deterministic story text."""
    rule_result = game_response.rule_result or {}
    return NarrationProposal(
        text=game_response.text,
        claimed_state_changes=tuple(rule_result.get("state_changes", [])),
        claimed_new_clues=tuple(rule_result.get("new_clues", [])),
        claimed_location_after=rule_result.get("location_after"),
        source="template",
    )


def validate_narration_proposal(game_response, proposal):
    """Validate structured claims before narration is trusted."""
    errors = []
    rule_result = game_response.rule_result or {}

    if not proposal.text.strip():
        errors.append("Narration text is empty.")

    allowed_state_changes = set(rule_result.get("state_changes", []))
    for claimed_change in proposal.claimed_state_changes:
        if claimed_change not in allowed_state_changes:
            errors.append(f"Unapproved state change claim: {claimed_change}")

    allowed_clues = set(rule_result.get("new_clues", []))
    for claimed_clue in proposal.claimed_new_clues:
        if claimed_clue not in allowed_clues:
            errors.append(f"Unapproved clue claim: {claimed_clue}")

    allowed_location_after = rule_result.get("location_after")
    if proposal.claimed_location_after and proposal.claimed_location_after != allowed_location_after:
        errors.append(f"Unapproved location claim: {proposal.claimed_location_after}")

    return NarrationValidation(is_valid=not errors, errors=tuple(errors))


def render_safe_narration(game_response, proposer=None, provider=None):
    """Return proposed narration only if validation passes."""
    if provider is not None:
        proposal = provider.propose_narration(game_response)
    elif proposer is None:
        proposal = build_template_narration_proposal(game_response)
    else:
        proposal = proposer(game_response)

    validation = validate_narration_proposal(game_response, proposal)
    if validation.is_valid:
        return NarrationResult(
            text=proposal.text,
            proposal=proposal,
            validation=validation,
            used_fallback=False,
        )

    fallback = build_template_narration_proposal(game_response)
    return NarrationResult(
        text=fallback.text,
        proposal=proposal,
        validation=validation,
        used_fallback=True,
    )
