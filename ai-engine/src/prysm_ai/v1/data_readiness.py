"""Validate and canonicalize Prysm's raw synthetic financial data.

The module deliberately separates immutable source data, deterministic
canonicalization, machine-readable audit evidence, and modeling views.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


TABLE_KEYS = {
    "accounts": "account_id",
    "banks": "institution_id",
    "companies": "company_id",
    "devices": "device_id",
    "ground_truth": "ground_truth_id",
    "invoices": "invoice_id",
    "persons": "person_id",
    "relationships": "relationship_id",
    "transactions": "transaction_id",
}

REQUIRED_COLUMNS = {
    "accounts": {"account_id", "owner_id", "owner_type", "institution_id", "account_type", "currency", "opened_at", "closed_at", "status", "average_balance", "city", "country"},
    "banks": {"institution_id", "institution_name", "institution_type", "country", "supported_currencies"},
    "companies": {"company_id", "company_name", "country", "industry", "company_size", "employee_count", "annual_revenue", "registration_date", "city", "region", "status"},
    "devices": {"device_id", "device_type", "os", "browser", "device_fingerprint", "first_seen", "last_seen", "city", "country"},
    "ground_truth": {"ground_truth_id", "entity_type", "entity_id", "behavior_type", "risk_pattern", "is_anomalous", "severity", "pattern_start", "pattern_end", "related_entity_ids"},
    "invoices": {"invoice_id", "issuer_id", "issuer_type", "recipient_id", "recipient_type", "issue_date", "due_date", "amount", "currency", "service_type", "status"},
    "persons": {"person_id", "first_name", "last_name", "date_of_birth", "gender", "nationality", "occupation", "employment_status", "declared_monthly_income", "income_currency", "city", "region", "country", "phone_hash", "address_hash", "created_at"},
    "relationships": {"relationship_id", "source_type", "source_id", "relationship_type", "target_type", "target_id", "start_time", "end_time", "confidence"},
    "transactions": {"transaction_id", "timestamp", "sender_account_id", "receiver_account_id", "amount", "currency", "amount_etb", "transaction_type", "channel", "device_id", "city", "country", "ip_hash", "reference_id", "invoice_id", "status"},
}

TYPE_TO_TABLE = {"Person": "persons", "Company": "companies", "Account": "accounts"}
DATE_COLUMNS = {
    "accounts": ["opened_at", "closed_at"],
    "companies": ["registration_date"],
    "devices": ["first_seen", "last_seen"],
    "ground_truth": ["pattern_start", "pattern_end"],
    "invoices": ["issue_date", "due_date"],
    "persons": ["date_of_birth", "created_at"],
    "relationships": ["start_time", "end_time"],
    "transactions": ["timestamp"],
}


def _json_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(v) for v in value]
    if hasattr(value, "item"):
        return value.item()
    if pd.isna(value):
        return None
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _typed_key(entity_type: pd.Series, entity_id: pd.Series) -> pd.Series:
    return entity_type.astype("string") + ":" + entity_id.astype("string")


@dataclass
class FoundationBuilder:
    raw_dir: Path
    output_dir: Path
    report_dir: Path

    def load(self) -> dict[str, pd.DataFrame]:
        missing = [name for name in TABLE_KEYS if not (self.raw_dir / f"{name}.parquet").is_file()]
        if missing:
            raise FileNotFoundError(f"Missing required raw datasets: {', '.join(missing)}")
        tables = {name: pd.read_parquet(self.raw_dir / f"{name}.parquet") for name in TABLE_KEYS}
        schema_errors = {
            name: sorted(REQUIRED_COLUMNS[name] - set(frame.columns))
            for name, frame in tables.items() if REQUIRED_COLUMNS[name] - set(frame.columns)
        }
        if schema_errors:
            raise ValueError(f"Missing required columns: {schema_errors}")
        for name, columns in DATE_COLUMNS.items():
            for column in columns:
                tables[name][column] = pd.to_datetime(tables[name][column], errors="coerce", utc=True)
        return tables

    @staticmethod
    def canonicalize_persons(persons: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Choose one deterministic row per ID while retaining duplicate lineage.

        Prefer the most complete row, then the latest created_at, then original
        source order. No fuzzy merging is performed because IDs are authoritative.
        """
        work = persons.copy()
        work["_source_row"] = range(len(work))
        work["_completeness"] = work.notna().sum(axis=1)
        work = work.sort_values(
            ["person_id", "_completeness", "created_at", "_source_row"],
            ascending=[True, False, False, True],
            kind="stable",
        )
        canonical = work.drop_duplicates("person_id", keep="first").copy()
        selected = canonical.set_index("person_id")["_source_row"]
        duplicate_ids = work.loc[work.duplicated("person_id", keep=False), "person_id"]
        lineage = work.loc[work["person_id"].isin(duplicate_ids), ["person_id", "_source_row", "_completeness"]].copy()
        lineage["selected_as_canonical"] = lineage["_source_row"].eq(lineage["person_id"].map(selected))
        canonical = canonical.sort_values("_source_row").drop(columns=["_source_row", "_completeness"])
        return canonical.reset_index(drop=True), lineage.reset_index(drop=True)

    @staticmethod
    def _reference_audit(tables: dict[str, pd.DataFrame]) -> dict[str, Any]:
        ids = {name: set(frame[TABLE_KEYS[name]].dropna()) for name, frame in tables.items()}
        checks: dict[str, Any] = {}

        def simple(name: str, source: str, column: str, target: str, nullable: bool = False) -> None:
            values = tables[source][column]
            present = values.notna()
            valid = values.isin(ids[target])
            checks[name] = {
                "rows": int(len(values)), "null": int((~present).sum()),
                "invalid_non_null": int((present & ~valid).sum()),
                "nullable_by_contract": nullable,
            }

        simple("accounts.institution_id->banks", "accounts", "institution_id", "banks")
        simple("transactions.sender->accounts", "transactions", "sender_account_id", "accounts")
        simple("transactions.receiver->accounts", "transactions", "receiver_account_id", "accounts")
        simple("transactions.device->devices", "transactions", "device_id", "devices", True)
        simple("transactions.invoice->invoices", "transactions", "invoice_id", "invoices", True)

        for table, type_col, id_col, label in [
            ("accounts", "owner_type", "owner_id", "accounts.owner"),
            ("invoices", "issuer_type", "issuer_id", "invoices.issuer"),
            ("invoices", "recipient_type", "recipient_id", "invoices.recipient"),
            ("ground_truth", "entity_type", "entity_id", "ground_truth.entity"),
            ("relationships", "source_type", "source_id", "relationships.source"),
            ("relationships", "target_type", "target_id", "relationships.target"),
        ]:
            frame = tables[table]
            recognized = frame[type_col].isin(TYPE_TO_TABLE)
            valid = pd.Series(False, index=frame.index)
            for entity_type, target in TYPE_TO_TABLE.items():
                mask = frame[type_col].eq(entity_type)
                valid.loc[mask] = frame.loc[mask, id_col].isin(ids[target])
            checks[label] = {
                "rows": int(len(frame)),
                "unknown_type": int((~recognized).sum()),
                "null_id": int(frame[id_col].isna().sum()),
                "invalid_typed_reference": int((recognized & ~valid).sum()),
                "types": sorted(str(v) for v in frame[type_col].dropna().unique()),
            }
        return checks

    @staticmethod
    def _temporal_audit(t: dict[str, pd.DataFrame]) -> dict[str, Any]:
        tx = t["transactions"]
        accounts = t["accounts"].set_index("account_id")
        sender_open = tx["sender_account_id"].map(accounts["opened_at"])
        receiver_open = tx["receiver_account_id"].map(accounts["opened_at"])
        sender_close = tx["sender_account_id"].map(accounts["closed_at"])
        receiver_close = tx["receiver_account_id"].map(accounts["closed_at"])
        relationships = t["relationships"]
        invoices = t["invoices"]
        devices = t["devices"]
        ground = t["ground_truth"]
        issue_date = tx["invoice_id"].map(invoices.set_index("invoice_id")["issue_date"])
        return {
            "accounts_closed_before_opened": int((t["accounts"]["closed_at"] < t["accounts"]["opened_at"]).sum()),
            "devices_last_before_first": int((devices["last_seen"] < devices["first_seen"]).sum()),
            "invoices_due_before_issue": int((invoices["due_date"] < invoices["issue_date"]).sum()),
            "relationships_end_before_start": int((relationships["end_time"] < relationships["start_time"]).sum()),
            "ground_truth_end_before_start": int((ground["pattern_end"] < ground["pattern_start"]).sum()),
            "transactions_before_sender_open": int((tx["timestamp"] < sender_open).sum()),
            "transactions_before_receiver_open": int((tx["timestamp"] < receiver_open).sum()),
            "transactions_after_sender_close": int((sender_close.notna() & (tx["timestamp"] > sender_close)).sum()),
            "transactions_after_receiver_close": int((receiver_close.notna() & (tx["timestamp"] > receiver_close)).sum()),
            "invoice_linked_transactions_before_issue": int((tx["invoice_id"].notna() & (tx["timestamp"] < issue_date)).sum()),
            "closed_status_without_closed_at": int((t["accounts"]["status"].eq("Closed") & t["accounts"]["closed_at"].isna()).sum()),
            "nonclosed_status_with_closed_at": int((~t["accounts"]["status"].eq("Closed") & t["accounts"]["closed_at"].notna()).sum()),
        }

    @staticmethod
    def _financial_audit(t: dict[str, pd.DataFrame]) -> dict[str, Any]:
        tx = t["transactions"]
        invoices = t["invoices"]
        accounts = t["accounts"]
        bank_currency = t["banks"].set_index("institution_id")["supported_currencies"]
        supported = [currency in set(bank_currency.loc[institution]) for institution, currency in zip(accounts["institution_id"], accounts["currency"])]
        currency_domains = sorted(set(accounts["currency"]) | set(invoices["currency"]) | set(tx["currency"]))
        rate = tx["amount_etb"] / tx["amount"]
        rates = tx.assign(_rate=rate).groupby("currency", dropna=False)["_rate"].agg(["count", "min", "max", "median"])
        return {
            "transaction_nonpositive_amount": int((tx["amount"] <= 0).sum()),
            "transaction_nonpositive_amount_etb": int((tx["amount_etb"] <= 0).sum()),
            "invoice_nonpositive_amount": int((invoices["amount"] <= 0).sum()),
            "account_negative_average_balance": int((accounts["average_balance"] < 0).sum()),
            "account_currency_not_supported_by_bank": int(len(supported) - sum(supported)),
            "transaction_currency_not_in_sender_account_currency": int((tx["currency"] != tx["sender_account_id"].map(accounts.set_index("account_id")["currency"])).sum()),
            "currency_domain": currency_domains,
            "etb_rate_by_currency": _json_value(rates.reset_index().to_dict("records")),
        }

    @staticmethod
    def _label_audit(t: dict[str, pd.DataFrame]) -> dict[str, Any]:
        gt = t["ground_truth"].copy()
        label_cols = ["entity_type", "entity_id", "behavior_type", "risk_pattern", "is_anomalous", "severity", "pattern_start", "pattern_end"]
        exact_semantic = gt.duplicated(label_cols, keep=False)
        window_key = ["entity_type", "entity_id", "pattern_start", "pattern_end"]
        conflicts = gt.groupby(window_key, dropna=False)["is_anomalous"].nunique().gt(1)
        entity_label_counts = gt.groupby(["entity_type", "entity_id"])["is_anomalous"].nunique()
        known_ids = set().union(
            set(t["persons"]["person_id"]), set(t["companies"]["company_id"]),
            set(t["accounts"]["account_id"]), set(t["transactions"]["transaction_id"]),
            set(t["invoices"]["invoice_id"]), set(t["devices"]["device_id"]),
        )
        related = [item for values in gt["related_entity_ids"] if values is not None for item in values]
        return {
            "rows": int(len(gt)),
            "duplicate_primary_keys": int(gt["ground_truth_id"].duplicated(keep=False).sum()),
            "exact_semantic_duplicate_rows": int(exact_semantic.sum()),
            "same_window_conflicting_label_groups": int(conflicts.sum()),
            "entities_with_both_labels_across_time": int(entity_label_counts.gt(1).sum()),
            "related_entity_id_values": len(related),
            "unresolved_related_entity_id_values": int(sum(value not in known_ids for value in related)),
            "class_counts": _json_value(gt["is_anomalous"].value_counts(dropna=False).to_dict()),
            "severity_by_label": _json_value(pd.crosstab(gt["severity"], gt["is_anomalous"], dropna=False).to_dict()),
        }

    @staticmethod
    def _missingness(t: dict[str, pd.DataFrame]) -> dict[str, Any]:
        semantic = {
            "accounts.closed_at": "mixed: structural for non-Closed accounts, but missing/invalid lifecycle data when status is Closed",
            "relationships.end_time": "structural: null means open-ended relationship",
            "ground_truth.pattern_end": "structural: null means ongoing/open-ended label window",
            "transactions.invoice_id": "conditional: only invoice-linked transactions need an invoice",
            "transactions.reference_id": "conditional/operational: channel or transaction type may not emit a reference",
            "transactions.device_id": "conditional: non-device channels can legitimately lack a device",
            "transactions.ip_hash": "conditional: non-IP channels can legitimately lack an IP",
            "persons.employment_status": "unknown attribute; retain explicit missing indicator",
            "persons.phone_hash": "unknown identifier; never impute",
            "persons.address_hash": "unknown identifier; never impute",
            "devices.browser": "conditional: some device types/clients have no browser",
        }
        result: dict[str, Any] = {}
        for name, frame in t.items():
            missing = frame.isna().sum()
            result[name] = {
                column: {"count": int(count), "rate": float(count / len(frame))}
                for column, count in missing.items() if count
            }
        result["semantics"] = semantic
        return result

    @staticmethod
    def _relationship_overlap_audit(t: dict[str, pd.DataFrame]) -> dict[str, Any]:
        r = t["relationships"].copy()
        pair = ["source_type", "source_id", "relationship_type", "target_type", "target_id"]
        duplicate_rows = r.duplicated(pair + ["start_time", "end_time"], keep=False)
        # For each identical typed edge, detect any interval overlap after ordering.
        ordered = r.sort_values(pair + ["start_time", "end_time"], kind="stable")
        prior_end = ordered.groupby(pair, dropna=False)["end_time"].shift()
        overlap = prior_end.isna() | (ordered["start_time"] <= prior_end)
        repeated = ordered.duplicated(pair, keep=False)
        return {
            "exact_duplicate_interval_rows": int(duplicate_rows.sum()),
            "repeated_typed_edge_rows": int(repeated.sum()),
            "possible_overlapping_interval_rows": int((repeated & overlap).sum()),
            "note": "Open-ended prior intervals count as possible overlaps; domain resolution is deferred.",
        }

    def audit(self, t: dict[str, pd.DataFrame]) -> dict[str, Any]:
        duplicate_keys = {
            name: int(frame[key].duplicated(keep=False).sum())
            for name, key in TABLE_KEYS.items() for frame in [t[name]]
        }
        duplicate_person_ids = t["persons"].groupby("person_id").size()
        conflicting_person_ids = 0
        for _, group in t["persons"].loc[t["persons"]["person_id"].isin(duplicate_person_ids[duplicate_person_ids > 1].index)].groupby("person_id"):
            if len(group.drop_duplicates()) > 1:
                conflicting_person_ids += 1
        return {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": {
                name: {"rows": int(len(t[name])), "columns": int(len(t[name].columns)), "sha256": _sha256(self.raw_dir / f"{name}.parquet")}
                for name in TABLE_KEYS
            },
            "primary_keys": {"duplicate_rows_by_table": duplicate_keys},
            "person_canonicalization": {
                "duplicate_person_ids": int((duplicate_person_ids > 1).sum()),
                "rows_with_duplicate_person_id": int(duplicate_person_ids[duplicate_person_ids > 1].sum()),
                "conflicting_duplicate_person_ids": conflicting_person_ids,
            },
            "references": self._reference_audit(t),
            "temporal": self._temporal_audit(t),
            "financial": self._financial_audit(t),
            "missingness": self._missingness(t),
            "labels": self._label_audit(t),
            "relationship_intervals": self._relationship_overlap_audit(t),
        }

    def materialize(self, t: dict[str, pd.DataFrame], audit: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        persons, lineage = self.canonicalize_persons(t["persons"])
        persons.to_parquet(self.output_dir / "persons.parquet", index=False)
        lineage.to_parquet(self.output_dir / "person_duplicate_lineage.parquet", index=False)

        relationships = t["relationships"].copy()
        relationships["source_key"] = _typed_key(relationships["source_type"], relationships["source_id"])
        relationships["target_key"] = _typed_key(relationships["target_type"], relationships["target_id"])
        relationships.to_parquet(self.output_dir / "relationship_edges.parquet", index=False)

        invoices = t["invoices"].copy()
        invoices["issuer_key"] = _typed_key(invoices["issuer_type"], invoices["issuer_id"])
        invoices["recipient_key"] = _typed_key(invoices["recipient_type"], invoices["recipient_id"])
        invoices.to_parquet(self.output_dir / "invoices.parquet", index=False)

        ground = t["ground_truth"].copy()
        ground["entity_key"] = _typed_key(ground["entity_type"], ground["entity_id"])
        ground.to_parquet(self.output_dir / "ground_truth_labels.parquet", index=False)

        # Preserve large facts without copying them: lightweight graph bridges are
        # the necessary normalization at this phase.
        accounts = t["accounts"].copy()
        accounts["owner_key"] = _typed_key(accounts["owner_type"], accounts["owner_id"])
        accounts.to_parquet(self.output_dir / "accounts.parquet", index=False)

        transaction_edges = t["transactions"][[
            "transaction_id", "timestamp", "sender_account_id", "receiver_account_id",
            "amount", "currency", "amount_etb", "transaction_type", "channel",
            "device_id", "invoice_id", "status",
        ]].copy()
        transaction_edges["sender_key"] = "Account:" + transaction_edges["sender_account_id"].astype("string")
        transaction_edges["receiver_key"] = "Account:" + transaction_edges["receiver_account_id"].astype("string")
        transaction_edges.to_parquet(self.output_dir / "transaction_edges.parquet", index=False)

        with (self.report_dir / "data_quality_report.json").open("w", encoding="utf-8") as handle:
            json.dump(_json_value(audit), handle, indent=2, sort_keys=True)

        inventory = {p.name: {"rows": int(pd.read_parquet(p).shape[0]), "sha256": _sha256(p)} for p in sorted(self.output_dir.glob("*.parquet"))}
        with (self.output_dir / "MANIFEST.json").open("w", encoding="utf-8") as handle:
            json.dump({"generated_at_utc": audit["generated_at_utc"], "files": inventory}, handle, indent=2, sort_keys=True)

    def run(self) -> dict[str, Any]:
        tables = self.load()
        audit = self.audit(tables)
        self.materialize(tables, audit)
        return audit
