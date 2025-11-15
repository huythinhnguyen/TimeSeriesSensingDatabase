-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create raw measurements table
CREATE TABLE measurements (
    time TIMESTAMPTZ NOT NULL,
    sensor_id TEXT NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    conductivity INTEGER NOT NULL
);

-- Convert to hypertable
SELECT create_hypertable('measurements', 'time');

-- Create index for sensor queries
CREATE INDEX idx_sensor_time ON measurements (sensor_id, time DESC);

-- Create 1-minute continuous aggregate
CREATE MATERIALIZED VIEW measurements_1min
WITH (timescaledb.continuous) AS
SELECT
    sensor_id,
    time_bucket('1 minute', time) AS bucket,
    AVG(temperature) AS avg_temperature,
    MIN(temperature) AS min_temperature,
    MAX(temperature) AS max_temperature,
    STDDEV(temperature) AS stddev_temperature,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY temperature) AS median_temperature,
    AVG(conductivity) AS avg_conductivity,
    MIN(conductivity) AS min_conductivity,
    MAX(conductivity) AS max_conductivity,
    STDDEV(conductivity) AS stddev_conductivity,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY conductivity) AS median_conductivity,
    COUNT(*) AS count
FROM measurements
GROUP BY sensor_id, bucket;

-- Create 5-minute continuous aggregate
CREATE MATERIALIZED VIEW measurements_5min
WITH (timescaledb.continuous) AS
SELECT
    sensor_id,
    time_bucket('5 minutes', time) AS bucket,
    AVG(temperature) AS avg_temperature,
    MIN(temperature) AS min_temperature,
    MAX(temperature) AS max_temperature,
    STDDEV(temperature) AS stddev_temperature,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY temperature) AS median_temperature,
    AVG(conductivity) AS avg_conductivity,
    MIN(conductivity) AS min_conductivity,
    MAX(conductivity) AS max_conductivity,
    STDDEV(conductivity) AS stddev_conductivity,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY conductivity) AS median_conductivity,
    COUNT(*) AS count
FROM measurements
GROUP BY sensor_id, bucket;

-- Add refresh policies | Hardcoded the value here but we should move it to a config.
SELECT add_continuous_aggregate_policy('measurements_1min',
    start_offset => INTERVAL '2 hours',
    end_offset => INTERVAL '10 seconds', -- this add 10 second lag from newest data
    schedule_interval => INTERVAL '1 minute'); -- this is how often we will run

SELECT add_continuous_aggregate_policy('measurements_5min',
    start_offset => INTERVAL '1 day',
    end_offset => INTERVAL '1 minute', -- this add 1 minute lag from newest data
    schedule_interval => INTERVAL '5 minutes'); -- this is how often we will run 

-- Add retention policy (optional, configurable)
-- SELECT add_retention_policy('measurements', INTERVAL '7 days');
