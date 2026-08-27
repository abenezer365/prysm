"""Persons generator — 100,000 Ethiopian-realistic person records."""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import polars as pl

from src.utils.ethiopian_data import (
    determine_employment_status,
    get_city_weights,
    get_income_params,
    get_occupation_weights,
    get_region,
    load_names,
)
from src.utils.distributions import lognormal_income
from src.utils.hashing import address_hash as make_address_hash, phone_hash as make_phone_hash


def generate_persons(config: dict) -> pl.DataFrame:
    seed: int = config.get("seed", 42)
    count: int = config.get("dataset", {}).get("persons", 100_000)
    reference_date: str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    ref_dt = datetime.fromisoformat(reference_date)
    ref_ts = ref_dt.timestamp()
    start_ts = datetime.fromisoformat(config.get("temporal", {}).get("start_date", "2022-01-01")).timestamp()

    dq = config.get("data_quality", {}).get("column_missing_rates", {})
    phone_missing_rate = dq.get("phone_hash", 0.05)
    address_missing_rate = dq.get("address_hash", 0.08)
    emp_missing_rate = dq.get("employment_status", 0.03)

    rng = np.random.default_rng(seed)

    boy_names, girl_names = load_names(config)
    boy_names = list(boy_names)
    girl_names = list(girl_names)

    occs, occ_weights = get_occupation_weights(config)
    cities, city_weights = get_city_weights(config)

    # Pre-generate arrays for speed
    genders = np.where(rng.random(count) < 0.48, "M", "F")
    boy_idx = rng.integers(0, len(boy_names), size=count)
    girl_idx = rng.integers(0, len(girl_names), size=count)
    surname_idx = rng.integers(0, len(boy_names), size=count)
    occ_choices = rng.choice(len(occs), size=count, p=occ_weights)
    city_choices = rng.choice(len(cities), size=count, p=city_weights)
    ages = rng.integers(18, 65, size=count)
    dob_offsets = rng.integers(0, 365, size=count)
    created_offsets = rng.integers(0, 365 * 5, size=count)
    nationality_rolls = rng.random(count)
    phone_mask = rng.random(count) < phone_missing_rate
    address_mask = rng.random(count) < address_missing_rate
    emp_mask = rng.random(count) < emp_missing_rate

    persons: list[dict] = []
    for i in range(count):
        gender = genders[i]
        first = boy_names[boy_idx[i]] if gender == "M" else girl_names[girl_idx[i]]
        surname = boy_names[surname_idx[i]]
        occ = occs[occ_choices[i]]
        city = cities[city_choices[i]]
        region = get_region(city, config)
        min_inc, max_inc, curr = get_income_params(occ, config)
        income = lognormal_income(min_inc, max_inc, rng)
        emp_status = determine_employment_status(occ, config)

        dob = ref_dt - timedelta(days=int(ages[i]) * 365 + int(dob_offsets[i]))
        created_at = datetime.fromtimestamp(rng.uniform(start_ts, ref_ts))

        ph = None if phone_mask[i] else make_phone_hash(first, surname, city)
        ah = None if address_mask[i] else make_address_hash(first, surname, city, region)
        es = None if emp_mask[i] else emp_status

        persons.append(
            {
                "person_id": f"P{str(i + 1).zfill(6)}",
                "first_name": first,
                "last_name": surname,
                "date_of_birth": dob.date(),
                "gender": gender,
                "nationality": "Ethiopian" if nationality_rolls[i] < 0.92 else "Other",
                "occupation": occ,
                "employment_status": es,
                "declared_monthly_income": income,
                "income_currency": curr,
                "city": city,
                "region": region,
                "country": "Ethiopia",
                "phone_hash": ph,
                "address_hash": ah,
                "created_at": created_at,
            }
        )

    return pl.DataFrame(persons)
