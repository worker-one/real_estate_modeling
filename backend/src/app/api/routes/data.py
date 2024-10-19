import logging

from fastapi import APIRouter
from app.api import schemas
from app.core.data import get_prices_within_radius

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# FastAPI route for the task
@router.post("/prices_in_radius", response_model=list[dict[str, float]])
def prices_in_radius(request: schemas.LocationRequest):
    """
    Get prices within a specified radius from a given location.

    Args:
        request (schemas.LocationRequest): The location request containing latitude, longitude, and radius.

    Returns:
        list[float]: A list of prices within the specified radius.
    """
    logging.info(f"Received request for prices within radius of {request.radius} km from {request.latitude}, {request.longitude}")
    prices = get_prices_within_radius(
        center_lat=request.latitude,
        center_lon=request.longitude,
        radius=request.radius
    )
    return prices
