"""Companies generator — 10,000 synthetic Ethiopian/international companies."""
from __future__ import annotations

from datetime import datetime, date

import numpy as np
import polars as pl

from src.utils.ethiopian_data import get_city_weights, get_region


# International tech/startup name components
_INTL_PREFIXES = [
    "Apex", "Nova", "Orbit", "Zenith", "Vertex", "Flux", "Nexus", "Axiom",
    "Cipher", "Helix", "Vortex", "Cascade", "Prism", "Quantum", "Ionic",
    "Synapse", "Aether", "Cobalt", "Ember", "Stratos",
]
_INTL_SUFFIXES = [
    "Tech", "Labs", "Systems", "Digital", "AI", "IO", "Cloud", "Hub",
    "Works", "Group", "Solutions", "Dynamics", "Ventures", "Data", "Net",
]

# Local Ethiopian company name components
_ETH_PREFIXES = [
    "Abay", "Awash", "Tana", "Rift", "Addis", "Harar", "Simien", "Lalibela",
    "Nile", "Oromia", "Tigray", "Amhara", "Bale", "Gambella",
]
_ETH_SUFFIXES = [
    "Trading", "PLC", "Import Export", "Construction", "Manufacturing",
    "Agro", "Textile", "Investment", "Real Estate", "Services",
]


def _make_company_name(is_international: bool, rng: np.random.Generator, idx: int) -> str:
    if is_international:
        pre = _INTL_PREFIXES[rng.integers(0, len(_INTL_PREFIXES))]
        suf = _INTL_SUFFIXES[rng.integers(0, len(_INTL_SUFFIXES))]
        return f"{pre}{suf} {idx}"
    else:
        pre = _ETH_PREFIXES[rng.integers(0, len(_ETH_PREFIXES))]
        suf = _ETH_SUFFIXES[rng.integers(0, len(_ETH_SUFFIXES))]
        return f"{pre} {suf}"


def generate_companies(config: dict) -> pl.DataFrame:
    seed: int = config.get("seed", 42) + 1  # offset seed
    count: int = config.get("dataset", {}).get("companies", 10_000)
    ref_date: str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    start_date: str = config.get("temporal", {}).get("start_date", "2022-01-01")
    ref_dt = datetime.fromisoformat(ref_date)
    start_dt = datetime.fromisoformat(start_date)
    days_range = (ref_dt - start_dt).days

    rng = np.random.default_rng(seed)
    cities, city_weights = get_city_weights(config)

    intl_industries = config.get("company_industries", {}).get(
        "international",
        ["Technology", "FinTech", "E-Commerce", "Logistics", "Consulting"],
    )
    local_industries = config.get("company_industries", {}).get(
        "local",
        ["Agriculture", "Construction", "Retail", "Import/Export", "Manufacturing"],
    )
    sizes_cfg: dict = config.get("company_sizes", {
        "Micro": [1, 9], "Small": [10, 49], "Medium": [50, 249],
        "Large": [250, 4999], "Enterprise": [5000, 50000],
    })
    sizes = list(sizes_cfg.keys())
    size_weights = [0.30, 0.35, 0.20, 0.12, 0.03]

    companies: list[dict] = []
    for i in range(count):
        is_international = rng.random() < 0.70
        industry_pool = intl_industries if is_international else local_industries
        industry = industry_pool[rng.integers(0, len(industry_pool))]
        country = "USA" if is_international else "Ethiopia"
        city_choice = cities[rng.choice(len(cities), p=city_weights)]
        region = get_region(city_choice, config)
        size_label = sizes[rng.choice(len(sizes), p=size_weights)]
        size_range = sizes_cfg[size_label]
        emp_count = int(rng.integers(size_range[0], size_range[1] + 1))
        annual_rev = int(rng.lognormal(mean=np.log(max(emp_count * 5000, 100_000)), sigma=0.7))
        reg_date = (start_dt + (ref_dt - start_dt) * rng.random()).date()

        companies.append(
            {
                "company_id": f"C{str(i + 1).zfill(5)}",
                "company_name": _make_company_name(is_international, rng, i + 1),
                "country": country,
                "industry": industry,
                "company_size": size_label,
                "employee_count": emp_count,
                "annual_revenue": annual_rev,
                "registration_date": reg_date,
                "city": city_choice,
                "region": region,
                "status": rng.choice(["Active", "Suspended", "Dissolved"], p=[0.85, 0.10, 0.05]),
            }
        )

    return pl.DataFrame(companies)
