"""Versioned source contract. No labels, splits, or derived model scores in facts."""
import pyarrow as pa

VERSION = "prysm-benchmark-v1"
TS = pa.timestamp("us", tz="UTC")
S, F, L = pa.string(), pa.float64(), pa.list_(pa.string())


def schema(fields, nullable=()):
    return pa.schema([pa.field(name, kind, nullable=name in nullable) for name, kind in fields])


GEO = [("city", S), ("region", S), ("country", S), ("latitude", F), ("longitude", F)]
SCHEMAS = {
    "persons": schema([
        ("person_id", S), ("first_name", S), ("last_name", S), ("date_of_birth", TS),
        ("gender", S), ("occupation", S), ("employment_status", S),
        ("declared_monthly_income", F), ("income_currency", S), ("created_at", TS), *GEO]),
    "companies": schema([
        ("company_id", S), ("company_name", S), ("industry", S), ("registration_date", TS),
        ("declared_sales_etb", F), ("sales_period_start", TS), ("sales_period_end", TS),
        ("sales_reported_at", TS), *GEO]),
    "institutions": schema([("institution_id", S), ("institution_name", S),
                            ("institution_type", S), ("country", S)]),
    "accounts": schema([
        ("account_id", S), ("owner_type", S), ("owner_id", S), ("institution_id", S),
        ("account_type", S), ("currency", S), ("opened_at", TS), ("closed_at", TS),
        ("status", S)], nullable=("closed_at",)),
    "relationships": schema([
        ("relationship_id", S), ("source_type", S), ("source_id", S),
        ("relationship_type", S), ("target_type", S), ("target_id", S),
        ("start_time", TS), ("end_time", TS), ("confidence", F)], nullable=("end_time",)),
    "transactions": schema([
        ("transaction_id", S), ("timestamp", TS), ("sender_account_id", S),
        ("receiver_account_id", S), ("amount", F), ("currency", S), ("fx_rate_to_etb", F),
        ("amount_etb", F), ("transaction_type", S), ("channel", S), ("device_id", S),
        ("status", S), *GEO], nullable=("device_id",)),
    "ground_truth": schema([
        ("ground_truth_id", S), ("entity_key", S), ("scenario", S), ("is_suspicious", pa.bool_()),
        ("split", S), ("history_start", TS), ("window_start", TS), ("window_end", TS),
        ("as_of", TS), ("member_entity_keys", L), ("context_transaction_ids", L),
        ("evidence_transaction_ids", L), ("evidence_relationship_ids", L), ("rationale", S)]),
}
KEYS = {name: next(iter(value)).name for name, value in SCHEMAS.items()}
PATTERNS = ("structuring", "velocity", "amount", "geography", "network", "family", "tax", "theft")
NORMAL = dict(zip(PATTERNS, (
    "ordinary_deposits", "market_day_sales", "asset_sale", "planned_travel",
    "supplier_settlement", "family_support", "declared_trading", "planned_purchase")))
RATIONALES = {
    "structuring": "Six tightly clustered cash deposits just below an invented 10,000 ETB review reference; this is not a legal reporting threshold.",
    "velocity": "Six transfers within fifteen minutes after a sparse three-month history.",
    "amount": "A transfer twelve times declared monthly income without an asset-sale context.",
    "geography": "Two physical branch events in Addis Ababa and Mekelle fifteen minutes apart; coordinates describe branch location, not IP location.",
    "network": "Two rapid circular movements through a customer and the subject-owned business.",
    "family": "Funds rapidly pass through a documented relative to the subject-owned business twice; kinship alone is not suspicious.",
    "tax": "Repeated business-sale receipts routed to the owner's personal account while the business declares substantially lower sales for the same period; an injected omission, not a legal finding.",
    "theft": "Abrupt large outflows on a previously unseen device, unlike the documented purchase control; the simulated unauthorized intent is ground truth only.",
}
