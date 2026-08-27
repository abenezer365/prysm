"""Transactions generator — 700,000 transactions in batches."""
from __future__ import annotations

from datetime import datetime

import numpy as np
import polars as pl

from src.utils.ethiopian_data import get_city_weights, get_region, to_etb
from src.utils.hashing import ip_hash as make_ip_hash


def generate_transactions(
    config: dict,
    account_ids: list[str],
    device_ids: list[str],
    invoice_ids: list[str],
) -> pl.DataFrame:
    seed: int = config.get("seed", 42) + 5
    count: int = config.get("dataset", {}).get("transactions", 700_000)
    ref_date: str = config.get("temporal", {}).get("reference_date", "2026-01-01")
    start_date: str = config.get("temporal", {}).get("start_date", "2022-01-01")
    ref_ts = datetime.fromisoformat(ref_date).timestamp()
    start_ts = datetime.fromisoformat(start_date).timestamp()

    dq = config.get("data_quality", {}).get("column_missing_rates", {})
    device_missing_rate = dq.get("device_id", 0.05)
    invoice_missing_rate = dq.get("invoice_id", 0.15)

    rng = np.random.default_rng(seed)
    cities, city_weights = get_city_weights(config)
    tx_types = config.get("transaction_types", ["Transfer", "Payment", "Withdrawal", "Deposit"])
    channels = config.get("transaction_channels", ["ATM", "Mobile Banking", "Internet Banking", "Branch", "USSD"])
    currencies_cfg = config.get("currencies", {})
    primary_currency = currencies_cfg.get("primary", "ETB")
    foreign_currencies = currencies_cfg.get("foreign", ["USD", "EUR"])
    statuses = ["Completed", "Pending", "Failed", "Reversed"]
    status_weights = [0.88, 0.05, 0.05, 0.02]
    tx_type_weights = [0.30, 0.25, 0.15, 0.15, 0.03, 0.03, 0.02, 0.04, 0.02, 0.01]

    # Channel weights
    channel_weights = [0.20, 0.40, 0.15, 0.15, 0.07, 0.02, 0.01]

    all_records: list[dict] = []
    batch_size = config.get("output", {}).get("batch_size", 10_000)

    tx_type_list = tx_types[:10] if len(tx_types) >= 10 else tx_types
    tw_adjusted = tx_type_weights[: len(tx_type_list)]
    tw_adjusted = [w / sum(tw_adjusted) for w in tw_adjusted]

    ch_list = channels[:7] if len(channels) >= 7 else channels
    cw_adjusted = channel_weights[: len(ch_list)]
    cw_adjusted = [w / sum(cw_adjusted) for w in cw_adjusted]

    currency_pool = [primary_currency] + foreign_currencies
    currency_weights = [0.82, 0.07, 0.05, 0.03, 0.02, 0.01][: len(currency_pool)]
    currency_weights = [w / sum(currency_weights) for w in currency_weights]

    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)
        batch_n = batch_end - batch_start

        sender_idx = rng.integers(0, len(account_ids), size=batch_n)
        receiver_idx = rng.integers(0, len(account_ids), size=batch_n)
        # Avoid self-transfers
        same_mask = sender_idx == receiver_idx
        receiver_idx[same_mask] = (receiver_idx[same_mask] + 1) % len(account_ids)

        timestamps = rng.uniform(start_ts, ref_ts, size=batch_n)
        amounts = np.exp(rng.normal(loc=np.log(5_000), scale=1.8, size=batch_n)).astype(int)
        amounts = np.clip(amounts, 50, 5_000_000)
        tx_type_choices = rng.choice(len(tx_type_list), size=batch_n, p=tw_adjusted)
        channel_choices = rng.choice(len(ch_list), size=batch_n, p=cw_adjusted)
        currency_choices = rng.choice(len(currency_pool), size=batch_n, p=currency_weights)
        device_mask = rng.random(batch_n) < device_missing_rate
        invoice_mask = rng.random(batch_n) < invoice_missing_rate
        device_choices = rng.integers(0, len(device_ids), size=batch_n)
        invoice_choices = rng.integers(0, len(invoice_ids), size=batch_n)
        status_choices = rng.choice(statuses, size=batch_n, p=status_weights)
        city_choices = rng.choice(len(cities), size=batch_n, p=city_weights)

        for j in range(batch_n):
            global_i = batch_start + j
            currency = currency_pool[currency_choices[j]]
            amount = int(amounts[j])
            amount_etb = to_etb(amount, currency, config)
            ts = datetime.fromtimestamp(timestamps[j])
            tx_id = f"TX{str(global_i + 1).zfill(8)}"
            city = cities[city_choices[j]]

            dev_id = None if device_mask[j] else device_ids[device_choices[j]]
            inv_id = None if invoice_mask[j] else invoice_ids[invoice_choices[j]]
            ip = None if rng.random() < 0.10 else make_ip_hash(account_ids[sender_idx[j]], str(ts))
            ref_id = None if rng.random() < 0.70 else f"REF{str(global_i + 1).zfill(8)}"

            all_records.append(
                {
                    "transaction_id": tx_id,
                    "timestamp": ts,
                    "sender_account_id": account_ids[sender_idx[j]],
                    "receiver_account_id": account_ids[receiver_idx[j]],
                    "amount": amount,
                    "currency": currency,
                    "amount_etb": amount_etb,
                    "transaction_type": tx_type_list[tx_type_choices[j]],
                    "channel": ch_list[channel_choices[j]],
                    "device_id": dev_id,
                    "city": city,
                    "country": "Ethiopia",
                    "ip_hash": ip,
                    "reference_id": ref_id,
                    "invoice_id": inv_id,
                    "status": status_choices[j],
                }
            )

    return pl.DataFrame(all_records)
