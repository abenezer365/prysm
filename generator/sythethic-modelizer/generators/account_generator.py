"""
Account Generator.
"""
import numpy as np
import polars as pl
from generators.base import BaseGenerator

class AccountGenerator(BaseGenerator):
    def __init__(self, config: dict, seed: int, output_dir: str):
        super().__init__(config, seed, output_dir, "accounts")

    def generate(self, person_ids: list, company_ids: list, institution_ids: list) -> dict:
        progress = self.start_progress(len(person_ids) + len(company_ids), "Generating accounts")
        
        acc_ids = []
        owner_ids = []
        owner_types = []
        inst_ids_col = []
        
        # People accounts
        for i, pid in enumerate(person_ids):
            num_accs = self.rng.choice([1,2,3], p=[0.5, 0.3, 0.2])
            for j in range(num_accs):
                acc_ids.append(f"A_P_{pid}_{j}")
                owner_ids.append(pid)
                owner_types.append("person")
                inst_ids_col.append(self.rng.choice(institution_ids))
            
            if i % 10000 == 0:
                progress.update(10000)
                
        # Company accounts
        for i, cid in enumerate(company_ids):
            num_accs = self.rng.choice([1,2,3], p=[0.2, 0.5, 0.3])
            for j in range(num_accs):
                acc_ids.append(f"A_C_{cid}_{j}")
                owner_ids.append(cid)
                owner_types.append("company")
                inst_ids_col.append(self.rng.choice(institution_ids))
                
        progress.close()
        
        df = pl.DataFrame({
            "account_id": acc_ids,
            "owner_id": owner_ids,
            "owner_type": owner_types,
            "institution_id": inst_ids_col,
            "currency": ["ETB"] * len(acc_ids),
        })
        
        self.records_generated = len(df)
        output_path = self.write_parquet(df)
        
        return {
            "account_ids": acc_ids,
            "person_accounts": {p: [a for a, o in zip(acc_ids, owner_ids) if o == p] for p in person_ids[:100]}, # Trim for memory
            "stats": self.get_stats(),
        }

