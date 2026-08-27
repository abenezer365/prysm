"""
Company generator for the synthetic financial ecosystem.

Generates both domestic Ethiopian companies and selects foreign companies
for realistic employment and B2B transaction networks.
"""

import numpy as np
import polars as pl
from typing import Dict, Any

from generators.base import BaseGenerator
from data_sources.ethiopian_geography import get_cities_batch
from data_sources.foreign_companies import get_all_foreign_companies, get_random_suspicious_entity

class CompanyGenerator(BaseGenerator):
    """Generates the companies dataset."""

    def __init__(self, config: dict, seed: int, output_dir: str):
        super().__init__(config, seed, output_dir, "companies")

    def generate(self, **kwargs) -> Dict[str, Any]:
        target_count = self.config["population"]["companies"]
        progress = self.start_progress(target_count, "Generating companies")

        all_company_ids = []
        all_dfs = []
        generated = 0
        
        # 30% foreign / platforms / suspicious, 70% domestic
        foreign_target = int(target_count * 0.3)
        domestic_target = target_count - foreign_target
        
        # 1. Domestic Companies
        if domestic_target > 0:
            dom_ids = self.generate_ids_batch("C", 1, domestic_target)
            cities = get_cities_batch(self.rng, domestic_target)
            
            industries = ["Retail", "Import/Export", "Construction", "Agriculture", 
                          "Technology", "Consulting", "Manufacturing", "Logistics"]
            ind_weights = [0.25, 0.15, 0.15, 0.1, 0.1, 0.1, 0.1, 0.05]
            
            dom_industries = self.weighted_choice(industries, ind_weights, domestic_target)
            
            sizes = ["micro", "small", "medium", "large"]
            size_weights = [0.5, 0.3, 0.15, 0.05]
            dom_sizes = self.weighted_choice(sizes, size_weights, domestic_target)
            
            dom_names = [f"Company {i} {dom_industries[i]}" for i in range(domestic_target)]
            
            dom_df = pl.DataFrame({
                "company_id": dom_ids,
                "name": dom_names,
                "type": ["domestic"] * domestic_target,
                "industry": dom_industries.tolist(),
                "country": ["Ethiopia"] * domestic_target,
                "city": [c["name"] for c in cities],
                "size": dom_sizes.tolist(),
            })
            all_dfs.append(dom_df)
            all_company_ids.extend(dom_ids)
            progress.update(domestic_target)
            generated += domestic_target

        # 2. Foreign / Platforms
        if foreign_target > 0:
            for_ids = self.generate_ids_batch("F", 1, foreign_target)
            
            # Use real foreign companies reference mixed with some generic
            foreign_ref = get_all_foreign_companies()
            
            for_names = []
            for_industries = []
            for_countries = []
            
            for i in range(foreign_target):
                if self.rng.random() < 0.1: # 10% suspicious fictional
                    susp = get_random_suspicious_entity(self.rng)
                    for_names.append(susp["name"])
                    for_industries.append(susp["industry"])
                    for_countries.append(susp["country"])
                else:
                    ref = self.rng.choice(foreign_ref)
                    for_names.append(ref["name"] + f" {self.rng.integers(1,1000)}" if self.rng.random() < 0.5 else ref["name"])
                    for_industries.append(ref["industry"])
                    for_countries.append(ref["country"])
                    
            for_df = pl.DataFrame({
                "company_id": for_ids,
                "name": for_names,
                "type": ["foreign"] * foreign_target,
                "industry": for_industries,
                "country": for_countries,
                "city": ["Unknown"] * foreign_target,
                "size": ["large"] * foreign_target,
            })
            all_dfs.append(for_df)
            all_company_ids.extend(for_ids)
            progress.update(foreign_target)

        progress.close()
        
        full_df = pl.concat(all_dfs)
        self.records_generated = len(full_df)
        output_path = self.write_parquet(full_df)
        self.end_time = __import__("time").time()
        
        print(f"  -> Companies: {self.records_generated:,}")
        print(f"  -> Output: {output_path}")

        return {
            "company_ids": all_company_ids,
            "stats": self.get_stats(),
        }

