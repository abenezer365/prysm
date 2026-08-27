"""
Financial Institution Generator.
"""
import polars as pl
from generators.base import BaseGenerator
from data_sources.financial_institutions import get_all_institutions

class InstitutionGenerator(BaseGenerator):
    def __init__(self, config: dict, seed: int, output_dir: str):
        super().__init__(config, seed, output_dir, "institutions")

    def generate(self, **kwargs) -> dict:
        insts = get_all_institutions()
        
        df = pl.DataFrame({
            "institution_id": [i["id"] for i in insts],
            "name": [i["name"] for i in insts],
            "type": [i["type"] for i in insts],
            "branch_count": [i["branch_count"] for i in insts],
        })
        
        self.records_generated = len(df)
        output_path = self.write_parquet(df)
        self.end_time = __import__("time").time()
        
        return {
            "institution_ids": [i["id"] for i in insts],
            "stats": self.get_stats()
        }

