"""Game session routes."""

from fastapi import APIRouter

from phase2_api.schemas import (
    ActionRequest,
    ActionResponse,
    GameCreateRequest,
    GameCreateResponse,
    GameStateResponse,
)
from phase2_api.services.session_store import (
    create_game_session,
    get_game_state,
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


@router.get("/games/{game_id}", response_model=GameStateResponse)
def read_game(game_id: str):
    state = get_game_state(game_id)
    return GameStateResponse(game_id=game_id, state=state.to_public_dict())


@router.post("/games/{game_id}/actions", response_model=ActionResponse)
def create_action(game_id: str, request: ActionRequest):
    response = submit_game_action(game_id, request.text)
    return ActionResponse(game_id=game_id, response=response.to_dict())
