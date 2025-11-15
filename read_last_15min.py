#!/usr/bin/env python3
"""
Read last 15 minutes of sensor data
"""
import requests
import argparse
from datetime import datetime, timedelta, timezone

BASE_URL = 'http://localhost:5000'

def get_last_15_minutes(sensor_id, endpoint, resolution=None):
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=15)
    
    params = {
        'sensor_id': sensor_id,
        'start': start_time.isoformat().replace('+00:00', 'Z'),
        'end': end_time.isoformat().replace('+00:00', 'Z')
    }
    
    if resolution:
        params['resolution'] = resolution
    
    url = f"{BASE_URL}/{endpoint}"
    print(f"Querying {endpoint} for {sensor_id} from {start_time.strftime('%H:%M:%S')} to {end_time.strftime('%H:%M:%S')}")
    print("-" * 60)
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data['count']} records")
        if endpoint == 'statistics':
            print(f"Resolution: {data['resolution']}\n")
        else:
            print()
        
        if endpoint == 'measurements':
            for m in data['measurements']:
                timestamp = datetime.fromisoformat(m['timestamp'].replace('Z', '+00:00'))
                print(f"{timestamp.strftime('%H:%M:%S')} - Temp: {m['temperature']}°C, Cond: {m['conductivity']} µS/cm")
        else:
            for s in data['statistics']:
                timestamp = datetime.fromisoformat(s['timestamp'].replace('Z', '+00:00'))
                print(f"{timestamp.strftime('%H:%M:%S')} - Temp: avg={s['temperature']['avg']:.1f} min={s['temperature']['min']:.1f} max={s['temperature']['max']:.1f} "
                      f"med={s['temperature']['median']:.1f} std={s['temperature']['stddev']:.1f}, "
                      f"Cond: avg={s['conductivity']['avg']:.0f} min={s['conductivity']['min']} max={s['conductivity']['max']} "
                      f"med={s['conductivity']['median']:.0f} std={s['conductivity']['stddev']:.0f}, count={s['count']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Read last 15 minutes of sensor data')
    parser.add_argument('--sensor', '-s', default='sensor_001', 
                        help='Sensor ID (default: sensor_001)')
    parser.add_argument('--type', '-t', choices=['measurements', 'statistics'], 
                        default='measurements',
                        help='Data type: measurements (raw) or statistics (aggregated)')
    parser.add_argument('--resolution', '-r', choices=['1min', '5min'],
                        help='Force resolution for statistics (default: auto-select)')
    
    args = parser.parse_args()
    get_last_15_minutes(args.sensor, args.type, args.resolution)
