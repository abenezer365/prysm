# Task: Analyze All Raw Datasets and Create a Compact Data Manifest

## Objective

Explore the entire `raw/` directory and analyze **every dataset/file that contains structured or semi-structured data**.

Your job is to create a **small, highly-compressed data inventory and analysis document** that describes what data Prysm has, what each dataset contains, how datasets relate to each other, and any important data-quality or modeling observations.

The final document will later be provided to Prysm's AI engine as context, so **do NOT copy raw records or large samples into it**.

The goal is:

> Maximum useful information with minimum token usage.

---

# 1. Explore the Entire Raw Data Directory

Start from:

```text
raw_data/
```

Recursively inspect all relevant files and subdirectories.

You must make sure that **every dataset is analyzed**.

Look for common formats such as:

* CSV
* Parquet
* JSON
* JSONL
* Excel
* TSV
* SQL/database dumps
* other structured/tabular formats

Do not assume filenames or directory structure are complete.

If there are unsupported files, identify them separately rather than silently ignoring them.

---

# 2. Be Efficient

There may be very large datasets.

Do NOT load entire datasets into memory unnecessarily.

Use efficient inspection techniques appropriate to each format.

For example:

* Read schema/metadata first.
* For Parquet, inspect metadata, schema, row groups, column statistics where available.
* For CSV/TSV, inspect headers and stream/sample intelligently.
* For JSON/JSONL, inspect structure without loading unnecessarily large files.
* Calculate statistics using chunking or efficient dataframe operations when necessary.
* Use shell/Python utilities or temporary scripts when they significantly reduce work.
* Reuse helper scripts/functions instead of repeatedly performing expensive operations.

The objective is to analyze **all datasets**, not to exhaust tokens or RAM processing redundant information.

---

# 3. Analyze Each Dataset

For every dataset, determine the following.

### Basic information

Record:

* dataset/file name
* relative path
* file format
* approximate/exact size
* number of rows
* number of columns

### Schema

For every column, identify:

* column name
* inferred data type
* likely semantic meaning
* whether it appears to be an ID/key
* whether it appears categorical
* whether it appears numerical
* whether it appears temporal/date/time
* whether it appears textual
* whether it appears geographic/country-related
* whether it appears financial/transaction-related

Do NOT write verbose descriptions for every column.

Use compact notation.

Example:

```text
transactions.csv
rows: 1.2M
cols: 18

columns:
transaction_id [id]
sender_id [fk/person]
receiver_id [fk/person]
timestamp [datetime]
amount [numeric/currency]
currency [categorical]
country [geo]
channel [categorical]
...
```

---

# 4. Identify Important Statistical Properties

Where useful, calculate compact statistics such as:

* null/missing percentage
* unique count/cardinality
* min/max for numerical values
* approximate distributions
* number of unique categories
* date range
* duplicated IDs
* obvious invalid values
* suspicious outliers
* highly sparse columns

Do NOT include huge distributions.

Only record findings that could matter for:

* fraud detection
* AML detection
* anomaly detection
* behavioral analysis
* graph construction
* foreign-income detection
* risk scoring
* entity resolution

---

# 5. Identify Keys and Relationships

This is extremely important.

Try to determine relationships between datasets.

Look for:

* primary-key-like columns
* foreign-key-like columns
* shared IDs
* account/person relationships
* company/person relationships
* transaction relationships
* device relationships
* address relationships
* phone relationships
* payment-platform relationships
* temporal relationships
* geographic relationships

For example:

```text
persons.person_id
    ↓
accounts.person_id

accounts.account_id
    ↓
transactions.sender_account_id

transactions.receiver_account_id
    ↓
accounts.account_id

persons.person_id
    ↓
companies.owner_id
```

Use actual discovered relationships rather than inventing them.

Clearly distinguish:

```text
confirmed relationship
likely relationship
possible relationship
```

when confidence differs.

---

# 6. Think Like a Data Scientist

While analyzing the datasets, identify features that could potentially support Prysm's AI systems.

Consider whether the available data supports signals such as:

### Fraud

* unusual transaction patterns
* velocity
* amount anomalies
* account relationships
* shared identifiers
* device patterns

### AML

* transaction networks
* geographic exposure
* unusual flows
* intermediary accounts
* circular transaction patterns
* structuring/smurfing indicators

### Anomaly Detection

* behavioral baselines
* temporal anomalies
* amount anomalies
* frequency anomalies
* unusual counterparties

### Behavioral Analysis

* transaction frequency
* spending patterns
* income patterns
* account activity
* temporal behavior

### Foreign Income

* foreign transactions
* currencies
* countries
* foreign counterparties
* payment platforms
* cross-border activity

### Graph/GNN

Identify columns that could become:

```text
nodes
edges
node features
edge features
temporal features
```

Do not build the GNN yet.

Only identify the data required to build it.

---

# 7. Identify Data Quality Problems

Create a very compact section describing important problems discovered.

Examples:

```text
quality:
- transaction_id: ~0.2% duplicates
- sender_id: ~1.1% missing
- currency: 3 unexpected values
- timestamp: mixed formats
- person_id ↔ account_id relationship appears strong
```

Do not list hundreds of minor issues.

Prioritize issues that could affect:

* model training
* graph construction
* entity resolution
* risk scoring
* database migration
* feature engineering

---

# 8. Identify Redundancy and Overlap

Determine whether multiple datasets contain overlapping information.

For example:

```text
persons.csv ↔ customers.csv
possible duplicate entity information

transactions_2024.csv + transactions_2025.csv
same schema / temporal partitions

accounts.csv + bank_accounts.csv
possible semantic overlap
```

This will help us later decide how the data should be normalized in PostgreSQL.

---

# 9. Recommend a Logical Data Model

Based ONLY on the discovered datasets, provide a short proposed conceptual model.

For example:

```text
Person
 ├── Account
 │    └── Transaction
 ├── Company
 ├── Device
 ├── Address
 └── Phone

Company
 └── Transaction

Transaction
 ├── Sender
 ├── Receiver
 ├── Currency
 ├── Country
 └── PaymentPlatform
```

Only include entities that are supported by the actual raw data.

This is a conceptual recommendation, not the final PostgreSQL schema.

---

# 10. Create the Output File

Create:

```text
raw_data/DATASET_MANIFEST.md
```

The document must be **short, compact, and machine/AI friendly**.

Recommended structure:

````markdown
# Prysm Raw Data Manifest

## Overview

Datasets: X
Total rows: X
Total columns: X
Formats: CSV, Parquet, JSON
Date coverage: XXXX–XXXX

## Dataset Inventory

| Dataset | Rows | Cols | Purpose | Key |
|---|---:|---:|---|---|
| persons | ... | ... | person/entity data | person_id |
| accounts | ... | ... | financial accounts | account_id |
| transactions | ... | ... | financial activity | transaction_id |

## Compact Schemas

### persons
`person_id[id], name[text], country[geo], ...`

### accounts
`account_id[id], person_id[fk], balance[num], ...`

### transactions
`transaction_id[id], sender_account_id[fk], receiver_account_id[fk], amount[num], currency[cat], timestamp[datetime], ...`

## Relationships

```text
person → account
account → transaction
person → company
transaction → country
...
````

## Important Features

### Fraud

`amount, velocity, counterparty, timestamp, ...`

### AML

`sender, receiver, country, transaction network, ...`

### Anomaly

`amount, frequency, temporal behavior, ...`

### Behavioral

`transaction frequency, spending patterns, ...`

### Foreign Income

`country, currency, foreign counterparties, ...`

### Graph/GNN

`person, account, company, transaction, device, ...`

## Data Quality

* ...
* ...
* ...

## Redundancy / Overlap

* ...
* ...

## Modeling Notes

* ...
* ...

## Analysis Summary

A very short paragraph summarizing what the raw data provides and the most important limitations/opportunities for Prysm.

````

---

# 11. Keep the Manifest SMALL

This requirement is critical.

The manifest should ideally remain **a few KB to perhaps tens of KB**, depending on the number of datasets.

Do NOT include:

- raw records
- large examples
- huge value lists
- complete frequency tables
- complete categorical enumerations
- repeated explanations
- unnecessary prose
- duplicated schema information

Use compact notation.

Prefer:

```text
amount [numeric]
````

over:

```text
The amount column contains numerical values representing the monetary value associated with each transaction...
```

---

# 12. Accuracy Requirements

Do not hallucinate.

Every statement must come from actual inspection of the raw data.

If something is uncertain, explicitly mark it:

```text
likely
possible
uncertain
```

Do not claim a column is a foreign key merely because its name looks like one.

Use actual overlap/cardinality/value analysis where practical.

---

# 13. Verification Before Finishing

Before declaring the task complete:

1. Recursively enumerate the entire `raw_data/` directory.
2. Confirm every relevant dataset was inspected.
3. Confirm row/column counts where possible.
4. Confirm the manifest references every dataset.
5. Check that relationships are based on actual evidence.
6. Check for important missing-value problems.
7. Check for duplicate/overlapping datasets.
8. Check that the manifest is compact.
9. Validate that `DATASET_MANIFEST.md` is readable and well structured.
10. Do a final pass specifically looking for datasets accidentally skipped.

If helper scripts were created solely for analysis, they may be kept if reusable, but do not clutter the repository with unnecessary temporary files.

---

# Final Deliverable

The primary deliverable is:

```text
raw_data/DATASET_MANIFEST.md
```

The final response should briefly report:

```text
Datasets analyzed: X
Rows analyzed: X
Manifest created: raw_data/DATASET_MANIFEST.md
Important relationships found: X
Major data-quality issues: X
```

Do not paste the entire manifest into the response.

The manifest itself is the deliverable.

## Core Principle

**Inspect everything. Store almost nothing. Summarize intelligently.**

The purpose of this file is to give Prysm's AI and engineering systems a compact understanding of the raw data without repeatedly scanning millions of records or consuming unnecessary context tokens.
