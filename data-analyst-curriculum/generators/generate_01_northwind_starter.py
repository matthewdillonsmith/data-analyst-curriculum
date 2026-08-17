from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .common import GeneratorContext, money, random_dates
from .export_utils import export_dataset


STAGE = "01_northwind_starter"


def build_tables(scale: str = "small", seed: int = 101) -> tuple[dict[str, pd.DataFrame], dict]:
    ctx = GeneratorContext(seed, scale)

    categories = pd.DataFrame(
        {
            "category_id": range(1, 9),
            "category_name": [
                "Beverages", "Condiments", "Confections", "Dairy", "Grains",
                "Meat", "Produce", "Seafood",
            ],
        }
    )

    n_products = ctx.n(40, max_value=250)
    products = pd.DataFrame(
        {
            "product_id": range(1, n_products + 1),
            "product_name": [f"Product {i:03d}" for i in range(1, n_products + 1)],
            "category_id": ctx.rng.integers(1, 9, size=n_products),
            "unit_price": money(ctx.rng.uniform(4, 120, size=n_products)),
            "discontinued": ctx.rng.choice([0, 1], size=n_products, p=[0.93, 0.07]),
        }
    )

    n_customers = ctx.n(120, max_value=1500)
    customer_rows = []
    for i in range(1, n_customers + 1):
        company = ctx.fake.company()
        customer_rows.append(
            {
                "customer_id": f"C{i:04d}",
                "company_name": company,
                "contact_name": ctx.fake.name(),
                "city": ctx.fake.city(),
                "state": ctx.rng.choice(["NC", "SC", "VA", "GA", "TN"]),
                "country": "USA",
            }
        )
    customers = pd.DataFrame(customer_rows)

    n_employees = 10
    employees = pd.DataFrame(
        {
            "employee_id": range(1, n_employees + 1),
            "employee_name": [ctx.fake.name() for _ in range(n_employees)],
            "title": ctx.rng.choice(
                ["Sales Representative", "Account Manager", "Sales Coordinator"], size=n_employees
            ),
        }
    )

    n_orders = ctx.n(500, max_value=8000)
    order_dates = random_dates(ctx, n_orders, "2025-01-01", "2026-06-30").sort_values().reset_index(drop=True)
    orders = pd.DataFrame(
        {
            "order_id": range(10001, 10001 + n_orders),
            "customer_id": ctx.rng.choice(customers["customer_id"], size=n_orders),
            "employee_id": ctx.rng.integers(1, n_employees + 1, size=n_orders),
            "order_date": order_dates.dt.strftime("%Y-%m-%d"),
            "ship_city": [ctx.fake.city() for _ in range(n_orders)],
            "ship_state": ctx.rng.choice(["NC", "SC", "VA", "GA", "TN"], size=n_orders),
        }
    )

    detail_rows = []
    detail_id = 1
    product_prices = products.set_index("product_id")["unit_price"].to_dict()
    for order_id in orders["order_id"]:
        count = int(ctx.rng.integers(1, 6))
        selected = ctx.rng.choice(products["product_id"], size=count, replace=False)
        for product_id in selected:
            detail_rows.append(
                {
                    "order_detail_id": detail_id,
                    "order_id": int(order_id),
                    "product_id": int(product_id),
                    "unit_price": float(product_prices[int(product_id)]),
                    "quantity": int(ctx.rng.integers(1, 12)),
                    "discount_pct": float(ctx.rng.choice([0.0, 0.05, 0.10, 0.15], p=[0.72, 0.12, 0.10, 0.06])),
                }
            )
            detail_id += 1
    order_details = pd.DataFrame(detail_rows)

    tables = {
        "categories": categories,
        "products": products,
        "customers": customers,
        "employees": employees,
        "orders": orders,
        "order_details": order_details,
    }
    manifest = {
        "teaching_goal": "Absolute beginner relational data. Intentionally clean.",
        "known_quality_defects": [],
        "ground_truth": {
            "intentional_duplicates": 0,
            "intentional_orphans": 0,
            "intentional_nulls": 0,
        },
    }
    return tables, manifest


def generate(root: Path, scale: str = "small", seed: int = 101) -> Path:
    tables, manifest = build_tables(scale, seed)
    return export_dataset(
        root,
        STAGE,
        "Northwind-Style Starter Dataset",
        "Stage 1 — Absolute Beginner / Clean",
        tables,
        primary_keys={
            "categories": ["category_id"],
            "products": ["product_id"],
            "customers": ["customer_id"],
            "employees": ["employee_id"],
            "orders": ["order_id"],
            "order_details": ["order_detail_id"],
        },
        foreign_keys={
            "products": [(["category_id"], "categories", ["category_id"])],
            "orders": [(["customer_id"], "customers", ["customer_id"]), (["employee_id"], "employees", ["employee_id"])],
            "order_details": [(["order_id"], "orders", ["order_id"]), (["product_id"], "products", ["product_id"])],
        },
        manifest=manifest,
        notes=(
            "A synthetic Northwind-style teaching dataset for SQL/Excel fundamentals. "
            "It is not Microsoft's original Northwind data, but uses the same beginner-friendly retail concepts. "
            "Faculty may substitute the official Northwind sample database while keeping the Stage 1 exercises."
        ),
    )
