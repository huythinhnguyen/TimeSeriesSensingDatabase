#!/bin/bash

# Test script for TimeSeriesSensingDatabase API
# Usage: ./test_api.sh

BASE_URL="http://localhost:5000"

echo "=== Testing TimeSeriesSensingDatabase API ==="
echo ""

# Test 1: POST measurement
echo "Test 1: POST /measurements"
curl -X POST $BASE_URL/measurements \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sensor_001",
    "timestamp": "2024-01-01T12:00:00Z",
    "temperature": 25.5,
    "conductivity": 1500
  }'
echo -e "\n"

# Test 2: POST another measurement
echo "Test 2: POST another measurement"
curl -X POST $BASE_URL/measurements \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sensor_001",
    "timestamp": "2024-01-01T12:00:30Z",
    "temperature": 26.0,
    "conductivity": 1520
  }'
echo -e "\n"

# Wait a moment for data to be available
sleep 2

# Test 3: GET raw measurements
echo "Test 3: GET /measurements"
curl "$BASE_URL/measurements?sensor_id=sensor_001&start=2024-01-01T11:00:00Z&end=2024-01-01T13:00:00Z"
echo -e "\n"

# Test 4: GET statistics
echo "Test 4: GET /statistics"
curl "$BASE_URL/statistics?sensor_id=sensor_001&start=2024-01-01T11:00:00Z&end=2024-01-01T13:00:00Z"
echo -e "\n"

# Test 5: Invalid request (missing field)
echo "Test 5: Invalid POST (missing field)"
curl -X POST $BASE_URL/measurements \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "sensor_001",
    "timestamp": "2024-01-01T12:00:00Z",
    "temperature": 25.5
  }'
echo -e "\n"

# Test 6: Invalid query (missing sensor_id)
echo "Test 6: Invalid GET (missing sensor_id)"
curl "$BASE_URL/measurements?start=2024-01-01T11:00:00Z&end=2024-01-01T13:00:00Z"
echo -e "\n"

echo "=== Tests Complete ==="
