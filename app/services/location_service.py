from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from datetime import datetime
from typing import Optional, List
from app.models import AnimalLocation
from app.schemas import AnimalLocationCreate, AnimalLocationResponse


class LocationService:
    @staticmethod
    async def create_location(
        session: AsyncSession,
        location_data: AnimalLocationCreate
    ) -> AnimalLocation:
        """Create a new animal location record."""
        location = AnimalLocation(
            animal_id=location_data.animal_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            timestamp=location_data.timestamp
        )
        session.add(location)
        await session.commit()
        await session.refresh(location)
        return location
    
    @staticmethod
    async def get_latest_location(
        session: AsyncSession,
        animal_id: str
    ) -> Optional[AnimalLocation]:
        """Get the latest location for an animal."""
        result = await session.execute(
            select(AnimalLocation)
            .where(AnimalLocation.animal_id == animal_id)
            .order_by(desc(AnimalLocation.timestamp))
            .limit(1)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_location_history(
        session: AsyncSession,
        animal_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AnimalLocation]:
        """Get location history for an animal with optional date range."""
        query = select(AnimalLocation).where(AnimalLocation.animal_id == animal_id)
        
        if start_date:
            query = query.where(AnimalLocation.timestamp >= start_date)
        if end_date:
            query = query.where(AnimalLocation.timestamp <= end_date)
        
        query = query.order_by(desc(AnimalLocation.timestamp))
        
        result = await session.execute(query)
        return list(result.scalars().all())

