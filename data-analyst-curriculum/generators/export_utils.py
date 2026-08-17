from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .common import ensure_dir


TYPE_MAP_POSTGRES = {
    "int64": "BIGINT",
    "int32": "INTEGER",
    "float64": "DOUBLE PRECISION",
    "float32": "REAL",
    "bool": "BOOLEAN",
    "datetime64[ns]": "TIMESTAMP",
}

TYPE_MAP_SQLSERVER = {
    "int64": "BIGINT",
    "int32": "INT",
    "float64": "FLOAT",
    "float32": "REAL",
    "bool": "BIT",
    "datetime64[ns]": "DATETIME2",
}


def sql_identifier(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def infer_sql_type(series: pd.Series, dialect: str) -> str:
    dtype = str(series.dtype)
    mapping = TYPE_MAP_POSTGRES if dialect == "postgresql" else TYPE_MAP_SQLSERVER
    if dtype in mapping:
        return mapping[dtype]
    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"
    if pd.api.types.is_float_dtype(series):
        return "DOUBLE PRECISION" if dialect == "postgresql" else "FLOAT"
    if pd.api.types.is_bool_dtype(series):
        return "BOOLEAN" if dialect == "postgresql" else "BIT"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP" if dialect == "postgresql" else "DATETIME2"

    nonnull = series.dropna().astype(str)
    max_len = int(nonnull.str.len().max()) if not nonnull.empty else 50
    if max_len > 4000:
        return "TEXT" if dialect == "postgresql" else "NVARCHAR(MAX)"
    size = max(20, min(max_len + 10, 4000))
    return f"VARCHAR({size})" if dialect == "postgresql" else f"NVARCHAR({size})"


def create_schema_sql(
    tables: dict[str, pd.DataFrame],
    primary_keys: dict[str, list[str]],
    foreign_keys: dict[str, list[tuple[list[str], str, list[str]]]],
    dialect: str,
) -> str:
    drops = [f"DROP TABLE IF EXISTS {sql_identifier(name)};" for name in reversed(list(tables.keys()))]
    blocks: list[str] = []
    for table_name, df in tables.items():
        cols = []
        for col in df.columns:
            cols.append(f"    {sql_identifier(col)} {infer_sql_type(df[col], dialect)}")
        pk = primary_keys.get(table_name)
        if pk:
            cols.append("    PRIMARY KEY (" + ", ".join(sql_identifier(x) for x in pk) + ")")
        for local_cols, ref_table, ref_cols in foreign_keys.get(table_name, []):
            cols.append(
                "    FOREIGN KEY ("
                + ", ".join(sql_identifier(x) for x in local_cols)
                + ") REFERENCES "
                + sql_identifier(ref_table)
                + " ("
                + ", ".join(sql_identifier(x) for x in ref_cols)
                + ")"
            )
        blocks.append(
            f"CREATE TABLE {sql_identifier(table_name)} (\n"
            + ",\n".join(cols)
            + "\n);"
        )
    return "\n".join(drops) + "\n\n" + "\n\n".join(blocks) + "\n"


def normalize_for_export(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for col in result.columns:
        if pd.api.types.is_datetime64_any_dtype(result[col]):
            result[col] = result[col].dt.strftime("%Y-%m-%d %H:%M:%S")
    return result


def export_dataset(
    root: Path,
    stage_name: str,
    title: str,
    difficulty: str,
    tables: dict[str, pd.DataFrame],
    primary_keys: dict[str, list[str]] | None = None,
    foreign_keys: dict[str, list[tuple[list[str], str, list[str]]]] | None = None,
    manifest: dict[str, Any] | None = None,
    notes: str = "",
) -> Path:
    primary_keys = primary_keys or {}
    foreign_keys = foreign_keys or {}
    manifest = manifest or {}
    stage_dir = ensure_dir(root / "datasets" / stage_name)
    csv_dir = ensure_dir(stage_dir / "csv")
    json_dir = ensure_dir(stage_dir / "json")
    db_dir = ensure_dir(stage_dir / "database")
    sql_dir = ensure_dir(stage_dir / "sql")

    normalized = {name: normalize_for_export(df) for name, df in tables.items()}

    for name, df in normalized.items():
        df.to_csv(csv_dir / f"{name}.csv", index=False)
        records = json.loads(df.to_json(orient="records", date_format="iso"))
        (json_dir / f"{name}.json").write_text(
            json.dumps(records, separators=(",", ":"), ensure_ascii=False), encoding="utf-8"
        )

    sqlite_path = db_dir / f"{stage_name}.sqlite"
    if sqlite_path.exists():
        sqlite_path.unlink()
    with sqlite3.connect(sqlite_path) as conn:
        for name, df in normalized.items():
            df.to_sql(name, conn, if_exists="replace", index=False)

    (sql_dir / "postgresql_schema.sql").write_text(
        create_schema_sql(tables, primary_keys, foreign_keys, "postgresql"), encoding="utf-8"
    )
    (sql_dir / "sqlserver_schema.sql").write_text(
        create_schema_sql(tables, primary_keys, foreign_keys, "sqlserver"), encoding="utf-8"
    )

    info = {
        "stage": stage_name,
        "title": title,
        "difficulty": difficulty,
        "tables": {name: int(len(df)) for name, df in tables.items()},
        "formats": ["csv", "json", "sqlite", "postgresql_schema", "sqlserver_schema"],
        "notes": notes,
    }
    (stage_dir / "dataset_info.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

    readme = f"""# {title}\n\n**Stage:** `{stage_name}`  \n**Difficulty:** {difficulty}\n\n{notes}\n\n## Included formats\n\n- `csv/` — one CSV per table\n- `json/` — one JSON array per table\n- `database/{stage_name}.sqlite` — ready-to-query SQLite database\n- `sql/postgresql_schema.sql` — PostgreSQL DDL\n- `sql/sqlserver_schema.sql` — SQL Server DDL\n\n## Tables\n\n"""
    for name, df in tables.items():
        readme += f"- `{name}` — {len(df):,} rows\n"
    (stage_dir / "README.md").write_text(readme, encoding="utf-8")

    manifest_path = ensure_dir(root / "instructor" / "manifests") / f"{stage_name}.yaml"
    manifest_doc = {
        "stage": stage_name,
        "title": title,
        "difficulty": difficulty,
        "row_counts": {name: int(len(df)) for name, df in tables.items()},
        **manifest,
    }
    manifest_path.write_text(yaml.safe_dump(manifest_doc, sort_keys=False), encoding="utf-8")
    return stage_dir
