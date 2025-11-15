from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas import AlertResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
async def get_all_alerts(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of alerts to return"),
    db: AsyncSession = Depends(get_db)
):
    """Get all alerts, ordered by most recent."""
    alerts = await AlertService.get_all_alerts(db, limit)
    return alerts

