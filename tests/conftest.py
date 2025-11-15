import pytest
from app import create_app
from unittest.mock import Mock

@pytest.fixture
def app():
    """Create test app with mock database"""
    mock_db = Mock()
    config = {
        'TESTING': True,
        'DATABASE_URL': 'mock://test',
        'DB': mock_db
    }
    app = create_app(config)
    yield app

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def mock_db(app):
    """Get mock database from app"""
    return app.config['DB']
