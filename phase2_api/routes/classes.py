"""Class configuration routes."""

from fastapi import APIRouter

from phase1_cli.data import CLASSES
from phase2_api.schemas import ClassListResponse


router = APIRouter(tags=["classes"])


@router.get("/classes", response_model=ClassListResponse)
def list_classes():
    return ClassListResponse(classes=list(CLASSES.values()))
