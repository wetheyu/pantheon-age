"""Location and map routes."""

from fastapi import APIRouter

from phase1_cli.data import LOCATION_DESCRIPTIONS, LOCATIONS
from phase2_api.schemas import LocationListResponse


router = APIRouter(tags=["locations"])


@router.get("/locations", response_model=LocationListResponse)
def list_locations():
    locations = []
    for name, exits in LOCATIONS.items():
        locations.append(
            {
                "name": name,
                "description": LOCATION_DESCRIPTIONS[name],
                "exits": list(exits),
            }
        )

    return LocationListResponse(locations=locations)
