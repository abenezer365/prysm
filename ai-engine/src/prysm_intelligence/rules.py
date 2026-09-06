"""Six configurable fact rules; temporal family/cycle rules live in network.py."""
import pandas as pd

from .evidence import Lead
from .features import densest, distance_km


def rule_leads(snapshot, f, c):
    found, checks = [], {}
    recent = f.recent

    def emit(code, reason, rows, measurements, strength=.9, relationships=None, entities=None):
        found.append(Lead(code, "rules", reason, strength, rows.transaction_id.tolist(),
                          relationships or [], entities or [], measurements))
        checks[code] = "triggered"

    codes = ("STRUCTURED_DEPOSITS", "HIGH_VELOCITY", "UNEXPLAINED_AMOUNT", "IMPOSSIBLE_BRANCH_TRAVEL", "BUSINESS_RECEIPTS_MISMATCH", "NEW_DEVICE_RAPID_OUTFLOW")
    checks.update({code: "not_triggered" for code in codes})
    deposits = recent[recent.receiver_account_id.isin(f.own_accounts) & recent.transaction_type.eq("Cash Deposit")
                      & recent.amount_etb.ge(c["structuring_reference_etb"]*c["structuring_lower_fraction"])
                      & recent.amount_etb.lt(c["structuring_reference_etb"])]
    cluster = densest(deposits, c["structuring_minutes"])
    if len(cluster) >= c["structuring_min_count"]:
        emit("STRUCTURED_DEPOSITS", "Clustered cash deposits just below the configured synthetic review reference; this reference is not a legal threshold.",
             deposits[deposits.transaction_id.isin([t["transaction_id"] for t in cluster])],
             {"count": len(cluster), "reference_etb": c["structuring_reference_etb"], "minutes": c["structuring_minutes"]})
    cluster = densest(recent, c["velocity_minutes"])
    if len(cluster) >= c["velocity_count"] and len(f.history) >= 4:
        emit("HIGH_VELOCITY", "Observed activity is concentrated into a short interval after sparse historical activity.",
             recent[recent.transaction_id.isin([t["transaction_id"] for t in cluster])],
             {"count": len(cluster), "minutes": c["velocity_minutes"], "prior_count": len(f.history)})
    if f.income is None or not len(f.history):
        checks["UNEXPLAINED_AMOUNT"] = "unavailable"
    else:
        unusual = recent[recent.amount_etb.ge(f.income*c["amount_income_multiple"])
                         & recent.amount_etb.ge(f.values["history_median_etb"]*c["amount_history_multiple"])
                         & ~recent.transaction_type.eq("Asset Sale")]
        if len(unusual):
            emit("UNEXPLAINED_AMOUNT", "Amount exceeds both declared monthly income and historical transaction size without recorded asset-sale context.", unusual,
                 {"income_etb": f.income, "history_median_etb": f.values["history_median_etb"], "income_multiple": c["amount_income_multiple"]})
    travel = [p for p in f.travel_pairs if p["distance_km"] >= c["travel_min_km"] and p["speed_kmh"] > c["travel_speed_kmh"]]
    if travel:
        ids = {tid for p in travel for tid in p["transaction_ids"]}
        emit("IMPOSSIBLE_BRANCH_TRAVEL", "Initiating-account branch events imply implausible physical travel; verify location quality or unauthorized account use.",
             recent[recent.transaction_id.isin(ids)], {"pairs": travel, "speed_reference_kmh": c["travel_speed_kmh"]})
    declarations = 0
    rel = snapshot.relationships
    owned = rel[rel.relationship_type.eq("beneficial_owner") & (rel.source_type+":"+rel.source_id).eq(snapshot.subject)]
    for relationship in owned.itertuples(index=False):
        companies = snapshot.companies[snapshot.companies.company_id.eq(relationship.target_id)]
        if companies.empty:
            continue
        business = companies.iloc[0]
        if pd.isna(business.declared_sales_etb) or business.sales_reported_at > snapshot.cutoff:
            continue
        declarations += 1
        sales = recent[recent.receiver_account_id.isin(f.own_accounts) & recent.transaction_type.eq("Business Sale")
                       & recent.timestamp.ge(business.sales_period_start) & recent.timestamp.lt(business.sales_period_end)]
        nearby = [t for t in sales.to_dict("records") if distance_km(t, business) <= c["tax_near_business_km"]]
        total = float(sales.amount_etb.sum())
        if len(nearby) >= 3 and total > max(business.declared_sales_etb, 1)*c["tax_receipts_multiple"]:
            emit("BUSINESS_RECEIPTS_MISMATCH", "Business-tagged receipts reach the beneficial owner's personal accounts near the business and exceed its available declaration for the same period. This is a potential tax-investigation lead, not proof of evasion.",
                 sales, {"business_id": business.company_id, "declared_sales_etb": float(business.declared_sales_etb), "personal_receipts_etb": total,
                         "nearby_receipts": len(nearby), "distance_reference_km": c["tax_near_business_km"],
                         "sales_period_start": business.sales_period_start.isoformat(), "sales_period_end": business.sales_period_end.isoformat(),
                         "sales_reported_at": business.sales_reported_at.isoformat(), "declaration_source": "companies.parquet"},
                 relationships=[relationship.relationship_id], entities=[f"Company:{business.company_id}"])
    if not declarations:
        checks["BUSINESS_RECEIPTS_MISMATCH"] = "unavailable"
    if f.income is None or not len(f.history):
        checks["NEW_DEVICE_RAPID_OUTFLOW"] = "unavailable"
    else:
        fresh = recent[recent.transaction_id.isin(f.support["new_device_fraction"]) & ~recent.transaction_type.eq("Purchase")]
        cluster = densest(fresh, c["new_device_minutes"])
        total = sum(t["amount_etb"] for t in cluster)
        if len(cluster) >= 3 and total > f.income*c["new_device_outflow_multiple"]:
            emit("NEW_DEVICE_RAPID_OUTFLOW", "Large rapid outflows use devices absent from prior initiating-account activity; investigate possible unauthorized use.",
                 fresh[fresh.transaction_id.isin([t["transaction_id"] for t in cluster])],
                 {"outflow_etb": total, "income_etb": f.income, "count": len(cluster), "minutes": c["new_device_minutes"]})
    return found, checks
