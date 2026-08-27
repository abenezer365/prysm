"""
Employment History Generator.
"""
import numpy as np
import polars as pl
from generators.base import BaseGenerator

class EmploymentGenerator(BaseGenerator):
    def __init__(self, config: dict, seed: int, output_dir: str):
        super().__init__(config, seed, output_dir, "employment_history")

    def generate(self, person_ids: list, company_ids: list, behavior_map: dict) -> dict:
        progress = self.start_progress(len(person_ids), "Generating employment")
        
        emp_ids = []
        p_ids = []
        c_ids = []
        salaries = []
        
        # Simplified: assign 1 job per person for now to stay fast
        c_idx = 0
        
        for i, pid in enumerate(person_ids):
            beh = behavior_map.get(pid, "normal")
            
            # Skip students/unemployed mostly
            if beh == "student" and self.rng.random() > 0.2:
                continue
                
            emp_ids.append(f"E{i:06d}")
            p_ids.append(pid)
            c_ids.append(company_ids[c_idx % len(company_ids)])
            
            base_sal = 15000
            if beh == "high_income_worker":
                base_sal = 80000
            elif beh == "remote_worker" or beh == "international_worker":
                base_sal = 120000
                
            salaries.append(int(self.rng.normal(base_sal, base_sal * 0.2)))
            c_idx += 1
            
            if i % 10000 == 0:
                progress.update(10000)
                
        progress.close()
        
        df = pl.DataFrame({
            "employment_id": emp_ids,
            "person_id": p_ids,
            "company_id": c_ids,
            "monthly_salary": salaries,
        })
        
        self.records_generated = len(df)
        output_path = self.write_parquet(df)
        
        return {
            "stats": self.get_stats(),
            "employment_map": dict(zip(p_ids, salaries)) # pid -> salary
        }

