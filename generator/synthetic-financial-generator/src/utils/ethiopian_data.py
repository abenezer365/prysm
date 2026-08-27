"""Utility helpers for Ethiopian data: cities, regions, occupations, banks."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Name loaders
# ---------------------------------------------------------------------------

def load_names(config: dict) -> tuple[list[str], list[str]]:
    """Load boy and girl name lists from the configured CSV paths."""
    root = Path(__file__).resolve().parent.parent.parent  # generator root
    names_cfg = config.get("names", {})
    boy_path = root / names_cfg.get("boy_names_path", "../../data/boy-names.csv")
    girl_path = root / names_cfg.get("girl_names_path", "../../data/girl-names.csv")

    # Resolve relative paths from the generator root
    boy_path = boy_path.resolve()
    girl_path = girl_path.resolve()

    boy_names = pd.read_csv(boy_path)["name"].dropna().tolist()
    girl_names = pd.read_csv(girl_path)["name"].dropna().tolist()
    return boy_names, girl_names


# ---------------------------------------------------------------------------
# City / region helpers
# ---------------------------------------------------------------------------

def get_city_weights(config: dict) -> tuple[list[str], list[float]]:
    cities_cfg: dict = config.get("cities", {})
    cities = list(cities_cfg.keys())
    weights = list(cities_cfg.values())
    # Normalise to guard against rounding errors
    total = sum(weights)
    weights = [w / total for w in weights]
    return cities, weights


def get_region(city: str, config: dict) -> str:
    mapping: dict = config.get("city_region_map", {})
    return mapping.get(city, "Addis Ababa")


# ---------------------------------------------------------------------------
# Occupation / income helpers
# ---------------------------------------------------------------------------

def get_occupation_weights(config: dict) -> tuple[list[str], list[float]]:
    occ_cfg: dict = config.get("occupations", {})
    occs = list(occ_cfg.keys())
    weights = list(occ_cfg.values())
    total = sum(weights)
    weights = [w / total for w in weights]
    return occs, weights


def get_income_params(occupation: str, config: dict) -> tuple[int, int, str]:
    """Return (min_income, max_income, currency) for an occupation."""
    income_cfg: dict = config.get("income_by_occupation", {})
    if occupation in income_cfg:
        entry = income_cfg[occupation]
        return int(entry[0]), int(entry[1]), str(entry[2])
    return 3000, 15000, "ETB"


def determine_employment_status(occupation: str, config: dict) -> str:
    emp_cfg: dict = config.get("employment_by_occupation", {})
    if occupation in emp_cfg:
        return emp_cfg[occupation]
    return emp_cfg.get("default", "Employed")


# ---------------------------------------------------------------------------
# FX helpers
# ---------------------------------------------------------------------------

def to_etb(amount: float, currency: str, config: dict) -> int:
    rates: dict = config.get("currencies", {}).get("fx_rates_to_etb", {})
    rate = rates.get(currency, 1.0)
    return max(1, int(round(amount * rate)))


# ---------------------------------------------------------------------------
# Bank helpers
# ---------------------------------------------------------------------------

def get_bank_list(config: dict) -> list[dict]:
    banks_cfg: dict = config.get("banks", {})
    result = []
    idx = 1
    for b in banks_cfg.get("local", []):
        result.append({
            "institution_id": f"BNK{str(idx).zfill(3)}",
            "institution_name": b["name"],
            "institution_type": b.get("type", "Commercial"),
            "country": "Ethiopia",
            "supported_currencies": ["ETB", "USD", "EUR"],
        })
        idx += 1
    for b in banks_cfg.get("foreign", []):
        result.append({
            "institution_id": f"BNK{str(idx).zfill(3)}",
            "institution_name": b["name"],
            "institution_type": b.get("type", "Foreign"),
            "country": b.get("country", "Unknown"),
            "supported_currencies": ["USD", "EUR", "GBP", "AED", "CHF", "ETB"],
        })
        idx += 1
    return result
