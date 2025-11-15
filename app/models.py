import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from app.exceptions import DatabaseError

class Database:
    def __init__(self, database_url):
        self.database_url = database_url
        self.conn = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.database_url)
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to connect to database: {str(e)}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def insert_measurement(self, sensor_id, timestamp, temperature, conductivity):
        """Insert a raw measurement"""
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO measurements (time, sensor_id, temperature, conductivity)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (timestamp, sensor_id, temperature, conductivity)
                )
                self.conn.commit()
        except psycopg2.Error as e:
            self.conn.rollback()
            raise DatabaseError(f"Failed to insert measurement: {str(e)}")
    
    def get_raw_measurements(self, sensor_id, start_time, end_time):
        """Query raw measurements"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT time, sensor_id, temperature, conductivity
                    FROM measurements
                    WHERE sensor_id = %s AND time >= %s AND time <= %s
                    ORDER BY time ASC
                    """,
                    (sensor_id, start_time, end_time)
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to query measurements: {str(e)}")
    
    def get_aggregated_1min(self, sensor_id, start_time, end_time):
        """Query 1-minute aggregated data"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT bucket, sensor_id, avg_temperature, min_temperature, max_temperature, 
                           stddev_temperature, median_temperature,
                           avg_conductivity, min_conductivity, max_conductivity, 
                           stddev_conductivity, median_conductivity, count
                    FROM measurements_1min
                    WHERE sensor_id = %s AND bucket >= %s AND bucket <= %s
                    ORDER BY bucket ASC
                    """,
                    (sensor_id, start_time, end_time)
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to query 1-min aggregates: {str(e)}")
    
    def get_aggregated_5min(self, sensor_id, start_time, end_time):
        """Query 5-minute aggregated data"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT bucket, sensor_id, avg_temperature, min_temperature, max_temperature, 
                           stddev_temperature, median_temperature,
                           avg_conductivity, min_conductivity, max_conductivity, 
                           stddev_conductivity, median_conductivity, count
                    FROM measurements_5min
                    WHERE sensor_id = %s AND bucket >= %s AND bucket <= %s
                    ORDER BY bucket ASC
                    """,
                    (sensor_id, start_time, end_time)
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            raise DatabaseError(f"Failed to query 5-min aggregates: {str(e)}")
