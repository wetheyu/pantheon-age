"""Class configuration routes."""

from fastapi import APIRouter

from phase1_cli.data import CLASSES


router = APIRouter(tags=["classes"])


@router.get("/classes")
def list_classes():
    return {
        "classes": list(CLASSES.values()),
    }
