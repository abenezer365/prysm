"""
Ethiopian geography data source for synthetic generation.
"""

import numpy as np
from typing import List, Dict, Any

CITIES = [
    {"name": "Addis Ababa", "region": "Addis Ababa", "population_weight": 0.15, "urban_level": "major_city"},
    {"name": "Dire Dawa", "region": "Dire Dawa", "population_weight": 0.03, "urban_level": "major_city"},
    {"name": "Bahir Dar", "region": "Amhara", "population_weight": 0.025, "urban_level": "major_city"},
    {"name": "Hawassa", "region": "Sidama", "population_weight": 0.025, "urban_level": "major_city"},
    {"name": "Mekelle", "region": "Tigray", "population_weight": 0.02, "urban_level": "major_city"},
    {"name": "Gondar", "region": "Amhara", "population_weight": 0.02, "urban_level": "major_city"},
    {"name": "Jimma", "region": "Oromia", "population_weight": 0.02, "urban_level": "major_city"},
    {"name": "Adama", "region": "Oromia", "population_weight": 0.025, "urban_level": "major_city"},
    {"name": "Bishoftu", "region": "Oromia", "population_weight": 0.015, "urban_level": "major_city"},
    {"name": "Harar", "region": "Harari", "population_weight": 0.012, "urban_level": "major_city"},
    {"name": "Dessie", "region": "Amhara", "population_weight": 0.015, "urban_level": "city"},
    {"name": "Arba Minch", "region": "SNNPR", "population_weight": 0.015, "urban_level": "city"},
    {"name": "Debre Birhan", "region": "Amhara", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Debre Markos", "region": "Amhara", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Nekemte", "region": "Oromia", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Gambela", "region": "Gambela", "population_weight": 0.008, "urban_level": "city"},
    {"name": "Jijiga", "region": "Somali", "population_weight": 0.012, "urban_level": "city"},
    {"name": "Shashamane", "region": "Oromia", "population_weight": 0.012, "urban_level": "city"},
    {"name": "Dilla", "region": "SNNPR", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Wolkite", "region": "Central Ethiopia", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Hosaena", "region": "Central Ethiopia", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Asella", "region": "Oromia", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Ambo", "region": "Oromia", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Sodo", "region": "SNNPR", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Axum", "region": "Tigray", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Lalibela", "region": "Amhara", "population_weight": 0.005, "urban_level": "town"},
    {"name": "Kombolcha", "region": "Amhara", "population_weight": 0.01, "urban_level": "city"},
    {"name": "Butajira", "region": "Central Ethiopia", "population_weight": 0.01, "urban_level": "city"}
]

# Add rural/other buffer to make weights sum to 1.0 (approximately, we'll normalize in the function)

SUBCITIES_ADDIS = [
    "Bole", "Kirkos", "Lideta", "Arada", "Addis Ketema", 
    "Yeka", "Gulele", "Kolfe Keranio", "Nifas Silk-Lafto", "Akaki Kality", "Lemi Kura"
]

ADDRESS_TEMPLATES = [
    "{subcity} Sub City, Woreda {woreda}, Kebele {kebele}",
    "{area_name}, {city}",
    "Near {landmark}, {city}"
]

def get_random_city(rng: np.random.Generator) -> Dict[str, Any]:
    weights = [c["population_weight"] for c in CITIES]
    total = sum(weights)
    norm_weights = [w / total for w in weights]
    idx = rng.choice(len(CITIES), p=norm_weights)
    return CITIES[idx]

def get_cities_batch(rng: np.random.Generator, count: int) -> List[Dict[str, Any]]:
    weights = [c["population_weight"] for c in CITIES]
    total = sum(weights)
    norm_weights = [w / total for w in weights]
    indices = rng.choice(len(CITIES), p=norm_weights, size=count)
    return [CITIES[i] for i in indices]

def get_region_for_city(city_name: str) -> str:
    for c in CITIES:
        if c["name"] == city_name:
            return c["region"]
    return "Unknown"

def get_random_address(rng: np.random.Generator, city_name: str) -> str:
    if city_name == "Addis Ababa":
        subcity = rng.choice(SUBCITIES_ADDIS)
        woreda = rng.integers(1, 15)
        kebele = rng.integers(1, 20)
        return f"{subcity} Sub City, Woreda {woreda:02d}, Kebele {kebele:02d}"
    else:
        woreda = rng.integers(1, 10)
        kebele = rng.integers(1, 10)
        return f"Woreda {woreda:02d}, Kebele {kebele:02d}, {city_name}"

