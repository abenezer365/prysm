"""Deterministic hashing helpers."""
from __future__ import annotations

import hashlib


def sha256_short(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def phone_hash(first: str, last: str, city: str) -> str:
    return sha256_short(f"{first}{last}{city}", 16)


def address_hash(first: str, last: str, city: str, region: str) -> str:
    return sha256_short(f"{first}{last}{city}{region}", 16)


def device_fingerprint(device_id: str, os: str, device_type: str) -> str:
    return sha256_short(f"{device_id}{os}{device_type}", 32)


def ip_hash(account_id: str, ts: str) -> str:
    return sha256_short(f"{account_id}{ts}", 16)
