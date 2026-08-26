import numpy as np
import polars as pl
from typing import Dict, Any, List
from datetime import datetime, timedelta

CURRENCIES = {
    'ETB': {'name': 'Ethiopian Birr', 'symbol': 'Br', 'country': 'Ethiopia', 'is_major': False},
    'USD': {'name': 'US Dollar', 'symbol': '$', 'country': 'United States', 'is_major': True},
    'EUR': {'name': 'Euro', 'symbol': '€', 'country': 'Eurozone', 'is_major': True},
    'GBP': {'name': 'British Pound', 'symbol': '£', 'country': 'United Kingdom', 'is_major': True},
    'AED': {'name': 'UAE Dirham', 'symbol': 'د.إ', 'country': 'United Arab Emirates', 'is_major': False},
    'SAR': {'name': 'Saudi Riyal', 'symbol': '﷼', 'country': 'Saudi Arabia', 'is_major': False},
    'KES': {'name': 'Kenyan Shilling', 'symbol': 'KSh', 'country': 'Kenya', 'is_major': False},
    'CNY': {'name': 'Chinese Yuan', 'symbol': '¥', 'country': 'China', 'is_major': True},
    'JPY': {'name': 'Japanese Yen', 'symbol': '¥', 'country': 'Japan', 'is_major': True},
    'CHF': {'name': 'Swiss Franc', 'symbol': 'Fr', 'country': 'Switzerland', 'is_major': True},
    'CAD': {'name': 'Canadian Dollar', 'symbol': '$', 'country': 'Canada', 'is_major': True},
    'AUD': {'name': 'Australian Dollar', 'symbol': '$', 'country': 'Australia', 'is_major': True},
    'INR': {'name': 'Indian Rupee', 'symbol': '₹', 'country': 'India', 'is_major': False},
    'ZAR': {'name': 'South African Rand', 'symbol': 'R', 'country': 'South Africa', 'is_major': False},
    'EGP': {'name': 'Egyptian Pound', 'symbol': '£', 'country': 'Egypt', 'is_major': False},
    'NGN': {'name': 'Nigerian Naira', 'symbol': '₦', 'country': 'Nigeria', 'is_major': False}
}

BASE_EXCHANGE_RATES = {
    'USD': 52.0,
    'EUR': 55.0,
    'GBP': 63.0,
    'AED': 14.0,
    'SAR': 14.0,
    'KES': 0.44,
    'CNY': 7.7,
    'JPY': 0.38,
    'CHF': 56.0,
    'CAD': 40.0,
    'AUD': 37.0,
    'INR': 0.65,
    'ZAR': 3.3,
    'EGP': 2.5,
    'NGN': 0.12
}

YEARLY_DEPRECIATION = {
    2022: 1.0,
    2023: 1.08,
    2024: 1.15,
    2025: 1.25,
    2026: 1.35
}

def generate_exchange_rate_history(rng: np.random.Generator, start_date: datetime, end_date: datetime) -> pl.DataFrame:
    days = (end_date - start_date).days + 1
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    data = []
    
    for currency, base_rate in BASE_EXCHANGE_RATES.items():
        # Random walk generation with slight daily volatility (std = 0.005)
        # We model the walk around a base 1.0 multiplier
        volatility = rng.normal(0, 0.005, size=days)
        random_walk = np.exp(np.cumsum(volatility))
        
        for i, date in enumerate(dates):
            year = date.year
            depreciation = YEARLY_DEPRECIATION.get(year, YEARLY_DEPRECIATION[max(YEARLY_DEPRECIATION.keys())])
            
            # Apply base rate, random walk factor, and yearly depreciation
            current_rate = base_rate * depreciation * random_walk[i]
            
            data.append({
                'date': date,
                'currency_from': currency,
                'currency_to': 'ETB',
                'rate': current_rate
            })
            
            # Add inverse rate
            data.append({
                'date': date,
                'currency_from': 'ETB',
                'currency_to': currency,
                'rate': 1.0 / current_rate
            })
            
    # Add ETB to ETB
    for date in dates:
        data.append({
            'date': date,
            'currency_from': 'ETB',
            'currency_to': 'ETB',
            'rate': 1.0
        })
        
    return pl.DataFrame(data)

def get_exchange_rate(rates_df: pl.DataFrame, date: datetime, currency_from: str, currency_to: str = 'ETB') -> float:
    if currency_from == currency_to:
        return 1.0
        
    # Convert date to start of day for exact matching
    target_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    result = rates_df.filter(
        (pl.col('date') == target_date) & 
        (pl.col('currency_from') == currency_from) & 
        (pl.col('currency_to') == currency_to)
    )
    
    if len(result) > 0:
        return result['rate'][0]
        
    # If exact date not found, get the closest one
    # Note: In a real app we'd sort and get the closest, but assuming daily data exists here.
    # Fallback to get_rate_for_date approximation
    return get_rate_for_date(np.random.default_rng(42), currency_from, target_date)

def convert_to_etb(amount: float, currency: str, date: datetime, rates_df: pl.DataFrame) -> float:
    if currency == 'ETB':
        return amount
    rate = get_exchange_rate(rates_df, date, currency, 'ETB')
    return amount * rate

def get_rate_for_date(rng: np.random.Generator, currency: str, date: datetime) -> float:
    """Quick rate lookup without full history. Approximates based on year."""
    if currency == 'ETB':
        return 1.0
        
    base_rate = BASE_EXCHANGE_RATES.get(currency, 1.0)
    year = date.year
    depreciation = YEARLY_DEPRECIATION.get(year, YEARLY_DEPRECIATION[max(YEARLY_DEPRECIATION.keys())])
    
    # Add slight random noise based on the date to make it look realistic
    # (using deterministic seed based on date and currency so it's consistent)
    seed = int(date.timestamp()) + sum(ord(c) for c in currency)
    local_rng = np.random.default_rng(seed)
    noise = local_rng.normal(1.0, 0.05)
    
    return base_rate * depreciation * noise
