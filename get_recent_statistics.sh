#!/bin/bash

# Check for help flag
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    echo "Get recent statistics from sensor API"
    echo ""
    echo "Usage: $0 <sensor_id> <minutes_ago> <resolution> [-p|--pretty]"
    echo ""
    echo "Arguments:"
    echo "  sensor_id     Sensor identifier (e.g., sensor_001, sensor_002)"
    echo "  minutes_ago   Number of minutes back from current time"
    echo "  resolution    Aggregation resolution (1min or 5min)"
    echo ""
    echo "Options:"
    echo "  -p, --pretty  Format output as a pretty table"
    echo ""
    echo "Examples:"
    echo "  $0 sensor_001 5 1min       # Get 1-minute stats as JSON"
    echo "  $0 sensor_001 30 5min -p   # Get 5-minute stats as table"
    echo "  $0 sensor_002 10 1min --pretty"
    exit 0
fi

# Parse arguments
PRETTY=false
if [ $# -eq 4 ] && ([ "$4" = "-p" ] || [ "$4" = "--pretty" ]); then
    PRETTY=true
elif [ $# -ne 3 ]; then
    echo "Usage: $0 <sensor_id> <minutes_ago> <resolution> [-p|--pretty]"
    echo "Use -h for help"
    exit 1
fi

SENSOR_ID=$1
MINUTES_AGO=$2
RESOLUTION=$3

# Validate resolution
if [ "$RESOLUTION" != "1min" ] && [ "$RESOLUTION" != "5min" ]; then
    echo "Error: Resolution must be '1min' or '5min'"
    exit 1
fi

START=$(date -d "$MINUTES_AGO minutes ago" -u +%Y-%m-%dT%H:%M:%SZ)
END=$(date -u +%Y-%m-%dT%H:%M:%SZ)

if [ "$PRETTY" = true ]; then
    curl -s "http://localhost:5000/statistics?sensor_id=$SENSOR_ID&start=$START&end=$END&resolution=$RESOLUTION" | \
    jq -r '
    ["Time", "Sensor", "Temp Avg", "Temp Min", "Temp Max", "Cond Avg", "Cond Min", "Cond Max", "Count"],
    (.statistics[] | [.timestamp[11:19], .sensor_id, (.temperature.avg|tostring), (.temperature.min|tostring), (.temperature.max|tostring), (.conductivity.avg|floor|tostring), (.conductivity.min|tostring), (.conductivity.max|tostring), (.count|tostring)]) |
    @tsv' | \
    column -t -s $'\t'
else
    curl "http://localhost:5000/statistics?sensor_id=$SENSOR_ID&start=$START&end=$END&resolution=$RESOLUTION"
fi
