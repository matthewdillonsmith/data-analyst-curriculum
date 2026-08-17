from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

APP_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = Path(os.getenv("CURRICULUM_DATA_ROOT", APP_ROOT / "datasets")).resolve()

app = FastAPI(
    title="Data Analyst Curriculum Dataset API",
    description=(
        "Read-only API for the staged synthetic datasets used in the Data Analyst curriculum. "
        "Each stage is backed by its generated SQLite database."
    ),
    version="1.0.0",
)


def safe_name(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
        raise HTTPException(status_code=400, detail="Invalid identifier")
    return value


def stage_dirs() -> list[Path]:
    if not DATA_ROOT.exists():
        return []
    return sorted([p for p in DATA_ROOT.iterdir() if p.is_dir() and (p / "database").exists()])


def find_stage(stage: str) -> Path:
    for path in stage_dirs():
        if path.name == stage:
            return path
    raise HTTPException(status_code=404, detail=f"Unknown stage: {stage}")


def db_path(stage: str) -> Path:
    stage_dir = find_stage(stage)
    expected = stage_dir / "database" / f"{stage}.sqlite"
    if not expected.exists():
        raise HTTPException(status_code=404, detail="Stage database not generated")
    return expected


def table_names(stage: str) -> list[str]:
    with sqlite3.connect(db_path(stage)) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    return [row[0] for row in rows]


def table_columns(stage: str, table: str) -> list[str]:
    table = safe_name(table)
    if table not in table_names(stage):
        raise HTTPException(status_code=404, detail=f"Unknown table: {table}")
    with sqlite3.connect(db_path(stage)) as conn:
        rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    return [row[1] for row in rows]


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "Data Analyst Curriculum Dataset API",
        "docs": "/docs",
        "stages_endpoint": "/stages",
    }


@app.get("/stages")
def list_stages() -> list[dict[str, Any]]:
    result = []
    for stage_dir in stage_dirs():
        result.append({
            "stage": stage_dir.name,
            "tables": table_names(stage_dir.name),
        })
    return result


@app.get("/stages/{stage}/tables")
def list_tables(stage: str) -> dict[str, Any]:
    find_stage(stage)
    return {"stage": stage, "tables": table_names(stage)}


@app.get("/stages/{stage}/{table}")
def get_rows(
    stage: str,
    table: str,
    limit: int = Query(default=100, ge=1, le=5000),
    offset: int = Query(default=0, ge=0),
    sort_by: str | None = None,
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    filter_column: str | None = None,
    filter_value: str | None = None,
) -> JSONResponse:
    table = safe_name(table)
    columns = table_columns(stage, table)

    sql = f'SELECT * FROM "{table}"'
    params: list[Any] = []
    if filter_column is not None:
        if filter_column not in columns:
            raise HTTPException(status_code=400, detail=f"Unknown filter column: {filter_column}")
        sql += f' WHERE CAST("{filter_column}" AS TEXT) = ?'
        params.append(filter_value)

    if sort_by is not None:
        if sort_by not in columns:
            raise HTTPException(status_code=400, detail=f"Unknown sort column: {sort_by}")
        sql += f' ORDER BY "{sort_by}" {sort_dir.upper()}'

    sql += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with sqlite3.connect(db_path(stage)) as conn:
        conn.row_factory = sqlite3.Row
        rows = [dict(row) for row in conn.execute(sql, params).fetchall()]
        count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

    return JSONResponse({
        "stage": stage,
        "table": table,
        "total_rows": count,
        "limit": limit,
        "offset": offset,
        "results": rows,
    })


@app.get("/stages/{stage}/{table}/schema")
def get_schema(stage: str, table: str) -> dict[str, Any]:
    table = safe_name(table)
    columns = table_columns(stage, table)
    with sqlite3.connect(db_path(stage)) as conn:
        rows = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
    return {
        "stage": stage,
        "table": table,
        "columns": [
            {
                "name": row[1],
                "type": row[2],
                "not_null": bool(row[3]),
                "default": row[4],
                "primary_key_position": row[5],
            }
            for row in rows
        ],
    }
