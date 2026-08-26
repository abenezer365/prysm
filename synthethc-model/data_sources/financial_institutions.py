"""
Ethiopian financial institutions reference data.
"""

import numpy as np
from typing import List, Dict, Any

COMMERCIAL_BANKS = [
    {"id": "CB_001", "name": "Commercial Bank of Ethiopia", "short_name": "CBE", "type": "commercial_bank", "branch_count": 1800},
    {"id": "CB_002", "name": "Dashen Bank", "short_name": "Dashen", "type": "commercial_bank", "branch_count": 600},
    {"id": "CB_003", "name": "Awash Bank", "short_name": "Awash", "type": "commercial_bank", "branch_count": 700},
    {"id": "CB_004", "name": "Bank of Abyssinia", "short_name": "BoA", "type": "commercial_bank", "branch_count": 600},
    {"id": "CB_005", "name": "Wegagen Bank", "short_name": "Wegagen", "type": "commercial_bank", "branch_count": 400},
    {"id": "CB_006", "name": "NIB International Bank", "short_name": "NIB", "type": "commercial_bank", "branch_count": 350},
    {"id": "CB_007", "name": "United Bank", "short_name": "Hibret", "type": "commercial_bank", "branch_count": 350},
    {"id": "CB_008", "name": "Zemen Bank", "short_name": "Zemen", "type": "commercial_bank", "branch_count": 80},
    {"id": "CB_009", "name": "Berhan Bank", "short_name": "Berhan", "type": "commercial_bank", "branch_count": 300},
    {"id": "CB_010", "name": "Abay Bank", "short_name": "Abay", "type": "commercial_bank", "branch_count": 350},
    {"id": "CB_011", "name": "Cooperative Bank of Oromia", "short_name": "Coop", "type": "commercial_bank", "branch_count": 500},
]

MICROFINANCE_INSTITUTIONS = [
    {"id": "MFI_001", "name": "Amhara Credit & Savings", "short_name": "ACSI", "type": "mfi", "branch_count": 400},
    {"id": "MFI_002", "name": "Oromia Credit & Savings", "short_name": "OCSSCO", "type": "mfi", "branch_count": 350},
    {"id": "MFI_003", "name": "Dedebit Credit & Savings", "short_name": "DECSI", "type": "mfi", "branch_count": 150},
    {"id": "MFI_004", "name": "Omo Microfinance", "short_name": "OMO", "type": "mfi", "branch_count": 200},
]

PAYMENT_PROVIDERS = [
    {"id": "PAY_001", "name": "telebirr", "short_name": "telebirr", "type": "payment_provider", "branch_count": 0},
    {"id": "PAY_002", "name": "CBE Birr", "short_name": "CBEBirr", "type": "payment_provider", "branch_count": 0},
    {"id": "PAY_003", "name": "M-PESA Ethiopia", "short_name": "MPESA", "type": "payment_provider", "branch_count": 0},
    {"id": "PAY_004", "name": "Amole", "short_name": "Amole", "type": "payment_provider", "branch_count": 0},
]

INTERNATIONAL_INTERMEDIARIES = [
    {"id": "INT_001", "name": "SWIFT", "short_name": "SWIFT", "type": "international", "branch_count": 0},
    {"id": "INT_002", "name": "Western Union", "short_name": "WU", "type": "international", "branch_count": 0},
    {"id": "INT_003", "name": "WorldRemit", "short_name": "WorldRemit", "type": "international", "branch_count": 0},
    {"id": "INT_004", "name": "Wise", "short_name": "Wise", "type": "international", "branch_count": 0},
    {"id": "INT_005", "name": "PayPal", "short_name": "PayPal", "type": "international", "branch_count": 0},
]

def get_all_institutions() -> List[Dict[str, Any]]:
    return COMMERCIAL_BANKS + MICROFINANCE_INSTITUTIONS + PAYMENT_PROVIDERS + INTERNATIONAL_INTERMEDIARIES

def get_institution_by_id(inst_id: str) -> Dict[str, Any]:
    all_inst = get_all_institutions()
    for inst in all_inst:
        if inst["id"] == inst_id:
            return inst
    raise ValueError(f"Unknown institution ID: {inst_id}")

def get_random_institution(rng: np.random.Generator, inst_type: str = None) -> Dict[str, Any]:
    insts = get_all_institutions()
    if inst_type:
        insts = [i for i in insts if i["type"] == inst_type]
    idx = rng.integers(0, len(insts))
    return insts[idx]

def generate_account_number(rng: np.random.Generator, inst: Dict[str, Any]) -> str:
    if inst["type"] == "commercial_bank":
        return f"1000{rng.integers(100000000, 999999999)}"
    elif inst["type"] == "payment_provider":
        return f"+251{rng.integers(910000000, 999999999)}"
    else:
        return f"{rng.integers(100000, 999999)}-{rng.integers(100,999)}"

def generate_branch_code(rng: np.random.Generator, inst: Dict[str, Any]) -> str:
    if inst["branch_count"] > 0:
        return f"BR{rng.integers(1, inst['branch_count'] + 1):04d}"
    return "ONLINE"

