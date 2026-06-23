"""Pantheon configuration routes."""

from fastapi import APIRouter

from phase1_cli.data import GODS
from phase2_api.schemas import GodListResponse


router = APIRouter(tags=["gods"])


@router.get("/gods", response_model=GodListResponse)
def list_gods():
    return GodListResponse(gods=list(GODS))
