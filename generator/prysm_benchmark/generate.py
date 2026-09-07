"""Small hand-designed cases with one local seeded RNG and independent households."""
from __future__ import annotations

import random
import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pyarrow as pa

from .contract import NORMAL, PATTERNS, RATIONALES, SCHEMAS, VERSION

# Approximate city centres, used as fictional branch locations (not real addresses).
PLACES = (
    ("Addis Ababa", "Addis Ababa", "Ethiopia", 9.03, 38.74),
    ("Adama", "Oromia", "Ethiopia", 8.54, 39.27),
    ("Hawassa", "Sidama", "Ethiopia", 7.05, 38.48),
    ("Bahir Dar", "Amhara", "Ethiopia", 11.59, 37.39),
    ("Mekelle", "Tigray", "Ethiopia", 13.50, 39.47),
    ("Dire Dawa", "Dire Dawa", "Ethiopia", 9.60, 41.87),
    ("Dubai", "Dubai", "United Arab Emirates", 25.20, 55.27),
)
OCCUPATIONS = (
    ("produce_trader", "Agricultural trade", 7000, 20000),
    ("shopkeeper", "Retail", 9000, 28000),
    ("tailor", "Textiles", 6000, 16000),
    ("transport_operator", "Transport", 12000, 35000),
)
REPOSITORY = Path(__file__).resolve().parents[2]


def _names(filename):
    with (REPOSITORY / "data" / "demo" / filename).open(encoding="utf-8-sig", newline="") as stream:
        return tuple(row["name"].strip() for row in csv.DictReader(stream) if row.get("name", "").strip())


NAMES = {"Female": _names("girl-names.csv"), "Male": _names("boy-names.csv")}


def geo(place):
    return dict(zip(("city", "region", "country", "latitude", "longitude"), place))


def check_config(config):
    if config.get("version") != VERSION:
        raise ValueError("Unsupported benchmark version")
    if type(config.get("seed")) is not int:
        raise ValueError("seed must be an integer")
    count = config.get("cases_per_pattern_per_split")
    if type(count) is not int or not 9 <= count <= 1000:
        raise ValueError("cases_per_pattern_per_split must be 9..1000")
    fraction = config.get("suspicious_fraction", 1 / count)
    if type(fraction) not in (int, float) or not .05 <= fraction <= .5:
        raise ValueError("suspicious_fraction must be between 0.05 and 0.5")
    if set(config.get("splits", {})) != {"train", "validation", "test"}:
        raise ValueError("splits must contain train, validation, test")
    starts = [date.fromisoformat(config["splits"][s])
              for s in ("train", "validation", "test")]
    if any((b-a).days < 112 for a, b in zip(starts, starts[1:])):
        raise ValueError("Split starts must be chronological and at least 112 days apart")
    rates = config.get("fx_rates_to_etb", {})
    if set(rates) != {"ETB", "USD"} or rates["ETB"] != 1 or not 0 < rates["USD"] < 10000:
        raise ValueError("Expected ETB=1 and a finite positive synthetic USD rate below 10000")


def generate(config):
    check_config(config)
    rng = random.Random(config["seed"])
    name_pools = {}
    for gender, first_names in NAMES.items():
        combinations = [(first, last) for first in first_names for last in NAMES["Male"] if first != last]
        rng.shuffle(combinations)
        name_pools[gender] = iter(combinations)
    rows = {name: [] for name in SCHEMAS}
    rows["institutions"] = [
        dict(institution_id="B001", institution_name="Synthetic Ethiopian Bank", institution_type="Bank", country="Ethiopia"),
        dict(institution_id="B002", institution_name="Synthetic Mobile Wallet", institution_type="Mobile Money", country="Ethiopia"),
        dict(institution_id="B003", institution_name="Synthetic Diaspora Bank", institution_type="Bank", country="United Arab Emirates"),
    ]
    case_number = 0
    for split in ("train", "validation", "test"):
        start = datetime.fromisoformat(config["splits"][split]).replace(tzinfo=timezone.utc)
        # A shuffled assignment prevents positives occupying a predictable ID range.
        positive_count = round(config["cases_per_pattern_per_split"] * config.get("suspicious_fraction", 1 / config["cases_per_pattern_per_split"]))
        assignments = [(p, n < positive_count) for p in PATTERNS
                       for n in range(config["cases_per_pattern_per_split"])]
        rng.shuffle(assignments)
        for pattern, positive in assignments:
            case_number += 1
            pid = [f"P{case_number:04d}{i}" for i in range(3)]
            cid = f"C{case_number:04d}"
            aids = [f"A{case_number:04d}{i}" for i in range(4)]
            owners = [("Person", p) for p in pid] + [("Company", cid)]
            home = rng.choices(PLACES[:6], weights=(40, 16, 12, 12, 10, 10))[0]
            relative_home = PLACES[6] if rng.random() < .25 else home
            places = [home, home, relative_home, home]
            occupation, industry, low, high = rng.choice(OCCUPATIONS)
            income = float(rng.randrange(low, high, 100))
            window = start + timedelta(days=94, hours=8)
            end = window + timedelta(days=7)
            for i, person in enumerate(pid):
                gender = rng.choice(tuple(NAMES))
                first_name, last_name = next(name_pools[gender])
                rows["persons"].append(dict(
                    person_id=person, first_name=first_name, last_name=last_name,
                    date_of_birth=datetime(rng.randint(1970, 2000), rng.randint(1, 12), rng.randint(1, 28), tzinfo=timezone.utc),
                    gender=gender, occupation=occupation if i == 0 else ("sales_assistant" if i == 1 else "service_worker"),
                    employment_status="Self-employed" if i == 0 else "Employed",
                    declared_monthly_income=income if i == 0 else (800.0 if places[i][2] != "Ethiopia" else 9000.0),
                    income_currency="USD" if places[i][2] != "Ethiopia" else "ETB",
                    created_at=start-timedelta(days=400), **geo(places[i])))
            company = dict(company_id=cid, company_name=f"Synthetic {home[0]} {industry} {case_number:04d}",
                           industry=industry, registration_date=start-timedelta(days=500),
                           declared_sales_etb=income, sales_period_start=window, sales_period_end=end,
                           sales_reported_at=end+timedelta(hours=1), **geo(home))
            rows["companies"].append(company)
            for i, (kind, owner) in enumerate(owners):
                foreign = places[i][2] != "Ethiopia"
                rows["accounts"].append(dict(account_id=aids[i], owner_type=kind, owner_id=owner,
                    institution_id="B003" if foreign else ("B002" if i == 1 else "B001"),
                    account_type="Business" if kind == "Company" else ("Wallet" if i == 1 else "Savings"),
                    currency="USD" if foreign else "ETB", opened_at=start-timedelta(days=365),
                    closed_at=None, status="Active"))
            rel_ids = []
            for source, target, relation in [(0, 2, "family"), (0, 3, "beneficial_owner"), (3, 1, "employer_employee")]:
                rid = f"R{len(rows['relationships'])+1:06d}"
                rel_ids.append(rid)
                rows["relationships"].append(dict(relationship_id=rid,
                    source_type=owners[source][0], source_id=owners[source][1],
                    target_type=owners[target][0], target_id=owners[target][1], relationship_type=relation,
                    start_time=start-timedelta(days=300), end_time=None, confidence=1.0))

            def transfer(day, sender, receiver, amount_etb, kind="Transfer", channel="Mobile Banking", place=None, new_device=False):
                currency = "USD" if places[sender][2] != "Ethiopia" else "ETB"
                rate = config["fx_rates_to_etb"][currency]
                amount = round(amount_etb / rate, 2)
                txid = f"T{len(rows['transactions'])+1:07d}"
                if places[sender][2] != places[receiver][2]:
                    channel = "International Transfer"
                rows["transactions"].append(dict(transaction_id=txid, timestamp=day,
                    sender_account_id=aids[sender], receiver_account_id=aids[receiver], amount=amount,
                    currency=currency, fx_rate_to_etb=rate, amount_etb=round(amount*rate, 2),
                    transaction_type=kind, channel=channel,
                    device_id=None if channel == "Branch" else f"D{aids[sender]}{'b' if new_device else 'a'}",
                    status="Completed", **geo(place or places[sender])))
                return txid

            context = []
            for month in range(3):
                day = start+timedelta(days=month*30)
                context.extend([
                    transfer(day+timedelta(days=2), 1, 3, income*2, "Business Sale"),
                    transfer(day+timedelta(days=4), 3, 0, income*rng.uniform(.9, 1.1), "Owner Draw"),
                    transfer(day+timedelta(days=9), 0, 1, income*rng.uniform(.15, .3), "Purchase"),
                    transfer(day+timedelta(days=18), 2, 0, income*.1, "Family Support"),
                ])
            evidence = []
            for j in range(6):
                when = window+timedelta(days=j)
                sender, receiver, amount = 0, 1, income*rng.uniform(.04, .12)
                kind, channel, place, new_device = "Purchase", "Mobile Banking", home, False
                if pattern == "structuring":
                    sender, receiver = 1, 0
                    amount = (9800+j*20) if positive else income*rng.uniform(.15, .6)
                    kind, channel = "Cash Deposit", "Branch"
                    if positive:
                        when = window+timedelta(minutes=j*12)
                elif pattern == "velocity":
                    sender, receiver, kind = 1, 0, "Business Sale"
                    when = window+timedelta(minutes=j*3) if positive else window+timedelta(hours=j*2)
                elif pattern == "amount" and j == 0:
                    sender, receiver, amount = 1, 0, income*12
                    kind = "Transfer" if positive else "Asset Sale"
                elif pattern == "geography":
                    channel, place = "Branch", PLACES[0] if j % 2 == 0 else PLACES[4]
                    if positive:
                        when = window+timedelta(minutes=j*15)
                elif pattern in {"network", "family"}:
                    middle = 1 if pattern == "network" else 2
                    route = [(0, middle), (middle, 3), (3, 0)] if positive else [(0, middle), (3, 1), (1, 3)]
                    sender, receiver = route[j % 3]
                    amount = income*.8 if positive else income*rng.uniform(.1, .3)
                    kind = "Transfer" if positive else ("Family Support" if pattern == "family" else "Supplier Payment")
                    place = places[sender]
                    if positive:
                        when = window+timedelta(minutes=j*10)
                elif pattern == "tax":
                    sender, receiver, amount, kind = 1, (0 if positive else 3), income*2, "Business Sale"
                elif pattern == "theft":
                    amount = income*2 if positive else income*.1
                    new_device = j == 0 or positive
                    kind = "Transfer" if positive else "Purchase"
                    if positive:
                        when = window+timedelta(minutes=j*5)
                evidence.append(transfer(when, sender, receiver, amount, kind, channel, place, new_device))
            if pattern == "tax" and not positive:
                company["declared_sales_etb"] = income*12
            rows["ground_truth"].append(dict(ground_truth_id=f"G{case_number:04d}",
                entity_key=f"Person:{pid[0]}", scenario=pattern if positive else NORMAL[pattern],
                is_suspicious=positive, split=split, history_start=start, window_start=window,
                window_end=end, as_of=end+timedelta(hours=2),
                member_entity_keys=[f"{kind}:{owner}" for kind, owner in owners],
                context_transaction_ids=context, evidence_transaction_ids=evidence,
                evidence_relationship_ids=rel_ids,
                rationale=RATIONALES[pattern] if positive else f"Designed benign control: {NORMAL[pattern].replace('_', ' ')}. No suspicious intent injected; unusual behavior alone is insufficient."))
    return {name: pa.Table.from_pylist(values, schema=SCHEMAS[name]) for name, values in rows.items()}
