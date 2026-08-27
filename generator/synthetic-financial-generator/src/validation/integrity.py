"""Data integrity validation — FK checks, orphan detection, range validation."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

import polars as pl


def validate_all(
    datasets: dict[str, pl.DataFrame],
    config: dict,
) -> dict[str, Any]:
    """
    Run all integrity checks and return a dictionary of results.
    Returns a dict with keys: errors (list of strings), warnings (list), passed (bool).
    """
    errors: list[str] = []
    warnings: list[str] = []
    start_date_str = config.get("temporal", {}).get("start_date", "2022-01-01")
    end_date_str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    start_dt = date.fromisoformat(start_date_str)
    end_dt = date.fromisoformat(end_date_str)

    persons = datasets.get("persons")
    companies = datasets.get("companies")
    banks = datasets.get("banks")
    accounts = datasets.get("accounts")
    devices = datasets.get("devices")
    invoices = datasets.get("invoices")
    transactions = datasets.get("transactions")
    relationships = datasets.get("relationships")
    ground_truth = datasets.get("ground_truth")

    # Build valid ID sets
    person_ids = set(persons["person_id"].to_list()) if persons is not None else set()
    company_ids = set(companies["company_id"].to_list()) if companies is not None else set()
    bank_ids = set(banks["institution_id"].to_list()) if banks is not None else set()
    account_ids = set(accounts["account_id"].to_list()) if accounts is not None else set()
    device_ids = set(devices["device_id"].to_list()) if devices is not None else set()
    invoice_ids = set(invoices["invoice_id"].to_list()) if invoices is not None else set()
    valid_rel_types = set(config.get("relationship_types", []))

    # --- Accounts FK ---
    if accounts is not None:
        # owner_id must exist in persons or companies
        for row in accounts.select(["owner_id", "owner_type"]).to_dicts():
            oid, otype = row["owner_id"], row["owner_type"]
            if otype == "Person" and oid not in person_ids:
                errors.append(f"Account owner_id {oid} (Person) not found")
            elif otype == "Company" and oid not in company_ids:
                errors.append(f"Account owner_id {oid} (Company) not found")
        # institution_id
        bad_banks = set(accounts["institution_id"].to_list()) - bank_ids
        if bad_banks:
            errors.append(f"Accounts reference unknown bank IDs: {list(bad_banks)[:5]}")

    # --- Transactions FK ---
    if transactions is not None:
        bad_sender = set(transactions["sender_account_id"].to_list()) - account_ids
        if bad_sender:
            errors.append(f"Transactions reference unknown sender accounts: {list(bad_sender)[:5]}")
        bad_receiver = set(transactions["receiver_account_id"].to_list()) - account_ids
        if bad_receiver:
            errors.append(f"Transactions reference unknown receiver accounts: {list(bad_receiver)[:5]}")

        # Positive amounts
        neg_amounts = transactions.filter(pl.col("amount") <= 0)
        if len(neg_amounts) > 0:
            errors.append(f"{len(neg_amounts)} transactions have non-positive amounts")

        # Device IDs (nullable) must be valid when present
        tx_dev = transactions.filter(pl.col("device_id").is_not_null())
        bad_devs = set(tx_dev["device_id"].to_list()) - device_ids
        if bad_devs:
            errors.append(f"Transactions reference unknown device IDs: {list(bad_devs)[:5]}")

        # Invoice IDs (nullable) must be valid when present
        tx_inv = transactions.filter(pl.col("invoice_id").is_not_null())
        bad_invs = set(tx_inv["invoice_id"].to_list()) - invoice_ids
        if bad_invs:
            errors.append(f"Transactions reference unknown invoice IDs: {list(bad_invs)[:5]}")

    # --- Relationships ---
    if relationships is not None and valid_rel_types:
        bad_rel_types = set(relationships["relationship_type"].to_list()) - valid_rel_types
        if bad_rel_types:
            errors.append(f"Unknown relationship types: {bad_rel_types}")

    # --- Date ranges ---
    date_checks = [
        ("persons", "date_of_birth"),
        ("accounts", "opened_at"),
        ("transactions", "timestamp"),
    ]
    for ds_name, col_name in date_checks:
        ds = datasets.get(ds_name)
        if ds is None or col_name not in ds.columns:
            continue
        # Just a basic null check for dates
        null_count = ds[col_name].null_count()
        if null_count > 0:
            warnings.append(f"{ds_name}.{col_name} has {null_count} null values (unexpected)")

    return {
        "passed": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors[:50],   # cap at 50
        "warnings": warnings[:50],
    }
