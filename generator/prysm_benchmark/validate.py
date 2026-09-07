"""Fail-fast structural and scenario evidence checks; never silently clean facts."""
from __future__ import annotations

from collections import Counter
from math import isfinite

from .contract import KEYS, NORMAL, PATTERNS, SCHEMAS
from .generate import PLACES, check_config


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(tables, config):
    check_config(config)
    require(set(tables) == set(SCHEMAS), "Dataset table set does not match contract")
    data = {}
    for name, expected in SCHEMAS.items():
        table = tables[name]
        require(table.schema.equals(expected, check_metadata=False), f"{name}: schema mismatch")
        for field in expected:
            if not field.nullable:
                require(table[field.name].null_count == 0, f"{name}.{field.name}: missing required value")
        rows = table.to_pylist()
        require(len(rows) > 0, f"{name}: empty required table")
        ids = [r[KEYS[name]] for r in rows]
        require(len(set(ids)) == len(ids), f"{name}: duplicate identifier")
        for r in rows:
            for key, value in r.items():
                if isinstance(value, float):
                    require(isfinite(value), f"{name}.{key}: non-finite value")
                if isinstance(value, str):
                    require(bool(value.strip()), f"{name}.{key}: empty value")
            if "latitude" in r:
                require(-90 <= r["latitude"] <= 90 and -180 <= r["longitude"] <= 180,
                        f"{name}: invalid geographic coordinates")
                require(any(r["city"] == p[0] and r["region"] == p[1] and r["country"] == p[2]
                            and abs(r["latitude"]-p[3]) < .2 and abs(r["longitude"]-p[4]) < .2 for p in PLACES),
                        f"{name}: contradictory city/region/country/coordinates")
        data[name] = {r[KEYS[name]]: r for r in rows}
    people, companies, accounts, tx, rel, truth = (data[n] for n in
        ("persons", "companies", "accounts", "transactions", "relationships", "ground_truth"))
    entities = {f"Person:{k}": v for k, v in people.items()} | {f"Company:{k}": v for k, v in companies.items()}
    entity_ids, transaction_ids, relationship_ids = set(entities), set(tx), set(rel)
    owners = {}
    for a in accounts.values():
        key = f"{a['owner_type']}:{a['owner_id']}"
        require(key in entities, "accounts: invalid typed owner")
        owners[a["account_id"]] = key
        require(a["institution_id"] in data["institutions"], "accounts: invalid institution reference")
        require(a["currency"] in config["fx_rates_to_etb"], "accounts: unsupported currency")
        require(a["account_type"] in {"Business", "Savings", "Wallet"}, "accounts: invalid account type")
        require((a["account_type"] == "Business") == (a["owner_type"] == "Company"), "accounts: contradictory owner/account type")
        require(a["status"] in {"Active", "Closed"} and (a["status"] == "Closed") == (a["closed_at"] is not None), "accounts: contradictory status")
        require(a["closed_at"] is None or a["closed_at"] >= a["opened_at"], "accounts: reversed lifecycle")
        created = entities[key].get("created_at", entities[key].get("registration_date"))
        require(a["opened_at"] >= created, "accounts: opened before owner existed")
    require(set(owners.values()) == set(entities), "entities: orphan without an account")
    require({a["institution_id"] for a in accounts.values()} == set(data["institutions"]), "institutions: orphan")
    for p in people.values():
        age = (p["created_at"]-p["date_of_birth"]).days / 365.25
        require(18 <= age <= 100 and p["declared_monthly_income"] > 0, "persons: invalid age/income")
        require(p["income_currency"] in config["fx_rates_to_etb"], "persons: invalid income currency")
    for c in companies.values():
        require(0 <= c["declared_sales_etb"] and c["registration_date"] < c["sales_period_start"] <= c["sales_period_end"] <= c["sales_reported_at"], "companies: invalid declaration period/value")
    seen_edges = set()
    for r in rel.values():
        source, target = f"{r['source_type']}:{r['source_id']}", f"{r['target_type']}:{r['target_id']}"
        kind = r["relationship_type"]
        require(source in entities and target in entities and source != target, "relationships: broken or self reference")
        expected = {"family": ("Person", "Person"), "beneficial_owner": ("Person", "Company"), "employer_employee": ("Company", "Person")}
        require(kind in expected and (r["source_type"], r["target_type"]) == expected[kind], "relationships: contradictory endpoint types")
        pair = tuple(sorted((source, target))) if kind == "family" else (source, target)
        edge = (*pair, kind)
        require(edge not in seen_edges, "relationships: duplicate/contradictory relationship")
        seen_edges.add(edge)
        require(0 <= r["confidence"] <= 1 and (r["end_time"] is None or r["end_time"] >= r["start_time"]), "relationships: invalid interval/confidence")
        for key in (source, target):
            e = entities[key]
            require(r["start_time"] >= e.get("created_at", e.get("registration_date")), "relationships: predates entity")
    used_accounts = set()
    for t in tx.values():
        sender, receiver = t["sender_account_id"], t["receiver_account_id"]
        require(sender in accounts and receiver in accounts and sender != receiver, "transactions: invalid account reference")
        used_accounts.update((sender, receiver))
        require(t["amount"] > 0 and t["amount_etb"] > 0 and t["fx_rate_to_etb"] > 0, "transactions: invalid amount/rate")
        require(t["currency"] in config["fx_rates_to_etb"] and t["fx_rate_to_etb"] == config["fx_rates_to_etb"].get(t["currency"]), "transactions: inconsistent FX rate")
        require(abs(round(t["amount"]*t["fx_rate_to_etb"], 2)-t["amount_etb"]) < .005, "transactions: inconsistent ETB conversion")
        require(t["currency"] == accounts[sender]["currency"], "transactions: sender settlement currency mismatch")
        require(t["channel"] in {"Mobile Banking", "International Transfer", "Branch"} and t["status"] == "Completed", "transactions: invalid channel/status")
        cross_border = entities[owners[sender]]["country"] != entities[owners[receiver]]["country"]
        require((t["channel"] == "International Transfer") == cross_border, "transactions: inconsistent cross-border channel")
        require(t["transaction_type"] in {"Transfer", "Purchase", "Business Sale", "Owner Draw", "Family Support", "Cash Deposit", "Asset Sale", "Supplier Payment"}, "transactions: invalid type")
        require((t["channel"] == "Branch") == (t["device_id"] is None), "transactions: inconsistent device/channel")
        for aid in (sender, receiver):
            a = accounts[aid]
            require(a["opened_at"] <= t["timestamp"] and (a["closed_at"] is None or t["timestamp"] <= a["closed_at"]), "transactions: outside account lifecycle")
    require(used_accounts == set(accounts), "accounts: orphan without activity")
    used_entities, used_tx, used_rel, counts = set(), [], [], Counter()
    split_bounds = {}
    for g in truth.values():
        scenario, positive = g["scenario"], g["is_suspicious"]
        require(scenario in (*PATTERNS, *NORMAL.values()) and positive == (scenario in PATTERNS), "ground_truth: inconsistent label/scenario")
        require(g["split"] in config["splits"], "ground_truth: invalid split")
        members = set(g["member_entity_keys"])
        require(len(members) == len(g["member_entity_keys"]) and members <= entity_ids and g["entity_key"] in members, "ground_truth: invalid member entities")
        require(not members & used_entities, "ground_truth: household/entity leakage between cases or splits")
        used_entities.update(members)
        require(g["history_start"] < g["window_start"] <= g["window_end"] < g["as_of"], "ground_truth: reversed observation timestamps")
        expected_start = config["splits"][g["split"]]
        require(g["history_start"].isoformat()[:10] == expected_start, "ground_truth: inconsistent split start")
        require((g["as_of"]-g["history_start"]).days < 112, "ground_truth: observation exceeds split window")
        require(g["context_transaction_ids"] and g["evidence_transaction_ids"], "ground_truth: missing context/evidence")
        for field, lower, upper in (("context_transaction_ids", g["history_start"], g["window_start"]),
                                     ("evidence_transaction_ids", g["window_start"], g["window_end"])):
            ids = g[field]
            require(len(ids) == len(set(ids)) and set(ids) <= transaction_ids, "ground_truth: duplicate/missing transaction evidence")
            for tid in ids:
                t = tx[tid]
                require(lower <= t["timestamp"] < upper, "ground_truth: evidence outside declared window")
                require(owners[t["sender_account_id"]] in members and owners[t["receiver_account_id"]] in members, "ground_truth: unaffiliated transaction evidence")
            used_tx.extend(ids)
        ids = g["evidence_relationship_ids"]
        require(ids and len(ids) == len(set(ids)) and set(ids) <= relationship_ids, "ground_truth: missing/duplicate relationship evidence")
        for rid in ids:
            r = rel[rid]
            require(f"{r['source_type']}:{r['source_id']}" in members and f"{r['target_type']}:{r['target_id']}" in members, "ground_truth: unaffiliated relationship")
            require(r["start_time"] <= g["history_start"] and (r["end_time"] is None or r["end_time"] >= g["as_of"]), "ground_truth: inactive relationship evidence")
        used_rel.extend(ids)
        case_companies = [entities[k] for k in members if k.startswith("Company:")]
        require(len(case_companies) == 1, "ground_truth: expected one case business")
        c = case_companies[0]
        require(c["sales_period_start"] == g["window_start"] and c["sales_period_end"] == g["window_end"] and c["sales_reported_at"] <= g["as_of"], "ground_truth: declaration unavailable at cutoff or wrong period")
        if positive:
            _validate_pattern(g, tx, rel, entities, owners, c)
        else:
            _validate_control(g, tx, entities, owners, c)
        counts[(g["split"], scenario)] += 1
        split_bounds.setdefault(g["split"], []).append(g["as_of"])
    require(used_entities == set(entities), "ground_truth: unlabeled/orphan case entities")
    require(len(used_tx) == len(set(used_tx)) and set(used_tx) == set(tx), "ground_truth: overlapping or uncovered transactions")
    require(len(used_rel) == len(set(used_rel)) and set(used_rel) == set(rel), "ground_truth: overlapping or uncovered relationships")
    for split in config["splits"]:
        positive_count = round(config["cases_per_pattern_per_split"] * config.get("suspicious_fraction", 1 / config["cases_per_pattern_per_split"]))
        for pattern in PATTERNS:
            require(counts[split, pattern] == positive_count and counts[split, NORMAL[pattern]] == config["cases_per_pattern_per_split"]-positive_count, "ground_truth: wrong scenario distribution")
    require(max(split_bounds["train"]) < min(split_bounds["validation"]) and max(split_bounds["validation"]) < min(split_bounds["test"]), "ground_truth: temporal split leakage")
    return {"status": "passed", "rows": {name: len(table) for name, table in tables.items()},
            "cases": len(truth), "suspicious_cases": sum(g["is_suspicious"] for g in truth.values()),
            "scenario_counts": {f"{split}/{scenario}": count for (split, scenario), count in sorted(counts.items())}}


def _validate_pattern(g, transactions, relationships, entities, owners, company):
    evidence = sorted((transactions[i] for i in g["evidence_transaction_ids"]), key=lambda t: t["timestamp"])
    subject = g["entity_key"]
    income = entities[subject]["declared_monthly_income"]
    span = (evidence[-1]["timestamp"]-evidence[0]["timestamp"]).total_seconds()
    pattern = g["scenario"]
    if pattern == "structuring":
        valid = len(evidence) >= 5 and span <= 3600 and all(t["transaction_type"] == "Cash Deposit" and 9500 <= t["amount_etb"] < 10000 and owners[t["receiver_account_id"]] == subject for t in evidence)
    elif pattern == "velocity":
        valid = len(evidence) >= 6 and span <= 900
    elif pattern == "amount":
        valid = any(t["amount_etb"] >= 10*income and t["transaction_type"] != "Asset Sale" for t in evidence)
    elif pattern == "geography":
        a, b = evidence[:2]
        valid = a["channel"] == b["channel"] == "Branch" and abs(a["latitude"]-b["latitude"]) > 4 and (b["timestamp"]-a["timestamp"]).total_seconds() <= 900
    elif pattern in {"network", "family"}:
        valid = len(evidence) >= 6 and span <= 3600
        for cycle in (evidence[:3], evidence[3:6]):
            valid &= all(cycle[i]["receiver_account_id"] == cycle[(i+1) % 3]["sender_account_id"] for i in range(3))
        if pattern == "family":
            middle = owners[evidence[0]["receiver_account_id"]]
            valid &= any(r["relationship_type"] == "family" and {f"{r['source_type']}:{r['source_id']}", f"{r['target_type']}:{r['target_id']}"} == {subject, middle} for r in (relationships[i] for i in g["evidence_relationship_ids"]))
    elif pattern == "tax":
        sales = sum(t["amount_etb"] for t in evidence if t["transaction_type"] == "Business Sale" and owners[t["receiver_account_id"]] == subject)
        valid = sales > 5*company["declared_sales_etb"]
    else:  # theft
        prior = {transactions[i]["device_id"] for i in g["context_transaction_ids"] if owners[transactions[i]["sender_account_id"]] == subject}
        valid = span <= 1800 and sum(t["amount_etb"] for t in evidence) > 5*income and all(t["device_id"] not in prior and owners[t["sender_account_id"]] == subject for t in evidence)
    require(valid, f"ground_truth: {pattern} evidence does not support injected pattern")


def _validate_control(g, transactions, entities, owners, company):
    """A normal label must retain the benign context its scenario promises."""
    events = sorted((transactions[i] for i in g["evidence_transaction_ids"]), key=lambda t: t["timestamp"])
    span = (events[-1]["timestamp"]-events[0]["timestamp"]).total_seconds()
    scenario, subject = g["scenario"], g["entity_key"]
    income = entities[subject]["declared_monthly_income"]
    if scenario == "ordinary_deposits":
        valid = span >= 86400 and len({t["amount_etb"] for t in events}) >= 3 and all(t["transaction_type"] == "Cash Deposit" for t in events)
    elif scenario == "market_day_sales":
        valid = span >= 5*3600 and all(t["transaction_type"] == "Business Sale" for t in events)
    elif scenario == "asset_sale":
        valid = any(t["transaction_type"] == "Asset Sale" and t["amount_etb"] >= 10*income for t in events)
    elif scenario == "planned_travel":
        valid = all(t["channel"] == "Branch" for t in events) and all((b["timestamp"]-a["timestamp"]).total_seconds() >= 12*3600 for a, b in zip(events, events[1:]) if a["city"] != b["city"])
    elif scenario in {"supplier_settlement", "family_support"}:
        kind = "Supplier Payment" if scenario == "supplier_settlement" else "Family Support"
        valid = span >= 86400 and all(t["transaction_type"] == kind for t in events)
    elif scenario == "declared_trading":
        key = f"Company:{company['company_id']}"
        sales = sum(t["amount_etb"] for t in events if owners[t["receiver_account_id"]] == key and t["transaction_type"] == "Business Sale")
        valid = sales > 0 and abs(sales-company["declared_sales_etb"]) < .01
    else:  # planned_purchase
        valid = span >= 86400 and sum(t["amount_etb"] for t in events) < income and all(t["transaction_type"] == "Purchase" for t in events)
    require(valid, f"ground_truth: {scenario} evidence does not support benign control")
