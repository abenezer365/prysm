import numpy as np
from typing import Dict, List, Tuple, Optional, Any

# Language group probability weights reflecting Ethiopian demographics
LANGUAGE_GROUP_WEIGHTS: Dict[str, float] = {
    "oromo": 0.34,
    "amharic": 0.27,
    "somali": 0.06,
    "tigrinya": 0.06,
    "sidama": 0.04,
    "gurage": 0.03,
    "wolayta": 0.02,
    "afar": 0.02,
    "hadiya": 0.02,
    "gambela": 0.01,
    "other": 0.13
}

MALE_FIRST_NAMES: Dict[str, List[str]] = {
    "amharic": [
        "Abebe", "Dawit", "Samuel", "Natnael", "Yonas", "Biruk", "Nahom", "Daniel", "Yonatan", "Mulugeta",
        "Getachew", "Kebede", "Tadesse", "Bekele", "Hailu", "Tesfaye", "Girma", "Wondimu", "Asefa", "Meseret",
        "Dereje", "Solomon", "Abraham", "Yohannes", "Henok", "Mikael", "Biniam", "Ermias", "Eyob", "Fasil",
        "Gebre", "Habte", "Isayas", "Kiros", "Lemma", "Mengistu", "Negash", "Petros", "Fikru", "Alemayehu",
        "Berhanu", "Desalegn", "Fantahun", "Gebremariam", "Habtamu", "Kassahun", "Mekonnen", "Shiferaw", "Teferi", "Worku",
        "Zelalem", "Amanuel", "Bereket", "Dagmawi", "Ephrem", "Fitsum", "Gebrehiwot", "Hagos", "Jemal", "Kidane",
        "Legesse", "Mamo", "Neway", "Paulos", "Robel", "Seleshi", "Teshome", "Wubet", "Yared", "Zerihun",
        "Abrham", "Belay", "Chala", "Dawud", "Eskindir", "Feleke", "Gizachew", "Hailemichael", "Iyasu", "Kibrom",
        "Tilahun", "Mulatu", "Ewnetu", "Zewdu", "Admasu"
    ],
    "oromo": [
        "Chaltu", "Gammachu", "Hundessa", "Lemi", "Bonsa", "Daba", "Gutu", "Jarra", "Kuma", "Olana",
        "Tura", "Wako", "Boru", "Dinka", "Gada", "Hika", "Kedir", "Liban", "Megersa", "Nagawo",
        "Oba", "Roba", "Sima", "Tola", "Warku", "Abdi", "Bati", "Caalaa", "Dama", "Elema",
        "Fayera", "Garo", "Haro", "Ibsa", "Jilo", "Kaso", "Lata", "Moti", "Nado", "Obbo",
        "Raga", "Sori", "Teso", "Urgo", "Wami", "Abba", "Bako", "Chali", "Dadi", "Eshetu",
        "Fita", "Galata", "Hunde", "Irko", "Jaba", "Kebena", "Lamu", "Merera", "Naga", "Gutama",
        "Tolessa", "Fikadu", "Birbissa", "Tullu", "Mormor"
    ],
    "tigrinya": [
        "Amanuel", "Berhane", "Dawit", "Efrem", "Filmon", "Gebremedhin", "Haile", "Iyasu", "Kahsay", "Leul",
        "Mehari", "Negasi", "Okbay", "Petros", "Russom", "Semere", "Tekle", "Weldeab", "Yemane", "Zerabruk",
        "Abrham", "Berhe", "Debesay", "Estifanos", "Fesseha", "Ghirmay", "Hadgu", "Iyob", "Kidane", "Mebrahtu",
        "Negusse", "Ogbazghi", "Redae", "Seyoum", "Tesfamariam", "Weldemariam", "Yohannes", "Zekarias", "Asgedom", "Birhane",
        "Desta", "Eyasu", "Fissehaye", "Goitom", "Habtom", "Kinfe", "Mengsteab", "Rezene", "Seyum", "Tesfalem",
        "Yemane", "Ghidey", "Aregawi", "Mulu"
    ],
    "sidama": [
        "Adula", "Assefa", "Balcha", "Bekele", "Chamo", "Dada", "Dale", "Damo", "Desta", "Fisseha",
        "Gebre", "Girma", "Hailu", "Kiros", "Lema", "Mamo", "Megersa", "Melese", "Mulu", "Negash",
        "Oda", "Roba", "Shanko", "Tadesse", "Taye", "Tefera", "Tesfaye", "Wako", "Yohannes", "Zeleke",
        "Fikru", "Guta"
    ],
    "gurage": [
        "Abebe", "Alem", "Ali", "Assefa", "Bekele", "Bereket", "Dawit", "Dereje", "Fikru", "Gebre",
        "Girma", "Habtamu", "Hailu", "Jemal", "Kedir", "Lemma", "Mamo", "Mekonnen", "Melese", "Mesfin",
        "Mulugeta", "Negash", "Omar", "Osman", "Said", "Samuel", "Seid", "Solomon", "Tadesse", "Tesfaye",
        "Zelalem", "Zewdu"
    ],
    "wolayta": [
        "Abe", "Amanuel", "Assefa", "Bekele", "Desta", "Elito", "Ephrem", "Eyasu", "Girma", "Hailu",
        "Lema", "Mamo", "Markos", "Melese", "Mulu", "Paulos", "Petros", "Samuel", "Solomon", "Tadesse",
        "Taye", "Tefera", "Tesfaye", "Tona", "Yohannes", "Zeleke"
    ],
    "somali": [
        "Abdi", "Abdullahi", "Ahmed", "Ali", "Farah", "Hassan", "Hussein", "Ibrahim", "Jama", "Mahmoud",
        "Mohamed", "Muse", "Nur", "Omar", "Osman", "Said", "Samatar", "Shirwa", "Suleiman", "Warsame",
        "Yusuf", "Guled", "Khalid", "Liban", "Roble", "Salad"
    ],
    "afar": [
        "Abdallah", "Abu", "Ahmed", "Ali", "Alo", "Amina", "Hamed", "Hassan", "Hussein", "Ibrahim",
        "Ismail", "Kamil", "Mahmoud", "Mohamed", "Musa", "Omar", "Osman", "Said", "Saleh", "Yusuf",
        "Yassin"
    ],
    "hadiya": [
        "Amanuel", "Assefa", "Bekele", "Beyene", "Desta", "Ephrem", "Gebre", "Girma", "Hailu", "Lema",
        "Mamo", "Melese", "Mulu", "Paulos", "Petros", "Samuel", "Solomon", "Tadesse", "Tefera", "Tesfaye",
        "Yohannes"
    ],
    "gambela": [
        "Okelo", "Obang", "Ojulu", "Omod", "Oman", "Okoth", "Omot", "Odola", "Opiew", "Obala",
        "Akelo", "Abula", "Othow", "Gilo", "Cham", "Gatluak"
    ],
    "other": [
        "John", "David", "Michael", "Paul", "Peter", "James", "Robert", "Joseph", "Thomas", "Charles"
    ]
}

FEMALE_FIRST_NAMES: Dict[str, List[str]] = {
    "amharic": [
        "Bethel", "Hana", "Mekdes", "Meron", "Selam", "Tigist", "Liya", "Rahel", "Eden", "Sara",
        "Mahlet", "Bezawit", "Helina", "Yordanos", "Rediet", "Kidist", "Tsion", "Nardos", "Seble", "Eyerusalem",
        "Meseret", "Aida", "Birtukan", "Chaltu", "Dagmawit", "Emebet", "Firehiwot", "Genet", "Hirut", "Konjit",
        "Lulit", "Meaza", "Nigist", "Rahwa", "Senait", "Tizita", "Wude", "Yemsrach", "Zenebech", "Alemitu",
        "Amsale", "Askale", "Aster", "Aynalem", "Azeb", "Belaynesh", "Bogalech", "Buzunesh", "Etenesh", "Fikre",
        "Frehiwot", "Mulu", "Netsanet", "Roman", "Samrawit", "Tadelech", "Tarik", "Tiruwork", "Tsehay", "Welela",
        "Wengel", "Worknesh", "Yalemzewd", "Yeshi", "Yodit", "Zewditu", "Zufan", "Ababa", "Almaz", "Amleset",
        "Asnakech", "Ayinalem", "Bekelech", "Bizunesh", "Desta", "Elfinesh", "Haregewoin", "Kalkidan", "Lakech", "Makeda"
    ],
    "oromo": [
        "Chaltu", "Ayantu", "Biftu", "Boontu", "Caaltu", "Dureti", "Elellee", "Fasika", "Gale", "Hawwi",
        "Ibsitu", "Jalallee", "Kello", "Lelise", "Magartu", "Naol", "Obsi", "Qonjit", "Robe", "Sena",
        "Tigist", "Urgi", "Walabuu", "Xajjii", "Yadii", "Zala", "Arfasi", "Baredu", "Bokku", "Cali",
        "Dara", "Eebbisee", "Furtu", "Gudatu", "Hunde", "Ifa", "Jitu", "Kuli", "Lensa", "Murtu",
        "Nage", "Oka", "Qabale", "Rabia", "Siko", "Toltu", "Urge", "Wagari", "Bilan", "Gamte",
        "Hawi", "Kenna", "Lalise", "Saba", "Tola", "Yero"
    ],
    "tigrinya": [
        "Almaz", "Amleset", "Askale", "Aster", "Awet", "Azeb", "Blen", "Bisrat", "Eden", "Elsa",
        "Feven", "Freweyni", "Genet", "Haben", "Hadas", "Haregu", "Helen", "Hermela", "Hirut", "Kisanet",
        "Kokeb", "Lemlem", "Lidya", "Luam", "Lwam", "Mahlet", "Makda", "Marta", "Meaza", "Meron",
        "Mieraf", "Mulu", "Nigisti", "Rahel", "Rahwa", "Rigbe", "Roman", "Ruta", "Saba", "Salina",
        "Samrawit", "Sara", "Selam", "Selamawit", "Senait", "Sinit", "Soliana", "Tirhas", "Tsehay", "Winta",
        "Yodit", "Yordanos", "Zaid"
    ],
    "sidama": [
        "Ayantu", "Burtukan", "Desta", "Elfinesh", "Genet", "Hirut", "Mulu", "Netsanet", "Tigist", "Tsehay",
        "Wude", "Zenebech", "Alemitu", "Askale", "Aster", "Azeb", "Belaynesh", "Etenesh", "Mekdes", "Roman",
        "Senait", "Tadelech", "Tiruwork", "Worknesh", "Yeshi", "Yodit", "Zewditu", "Almaz", "Bekelech", "Bizunesh",
        "Ayana"
    ],
    "gurage": [
        "Aida", "Alemitu", "Almaz", "Aster", "Azeb", "Bekelech", "Belaynesh", "Bizunesh", "Desta", "Elfinesh",
        "Etenesh", "Genet", "Hirut", "Mekdes", "Mulu", "Netsanet", "Roman", "Senait", "Tadelech", "Tigist",
        "Tiruwork", "Tsehay", "Worknesh", "Wude", "Yeshi", "Yodit", "Zenebech", "Zewditu", "Amsale", "Askale",
        "Zufan", "Bogalech"
    ],
    "wolayta": [
        "Alemitu", "Almaz", "Aster", "Azeb", "Bekelech", "Bizunesh", "Desta", "Elfinesh", "Etenesh", "Genet",
        "Hirut", "Mekdes", "Mulu", "Netsanet", "Roman", "Senait", "Tadelech", "Tigist", "Tsehay", "Worknesh",
        "Wude", "Yeshi", "Yodit", "Zenebech", "Zewditu", "Tena", "Damo"
    ],
    "somali": [
        "Amina", "Asho", "Batulo", "Cawo", "Deqo", "Fadumo", "Farhiya", "Halima", "Hawa", "Hodan",
        "Iftin", "Khadija", "Layla", "Maryan", "Nasha", "Nimco", "Nuur", "Qali", "Ruqiyo", "Safiyo",
        "Sahra", "Shukri", "Ubah", "Xaliimo", "Yurub", "Zahra"
    ],
    "afar": [
        "Amina", "Asha", "Fatima", "Halima", "Hawa", "Khadija", "Mariam", "Safia", "Zahra", "Zainab",
        "Aliya", "Asma", "Ayisha", "Faduma", "Farhiya", "Hodan", "Layla", "Nura", "Ruqia", "Sadia",
        "Suhaila", "Ado"
    ],
    "hadiya": [
        "Alemitu", "Almaz", "Aster", "Azeb", "Bekelech", "Bizunesh", "Desta", "Elfinesh", "Etenesh", "Genet",
        "Hirut", "Mekdes", "Mulu", "Netsanet", "Roman", "Senait", "Tadelech", "Tigist", "Tsehay", "Worknesh",
        "Zenebech"
    ],
    "gambela": [
        "Akelo", "Ojulu", "Omod", "Awili", "Ajulu", "Ariat", "Atoch", "Awar", "Nyibol", "Nyalok",
        "Nyapal", "Nyagak", "Nyamoch", "Nyaguwa", "Nyamal"
    ],
    "other": [
        "Mary", "Sarah", "Elizabeth", "Ruth", "Esther", "Martha", "Rachel", "Hannah", "Rebecca", "Naomi"
    ]
}

FATHER_NAMES: List[str] = [
    "Abebe", "Dawit", "Samuel", "Natnael", "Yonas", "Biruk", "Nahom", "Daniel", "Yonatan", "Mulugeta",
    "Getachew", "Kebede", "Tadesse", "Bekele", "Hailu", "Tesfaye", "Girma", "Wondimu", "Asefa", "Meseret",
    "Dereje", "Solomon", "Abraham", "Yohannes", "Henok", "Mikael", "Biniam", "Ermias", "Eyob", "Fasil",
    "Gebre", "Habte", "Isayas", "Kiros", "Lemma", "Mengistu", "Negash", "Petros", "Fikru", "Alemayehu",
    "Berhanu", "Desalegn", "Fantahun", "Gebremariam", "Habtamu", "Kassahun", "Mekonnen", "Shiferaw", "Teferi", "Worku",
    "Zelalem", "Amanuel", "Bereket", "Dagmawi", "Ephrem", "Fitsum", "Gebrehiwot", "Hagos", "Jemal", "Kidane",
    "Legesse", "Mamo", "Neway", "Paulos", "Robel", "Seleshi", "Teshome", "Wubet", "Yared", "Zerihun",
    "Abrham", "Belay", "Chala", "Dawud", "Eskindir", "Feleke", "Gizachew", "Hailemichael", "Iyasu", "Kibrom",
    "Chaltu", "Gammachu", "Hundessa", "Lemi", "Bonsa", "Daba", "Gutu", "Jarra", "Kuma", "Olana",
    "Tura", "Wako", "Boru", "Dinka", "Gada", "Hika", "Kedir", "Liban", "Megersa", "Nagawo",
    "Oba", "Roba", "Sima", "Tola", "Warku", "Abdi", "Bati", "Caalaa", "Dama", "Elema",
    "Fayera", "Garo", "Haro", "Ibsa", "Jilo", "Kaso", "Lata", "Moti", "Nado", "Obbo",
    "Raga", "Sori", "Teso", "Urgo", "Wami", "Abba", "Bako", "Chali", "Dadi", "Eshetu",
    "Fita", "Galata", "Hunde", "Irko", "Jaba", "Kebena", "Lamu", "Merera", "Naga", "Amanuel",
    "Berhane", "Efrem", "Filmon", "Gebremedhin", "Haile", "Kahsay", "Leul", "Mehari", "Negasi",
    "Okbay", "Russom", "Semere", "Tekle", "Weldeab", "Yemane", "Zerabruk", "Berhe", "Debesay", "Estifanos",
    "Fesseha", "Ghirmay", "Hadgu", "Iyob", "Mebrahtu", "Negusse", "Ogbazghi", "Redae", "Seyoum", "Tesfamariam",
    "Weldemariam", "Zekarias", "Asgedom", "Birhane", "Desta", "Eyasu", "Fissehaye", "Goitom", "Habtom", "Kinfe",
    "Mengsteab", "Rezene", "Seyum", "Tesfalem", "Adula", "Assefa", "Balcha", "Chamo", "Dada", "Dale",
    "Damo", "Shanko", "Taye", "Tefera", "Zeleke", "Alem", "Ali", "Mesfin", "Omar", "Osman",
    "Said", "Seid", "Zewdu", "Abe", "Elito", "Markos", "Tona", "Abdullahi", "Ahmed", "Farah",
    "Hassan", "Hussein", "Ibrahim", "Jama", "Mahmoud", "Mohamed", "Muse", "Nur", "Samatar", "Shirwa",
    "Suleiman", "Warsame", "Yusuf", "Guled", "Khalid", "Roble", "Salad", "Abdallah", "Abu", "Alo",
    "Hamed", "Ismail", "Kamil", "Musa", "Saleh", "Yassin", "Beyene", "Okelo", "Obang", "Ojulu",
    "Omod", "Oman", "Okoth", "Omot", "Odola", "Opiew", "Obala", "Akelo", "Abula", "Othow",
    "Gilo", "Cham", "Gatluak", "Tilahun", "Mulatu", "Ewnetu", "Admasu", "Gutama", "Tolessa", "Fikadu",
    "Birbissa", "Tullu", "Mormor", "Ghidey", "Aregawi", "Mulu", "Fikru", "Guta", "John", "David",
    "Michael", "Paul", "Peter", "James", "Robert", "Joseph", "Thomas", "Charles"
]

def get_language_group(rng: np.random.Generator) -> str:
    """
    Returns a weighted random language group based on Ethiopian demographics.
    """
    groups = list(LANGUAGE_GROUP_WEIGHTS.keys())
    weights = list(LANGUAGE_GROUP_WEIGHTS.values())
    
    # Normalize weights to ensure they sum exactly to 1.0
    total = sum(weights)
    normalized_weights = [w / total for w in weights]
    
    return str(rng.choice(groups, p=normalized_weights))

def get_random_name(rng: np.random.Generator, gender: str, language_group: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Returns a tuple of (first_name, father_name, grandfather_name).
    """
    if language_group is None:
        language_group = get_language_group(rng)
        
    if language_group not in LANGUAGE_GROUP_WEIGHTS:
        language_group = "other"
        
    if gender.lower() == "female":
        first_names = FEMALE_FIRST_NAMES.get(language_group, FEMALE_FIRST_NAMES["other"])
    else:
        first_names = MALE_FIRST_NAMES.get(language_group, MALE_FIRST_NAMES["other"])
        
    first_name = str(rng.choice(first_names))
    father_name = str(rng.choice(FATHER_NAMES))
    grandfather_name = str(rng.choice(FATHER_NAMES))
    
    return first_name, father_name, grandfather_name

def get_full_name(rng: np.random.Generator, gender: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns a dictionary containing first_name, father_name, grandfather_name, gender, and language_group.
    """
    language_group = get_language_group(rng)
    
    if gender is None:
        gender = str(rng.choice(["male", "female"]))
        
    first_name, father_name, grandfather_name = get_random_name(rng, gender, language_group)
    
    return {
        "first_name": first_name,
        "father_name": father_name,
        "grandfather_name": grandfather_name,
        "gender": gender,
        "language_group": language_group
    }

def generate_names_batch(rng: np.random.Generator, count: int) -> List[Dict[str, Any]]:
    """
    Generates a batch of names efficiently.
    """
    # Pre-generate random attributes
    genders = rng.choice(["male", "female"], size=count)
    
    groups = list(LANGUAGE_GROUP_WEIGHTS.keys())
    weights = list(LANGUAGE_GROUP_WEIGHTS.values())
    total = sum(weights)
    normalized_weights = [w / total for w in weights]
    language_groups = rng.choice(groups, p=normalized_weights, size=count)
    
    results = []
    
    # Process batch
    for i in range(count):
        gender = genders[i]
        lang_group = language_groups[i]
        
        if gender == "female":
            first_names = FEMALE_FIRST_NAMES.get(lang_group, FEMALE_FIRST_NAMES["other"])
        else:
            first_names = MALE_FIRST_NAMES.get(lang_group, MALE_FIRST_NAMES["other"])
            
        first_name = str(rng.choice(first_names))
        father_name = str(rng.choice(FATHER_NAMES))
        grandfather_name = str(rng.choice(FATHER_NAMES))
        
        results.append({
            "first_name": first_name,
            "father_name": father_name,
            "grandfather_name": grandfather_name,
            "gender": gender,
            "language_group": lang_group
        })
        
    return results
