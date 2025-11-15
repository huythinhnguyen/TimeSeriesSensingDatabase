import pytest
from datetime import datetime

class TestMeasurementsPost:
    def test_valid_measurement(self, client, mock_db):
        """Test posting valid measurement"""
        data = {
            'sensor_id': 'sensor_001',
            'timestamp': '2024-01-01T12:00:00Z',
            'temperature': 25.5,
            'conductivity': 1500
        }
        response = client.post('/measurements', json=data)
        assert response.status_code == 201
        assert mock_db.insert_measurement.called
    
    def test_missing_field(self, client):
        """Test missing required field"""
        data = {
            'sensor_id': 'sensor_001',
            'timestamp': '2024-01-01T12:00:00Z',
            'temperature': 25.5
        }
        response = client.post('/measurements', json=data)
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_invalid_timestamp(self, client):
        """Test invalid timestamp format"""
        data = {
            'sensor_id': 'sensor_001',
            'timestamp': 'invalid',
            'temperature': 25.5,
            'conductivity': 1500
        }
        response = client.post('/measurements', json=data)
        assert response.status_code == 400
    
    def test_invalid_temperature(self, client):
        """Test invalid temperature value"""
        data = {
            'sensor_id': 'sensor_001',
            'timestamp': '2024-01-01T12:00:00Z',
            'temperature': 'not_a_number',
            'conductivity': 1500
        }
        response = client.post('/measurements', json=data)
        assert response.status_code == 400
    
    def test_no_json_body(self, client):
        """Test request without JSON body"""
        response = client.post('/measurements')
        assert response.status_code == 400

class TestMeasurementsGet:
    def test_valid_query(self, client, mock_db):
        """Test valid raw measurements query"""
        mock_db.get_raw_measurements.return_value = [
            {
                'time': datetime(2024, 1, 1, 12, 0, 0),
                'sensor_id': 'sensor_001',
                'temperature': 25.5,
                'conductivity': 1500
            }
        ]
        
        response = client.get('/measurements?sensor_id=sensor_001&start=2024-01-01T12:00:00Z&end=2024-01-01T13:00:00Z')
        assert response.status_code == 200
        assert 'measurements' in response.json
        assert response.json['count'] == 1
    
    def test_missing_sensor_id(self, client):
        """Test query without sensor_id"""
        response = client.get('/measurements?start=2024-01-01T12:00:00Z&end=2024-01-01T13:00:00Z')
        assert response.status_code == 400
    
    def test_invalid_time_range(self, client):
        """Test query with invalid time range"""
        response = client.get('/measurements?sensor_id=sensor_001&start=2024-01-01T13:00:00Z&end=2024-01-01T12:00:00Z')
        assert response.status_code == 400
    
    def test_empty_results(self, client, mock_db):
        """Test query with no results"""
        mock_db.get_raw_measurements.return_value = []
        
        response = client.get('/measurements?sensor_id=sensor_001&start=2024-01-01T12:00:00Z&end=2024-01-01T13:00:00Z')
        assert response.status_code == 200
        assert response.json['count'] == 0

class TestStatisticsGet:
    def test_1min_resolution(self, client, mock_db):
        """Test statistics with 1-minute resolution"""
        mock_db.get_aggregated_1min.return_value = [
            {
                'bucket': datetime(2024, 1, 1, 12, 0, 0),
                'sensor_id': 'sensor_001',
                'avg_temperature': 25.5,
                'min_temperature': 25.0,
                'max_temperature': 26.0,
                'avg_conductivity': 1500.0,
                'min_conductivity': 1450,
                'max_conductivity': 1550,
                'count': 10
            }
        ]
        
        response = client.get('/statistics?sensor_id=sensor_001&start=2024-01-01T12:00:00Z&end=2024-01-01T12:30:00Z')
        assert response.status_code == 200
        assert response.json['resolution'] == '1min'
        assert 'statistics' in response.json
    
    def test_5min_resolution(self, client, mock_db):
        """Test statistics with 5-minute resolution"""
        mock_db.get_aggregated_5min.return_value = []
        
        response = client.get('/statistics?sensor_id=sensor_001&start=2024-01-01T12:00:00Z&end=2024-01-01T14:00:00Z')
        assert response.status_code == 200
        assert response.json['resolution'] == '5min'
    
    def test_missing_parameters(self, client):
        """Test statistics without required parameters"""
        response = client.get('/statistics')
        assert response.status_code == 400
