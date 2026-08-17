# Database Guide

Every dataset stage contains a ready-to-query SQLite database:

```text
datasets/<stage>/database/<stage>.sqlite
```

SQLite is used because students can query the database locally without installing a server.

## SQLite example

```bash
sqlite3 datasets/02_blue_ridge_outfitters_clean/database/02_blue_ridge_outfitters_clean.sqlite
```

Then:

```sql
.tables

SELECT
    order_status,
    COUNT(*) AS order_count
FROM orders
GROUP BY order_status
ORDER BY order_count DESC;
```

## PostgreSQL / SQL Server

Each stage includes generated schema files under `sql/` and all source tables under `csv/`.

The generic loader can place the CSV tables in an available database:

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "postgresql+psycopg://analyst:password@localhost/analytics"
```

or:

```powershell
python tools/load_database.py `
    datasets/02_blue_ridge_outfitters_clean `
    "mssql+pyodbc://analyst:password@localhost/analytics?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
```

## Recommended instructional progression

- Stage 01: SQLite or PostgreSQL
- Stage 02: PostgreSQL / SQL Server
- Stage 03: raw CSV loaded into staging tables before cleaning
- Stage 04: SQL Server/PostgreSQL with analytical views created by students
- Stage 05: operational SQLite/database + separate CSV/API sources
- Stage 06: PostgreSQL or another database capable of handling time-series exercises comfortably
- Stage 07: multiple simulated source systems with a student-built analytical layer
