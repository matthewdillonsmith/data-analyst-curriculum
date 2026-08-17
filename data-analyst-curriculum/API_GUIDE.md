# API Guide

The included FastAPI application turns every generated stage into a read-only REST-style API backed by the stage's SQLite database.

## Start locally

```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Interactive OpenAPI/Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Discover datasets

```http
GET /stages
```

## Discover tables in a stage

```http
GET /stages/05_piedmont_logistics_multisource/tables
```

## Retrieve rows

```http
GET /stages/05_piedmont_logistics_multisource/gps_events?limit=100&offset=0
```

The response is intentionally wrapped in a typical API envelope:

```json
{
  "stage": "05_piedmont_logistics_multisource",
  "table": "gps_events",
  "total_rows": 10000,
  "limit": 100,
  "offset": 0,
  "results": []
}
```

## Pagination

```http
GET /stages/05_piedmont_logistics_multisource/gps_events?limit=500&offset=0
GET /stages/05_piedmont_logistics_multisource/gps_events?limit=500&offset=500
GET /stages/05_piedmont_logistics_multisource/gps_events?limit=500&offset=1000
```

Maximum page size is 5,000 rows.

## Filtering

```http
GET /stages/02_blue_ridge_outfitters_clean/orders?filter_column=order_status&filter_value=Completed
```

## Sorting

```http
GET /stages/02_blue_ridge_outfitters_clean/orders?sort_by=order_timestamp&sort_dir=desc
```

## Schema inspection

```http
GET /stages/06_smart_campus_timeseries/sensor_readings/schema
```

## Python example

```python
import requests
import pandas as pd

url = "http://127.0.0.1:8000/stages/05_piedmont_logistics_multisource/gps_events"

response = requests.get(
    url,
    params={
        "limit": 1000,
        "offset": 0,
    },
    timeout=30,
)
response.raise_for_status()

payload = response.json()
df = pd.DataFrame(payload["results"])

print(df.head())
```

## Curriculum use

Early API assignments can explicitly provide the endpoint and pagination rules. Advanced assignments can simply provide the base URL and require students to inspect `/docs`, determine the relevant endpoint, retrieve all pages, validate counts, and persist the results.
