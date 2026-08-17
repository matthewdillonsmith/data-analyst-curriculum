from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

from .common import GeneratorContext, money, random_dates, choose_state
from .export_utils import export_dataset

CLEAN_STAGE = "02_blue_ridge_outfitters_clean"
MESSY_STAGE = "03_blue_ridge_outfitters_basic_quality"


def build_clean_tables(scale: str = "small", seed: int = 202) -> tuple[dict[str, pd.DataFrame], dict]:
    ctx = GeneratorContext(seed, scale)
    n_categories = 12
    categories = pd.DataFrame({
        "category_id": range(1, n_categories + 1),
        "category_name": [
            "Camping", "Hiking", "Climbing", "Cycling", "Fishing", "Paddling",
            "Footwear", "Apparel", "Hydration", "Navigation", "Winter", "Accessories"
        ],
    })

    n_products = ctx.n(150, max_value=3000)
    products = pd.DataFrame({
        "product_id": range(1, n_products + 1),
        "sku": [f"BRO-{i:06d}" for i in range(1, n_products + 1)],
        "product_name": [f"Outdoor Product {i:04d}" for i in range(1, n_products + 1)],
        "category_id": ctx.rng.integers(1, n_categories + 1, size=n_products),
        "unit_cost": money(ctx.rng.uniform(3, 180, size=n_products)),
        "list_price": money(ctx.rng.uniform(8, 420, size=n_products)),
        "active_flag": 1,
    })
    products["list_price"] = np.maximum(products["list_price"], products["unit_cost"] * 1.25).round(2)

    n_warehouses = 5
    warehouses = pd.DataFrame({
        "warehouse_id": range(1, n_warehouses + 1),
        "warehouse_name": ["Asheville", "Charlotte", "Raleigh", "Wilmington", "Greensboro"],
        "state": ["NC"] * n_warehouses,
    })

    n_customers = ctx.n(1000, max_value=40000)
    states = choose_state(ctx, n_customers)
    customers = pd.DataFrame({
        "customer_id": range(100001, 100001 + n_customers),
        "first_name": [ctx.fake.first_name() for _ in range(n_customers)],
        "last_name": [ctx.fake.last_name() for _ in range(n_customers)],
        "email": [ctx.fake.unique.email() for _ in range(n_customers)],
        "phone": [ctx.fake.numerify("###-###-####") for _ in range(n_customers)],
        "city": [ctx.fake.city() for _ in range(n_customers)],
        "state": states,
        "zipcode": [ctx.fake.postcode()[:5] for _ in range(n_customers)],
        "created_date": random_dates(ctx, n_customers, "2021-01-01", "2025-12-31").dt.strftime("%Y-%m-%d"),
    })

    n_orders = ctx.n(4000, max_value=180000)
    order_ts = random_dates(ctx, n_orders, "2025-01-01", "2026-06-30").sort_values().reset_index(drop=True)
    statuses = ctx.rng.choice(["Completed", "Shipped", "Cancelled", "Processing"], size=n_orders, p=[0.75, 0.13, 0.05, 0.07])
    orders = pd.DataFrame({
        "order_id": range(500001, 500001 + n_orders),
        "customer_id": ctx.rng.choice(customers["customer_id"], size=n_orders),
        "order_timestamp": order_ts.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "order_status": statuses,
        "sales_channel": ctx.rng.choice(["Web", "Mobile", "Phone"], size=n_orders, p=[0.68, 0.25, 0.07]),
    })

    item_rows = []
    item_id = 1
    price_lookup = products.set_index("product_id")["list_price"].to_dict()
    for order_id in orders["order_id"]:
        k = int(ctx.rng.integers(1, 5))
        pids = ctx.rng.choice(products["product_id"], size=k, replace=False)
        for pid in pids:
            list_price = float(price_lookup[int(pid)])
            discount = float(ctx.rng.choice([0, 0.05, 0.10, 0.15, 0.20], p=[0.62, 0.12, 0.12, 0.09, 0.05]))
            item_rows.append({
                "order_item_id": item_id,
                "order_id": int(order_id),
                "product_id": int(pid),
                "quantity": int(ctx.rng.integers(1, 5)),
                "unit_price": round(list_price * (1 - discount), 2),
                "discount_pct": discount,
            })
            item_id += 1
    order_items = pd.DataFrame(item_rows)

    totals = order_items.assign(line_total=order_items["quantity"] * order_items["unit_price"]).groupby("order_id", as_index=False)["line_total"].sum()
    payment_method = ctx.rng.choice(["Visa", "Mastercard", "Amex", "PayPal"], size=n_orders, p=[0.42, 0.31, 0.08, 0.19])
    payments = orders[["order_id", "order_timestamp", "order_status"]].merge(totals, on="order_id", how="left")
    payments["payment_id"] = range(900001, 900001 + n_orders)
    payments["payment_method"] = payment_method
    payments["payment_amount"] = payments["line_total"].round(2)
    payments["payment_status"] = np.where(payments["order_status"].eq("Cancelled"), "Refunded", "Paid")
    payments["payment_timestamp"] = pd.to_datetime(payments["order_timestamp"]) + pd.to_timedelta(ctx.rng.integers(1, 120, size=n_orders), unit="m")
    payments["payment_timestamp"] = payments["payment_timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    payments = payments[["payment_id", "order_id", "payment_timestamp", "payment_method", "payment_amount", "payment_status"]]

    ship_mask = ~orders["order_status"].isin(["Cancelled", "Processing"])
    ship_orders = orders.loc[ship_mask, ["order_id", "order_timestamp"]].reset_index(drop=True)
    n_ship = len(ship_orders)
    ship_start = pd.to_datetime(ship_orders["order_timestamp"]) + pd.to_timedelta(ctx.rng.integers(4, 72, size=n_ship), unit="h")
    ship_end = ship_start + pd.to_timedelta(ctx.rng.integers(12, 120, size=n_ship), unit="h")
    shipments = pd.DataFrame({
        "shipment_id": range(700001, 700001 + n_ship),
        "order_id": ship_orders["order_id"],
        "warehouse_id": ctx.rng.integers(1, n_warehouses + 1, size=n_ship),
        "carrier": ctx.rng.choice(["UPS", "FedEx", "USPS"], size=n_ship),
        "shipped_timestamp": ship_start.dt.strftime("%Y-%m-%d %H:%M:%S"),
        "delivered_timestamp": ship_end.dt.strftime("%Y-%m-%d %H:%M:%S"),
    })

    tables = {
        "customers": customers,
        "categories": categories,
        "products": products,
        "warehouses": warehouses,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
        "shipments": shipments,
    }
    return tables, {
        "teaching_goal": "Modern clean business data for Excel, SQL, statistics, and first Power BI work.",
        "known_quality_defects": [],
        "ground_truth": {"intentional_defects": 0},
    }


def inject_basic_quality_defects(tables: dict[str, pd.DataFrame], seed: int = 303) -> tuple[dict[str, pd.DataFrame], dict]:
    ctx = GeneratorContext(seed, "small")
    out = {k: v.copy() for k, v in tables.items()}
    defects: dict[str, int] = {}

    customers = out["customers"].copy()
    n = len(customers)

    # Missing contact data.
    email_idx = ctx.rng.choice(customers.index, size=max(1, int(n * 0.03)), replace=False)
    customers.loc[email_idx, "email"] = None
    phone_pool = customers.index.difference(email_idx)
    phone_idx = ctx.rng.choice(phone_pool, size=max(1, int(n * 0.06)), replace=False)
    customers.loc[phone_idx, "phone"] = None
    defects["missing_email"] = int(customers["email"].isna().sum())
    defects["missing_phone"] = int(customers["phone"].isna().sum())

    # Inconsistent state labels.
    state_idx = ctx.rng.choice(customers.index, size=max(1, int(n * 0.025)), replace=False)
    variants = ["North Carolina", "N.C.", "north carolina", "S.C.", "South Carolina", "virginia"]
    customers.loc[state_idx, "state"] = ctx.rng.choice(variants, size=len(state_idx))
    defects["inconsistent_state_values"] = len(state_idx)

    # Duplicate entities with new customer IDs but same identity attributes.
    dup_n = max(1, int(n * 0.012))
    source_idx = ctx.rng.choice(customers.index, size=dup_n, replace=False)
    duplicates = customers.loc[source_idx].copy()
    next_id = int(customers["customer_id"].max()) + 1
    duplicates["customer_id"] = range(next_id, next_id + dup_n)
    customers = pd.concat([customers, duplicates], ignore_index=True)
    defects["duplicate_customer_entities"] = dup_n

    # Mixed date formats in created_date.
    date_idx = ctx.rng.choice(customers.index, size=max(1, int(len(customers) * 0.02)), replace=False)
    for j, idx in enumerate(date_idx):
        try:
            dt = pd.Timestamp(customers.at[idx, "created_date"])
        except Exception:
            continue
        customers.at[idx, "created_date"] = dt.strftime("%m/%d/%Y") if j % 2 == 0 else dt.strftime("%m/%d/%y")
    defects["mixed_customer_date_formats"] = len(date_idx)
    out["customers"] = customers

    # Inconsistent order status text.
    orders = out["orders"].copy()
    status_idx = ctx.rng.choice(orders.index, size=max(1, int(len(orders) * 0.025)), replace=False)
    replacements = ["complete", "COMP", "Completed ", "shipped", "PROCESSING", "cancelled "]
    orders.loc[status_idx, "order_status"] = ctx.rng.choice(replacements, size=len(status_idx))
    defects["inconsistent_order_status"] = len(status_idx)

    # Orphan orders: customer IDs that do not exist.
    orphan_idx = ctx.rng.choice(orders.index, size=max(1, int(len(orders) * 0.003)), replace=False)
    orders.loc[orphan_idx, "customer_id"] = 99999999
    defects["orphan_orders"] = len(orphan_idx)
    out["orders"] = orders

    # Dirty unit_price makes the column textual in raw exports.
    items = out["order_items"].copy()
    items["unit_price"] = items["unit_price"].astype(object)
    dirty_idx = ctx.rng.choice(items.index, size=max(1, int(len(items) * 0.008)), replace=False)
    dirty_values = []
    for j, idx in enumerate(dirty_idx):
        value = float(items.at[idx, "unit_price"])
        if j % 4 == 0:
            dirty_values.append(f"${value:,.2f}")
        elif j % 4 == 1:
            dirty_values.append("N/A")
        elif j % 4 == 2:
            dirty_values.append(f"{value:.2f} ")
        else:
            dirty_values.append(f"{value:.2f}".replace(".", ","))
    items.loc[dirty_idx, "unit_price"] = dirty_values
    defects["dirty_unit_price_values"] = len(dirty_idx)
    out["order_items"] = items

    manifest = {
        "teaching_goal": "Students must profile, clean, normalize, and validate before analyzing.",
        "known_quality_defects": list(defects.keys()),
        "ground_truth": defects,
    }
    return out, manifest


def generate_clean(root: Path, scale: str = "small", seed: int = 202) -> Path:
    tables, manifest = build_clean_tables(scale, seed)
    return export_dataset(
        root, CLEAN_STAGE, "Blue Ridge Outfitters — Clean", "Stage 2 — Beginner / Clean Modern Business",
        tables,
        primary_keys={
            "customers": ["customer_id"], "categories": ["category_id"], "products": ["product_id"],
            "warehouses": ["warehouse_id"], "orders": ["order_id"], "order_items": ["order_item_id"],
            "payments": ["payment_id"], "shipments": ["shipment_id"],
        },
        foreign_keys={
            "products": [(["category_id"], "categories", ["category_id"])],
            "orders": [(["customer_id"], "customers", ["customer_id"])],
            "order_items": [(["order_id"], "orders", ["order_id"]), (["product_id"], "products", ["product_id"])],
            "payments": [(["order_id"], "orders", ["order_id"])],
            "shipments": [(["order_id"], "orders", ["order_id"]), (["warehouse_id"], "warehouses", ["warehouse_id"])],
        },
        manifest=manifest,
        notes="A fully clean e-commerce dataset used to move beyond Northwind while keeping the business model understandable.",
    )


def generate_messy(root: Path, scale: str = "small", seed: int = 202) -> Path:
    clean, _ = build_clean_tables(scale, seed)
    tables, manifest = inject_basic_quality_defects(clean, seed + 101)
    # Foreign keys are intentionally omitted from the generated DDL because the dataset contains deliberate orphans.
    return export_dataset(
        root, MESSY_STAGE, "Blue Ridge Outfitters — Raw", "Stage 3 — Early Intermediate / Basic Data Quality",
        tables,
        primary_keys={
            "categories": ["category_id"], "products": ["product_id"], "warehouses": ["warehouse_id"],
            "orders": ["order_id"], "order_items": ["order_item_id"], "payments": ["payment_id"], "shipments": ["shipment_id"],
        },
        manifest=manifest,
        notes="The same business students already know, but now with missing values, duplicate entities, inconsistent categories, mixed date formats, dirty numerics, and orphan records.",
    )
