from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas import GeofenceBoundaryCreate, GeofenceBoundaryResponse, GeofencePoint
from app.models import GeofenceBoundary
from app.services.geofence_service import GeofenceService
import json

router = APIRouter(prefix="/geofence", tags=["geofence"])


@router.post("", response_model=GeofenceBoundaryResponse)
async def update_geofence(
    boundary_data: GeofenceBoundaryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Update the geofence boundary polygon."""
    # Convert Pydantic models to JSON string
    points_json = [
        {"latitude": point.latitude, "longitude": point.longitude}
        for point in boundary_data.boundary_points
    ]
    
    # Check if a boundary with this name exists
    result = await db.execute(
        select(GeofenceBoundary).where(GeofenceBoundary.name == boundary_data.name)
    )
    existing_boundary = result.scalar_one_or_none()
    
    if existing_boundary:
        # Update existing
        existing_boundary.boundary_points = json.dumps(points_json)
        await db.commit()
        await db.refresh(existing_boundary)
        
        # Parse for response
        points_data = json.loads(existing_boundary.boundary_points)
        boundary_points = [
            GeofencePoint(latitude=p["latitude"], longitude=p["longitude"])
            for p in points_data
        ]
        
        return {
            "id": existing_boundary.id,
            "name": existing_boundary.name,
            "boundary_points": boundary_points,
            "created_at": existing_boundary.created_at,
            "updated_at": existing_boundary.updated_at
        }
    else:
        # Create new
        new_boundary = GeofenceBoundary(
            name=boundary_data.name,
            boundary_points=json.dumps(points_json)
        )
        db.add(new_boundary)
        await db.commit()
        await db.refresh(new_boundary)
        
        # Parse for response
        points_data = json.loads(new_boundary.boundary_points)
        boundary_points = [
            GeofencePoint(latitude=p["latitude"], longitude=p["longitude"])
            for p in points_data
        ]
        
        return {
            "id": new_boundary.id,
            "name": new_boundary.name,
            "boundary_points": boundary_points,
            "created_at": new_boundary.created_at,
            "updated_at": new_boundary.updated_at
        }


@router.get("", response_model=GeofenceBoundaryResponse)
async def get_geofence(
    db: AsyncSession = Depends(get_db)
):
    """Get the current geofence boundary."""
    boundary = await GeofenceService.get_current_boundary(db)
    
    if not boundary:
        raise HTTPException(
            status_code=404,
            detail="No geofence boundary configured"
        )
    
    # Parse boundary points for response
    try:
        points_data = json.loads(boundary.boundary_points)
        from app.schemas import GeofencePoint
        boundary_points = [
            GeofencePoint(latitude=p["latitude"], longitude=p["longitude"])
            for p in points_data
        ]
    except (json.JSONDecodeError, KeyError):
        boundary_points = []
    
    # Create response with parsed points
    return {
        "id": boundary.id,
        "name": boundary.name,
        "boundary_points": boundary_points,
        "created_at": boundary.created_at,
        "updated_at": boundary.updated_at
    }

