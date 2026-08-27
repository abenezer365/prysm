"""
Transaction Generator.
"""
import numpy as np
import polars as pl
from generators.base import BaseGenerator

class TransactionGenerator(BaseGenerator):
    def __init__(self, config: dict, seed: int, output_dir: str):
        super().__init__(config, seed, output_dir, "transactions")

    def generate(self, account_ids: list, suspicious_ids: set) -> dict:
        target_count = self.config["population"]["transactions"]
        progress = self.start_progress(target_count, "Generating transactions")
        
        all_txn_ids = []
        batch_size = self.config["generation"].get("transaction_batch_size", 50000)
        generated = 0
        
        acc_array = np.array(account_ids)
        
        while generated < target_count:
            batch = min(batch_size, target_count - generated)
            
            sender_idx = self.rng.integers(0, len(acc_array), size=batch)
            receiver_idx = self.rng.integers(0, len(acc_array), size=batch)
            
            # Avoid self transfers
            same_idx = sender_idx == receiver_idx
            receiver_idx[same_idx] = (receiver_idx[same_idx] + 1) % len(acc_array)
            
            amounts = self.log_normal_amounts(500, 1.5, batch, min_val=10.0, max_val=1000000.0)
            
            dates = self.random_dates("2024-01-01", "2026-06-30", batch)
            
            txn_ids = self.generate_ids_batch("T", generated, batch)
            
            df = pl.DataFrame({
                "txn_id": txn_ids,
                "sender_account_id": acc_array[sender_idx],
                "receiver_account_id": acc_array[receiver_idx],
                "amount": amounts,
                "currency": ["ETB"] * batch,
                "date": dates,
                "year": [str(d).split("-")[0] for d in dates]
            })
            
            # Write partitioned by year
            self.write_parquet_partitioned_batch(df, partition_cols=["year"])
            
            all_txn_ids.extend(txn_ids)
            generated += batch
            progress.update(batch)
            
        progress.close()
        self.end_time = __import__("time").time()
        
        return {
            "stats": self.get_stats()
        }

