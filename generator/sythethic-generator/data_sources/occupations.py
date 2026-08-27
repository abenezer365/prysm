import numpy as np
from typing import Dict, Any, List, Tuple

EMPLOYMENT_TYPES = {
    'employed': 0.45,
    'self_employed': 0.12,
    'freelancer': 0.08,
    'student': 0.10,
    'unemployed': 0.08,
    'business_owner': 0.05,
    'contractor': 0.04,
    'remote_worker': 0.04,
    'part_time': 0.04
}

OCCUPATIONS = [
    {
        'id': 'software_engineer',
        'name': 'Software Engineer',
        'category': 'technology',
        'weight': 0.015,
        'income_params': {
            'etb_monthly_base': 25000,
            'log_normal_sigma': 0.4,
            'experience_multiplier_range': (0.8, 3.5)
        },
        'foreign_income_probability': 0.4,
        'remote_work_probability': 0.5,
        'typical_employment_types': ['employed', 'freelancer', 'contractor', 'remote_worker']
    },
    {
        'id': 'web_developer',
        'name': 'Web Developer',
        'category': 'technology',
        'weight': 0.02,
        'income_params': {
            'etb_monthly_base': 20000,
            'log_normal_sigma': 0.35,
            'experience_multiplier_range': (0.8, 3.0)
        },
        'foreign_income_probability': 0.35,
        'remote_work_probability': 0.5,
        'typical_employment_types': ['employed', 'freelancer', 'contractor']
    },
    {
        'id': 'mobile_developer',
        'name': 'Mobile Developer',
        'category': 'technology',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 28000,
            'log_normal_sigma': 0.35,
            'experience_multiplier_range': (0.8, 3.2)
        },
        'foreign_income_probability': 0.45,
        'remote_work_probability': 0.55,
        'typical_employment_types': ['employed', 'freelancer', 'contractor']
    },
    {
        'id': 'data_scientist',
        'name': 'Data Scientist',
        'category': 'technology',
        'weight': 0.005,
        'income_params': {
            'etb_monthly_base': 35000,
            'log_normal_sigma': 0.4,
            'experience_multiplier_range': (0.9, 4.0)
        },
        'foreign_income_probability': 0.5,
        'remote_work_probability': 0.6,
        'typical_employment_types': ['employed', 'contractor', 'remote_worker']
    },
    {
        'id': 'ml_engineer',
        'name': 'ML Engineer',
        'category': 'technology',
        'weight': 0.002,
        'income_params': {
            'etb_monthly_base': 40000,
            'log_normal_sigma': 0.45,
            'experience_multiplier_range': (0.9, 4.5)
        },
        'foreign_income_probability': 0.6,
        'remote_work_probability': 0.65,
        'typical_employment_types': ['employed', 'contractor', 'remote_worker']
    },
    {
        'id': 'devops_engineer',
        'name': 'DevOps Engineer',
        'category': 'technology',
        'weight': 0.005,
        'income_params': {
            'etb_monthly_base': 35000,
            'log_normal_sigma': 0.3,
            'experience_multiplier_range': (0.9, 3.5)
        },
        'foreign_income_probability': 0.55,
        'remote_work_probability': 0.6,
        'typical_employment_types': ['employed', 'contractor']
    },
    {
        'id': 'database_admin',
        'name': 'Database Administrator',
        'category': 'technology',
        'weight': 0.008,
        'income_params': {
            'etb_monthly_base': 28000,
            'log_normal_sigma': 0.25,
            'experience_multiplier_range': (0.9, 2.8)
        },
        'foreign_income_probability': 0.1,
        'remote_work_probability': 0.2,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'qa_engineer',
        'name': 'QA Engineer',
        'category': 'technology',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 18000,
            'log_normal_sigma': 0.25,
            'experience_multiplier_range': (0.8, 2.5)
        },
        'foreign_income_probability': 0.2,
        'remote_work_probability': 0.4,
        'typical_employment_types': ['employed', 'freelancer']
    },
    {
        'id': 'systems_analyst',
        'name': 'Systems Analyst',
        'category': 'technology',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 25000,
            'log_normal_sigma': 0.25,
            'experience_multiplier_range': (0.9, 2.5)
        },
        'foreign_income_probability': 0.05,
        'remote_work_probability': 0.15,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'it_support',
        'name': 'IT Support',
        'category': 'technology',
        'weight': 0.02,
        'income_params': {
            'etb_monthly_base': 12000,
            'log_normal_sigma': 0.2,
            'experience_multiplier_range': (0.8, 2.0)
        },
        'foreign_income_probability': 0.02,
        'remote_work_probability': 0.1,
        'typical_employment_types': ['employed', 'part_time']
    },
    {
        'id': 'accountant',
        'name': 'Accountant',
        'category': 'professional',
        'weight': 0.04,
        'income_params': {
            'etb_monthly_base': 15000,
            'log_normal_sigma': 0.3,
            'experience_multiplier_range': (0.8, 2.8)
        },
        'foreign_income_probability': 0.05,
        'remote_work_probability': 0.1,
        'typical_employment_types': ['employed', 'self_employed', 'part_time']
    },
    {
        'id': 'lawyer',
        'name': 'Lawyer',
        'category': 'professional',
        'weight': 0.015,
        'income_params': {
            'etb_monthly_base': 30000,
            'log_normal_sigma': 0.5,
            'experience_multiplier_range': (0.7, 4.0)
        },
        'foreign_income_probability': 0.05,
        'remote_work_probability': 0.05,
        'typical_employment_types': ['employed', 'self_employed']
    },
    {
        'id': 'architect',
        'name': 'Architect',
        'category': 'professional',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 25000,
            'log_normal_sigma': 0.4,
            'experience_multiplier_range': (0.8, 3.5)
        },
        'foreign_income_probability': 0.1,
        'remote_work_probability': 0.15,
        'typical_employment_types': ['employed', 'self_employed', 'freelancer']
    },
    {
        'id': 'civil_engineer',
        'name': 'Civil Engineer',
        'category': 'professional',
        'weight': 0.03,
        'income_params': {
            'etb_monthly_base': 20000,
            'log_normal_sigma': 0.3,
            'experience_multiplier_range': (0.8, 3.0)
        },
        'foreign_income_probability': 0.02,
        'remote_work_probability': 0.02,
        'typical_employment_types': ['employed', 'self_employed', 'contractor']
    },
    {
        'id': 'mechanical_engineer',
        'name': 'Mechanical Engineer',
        'category': 'professional',
        'weight': 0.015,
        'income_params': {
            'etb_monthly_base': 18000,
            'log_normal_sigma': 0.25,
            'experience_multiplier_range': (0.8, 2.5)
        },
        'foreign_income_probability': 0.02,
        'remote_work_probability': 0.02,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'electrical_engineer',
        'name': 'Electrical Engineer',
        'category': 'professional',
        'weight': 0.015,
        'income_params': {
            'etb_monthly_base': 18000,
            'log_normal_sigma': 0.25,
            'experience_multiplier_range': (0.8, 2.5)
        },
        'foreign_income_probability': 0.02,
        'remote_work_probability': 0.02,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'consultant',
        'name': 'Consultant',
        'category': 'professional',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 35000,
            'log_normal_sigma': 0.4,
            'experience_multiplier_range': (0.9, 3.5)
        },
        'foreign_income_probability': 0.25,
        'remote_work_probability': 0.4,
        'typical_employment_types': ['employed', 'self_employed', 'contractor']
    },
    {
        'id': 'pharmacist',
        'name': 'Pharmacist',
        'category': 'professional',
        'weight': 0.015,
        'income_params': {
            'etb_monthly_base': 18000,
            'log_normal_sigma': 0.2,
            'experience_multiplier_range': (0.9, 2.2)
        },
        'foreign_income_probability': 0.01,
        'remote_work_probability': 0.01,
        'typical_employment_types': ['employed', 'self_employed']
    },
    {
        'id': 'doctor',
        'name': 'Doctor',
        'category': 'healthcare',
        'weight': 0.02,
        'income_params': {
            'etb_monthly_base': 35000,
            'log_normal_sigma': 0.4,
            'experience_multiplier_range': (0.8, 3.5)
        },
        'foreign_income_probability': 0.02,
        'remote_work_probability': 0.01,
        'typical_employment_types': ['employed', 'self_employed']
    },
    {
        'id': 'nurse',
        'name': 'Nurse',
        'category': 'healthcare',
        'weight': 0.04,
        'income_params': {
            'etb_monthly_base': 10000,
            'log_normal_sigma': 0.2,
            'experience_multiplier_range': (0.9, 2.0)
        },
        'foreign_income_probability': 0.01,
        'remote_work_probability': 0.01,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'medical_technician',
        'name': 'Medical Technician',
        'category': 'healthcare',
        'weight': 0.015,
        'income_params': {
            'etb_monthly_base': 12000,
            'log_normal_sigma': 0.2,
            'experience_multiplier_range': (0.9, 2.0)
        },
        'foreign_income_probability': 0.01,
        'remote_work_probability': 0.01,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'teacher',
        'name': 'Teacher',
        'category': 'education',
        'weight': 0.06,
        'income_params': {
            'etb_monthly_base': 8000,
            'log_normal_sigma': 0.15,
            'experience_multiplier_range': (0.9, 1.8)
        },
        'foreign_income_probability': 0.01,
        'remote_work_probability': 0.02,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'university_lecturer',
        'name': 'University Lecturer',
        'category': 'education',
        'weight': 0.015,
        'income_params': {
            'etb_monthly_base': 18000,
            'log_normal_sigma': 0.2,
            'experience_multiplier_range': (0.9, 2.5)
        },
        'foreign_income_probability': 0.1,
        'remote_work_probability': 0.05,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'researcher',
        'name': 'Researcher',
        'category': 'education',
        'weight': 0.005,
        'income_params': {
            'etb_monthly_base': 22000,
            'log_normal_sigma': 0.25,
            'experience_multiplier_range': (0.9, 2.5)
        },
        'foreign_income_probability': 0.2,
        'remote_work_probability': 0.15,
        'typical_employment_types': ['employed', 'contractor']
    },
    {
        'id': 'business_owner',
        'name': 'Business Owner',
        'category': 'business',
        'weight': 0.05,
        'income_params': {
            'etb_monthly_base': 40000,
            'log_normal_sigma': 0.8,
            'experience_multiplier_range': (0.5, 5.0)
        },
        'foreign_income_probability': 0.15,
        'remote_work_probability': 0.1,
        'typical_employment_types': ['business_owner']
    },
    {
        'id': 'trader',
        'name': 'Trader',
        'category': 'business',
        'weight': 0.08,
        'income_params': {
            'etb_monthly_base': 15000,
            'log_normal_sigma': 0.6,
            'experience_multiplier_range': (0.8, 3.0)
        },
        'foreign_income_probability': 0.1,
        'remote_work_probability': 0.02,
        'typical_employment_types': ['self_employed', 'business_owner']
    },
    {
        'id': 'import_export',
        'name': 'Import/Export',
        'category': 'business',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 60000,
            'log_normal_sigma': 0.7,
            'experience_multiplier_range': (0.8, 4.0)
        },
        'foreign_income_probability': 0.8,
        'remote_work_probability': 0.2,
        'typical_employment_types': ['business_owner', 'self_employed']
    },
    {
        'id': 'marketing_specialist',
        'name': 'Marketing Specialist',
        'category': 'business',
        'weight': 0.02,
        'income_params': {
            'etb_monthly_base': 16000,
            'log_normal_sigma': 0.3,
            'experience_multiplier_range': (0.8, 2.5)
        },
        'foreign_income_probability': 0.05,
        'remote_work_probability': 0.1,
        'typical_employment_types': ['employed', 'freelancer']
    },
    {
        'id': 'salesperson',
        'name': 'Salesperson',
        'category': 'business',
        'weight': 0.06,
        'income_params': {
            'etb_monthly_base': 10000,
            'log_normal_sigma': 0.4,
            'experience_multiplier_range': (0.8, 2.5)
        },
        'foreign_income_probability': 0.01,
        'remote_work_probability': 0.02,
        'typical_employment_types': ['employed', 'self_employed']
    },
    {
        'id': 'real_estate_agent',
        'name': 'Real Estate Agent',
        'category': 'business',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 25000,
            'log_normal_sigma': 0.6,
            'experience_multiplier_range': (0.5, 3.0)
        },
        'foreign_income_probability': 0.05,
        'remote_work_probability': 0.05,
        'typical_employment_types': ['self_employed', 'freelancer']
    },
    {
        'id': 'designer',
        'name': 'Designer',
        'category': 'creative',
        'weight': 0.015,
        'income_params': {
            'etb_monthly_base': 15000,
            'log_normal_sigma': 0.3,
            'experience_multiplier_range': (0.8, 2.5)
        },
        'foreign_income_probability': 0.2,
        'remote_work_probability': 0.3,
        'typical_employment_types': ['employed', 'freelancer']
    },
    {
        'id': 'ui_ux_designer',
        'name': 'UI/UX Designer',
        'category': 'creative',
        'weight': 0.008,
        'income_params': {
            'etb_monthly_base': 22000,
            'log_normal_sigma': 0.3,
            'experience_multiplier_range': (0.9, 3.0)
        },
        'foreign_income_probability': 0.3,
        'remote_work_probability': 0.4,
        'typical_employment_types': ['employed', 'freelancer', 'contractor']
    },
    {
        'id': 'content_creator',
        'name': 'Content Creator',
        'category': 'creative',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 12000,
            'log_normal_sigma': 0.6,
            'experience_multiplier_range': (0.5, 4.0)
        },
        'foreign_income_probability': 0.4,
        'remote_work_probability': 0.6,
        'typical_employment_types': ['freelancer', 'self_employed']
    },
    {
        'id': 'photographer',
        'name': 'Photographer',
        'category': 'creative',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 12000,
            'log_normal_sigma': 0.4,
            'experience_multiplier_range': (0.8, 2.5)
        },
        'foreign_income_probability': 0.05,
        'remote_work_probability': 0.05,
        'typical_employment_types': ['self_employed', 'freelancer']
    },
    {
        'id': 'journalist',
        'name': 'Journalist',
        'category': 'creative',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 12000,
            'log_normal_sigma': 0.25,
            'experience_multiplier_range': (0.8, 2.0)
        },
        'foreign_income_probability': 0.1,
        'remote_work_probability': 0.1,
        'typical_employment_types': ['employed', 'freelancer']
    },
    {
        'id': 'driver',
        'name': 'Driver',
        'category': 'service',
        'weight': 0.06,
        'income_params': {
            'etb_monthly_base': 6000,
            'log_normal_sigma': 0.15,
            'experience_multiplier_range': (0.9, 1.5)
        },
        'foreign_income_probability': 0.0,
        'remote_work_probability': 0.0,
        'typical_employment_types': ['employed', 'self_employed']
    },
    {
        'id': 'retail_worker',
        'name': 'Retail Worker',
        'category': 'service',
        'weight': 0.08,
        'income_params': {
            'etb_monthly_base': 5000,
            'log_normal_sigma': 0.15,
            'experience_multiplier_range': (0.9, 1.3)
        },
        'foreign_income_probability': 0.0,
        'remote_work_probability': 0.0,
        'typical_employment_types': ['employed', 'part_time']
    },
    {
        'id': 'hotel_worker',
        'name': 'Hotel Worker',
        'category': 'service',
        'weight': 0.03,
        'income_params': {
            'etb_monthly_base': 6000,
            'log_normal_sigma': 0.2,
            'experience_multiplier_range': (0.9, 1.6)
        },
        'foreign_income_probability': 0.02,
        'remote_work_probability': 0.0,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'bank_teller',
        'name': 'Bank Teller',
        'category': 'service',
        'weight': 0.01,
        'income_params': {
            'etb_monthly_base': 12000,
            'log_normal_sigma': 0.15,
            'experience_multiplier_range': (0.9, 1.8)
        },
        'foreign_income_probability': 0.0,
        'remote_work_probability': 0.0,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'farmer',
        'name': 'Farmer',
        'category': 'agriculture',
        'weight': 0.1,
        'income_params': {
            'etb_monthly_base': 8000,
            'log_normal_sigma': 0.5,
            'experience_multiplier_range': (0.8, 2.0)
        },
        'foreign_income_probability': 0.0,
        'remote_work_probability': 0.0,
        'typical_employment_types': ['self_employed']
    },
    {
        'id': 'agricultural_engineer',
        'name': 'Agricultural Engineer',
        'category': 'agriculture',
        'weight': 0.005,
        'income_params': {
            'etb_monthly_base': 16000,
            'log_normal_sigma': 0.25,
            'experience_multiplier_range': (0.8, 2.5)
        },
        'foreign_income_probability': 0.05,
        'remote_work_probability': 0.05,
        'typical_employment_types': ['employed', 'contractor']
    },
    {
        'id': 'government_employee',
        'name': 'Government Employee',
        'category': 'government',
        'weight': 0.08,
        'income_params': {
            'etb_monthly_base': 10000,
            'log_normal_sigma': 0.2,
            'experience_multiplier_range': (0.8, 2.2)
        },
        'foreign_income_probability': 0.0,
        'remote_work_probability': 0.0,
        'typical_employment_types': ['employed']
    },
    {
        'id': 'ngo_worker',
        'name': 'NGO Worker',
        'category': 'government',
        'weight': 0.02,
        'income_params': {
            'etb_monthly_base': 25000,
            'log_normal_sigma': 0.3,
            'experience_multiplier_range': (0.9, 2.5)
        },
        'foreign_income_probability': 0.2,
        'remote_work_probability': 0.1,
        'typical_employment_types': ['employed', 'contractor']
    },
    {
        'id': 'student',
        'name': 'Student',
        'category': 'other',
        'weight': 0.10,
        'income_params': {
            'etb_monthly_base': 2000,
            'log_normal_sigma': 0.5,
            'experience_multiplier_range': (0.8, 1.2)
        },
        'foreign_income_probability': 0.05,
        'remote_work_probability': 0.1,
        'typical_employment_types': ['student', 'part_time', 'freelancer']
    },
    {
        'id': 'freelancer',
        'name': 'Freelancer',
        'category': 'other',
        'weight': 0.02,
        'income_params': {
            'etb_monthly_base': 15000,
            'log_normal_sigma': 0.6,
            'experience_multiplier_range': (0.5, 3.5)
        },
        'foreign_income_probability': 0.4,
        'remote_work_probability': 0.8,
        'typical_employment_types': ['freelancer']
    },
    {
        'id': 'construction_worker',
        'name': 'Construction Worker',
        'category': 'other',
        'weight': 0.04,
        'income_params': {
            'etb_monthly_base': 7000,
            'log_normal_sigma': 0.2,
            'experience_multiplier_range': (0.8, 1.5)
        },
        'foreign_income_probability': 0.0,
        'remote_work_probability': 0.0,
        'typical_employment_types': ['employed', 'self_employed', 'part_time']
    }
]

def get_random_occupation(rng: np.random.Generator) -> Dict[str, Any]:
    weights = [occ['weight'] for occ in OCCUPATIONS]
    total_weight = sum(weights)
    norm_weights = [w / total_weight for w in weights]
    choice = rng.choice(len(OCCUPATIONS), p=norm_weights)
    return OCCUPATIONS[choice]

def calculate_salary(rng: np.random.Generator, occupation: Dict[str, Any], experience_years: float, city: str, employment_type: str) -> float:
    params = occupation['income_params']
    base = params['etb_monthly_base']
    sigma = params['log_normal_sigma']
    exp_min, exp_max = params['experience_multiplier_range']
    
    mu = np.log(base)
    random_base = rng.lognormal(mean=mu, sigma=sigma)
    
    exp_mult = exp_min + (exp_max - exp_min) * (min(experience_years, 30) / 30)
    
    # City modifier
    city_mult = 1.0
    if city == 'Addis Ababa':
        city_mult = 1.3
    elif city in ['Dire Dawa', 'Mekelle', 'Hawassa', 'Adama', 'Bahir Dar']:
        city_mult = 1.1
    
    # Emp modifier
    emp_mult = 1.0
    if employment_type == 'part_time':
        emp_mult = 0.5
    elif employment_type == 'freelancer':
        emp_mult = rng.uniform(0.5, 1.5)
        
    return random_base * exp_mult * city_mult * emp_mult

def get_occupation_by_id(occupation_id: str) -> Dict[str, Any]:
    for occ in OCCUPATIONS:
        if occ['id'] == occupation_id:
            return occ
    return OCCUPATIONS[0] # Fallback

def get_occupations_batch(rng: np.random.Generator, count: int) -> List[Dict[str, Any]]:
    weights = [occ['weight'] for occ in OCCUPATIONS]
    total_weight = sum(weights)
    norm_weights = [w / total_weight for w in weights]
    choices = rng.choice(len(OCCUPATIONS), size=count, p=norm_weights)
    return [OCCUPATIONS[i] for i in choices]
