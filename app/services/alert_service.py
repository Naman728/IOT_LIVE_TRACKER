from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from app.models import Alert
from app.schemas import AlertCreate, AlertResponse


class AlertService:
    @staticmethod
    async def create_alert(
        session: AsyncSession,
        alert_data: AlertCreate
    ) -> Alert:
        """Create a new alert record."""
        alert = Alert(
            animal_id=alert_data.animal_id,
            latitude=alert_data.latitude,
            longitude=alert_data.longitude,
            timestamp=alert_data.timestamp,
            alert_type=alert_data.alert_type,
            message=alert_data.message
        )
        session.add(alert)
        await session.commit()
        await session.refresh(alert)
        return alert
    
    @staticmethod
    async def get_all_alerts(
        session: AsyncSession,
        limit: int = 100
    ) -> List[Alert]:
        """Get all alerts, ordered by most recent."""
        result = await session.execute(
            select(Alert)
            .order_by(desc(Alert.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_alerts_by_animal(
        session: AsyncSession,
        animal_id: str,
        limit: int = 100
    ) -> List[Alert]:
        """Get alerts for a specific animal."""
        result = await session.execute(
            select(Alert)
            .where(Alert.animal_id == animal_id)
            .order_by(desc(Alert.timestamp))
            .limit(limit)
        )
        return list(result.scalars().all())

