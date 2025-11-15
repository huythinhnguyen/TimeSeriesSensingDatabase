import pytest
from datetime import datetime, timedelta
from app.aggregation import select_resolution, format_aggregated_result, format_raw_result

class TestResolutionSelection:
    def test_short_range_1min(self):
        """Test 1-minute resolution for short time range"""
        start = datetime(2024, 1, 1, 12, 0, 0)
        end = datetime(2024, 1, 1, 12, 30, 0)
        assert select_resolution(start, end) == '1min'
    
    def test_long_range_5min(self):
        """Test 5-minute resolution for long time range"""
        start = datetime(2024, 1, 1, 12, 0, 0)
        end = datetime(2024, 1, 1, 14, 0, 0)
        assert select_resolution(start, end) == '5min'
    
    def test_threshold_boundary(self):
        """Test resolution at threshold boundary"""
        start = datetime(2024, 1, 1, 12, 0, 0)
        end = datetime(2024, 1, 1, 13, 0, 0)
        assert select_resolution(start, end) == '1min'

class TestFormatting:
    def test_format_aggregated_result(self):
        """Test formatting aggregated database row"""
        row = {
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
        result = format_aggregated_result(row)
        assert result['sensor_id'] == 'sensor_001'
        assert result['temperature']['avg'] == 25.5
        assert result['count'] == 10
    
    def test_format_raw_result(self):
        """Test formatting raw database row"""
        row = {
            'time': datetime(2024, 1, 1, 12, 0, 0),
            'sensor_id': 'sensor_001',
            'temperature': 25.5,
            'conductivity': 1500
        }
        result = format_raw_result(row)
        assert result['sensor_id'] == 'sensor_001'
        assert result['temperature'] == 25.5
        assert result['conductivity'] == 1500
