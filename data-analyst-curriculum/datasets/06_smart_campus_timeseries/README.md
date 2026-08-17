# Smart Campus Energy & Sensor Data

**Stage:** `06_smart_campus_timeseries`  
**Difficulty:** Stage 6 — Advanced / Time Series & IoT

15-minute smart-building data spanning both 2026 U.S. DST transitions, with missing intervals, duplicate records, sentinel values, impossible readings, and outliers.

## Included formats

- `csv/` — one CSV per table
- `json/` — one JSON array per table
- `database/06_smart_campus_timeseries.sqlite` — ready-to-query SQLite database
- `sql/postgresql_schema.sql` — PostgreSQL DDL
- `sql/sqlserver_schema.sql` — SQL Server DDL

## Tables

- `buildings` — 3 rows
- `sensors` — 12 rows
- `sensor_readings` — 50,611 rows
