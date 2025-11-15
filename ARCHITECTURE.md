# Architecture Documentation

## Overview

The Aquatic Lab system is designed to efficiently handle high-frequency sensor data (6 measurements per second from 3 sensors) with automatic aggregation and optimized query performance.

## Technology Choices

### TimescaleDB
**Why:** Purpose-built for time-series data with native support for:
- Hypertables: Automatic partitioning by time
- Continuous aggregates: Automatic downsampling with materialized views
- Efficient time-range queries
- Built-in retention policies

**Alternative considered:** Plain PostgreSQL with manual aggregation jobs
**Decision:** TimescaleDB provides better performance and reduces implementation complexity

### Flask
**Why:** Lightweight, RESTful-friendly, minimal boilerplate
**Alternative considered:** FastAPI
**Decision:** Flask is simpler for this use case and meets all requirements

## Database Schema

### Raw Measurements Table
```sql
CREATE TABLE measurements (
    time TIMESTAMPTZ NOT NULL,
    sensor_id TEXT NOT NULL,
    temperature DOUBLE PRECISION NOT NULL,
    conductivity INTEGER NOT NULL
);
```

Converted to hypertable for automatic time-based partitioning.

### Continuous Aggregates

**1-Minute Aggregate:**
- Computes: avg, min, max, median, stddev, count for temperature and conductivity
- Refresh policy: Every 1 minute
- Use case: Recent data queries (last hour)

**5-Minute Aggregate:**
- Same statistics as 1-minute (avg, min, max, median, stddev, count)
- Refresh policy: Every 5 minutes
- Use case: Historical data queries (older than 1 hour)

**Median Calculation:**
Uses PostgreSQL's `PERCENTILE_CONT(0.5)` function for accurate median computation within each time bucket.

## Data Flow

1. **Ingestion**: Sensor → POST /measurements → Raw table
2. **Aggregation**: TimescaleDB continuous aggregates automatically compute statistics
3. **Query**: Client → GET /statistics → API selects resolution → Returns aggregated data

## Resolution Selection Logic

Located in `app/aggregation.py`:

```python
def select_resolution(start_time, end_time):
    time_diff = end_time - start_time
    threshold = timedelta(hours=Config.HIGH_RES_THRESHOLD_HOURS)
    
    if time_diff <= threshold:
        return '1min'
    else:
        return '5min'
```

**Manual Override:**
Users can force a specific resolution via the `resolution` query parameter:
```bash
# Force 1-minute resolution regardless of time range
curl "...?resolution=1min"

# Force 5-minute resolution
curl "...?resolution=5min"
```

**Rationale:**
- Short queries need high resolution for detailed analysis
- Long queries benefit from reduced data volume
- Threshold is configurable for different use cases
- Manual override provides flexibility for specific needs

## Error Handling Strategy

### Input Validation
- All required fields checked before database operations
- Type validation for temperature (float) and conductivity (int)
- Timestamp format validation (ISO 8601)
- Reasonable range checks (temperature: -50 to 100°C)

### Database Errors
- Connection failures caught and logged
- Transactions rolled back on insert failures
- Generic error messages returned to client (security)

### HTTP Status Codes
- `201`: Successful measurement creation
- `200`: Successful query
- `400`: Client error (validation failure)
- `500`: Server error (database issues)

## Extensibility

### Custom Aggregation Logic
The `app/aggregation.py` module is designed for extension:
- `select_resolution()`: Can be enhanced with more sophisticated logic (e.g., based on data volume, user preferences)
- Additional resolution levels can be added (e.g., 15-minute, hourly)
- Custom statistics can be computed (e.g., median, percentiles)
- Manual resolution override allows users to bypass automatic selection

### Data Retention
Retention policies are configurable but must be manually enabled:
```sql
SELECT add_retention_policy('measurements', INTERVAL '7 days');
SELECT add_retention_policy('measurements_1min', INTERVAL '30 days');
SELECT add_retention_policy('measurements_5min', INTERVAL '365 days');
```

Default retention (if not enabled): Indefinite storage

## Performance Considerations

### Indexing
- Primary index: Time-based (hypertable)
- Secondary index: `(sensor_id, time DESC)` for sensor-specific queries

### Query Optimization
- Continuous aggregates pre-compute statistics
- Time-based partitioning reduces scan size
- Appropriate resolution selection minimizes data transfer

### Scalability
Current design handles:
- 6 measurements/second = 518,400 measurements/day
- With 3 sensors = 1.5M measurements/day
- 1-minute aggregates: ~4,320 rows/day/sensor
- 5-minute aggregates: ~864 rows/day/sensor

## Testing Strategy

### Unit Tests
- Input validation logic
- Resolution selection algorithm
- Data formatting functions
- API endpoint behavior

### Integration Tests
- End-to-end API workflows
- Database operations (with mock)
- Error handling paths

### Manual Testing
- Sensor simulator for realistic load
- curl commands for API verification
- `read_last_15min.py` helper script for quick queries
- Postman collection (can be added)

## Database Connection Management

**Issue:** Flask's development server uses multiple threads, but PostgreSQL connections are not thread-safe.

**Solution:** Per-request database connections using Flask's `g` object:
```python
@app.before_request
def before_request():
    if 'db' not in g:
        g.db = Database(app.config['DATABASE_URL'])
        g.db.connect()

@app.teardown_appcontext
def shutdown_session(exception=None):
    db = g.pop('db', None)
    if db:
        db.close()
```

This ensures each request gets its own connection, preventing threading issues.

## Security Considerations

### Input Validation
- All inputs validated before database operations
- SQL injection prevented via parameterized queries
- Type checking for all numeric values

### Error Messages
- Generic error messages to clients
- Detailed errors logged server-side
- No sensitive information in responses

## Future Enhancements

### Potential Improvements
1. **Authentication**: Add API key or OAuth for production
2. **Rate Limiting**: Prevent abuse of ingestion endpoint
3. **Batch Ingestion**: Accept multiple measurements in single request
4. **WebSocket Support**: Real-time data streaming
5. **Alerting**: Threshold-based notifications
6. **Additional Percentiles**: P90, P95, P99 (similar to median implementation)
7. **Multi-sensor Queries**: Compare multiple sensors in single request
8. **Data Export**: CSV/JSON export for analysis tools
9. **Query Caching**: Cache frequently accessed aggregates
10. **Compression**: Enable TimescaleDB compression for older data

### Monitoring
Consider adding:
- Prometheus metrics for ingestion rate
- Grafana dashboards for system health
- Alert on database connection failures
- Track query performance

## Deployment Considerations

### Production Checklist
- [ ] Set `FLASK_DEBUG=False`
- [ ] Use production WSGI server (gunicorn)
- [ ] Configure database connection pooling
- [ ] Set up database backups
- [ ] Enable SSL/TLS for database connection
- [ ] Configure retention policies
- [ ] Set up monitoring and alerting
- [ ] Load testing with expected traffic
- [ ] Document disaster recovery procedures
