from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import random

import numpy as np
import pandas as pd
from faker import Faker


SCALE_MULTIPLIERS = {
    "small": 1,
    "medium": 4,
    "large": 12,
}

US_STATES = [
    ("NC", "North Carolina"),
    ("SC", "South Carolina"),
    ("VA", "Virginia"),
    ("GA", "Georgia"),
    ("TN", "Tennessee"),
    ("FL", "Florida"),
]


@dataclass
class GeneratorContext:
    seed: int
    scale: str

    def __post_init__(self) -> None:
        if self.scale not in SCALE_MULTIPLIERS:
            raise ValueError(f"Unknown scale: {self.scale}")
        self.multiplier = SCALE_MULTIPLIERS[self.scale]
        self.rng = np.random.default_rng(self.seed)
        self.py_random = random.Random(self.seed)
        self.fake = Faker("en_US")
        self.fake.seed_instance(self.seed)

    def n(self, base: int, *, max_value: int | None = None) -> int:
        value = max(1, int(base * self.multiplier))
        if max_value is not None:
            value = min(value, max_value)
        return value


def random_dates(ctx: GeneratorContext, n: int, start: str, end: str) -> pd.Series:
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    seconds = int((end_ts - start_ts).total_seconds())
    offsets = ctx.rng.integers(0, max(seconds, 1), size=n)
    return pd.Series([start_ts + pd.Timedelta(seconds=int(x)) for x in offsets])


def random_date_strings(ctx: GeneratorContext, n: int, start: str, end: str) -> list[str]:
    return random_dates(ctx, n, start, end).dt.strftime("%Y-%m-%d").tolist()


def choose_state(ctx: GeneratorContext, n: int) -> list[str]:
    codes = [x[0] for x in US_STATES]
    probs = np.array([0.48, 0.18, 0.12, 0.09, 0.07, 0.06])
    return ctx.rng.choice(codes, size=n, p=probs).tolist()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def money(values: np.ndarray | list[float]) -> np.ndarray:
    return np.round(np.asarray(values, dtype=float), 2)


def iso_timestamp(ts: pd.Timestamp | datetime) -> str:
    if isinstance(ts, pd.Timestamp):
        ts = ts.to_pydatetime()
    return ts.isoformat(sep=" ", timespec="seconds")


def make_person_rows(ctx: GeneratorContext, n: int, start_id: int = 1) -> pd.DataFrame:
    rows = []
    states = choose_state(ctx, n)
    for i in range(n):
        first = ctx.fake.first_name()
        last = ctx.fake.last_name()
        rows.append(
            {
                "person_id": start_id + i,
                "first_name": first,
                "last_name": last,
                "email": f"{first}.{last}.{start_id+i}@example.edu".lower().replace("'", ""),
                "phone": ctx.fake.numerify("###-###-####"),
                "street": ctx.fake.street_address(),
                "city": ctx.fake.city(),
                "state": states[i],
                "zipcode": ctx.fake.postcode()[:5],
            }
        )
    return pd.DataFrame(rows)
