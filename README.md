# Data Analyst Curriculum — Synthetic Dataset Repository

This repository contains a staged family of synthetic datasets for a community-college Data Analyst certificate/diploma program. The data begins clean and highly structured, then becomes progressively more realistic, ambiguous, multi-source, and operationally messy.

The repository is designed so the same academic program can teach:

- Excel / Power Query
- SQL
- Python / pandas
- Statistics
- Power BI / data visualization
- Data quality and governance
- APIs and JSON
- ETL / ELT
- Time-series analysis
- Requirements gathering
- Enterprise analytics project delivery

All custom datasets are synthetic. They contain no real cooperative member information.

## Repository structure

```text
data-analyst-curriculum/
│
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
│
├── datasets/
│   ├── 01_northwind_starter/
│   │   ├── csv/
│   │   ├── json/
│   │   ├── database/
│   │   └── sql/
│   ├── 02_blue_ridge_outfitters_clean/
│   ├── 03_blue_ridge_outfitters_basic_quality/
│   ├── 04_carolina_home_services_operational/
│   ├── 05_piedmont_logistics_multisource/
│   ├── 06_smart_campus_timeseries/
│   └── 07_coastal_communications_capstone/
│
├── generators/
│   ├── common.py
│   ├── export_utils.py
│   ├── generate_all.py
│   ├── generate_stage.py
│   └── stage-specific generators...
│
├── instructor/
│   ├── manifests/
│   ├── answer_keys/
│   └── rubrics/
│
├── student/
│   ├── data_dictionaries/
│   ├── assignments/
│   └── templates/
│
├── api/
│   └── main.py
│
└── tools/
    └── load_database.py
```

## Academic progression

| Stage | Dataset | Difficulty | Primary instructional purpose |
|---|---|---|---|
| 01 | Northwind-Style Starter | Absolute Beginner | Relational concepts, beginner SQL, beginner Excel |
| 02 | Blue Ridge Outfitters — Clean | Beginner | Clean modern business data, Excel, SQL, statistics |
| 03 | Blue Ridge Outfitters — Raw | Early Intermediate | Missing data, duplicates, inconsistent values, data profiling |
| 04 | Carolina Home Services | Intermediate | Event data, work orders, cycle time, grain, join multiplication |
| 05 | Piedmont Logistics | Upper Intermediate | Multi-source integration, CSV + database + API-style JSON, source-of-truth conflicts |
| 06 | Smart Campus | Advanced | High-volume time series, DST, missing intervals, duplicates, anomalies |
| 07 | Coastal Communications Cooperative | Advanced Capstone | Enterprise ambiguity, SCDs, snapshots, late-arriving data, conflicting definitions |

## Dataset formats

Every stage is exported in multiple forms:

```text
csv/            One CSV per table
json/           One JSON array per table
database/       Ready-to-query SQLite database
sql/            PostgreSQL and SQL Server schema DDL
```

Stages 05 and 07 additionally include `native_sources/` directories that deliberately split the company across database, CSV, and API-style JSON sources.

## Generate the datasets

Create a Python virtual environment and install dependencies:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

Generate the included small teaching versions:

```bash
python -m generators.generate_all --scale small
```

Generate only one stage:

```bash
python -m generators.generate_stage 04 --scale small
```

Supported scales:

```text
small     Classroom / laptop friendly
medium    Larger labs and database exercises
large     Performance and higher-volume exercises
```

The generated repository ships with the `small` versions already populated.

## Reproducibility

The generators use deterministic random seeds. The instructor manifests record the intended defects and their generated counts.

This allows faculty to know the ground truth while students are expected to discover issues through profiling and validation.

## Instructor versus student materials

### `instructor/`

Contains:

- Ground-truth defect manifests
- Instructor answer keys
- Suggested validation queries
- Grading rubrics

These files should not be distributed to students before assignments are complete.

### `student/`

Contains:

- Data dictionaries
- Assignments
- Project templates
- Data-quality checklists

As the stages advance, student documentation becomes deliberately less complete.

## Run the dataset API

Every generated SQLite stage can be exposed through the included FastAPI application.

Start locally:

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Then open the automatically generated API documentation at:

```text
http://127.0.0.1:8000/docs
```

Useful routes:

```text
GET /stages
GET /stages/{stage}/tables
GET /stages/{stage}/{table}
GET /stages/{stage}/{table}/schema
```

Example:

```text
GET /stages/02_blue_ridge_outfitters_clean/orders?limit=100
```

Filtering example:

```text
GET /stages/02_blue_ridge_outfitters_clean/orders?filter_column=order_status&filter_value=Completed
```

The API is intentionally read-only.

## Docker API

Run:

```bash
docker compose up --build
```

The API will be available on port `8000`.

## Load into PostgreSQL or SQL Server

A ready-to-use SQLite database is included for every stage. To teach against PostgreSQL or SQL Server, load the CSV exports using `tools/load_database.py`.

PostgreSQL example:

```bash
python tools/load_database.py \
    datasets/02_blue_ridge_outfitters_clean \
    "postgresql+psycopg://analyst:password@localhost/analytics"
```

SQL Server example:

```powershell
python tools/load_database.py `
    datasets/02_blue_ridge_outfitters_clean `
    "mssql+pyodbc://analyst:password@localhost/analytics?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
```

The `sql/` directory in each stage also contains generated DDL for PostgreSQL and SQL Server.

## Recommended teaching philosophy

The degree of assignment guidance should decrease as the data becomes more difficult.

### Early stage

> Write a query showing sales by state.

### Intermediate stage

> Validate the customer and order data, then determine which states generated the most revenue.

### Advanced stage

> Finance and Operations report different active-customer totals. Determine why and recommend a governed definition for leadership reporting.

At the advanced level, students should not be told which table, column, join, or defect is responsible.
