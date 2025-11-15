#!/bin/bash

# Check for help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Get recent raw measurements from sensor API"
    echo ""
    echo "Usage: $0 <sensor_id> <minutes_ago> [-p|--pretty]"
    echo ""
    echo "Arguments:"
    echo "  sensor_id     Sensor identifier (e.g., sensor_001, sensor_002)"
    echo "  minutes_ago   Number of minutes back from current time"
    echo ""
    echo "Options:"
    echo "  -p, --pretty  Format output as a pretty table"
    echo ""
    echo "Examples:"
    echo "  $0 sensor_001 5         # Get raw JSON data"
    echo "  $0 sensor_001 5 -p     # Get formatted table"
    echo "  $0 sensor_002 10 --pretty"
    exit 0
fi

# Parse arguments
PRETTY=false
if [ $# -eq 3 ] && ([ "$3" = "-p" ] || [ "$3" = "--pretty" ]); then
    PRETTY=true
elif [ $# -ne 2 ]; then
    echo "Usage: $0 <sensor_id> <minutes_ago> [-p|--pretty]"
    echo "Use -h for help"
    exit 1
fi

SENSOR_ID=$1
MINUTES_AGO=$2

START=$(date -d "$MINUTES_AGO minutes ago" -u +%Y-%m-%dT%H:%M:%SZ)
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)

if [ "$PRETTY" = true ]; then
    curl -s "http://localhost:5000/measurements?sensor_id=$SENSOR_ID&start=$START&end=$END" | \
    jq -r '
    ["Time", "Sensor", "Temperature (°C)", "Conductivity (µS/cm)"],
    (.measurements[] | [.timestamp[11:19], .sensor_id, .temperature, .conductivity]) |
    @tsv' | \
    column -t -s $'\t'
else
    curl "http://localhost:5000/measurements?sensor_id=$SENSOR_ID&start=$START&end=$END"
fi
