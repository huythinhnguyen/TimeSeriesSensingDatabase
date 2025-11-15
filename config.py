import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://database_user:database_pass@localhost:5432/my_lab')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    
    # Retention policies
    RAW_DATA_RETENTION_DAYS = int(os.getenv('RAW_DATA_RETENTION_DAYS', 1))
    ONE_MIN_RETENTION_DAYS = int(os.getenv('ONE_MIN_RETENTION_DAYS', 7))
    FIVE_MIN_RETENTION_DAYS = int(os.getenv('FIVE_MIN_RETENTION_DAYS', 30))
    
    # Resolution selection threshold
    HIGH_RES_THRESHOLD_HOURS = int(os.getenv('HIGH_RES_THRESHOLD_HOURS', 1))

    # Normal range for sensor data. Outside this will raise error.
    TEMP_RANGE_MIN = float(os.getenv('TEMP_RANGE_MIN', -100))
    TEMP_RANGE_MAX = float(os.getenv('TEMP_RANGE_MAX', 100))
    CONDUCTIVITY_RANGE_MIN = int(os.getenv('CONDUCTIVITY_RANGE_MIN', 0))
    CONDUCTIVITY_RANGE_MAX = int(os.getenv('CONDUCTIVITY_RANGE_MAX', 10000))
