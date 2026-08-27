"""Invoices generator — 200,000 invoices between persons and companies."""
from __future__ import annotations

from datetime import datetime, timedelta

import numpy as np
import polars as pl


def generate_invoices(
    config: dict,
    person_ids: list[str],
    company_ids: list[str],
) -> pl.DataFrame:
    seed: int = config.get("seed", 42) + 4
    count: int = config.get("dataset", {}).get("invoices", 200_000)
    ref_date: str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    start_date: str = config.get("temporal", {}).get("start_date", "2022-01-01")
    ref_dt = datetime.fromisoformat(ref_date)
    start_dt = datetime.fromisoformat(start_date)
    total_days = (ref_dt - start_dt).days

    rng = np.random.default_rng(seed)
    currencies_cfg = config.get("currencies", {})
    primary_currency = currencies_cfg.get("primary", "ETB")
    foreign_currencies = currencies_cfg.get("foreign", ["USD", "EUR"])
    service_types = config.get("invoice_service_types", [
        "Software Development", "Consulting", "Import Duty", "Logistics", "Equipment Supply",
    ])
    statuses = ["Paid", "Pending", "Overdue", "Cancelled"]
    status_weights = [0.70, 0.15, 0.10, 0.05]

    all_entity_ids = person_ids + company_ids
    all_entity_types = ["Person"] * len(person_ids) + ["Company"] * len(company_ids)

    invoices: list[dict] = []
    for i in range(count):
        # Choose issuer and recipient (different entities)
        idx_issuer = rng.integers(0, len(all_entity_ids))
        idx_recip = rng.integers(0, len(all_entity_ids))
        # Ensure issuer != recipient (best effort)
        if idx_recip == idx_issuer:
            idx_recip = (idx_recip + 1) % len(all_entity_ids)

        issue_date = (start_dt + timedelta(days=int(rng.integers(0, total_days)))).date()
        due_date = (datetime.combine(issue_date, datetime.min.time()) + timedelta(days=int(rng.integers(7, 90)))).date()
        amount = int(rng.lognormal(mean=np.log(20_000), sigma=1.5))
        amount = max(500, min(10_000_000, amount))
        currency = rng.choice([primary_currency] + foreign_currencies, p=[0.75, 0.10, 0.05, 0.05, 0.03, 0.02])
        service = service_types[rng.integers(0, len(service_types))]
        status = rng.choice(statuses, p=status_weights)

        invoices.append(
            {
                "invoice_id": f"INV{str(i + 1).zfill(7)}",
                "issuer_id": all_entity_ids[idx_issuer],
                "issuer_type": all_entity_types[idx_issuer],
                "recipient_id": all_entity_ids[idx_recip],
                "recipient_type": all_entity_types[idx_recip],
                "issue_date": issue_date,
                "due_date": due_date,
                "amount": amount,
                "currency": currency,
                "service_type": service,
                "status": status,
            }
        )

    return pl.DataFrame(invoices)
