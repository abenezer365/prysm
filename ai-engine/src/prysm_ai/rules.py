"""Configurable, explainable pattern rules."""

from __future__ import annotations

from .contracts import RuleFinding


class RuleEngine:
    def __init__(self, config: dict):
        self.config = config

    @staticmethod
    def _finding(rule_id: str, name: str, entity_key: str, score: float, explanation: str, measurements: dict, severity: str = "medium", transaction_ids: list[str] | None = None) -> RuleFinding:
        evidence = [] if transaction_ids is None else [str(value) for value in transaction_ids]
        return RuleFinding(rule_id, name, "triggered", severity, float(min(max(score, 0), 1)), explanation, [entity_key], evidence, measurements)

    def evaluate(self, row: dict) -> list[RuleFinding]:
        c, found = self.config, []
        spec = c["unusual_amount"]
        if spec["enabled"] and row["history_tx_count"] >= 5 and row["recent_amount_z"] >= spec["z_threshold"] and row["history_mean_amount_etb"] >= spec["minimum_etb"]:
            found.append(self._finding("TX_AMOUNT_DEVIATION", "Unusual transaction amount", row["entity_key"], row["recent_amount_z"] / 6, "Recent amount behavior is materially above the entity's prior baseline.", {"z_score": row["recent_amount_z"], "history_mean_etb": row["history_mean_amount_etb"]}, transaction_ids=row.get("transaction_ids_30d", [])))
        spec = c["transaction_burst"]
        if spec["enabled"] and row["tx_count_1d"] >= spec["count_24h"]:
            found.append(self._finding("TX_BURST_24H", "Transaction burst", row["entity_key"], row["tx_count_1d"] / (2 * spec["count_24h"]), "The 24-hour transaction count exceeds the configured burst threshold.", {"count_24h": row["tx_count_1d"]}, transaction_ids=row.get("transaction_ids_30d", [])))
        spec = c["unusual_frequency"]
        if spec["enabled"] and row["tx_count_30d"] >= spec["minimum_count_30d"] and row["recent_to_history_count_ratio"] >= spec["recent_to_history_ratio"]:
            found.append(self._finding("TX_FREQUENCY_CHANGE_30D", "Unusual transaction frequency", row["entity_key"], row["recent_to_history_count_ratio"] / 4, "Thirty-day transaction frequency exceeds the entity's historical rate.", {"count_30d": row["tx_count_30d"], "activity_ratio": row["recent_to_history_count_ratio"]}, transaction_ids=row.get("transaction_ids_30d", [])))
        spec = c["rapid_outflow"]
        if spec["enabled"] and row["inflow_etb_7d"] >= spec["minimum_inflow_etb_7d"] and row["outflow_ratio_7d"] >= spec["outflow_ratio"]:
            found.append(self._finding("RAPID_OUTFLOW_7D", "Rapid outflow pattern", row["entity_key"], row["outflow_ratio_7d"] / 2, "Seven-day outflow is high relative to inflow.", {"inflow_etb_7d": row["inflow_etb_7d"], "outflow_etb_7d": row["outflow_etb_7d"], "ratio": row["outflow_ratio_7d"]}, "high", row.get("transaction_ids_30d", [])))
        spec = c["foreign_income_increase"]
        if spec["enabled"] and row["foreign_inflow_etb_30d"] >= spec["minimum_etb_30d"] and row["foreign_recent_to_history_ratio"] >= spec["recent_to_history_ratio"]:
            found.append(self._finding("FOREIGN_CURRENCY_INFLOW_CHANGE", "Foreign-currency inflow increase", row["entity_key"], row["foreign_recent_to_history_ratio"] / 4, "Recent foreign-currency inflow exceeds the historical rate; geography is not inferred.", {"foreign_inflow_etb_30d": row["foreign_inflow_etb_30d"], "rate_ratio": row["foreign_recent_to_history_ratio"]}, transaction_ids=row.get("transaction_ids_30d", [])))
        spec = c["counterparty_change"]
        if spec["enabled"] and row["counterparty_count_30d"] >= spec["minimum_counterparties_30d"] and row["recent_to_history_count_ratio"] >= spec["recent_to_history_ratio"]:
            found.append(self._finding("COUNTERPARTY_ACTIVITY_CHANGE", "Unusual counterparty activity", row["entity_key"], row["recent_to_history_count_ratio"] / 4, "Recent activity and counterparty breadth exceed the historical rate.", {"counterparties_30d": row["counterparty_count_30d"], "activity_ratio": row["recent_to_history_count_ratio"]}, transaction_ids=row.get("transaction_ids_30d", [])))
        spec = c["shared_identifiers"]
        shared = row["shared_device_relationship_count"] + row["shared_address_relationship_count"]
        if spec["enabled"] and shared >= spec["minimum_connections"]:
            found.append(self._finding("SHARED_IDENTIFIER_NETWORK", "Shared identifier network", row["entity_key"], shared / 5, "Multiple active shared-device/address relationships are present.", {"shared_relationships": shared}, "low"))
        spec = c["invoice_chronology"]
        if spec["enabled"] and row["invoice_invalid_count_30d"] >= spec["minimum_invalid_events_30d"]:
            found.append(self._finding("INVOICE_CHRONOLOGY", "Invoice chronology inconsistency", row["entity_key"], row["invoice_invalid_count_30d"] / 3, "An invoice-linked transaction predates the invoice issue date.", {"invalid_events_30d": row["invoice_invalid_count_30d"]}, "low", row.get("transaction_ids_30d", [])))
        return found
