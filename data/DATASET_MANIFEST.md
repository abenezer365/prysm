# Prysm Raw Data Manifest

## Overview

- Datasets: 9 Parquet files; unsupported structured formats: none found.
- Total rows: 1,756,020; total columns: 99; raw size: 57.6 MB.
- Date coverage: 2022-01-01 to 2025-12-31 (where temporal fields exist).
- Values are synthetic-looking and mostly Ethiopia-focused: person and transaction `country` are Ethiopia; currencies are ETB, AED, CHF, EUR, GBP, USD.

## Dataset Inventory

| Dataset | Rows | Cols | Size | Purpose | Key |
|---|---:|---:|---:|---|---|
| accounts.parquet | 150,000 | 12 | 1.96 MB | person/company financial accounts | `account_id` |
| banks.parquet | 20 | 5 | 2 KB | financial institutions | `institution_id` |
| companies.parquet | 10,000 | 11 | 192 KB | company/entity master data | `company_id` |
| devices.parquet | 90,000 | 9 | 3.56 MB | device fingerprints and location | `device_id` |
| ground_truth.parquet | 5,000 | 10 | 145 KB | labeled risk/anomaly patterns | `ground_truth_id` |
| invoices.parquet | 200,000 | 11 | 3.48 MB | person/company invoices | `invoice_id` |
| persons.parquet | 101,000 | 16 | 3.92 MB | person/entity master data | `person_id` (100,000 unique) |
| relationships.parquet | 500,000 | 9 | 12.80 MB | typed, temporal entity graph edges | `relationship_id` |
| transactions.parquet | 700,000 | 16 | 31.53 MB | account-to-account financial activity | `transaction_id` |

## Compact Schemas

### accounts
`account_id[id], owner_id[id/fk Person|Company], owner_type[cat], institution_id[fk Bank], account_type[cat], currency[cat], opened_at[date], closed_at[date], status[cat], average_balance[numeric], city[geo], country[geo]`

### banks
`institution_id[id], institution_name[text], institution_type[cat], country[geo], supported_currencies[list/currency]`

### companies
`company_id[id], company_name[text], country[geo], industry[cat], company_size[cat], employee_count[numeric], annual_revenue[numeric/currency-unspecified], registration_date[date], city[geo], region[geo], status[cat]`

### devices
`device_id[id], device_type[cat], os[cat], browser[cat], device_fingerprint[id-like], first_seen[datetime], last_seen[datetime], city[geo], country[geo]`

### ground_truth
`ground_truth_id[id], entity_type[cat], entity_id[fk Person|Account|Company], behavior_type[cat], risk_pattern[cat], is_anomalous[bool], severity[cat], pattern_start[date], pattern_end[date], related_entity_ids[list/id]`

### invoices
`invoice_id[id], issuer_id[fk Person|Company], issuer_type[cat], recipient_id[fk Person|Company], recipient_type[cat], issue_date[date], due_date[date], amount[numeric/currency], currency[cat], service_type[cat], status[cat]`

### persons
`person_id[id], first_name[text], last_name[text], date_of_birth[date], gender[cat], nationality[cat], occupation[cat], employment_status[cat], declared_monthly_income[numeric/currency], income_currency[cat], city[geo], region[geo], country[geo], phone_hash[id-like], address_hash[id-like], created_at[datetime]`

### relationships
`relationship_id[id], source_type[cat], source_id[fk], relationship_type[cat], target_type[cat], target_id[fk], start_time[datetime], end_time[datetime], confidence[numeric 0.3-1.0]`

### transactions
`transaction_id[id], timestamp[datetime], sender_account_id[fk Account], receiver_account_id[fk Account], amount[numeric/currency], currency[cat], amount_etb[numeric/ETB], transaction_type[cat], channel[cat], device_id[fk Device], city[geo], country[geo], ip_hash[id-like], reference_id[id-like], invoice_id[fk Invoice], status[cat]`

## Relationships

**Confirmed by value overlap/cardinality:**

```text
persons.person_id / companies.company_id -> accounts.owner_id (typed by owner_type)
banks.institution_id -> accounts.institution_id (all 20 bank IDs occur)
accounts.account_id -> transactions.sender_account_id and receiver_account_id
devices.device_id -> transactions.device_id (89,927 distinct IDs overlap)
invoices.invoice_id -> transactions.invoice_id (183,967 distinct IDs overlap)
```

**Likely / typed but not fully referentially constrained:**

```text
persons/company.company_id -> invoices.issuer_id and recipient_id (use issuer_type/recipient_type)
Person|Account|Company -> ground_truth.entity_id (use entity_type)
Person|Account|Company -> relationships.source_id / target_id (use source_type/target_type)
```

Relationships contain 10 edge types including `employer_employee`, `family`, `joint_account`, `shared_address`, `shared_device`, `business_partner`, and `supplier_customer`; they are the primary general-purpose graph source.

## Important Features

- **Fraud:** transaction amount/ETB amount, velocity, status, channel, device/IP/address sharing, invoice linkage, rapid movement and false-invoice labels.
- **AML:** sender/receiver network, layering, structuring, smurfing, round-tripping, shell-company labels, cross-currency activity, geography and temporal edges.
- **Anomaly:** labeled `is_anomalous`, severity/risk pattern, amount outliers, frequency/velocity, counterparties and time windows.
- **Behavioral:** account type/status, balance, transaction type/channel, income, occupation and temporal activity.
- **Foreign income:** currency and `amount_etb`, institution/company/counterparty country; current person/transaction country fields contain only Ethiopia.
- **Graph/GNN:** nodes = Person, Company, Account, Bank, Device, Invoice; edges = transactions, relationships, ownership, institution, invoice party links; features = amount, currency, type, channel, confidence, location, time and labels.

## Data Quality

- `persons.person_id`: 101,000 rows but 100,000 unique; 1,000 duplicate rows/IDs require deduplication or lineage handling.
- `accounts.closed_at`: 136,559 null (91.04%), consistent with open accounts but must not be treated as random missingness.
- `transactions`: `invoice_id` 27.82% null, `reference_id` 70.05% null, `ip_hash` 14.50% null, `device_id` 9.77% null.
- `persons`: `employment_status` 6.04%, `phone_hash` 9.77%, `address_hash` 15.28% null; this weakens entity resolution/shared-identifier features.
- `devices.browser` 5.78% null; `ground_truth.pattern_end` 41.28% null; `relationships.end_time` 75.00% null, likely open-ended edges.
- `ground_truth.entity_id`, relationship endpoints, and invoice party IDs are polymorphic; type columns are required during joins. `ground_truth.entity_id` is not globally unique (40 duplicates).
- Numeric ranges: transaction `amount` 50-5,000,000 and `amount_etb` 50-325,000,000; account balance 103-2,541,208; invoice amount 500-10,000,000. Validate currency conversion and outliers before modeling.

## Redundancy / Overlap

- No same-schema temporal partitions or obvious duplicate files found.
- `relationships` overlaps entity/master concepts in accounts, persons and companies, but adds typed temporal edges and confidence; retain as graph evidence rather than treating it as a replacement master table.
- `ground_truth` references the same entity domains as master data and is a label table, not a duplicate entity source.

## Modeling Notes

- Normalize Person, Company, Bank, Account, Device and Invoice as entity domains; keep typed polymorphic links explicit or resolve to bridge tables.
- Preserve transaction and relationship timestamps for temporal graphs, velocity, windowed features and open-ended intervals.
- Deduplicate persons before foreign-key enforcement; validate all transaction, invoice and device references against master keys.
- Treat hashes as privacy-preserving join keys, not recoverable identity fields. Country coverage is insufficient for strong foreign-income geography without more international data.

## Analysis Summary

The raw data supports a substantial temporal financial graph: 700k transactions, 500k typed relationships, 150k accounts, entity masters, devices, invoices and 5k risk labels. It is suitable for fraud, AML, anomaly and behavioral feature engineering, but polymorphic IDs, duplicate persons, sparse identifiers and Ethiopia-only observed transaction/person geography require validation and careful normalization first.