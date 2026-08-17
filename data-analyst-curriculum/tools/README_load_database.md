# `load_database.py`

## Overview

`load_database.py` is a command-line utility that loads the CSV files from any generated curriculum dataset stage into a SQLAlchemy-supported relational database.

It provides a simple bridge between the repository's generated datasets and database platforms used in the classroom, including:

- PostgreSQL
- Microsoft SQL Server
- SQLite
- Other SQLAlchemy-supported databases when the appropriate driver is installed

The loader is located at:

```text
tools/load_database.py
```

The recommended way to run it is from the repository root.

```mermaid
flowchart LR
    A[Generated Dataset Stage] --> B[CSV Files]
    B --> C[load_database.py]
    C --> D[(PostgreSQL)]
    C --> E[(SQL Server)]
    C --> F[(SQLite)]
    C --> G[(Other SQLAlchemy Database)]
```

---

# Requirements

Install the repository dependencies before using the loader:

```bash
pip install -r requirements.txt
```

The loader directly uses:

- `pandas`
- `SQLAlchemy`

The repository also includes the primary drivers used by the curriculum:

```text
pandas>=2.2
SQLAlchemy>=2.0
psycopg[binary]>=3.2
pyodbc>=5.1
```

`psycopg` is used for PostgreSQL.

`pyodbc` is used for Microsoft SQL Server.

SQL Server users normally also need a Microsoft ODBC Driver for SQL Server installed on the operating system.

---

# Basic Usage

The basic command is:

```bash
python tools/load_database.py <stage_dir> "<connection_string>"
```

The complete syntax is:

```bash
python tools/load_database.py \
    <stage_dir> \
    "<connection_string>" \
    [--schema <schema_name>] \
    [--if-exists fail|replace|append]
```

To display the built-in command help:

```bash
python tools/load_database.py --help
```

---

# Command-Line Arguments

| Argument | Required | Default | Description |
|---|---:|---|---|
| `stage_dir` | Yes | — | Path to a generated curriculum dataset stage |
| `connection_string` | Yes | — | SQLAlchemy database connection string |
| `--schema` | No | `None` | Destination database schema, if supported |
| `--if-exists` | No | `replace` | Controls behavior when a destination table already exists |

The valid `--if-exists` values are:

| Value | Behavior |
|---|---|
| `fail` | Raise an error when the table already exists |
| `replace` | Drop the existing table and recreate it from the CSV |
| `append` | Insert rows into the existing table |

> **Important:** The default is `replace`. Do not point the loader at tables that contain data you need to preserve.

---

# Expected Stage Structure

The loader expects the supplied stage directory to contain a `csv` subdirectory.

Example:

```text
datasets/
└── 04_carolina_home_services_operational/
    ├── csv/
    │   ├── appointments.csv
    │   ├── customers.csv
    │   ├── invoices.csv
    │   ├── payments.csv
    │   ├── technicians.csv
    │   ├── work_order_events.csv
    │   ├── work_order_parts.csv
    │   └── work_orders.csv
    │
    ├── json/
    ├── database/
    ├── sql/
    ├── dataset_info.json
    └── README.md
```

The stage argument should point to:

```text
datasets/04_carolina_home_services_operational
```

not:

```text
datasets/04_carolina_home_services_operational/csv
```

The script automatically appends `/csv`.

If the expected CSV directory is missing, the script exits with an error.

---

# How Tables Are Named

Each CSV filename becomes the destination table name.

For example:

```text
customers.csv
```

becomes:

```text
customers
```

and:

```text
work_order_events.csv
```

becomes:

```text
work_order_events
```

All `.csv` files in the stage's `csv` directory are processed in sorted filename order.

---

# What the Loader Does

For each CSV file, the loader:

1. Resolves the stage directory.
2. Locates its `csv` subdirectory.
3. Creates a SQLAlchemy database engine.
4. Reads the CSV into a pandas `DataFrame`.
5. Uses the filename as the destination table name.
6. Writes the `DataFrame` to the database.
7. Repeats until all CSV files are loaded.

```mermaid
flowchart TD
    A[Stage Directory] --> B[Locate stage/csv]
    B --> C{Directory Exists?}
    C -->|No| D[Exit With Error]
    C -->|Yes| E[Create SQLAlchemy Engine]
    E --> F[Find CSV Files]
    F --> G[Read CSV With pandas]
    G --> H[Filename Becomes Table Name]
    H --> I[Write DataFrame to Database]
    I --> J{More CSV Files?}
    J -->|Yes| G
    J -->|No| K[Load Complete]
```

The current implementation reads files with:

```python
df = pd.read_csv(
    csv_path,
    low_memory=False,
)
```

and writes them with:

```python
df.to_sql(
    table,
    engine,
    schema=args.schema,
    if_exists=args.if_exists,
    index=False,
    chunksize=1000,
    method=None,
)
```

---

# PostgreSQL

## Basic PostgreSQL Load

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics"
```

Without `--schema`, PostgreSQL normally uses the connection's default schema, usually `public`.

## PostgreSQL With a Dedicated Schema

Create the schema first:

```sql
CREATE SCHEMA IF NOT EXISTS blue_ridge_outfitters;
```

Then load the stage:

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --schema blue_ridge_outfitters
```

> The loader does not create the schema. The destination schema must already exist.

---

# Microsoft SQL Server

## SQL Server Authentication Example

### Bash

```bash
python tools/load_database.py \
    datasets/04_carolina_home_services_operational \
    "mssql+pyodbc://analyst:password@localhost/AnalyticsTraining?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
```

### PowerShell

```powershell
python tools/load_database.py `
    datasets/04_carolina_home_services_operational `
    "mssql+pyodbc://analyst:password@localhost/AnalyticsTraining?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
```

## SQL Server With a Dedicated Schema

Create the schema first:

```sql
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'home_services'
)
BEGIN
    EXEC('CREATE SCHEMA home_services');
END;
```

Then load the dataset:

```powershell
python tools/load_database.py `
    datasets/04_carolina_home_services_operational `
    "mssql+pyodbc://analyst:password@localhost/AnalyticsTraining?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes" `
    --schema home_services
```

---

# SQLite

The repository already contains generated SQLite databases for each curriculum stage, so the loader is normally unnecessary for SQLite.

However, it can be used to build a new SQLite database from the stage CSV files:

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "sqlite:///blue_ridge_outfitters.sqlite"
```

This creates:

```text
blue_ridge_outfitters.sqlite
```

in the current working directory.

Do not normally use `--schema` with SQLite.

---

# `--if-exists` Behavior

## `replace`

`replace` is the default.

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --if-exists replace
```

Use this when:

- Resetting a classroom database
- Recreating a dataset between exercises
- Returning students to a known starting state

When a table already exists, pandas drops it and recreates it.

## `fail`

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --if-exists fail
```

Use this when you want protection against accidentally replacing an existing table.

## `append`

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --if-exists append
```

Use this when intentionally simulating an incremental load.

The loader itself performs no deduplication. Loading the same CSV twice with `append` can therefore create duplicate records.

---

# Loading the Curriculum Stages

The following examples use PostgreSQL and dedicated schemas.

The schemas are examples and must be created before running the loader.

## Stage 01 — Northwind-Style Starter

```bash
python tools/load_database.py \
    datasets/01_northwind_starter \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --schema stage01
```

## Stage 02 — Blue Ridge Outfitters Clean

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --schema stage02
```

## Stage 03 — Blue Ridge Outfitters Basic Quality

```bash
python tools/load_database.py \
    datasets/03_blue_ridge_outfitters_basic_quality \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --schema stage03
```

## Stage 04 — Carolina Home Services Operational

```bash
python tools/load_database.py \
    datasets/04_carolina_home_services_operational \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --schema stage04
```

## Stage 05 — Piedmont Logistics Multisource

```bash
python tools/load_database.py \
    datasets/05_piedmont_logistics_multisource \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --schema stage05
```

## Stage 06 — Smart Campus Timeseries

```bash
python tools/load_database.py \
    datasets/06_smart_campus_timeseries \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --schema stage06
```

## Stage 07 — Coastal Communications Capstone

```bash
python tools/load_database.py \
    datasets/07_coastal_communications_capstone \
    "postgresql+psycopg://analyst:password@localhost:5432/analytics" \
    --schema stage07
```

---

# Important Limitation: Database Constraints

The loader is intentionally generic and simple.

It uses:

```python
pandas.DataFrame.to_sql()
```

to infer destination tables from the CSV data.

Because of that, it does **not automatically reproduce the full relational design** represented by the generated SQL schema files.

The loader does not explicitly create:

- Primary keys
- Foreign keys
- Unique constraints
- Check constraints
- Indexes
- Views
- Stored procedures
- Triggers
- Database-specific column definitions

For example, the curriculum may logically define:

```text
customers
    customer_id PK

orders
    order_id PK
    customer_id FK -> customers.customer_id
```

The generic loader creates the columns, but it may not create actual `PRIMARY KEY` and `FOREIGN KEY` constraints.

This behavior is useful for introductory exercises, but it matters for advanced database instruction.

---

# Generated SQL Schema Files

Each dataset stage contains SQL-oriented files under:

```text
datasets/<stage>/sql/
```

including files such as:

```text
postgresql_schema.sql
sqlserver_schema.sql
```

Those files should be used when an exercise requires explicit relational structures.

```mermaid
flowchart LR
    A[SQL Schema File] --> B[Create Tables + Constraints]
    C[CSV Files] --> D[Load Data]
    B --> E[(Relational Database)]
    D --> E
```

The current `load_database.py` script does not execute the generated schema files automatically.

---

# Recommended Classroom Usage

## Beginner

For beginner SQL work, the generic loader is usually sufficient.

The focus can remain on:

- `SELECT`
- `WHERE`
- `ORDER BY`
- `GROUP BY`
- `JOIN`
- Aggregation

## Intermediate

For intermediate work, PostgreSQL or SQL Server is recommended.

Students can create:

- Views
- CTE-based queries
- Data-quality checks
- Reconciliation queries
- Analytical datasets
- Window-function analysis

## Advanced

For advanced coursework, students can be required to build a proper ingestion workflow:

```mermaid
flowchart LR
    A[CSV / JSON / API] --> B[(staging)]
    B --> C[Validation + Transformation]
    C --> D[(curated)]
    D --> E[(analytics)]
    E --> F[Power BI / Python]
```

A possible assignment sequence is:

1. Create the database schema.
2. Load raw files into staging tables.
3. Profile and validate the source data.
4. Correct or quarantine invalid records.
5. Transform the data into curated tables.
6. Create relational constraints and indexes.
7. Build an analytical layer.
8. Connect Power BI or Python to the analytical layer.

---

# Connection String Considerations

## Passwords With Special Characters

SQLAlchemy database URLs contain reserved characters.

If a username or password contains characters such as:

```text
@
:
/
?
#
%
```

those characters may need to be URL-encoded when embedded directly in the connection string.

## Credential Exposure

Because the current script accepts the connection string as a command-line argument, credentials may be visible in:

- Shell history
- Process listings
- Terminal output copied into documentation

Use dedicated training credentials and avoid production credentials.

Environment-variable or `.env` support would be a useful future enhancement.

---

# Troubleshooting

## `CSV directory not found`

Make sure the argument points to the stage directory.

Correct:

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "sqlite:///training.sqlite"
```

Incorrect:

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean/csv \
    "sqlite:///training.sqlite"
```

## PostgreSQL Driver Error

Install the repository dependencies:

```bash
pip install -r requirements.txt
```

or:

```bash
pip install "psycopg[binary]>=3.2"
```

## SQL Server Driver Error

Check installed ODBC drivers:

```python
import pyodbc

print(pyodbc.drivers())
```

Your connection string must reference a driver that is actually installed.

## Schema Does Not Exist

The loader accepts a schema name but does not create the schema.

PostgreSQL:

```sql
CREATE SCHEMA stage04;
```

SQL Server:

```sql
CREATE SCHEMA stage04;
```

## Tables Load but Relationships Are Missing

This is expected with the generic loader.

`pandas.to_sql()` creates tables from DataFrame columns but does not reproduce the full PK/FK/index definitions from the generated schema files.

Use the SQL schema files when those structures are part of the exercise.

## Duplicate Rows After `append`

`append` performs no deduplication.

If the same stage is loaded twice with:

```text
--if-exists append
```

the data may be duplicated.

Use `replace` when resetting a classroom database, or implement deduplication/constraints when teaching incremental loading.

---

# Summary

`load_database.py` provides a simple way to move generated curriculum data from CSV files into a relational database.

The typical workflow is:

```text
Generate Dataset
      ↓
Choose Curriculum Stage
      ↓
Run load_database.py
      ↓
Load PostgreSQL / SQL Server / SQLite
      ↓
Query and Validate
      ↓
Transform and Analyze
```

For introductory coursework, the automatically inferred tables are generally sufficient.

For advanced coursework, use the generated SQL schema files or require students to build a staging-to-curated workflow so they also gain experience with relational constraints, indexes, data types, and controlled data loading.
