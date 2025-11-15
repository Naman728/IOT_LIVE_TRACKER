from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.schemas import AnimalLocationResponse
from app.services.location_service import LocationService

router = APIRouter(prefix="/animals", tags=["animals"])


@router.get("/{animal_id}/latest", response_model=AnimalLocationResponse)
async def get_latest_location(
    animal_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get the latest GPS location for an animal."""
    location = await LocationService.get_latest_location(db, animal_id)
    
    if not location:
        raise HTTPException(
            status_code=404,
            detail=f"No location data found for animal {animal_id}"
        )
    
    return location


@router.get("/{animal_id}/history", response_model=list[AnimalLocationResponse])
async def get_location_history(
    animal_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date for filtering (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering (ISO format)"),
    db: AsyncSession = Depends(get_db)
):
    """Get location history for an animal with optional date range filtering."""
    locations = await LocationService.get_location_history(
        db, animal_id, start_date, end_date
    )
    
    if not locations:
        raise HTTPException(
            status_code=404,
            detail=f"No location history found for animal {animal_id}"
        )
    
    return locations

