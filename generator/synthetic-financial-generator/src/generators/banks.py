"""Banks generator — exactly 20 Ethiopian and foreign banks."""
from __future__ import annotations

import polars as pl
import pyarrow as pa

from src.utils.ethiopian_data import get_bank_list


SCHEMA = pa.schema(
    [
        pa.field("institution_id", pa.string()),
        pa.field("institution_name", pa.string()),
        pa.field("institution_type", pa.string()),
        pa.field("country", pa.string()),
        pa.field("supported_currencies", pa.list_(pa.string())),
    ]
)


def generate_banks(config: dict) -> pl.DataFrame:
    """Generate exactly 20 bank records."""
    records = get_bank_list(config)
    # Ensure we get exactly the configured count (pad / trim)
    target = config.get("dataset", {}).get("banks", 20)
    records = records[:target]
    return pl.DataFrame(
        {
            "institution_id": [r["institution_id"] for r in records],
            "institution_name": [r["institution_name"] for r in records],
            "institution_type": [r["institution_type"] for r in records],
            "country": [r["country"] for r in records],
            "supported_currencies": [r["supported_currencies"] for r in records],
        }
    )
