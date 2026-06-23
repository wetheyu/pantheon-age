"""Character creation routes."""

from fastapi import APIRouter

from phase2_api.schemas import CharacterCreateRequest, CharacterResponse
from phase2_api.services.session_store import build_api_character


router = APIRouter(tags=["characters"])


@router.post("/characters", response_model=CharacterResponse)
def create_character(request: CharacterCreateRequest):
    character = build_api_character(request.name, request.class_id, request.god)
    return CharacterResponse(character=character.to_public_dict())
