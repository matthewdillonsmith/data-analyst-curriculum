from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from .common import GeneratorContext, money, random_dates, choose_state
from .export_utils import export_dataset

STAGE = "04_carolina_home_services_operational"


def build_tables(scale: str = "small", seed: int = 404) -> tuple[dict[str, pd.DataFrame], dict]:
    ctx = GeneratorContext(seed, scale)

    n_customers = ctx.n(1500, max_value=30000)
    customers = pd.DataFrame({
        "customer_id": range(200001, 200001 + n_customers),
        "customer_name": [ctx.fake.name() for _ in range(n_customers)],
        "phone": [ctx.fake.numerify("###-###-####") for _ in range(n_customers)],
        "email": [ctx.fake.unique.email() for _ in range(n_customers)],
        "state": choose_state(ctx, n_customers),
        "customer_since": random_dates(ctx, n_customers, "2018-01-01", "2025-12-31").dt.strftime("%Y-%m-%d"),
    })

    n_locations = ctx.n(1800, max_value=35000)
    service_locations = pd.DataFrame({
        "service_location_id": range(300001, 300001 + n_locations),
        "customer_id": ctx.rng.choice(customers["customer_id"], size=n_locations),
        "street": [ctx.fake.street_address() for _ in range(n_locations)],
        "city": [ctx.fake.city() for _ in range(n_locations)],
        "state": choose_state(ctx, n_locations),
        "zipcode": [ctx.fake.postcode()[:5] for _ in range(n_locations)],
    })

    n_techs = 80
    technicians = pd.DataFrame({
        "technician_id": range(1, n_techs + 1),
        "technician_name": [ctx.fake.name() for _ in range(n_techs)],
        "trade": ctx.rng.choice(["HVAC", "Electrical", "Plumbing"], size=n_techs),
        "hire_date": random_dates(ctx, n_techs, "2017-01-01", "2025-12-31").dt.strftime("%Y-%m-%d"),
        "active_flag": ctx.rng.choice([1, 0], size=n_techs, p=[0.93, 0.07]),
    })

    service_type_names = [
        "HVAC Repair", "HVAC Install", "HVAC Preventive Maintenance", "Electrical Repair",
        "Panel Upgrade", "Generator Service", "Plumbing Repair", "Water Heater",
        "Drain Service", "Inspection", "Emergency Call", "Warranty Follow-up",
    ]
    service_types = pd.DataFrame({
        "service_type_id": range(1, len(service_type_names) + 1),
        "service_type_name": service_type_names,
        "target_hours": [8, 72, 168, 8, 120, 72, 8, 48, 8, 96, 4, 72],
    })

    n_work_orders = ctx.n(4000, max_value=120000)
    created = random_dates(ctx, n_work_orders, "2025-01-01", "2026-06-30").sort_values().reset_index(drop=True)
    status = ctx.rng.choice(["COMPLETED", "OPEN", "CANCELLED"], size=n_work_orders, p=[0.83, 0.12, 0.05])
    priority = ctx.rng.choice(["Routine", "Priority", "Emergency"], size=n_work_orders, p=[0.73, 0.21, 0.06])
    work_orders = pd.DataFrame({
        "work_order_id": range(400001, 400001 + n_work_orders),
        "service_location_id": ctx.rng.choice(service_locations["service_location_id"], size=n_work_orders),
        "service_type_id": ctx.rng.integers(1, len(service_types) + 1, size=n_work_orders),
        "created_timestamp": created.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "status": status,
        "priority": priority,
        "reported_channel": ctx.rng.choice(["Phone", "Web", "Mobile", "Technician"], size=n_work_orders, p=[0.45, 0.27, 0.18, 0.10]),
    })

    assignments = pd.DataFrame({
        "assignment_id": range(1, n_work_orders + 1),
        "work_order_id": work_orders["work_order_id"],
        "technician_id": ctx.rng.integers(1, n_techs + 1, size=n_work_orders),
        "assigned_timestamp": (pd.to_datetime(work_orders["created_timestamp"]) + pd.to_timedelta(ctx.rng.integers(5, 360, size=n_work_orders), unit="m")).dt.strftime("%Y-%m-%d %H:%M:%S"),
    })

    event_rows = []
    event_id = 1
    missing_completion = 0
    duplicate_events = 0
    out_of_sequence = 0
    reopened = 0
    complete_ids = set(work_orders.loc[work_orders["status"] == "COMPLETED", "work_order_id"].tolist())
    missing_completion_ids = set(ctx.rng.choice(list(complete_ids), size=max(1, int(len(complete_ids) * 0.015)), replace=False).tolist())
    reopened_ids = set(ctx.rng.choice(list(complete_ids - missing_completion_ids), size=max(1, int(len(complete_ids) * 0.012)), replace=False).tolist())
    out_seq_ids = set(ctx.rng.choice(list(complete_ids - missing_completion_ids - reopened_ids), size=max(1, int(len(complete_ids) * 0.01)), replace=False).tolist())

    created_lookup = work_orders.set_index("work_order_id")["created_timestamp"].to_dict()
    status_lookup = work_orders.set_index("work_order_id")["status"].to_dict()
    for wo in work_orders["work_order_id"]:
        base = pd.Timestamp(created_lookup[int(wo)])
        assigned_ts = base + pd.Timedelta(minutes=int(ctx.rng.integers(5, 240)))
        enroute_ts = assigned_ts + pd.Timedelta(minutes=int(ctx.rng.integers(15, 480)))
        arrived_ts = enroute_ts + pd.Timedelta(minutes=int(ctx.rng.integers(10, 180)))
        complete_ts = arrived_ts + pd.Timedelta(minutes=int(ctx.rng.integers(30, 600)))

        events = [("CREATED", base), ("ASSIGNED", assigned_ts), ("ENROUTE", enroute_ts), ("ARRIVED", arrived_ts)]
        if wo in out_seq_ids:
            # Deliberate sequence defect: ENROUTE logged after ARRIVED.
            events[2] = ("ENROUTE", arrived_ts + pd.Timedelta(minutes=20))
            out_of_sequence += 1
        if status_lookup[int(wo)] == "COMPLETED" and wo not in missing_completion_ids:
            events.append(("COMPLETED", complete_ts))
            if wo in reopened_ids:
                events.append(("REOPENED", complete_ts + pd.Timedelta(days=1)))
                events.append(("ASSIGNED", complete_ts + pd.Timedelta(days=1, hours=1)))
                events.append(("COMPLETED", complete_ts + pd.Timedelta(days=2, hours=2)))
                reopened += 1
        elif status_lookup[int(wo)] == "COMPLETED":
            missing_completion += 1
        elif status_lookup[int(wo)] == "CANCELLED":
            events.append(("CANCELLED", assigned_ts + pd.Timedelta(hours=1)))

        for event_type, event_ts in events:
            event_rows.append({
                "event_id": event_id,
                "work_order_id": int(wo),
                "event_type": event_type,
                "event_timestamp": event_ts.strftime("%Y-%m-%d %H:%M:%S"),
                "source_system": ctx.rng.choice(["Dispatch", "Mobile", "CRM"], p=[0.5, 0.4, 0.1]),
            })
            event_id += 1

    work_order_events = pd.DataFrame(event_rows)
    dup_n = max(1, int(len(work_order_events) * 0.004))
    dup_sample = work_order_events.sample(n=dup_n, random_state=seed).copy()
    dup_sample["event_id"] = range(event_id, event_id + dup_n)
    work_order_events = pd.concat([work_order_events, dup_sample], ignore_index=True)
    duplicate_events = dup_n

    appointments = pd.DataFrame({
        "appointment_id": range(1, n_work_orders + 1),
        "work_order_id": work_orders["work_order_id"],
        "scheduled_start": (pd.to_datetime(work_orders["created_timestamp"]) + pd.to_timedelta(ctx.rng.integers(2, 144, size=n_work_orders), unit="h")).dt.strftime("%Y-%m-%d %H:%M:%S"),
        "appointment_status": np.where(work_orders["status"].eq("CANCELLED"), "Cancelled", "Scheduled"),
    })

    n_parts = 200
    parts = pd.DataFrame({
        "part_id": range(1, n_parts + 1),
        "part_name": [f"Service Part {i:04d}" for i in range(1, n_parts + 1)],
        "unit_cost": money(ctx.rng.uniform(1, 350, size=n_parts)),
    })
    part_rows = []
    line_id = 1
    for wo in work_orders["work_order_id"]:
        for pid in ctx.rng.choice(parts["part_id"], size=int(ctx.rng.integers(0, 4)), replace=False):
            part_rows.append({
                "work_order_part_id": line_id,
                "work_order_id": int(wo),
                "part_id": int(pid),
                "quantity": int(ctx.rng.integers(1, 4)),
            })
            line_id += 1
    work_order_parts = pd.DataFrame(part_rows, columns=["work_order_part_id", "work_order_id", "part_id", "quantity"])

    completed = work_orders[work_orders["status"] == "COMPLETED"].copy().reset_index(drop=True)
    n_inv = len(completed)
    invoices = pd.DataFrame({
        "invoice_id": range(600001, 600001 + n_inv),
        "work_order_id": completed["work_order_id"],
        "invoice_date": (pd.to_datetime(completed["created_timestamp"]) + pd.to_timedelta(ctx.rng.integers(1, 15, size=n_inv), unit="D")).dt.strftime("%Y-%m-%d"),
        "labor_amount": money(ctx.rng.uniform(75, 850, size=n_inv)),
        "parts_amount": money(ctx.rng.uniform(0, 1200, size=n_inv)),
    })
    invoices["invoice_total"] = (invoices["labor_amount"] + invoices["parts_amount"]).round(2)

    paid_mask = ctx.rng.random(n_inv) < 0.9
    paid_invoices = invoices.loc[paid_mask].reset_index(drop=True)
    payments = pd.DataFrame({
        "payment_id": range(800001, 800001 + len(paid_invoices)),
        "invoice_id": paid_invoices["invoice_id"],
        "payment_date": (pd.to_datetime(paid_invoices["invoice_date"]) + pd.to_timedelta(ctx.rng.integers(0, 45, size=len(paid_invoices)), unit="D")).dt.strftime("%Y-%m-%d"),
        "payment_amount": paid_invoices["invoice_total"],
    })

    tables = {
        "customers": customers,
        "service_locations": service_locations,
        "technicians": technicians,
        "service_types": service_types,
        "work_orders": work_orders,
        "technician_assignments": assignments,
        "work_order_events": work_order_events,
        "appointments": appointments,
        "parts": parts,
        "work_order_parts": work_order_parts,
        "invoices": invoices,
        "payments": payments,
    }
    manifest = {
        "teaching_goal": "Operational event data, workflow reconstruction, cycle-time analysis, grain, and join multiplication.",
        "known_quality_defects": [
            "missing_completion_events", "duplicate_work_order_events", "out_of_sequence_events", "reopened_work_orders"
        ],
        "ground_truth": {
            "missing_completion_events": int(missing_completion),
            "duplicate_work_order_events": int(duplicate_events),
            "out_of_sequence_events": int(out_of_sequence),
            "reopened_work_orders": int(reopened),
        },
        "important_teaching_trap": "Joining work_order_events and work_order_parts directly at detail grain multiplies rows.",
    }
    return tables, manifest


def generate(root: Path, scale: str = "small", seed: int = 404) -> Path:
    tables, manifest = build_tables(scale, seed)
    return export_dataset(
        root, STAGE, "Carolina Home Services", "Stage 4 — Intermediate / Messy Operational Events",
        tables,
        primary_keys={
            "customers": ["customer_id"], "service_locations": ["service_location_id"], "technicians": ["technician_id"],
            "service_types": ["service_type_id"], "work_orders": ["work_order_id"], "technician_assignments": ["assignment_id"],
            "work_order_events": ["event_id"], "appointments": ["appointment_id"], "parts": ["part_id"],
            "work_order_parts": ["work_order_part_id"], "invoices": ["invoice_id"], "payments": ["payment_id"],
        },
        foreign_keys={
            "service_locations": [(["customer_id"], "customers", ["customer_id"])],
            "work_orders": [(["service_location_id"], "service_locations", ["service_location_id"]), (["service_type_id"], "service_types", ["service_type_id"])],
            "technician_assignments": [(["work_order_id"], "work_orders", ["work_order_id"]), (["technician_id"], "technicians", ["technician_id"])],
            "work_order_events": [(["work_order_id"], "work_orders", ["work_order_id"])],
            "appointments": [(["work_order_id"], "work_orders", ["work_order_id"])],
            "work_order_parts": [(["work_order_id"], "work_orders", ["work_order_id"]), (["part_id"], "parts", ["part_id"])],
            "invoices": [(["work_order_id"], "work_orders", ["work_order_id"])],
            "payments": [(["invoice_id"], "invoices", ["invoice_id"])],
        },
        manifest=manifest,
        notes="A service-company operational dataset with event histories, reopened jobs, missing completion events, duplicate events, and many-to-many join risks.",
    )
