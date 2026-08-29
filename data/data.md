# MVP Synthetic Financial Data Generator: Implementation Prompt

## Project Overview
Build a production-ready synthetic financial ecosystem generator for an Ethiopia-focused AI financial intelligence platform. The generator will create approximately **1.75 million records** across nine interconnected datasets with realistic Ethiopian characteristics. The data will be used to train machine learning models for AML, anomaly detection, graph neural networks, and financial intelligence.


## Core Requirements

- **Total records target:** Approximately 1,755,020; see the breakdown below.
- **Primary output format:** Parquet with ZSTD compression.
- **Ethiopian realism:** Names, locations, occupations, incomes, and banking must reflect Ethiopian reality.
- **Data consistency:** All foreign keys must be valid, and relationships must form a connected graph.
- **Reproducibility:** The same seed and configuration must produce identical output.
- **Scalability:** The generator must scale to 10 million or more records without schema changes.
- **Data quality:** Include controlled missing values, duplicates, near-duplicates, and formatting inconsistencies.

### Dataset Breakdown

| Dataset        | Count    |
|----------------|----------|
| Persons        | 100,000  |
| Companies      | 10,000   |
| Accounts       | 150,000  |
| Banks          | 20       |
| Devices        | 90,000   |
| Invoices       | 200,000  |
| Transactions   | 700,000  |
| Relationships  | 500,000  |
| Ground Truth   | 5,000    |
| **Total**      | **1,755,020** |

---

## Exact Parquet Schemas

Use the following column names and logical types exactly. Nullable fields may contain null values.

### 1. `persons.parquet`
- `person_id` (string)
- `first_name` (string)
- `last_name` (string)
- `date_of_birth` (date)
- `gender` (string)
- `nationality` (string)
- `occupation` (string)
- `employment_status` (string)
- `declared_monthly_income` (int)
- `income_currency` (string)
- `city` (string)
- `region` (string)
- `country` (string)
- `phone_hash` (string, nullable)
- `address_hash` (string, nullable)
- `created_at` (datetime)

### 2. `companies.parquet`
- `company_id` (string)
- `company_name` (string)
- `country` (string)
- `industry` (string)
- `company_size` (string)
- `employee_count` (int)
- `annual_revenue` (int)
- `registration_date` (date)
- `city` (string)
- `region` (string)
- `status` (string)

### 3. `accounts.parquet`
- `account_id` (string)
- `owner_id` (string)
- `owner_type` (string: `Person` or `Company`)
- `institution_id` (string)
- `account_type` (string)
- `currency` (string)
- `opened_at` (date)
- `closed_at` (date, nullable)
- `status` (string)
- `average_balance` (int)
- `city` (string)
- `country` (string)

### 4. `banks.parquet`
- `institution_id` (string)
- `institution_name` (string)
- `institution_type` (string)
- `country` (string)
- `supported_currencies` (list<string>)

### 5. `devices.parquet`
- `device_id` (string)
- `device_type` (string)
- `os` (string)
- `browser` (string, nullable)
- `device_fingerprint` (string)
- `first_seen` (datetime)
- `last_seen` (datetime)
- `city` (string)
- `country` (string)

### 6. `invoices.parquet`
- `invoice_id` (string)
- `issuer_id` (string)
- `issuer_type` (string)
- `recipient_id` (string)
- `recipient_type` (string)
- `issue_date` (date)
- `due_date` (date)
- `amount` (int)
- `currency` (string)
- `service_type` (string)
- `status` (string)

### 7. `transactions.parquet`
- `transaction_id` (string)
- `timestamp` (datetime)
- `sender_account_id` (string)
- `receiver_account_id` (string)
- `amount` (int)
- `currency` (string)
- `amount_etb` (int)  # Converted to ETB.
- `transaction_type` (string)
- `channel` (string)
- `device_id` (string, nullable)
- `city` (string)
- `country` (string)
- `ip_hash` (string, nullable)
- `reference_id` (string, nullable)
- `invoice_id` (string, nullable)
- `status` (string)

### 8. `relationships.parquet`
- `relationship_id` (string)
- `source_type` (string)
- `source_id` (string)
- `relationship_type` (string)
- `target_type` (string)
- `target_id` (string)
- `start_time` (datetime)
- `end_time` (datetime, nullable)
- `confidence` (float)

### 9. `ground_truth.parquet`
- `ground_truth_id` (string)
- `entity_type` (string)
- `entity_id` (string)
- `behavior_type` (string)
- `risk_pattern` (string)
- `is_anomalous` (boolean)
- `severity` (string)
- `pattern_start` (date)
- `pattern_end` (date, nullable)
- `related_entity_ids` (list<string>, nullable)

---

## Ethiopian Realism Requirements

### Names
- Load Ethiopian male and female first names from **`boy-names.csv`** and **`girl-names.csv`** provided at runtime.
- Generate the surname from the father's first name, following the Ethiopian naming convention; `last_name` must be a randomly selected male first name.
- Use an approximate gender distribution of 48% male and 52% female.

### Cities & Regions
Use a weighted city distribution with Addis Ababa at approximately 35% and the remaining cities defined in the configuration. Include all Ethiopian regions and keep the city-to-region mapping consistent.

### Occupations & Incomes
Use realistic occupation distributions with salary ranges tied to occupation, experience, and city. Incomes should reflect the Ethiopian market and be expressed in ETB unless the configuration explicitly specifies another currency. Define the detailed distribution in the configuration.

### Banks
- 70% Ethiopian banks, such as Commercial Bank of Ethiopia and Dashen Bank.
- 30% international or foreign banks, such as Swiss and UAE institutions, for foreign-income scenarios.

### Companies
- 70% international technology or startup companies with synthetic names.
- 30% local Ethiopian companies with synthetic names.

### Currencies
- Use ETB for the majority of records, with USD and EUR for foreign income and transactions.

---

## Algorithms and Implementation Details

### Person Generation
```python
from datetime import datetime, timedelta

import hashlib

import numpy as np
import pandas as pd

def generate_persons(count, seed, config):
    np.random.seed(seed)
    male_names = load_csv('boy-names.csv')['name'].tolist()
    female_names = load_csv('girl-names.csv')['name'].tolist()
    
    # Occupation distribution; define the complete distribution in config.
    occupations = {
        'software_engineer': 0.12, 'teacher': 0.08, 'doctor': 0.03,
        'business_owner': 0.08, 'freelancer': 0.12, 'student': 0.15,
        # ... complete list in config
    }
    # Income ranges per occupation: minimum, maximum, and currency.
    income_by_occ = {
        'software_engineer': (15000, 60000, 'ETB'),
        # ... complete mapping in config
    }
    city_weights = {...}  # Define the distribution in config.
    
    persons = []
    for i in range(count):
        gender = 'M' if np.random.random() < 0.48 else 'F'
        first = male_names[np.random.randint(len(male_names))] if gender == 'M' else female_names[np.random.randint(len(female_names))]
        surname = male_names[np.random.randint(len(male_names))]  # Father's name.
        occupation = np.random.choice(list(occupations.keys()), p=list(occupations.values()))
        min_inc, max_inc, curr = income_by_occ[occupation]
        # Add experience variation.
        income = int(np.random.lognormal(mean=np.log(min_inc + (max_inc-min_inc)*0.4), sigma=0.5))
        income = max(2000, min(150000, income))
        city = np.random.choice(list(city_weights.keys()), p=list(city_weights.values()))
        region = get_region(city)
        # Generate deterministic hashes from the generated attributes.
        phone_hash = hashlib.sha256(f"{first}{surname}{city}".encode()).hexdigest()[:16]
        address_hash = hashlib.sha256(f"{first}{surname}{city}{region}".encode()).hexdigest()[:16]
        # Use a configured reference date so generation remains reproducible.
        age = np.random.randint(18, 65)
        reference_date = config.get('reference_date', '2026-01-01')
        reference_datetime = datetime.fromisoformat(reference_date)
        dob = reference_datetime - timedelta(days=age * 365 + np.random.randint(0, 365))
        created_at = reference_datetime - timedelta(days=np.random.randint(0, 365 * 5))
        persons.append({
            'person_id': f"P{str(i+1).zfill(6)}",
            'first_name': first,
            'last_name': surname,
            'date_of_birth': dob.date(),
            'gender': gender,
            'nationality': 'Ethiopian' if np.random.random() < 0.92 else 'Other',
            'occupation': occupation,
            'employment_status': determine_employment_status(occupation, age),
            'declared_monthly_income': income,
            'income_currency': curr,
            'city': city,
            'region': region,
            'country': 'Ethiopia',
            'phone_hash': phone_hash if np.random.random() > 0.05 else None,
            'address_hash': address_hash if np.random.random() > 0.08 else None,
            'created_at': created_at
        })
    return pd.DataFrame(persons)

```


## Data Quality and Corruption

### Missing Values
Add column-specific missingness; missingness must not be uniform:

- `phone_hash`: 5%
- `address_hash`: 8%
- `browser`: 3%
- `invoice_id`: 15% (not all transactions have invoices)
- `device_id`: 5%
- `closed_at`: 70% null (active accounts)
- `employment_status`: 3%

### Duplicates and Near-Duplicates
Create approximately 1% duplicate records with slight variations, such as name case and formatting, to challenge entity resolution.

### Formatting Inconsistencies
Randomly apply case changes, extra spaces, and phone-number variations.

## Validation and Reports

After generation, automatically produce the following reports:

- `generation_report.json`: counts, runtime, seed, and the configuration used.
- `realism_report.json`: Ethiopian content ratio, income distribution, temporal spread, and relationship statistics.
- `validation_report.json`: foreign-key integrity, missing-value statistics, duplicate rates, and schema validation.

Validation must check the following:

- All referenced IDs exist.
- No orphan accounts, devices, or other generated entities.
- Transaction amounts are positive.
- Dates are within the configured date range.
- Relationship types are valid.

## Reproducibility and Scalability

- Seed support: `--seed 42` must yield identical output for the same configuration and reference date.
- Scaling: The generator must be configuration-driven, with the schema unchanged for larger counts.
- Batch generation: Write in chunks to avoid memory overflow; use Polars streaming where appropriate.

## Implementation Stack

- Python 3.9 or later
- Polars as the primary engine, or PyArrow
- NumPy for distributions
- Faker, optional for some fields
- PyYAML for configuration
- Click for the CLI
- Pydantic for schema validation

## Suggested Folder Structure

Change this structure if the implementation requires it.

```text
synthetic_financial_generator/
├── src/
│   ├── generators/          # One per dataset
│   ├── data_quality/        # Missing values, duplicates, and corruption
│   ├── validation/          # Integrity checks and reports
│   └── utils/               # Hashing, distributions, and Ethiopian data
├── data/
│   ├── raw/                 # Final Parquet files
│   └── samples/             # Optional CSV samples
├── reports/                 # JSON reports
├── names_data/              # boy-names.csv, girl-names.csv
├── config.yaml
├── main.py                  # Entry point
└── requirements.txt
```