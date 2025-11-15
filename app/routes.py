from flask import Blueprint, request, jsonify, g
from datetime import datetime
from app.validators import validate_measurement, validate_time_range
from app.exceptions import ValidationError, DatabaseError
from app.aggregation import select_resolution, format_aggregated_result, format_raw_result

api = Blueprint('api', __name__)

def get_db():
    """Get database instance from request context"""
    return g.db

@api.route('/measurements', methods=['POST'])
def create_measurement():
    """Ingest sensor measurement data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        validate_measurement(data)
        
        db = get_db()
        timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        db.insert_measurement(
            sensor_id=data['sensor_id'],
            timestamp=timestamp,
            temperature=float(data['temperature']),
            conductivity=int(data['conductivity'])
        )
        
        return jsonify({'message': 'Measurement recorded'}), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/measurements', methods=['GET'])
def get_measurements():
    """Query raw measurements by sensor and time range"""
    try:
        sensor_id = request.args.get('sensor_id')
        start = request.args.get('start')
        end = request.args.get('end')
        
        if not sensor_id:
            return jsonify({'error': 'sensor_id parameter is required'}), 400
        
        start_dt, end_dt = validate_time_range(start, end)
        
        db = get_db()
        rows = db.get_raw_measurements(sensor_id, start_dt, end_dt)
        
        results = [format_raw_result(row) for row in rows]
        
        return jsonify({
            'sensor_id': sensor_id,
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'count': len(results),
            'measurements': results
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api.route('/statistics', methods=['GET'])
def get_statistics():
    """Query aggregated statistics with automatic resolution selection"""
    try:
        sensor_id = request.args.get('sensor_id')
        start = request.args.get('start')
        end = request.args.get('end')
        force_resolution = request.args.get('resolution')
        
        if not sensor_id:
            return jsonify({'error': 'sensor_id parameter is required'}), 400
        
        start_dt, end_dt = validate_time_range(start, end)
        
        if force_resolution and force_resolution not in ['1min', '5min']:
            return jsonify({'error': 'resolution must be 1min or 5min'}), 400
        
        resolution = force_resolution or select_resolution(start_dt, end_dt)
        
        db = get_db()
        if resolution == '1min':
            rows = db.get_aggregated_1min(sensor_id, start_dt, end_dt)
        else:
            rows = db.get_aggregated_5min(sensor_id, start_dt, end_dt)
        
        results = [format_aggregated_result(row) for row in rows]
        
        return jsonify({
            'sensor_id': sensor_id,
            'start': start_dt.isoformat(),
            'end': end_dt.isoformat(),
            'resolution': resolution,
            'count': len(results),
            'statistics': results
        }), 200
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except DatabaseError as e:
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@api.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@api.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500
