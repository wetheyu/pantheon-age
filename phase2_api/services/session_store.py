"""Game session service for the Phase 2 API.

Phase 3 persists sessions through a SQLite repository while keeping the public
API route shape unchanged.
"""

from uuid import uuid4

from fastapi import HTTPException

from phase1_cli.character import build_character
from phase1_cli.data import CLASSES, GODS
from phase1_cli.game_service import handle_player_input
from phase1_cli.game_state import GameState
from phase1_cli.scenarios import (
    WORLD_GAME_MODE,
    background_options,
    city_names_for_origin,
    configure_character_for_game_mode,
    ethnicity_names_for_origin,
    origin_country_ids,
    get_origin_country,
    normalize_game_mode,
)
from phase1_cli.story import render_opening
from phase3_persistence.errors import PersistenceError
from phase3_persistence.sqlite_repository import GameSessionRepository


_REPOSITORY = GameSessionRepository()


def configure_storage(db_path):
    """Point the session service at another SQLite database path."""
    global _REPOSITORY
    _REPOSITORY = GameSessionRepository(db_path)


def validate_character_input(class_id, god):
    if class_id not in CLASSES:
        raise HTTPException(status_code=400, detail=f"Unknown class_id: {class_id}")

    if god not in GODS:
        raise HTTPException(status_code=400, detail=f"Unknown god: {god}")


def build_api_character(name, class_id, god):
    validate_character_input(class_id, god)
    return build_character(name.strip() or "无名冒险者", class_id, god)


def list_origin_options():
    countries = []
    for country_id in origin_country_ids():
        country = get_origin_country(country_id)
        countries.append(
            {
                "country_id": country_id,
                "name": country["name"],
                "formal_name": country["formal_name"],
                "identity": country["identity"],
                "summary": country["summary"],
                "cities": [dict(city) for city in country["cities"]],
                "ethnicities": [dict(ethnicity) for ethnicity in country.get("ethnicities", ())],
            }
        )
    return {
        "countries": countries,
        "backgrounds": [dict(background) for background in background_options()],
    }


def validate_game_mode(game_mode):
    raw_mode = str(game_mode or "tutorial").strip().lower()
    accepted = {"tutorial", "world", "agentic", "open_world", "open-world"}
    if raw_mode not in accepted:
        raise HTTPException(status_code=400, detail=f"Unknown game_mode: {game_mode}")
    return normalize_game_mode(raw_mode)


def validate_world_origin_input(origin_country_id=None, origin_city=None, origin_ethnicity=None, background_id=None):
    country_id = origin_country_id or "albion"
    if country_id not in origin_country_ids():
        raise HTTPException(status_code=400, detail=f"Unknown origin_country_id: {origin_country_id}")

    if origin_city and origin_city not in city_names_for_origin(country_id):
        raise HTTPException(status_code=400, detail=f"Unknown origin_city for {country_id}: {origin_city}")

    ethnicities = ethnicity_names_for_origin(country_id)
    if origin_ethnicity and ethnicities and origin_ethnicity not in ethnicities:
        raise HTTPException(status_code=400, detail=f"Unknown origin_ethnicity for {country_id}: {origin_ethnicity}")

    background_ids = {background["background_id"] for background in background_options()}
    if background_id and background_id not in background_ids:
        raise HTTPException(status_code=400, detail=f"Unknown background_id: {background_id}")


def create_game_session(
    name,
    class_id,
    god,
    game_mode="tutorial",
    origin_country_id=None,
    origin_city=None,
    origin_ethnicity=None,
    background_id=None,
):
    mode = validate_game_mode(game_mode)
    if mode == WORLD_GAME_MODE:
        validate_world_origin_input(origin_country_id, origin_city, origin_ethnicity, background_id)

    character = build_api_character(name, class_id, god)
    configure_character_for_game_mode(
        character,
        mode,
        origin_country_id=origin_country_id,
        origin_city=origin_city,
        origin_ethnicity=origin_ethnicity,
        background_id=background_id,
    )
    state = GameState(character)
    game_id = uuid4().hex
    _save_state(game_id, state)
    return game_id, state, render_opening(character)


def build_game_setup_payload(state):
    player = state.player
    flags = player.flags
    return {
        "game_mode": flags.get("game_mode", "tutorial"),
        "scenario_id": flags.get("scenario_id"),
        "origin": {
            "country_id": flags.get("origin_country_id"),
            "country": flags.get("origin_country"),
            "formal_name": flags.get("origin_country_formal_name"),
            "identity": flags.get("origin_identity"),
            "ethnicity": flags.get("origin_ethnicity"),
            "city": flags.get("origin_city"),
            "city_title": flags.get("origin_city_title"),
            "background_id": flags.get("background_id"),
            "background_name": flags.get("background_name"),
            "wealth_level": flags.get("wealth_level"),
            "wealth_label": flags.get("wealth_label"),
        },
        "current_scene_focus": flags.get("current_scene_focus"),
        "opening_profile": flags.get("opening_profile"),
    }


def summarize_game_session(game_id, state):
    player = state.player
    return {
        "game_id": game_id,
        "player_name": player.name,
        "class_id": player.class_id,
        "class_name": player.class_name,
        "god": player.god,
        "current_location": state.current_location,
        "turn": state.turn,
        "is_game_over": state.is_game_over,
    }


def list_game_sessions():
    sessions = _read_sessions()
    return [summarize_game_session(game_id, state) for game_id, state in sessions]


def get_game_state(game_id):
    state = _read_state(game_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")
    return state


def delete_game_session(game_id):
    if not _delete_state(game_id):
        raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")


def submit_game_action(game_id, text):
    state = get_game_state(game_id)
    response = handle_player_input(state, text)
    _save_state(game_id, state)
    return response


def build_action_api_view(response, include_debug=False):
    legacy_payload = response.to_dict(include_runtime=include_debug)
    mechanics = {
        "kind": response.kind,
        "consumes_turn": response.consumes_turn,
        "rule_result": response.rule_result,
        "action": response.action,
        "ending_text": response.ending_text,
        "committed_effects": committed_effects_from_response(response),
        "roll": (response.rule_result or {}).get("roll") if response.rule_result else None,
        "state_changes": list((response.rule_result or {}).get("state_changes", [])),
        "new_clues": list((response.rule_result or {}).get("new_clues", [])),
    }
    return {
        "response": legacy_payload,
        "story": response.text,
        "state": response.state.to_public_dict(),
        "mechanics": mechanics,
        "debug": build_action_debug_payload(response) if include_debug else None,
    }


def committed_effects_from_response(response):
    runtime = response.llm_runtime or {}
    agentic = runtime.get("agentic_runtime", {})
    commit = agentic.get("commit", {})
    return list(commit.get("committed_effects", []))


def build_action_debug_payload(response):
    runtime = response.llm_runtime or {}
    return {
        "observability": build_observability_payload(response),
        "llm_runtime": runtime,
        "rule_result": response.rule_result,
        "action": response.action,
    }


def build_observability_payload(response):
    runtime = response.llm_runtime or {}
    if runtime.get("phase") == "phase5-agentic-runtime":
        return runtime.get("observability", {})

    providers = runtime.get("providers", {})
    action_candidate = runtime.get("action_candidate", {})
    narration = runtime.get("narration", {})
    return {
        "schema_version": "10.1",
        "runtime_phase": "phase4-structured-runtime",
        "providers": {
            "llm_enabled": providers.get("llm_enabled"),
            "model": providers.get("model"),
            "reason": providers.get("reason"),
            "action_provider": providers.get("action_provider"),
            "narration_provider": providers.get("narration_provider"),
        },
        "fallbacks": {
            "error_count": len(runtime.get("errors", [])),
            "errors": list(runtime.get("errors", [])),
            "action_candidate_used_fallback": action_candidate.get("used_fallback"),
            "narration_used_fallback": narration.get("used_fallback"),
        },
    }


def list_game_events(game_id):
    events = _read_events(game_id)
    if events is None:
        raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")
    return events


def clear_sessions():
    """Clear persisted sessions for tests."""
    try:
        _REPOSITORY.clear()
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _save_state(game_id, state):
    try:
        _REPOSITORY.save(game_id, state)
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _read_state(game_id):
    try:
        return _REPOSITORY.get(game_id)
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _read_sessions():
    try:
        return _REPOSITORY.list()
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _delete_state(game_id):
    try:
        return _REPOSITORY.delete(game_id)
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _read_events(game_id):
    try:
        return _REPOSITORY.list_events(game_id)
    except PersistenceError as error:
        raise _persistence_http_error(error) from error


def _persistence_http_error(error):
    return HTTPException(status_code=500, detail=f"Persistence error: {error}")
