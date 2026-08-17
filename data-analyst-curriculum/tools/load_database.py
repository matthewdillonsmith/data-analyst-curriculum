from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load a generated stage's CSV files into any SQLAlchemy-supported database."
    )
    parser.add_argument("stage_dir", help="Path to a stage directory, e.g. datasets/02_blue_ridge_outfitters_clean")
    parser.add_argument(
        "connection_string",
        help=(
            "SQLAlchemy connection string. Examples: "
            "postgresql+psycopg://user:password@localhost/analytics or "
            "mssql+pyodbc://user:password@server/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
        ),
    )
    parser.add_argument("--schema", default=None, help="Destination database schema, if supported")
    parser.add_argument("--if-exists", choices=["fail", "replace", "append"], default="replace")
    args = parser.parse_args()

    stage_dir = Path(args.stage_dir).resolve()
    csv_dir = stage_dir / "csv"
    if not csv_dir.exists():
        raise SystemExit(f"CSV directory not found: {csv_dir}")

    engine = create_engine(args.connection_string)
    for csv_path in sorted(csv_dir.glob("*.csv")):
        table = csv_path.stem
        print(f"Loading {table} from {csv_path.name}...")
        df = pd.read_csv(csv_path, low_memory=False)
        df.to_sql(
            table,
            engine,
            schema=args.schema,
            if_exists=args.if_exists,
            index=False,
            chunksize=1000,
            method=None,
        )
    print("Load complete.")


if __name__ == "__main__":
    main()
