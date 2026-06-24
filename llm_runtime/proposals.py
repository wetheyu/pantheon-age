"""Scene, event, and generated-content proposal validation for Phase 4."""

from .contracts import (
    AUTHORITY_LEVELS,
    GENERATED_CONTENT_TYPES,
    EventProposal,
    GeneratedContentProposal,
    ProposalValidation,
    SceneProposal,
)


DISPLAY_ONLY_AUTHORITY_LEVELS = frozenset({"flavor", "temporary"})


def validate_scene_proposal(proposal):
    """Validate a scene proposal before it can be shown or persisted."""
    errors = []

    if not isinstance(proposal.title, str) or not proposal.title.strip():
        errors.append("Scene title is empty.")

    if not isinstance(proposal.description, str) or not proposal.description.strip():
        errors.append("Scene description is empty.")

    errors.extend(validate_common_proposal_fields(proposal, "Scene"))

    return ProposalValidation(is_valid=not errors, errors=tuple(errors))


def validate_event_proposal(proposal):
    """Validate an event proposal before it can be shown or persisted."""
    errors = []

    if not isinstance(proposal.event_type, str) or not proposal.event_type.strip():
        errors.append("Event type is empty.")

    if not isinstance(proposal.summary, str) or not proposal.summary.strip():
        errors.append("Event summary is empty.")

    errors.extend(validate_common_proposal_fields(proposal, "Event"))

    return ProposalValidation(is_valid=not errors, errors=tuple(errors))


def validate_generated_content_proposal(proposal):
    """Validate open-ended generated content before display or persistence."""
    errors = []

    if not isinstance(proposal.content_type, str) or not proposal.content_type.strip():
        errors.append("Generated content type is empty.")
    elif proposal.content_type not in GENERATED_CONTENT_TYPES:
        errors.append(f"Unsupported generated content type: {proposal.content_type}")

    if not isinstance(proposal.name, str) or not proposal.name.strip():
        errors.append("Generated content name is empty.")

    if not isinstance(proposal.description, str) or not proposal.description.strip():
        errors.append("Generated content description is empty.")

    errors.extend(validate_common_proposal_fields(proposal, "Generated content"))

    if proposal.claimed_inventory_changes:
        errors.append("Generated content proposal cannot change inventory.")

    if proposal.claimed_relationship_changes:
        errors.append("Generated content proposal cannot commit relationship changes.")

    if proposal.claimed_faction_changes:
        errors.append("Generated content proposal cannot commit faction changes.")

    return ProposalValidation(is_valid=not errors, errors=tuple(errors))


def validate_common_proposal_fields(proposal, label):
    errors = []

    location = getattr(proposal, "location", None)
    if location is not None:
        if not isinstance(location, str) or not location.strip():
            errors.append(f"{label} location is empty.")

    if proposal.authority_level not in AUTHORITY_LEVELS:
        errors.append(f"Unknown authority level: {proposal.authority_level}")
    elif proposal.authority_level not in DISPLAY_ONLY_AUTHORITY_LEVELS:
        errors.append(
            f"{label} authority level requires a later validator or memory layer: "
            f"{proposal.authority_level}"
        )

    if proposal.claimed_facts:
        errors.append(f"{label} proposal cannot commit persistent facts in Phase 4.4.")

    if proposal.claimed_state_changes:
        errors.append(f"{label} proposal cannot claim mechanical state changes.")

    if proposal.claimed_new_clues:
        errors.append(f"{label} proposal cannot grant clues.")

    if getattr(proposal, "claimed_location_after", None):
        errors.append(f"{label} proposal cannot move the player.")

    return errors
