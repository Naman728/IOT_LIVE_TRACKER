from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import animals, alerts, geofence

app = FastAPI(
    title="Livestock Tracking System API",
    description="IoT GPS-based livestock tracking system with geofencing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(animals.router)
app.include_router(alerts.router)
app.include_router(geofence.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Livestock Tracking System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

