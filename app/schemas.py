from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Tuple


class GPSData(BaseModel):
    animal_id: str = Field(..., description="Unique identifier for the animal")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    timestamp: datetime = Field(..., description="Timestamp of the GPS reading")


class AnimalLocationResponse(BaseModel):
    id: int
    animal_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AnimalLocationCreate(BaseModel):
    animal_id: str
    latitude: float
    longitude: float
    timestamp: datetime


class GeofencePoint(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class GeofenceBoundaryCreate(BaseModel):
    name: Optional[str] = "default"
    boundary_points: List[GeofencePoint] = Field(..., min_items=3, description="At least 3 points required for polygon")


class GeofenceBoundaryResponse(BaseModel):
    id: int
    name: str
    boundary_points: List[GeofencePoint]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    animal_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    alert_type: str
    message: Optional[str]
    
    class Config:
        from_attributes = True


class AlertCreate(BaseModel):
    animal_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    alert_type: str = "geofence_breach"
    message: Optional[str] = None

