from datetime import datetime, timedelta
from config import Config

def select_resolution(start_time, end_time):
    """
    Select appropriate resolution based on time range.
    Returns 'raw', '1min', or '5min'
    
    This function can be extended with custom logic for resolution selection.
    """
    time_diff = end_time - start_time
    threshold = timedelta(hours=Config.HIGH_RES_THRESHOLD_HOURS)
    
    if time_diff <= threshold:
        return '1min'
    else:
        return '5min'

def format_aggregated_result(row):
    """Format aggregated database row for API response"""
    return {
        'timestamp': row['bucket'].isoformat(),
        'sensor_id': row['sensor_id'],
        'temperature': {
            'avg': float(row['avg_temperature']),
            'min': float(row['min_temperature']),
            'max': float(row['max_temperature']),
            'stddev': float(row['stddev_temperature']) if row['stddev_temperature'] else 0.0,
            'median': float(row['median_temperature']) if row['median_temperature'] else 0.0
        },
        'conductivity': {
            'avg': float(row['avg_conductivity']),
            'min': int(row['min_conductivity']),
            'max': int(row['max_conductivity']),
            'stddev': float(row['stddev_conductivity']) if row['stddev_conductivity'] else 0.0,
            'median': float(row['median_conductivity']) if row['median_conductivity'] else 0.0
        },
        'count': int(row['count'])
    }

def format_raw_result(row):
    """Format raw database row for API response"""
    return {
        'timestamp': row['time'].isoformat(),
        'sensor_id': row['sensor_id'],
        'temperature': float(row['temperature']),
        'conductivity': int(row['conductivity'])
    }
