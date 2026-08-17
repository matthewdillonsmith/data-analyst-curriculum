from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

from .common import GeneratorContext
from .export_utils import export_dataset

STAGE = "06_smart_campus_timeseries"


def _build_time_index() -> pd.DatetimeIndex:
    spring = pd.date_range(
        "2026-02-25 00:00", "2026-03-18 23:45", freq="15min", tz="America/New_York"
    )
    fall = pd.date_range(
        "2026-10-20 00:00", "2026-11-10 23:45", freq="15min", tz="America/New_York"
    )
    return spring.append(fall)


def build_tables(scale: str = "small", seed: int = 606) -> tuple[dict[str, pd.DataFrame], dict]:
    ctx = GeneratorContext(seed, scale)
    n_buildings = 3 if scale == "small" else (8 if scale == "medium" else 14)
    sensors_per_building = 4 if scale == "small" else (8 if scale == "medium" else 10)

    buildings = pd.DataFrame({
        "building_id": range(1, n_buildings + 1),
        "building_name": [f"Campus Building {i:02d}" for i in range(1, n_buildings + 1)],
        "building_type": ctx.rng.choice(["Academic", "Administration", "Lab", "Residence"], size=n_buildings),
        "square_feet": ctx.rng.integers(18000, 180000, size=n_buildings),
        "commissioned_year": ctx.rng.integers(1970, 2026, size=n_buildings),
    })

    sensor_rows = []
    sensor_id = 1001
    for bid in buildings["building_id"]:
        for _ in range(sensors_per_building):
            sensor_rows.append({
                "sensor_id": sensor_id,
                "building_id": int(bid),
                "sensor_name": f"B{int(bid):02d}-S{sensor_id}",
                "sensor_type": "environment_energy",
                "installed_date": "2025-01-15",
            })
            sensor_id += 1
    sensors = pd.DataFrame(sensor_rows)

    idx = _build_time_index()
    rows = []
    reading_id = 1
    for sensor in sensors.itertuples(index=False):
        base_temp = float(ctx.rng.uniform(68, 74))
        base_kw = float(ctx.rng.uniform(12, 70))
        for ts in idx:
            hour = ts.hour + ts.minute / 60.0
            day_factor = 1.0 if ts.weekday() < 5 else 0.68
            occupancy = max(0, int(75 * day_factor * max(0, np.sin((hour - 6) / 12 * np.pi)) + ctx.rng.normal(0, 6)))
            temp = base_temp + 2.8 * np.sin((hour - 8) / 24 * 2 * np.pi) + ctx.rng.normal(0, 0.9)
            humidity = 47 + 9 * np.sin((hour + 2) / 24 * 2 * np.pi) + ctx.rng.normal(0, 4)
            kw = base_kw * (0.48 + day_factor * max(0, np.sin((hour - 5) / 14 * np.pi))) + occupancy * 0.06 + ctx.rng.normal(0, 2.5)
            rows.append({
                "reading_id": reading_id,
                "sensor_id": int(sensor.sensor_id),
                "local_timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
                "utc_timestamp": ts.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%S%z"),
                "utc_offset": ts.strftime("%z"),
                "temperature_f": round(float(temp), 2),
                "humidity_pct": round(float(humidity), 2),
                "occupancy": occupancy,
                "kw": round(float(max(0, kw)), 3),
                "hvac_status": "ON" if kw > base_kw * 0.55 else "OFF",
            })
            reading_id += 1
    readings = pd.DataFrame(rows)

    defects: dict[str, int] = {}

    # Randomly missing expected sensor intervals.
    missing_n = max(1, int(len(readings) * 0.003))
    missing_idx = ctx.rng.choice(readings.index, size=missing_n, replace=False)
    readings = readings.drop(index=missing_idx).reset_index(drop=True)
    defects["random_missing_intervals"] = missing_n

    # Duplicate exact records with new reading IDs.
    dup_n = max(1, int(len(readings) * 0.0015))
    dup = readings.sample(n=dup_n, random_state=seed).copy()
    dup["reading_id"] = range(int(readings["reading_id"].max()) + 1, int(readings["reading_id"].max()) + 1 + dup_n)
    readings = pd.concat([readings, dup], ignore_index=True)
    defects["duplicate_sensor_intervals"] = dup_n

    # Sentinel temperature values.
    sentinel_n = max(1, int(len(readings) * 0.0008))
    sentinel_idx = ctx.rng.choice(readings.index, size=sentinel_n, replace=False)
    readings.loc[sentinel_idx, "temperature_f"] = -999.0
    defects["temperature_sentinel_values"] = sentinel_n

    # Impossible humidity values.
    humidity_n = max(1, int(len(readings) * 0.0006))
    humidity_idx = ctx.rng.choice(readings.index.difference(sentinel_idx), size=humidity_n, replace=False)
    readings.loc[humidity_idx, "humidity_pct"] = ctx.rng.uniform(120, 250, size=humidity_n).round(2)
    defects["humidity_over_100_pct"] = humidity_n

    # Negative campus consumption values.
    negative_n = max(1, int(len(readings) * 0.0004))
    negative_idx = ctx.rng.choice(readings.index.difference(sentinel_idx).difference(humidity_idx), size=negative_n, replace=False)
    readings.loc[negative_idx, "kw"] = -ctx.rng.uniform(5, 250, size=negative_n).round(3)
    defects["negative_kw_values"] = negative_n

    # Extreme spikes.
    spike_n = max(1, int(len(readings) * 0.0004))
    spike_idx = ctx.rng.choice(readings.index.difference(sentinel_idx).difference(humidity_idx).difference(negative_idx), size=spike_n, replace=False)
    readings.loc[spike_idx, "kw"] = ctx.rng.uniform(3000, 10000, size=spike_n).round(3)
    defects["extreme_kw_spikes"] = spike_n

    # DST characteristics are naturally present in local_timestamp.
    duplicated_local = int(readings.duplicated(subset=["sensor_id", "local_timestamp"], keep=False).sum())
    spring_2am_rows = int(readings[readings["local_timestamp"].str.startswith("2026-03-08 02:")].shape[0])
    defects["rows_in_duplicated_local_fall_hour"] = duplicated_local
    defects["spring_forward_local_2am_rows"] = spring_2am_rows

    tables = {
        "buildings": buildings,
        "sensors": sensors,
        "sensor_readings": readings,
    }
    manifest = {
        "teaching_goal": "Time-series validation, high-volume data, missing intervals, duplicate intervals, time zones, DST, sensor anomalies, and anomaly-vs-error judgment.",
        "known_quality_defects": list(defects.keys()),
        "ground_truth": defects,
        "time_zone": "America/New_York",
        "dst_instruction": "local_timestamp intentionally becomes non-unique during fall back; utc_timestamp remains unambiguous. Spring-forward 02:00 local time is absent by design.",
    }
    return tables, manifest


def generate(root: Path, scale: str = "small", seed: int = 606) -> Path:
    tables, manifest = build_tables(scale, seed)
    return export_dataset(
        root, STAGE, "Smart Campus Energy & Sensor Data", "Stage 6 — Advanced / Time Series & IoT",
        tables,
        primary_keys={"buildings": ["building_id"], "sensors": ["sensor_id"], "sensor_readings": ["reading_id"]},
        foreign_keys={
            "sensors": [(["building_id"], "buildings", ["building_id"])],
            "sensor_readings": [(["sensor_id"], "sensors", ["sensor_id"])],
        },
        manifest=manifest,
        notes="15-minute smart-building data spanning both 2026 U.S. DST transitions, with missing intervals, duplicate records, sentinel values, impossible readings, and outliers.",
    )
