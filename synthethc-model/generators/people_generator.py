"""
People generator for the synthetic financial ecosystem.

Generates realistic synthetic Ethiopian people with:
- Ethiopian names from diverse language groups
- Population-weighted city assignments
- Realistic age and gender distributions
- Behavior archetypes (normal, remote_worker, freelancer, etc.)
- Suspicious flags (hidden in truth table)
"""

import numpy as np
import polars as pl

from generators.base import BaseGenerator
from data_sources.ethiopian_names import (
    generate_names_batch,
    LANGUAGE_GROUP_WEIGHTS,
)
from data_sources.ethiopian_geography import get_cities_batch


class PeopleGenerator(BaseGenerator):
    """Generates the people dataset with realistic Ethiopian demographics."""

    def __init__(self, config: dict, seed: int, output_dir: str):
        super().__init__(config, seed, output_dir, "people")

    def generate(self, **kwargs) -> dict:
        """Generate the people dataset.
        
        Returns:
            dict with:
                - person_ids: list of generated person IDs
                - behavior_map: dict mapping person_id -> behavior_type
                - suspicious_ids: set of person IDs flagged as suspicious
                - stats: generation statistics
        """
        target_count = self.config["population"]["people"]
        demographics = self.config.get("demographics", {})
        behaviors = self.config.get("behaviors", {})
        risk_patterns = self.config.get("risk_patterns", {})

        progress = self.start_progress(target_count, "Generating people")

        all_person_ids = []
        behavior_map = {}
        suspicious_ids = set()
        suspicious_patterns = {}
        truth_records = []

        # Calculate total suspicious rate
        total_suspicious_rate = sum(risk_patterns.values())

        # Process in batches
        generated = 0
        batch_num = 0
        all_dfs = []

        while generated < target_count:
            batch_count = min(self.batch_size, target_count - generated)
            batch_start = generated
            
            # Generate IDs
            person_ids = self.generate_ids_batch("P", batch_start, batch_count)

            # Generate names with language group diversity
            names_data = generate_names_batch(self.rng, batch_count)

            # Generate demographics
            male_ratio = demographics.get("male_ratio", 0.52)
            genders = self.rng.choice(
                ["male", "female"],
                size=batch_count,
                p=[male_ratio, 1 - male_ratio],
            )
            
            # Override names based on actual gender
            for i in range(batch_count):
                if genders[i] != names_data[i]["gender"]:
                    names_data[i] = generate_names_batch(self.rng, 1)[0]
                    names_data[i]["gender"] = genders[i]

            # Generate ages using normal distribution
            age_config = demographics.get("age_distribution", {})
            ages = self.rng.normal(
                loc=age_config.get("mean", 32),
                scale=age_config.get("std", 12),
                size=batch_count,
            ).astype(int)
            ages = np.clip(ages, age_config.get("min", 18), age_config.get("max", 75))
            
            # Calculate birth years
            birth_years = 2026 - ages
            birth_months = self.rng.integers(1, 13, size=batch_count)
            birth_days = self.rng.integers(1, 29, size=batch_count)
            dobs = [
                f"{birth_years[i]}-{birth_months[i]:02d}-{birth_days[i]:02d}"
                for i in range(batch_count)
            ]

            # Generate cities (population-weighted)
            cities = get_cities_batch(self.rng, batch_count)
            city_names = [c["name"] for c in cities]
            region_names = [c["region"] for c in cities]

            # Generate behavior types
            behavior_types = list(behaviors.keys())
            behavior_weights = list(behaviors.values())
            assigned_behaviors = self.weighted_choice(
                behavior_types, behavior_weights, batch_count
            )

            # Determine suspicious flags
            is_suspicious = self.rng.random(batch_count) < total_suspicious_rate
            
            # Assign specific suspicious patterns
            pattern_types = list(risk_patterns.keys())
            pattern_weights = list(risk_patterns.values())
            pattern_weights_norm = np.array(pattern_weights) / sum(pattern_weights)
            
            for i in range(batch_count):
                pid = person_ids[i]
                behavior_map[pid] = assigned_behaviors[i]
                
                if is_suspicious[i]:
                    suspicious_ids.add(pid)
                    pattern = self.rng.choice(pattern_types, p=pattern_weights_norm)
                    suspicious_patterns[pid] = pattern
                    truth_records.append({
                        "entity_id": pid,
                        "entity_type": "person",
                        "pattern_type": pattern,
                        "severity": self.rng.choice(
                            ["low", "medium", "high"],
                            p=[0.3, 0.5, 0.2],
                        ),
                    })

            # Generate phone numbers
            phones = self.generate_phone_number(batch_count)

            # Generate emails
            emails = [
                self.generate_email(
                    names_data[i]["first_name"],
                    names_data[i]["father_name"],
                    batch_start + i,
                )
                for i in range(batch_count)
            ]

            # Nationality
            eth_ratio = demographics.get("ethiopia_ratio", 0.92)
            nationalities = self.rng.choice(
                ["Ethiopian", "Kenyan", "Eritrean", "Somali", "Sudanese",
                 "Djiboutian", "American", "British", "Indian", "Chinese"],
                size=batch_count,
                p=[eth_ratio, 0.015, 0.015, 0.01, 0.01,
                   0.005, 0.01, 0.005, 0.005, 0.005],
            )

            # Build DataFrame
            df = pl.DataFrame({
                "person_id": person_ids,
                "first_name": [n["first_name"] for n in names_data],
                "father_name": [n["father_name"] for n in names_data],
                "grandfather_name": [n["grandfather_name"] for n in names_data],
                "gender": genders.tolist(),
                "date_of_birth": dobs,
                "city": city_names,
                "region": region_names,
                "phone": phones,
                "email": emails,
                "nationality": nationalities.tolist(),
                "language_group": [n["language_group"] for n in names_data],
                "behavior_type": assigned_behaviors.tolist(),
            })

            all_dfs.append(df)
            all_person_ids.extend(person_ids)
            generated += batch_count
            progress.update(batch_count)
            batch_num += 1

        progress.close()

        # Concatenate all batches and write
        full_df = pl.concat(all_dfs)
        self.records_generated = len(full_df)
        output_path = self.write_parquet(full_df)
        self.end_time = __import__("time").time()

        # Write truth data for suspicious persons
        if truth_records:
            truth_df = pl.DataFrame(truth_records)
            truth_dir = self.output_dir.parent / "truth"
            truth_dir.mkdir(parents=True, exist_ok=True)
            truth_df.write_parquet(
                str(truth_dir / "suspicious_persons.parquet"),
                compression=self.compression,
            )

        print(f"  -> People: {self.records_generated:,} records")
        print(f"  -> Suspicious: {len(suspicious_ids):,} ({100*len(suspicious_ids)/self.records_generated:.1f}%)")
        print(f"  -> Output: {output_path}")

        return {
            "person_ids": all_person_ids,
            "behavior_map": behavior_map,
            "suspicious_ids": suspicious_ids,
            "suspicious_patterns": suspicious_patterns,
            "stats": self.get_stats(),
        }
