import numpy as np
from typing import Dict, Any, List

TECH_COMPANIES = [
    {"name": "Microsoft", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 15000), "payment_frequency": "monthly"},
    {"name": "Google", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3500, 18000), "payment_frequency": "monthly"},
    {"name": "Amazon", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 16000), "payment_frequency": "monthly"},
    {"name": "Meta", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3500, 18000), "payment_frequency": "monthly"},
    {"name": "Apple", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3500, 17000), "payment_frequency": "monthly"},
    {"name": "IBM", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Oracle", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 13000), "payment_frequency": "monthly"},
    {"name": "Adobe", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Cisco", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2800, 12000), "payment_frequency": "monthly"},
    {"name": "NVIDIA", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (4000, 20000), "payment_frequency": "monthly"},
    {"name": "Salesforce", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 15000), "payment_frequency": "monthly"},
    {"name": "SAP", "country": "Germany", "industry": "Technology", "currency": "EUR", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Intel", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 13000), "payment_frequency": "monthly"},
    {"name": "Samsung", "country": "South Korea", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2000, 10000), "payment_frequency": "monthly"},
    {"name": "Sony", "country": "Japan", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2000, 9000), "payment_frequency": "monthly"},
    {"name": "Twitter", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 15000), "payment_frequency": "monthly"},
    {"name": "Netflix", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (4000, 22000), "payment_frequency": "monthly"},
    {"name": "Spotify", "country": "Sweden", "industry": "Technology", "currency": "EUR", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Uber", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Airbnb", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 15000), "payment_frequency": "monthly"},
    {"name": "Stripe", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3500, 16000), "payment_frequency": "monthly"},
    {"name": "Shopify", "country": "Canada", "industry": "Technology", "currency": "CAD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Atlassian", "country": "Australia", "industry": "Technology", "currency": "AUD", "typical_payment_range_usd": (2500, 13000), "payment_frequency": "monthly"},
    {"name": "GitHub", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "GitLab", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "JetBrains", "country": "Czech Republic", "industry": "Technology", "currency": "EUR", "typical_payment_range_usd": (2500, 11000), "payment_frequency": "monthly"},
    {"name": "DigitalOcean", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2000, 9000), "payment_frequency": "monthly"},
    {"name": "Cloudflare", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Datadog", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Twilio", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2800, 13000), "payment_frequency": "monthly"},
    {"name": "Square", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Palantir", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3500, 16000), "payment_frequency": "monthly"},
    {"name": "Snowflake", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3500, 17000), "payment_frequency": "monthly"},
    {"name": "Databricks", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3500, 16000), "payment_frequency": "monthly"},
    {"name": "MongoDB", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2800, 13000), "payment_frequency": "monthly"},
    {"name": "Elastic", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2800, 13000), "payment_frequency": "monthly"},
    {"name": "HashiCorp", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2800, 13000), "payment_frequency": "monthly"},
    {"name": "Confluent", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "CrowdStrike", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 15000), "payment_frequency": "monthly"},
    {"name": "Okta", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2800, 13000), "payment_frequency": "monthly"},
    {"name": "Zoom", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Slack", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Notion", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Figma", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2800, 13000), "payment_frequency": "monthly"},
    {"name": "Vercel", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 11000), "payment_frequency": "monthly"},
    {"name": "Supabase", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 11000), "payment_frequency": "monthly"},
    {"name": "PlanetScale", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 11000), "payment_frequency": "monthly"},
    {"name": "Linear", "country": "USA", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 10000), "payment_frequency": "monthly"},
    {"name": "Raycast", "country": "UK", "industry": "Technology", "currency": "GBP", "typical_payment_range_usd": (2000, 9000), "payment_frequency": "monthly"},
    {"name": "Tailwind Labs", "country": "Canada", "industry": "Technology", "currency": "USD", "typical_payment_range_usd": (2500, 10000), "payment_frequency": "monthly"},
]

FREELANCE_PLATFORMS = [
    {"name": "Upwork", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (500, 8000), "payment_frequency": "varied"},
    {"name": "Fiverr", "country": "Israel", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (200, 5000), "payment_frequency": "varied"},
    {"name": "Toptal", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (3000, 12000), "payment_frequency": "varied"},
    {"name": "Freelancer.com", "country": "Australia", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (200, 4000), "payment_frequency": "varied"},
    {"name": "Guru", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (500, 5000), "payment_frequency": "varied"},
    {"name": "PeoplePerHour", "country": "UK", "industry": "Platform", "currency": "GBP", "typical_payment_range_usd": (300, 4000), "payment_frequency": "varied"},
    {"name": "99designs", "country": "Australia", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (300, 3000), "payment_frequency": "varied"},
    {"name": "DesignCrowd", "country": "Australia", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (200, 2500), "payment_frequency": "varied"},
    {"name": "Gigster", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (2000, 10000), "payment_frequency": "varied"},
    {"name": "CloudPeeps", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (500, 4000), "payment_frequency": "varied"},
    {"name": "FlexJobs", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (1000, 6000), "payment_frequency": "varied"},
    {"name": "We Work Remotely", "country": "Canada", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (2000, 8000), "payment_frequency": "varied"},
    {"name": "Remote.co", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (1500, 7000), "payment_frequency": "varied"},
    {"name": "Working Nomads", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (1500, 7000), "payment_frequency": "varied"},
    {"name": "AngelList", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (2000, 9000), "payment_frequency": "varied"},
    {"name": "Arc.dev", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (3000, 12000), "payment_frequency": "varied"},
    {"name": "Turing", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (3000, 10000), "payment_frequency": "varied"},
    {"name": "Andela", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (2500, 8000), "payment_frequency": "varied"},
    {"name": "Crossover", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (2000, 8000), "payment_frequency": "varied"},
    {"name": "Lemon.io", "country": "USA", "industry": "Platform", "currency": "USD", "typical_payment_range_usd": (2500, 8000), "payment_frequency": "varied"}
]

REMOTE_EMPLOYMENT_PLATFORMS = [
    {"name": "Deel", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Remote.com", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Oyster", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Papaya Global", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Velocity Global", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Globalization Partners", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Safeguard Global", "country": "UK", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Multiplier", "country": "Singapore", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Panther", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Lano", "country": "Germany", "industry": "Employer of Record", "currency": "EUR", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Rippling", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Gusto", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "OnTop", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Remofirst", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"},
    {"name": "Plane", "country": "USA", "industry": "Employer of Record", "currency": "USD", "typical_payment_range_usd": (1000, 15000), "payment_frequency": "monthly"}
]

OTHER_SECTOR_COMPANIES = [
    {"name": "McKinsey", "country": "USA", "industry": "Consulting", "currency": "USD", "typical_payment_range_usd": (5000, 20000), "payment_frequency": "monthly"},
    {"name": "BCG", "country": "USA", "industry": "Consulting", "currency": "USD", "typical_payment_range_usd": (5000, 20000), "payment_frequency": "monthly"},
    {"name": "Bain", "country": "USA", "industry": "Consulting", "currency": "USD", "typical_payment_range_usd": (5000, 20000), "payment_frequency": "monthly"},
    {"name": "Deloitte", "country": "UK", "industry": "Consulting", "currency": "USD", "typical_payment_range_usd": (4000, 15000), "payment_frequency": "monthly"},
    {"name": "PwC", "country": "UK", "industry": "Consulting", "currency": "USD", "typical_payment_range_usd": (4000, 15000), "payment_frequency": "monthly"},
    {"name": "EY", "country": "UK", "industry": "Consulting", "currency": "USD", "typical_payment_range_usd": (4000, 15000), "payment_frequency": "monthly"},
    {"name": "KPMG", "country": "Netherlands", "industry": "Consulting", "currency": "USD", "typical_payment_range_usd": (4000, 15000), "payment_frequency": "monthly"},
    {"name": "Accenture", "country": "Ireland", "industry": "Consulting", "currency": "USD", "typical_payment_range_usd": (3500, 14000), "payment_frequency": "monthly"},
    {"name": "JPMorgan", "country": "USA", "industry": "Finance", "currency": "USD", "typical_payment_range_usd": (5000, 25000), "payment_frequency": "monthly"},
    {"name": "Goldman Sachs", "country": "USA", "industry": "Finance", "currency": "USD", "typical_payment_range_usd": (5000, 25000), "payment_frequency": "monthly"},
    {"name": "Citi", "country": "USA", "industry": "Finance", "currency": "USD", "typical_payment_range_usd": (4500, 20000), "payment_frequency": "monthly"},
    {"name": "Morgan Stanley", "country": "USA", "industry": "Finance", "currency": "USD", "typical_payment_range_usd": (5000, 22000), "payment_frequency": "monthly"},
    {"name": "Bank of America", "country": "USA", "industry": "Finance", "currency": "USD", "typical_payment_range_usd": (4000, 18000), "payment_frequency": "monthly"},
    {"name": "HSBC", "country": "UK", "industry": "Finance", "currency": "GBP", "typical_payment_range_usd": (4000, 18000), "payment_frequency": "monthly"},
    {"name": "Barclays", "country": "UK", "industry": "Finance", "currency": "GBP", "typical_payment_range_usd": (4000, 18000), "payment_frequency": "monthly"},
    {"name": "Alibaba", "country": "China", "industry": "Ecommerce", "currency": "CNY", "typical_payment_range_usd": (2000, 12000), "payment_frequency": "monthly"},
    {"name": "eBay", "country": "USA", "industry": "Ecommerce", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Walmart", "country": "USA", "industry": "Retail", "currency": "USD", "typical_payment_range_usd": (2000, 10000), "payment_frequency": "monthly"},
    {"name": "Target", "country": "USA", "industry": "Retail", "currency": "USD", "typical_payment_range_usd": (2000, 10000), "payment_frequency": "monthly"},
    {"name": "Coursera", "country": "USA", "industry": "Education", "currency": "USD", "typical_payment_range_usd": (2000, 10000), "payment_frequency": "monthly"},
    {"name": "Udemy", "country": "USA", "industry": "Education", "currency": "USD", "typical_payment_range_usd": (2000, 10000), "payment_frequency": "monthly"},
    {"name": "edX", "country": "USA", "industry": "Education", "currency": "USD", "typical_payment_range_usd": (2000, 9000), "payment_frequency": "monthly"},
    {"name": "Duolingo", "country": "USA", "industry": "Education", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Reuters", "country": "UK", "industry": "Media", "currency": "USD", "typical_payment_range_usd": (2000, 9000), "payment_frequency": "monthly"},
    {"name": "Bloomberg", "country": "USA", "industry": "Media", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "New York Times", "country": "USA", "industry": "Media", "currency": "USD", "typical_payment_range_usd": (2500, 11000), "payment_frequency": "monthly"},
    {"name": "CNN", "country": "USA", "industry": "Media", "currency": "USD", "typical_payment_range_usd": (2500, 11000), "payment_frequency": "monthly"},
    {"name": "BBC", "country": "UK", "industry": "Media", "currency": "GBP", "typical_payment_range_usd": (2500, 10000), "payment_frequency": "monthly"},
    {"name": "Disney", "country": "USA", "industry": "Media", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Warner Bros", "country": "USA", "industry": "Media", "currency": "USD", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Pfizer", "country": "USA", "industry": "Healthcare", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Johnson & Johnson", "country": "USA", "industry": "Healthcare", "currency": "USD", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Novartis", "country": "Switzerland", "industry": "Healthcare", "currency": "CHF", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Roche", "country": "Switzerland", "industry": "Healthcare", "currency": "CHF", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "ExxonMobil", "country": "USA", "industry": "Energy", "currency": "USD", "typical_payment_range_usd": (3000, 15000), "payment_frequency": "monthly"},
    {"name": "Shell", "country": "UK", "industry": "Energy", "currency": "GBP", "typical_payment_range_usd": (3000, 15000), "payment_frequency": "monthly"},
    {"name": "BP", "country": "UK", "industry": "Energy", "currency": "GBP", "typical_payment_range_usd": (3000, 14000), "payment_frequency": "monthly"},
    {"name": "Toyota", "country": "Japan", "industry": "Automotive", "currency": "JPY", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Volkswagen", "country": "Germany", "industry": "Automotive", "currency": "EUR", "typical_payment_range_usd": (2500, 12000), "payment_frequency": "monthly"},
    {"name": "Ford", "country": "USA", "industry": "Automotive", "currency": "USD", "typical_payment_range_usd": (2500, 11000), "payment_frequency": "monthly"}
]

FICTIONAL_SUSPICIOUS_ENTITIES = [
    {"name": "GlobalTrade Dynamics LLC", "country": "Dubai", "industry": "Trading", "risk_level": "medium"},
    {"name": "Apex Financial Solutions FZE", "country": "Dubai", "industry": "Finance", "risk_level": "high"},
    {"name": "Meridian Capital Holdings", "country": "Cyprus", "industry": "Investment", "risk_level": "high"},
    {"name": "Pacific Rim Trading Co", "country": "Hong Kong", "industry": "Trading", "risk_level": "medium"},
    {"name": "Eastern Gateway Investments", "country": "Seychelles", "industry": "Investment", "risk_level": "high"},
    {"name": "Blue Horizon Logistics", "country": "Malta", "industry": "Logistics", "risk_level": "medium"},
    {"name": "Oasis Trading Partners", "country": "BVI", "industry": "Trading", "risk_level": "high"},
    {"name": "Sterling Wealth Management", "country": "Cayman Islands", "industry": "Finance", "risk_level": "high"},
    {"name": "Vanguard Global Imports", "country": "Panama", "industry": "Import/Export", "risk_level": "high"},
    {"name": "Nova Consulting Services", "country": "Cyprus", "industry": "Consulting", "risk_level": "medium"},
    {"name": "Pinnacle Capital Group", "country": "Dubai", "industry": "Investment", "risk_level": "high"},
    {"name": "Crestview Holdings Ltd", "country": "BVI", "industry": "Holding", "risk_level": "high"},
    {"name": "Summit Trading FZC", "country": "Dubai", "industry": "Trading", "risk_level": "medium"},
    {"name": "Azure Investments Corp", "country": "Panama", "industry": "Investment", "risk_level": "high"},
    {"name": "Zenith Global Ventures", "country": "Malta", "industry": "Ventures", "risk_level": "medium"},
    {"name": "Evergreen Capital Partners", "country": "Seychelles", "industry": "Finance", "risk_level": "high"},
    {"name": "Horizon Equities LLC", "country": "Cayman Islands", "industry": "Investment", "risk_level": "high"},
    {"name": "Nexus Trade Syndicate", "country": "Hong Kong", "industry": "Trading", "risk_level": "medium"},
    {"name": "Quantum Financial Ltd", "country": "BVI", "industry": "Finance", "risk_level": "high"},
    {"name": "Silverstone Assets", "country": "Cyprus", "industry": "Asset Management", "risk_level": "medium"}
]

# Generate more fictional entities to reach 100+
_prefixes = ["Global", "International", "Universal", "Continental", "Prime", "Alpha", "Omega", "Infinity", "Paramount", "Majestic"]
_nouns = ["Trade", "Commerce", "Ventures", "Enterprises", "Solutions", "Dynamics", "Synergy", "Systems", "Network", "Alliance"]
_suffixes = ["LLC", "Ltd", "Inc", "Corp", "GmbH", "SA", "NV", "PLC", "FZE", "Group"]
_countries = ["Dubai", "Cyprus", "BVI", "Seychelles", "Panama", "Malta", "Cayman Islands"]
_industries = ["Trading", "Finance", "Consulting", "Logistics", "Investment", "Holding", "Import/Export", "Services"]

def _generate_more_fictional_entities(count: int) -> List[Dict[str, str]]:
    entities = []
    import random
    random.seed(42) # Deterministic generation
    for _ in range(count):
        name = f"{random.choice(_prefixes)} {random.choice(_nouns)} {random.choice(_suffixes)}"
        country = random.choice(_countries)
        industry = random.choice(_industries)
        risk = random.choice(["medium", "high"])
        entities.append({
            "name": name,
            "country": country,
            "industry": industry,
            "risk_level": risk
        })
    return entities

FICTIONAL_SUSPICIOUS_ENTITIES.extend(_generate_more_fictional_entities(80))


def get_all_foreign_companies() -> List[Dict[str, Any]]:
    return TECH_COMPANIES + FREELANCE_PLATFORMS + REMOTE_EMPLOYMENT_PLATFORMS + OTHER_SECTOR_COMPANIES

def get_random_employer(rng: np.random.Generator, company_type: str = None) -> Dict[str, Any]:
    if company_type == 'tech':
        companies = TECH_COMPANIES
    elif company_type == 'freelance':
        companies = FREELANCE_PLATFORMS
    elif company_type == 'remote_platform':
        companies = REMOTE_EMPLOYMENT_PLATFORMS
    elif company_type == 'other':
        companies = OTHER_SECTOR_COMPANIES
    else:
        companies = get_all_foreign_companies()
        
    choice = rng.choice(len(companies))
    return companies[choice]

def get_random_suspicious_entity(rng: np.random.Generator) -> Dict[str, Any]:
    choice = rng.choice(len(FICTIONAL_SUSPICIOUS_ENTITIES))
    return FICTIONAL_SUSPICIOUS_ENTITIES[choice]

def get_companies_batch(rng: np.random.Generator, count: int, company_type: str = None) -> List[Dict[str, Any]]:
    if company_type == 'tech':
        companies = TECH_COMPANIES
    elif company_type == 'freelance':
        companies = FREELANCE_PLATFORMS
    elif company_type == 'remote_platform':
        companies = REMOTE_EMPLOYMENT_PLATFORMS
    elif company_type == 'other':
        companies = OTHER_SECTOR_COMPANIES
    elif company_type == 'suspicious':
        companies = FICTIONAL_SUSPICIOUS_ENTITIES
    else:
        companies = get_all_foreign_companies()
        
    choices = rng.choice(len(companies), size=count)
    return [companies[i] for i in choices]
