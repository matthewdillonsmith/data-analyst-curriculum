# Carolina Home Services

**Stage:** `04_carolina_home_services_operational`  
**Difficulty:** Stage 4 — Intermediate / Messy Operational Events

A service-company operational dataset with event histories, reopened jobs, missing completion events, duplicate events, and many-to-many join risks.

## Included formats

- `csv/` — one CSV per table
- `json/` — one JSON array per table
- `database/04_carolina_home_services_operational.sqlite` — ready-to-query SQLite database
- `sql/postgresql_schema.sql` — PostgreSQL DDL
- `sql/sqlserver_schema.sql` — SQL Server DDL

## Tables

- `customers` — 1,500 rows
- `service_locations` — 1,800 rows
- `technicians` — 80 rows
- `service_types` — 12 rows
- `work_orders` — 4,000 rows
- `technician_assignments` — 4,000 rows
- `work_order_events` — 19,690 rows
- `appointments` — 4,000 rows
- `parts` — 200 rows
- `work_order_parts` — 6,004 rows
- `invoices` — 3,333 rows
- `payments` — 3,019 rows
