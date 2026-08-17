from __future__ import annotations

from pathlib import Path
import json
import sqlite3

import numpy as np
import pandas as pd

from .common import GeneratorContext, money, random_dates, choose_state, ensure_dir
from .export_utils import export_dataset

STAGE = "07_coastal_communications_capstone"


def build_tables(scale: str = "small", seed: int = 707) -> tuple[dict[str, pd.DataFrame], dict]:
    ctx = GeneratorContext(seed, scale)

    n_members = ctx.n(2000, max_value=50000)
    members = pd.DataFrame({
        "member_id": range(100001, 100001 + n_members),
        "first_name": [ctx.fake.first_name() for _ in range(n_members)],
        "last_name": [ctx.fake.last_name() for _ in range(n_members)],
        "email": [ctx.fake.unique.email() for _ in range(n_members)],
        "phone": [ctx.fake.numerify("###-###-####") for _ in range(n_members)],
        "join_date": random_dates(ctx, n_members, "2014-01-01", "2025-12-31").dt.strftime("%Y-%m-%d"),
        "crm_status_cd": ctx.rng.choice(["A", "I", "P"], size=n_members, p=[0.86, 0.10, 0.04]),
    })

    addresses = pd.DataFrame({
        "address_id": range(1, n_members + 1),
        "member_id": members["member_id"],
        "address_type": "MAILING",
        "street": [ctx.fake.street_address() for _ in range(n_members)],
        "city": [ctx.fake.city() for _ in range(n_members)],
        "state": choose_state(ctx, n_members),
        "zipcode": [ctx.fake.postcode()[:5] for _ in range(n_members)],
    })

    n_accounts = ctx.n(2500, max_value=65000)
    account_member = ctx.rng.choice(members["member_id"], size=n_accounts)
    account_start = random_dates(ctx, n_accounts, "2018-01-01", "2026-01-31")
    active_mask = ctx.rng.random(n_accounts) < 0.84
    account_end = []
    for start, active in zip(account_start, active_mask):
        if active:
            account_end.append(None)
        else:
            end = pd.Timestamp(start) + pd.Timedelta(days=int(ctx.rng.integers(60, 1500)))
            account_end.append(min(end, pd.Timestamp("2026-06-30")).strftime("%Y-%m-%d"))
    accounts = pd.DataFrame({
        "account_id": range(300001, 300001 + n_accounts),
        "member_id": account_member,
        "service_address": [ctx.fake.street_address() for _ in range(n_accounts)],
        "service_city": [ctx.fake.city() for _ in range(n_accounts)],
        "service_state": choose_state(ctx, n_accounts),
        "start_date": account_start.dt.strftime("%Y-%m-%d"),
        "end_date": account_end,
        "billing_status_cd": np.where(active_mask, "ACTIVE", "CLOSED"),
    })

    plan_names = ["BASIC100", "FIBER500", "GIG1", "BUSINESS500", "BUSINESS1G"]
    plan_rows = []
    plan_history_id = 1
    for row in accounts.itertuples(index=False):
        first_plan = str(ctx.rng.choice(plan_names))
        start = pd.Timestamp(row.start_date)
        if ctx.rng.random() < 0.34 and start < pd.Timestamp("2025-01-01"):
            change = start + pd.Timedelta(days=int(ctx.rng.integers(180, 1200)))
            if change < pd.Timestamp("2026-06-30"):
                plan_rows.append({
                    "plan_history_id": plan_history_id,
                    "account_id": int(row.account_id),
                    "plan_cd": first_plan,
                    "effective_start": start.strftime("%Y-%m-%d"),
                    "effective_end": (change - pd.Timedelta(days=1)).strftime("%Y-%m-%d"),
                })
                plan_history_id += 1
                second = str(ctx.rng.choice([x for x in plan_names if x != first_plan]))
                plan_rows.append({
                    "plan_history_id": plan_history_id,
                    "account_id": int(row.account_id),
                    "plan_cd": second,
                    "effective_start": change.strftime("%Y-%m-%d"),
                    "effective_end": None,
                })
                plan_history_id += 1
                continue
        plan_rows.append({
            "plan_history_id": plan_history_id,
            "account_id": int(row.account_id),
            "plan_cd": first_plan,
            "effective_start": start.strftime("%Y-%m-%d"),
            "effective_end": None,
        })
        plan_history_id += 1
    plan_history = pd.DataFrame(plan_rows)

    # Monthly billing rows.
    bill_rows = []
    bill_id = 500001
    months = pd.period_range("2025-01", "2026-06", freq="M")
    plan_price = {"BASIC100": 54.99, "FIBER500": 79.99, "GIG1": 99.99, "BUSINESS500": 129.99, "BUSINESS1G": 179.99}
    plan_by_account = plan_history.sort_values("effective_start").groupby("account_id").tail(1).set_index("account_id")["plan_cd"].to_dict()
    for row in accounts.itertuples(index=False):
        start = pd.Timestamp(row.start_date)
        end = pd.Timestamp(row.end_date) if row.end_date else pd.Timestamp("2026-06-30")
        for month in months:
            month_start = month.start_time
            month_end = month.end_time
            if month_end < start or month_start > end:
                continue
            plan = plan_by_account.get(int(row.account_id), "BASIC100")
            base = plan_price[plan]
            taxes = round(base * float(ctx.rng.uniform(0.035, 0.075)), 2)
            misc = round(float(ctx.rng.choice([0, 0, 0, 4.99, 9.99, -5.00])), 2)
            bill_rows.append({
                "bill_id": bill_id,
                "account_id": int(row.account_id),
                "billing_month": month.strftime("%Y-%m"),
                "bill_date": month_start.strftime("%Y-%m-%d"),
                "service_amount": base,
                "tax_amount": taxes,
                "adjustment_amount": misc,
                "total_due": round(base + taxes + misc, 2),
                "load_timestamp": (month_start + pd.Timedelta(days=int(ctx.rng.integers(0, 4)))).strftime("%Y-%m-%d %H:%M:%S"),
            })
            bill_id += 1
    bills = pd.DataFrame(bill_rows)

    # Duplicate import block: a subset of bills are imported twice with new bill_id values.
    dup_bill_n = max(1, int(len(bills) * 0.006))
    dup_bills = bills.sample(n=dup_bill_n, random_state=seed).copy()
    dup_bills["bill_id"] = range(int(bills["bill_id"].max()) + 1, int(bills["bill_id"].max()) + 1 + dup_bill_n)
    dup_bills["load_timestamp"] = pd.to_datetime(dup_bills["load_timestamp"]) + pd.Timedelta(hours=3)
    dup_bills["load_timestamp"] = dup_bills["load_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    bills = pd.concat([bills, dup_bills], ignore_index=True)

    # Payments: not every bill is paid, and some load late.
    paid = bills.sample(frac=0.91, random_state=seed + 1).copy().reset_index(drop=True)
    payments = pd.DataFrame({
        "payment_id": range(700001, 700001 + len(paid)),
        "bill_id": paid["bill_id"],
        "account_id": paid["account_id"],
        "payment_date": (pd.to_datetime(paid["bill_date"]) + pd.to_timedelta(ctx.rng.integers(5, 45, size=len(paid)), unit="D")).dt.strftime("%Y-%m-%d"),
        "payment_amount": paid["total_due"],
    })
    late_load_idx = ctx.rng.choice(payments.index, size=max(1, int(len(payments) * 0.015)), replace=False)
    payments["load_timestamp"] = pd.to_datetime(payments["payment_date"]) + pd.to_timedelta(ctx.rng.integers(0, 3, size=len(payments)), unit="D")
    payments.loc[late_load_idx, "load_timestamp"] = pd.to_datetime(payments.loc[late_load_idx, "payment_date"]) + pd.to_timedelta(30, unit="D")
    payments["load_timestamp"] = payments["load_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

    adjustments = bills.sample(frac=0.08, random_state=seed + 2)[["bill_id", "account_id"]].reset_index(drop=True)
    adjustments["adjustment_id"] = range(1, len(adjustments) + 1)
    adjustments["adjustment_type_cd"] = ctx.rng.choice(["CR", "DR", "PROMO", "WRITE_OFF"], size=len(adjustments), p=[0.40, 0.25, 0.25, 0.10])
    adjustments["amount"] = money(ctx.rng.uniform(2, 90, size=len(adjustments)))
    adjustments.loc[adjustments["adjustment_type_cd"].isin(["CR", "PROMO"]), "amount"] *= -1

    n_orders = ctx.n(3500, max_value=90000)
    so_created = random_dates(ctx, n_orders, "2025-01-01", "2026-06-30").sort_values().reset_index(drop=True)
    service_orders = pd.DataFrame({
        "service_order_id": range(900001, 900001 + n_orders),
        "account_id": ctx.rng.choice(accounts["account_id"], size=n_orders),
        "order_type_cd": ctx.rng.choice(["INSTALL", "REPAIR", "MOVE", "UPGRADE", "DISCONNECT"], size=n_orders, p=[0.18, 0.42, 0.10, 0.22, 0.08]),
        "created_timestamp": so_created.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "status_cd": ctx.rng.choice(["O", "C", "X"], size=n_orders, p=[0.12, 0.83, 0.05]),
    })

    event_rows = []
    event_id = 1
    for row in service_orders.itertuples(index=False):
        base = pd.Timestamp(row.created_timestamp)
        events = [("CRT", base), ("ASN", base + pd.Timedelta(hours=int(ctx.rng.integers(1, 24))))]
        if row.status_cd == "C":
            events.append(("CMP", base + pd.Timedelta(hours=int(ctx.rng.integers(8, 240)))))
        elif row.status_cd == "X":
            events.append(("CAN", base + pd.Timedelta(hours=int(ctx.rng.integers(1, 48)))))
        for code, ts in events:
            event_rows.append({
                "service_event_id": event_id,
                "service_order_id": int(row.service_order_id),
                "event_cd": code,
                "event_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
            })
            event_id += 1
    service_order_events = pd.DataFrame(event_rows)

    n_devices = ctx.n(3000, max_value=80000)
    devices = pd.DataFrame({
        "device_id": range(1100001, 1100001 + n_devices),
        "account_id": ctx.rng.choice(accounts["account_id"], size=n_devices),
        "device_type_cd": ctx.rng.choice(["ONT", "RTR", "SW", "AP"], size=n_devices, p=[0.45, 0.38, 0.10, 0.07]),
        "install_date": random_dates(ctx, n_devices, "2018-01-01", "2026-05-31").dt.strftime("%Y-%m-%d"),
    })

    n_status = ctx.n(6000, max_value=200000)
    status_ts = random_dates(ctx, n_status, "2026-01-01", "2026-06-30").sort_values().reset_index(drop=True)
    device_status_history = pd.DataFrame({
        "status_event_id": range(1, n_status + 1),
        "device_id": ctx.rng.choice(devices["device_id"], size=n_status),
        "status_timestamp": status_ts.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "status_cd": ctx.rng.choice(["UP", "DOWN", "DEG"], size=n_status, p=[0.78, 0.16, 0.06]),
    })

    n_outages = ctx.n(300, max_value=7000)
    outage_start = random_dates(ctx, n_outages, "2025-01-01", "2026-06-30").sort_values().reset_index(drop=True)
    outage_hours = ctx.rng.uniform(0.25, 18, size=n_outages)
    outages = pd.DataFrame({
        "outage_id": range(1, n_outages + 1),
        "start_timestamp": outage_start.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "restore_timestamp": (outage_start + pd.to_timedelta(outage_hours, unit="h")).dt.strftime("%Y-%m-%d %H:%M:%S"),
        "cause_cd": ctx.rng.choice(["EQ", "WX", "FIB", "PWR", "UNK"], size=n_outages, p=[0.24, 0.20, 0.28, 0.16, 0.12]),
        "customers_affected": ctx.rng.integers(1, 1800, size=n_outages),
    })

    # Monthly balance snapshots; summing them across dates is intentionally wrong.
    snapshot_rows = []
    snap_id = 1
    snapshot_dates = pd.date_range("2025-01-31", "2026-06-30", freq="ME")
    for snap_date in snapshot_dates:
        sample_accounts = accounts.sample(frac=0.78, random_state=seed + snap_id)
        balances = np.maximum(0, ctx.rng.gamma(shape=2.2, scale=42, size=len(sample_accounts)))
        for account_id, bal in zip(sample_accounts["account_id"], balances):
            snapshot_rows.append({
                "snapshot_id": snap_id,
                "snapshot_date": snap_date.strftime("%Y-%m-%d"),
                "account_id": int(account_id),
                "balance": round(float(bal), 2),
                "status_cd": str(ctx.rng.choice(["CURRENT", "30", "60", "90+"], p=[0.79, 0.12, 0.06, 0.03])),
            })
            snap_id += 1
    account_balance_snapshots = pd.DataFrame(snapshot_rows)

    # Duplicate imported members with new IDs but matching email/phone.
    duplicate_member_n = max(1, int(n_members * 0.008))
    dup_members = members.sample(n=duplicate_member_n, random_state=seed + 5).copy()
    dup_members["member_id"] = range(int(members["member_id"].max()) + 1, int(members["member_id"].max()) + 1 + duplicate_member_n)
    dup_members["crm_status_cd"] = "A"
    members = pd.concat([members, dup_members], ignore_index=True)

    # Missing end dates for a subset of CLOSED accounts.
    closed_idx = accounts.index[accounts["billing_status_cd"].eq("CLOSED")]
    missing_end_idx = ctx.rng.choice(closed_idx, size=max(1, int(len(closed_idx) * 0.05)), replace=False)
    accounts.loc[missing_end_idx, "end_date"] = None

    tables = {
        "members": members,
        "addresses": addresses,
        "accounts": accounts,
        "plan_history": plan_history,
        "bills": bills,
        "payments": payments,
        "adjustments": adjustments,
        "service_orders": service_orders,
        "service_order_events": service_order_events,
        "devices": devices,
        "device_status_history": device_status_history,
        "outages": outages,
        "account_balance_snapshots": account_balance_snapshots,
    }

    manifest = {
        "teaching_goal": "Enterprise capstone: ambiguous definitions, SCD history, snapshots, late-arriving data, duplicate imports, operational codes, multiple business systems, and incomplete documentation.",
        "known_quality_defects": [
            "duplicate_member_entities", "duplicate_bill_imports", "closed_accounts_missing_end_date", "late_arriving_payments"
        ],
        "ground_truth": {
            "duplicate_member_entities": int(duplicate_member_n),
            "duplicate_bill_imports": int(dup_bill_n),
            "closed_accounts_missing_end_date": int(len(missing_end_idx)),
            "late_arriving_payments": int(len(late_load_idx)),
        },
        "business_definition_conflicts": {
            "active_member_finance": "Member with at least one account whose billing_status_cd = ACTIVE",
            "active_member_marketing": "Member with a bill in the prior 12 months",
            "active_member_operations": "Member with at least one installed network device tied to an account",
        },
        "code_mappings_instructor_only": {
            "members.crm_status_cd": {"A": "Active", "I": "Inactive", "P": "Prospect"},
            "service_orders.status_cd": {"O": "Open", "C": "Complete", "X": "Cancelled"},
            "service_order_events.event_cd": {"CRT": "Created", "ASN": "Assigned", "CMP": "Completed", "CAN": "Cancelled"},
        },
        "snapshot_warning": "account_balance_snapshots is point-in-time data; balances must not be summed across snapshot dates to represent a period total.",
    }
    return tables, manifest


def write_native_sources(stage_dir: Path, tables: dict[str, pd.DataFrame]) -> None:
    native = ensure_dir(stage_dir / "native_sources")
    db_dir = ensure_dir(native / "database")
    csv_dir = ensure_dir(native / "csv")
    json_dir = ensure_dir(native / "api_json")

    crm_db = db_dir / "crm.sqlite"
    if crm_db.exists(): crm_db.unlink()
    with sqlite3.connect(crm_db) as conn:
        for name in ["members", "addresses"]:
            tables[name].to_sql(name, conn, if_exists="replace", index=False)

    network_db = db_dir / "network.sqlite"
    if network_db.exists(): network_db.unlink()
    with sqlite3.connect(network_db) as conn:
        for name in ["devices", "device_status_history", "outages"]:
            tables[name].to_sql(name, conn, if_exists="replace", index=False)

    for name in ["accounts", "plan_history", "bills", "payments", "adjustments", "account_balance_snapshots"]:
        tables[name].to_csv(csv_dir / f"{name}.csv", index=False)

    service_payload = {
        "service_orders": json.loads(tables["service_orders"].to_json(orient="records")),
        "service_order_events": json.loads(tables["service_order_events"].to_json(orient="records")),
    }
    (json_dir / "operations_api_payload.json").write_text(json.dumps(service_payload, separators=(",", ":")), encoding="utf-8")


def generate(root: Path, scale: str = "small", seed: int = 707) -> Path:
    tables, manifest = build_tables(scale, seed)
    stage_dir = export_dataset(
        root, STAGE, "Coastal Communications Cooperative", "Stage 7 — Advanced Enterprise Capstone",
        tables,
        primary_keys={
            "addresses": ["address_id"], "accounts": ["account_id"], "plan_history": ["plan_history_id"],
            "bills": ["bill_id"], "payments": ["payment_id"], "adjustments": ["adjustment_id"],
            "service_orders": ["service_order_id"], "service_order_events": ["service_event_id"],
            "devices": ["device_id"], "device_status_history": ["status_event_id"], "outages": ["outage_id"],
            "account_balance_snapshots": ["snapshot_id"],
        },
        manifest=manifest,
        notes="A fictional telecommunications cooperative used as the final academic simulation before the real electric-cooperative internship. Some documentation is intentionally incomplete on the student side.",
    )
    write_native_sources(stage_dir, tables)
    return stage_dir
