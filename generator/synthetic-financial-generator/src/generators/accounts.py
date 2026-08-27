"""Accounts generator — 150,000 accounts linked to persons and companies."""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import polars as pl

from src.utils.ethiopian_data import get_city_weights, get_region


def generate_accounts(
    config: dict,
    person_ids: list[str],
    company_ids: list[str],
    bank_ids: list[str],
) -> pl.DataFrame:
    seed: int = config.get("seed", 42) + 2
    count: int = config.get("dataset", {}).get("accounts", 150_000)
    ref_date: str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    start_date: str = config.get("temporal", {}).get("start_date", "2022-01-01")
    ref_dt = datetime.fromisoformat(ref_date)
    start_dt = datetime.fromisoformat(start_date)

    dq = config.get("data_quality", {}).get("column_missing_rates", {})
    closed_at_null_rate = dq.get("closed_at", 0.70)

    rng = np.random.default_rng(seed)
    cities, city_weights = get_city_weights(config)
    account_types = config.get("account_types", ["Savings", "Current", "Business", "Fixed Deposit", "Mobile Money"])
    currencies_cfg = config.get("currencies", {})
    primary_currency = currencies_cfg.get("primary", "ETB")
    foreign_currencies = currencies_cfg.get("foreign", ["USD", "EUR"])

    # ~80% owned by persons, ~20% by companies
    n_person = int(count * 0.80)
    n_company = count - n_person

    owner_ids: list[str] = []
    owner_types: list[str] = []

    person_sample = rng.choice(person_ids, size=n_person, replace=True).tolist()
    company_sample = rng.choice(company_ids, size=n_company, replace=True).tolist()
    owner_ids = person_sample + company_sample
    owner_types = ["Person"] * n_person + ["Company"] * n_company

    # Shuffle together
    perm = rng.permutation(count)
    owner_ids = [owner_ids[p] for p in perm]
    owner_types = [owner_types[p] for p in perm]

    accounts: list[dict] = []
    for i in range(count):
        city = cities[rng.choice(len(cities), p=city_weights)]
        region = get_region(city, config)
        acc_type = account_types[rng.integers(0, len(account_types))]
        bank_id = bank_ids[rng.integers(0, len(bank_ids))]

        # Foreign bank accounts use foreign currency more often
        if "Foreign" in bank_id or rng.random() < 0.10:
            currency = rng.choice(foreign_currencies)
        else:
            currency = primary_currency

        opened_at = (start_dt + timedelta(days=int(rng.integers(0, (ref_dt - start_dt).days)))).date()
        closed_at = None
        if rng.random() > closed_at_null_rate:
            open_dt = datetime.combine(opened_at, datetime.min.time())
            max_days = max(31, (ref_dt - open_dt).days)
            days_after = int(rng.integers(30, max_days))
            closed_at_dt = open_dt + timedelta(days=days_after)
            closed_at = min(closed_at_dt, ref_dt).date()

        avg_balance = int(rng.lognormal(mean=np.log(15_000), sigma=1.2))
        avg_balance = max(100, min(5_000_000, avg_balance))

        status = "Closed" if closed_at else rng.choice(["Active", "Dormant", "Frozen"], p=[0.90, 0.07, 0.03])

        accounts.append(
            {
                "account_id": f"ACC{str(i + 1).zfill(7)}",
                "owner_id": owner_ids[i],
                "owner_type": owner_types[i],
                "institution_id": bank_id,
                "account_type": acc_type,
                "currency": currency,
                "opened_at": opened_at,
                "closed_at": closed_at,
                "status": status,
                "average_balance": avg_balance,
                "city": city,
                "country": "Ethiopia",
            }
        )

    return pl.DataFrame(accounts)
