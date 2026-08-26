"""
Device Generator.
"""
import numpy as np
import polars as pl
from generators.base import BaseGenerator

class DeviceGenerator(BaseGenerator):
    def __init__(self, config: dict, seed: int, output_dir: str):
        super().__init__(config, seed, output_dir, "devices")

    def generate(self, person_ids: list) -> dict:
        progress = self.start_progress(len(person_ids), "Generating devices")
        
        dev_ids = []
        owner_ids = []
        
        for i, pid in enumerate(person_ids):
            num_devs = self.rng.choice([1,2], p=[0.7, 0.3])
            for j in range(num_devs):
                dev_ids.append(f"D_{pid}_{j}")
                owner_ids.append(pid)
                
            if i % 10000 == 0:
                progress.update(10000)
                
        progress.close()
        
        df = pl.DataFrame({
            "device_id": dev_ids,
            "owner_id": owner_ids,
            "os": self.rng.choice(["Android", "iOS", "Windows", "macOS"], size=len(dev_ids), p=[0.6, 0.15, 0.2, 0.05])
        })
        
        self.records_generated = len(df)
        output_path = self.write_parquet(df)
        
        return {
            "device_ids": dev_ids,
            "stats": self.get_stats(),
        }

