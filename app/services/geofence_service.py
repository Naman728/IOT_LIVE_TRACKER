from shapely.geometry import Point, Polygon
from typing import List, Tuple, Optional
from app.models import GeofenceBoundary
from app.schemas import GeofencePoint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json


class GeofenceService:
    @staticmethod
    def is_inside_geofence(
        latitude: float,
        longitude: float,
        boundary_points: List[Tuple[float, float]]
    ) -> bool:
        """
        Check if a point (lat, lon) is inside the geofence polygon.
        
        Args:
            latitude: Latitude of the point
            longitude: Longitude of the point
            boundary_points: List of (lat, lon) tuples forming the polygon
            
        Returns:
            True if point is inside the polygon, False otherwise
        """
        if len(boundary_points) < 3:
            return False
        
        # Create a Point from the coordinates
        point = Point(longitude, latitude)  # Note: shapely uses (x, y) = (lon, lat)
        
        # Create a Polygon from boundary points
        # Shapely expects (x, y) format, so we use (lon, lat)
        polygon_coords = [(lon, lat) for lat, lon in boundary_points]
        polygon = Polygon(polygon_coords)
        
        return polygon.contains(point)
    
    @staticmethod
    async def get_current_boundary(session: AsyncSession) -> Optional[GeofenceBoundary]:
        """Get the current geofence boundary from database."""
        result = await session.execute(
            select(GeofenceBoundary).order_by(GeofenceBoundary.updated_at.desc()).limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    def parse_boundary_points(boundary: GeofenceBoundary) -> List[Tuple[float, float]]:
        """Parse boundary points from database JSON string."""
        try:
            points_data = json.loads(boundary.boundary_points)
            return [(point["latitude"], point["longitude"]) for point in points_data]
        except (json.JSONDecodeError, KeyError, TypeError):
            return []
    
    @staticmethod
    async def check_location(
        session: AsyncSession,
        latitude: float,
        longitude: float
    ) -> Tuple[bool, Optional[List[Tuple[float, float]]]]:
        """
        Check if location is inside geofence.
        
        Returns:
            Tuple of (is_inside, boundary_points)
        """
        boundary = await GeofenceService.get_current_boundary(session)
        
        if not boundary:
            # Default boundary if none exists
            default_boundary = [
                (12.9710, 77.5940),
                (12.9720, 77.5945),
                (12.9730, 77.5930),
                (12.9715, 77.5920)
            ]
            is_inside = GeofenceService.is_inside_geofence(
                latitude, longitude, default_boundary
            )
            return is_inside, default_boundary
        
        boundary_points = GeofenceService.parse_boundary_points(boundary)
        if not boundary_points:
            # Fallback to default if parsing fails
            default_boundary = [
                (12.9710, 77.5940),
                (12.9720, 77.5945),
                (12.9730, 77.5930),
                (12.9715, 77.5920)
            ]
            is_inside = GeofenceService.is_inside_geofence(
                latitude, longitude, default_boundary
            )
            return is_inside, default_boundary
        
        is_inside = GeofenceService.is_inside_geofence(
            latitude, longitude, boundary_points
        )
        return is_inside, boundary_points

