"""Game session routes."""

from fastapi import APIRouter

from phase2_api.schemas import (
    ActionRequest,
    ActionResponse,
    GameCreateRequest,
    GameCreateResponse,
    GameDeleteResponse,
    GameEventsResponse,
    GameListResponse,
    GameStateResponse,
)
from phase2_api.services.session_store import (
    create_game_session,
    delete_game_session,
    get_game_state,
    list_game_events,
    list_game_sessions,
    submit_game_action,
)


router = APIRouter(tags=["games"])


@router.post("/games", response_model=GameCreateResponse)
def create_game(request: GameCreateRequest):
    game_id, state, opening_text = create_game_session(request.name, request.class_id, request.god)
    return GameCreateResponse(
        game_id=game_id,
        state=state.to_public_dict(),
        opening_text=opening_text,
    )


@router.get("/games", response_model=GameListResponse)
def list_games():
    return GameListResponse(games=list_game_sessions())


@router.get("/games/{game_id}", response_model=GameStateResponse)
def read_game(game_id: str):
    state = get_game_state(game_id)
    return GameStateResponse(game_id=game_id, state=state.to_public_dict())


@router.get("/games/{game_id}/events", response_model=GameEventsResponse)
def read_game_events(game_id: str):
    return GameEventsResponse(game_id=game_id, events=list_game_events(game_id))


@router.delete("/games/{game_id}", response_model=GameDeleteResponse)
def delete_game(game_id: str):
    delete_game_session(game_id)
    return GameDeleteResponse(game_id=game_id, deleted=True)


@router.post("/games/{game_id}/actions", response_model=ActionResponse)
def create_action(game_id: str, request: ActionRequest):
    response = submit_game_action(game_id, request.text)
    return ActionResponse(game_id=game_id, response=response.to_dict())
