"""Temporal paths and family context come from observed edges, not label membership."""
from collections import defaultdict

from .evidence import Lead


def network_leads(snapshot, features, config):
    recent = snapshot.transactions[snapshot.transactions.timestamp.ge(snapshot.window_start)]
    outgoing = defaultdict(list)
    for row in recent.sort_values(["timestamp", "transaction_id"]).to_dict("records"):
        outgoing[row["sender_account_id"]].append(row)
    owners = snapshot.owners
    family = {}
    owner_relations = {}
    for row in snapshot.relationships.itertuples(index=False):
        source, target = f"{row.source_type}:{row.source_id}", f"{row.target_type}:{row.target_id}"
        if row.relationship_type == "family" and snapshot.subject in (source, target):
            family[target if source == snapshot.subject else source] = row.relationship_id
        if row.relationship_type == "beneficial_owner" and source == snapshot.subject:
            owner_relations[target] = row.relationship_id
    cycles, comparisons, bounded = [], 0, False
    for account in sorted(features.own_accounts):
        for a in outgoing[account]:
            for b in outgoing[a["receiver_account_id"]]:
                if b["timestamp"] < a["timestamp"] or b["receiver_account_id"] in {account, a["receiver_account_id"]}:
                    continue
                if (b["timestamp"]-a["timestamp"]).total_seconds() > config["cycle_minutes"]*60:
                    break
                for c in outgoing[b["receiver_account_id"]]:
                    comparisons += 1
                    if comparisons > 20000:
                        bounded = True
                        break
                    if c["timestamp"] < b["timestamp"]:
                        continue
                    if (c["timestamp"]-a["timestamp"]).total_seconds() > config["cycle_minutes"]*60:
                        break
                    amounts = [t["amount_etb"] for t in (a, b, c)]
                    if c["receiver_account_id"] == account and max(amounts)/min(amounts)-1 <= config["cycle_amount_tolerance"]:
                        cycles.append((a, b, c))
                if bounded:
                    break
            if bounded:
                break
        if bounded:
            break
    groups = {"RAPID_CIRCULAR_FLOW": [], "FAMILY_PASS_THROUGH": []}
    for cycle in cycles:
        middle = owners[cycle[0]["receiver_account_id"]]
        code = "FAMILY_PASS_THROUGH" if middle in family else "RAPID_CIRCULAR_FLOW"
        groups[code].append(cycle)
    leads = []
    for code, paths in groups.items():
        if not paths:
            continue
        txids = sorted({t["transaction_id"] for path in paths for t in path})
        entities = sorted({owners[t["sender_account_id"]] for path in paths for t in path})
        rids = [owner_relations[k] for k in entities if k in owner_relations]
        if code == "FAMILY_PASS_THROUGH":
            rids += [family[k] for k in entities if k in family]
        leads.append(Lead(code, "network", "Rapid, approximately amount-preserving circular movement"+
                          (" through a documented relative and connected accounts; family ties alone do not assign risk." if code == "FAMILY_PASS_THROUGH" else " through connected accounts; inspect the purpose of each leg."),
                          .95, txids, sorted(set(rids)), entities,
                          {"path_count": len(paths), "maximum_minutes": config["cycle_minutes"], "amount_tolerance": config["cycle_amount_tolerance"],
                           "transaction_paths": [[t["transaction_id"] for t in path] for path in paths]}))
    return leads, {"active_family_links": len(family), "active_owned_businesses": len(owner_relations),
                   "circular_paths": len(cycles), "search_truncated": bounded, "path_comparisons": comparisons}
