# Livestock Tracking System

A comprehensive IoT-based livestock tracking system using GPS devices, MQTT messaging, and real-time geofencing capabilities.

## 🏗️ System Architecture

```
┌─────────────────┐
│  IoT GPS Device │
│   (Hardware)    │
└────────┬────────┘
         │
         │ MQTT Publish
         │ Topic: livestock/gps/data
         ▼
┌─────────────────┐
│   MQTT Broker   │
│   (Mosquitto)   │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
         ▼                 ▼
┌─────────────────┐  ┌─────────────────┐
│  MQTT Listener  │  │  FastAPI Server │
│   (Python)      │  │   (REST API)    │
└────────┬────────┘  └─────────────────┘
         │
         │ Geofence Check
         │
         ├─────────────┐
         │             │
         ▼             ▼
┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │ MQTT Alert  │
│  Database   │  │   Topic     │
└─────────────┘  └─────────────┘
```

## 📊 Data Flow

1. **GPS Data Collection**: IoT GPS devices publish location data to MQTT topic `livestock/gps/data`
2. **Data Ingestion**: MQTT Listener service subscribes to GPS data and processes each message
3. **Geofencing**: Each GPS coordinate is checked against the configured geofence boundary
4. **Data Storage**: 
   - If inside boundary → Save to PostgreSQL `animal_locations` table
   - If outside boundary → Save to `alerts` table AND publish to MQTT topic `livestock/alerts`
5. **API Access**: FastAPI provides REST endpoints to query locations, history, and alerts

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- MQTT Broker (Mosquitto recommended)
- pip

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd /Users/namananand/IOT
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env  # Edit .env with your settings
   ```

   Update `.env` with your database and MQTT credentials:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/livestock_db
   MQTT_BROKER_HOST=localhost
   MQTT_BROKER_PORT=1883
   ```

5. **Set up PostgreSQL database**:
   ```bash
   createdb livestock_db
   ```

6. **Run database migrations**:
   ```bash
   cd backend
   alembic upgrade head
   cd ..
   ```

### Running the System

#### Option 1: Using the run script (recommended)
```bash
chmod +x run.sh
./run.sh
```

This will start both the FastAPI server and MQTT listener.

#### Option 2: Manual startup

**Terminal 1 - FastAPI Server**:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - MQTT Listener**:
```bash
python3 mqtt_listener/listener.py
```

### Accessing the API

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Alternative Docs**: http://localhost:8000/redoc

## 📡 MQTT Data Ingestion

### How It Works

The MQTT Listener (`mqtt_listener/listener.py`) is a standalone Python service that:

1. **Connects to MQTT Broker**: Uses paho-mqtt client with automatic reconnection
2. **Subscribes to GPS Data**: Listens to `livestock/gps/data` topic
3. **Validates Messages**: Parses and validates JSON using Pydantic models
4. **Geofence Check**: Calls geofencing service to determine if location is inside boundary
5. **Data Processing**:
   - **Inside**: Saves to PostgreSQL `animal_locations` table
   - **Outside**: Saves to `alerts` table and publishes alert to `livestock/alerts` topic
6. **Error Handling**: Handles JSON errors, connection failures, and database errors gracefully
7. **24/7 Operation**: Runs continuously with automatic reconnection on failures

### Message Format

**GPS Data (Input)**:
```json
{
  "animal_id": "A101",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "timestamp": "2025-01-01T10:20:30Z"
}
```

**Alert (Output)**:
```json
{
  "animal_id": "A101",
  "latitude": 12.9800,
  "longitude": 77.6000,
  "timestamp": "2025-01-01T10:20:30Z",
  "alert_type": "geofence_breach",
  "message": "Animal A101 is outside the geofence boundary"
}
```

## 🧭 Geofencing Logic

### How Geofencing Works

The geofencing system uses the **Shapely** library for geometric calculations:

1. **Boundary Definition**: Geofence is defined as a polygon using a list of (latitude, longitude) points
2. **Point-in-Polygon Check**: Uses Shapely's `Polygon.contains(Point)` method
3. **Default Boundary**: If no boundary is configured, uses a default farm boundary
4. **Boundary Storage**: Boundaries are stored in PostgreSQL `geofence_boundaries` table as JSON

### Default Boundary

```python
farm_boundary = [
    (12.9710, 77.5940),
    (12.9720, 77.5945),
    (12.9730, 77.5930),
    (12.9715, 77.5920)
]
```

### Updating Geofence

Use the FastAPI endpoint to update the geofence:

```bash
curl -X POST "http://localhost:8000/geofence" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "farm_boundary",
    "boundary_points": [
      {"latitude": 12.9710, "longitude": 77.5940},
      {"latitude": 12.9720, "longitude": 77.5945},
      {"latitude": 12.9730, "longitude": 77.5930},
      {"latitude": 12.9715, "longitude": 77.5920}
    ]
  }'
```

## 🌐 FastAPI Endpoints

### Public Routes

#### Get Latest Location
```http
GET /animals/{animal_id}/latest
```

**Response**:
```json
{
  "id": 1,
  "animal_id": "A101",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "timestamp": "2025-01-01T10:20:30Z"
}
```

#### Get Location History
```http
GET /animals/{animal_id}/history?start_date=2025-01-01T00:00:00Z&end_date=2025-01-01T23:59:59Z
```

**Query Parameters**:
- `start_date` (optional): ISO format datetime
- `end_date` (optional): ISO format datetime

#### Get All Alerts
```http
GET /alerts?limit=100
```

**Query Parameters**:
- `limit` (optional): Maximum number of alerts (default: 100, max: 1000)

### Admin Routes

#### Update Geofence
```http
POST /geofence
```

**Request Body**:
```json
{
  "name": "farm_boundary",
  "boundary_points": [
    {"latitude": 12.9710, "longitude": 77.5940},
    {"latitude": 12.9720, "longitude": 77.5945},
    {"latitude": 12.9730, "longitude": 77.5930}
  ]
}
```

#### Get Current Geofence
```http
GET /geofence
```

## 🧪 Testing with Mock Data

A test utility is provided to simulate GPS data from IoT devices:

```bash
python3 tests/send_mock_data.py
```

This script:
- Connects to MQTT broker
- Publishes dummy GPS data for multiple animals
- Alternates between inside/outside geofence coordinates
- Helps verify ingestion and alert generation

### Example Test Flow

1. **Start MQTT Broker** (if not running):
   ```bash
   mosquitto -v
   ```

2. **Start MQTT Listener**:
   ```bash
   python3 mqtt_listener/listener.py
   ```

3. **Start FastAPI Server**:
   ```bash
   cd backend && uvicorn app.main:app --reload
   ```

4. **Run Mock Publisher**:
   ```bash
   python3 tests/send_mock_data.py
   ```

5. **Verify Data**:
   - Check FastAPI docs: http://localhost:8000/docs
   - Query latest location: `GET /animals/A101/latest`
   - Query alerts: `GET /alerts`

## 📁 Project Structure

```
backend/
 ├── app/
 │    ├── main.py              # FastAPI application
 │    ├── config.py            # Configuration settings
 │    ├── database.py          # Database connection
 │    ├── models.py            # SQLAlchemy models
 │    ├── schemas.py           # Pydantic schemas
 │    ├── routers/
 │    │     ├── animals.py     # Animal location endpoints
 │    │     ├── alerts.py      # Alert endpoints
 │    │     └── geofence.py    # Geofence management
 │    ├── services/
 │    │     ├── geofence_service.py   # Geofencing logic
 │    │     ├── location_service.py   # Location CRUD
 │    │     └── alert_service.py     # Alert CRUD
 │    └── utils/
 │          └── mqtt_publisher.py    # MQTT publishing utility
 ├── alembic/                  # Database migrations
 │    ├── versions/            # Migration files
 │    └── env.py               # Alembic environment
 ├── alembic.ini               # Alembic configuration
mqtt_listener/
 └── listener.py              # MQTT ingestion service
tests/
 └── send_mock_data.py        # Mock GPS data publisher
requirements.txt              # Python dependencies
.env                         # Environment variables
README.md                    # This file
run.sh                       # Startup script
```

## 🗄️ Database Schema

### animal_locations
- `id` (PK, Integer)
- `animal_id` (String, Indexed)
- `latitude` (Float)
- `longitude` (Float)
- `timestamp` (DateTime, Indexed)

### geofence_boundaries
- `id` (PK, Integer)
- `name` (String)
- `boundary_points` (String, JSON)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### alerts
- `id` (PK, Integer)
- `animal_id` (String, Indexed)
- `latitude` (Float)
- `longitude` (Float)
- `timestamp` (DateTime, Indexed)
- `alert_type` (String)
- `message` (String, Nullable)

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

- **Database**: `DATABASE_URL`
- **MQTT**: `MQTT_BROKER_HOST`, `MQTT_BROKER_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD`
- **Topics**: `MQTT_TOPIC_GPS`, `MQTT_TOPIC_ALERTS`
- **JWT** (optional): `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`

## 🛠️ Development

### Running Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Adding New Endpoints

1. Create route in `backend/app/routers/`
2. Add service logic in `backend/app/services/`
3. Update schemas in `backend/app/schemas.py`
4. Include router in `backend/app/main.py`

## 📝 Notes

- The MQTT listener runs as a separate process from FastAPI
- Geofencing uses Shapely for accurate geometric calculations
- All database operations use async/await for better performance
- The system handles connection failures gracefully with automatic reconnection
- Default geofence is used if none is configured in the database

## 🐛 Troubleshooting

### MQTT Connection Issues
- Verify MQTT broker is running: `mosquitto -v`
- Check firewall settings
- Verify credentials in `.env`

### Database Connection Issues
- Ensure PostgreSQL is running
- Verify `DATABASE_URL` in `.env`
- Check database exists: `psql -l`

### Import Errors
- Ensure virtual environment is activated
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python path includes project root

## 📄 License

This project is provided as-is for educational and development purposes.

