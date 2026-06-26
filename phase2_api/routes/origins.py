"""Playable origin routes."""

from fastapi import APIRouter

from phase2_api.schemas import OriginListResponse
from phase2_api.services.session_store import list_origin_options


router = APIRouter(tags=["origins"])


@router.get("/origins", response_model=OriginListResponse)
def list_origins():
    return OriginListResponse(**list_origin_options())
