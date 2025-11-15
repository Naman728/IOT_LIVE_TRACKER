from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class AnimalLocation(Base):
    __tablename__ = "animal_locations"
    
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_animal_id', 'animal_id'),
        Index('idx_timestamp', 'timestamp'),
    )


class GeofenceBoundary(Base):
    __tablename__ = "geofence_boundaries"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, default="default")
    boundary_points = Column(String, nullable=False)  # JSON string of coordinates
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    animal_id = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    alert_type = Column(String, nullable=False, default="geofence_breach")
    message = Column(String, nullable=True)

