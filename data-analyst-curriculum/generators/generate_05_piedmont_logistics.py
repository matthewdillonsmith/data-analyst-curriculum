from __future__ import annotations

from pathlib import Path
import json
import sqlite3

import numpy as np
import pandas as pd

from .common import GeneratorContext, money, random_dates, choose_state, ensure_dir
from .export_utils import export_dataset

STAGE = "05_piedmont_logistics_multisource"


def build_tables(scale: str = "small", seed: int = 505) -> tuple[dict[str, pd.DataFrame], dict]:
    ctx = GeneratorContext(seed, scale)

    n_customers = ctx.n(2000, max_value=50000)
    states = choose_state(ctx, n_customers)
    customers = pd.DataFrame({
        "customer_id": range(100001, 100001 + n_customers),
        "customer_name": [ctx.fake.company() for _ in range(n_customers)],
        "billing_state": states,
        "active_flag": ctx.rng.choice([1, 0], size=n_customers, p=[0.91, 0.09]),
        "created_date": random_dates(ctx, n_customers, "2019-01-01", "2025-12-31").dt.strftime("%Y-%m-%d"),
    })

    n_warehouses = 10
    warehouses = pd.DataFrame({
        "warehouse_id": range(1, n_warehouses + 1),
        "warehouse_name": [f"Distribution Center {i:02d}" for i in range(1, n_warehouses + 1)],
        "city": [ctx.fake.city() for _ in range(n_warehouses)],
        "state": choose_state(ctx, n_warehouses),
    })

    n_drivers = ctx.n(120, max_value=1800)
    drivers = pd.DataFrame({
        "driver_id": range(1, n_drivers + 1),
        "driver_name": [ctx.fake.name() for _ in range(n_drivers)],
        "home_warehouse_id": ctx.rng.integers(1, n_warehouses + 1, size=n_drivers),
        "hire_date": random_dates(ctx, n_drivers, "2016-01-01", "2025-12-31").dt.strftime("%Y-%m-%d"),
        "active_flag": ctx.rng.choice([1, 0], size=n_drivers, p=[0.94, 0.06]),
    })

    n_vehicles = ctx.n(100, max_value=1500)
    vehicles = pd.DataFrame({
        "vehicle_id": range(1000, 1000 + n_vehicles),
        "vin_last8": [ctx.fake.bothify(text="??######").upper() for _ in range(n_vehicles)],
        "home_warehouse_id": ctx.rng.integers(1, n_warehouses + 1, size=n_vehicles),
        "model_year": ctx.rng.integers(2016, 2027, size=n_vehicles),
        "vehicle_type": ctx.rng.choice(["Box Truck", "Tractor", "Cargo Van"], size=n_vehicles, p=[0.42, 0.38, 0.20]),
    })

    n_shipments = ctx.n(5000, max_value=150000)
    pickup_ts = random_dates(ctx, n_shipments, "2025-01-01", "2026-06-30").sort_values().reset_index(drop=True)
    transit_hours = ctx.rng.integers(3, 120, size=n_shipments)
    promised_ts = pickup_ts + pd.to_timedelta(transit_hours, unit="h")
    actual_ts = promised_ts + pd.to_timedelta(ctx.rng.integers(-12, 36, size=n_shipments), unit="h")
    shipment_status = np.where(actual_ts <= pd.Timestamp("2026-06-30 23:59:59"), "Delivered", "In Transit")
    shipments = pd.DataFrame({
        "shipment_id": range(500001, 500001 + n_shipments),
        "customer_id": ctx.rng.choice(customers["customer_id"], size=n_shipments),
        "origin_warehouse_id": ctx.rng.integers(1, n_warehouses + 1, size=n_shipments),
        "driver_id": ctx.rng.integers(1, n_drivers + 1, size=n_shipments),
        "vehicle_id": ctx.rng.choice(vehicles["vehicle_id"], size=n_shipments),
        "pickup_timestamp": pickup_ts.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "promised_delivery_timestamp": promised_ts.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "actual_delivery_timestamp": pd.Series(actual_ts).dt.strftime("%Y-%m-%d %H:%M:%S"),
        "status": shipment_status,
        "weight_lbs": money(ctx.rng.lognormal(mean=6.2, sigma=0.8, size=n_shipments)),
    })

    event_rows = []
    event_id = 1
    for row in shipments.itertuples(index=False):
        pickup = pd.Timestamp(row.pickup_timestamp)
        promised = pd.Timestamp(row.promised_delivery_timestamp)
        actual = pd.Timestamp(row.actual_delivery_timestamp)
        checkpoints = [
            ("PICKED_UP", pickup),
            ("IN_TRANSIT", pickup + (promised - pickup) * 0.35),
            ("AT_TERMINAL", pickup + (promised - pickup) * 0.7),
            ("DELIVERED", actual),
        ]
        for event_type, ts in checkpoints:
            event_rows.append({
                "delivery_event_id": event_id,
                "shipment_id": int(row.shipment_id),
                "event_type": event_type,
                "event_timestamp": pd.Timestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
            })
            event_id += 1
    delivery_events = pd.DataFrame(event_rows)

    # CRM/customer-master source. Deliberately conflicts with billing state for a subset.
    customer_master = customers[["customer_id", "customer_name", "billing_state"]].copy()
    customer_master = customer_master.rename(columns={"billing_state": "crm_state"})
    conflict_idx = ctx.rng.choice(customer_master.index, size=max(1, int(n_customers * 0.025)), replace=False)
    state_choices = np.array(["NC", "SC", "VA", "GA", "TN", "FL"])
    for idx in conflict_idx:
        current = customer_master.at[idx, "crm_state"]
        alternatives = state_choices[state_choices != current]
        customer_master.at[idx, "crm_state"] = ctx.rng.choice(alternatives)
    customer_master["mailing_address"] = [ctx.fake.street_address() for _ in range(n_customers)]
    customer_master["mailing_city"] = [ctx.fake.city() for _ in range(n_customers)]

    # Fuel source uses inconsistent vehicle IDs and contains duplicates.
    n_fuel = ctx.n(8000, max_value=240000)
    selected_vehicle_ids = ctx.rng.choice(vehicles["vehicle_id"], size=n_fuel)
    fuel_ts = random_dates(ctx, n_fuel, "2025-01-01", "2026-06-30").sort_values().reset_index(drop=True)
    fuel_transactions = pd.DataFrame({
        "fuel_transaction_id": range(700001, 700001 + n_fuel),
        "vehicle": [f"TRK{int(v)}" for v in selected_vehicle_ids],
        "transaction_timestamp": fuel_ts.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "gallons": money(ctx.rng.uniform(3, 180, size=n_fuel)),
        "price_per_gallon": money(ctx.rng.uniform(2.4, 5.2, size=n_fuel)),
    })
    fuel_transactions["total_cost"] = (fuel_transactions["gallons"] * fuel_transactions["price_per_gallon"]).round(2)
    dup_fuel_n = max(1, int(n_fuel * 0.004))
    dup_fuel = fuel_transactions.sample(n=dup_fuel_n, random_state=seed).copy()
    fuel_transactions = pd.concat([fuel_transactions, dup_fuel], ignore_index=True)

    # GPS source simulates an API payload and uses TRK-#### identifiers.
    n_gps = ctx.n(10000, max_value=300000)
    gps_vehicle_ids = ctx.rng.choice(vehicles["vehicle_id"], size=n_gps)
    gps_ts = random_dates(ctx, n_gps, "2026-04-01", "2026-06-30").sort_values().reset_index(drop=True)
    gps_events = pd.DataFrame({
        "gps_event_id": range(1, n_gps + 1),
        "vehicle_id": [f"TRK-{int(v)}" for v in gps_vehicle_ids],
        "timestamp": gps_ts.dt.strftime("%Y-%m-%dT%H:%M:%S"),
        "latitude": np.round(ctx.rng.uniform(32.0, 37.0, size=n_gps), 6),
        "longitude": np.round(ctx.rng.uniform(-84.5, -75.0, size=n_gps), 6),
        "speed_mph": np.round(np.maximum(0, ctx.rng.normal(44, 18, size=n_gps)), 1),
    })

    # Missing drivers in a small number of shipment rows.
    missing_driver_idx = ctx.rng.choice(shipments.index, size=max(1, int(n_shipments * 0.006)), replace=False)
    shipments.loc[missing_driver_idx, "driver_id"] = np.nan

    tables = {
        "customers": customers,
        "customer_master": customer_master,
        "warehouses": warehouses,
        "drivers": drivers,
        "vehicles": vehicles,
        "shipments": shipments,
        "delivery_events": delivery_events,
        "fuel_transactions": fuel_transactions,
        "gps_events": gps_events,
    }
    manifest = {
        "teaching_goal": "Multi-source integration, source-of-truth reasoning, identifier normalization, files + database + API-style JSON.",
        "known_quality_defects": [
            "crm_vs_billing_state_conflicts", "duplicate_fuel_transactions", "missing_shipment_driver_ids", "vehicle_identifier_format_mismatch"
        ],
        "ground_truth": {
            "crm_vs_billing_state_conflicts": int(len(conflict_idx)),
            "duplicate_fuel_transactions": int(dup_fuel_n),
            "missing_shipment_driver_ids": int(len(missing_driver_idx)),
            "vehicle_identifier_formats": ["1000", "TRK1000", "TRK-1000"],
        },
        "source_semantics": {
            "customers.billing_state": "Billing/service state",
            "customer_master.crm_state": "CRM mailing state",
        },
    }
    return tables, manifest


def write_native_sources(stage_dir: Path, tables: dict[str, pd.DataFrame]) -> None:
    native = ensure_dir(stage_dir / "native_sources")
    core_dir = ensure_dir(native / "database")
    csv_dir = ensure_dir(native / "csv")
    api_dir = ensure_dir(native / "api_json")

    # Operational core database.
    core_tables = ["customers", "warehouses", "drivers", "vehicles", "shipments", "delivery_events"]
    core_path = core_dir / "piedmont_logistics_core.sqlite"
    if core_path.exists():
        core_path.unlink()
    with sqlite3.connect(core_path) as conn:
        for name in core_tables:
            tables[name].to_sql(name, conn, if_exists="replace", index=False)

    tables["customer_master"].to_csv(csv_dir / "customer_master.csv", index=False)
    tables["fuel_transactions"].to_csv(csv_dir / "fuel_transactions.csv", index=False)

    gps_records = json.loads(tables["gps_events"].to_json(orient="records"))
    (api_dir / "gps_events_api_payload.json").write_text(json.dumps({"results": gps_records}, separators=(",", ":")), encoding="utf-8")


def generate(root: Path, scale: str = "small", seed: int = 505) -> Path:
    tables, manifest = build_tables(scale, seed)
    stage_dir = export_dataset(
        root, STAGE, "Piedmont Logistics", "Stage 5 — Upper Intermediate / Multi-Source Integration",
        tables,
        primary_keys={
            "customers": ["customer_id"], "warehouses": ["warehouse_id"], "drivers": ["driver_id"], "vehicles": ["vehicle_id"],
            "shipments": ["shipment_id"], "delivery_events": ["delivery_event_id"], "gps_events": ["gps_event_id"],
        },
        manifest=manifest,
        notes="A logistics company spread across an operational database, customer-master CSV, fuel CSV, and GPS API-style JSON. Students must normalize IDs and resolve source-of-truth questions.",
    )
    write_native_sources(stage_dir, tables)
    return stage_dir
