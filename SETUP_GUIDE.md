# Quick Setup Guide

## Step-by-Step Instructions

### 1. Start the Database
```bash
cd aquatic-lab
docker-compose up -d
```

Wait ~10 seconds for TimescaleDB to initialize.

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start the Flask Application
```bash
python run.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

### 4. Test the API (in a new terminal)
```bash
./test_api.sh
```

Or manually:
```bash
# Post a measurement
curl -X POST http://localhost:5000/measurements \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sensor_001",
    "timestamp": "2024-01-01T12:00:00Z",
    "temperature": 25.5,
    "conductivity": 1500
  }'

# Query measurements
curl "http://localhost:5000/measurements?sensor_id=sensor_001&start=2024-01-01T11:00:00Z&end=2024-01-01T13:00:00Z"

# Query statistics
curl "http://localhost:5000/statistics?sensor_id=sensor_001&start=2024-01-01T11:00:00Z&end=2024-01-01T13:00:00Z"
```

### 5. Run the Sensor Simulator (in a new terminal)
```bash
python sensor_simulator.py
```

This will continuously send measurements from 3 sensors.

### 6. Run Unit Tests
```bash
pytest
```

Or with coverage:
```bash
pytest --cov=app tests/
```

## Troubleshooting

### Database Connection Error
- Ensure Docker is running: `docker ps`
- Check database logs: `docker-compose logs timescaledb`
- Verify port 5432 is not in use: `lsof -i :5432`

### Port 5000 Already in Use
- Change port in `run.py` and `sensor_simulator.py`
- Or kill the process: `lsof -ti:5000 | xargs kill -9`

### Import Errors
- Ensure you're in the project directory
- Verify virtual environment is activated (if using one)
- Reinstall dependencies: `pip install -r requirements.txt`

## Project Structure
```
aquatic-lab/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # API endpoints
│   ├── models.py            # Database operations
│   ├── aggregation.py       # Resolution selection logic
│   ├── validators.py        # Input validation
│   └── exceptions.py        # Custom exceptions
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_routes.py       # API endpoint tests
│   └── test_aggregation.py  # Aggregation logic tests
├── config.py                # Configuration
├── run.py                   # Application entry point
├── docker-compose.yml       # Database setup
├── init.sql                 # Database schema
├── requirements.txt         # Python dependencies
├── sensor_simulator.py      # Mock sensor data generator
├── test_api.sh             # API test script
├── .env                     # Environment variables
├── README.md               # Main documentation
└── ARCHITECTURE.md         # Design decisions
```

## Next Steps

1. Review [README.md](README.md) for detailed API documentation
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) for design decisions
3. Explore the code in `app/` directory
4. Run tests and experiment with the API
5. Try different time ranges to see resolution selection in action
