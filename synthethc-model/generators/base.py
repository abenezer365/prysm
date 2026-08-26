"""
Base generator class for the synthetic financial data generator.

Provides common functionality for all generators:
- Seeded random number generation
- Batch processing and Parquet output
- Progress tracking
- ID generation
"""

import os
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np
import polars as pl
import pyarrow as pa
import pyarrow.parquet as pq
from tqdm import tqdm


class BaseGenerator:
    """Base class for all data generators.
    
    Manages seeded RNG, batch writing to Parquet, and progress tracking.
    Subclasses implement generate() to produce their specific dataset.
    """

    def __init__(
        self,
        config: dict,
        seed: int,
        output_dir: str,
        phase_name: str,
    ):
        """Initialize the base generator.
        
        Args:
            config: Full configuration dictionary
            seed: Master seed for reproducibility
            output_dir: Root output directory (e.g., data/raw)
            phase_name: Name of this generation phase (e.g., 'people')
        """
        self.config = config
        self.seed = seed
        self.phase_name = phase_name
        self.output_dir = Path(output_dir)
        self.phase_dir = self.output_dir / phase_name
        self.phase_dir.mkdir(parents=True, exist_ok=True)

        # Create a seeded RNG for this phase
        # Use a derived seed so each phase is independent but reproducible
        phase_hash = hash(phase_name) % (2**31)
        self.rng = np.random.default_rng(seed + phase_hash)

        # Generation settings
        self.batch_size = config.get("generation", {}).get("batch_size", 10000)
        self.compression = config.get("generation", {}).get("parquet_compression", "snappy")

        # Tracking
        self.records_generated = 0
        self.start_time = None
        self.end_time = None
        self._parquet_writer = None
        self._parquet_schema = None

    def generate(self, **kwargs) -> dict:
        """Main generation method. Subclasses must implement this.
        
        Returns:
            dict with generation statistics and any lookup data needed
            by downstream generators.
        """
        raise NotImplementedError("Subclasses must implement generate()")

    def generate_id(self, prefix: str, index: int) -> str:
        """Generate a deterministic ID with a prefix.
        
        Args:
            prefix: ID prefix (e.g., 'P' for person, 'C' for company)
            index: Sequential index
            
        Returns:
            Formatted ID string (e.g., 'P000001')
        """
        return f"{prefix}{index:06d}"

    def generate_ids_batch(self, prefix: str, start: int, count: int) -> list[str]:
        """Generate a batch of sequential IDs.
        
        Args:
            prefix: ID prefix
            start: Starting index
            count: Number of IDs to generate
            
        Returns:
            List of ID strings
        """
        return [f"{prefix}{i:06d}" for i in range(start, start + count)]

    def write_parquet(
        self,
        df: pl.DataFrame,
        filename: str = None,
        partition_cols: list[str] = None,
    ) -> str:
        """Write a Polars DataFrame to Parquet.
        
        Args:
            df: DataFrame to write
            filename: Output filename (without extension). If None, uses phase_name.
            partition_cols: Columns to partition by (e.g., ['year'])
            
        Returns:
            Path to the written file/directory
        """
        if filename is None:
            filename = self.phase_name

        if partition_cols:
            # Write partitioned dataset using PyArrow
            output_path = str(self.phase_dir)
            table = df.to_arrow()
            pq.write_to_dataset(
                table,
                root_path=output_path,
                partition_cols=partition_cols,
                compression=self.compression,
            )
            return output_path
        else:
            output_path = str(self.phase_dir / f"{filename}.parquet")
            df.write_parquet(output_path, compression=self.compression)
            return output_path

    def append_parquet(self, df: pl.DataFrame, filename: str = None):
        """Append a batch to a Parquet file using streaming writer.
        
        Uses PyArrow's ParquetWriter for incremental writes.
        Call finalize_parquet() when done.
        
        Args:
            df: DataFrame batch to append
            filename: Output filename
        """
        if filename is None:
            filename = self.phase_name

        table = df.to_arrow()

        if self._parquet_writer is None:
            output_path = str(self.phase_dir / f"{filename}.parquet")
            self._parquet_schema = table.schema
            self._parquet_writer = pq.ParquetWriter(
                output_path,
                schema=self._parquet_schema,
                compression=self.compression,
            )

        self._parquet_writer.write_table(table)
        self.records_generated += len(df)

    def finalize_parquet(self):
        """Close the streaming Parquet writer."""
        if self._parquet_writer is not None:
            self._parquet_writer.close()
            self._parquet_writer = None
            self._parquet_schema = None

    def write_parquet_partitioned_batch(
        self,
        df: pl.DataFrame,
        partition_cols: list[str],
    ):
        """Write a batch to a partitioned Parquet dataset.
        
        Each batch is appended to the appropriate partition directory.
        
        Args:
            df: DataFrame batch
            partition_cols: Columns to partition by
        """
        table = df.to_arrow()
        pq.write_to_dataset(
            table,
            root_path=str(self.phase_dir),
            partition_cols=partition_cols,
            compression=self.compression,
            existing_data_behavior="overwrite_or_ignore",
        )
        self.records_generated += len(df)

    def start_progress(self, total: int, desc: str = None) -> tqdm:
        """Start a progress bar.
        
        Args:
            total: Total expected count
            desc: Description label
            
        Returns:
            tqdm progress bar instance
        """
        self.start_time = time.time()
        if desc is None:
            desc = f"Generating {self.phase_name}"
        return tqdm(total=total, desc=desc, unit="records")

    def get_elapsed_time(self) -> float:
        """Get elapsed time since generation started."""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def get_stats(self) -> dict:
        """Get generation statistics.
        
        Returns:
            Dict with records_generated, elapsed_time, records_per_second
        """
        elapsed = self.get_elapsed_time()
        return {
            "phase": self.phase_name,
            "records_generated": self.records_generated,
            "elapsed_seconds": round(elapsed, 2),
            "records_per_second": round(self.records_generated / max(elapsed, 0.001), 0),
        }

    def random_dates(
        self,
        start_date: str,
        end_date: str,
        count: int,
    ) -> np.ndarray:
        """Generate random dates uniformly distributed between start and end.
        
        Args:
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            count: Number of dates to generate
            
        Returns:
            NumPy array of date strings
        """
        start = np.datetime64(start_date)
        end = np.datetime64(end_date)
        days_range = (end - start).astype(int)
        random_days = self.rng.integers(0, max(days_range, 1), size=count)
        dates = start + random_days.astype("timedelta64[D]")
        return dates

    def random_timestamps(
        self,
        start_date: str,
        end_date: str,
        count: int,
        business_hours_bias: float = 0.0,
    ) -> np.ndarray:
        """Generate random timestamps with optional business hours bias.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            count: Number of timestamps
            business_hours_bias: 0.0 = uniform, 1.0 = fully business hours (8-18)
            
        Returns:
            NumPy array of datetime64[s]
        """
        start = np.datetime64(start_date)
        end = np.datetime64(end_date)
        total_seconds = int((end - start) / np.timedelta64(1, "s"))

        random_seconds = self.rng.integers(0, max(total_seconds, 1), size=count)
        timestamps = start + random_seconds.astype("timedelta64[s]")

        if business_hours_bias > 0:
            # Adjust hours: reject and resample non-business-hour timestamps
            # with probability proportional to bias
            hours = (random_seconds % 86400) // 3600
            is_business = (hours >= 8) & (hours < 18)
            resample_mask = ~is_business & (
                self.rng.random(count) < business_hours_bias
            )
            if resample_mask.any():
                n_resample = resample_mask.sum()
                new_hours = self.rng.integers(8, 18, size=n_resample)
                new_minutes = self.rng.integers(0, 60, size=n_resample)
                new_secs = self.rng.integers(0, 60, size=n_resample)
                day_offsets = random_seconds[resample_mask] - (
                    random_seconds[resample_mask] % 86400
                )
                adjusted = (
                    day_offsets
                    + new_hours * 3600
                    + new_minutes * 60
                    + new_secs
                )
                random_seconds[resample_mask] = adjusted
                timestamps = start + random_seconds.astype("timedelta64[s]")

        return timestamps

    def weighted_choice(
        self,
        options: list,
        weights: list[float],
        count: int,
    ) -> np.ndarray:
        """Make weighted random choices using NumPy.
        
        Args:
            options: List of options to choose from
            weights: Probability weights (will be normalized)
            count: Number of choices to make
            
        Returns:
            NumPy array of chosen values
        """
        weights = np.array(weights, dtype=float)
        weights = weights / weights.sum()
        indices = self.rng.choice(len(options), size=count, p=weights)
        return np.array(options)[indices]

    def log_normal_amounts(
        self,
        mean: float,
        sigma: float,
        count: int,
        min_val: float = 0.01,
        max_val: float = None,
    ) -> np.ndarray:
        """Generate log-normally distributed amounts.
        
        Args:
            mean: Mean of the underlying normal distribution (log-scale)
            sigma: Standard deviation of the underlying normal distribution
            count: Number of values
            min_val: Minimum clamp value
            max_val: Maximum clamp value (optional)
            
        Returns:
            NumPy array of amounts rounded to 2 decimal places
        """
        values = self.rng.lognormal(mean=np.log(mean), sigma=sigma, size=count)
        values = np.maximum(values, min_val)
        if max_val is not None:
            values = np.minimum(values, max_val)
        return np.round(values, 2)

    def poisson_counts(
        self,
        lam: float,
        count: int,
        min_val: int = 0,
        max_val: int = None,
    ) -> np.ndarray:
        """Generate Poisson-distributed counts.
        
        Args:
            lam: Expected rate (lambda)
            count: Number of values
            min_val: Minimum clamp value
            max_val: Maximum clamp value (optional)
            
        Returns:
            NumPy array of integer counts
        """
        values = self.rng.poisson(lam=lam, size=count)
        values = np.maximum(values, min_val)
        if max_val is not None:
            values = np.minimum(values, max_val)
        return values

    def generate_phone_number(self, count: int = 1) -> list[str]:
        """Generate synthetic Ethiopian phone numbers.
        
        Args:
            count: Number of phone numbers to generate
            
        Returns:
            List of phone number strings
        """
        prefixes = ["91", "92", "93", "94", "95", "96", "97", "98", "70", "71"]
        prefix_indices = self.rng.integers(0, len(prefixes), size=count)
        suffixes = self.rng.integers(1000000, 9999999, size=count)
        phones = []
        for i in range(count):
            fmt = self.rng.choice(
                ["+251{}{}", "0{}{}", "+251-{}-{}", "251{}{}"],
            )
            phones.append(fmt.format(prefixes[prefix_indices[i]], suffixes[i]))
        return phones

    def generate_email(self, first_name: str, father_name: str, index: int) -> str:
        """Generate a synthetic email address.
        
        Args:
            first_name: Person's first name
            father_name: Person's father's name
            index: Unique index for deduplication
            
        Returns:
            Synthetic email string
        """
        domains = [
            "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
            "ethionet.et", "telecom.et", "mail.com", "protonmail.com",
        ]
        domain = domains[index % len(domains)]
        first = first_name.lower().replace(" ", "")
        father = father_name.lower().replace(" ", "")
        
        patterns = [
            f"{first}.{father}@{domain}",
            f"{first}{father}@{domain}",
            f"{first}.{father}{index % 100}@{domain}",
            f"{first[0]}{father}@{domain}",
            f"{first}_{father}@{domain}",
        ]
        return patterns[index % len(patterns)]
