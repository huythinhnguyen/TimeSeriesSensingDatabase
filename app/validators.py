from datetime import datetime
from app.exceptions import ValidationError
from config import Config

def validate_measurement(data):
    """Validate incoming measurement data"""
    required_fields = ['sensor_id', 'timestamp', 'temperature', 'conductivity']
    
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")
    
    if not isinstance(data['sensor_id'], str) or not data['sensor_id']:
        raise ValidationError("sensor_id must be a non-empty string")
    
    try:
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        raise ValidationError("timestamp must be in ISO 8601 format")
    # I put these in here to show that I care for fault tolerance to sensor outputs.
    # However, I think it's best we either log another column to detect faulty sensor for quick queries
    # Or we let another service handle the faulty detection.
    try:
        temp = float(data['temperature'])
        if temp < Config.TEMP_RANGE_MIN or temp > Config.TEMP_RANGE_MAX:
            raise ValidationError(f"temperature out of reasonable range of [{Config.TEMP_RANGE_MIN}, {Config.TEMP_RANGE_MAX}]")
    except (ValueError, TypeError):
        raise ValidationError("temperature must be a number")
    
    try:
        cond = int(data['conductivity'])
        if cond < Config.CONDUCTIVITY_RANGE_MIN or cond > Config.CONDUCTIVITY_RANGE_MAX:
            raise ValidationError(f"conductivity out of reasonable range of [{Config.CONDUCTIVITY_RANGE_MIN}, {Config.CONDUCTIVITY_RANGE_MAX}]")
    except (ValueError, TypeError):
        raise ValidationError("conductivity must be an integer")
    
    return True

def validate_time_range(start, end):
    """Validate time range parameters"""
    if not start or not end:
        raise ValidationError("Both start and end parameters are required")
    
    try:
        start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
    except (ValueError, AttributeError):
        raise ValidationError("start and end must be in ISO 8601 format")
    
    if start_dt >= end_dt:
        raise ValidationError("start must be before end")
    
    return start_dt, end_dt
