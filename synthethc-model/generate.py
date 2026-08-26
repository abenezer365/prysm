"""
Main orchestrator for synthetic data generation.
"""
import argparse
import yaml
import time
from pathlib import Path

from generators.people_generator import PeopleGenerator
from generators.company_generator import CompanyGenerator
from generators.institution_generator import InstitutionGenerator
from generators.employment_generator import EmploymentGenerator
from generators.account_generator import AccountGenerator
from generators.device_generator import DeviceGenerator
from generators.transaction_generator import TransactionGenerator

def load_config(config_path: str) -> dict:
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def run():
    parser = argparse.ArgumentParser(description="Synthetic Financial Data Generator")
    parser.add_argument("--config", default="config/small_config.yaml")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="data/raw")
    args = parser.parse_args()

    config = load_config(args.config)
    seed = args.seed
    output_dir = args.output_dir

    print(f"Starting generation with seed {seed}")
    start_total = time.time()
    
    # 1. Institutions
    ig = InstitutionGenerator(config, seed, output_dir)
    inst_res = ig.generate()
    
    # 2. People
    pg = PeopleGenerator(config, seed, output_dir)
    people_res = pg.generate()
    
    # 3. Companies
    cg = CompanyGenerator(config, seed, output_dir)
    comp_res = cg.generate()
    
    # 4. Employment
    eg = EmploymentGenerator(config, seed, output_dir)
    emp_res = eg.generate(people_res["person_ids"], comp_res["company_ids"], people_res["behavior_map"])
    
    # 5. Accounts
    ag = AccountGenerator(config, seed, output_dir)
    acc_res = ag.generate(people_res["person_ids"], comp_res["company_ids"], inst_res["institution_ids"])
    
    # 6. Devices
    dg = DeviceGenerator(config, seed, output_dir)
    dev_res = dg.generate(people_res["person_ids"])
    
    # 7. Transactions
    tg = TransactionGenerator(config, seed, output_dir)
    txn_res = tg.generate(acc_res["account_ids"], people_res["suspicious_ids"])
    
    total_time = time.time() - start_total
    print(f"\\nGeneration complete in {total_time:.2f} seconds.")
    print(f"People: {config['population']['people']}")
    print(f"Companies: {config['population']['companies']}")
    print(f"Transactions: {config['population']['transactions']}")
    print(f"Data saved to: {output_dir}")

if __name__ == "__main__":
    run()

