# Piedmont Logistics

**Stage:** `05_piedmont_logistics_multisource`  
**Difficulty:** Stage 5 — Upper Intermediate / Multi-Source Integration

A logistics company spread across an operational database, customer-master CSV, fuel CSV, and GPS API-style JSON. Students must normalize IDs and resolve source-of-truth questions.

## Included formats

- `csv/` — one CSV per table
- `json/` — one JSON array per table
- `database/05_piedmont_logistics_multisource.sqlite` — ready-to-query SQLite database
- `sql/postgresql_schema.sql` — PostgreSQL DDL
- `sql/sqlserver_schema.sql` — SQL Server DDL

## Tables

- `customers` — 2,000 rows
- `customer_master` — 2,000 rows
- `warehouses` — 10 rows
- `drivers` — 120 rows
- `vehicles` — 100 rows
- `shipments` — 5,000 rows
- `delivery_events` — 20,000 rows
- `fuel_transactions` — 8,032 rows
- `gps_events` — 10,000 rows
