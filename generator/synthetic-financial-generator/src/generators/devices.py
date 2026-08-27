"""Devices generator — 90,000 device records."""
from __future__ import annotations

from datetime import datetime

import numpy as np
import polars as pl

from src.utils.ethiopian_data import get_city_weights, get_region
from src.utils.hashing import device_fingerprint


def generate_devices(config: dict) -> pl.DataFrame:
    seed: int = config.get("seed", 42) + 3
    count: int = config.get("dataset", {}).get("devices", 90_000)
    ref_date: str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    start_date: str = config.get("temporal", {}).get("start_date", "2022-01-01")
    ref_ts = datetime.fromisoformat(ref_date).timestamp()
    start_ts = datetime.fromisoformat(start_date).timestamp()

    dq = config.get("data_quality", {}).get("column_missing_rates", {})
    browser_missing_rate = dq.get("browser", 0.03)

    rng = np.random.default_rng(seed)
    cities, city_weights = get_city_weights(config)
    device_types = config.get("device_types", ["Mobile", "Tablet", "Desktop", "Laptop"])
    os_map: dict = config.get("operating_systems", {
        "Mobile": ["Android", "iOS"],
        "Tablet": ["Android", "iPadOS"],
        "Desktop": ["Windows", "Ubuntu", "macOS"],
        "Laptop": ["Windows", "Ubuntu", "macOS"],
    })
    browsers = config.get("browsers", ["Chrome", "Firefox", "Safari", "Edge", "Opera"])
    # Mobile-heavy distribution
    dt_weights = [0.55, 0.10, 0.15, 0.20]

    devices: list[dict] = []
    for i in range(count):
        dt = device_types[rng.choice(len(device_types), p=dt_weights)]
        os_pool = os_map.get(dt, ["Android"])
        os = os_pool[rng.integers(0, len(os_pool))]
        browser = None if rng.random() < browser_missing_rate else browsers[rng.integers(0, len(browsers))]
        city = cities[rng.choice(len(cities), p=city_weights)]
        region = get_region(city, config)

        first_seen_ts = rng.uniform(start_ts, ref_ts)
        last_seen_ts = rng.uniform(first_seen_ts, ref_ts)

        did = f"DEV{str(i + 1).zfill(7)}"
        fp = device_fingerprint(did, os, dt)

        devices.append(
            {
                "device_id": did,
                "device_type": dt,
                "os": os,
                "browser": browser,
                "device_fingerprint": fp,
                "first_seen": datetime.fromtimestamp(first_seen_ts),
                "last_seen": datetime.fromtimestamp(last_seen_ts),
                "city": city,
                "country": "Ethiopia",
            }
        )

    return pl.DataFrame(devices)
