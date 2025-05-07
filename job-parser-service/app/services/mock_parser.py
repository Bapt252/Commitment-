"""
Module de mock parser pour le service de parsing de fiches de poste.
Utilisé pour les tests et le développement sans dépendance à OpenAI.
"""

import logging
import random
import hashlib
import os
import re
from typing import Dict, Any, List, Optional

# Setup logging
logger = logging.getLogger(__name__)

# Données fictives pour les mocks
MOCK_TITLES = [
    "Comptable général", "Auditeur financier", "Contrôleur de gestion",
    "Directeur financier", "Comptable fournisseurs", "Comptable clients",
    "Responsable comptabilité", "Fiscaliste", "Comptable unique",
    "Analyste financier", "Trésorier", "Développeur Python", "Développeur Java", 
    "Développeur Full Stack", "Data Scientist", "DevOps Engineer", "Chef de projet IT",
    "Product Owner", "UX/UI Designer", "Ingénieur QA", "Architecte technique"
]

MOCK_COMPANIES = [
    "FinTech Solutions", "Mondial Audit", "Comptex", "Groupe Finance Plus",
    "EuroFisc", "Gestion & Stratégie", "Audit Expert", "CompTrust",
    "Finance Consulting", "Expertise Comptable Pro", "TechInnovate", 
    "DataSphere", "CodeMasters", "Agile Solutions", "WebFactory", 
    "NextGen Tech", "Cloud Systems", "Digital Solutions"
]

MOCK_LOCATIONS = [
    "Paris", "Lyon", "Bordeaux", "Marseille", "Lille", "Toulouse",
    "Nantes", "Strasbourg", "Montpellier", "Nice", "Rennes", "Grenoble",
    "Sophia Antipolis", "Aix-en-Provence"
]

MOCK_CONTRACT_TYPES = [
    "CDI", "CDD", "Freelance", "Stage", "Alternance",
    "Temps partiel", "Temps plein"
]

MOCK_SECTORS = [
    "Finance & Comptabilité", "Technologie & IT", "Santé & Médical", 
    "Éducation & Formation", "Marketing & Communication", "RH & Recrutement",
    "Industrie & Production", "Commerce & Distribution", "Services juridiques",
    "Construction & Immobilier"
]

MOCK_COMPANY_SIZES = [
    "Startup (<10 employés)", "TPE (10-49 employés)", "PME (50-249 employés)",
    "ETI (250-4999 employés)", "Grande entreprise (5000+ employés)"
]

MOCK_SKILLS = {
    "Finance & Comptabilité": [
        "Comptabilité générale", "Comptabilité analytique", "Normes IFRS",
        "Audit financier", "Fiscalité", "Reporting", "Consolidation",
        "ERP financiers", "Contrôle de gestion", "Gestion de trésorerie",
        "Analyse financière", "Excel avancé", "Clôture comptable",
        "Bilan", "Liasse fiscale", "Budgétisation", "Analyse des coûts",
        "Déclarations fiscales", "Rapprochement bancaire"
    ],
    "Technologie & IT": [
        "Python", "JavaScript", "React", "NodeJS", "Java", "C#", ".NET",
        "AWS", "Azure", "Docker", "Kubernetes", "CI/CD", "DevOps",
        "Machine Learning", "Data Science", "SQL", "NoSQL", "Git",
        "Agile/Scrum", "RESTful API", "Microservices", "Test Driven Development"
    ],
    "Marketing & Communication": [
        "Marketing digital", "SEO/SEA", "Réseaux sociaux", "Google Analytics",
        "Content marketing", "CRM", "Adobe Creative Suite", "Growth hacking",
        "Gestion de campagnes", "Marketing automation", "UX/UI Design",
        "Brand management", "Marketing stratégique", "Copywriting"
    ]
}

MOCK_REQUIREMENTS = [
    "DCG / DSCG", "Master CCA", "Diplôme de comptabilité", "Expertise comptable",
    "3-5 ans d'expérience", "Anglais professionnel", "Expérience en cabinet",
    "Connaissance de SAP", "Maîtrise d'Excel", "Rigueur et organisation",
    "Diplôme d'ingénieur", "Master en informatique", "Formation Bac+5",
    "Certification AWS/Azure", "Esprit d'équipe"
]

MOCK_BENEFITS = [
    "Tickets restaurant", "Mutuelle d'entreprise", "RTT",
    "Possibilité de télétravail", "Participation", "Intéressement",
    "Prime annuelle", "Formation continue", "Plan d'épargne entreprise",
    "Horaires flexibles", "13ème mois", "Bonus annuel", "Salle de sport",
    "Séminaires d'entreprise", "Ambiance startup", "Équipe internationale"
]

def extract_job_info_from_text(job_text: Optional[str]) -> Dict[str, Any]:
    """Tente d'extraire des informations pertinentes du texte de la fiche de poste
    
    Args:
        job_text: Texte de la fiche de poste
        
    Returns:
        Dict[str, Any]: Informations extraites
    """
    extracted = {}
    
    if not job_text:
        return extracted
    
    job_text_lower = job_text.lower()
    
    # Recherche de mots-clés pour le secteur
    sectors_keywords = {
        "Finance & Comptabilité": ["comptabilité", "finance", "audit", "fiscal", "trésorerie", "comptable"],
        "Technologie & IT": ["développeur", "informatique", "tech", "logiciel", "data", "code", "python", "java", "javascript"],
        "Marketing & Communication": ["marketing", "communication", "social media", "digital", "brand", "marque", "community"],
        "RH & Recrutement": ["ressources humaines", "recrutement", "talent", "rh", "carrière", "paie"],
        "Industrie & Production": ["industrie", "production", "usine", "manufacturing", "qualité", "maintenance"],
    }
    
    for sector, keywords in sectors_keywords.items():
        if any(keyword in job_text_lower for keyword in keywords):
            extracted["sector"] = sector
            break
    
    # Recherche de titres de poste courants
    title_patterns = [
        r"(?:recherch(?:e|ons)|offre d'emploi)[^\n.]*?([^\n.]+?(?:développeur|ingénieur|comptable|auditeur|consultant|chef de projet|manager|directeur)[^\n.]*?)(?:$|\n|\.|pour)",
        r"(?:poste de|profil)[^\n.]*?([^\n.]+?(?:développeur|ingénieur|comptable|auditeur|consultant|chef de projet|manager|directeur)[^\n.]*?)(?:$|\n|\.|h/f)",
        r"([^\n.]*?(?:développeur|ingénieur|comptable|auditeur|consultant|chef de projet|manager|directeur)[^\n.]*)(?:\s*\(h/f\)|\s*h/f)"
    ]
    
    for pattern in title_patterns:
        matches = re.findall(pattern, job_text_lower)
        if matches:
            # Nettoyer le résultat
            title = matches[0].strip()
            # Capitaliser le titre
            title = " ".join(word.capitalize() for word in title.split())
            extracted["title"] = title
            break
    
    # Recherche de lieu
    location_pattern = r"(?:lieu|localisation|basé à|site de travail|poste basé).*?(?:à|en|au)\s+([A-Za-zÀ-ÿ\s-]+?)(?:\s|\.|\n|$)"
    location_matches = re.findall(location_pattern, job_text_lower)
    if location_matches:
        location = location_matches[0].strip().capitalize()
        for known_location in MOCK_LOCATIONS:
            if known_location.lower() in location.lower():
                extracted["location"] = known_location
                break
        if "location" not in extracted:
            extracted["location"] = location
    
    # Recherche de type de contrat
    contract_pattern = r"(?:type de contrat|contrat)[^\n.]*?(CDI|CDD|Stage|Alternance|Freelance|Intérim)"
    contract_matches = re.findall(contract_pattern, job_text_lower)
    if contract_matches:
        extracted["contract_type"] = contract_matches[0]
    
    # Recherche d'informations sur le salaire
    salary_pattern = r"(?:salaire|rémunération)[^\n.]*?(\d+[^\n.]*?(?:€|euros|k€|k))"
    salary_matches = re.findall(salary_pattern, job_text_lower)
    if salary_matches:
        extracted["salary_info"] = salary_matches[0].strip()
    
    # Recherche d'expérience requise
    experience_pattern = r"(?:expérience)[^\n.]*?(\d+[^\n.]*?(?:an|année|ans|mois))"
    experience_matches = re.findall(experience_pattern, job_text_lower)
    if experience_matches:
        extracted["experience"] = experience_matches[0].strip()
    
    return extracted

def get_mock_job_data(job_text: str = None, filename: str = None) -> Dict[str, Any]:
    """Génère des données de fiche de poste fictives mais réalistes pour les tests
    
    Args:
        job_text: Texte de la fiche de poste (utilisé pour générer un hash déterministe)
        filename: Nom du fichier (utilisé comme fallback pour le hash)
        
    Returns:
        Dict[str, Any]: Données structurées fictives simulant l'analyse d'une fiche de poste
    """
    # Générer un hash déterministe basé sur l'entrée pour avoir une cohérence dans les mocks
    seed_text = job_text or filename or str(random.randint(1, 100000))
    seed = int(hashlib.md5(seed_text.encode('utf-8')).hexdigest(), 16) % 10000
    random.seed(seed)
    
    # Extraire des informations du texte si disponible
    extracted_info = {}
    if job_text:
        extracted_info = extract_job_info_from_text(job_text)
        logger.info(f"Informations extraites: {extracted_info}")
    
    # Définir le secteur (extrait ou aléatoire)
    sector = extracted_info.get("sector", random.choice(MOCK_SECTORS))
    
    # Simuler différents types d'offres
    is_junior = random.random() < 0.3
    is_senior = random.random() < 0.3
    is_manager = random.random() < 0.2
    
    # Utiliser le titre extrait ou en générer un cohérent avec le niveau
    if "title" in extracted_info:
        title = extracted_info["title"]
    else:
        base_title = random.choice(MOCK_TITLES)
        if is_junior:
            title = f"Assistant {base_title}" if random.random() < 0.5 else f"{base_title} Junior"
        elif is_senior:
            title = f"{base_title} Senior" if random.random() < 0.5 else f"{base_title} Confirmé"
        elif is_manager:
            title = f"Responsable {base_title}" if random.random() < 0.5 else f"Manager {base_title}"
        else:
            title = base_title
    
    # Déterminer les compétences basées sur le secteur
    sector_skills = MOCK_SKILLS.get(sector, MOCK_SKILLS["Technologie & IT"])
    
    # Générer des compétences requises et souhaitées
    num_required = random.randint(3, 6)
    num_preferred = random.randint(2, 5)
    
    all_skills = list(sector_skills)
    random.shuffle(all_skills)
    
    required_skills = all_skills[:num_required]
    preferred_skills = [skill for skill in all_skills[num_required:num_required+num_preferred] 
                       if skill not in required_skills]
    
    # Générer des responsabilités basées sur le titre et le niveau
    responsibilities = generate_responsibilities(title, sector, is_junior, is_senior, is_manager)
    
    # Générer des prérequis cohérents avec le niveau et le secteur
    requirements = generate_requirements(sector, is_junior, is_senior, is_manager)
    
    # Générer des avantages
    num_benefits = random.randint(3, 7)
    benefits = random.sample(MOCK_BENEFITS, num_benefits)
    
    # Politique de télétravail et salaire
    remote_options = [
        "Pas de télétravail", "1 jour par semaine", "2 jours par semaine", 
        "3 jours par semaine", "Télétravail possible", "Full remote"
    ]
    remote_policy = random.choice(remote_options)
    
    # Utiliser l'information de salaire extraite ou générer une fourchette de salaire basée sur le niveau
    if "salary_info" in extracted_info:
        salary_range = extracted_info["salary_info"]
    else:
        if "Finance" in sector:
            if is_junior:
                base_salary = random.randint(25, 35) * 1000
            elif is_senior:
                base_salary = random.randint(45, 60) * 1000
            elif is_manager:
                base_salary = random.randint(65, 95) * 1000
            else:
                base_salary = random.randint(35, 50) * 1000
        elif "Technologie" in sector:
            if is_junior:
                base_salary = random.randint(30, 40) * 1000
            elif is_senior:
                base_salary = random.randint(50, 70) * 1000
            elif is_manager:
                base_salary = random.randint(70, 100) * 1000
            else:
                base_salary = random.randint(40, 60) * 1000
        else:
            if is_junior:
                base_salary = random.randint(25, 35) * 1000
            elif is_senior:
                base_salary = random.randint(40, 55) * 1000
            elif is_manager:
                base_salary = random.randint(60, 85) * 1000
            else:
                base_salary = random.randint(30, 45) * 1000
                
        max_salary = base_salary + random.randint(5, 15) * 1000
        salary_range = f"{base_salary // 1000}K€ - {max_salary // 1000}K€"
    
    # Utiliser la localisation extraite ou en choisir une aléatoire
    location = extracted_info.get("location", random.choice(MOCK_LOCATIONS))
    
    # Utiliser le type de contrat extrait ou en choisir un aléatoire
    contract_type = extracted_info.get("contract_type", random.choice(MOCK_CONTRACT_TYPES))
    
    # Générer une description d'entreprise cohérente avec le secteur
    company_descriptions = {
        "Finance & Comptabilité": [
            "Cabinet d'expertise comptable reconnu pour son excellence dans le conseil fiscal.",
            "Entreprise leader en services financiers, accompagnant les grands groupes internationaux.",
            "Cabinet d'audit en pleine croissance, spécialisé dans les PME innovantes."
        ],
        "Technologie & IT": [
            "Startup en forte croissance développant des solutions cloud pour les entreprises.",
            "Éditeur de logiciels spécialisé dans les solutions de cybersécurité.",
            "Entreprise tech innovante créant des applications mobiles pour le secteur santé."
        ],
        "Marketing & Communication": [
            "Agence de communication digitale primée pour ses campagnes créatives.",
            "Cabinet de conseil en stratégie marketing pour les marques de luxe.",
            "Entreprise spécialisée dans le marketing d'influence et les réseaux sociaux."
        ]
    }
    
    sector_descriptions = company_descriptions.get(sector, company_descriptions["Technologie & IT"])
    company_description = random.choice(sector_descriptions)
    
    # Assembler le tout
    mock_data = {
        "title": title,
        "company": random.choice(MOCK_COMPANIES),
        "location": location,
        "sector": sector,
        "company_size": random.choice(MOCK_COMPANY_SIZES),
        "contract_type": contract_type,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "responsibilities": responsibilities,
        "requirements": requirements,
        "benefits": benefits,
        "salary_range": salary_range,
        "remote_policy": remote_policy,
        "application_process": "Envoyer CV et lettre de motivation",
        "company_description": company_description
    }
    
    logger.info(f"Données mock générées pour {filename or 'une fiche de poste'}")
    return mock_data

def generate_responsibilities(title: str, sector: str, is_junior: bool, is_senior: bool, is_manager: bool) -> List[str]:
    """Génère des responsabilités cohérentes avec le titre, le secteur et le niveau"""
    
    # Responsabilités par secteur
    sector_tasks = {
        "Finance & Comptabilité": {
            "common": [
                "Comptabilisation des factures",
                "Suivi des comptes fournisseurs/clients",
                "Préparation des déclarations fiscales",
                "Participation aux clôtures mensuelles et annuelles",
                "Rapprochements bancaires",
                "Suivi de la trésorerie"
            ],
            "senior": [
                "Supervision de l'équipe comptable",
                "Mise en place de procédures comptables",
                "Optimisation des processus financiers",
                "Collaboration avec les commissaires aux comptes",
                "Gestion de la relation avec l'administration fiscale",
                "Élaboration du reporting mensuel"
            ],
            "manager": [
                "Management d'une équipe de comptables",
                "Définition de la stratégie financière",
                "Pilotage des clôtures",
                "Relations avec les partenaires financiers",
                "Prise de décisions stratégiques",
                "Présentation des résultats financiers à la direction"
            ]
        },
        "Technologie & IT": {
            "common": [
                "Développement de nouvelles fonctionnalités",
                "Correction de bugs et maintenance du code",
                "Participation aux code reviews",
                "Rédaction de tests unitaires et d'intégration",
                "Participation aux cérémonies Agile",
                "Documentation technique"
            ],
            "senior": [
                "Conception d'architecture logicielle",
                "Mentorat des développeurs juniors",
                "Optimisation des performances des applications",
                "Mise en place de bonnes pratiques de développement",
                "Participation aux choix technologiques",
                "Développement de composants critiques"
            ],
            "manager": [
                "Gestion d'une équipe de développeurs",
                "Planification des sprints et des releases",
                "Coordination avec les autres départements",
                "Suivi de la qualité et des performances",
                "Veille technologique",
                "Mise en place de processus CI/CD"
            ]
        }
    }
    
    # Tâches spécifiques selon le titre
    title_tasks = {}
    if "auditeur" in title.lower():
        title_tasks = [
            "Réalisation de missions d'audit",
            "Analyse des risques financiers",
            "Contrôle interne",
            "Revue des procédures comptables",
            "Vérification de la conformité réglementaire"
        ]
    elif "développeur" in title.lower():
        if "python" in title.lower():
            title_tasks = [
                "Développement d'applications backend en Python",
                "Utilisation de frameworks comme Django ou Flask",
                "Intégration avec des bases de données SQL et NoSQL",
                "Mise en place d'API RESTful",
                "Déploiement sur des environnements cloud"
            ]
        elif "java" in title.lower():
            title_tasks = [
                "Développement d'applications d'entreprise en Java",
                "Utilisation de Spring Boot et Hibernate",
                "Conception de microservices",
                "Optimisation des performances JVM",
                "Intégration avec des systèmes existants"
            ]
    
    # Sélectionner le bon ensemble de tâches selon le secteur
    tasks_by_sector = sector_tasks.get(sector, sector_tasks["Technologie & IT"])
    
    # Combiner les tâches spécifiques au titre et au secteur
    if title_tasks:
        base_tasks = title_tasks
    else:
        base_tasks = tasks_by_sector["common"]
    
    if is_junior:
        # Les juniors ont principalement des tâches de base
        return random.sample(base_tasks, min(4, len(base_tasks)))
    elif is_senior:
        # Les seniors ont des tâches de base et des tâches avancées
        return random.sample(base_tasks, 2) + random.sample(tasks_by_sector["senior"], 3)
    elif is_manager:
        # Les managers ont principalement des tâches de management
        return random.sample(tasks_by_sector["manager"], 4) + random.sample(tasks_by_sector["senior"], 2)
    else:
        # Les profils intermédiaires ont un mix de tâches
        return random.sample(base_tasks, 3) + random.sample(tasks_by_sector["senior"], 2)

def generate_requirements(sector: str, is_junior: bool, is_senior: bool, is_manager: bool) -> List[str]:
    """Génère des prérequis cohérents avec le secteur et le niveau"""
    
    # Prérequis par secteur
    sector_reqs = {
        "Finance & Comptabilité": {
            "junior": [
                "Formation en comptabilité/gestion (DCG, BTS...)",
                "Première expérience en comptabilité souhaitée",
                "Maîtrise des outils bureautiques",
                "Connaissance des principes comptables",
                "Anglais niveau intermédiaire"
            ],
            "standard": [
                "Formation supérieure en comptabilité (DCG/DSCG)",
                "3 à 5 ans d'expérience en comptabilité",
                "Maîtrise des outils informatiques comptables",
                "Connaissance des normes comptables",
                "Anglais professionnel"
            ],
            "senior": [
                "Formation supérieure en comptabilité (DSCG, Master CCA)",
                "Minimum 5 ans d'expérience en comptabilité",
                "Expertise en fiscalité d'entreprise",
                "Maîtrise d'un ERP financier (SAP, Oracle...)",
                "Anglais courant indispensable"
            ],
            "manager": [
                "Formation supérieure en finance/comptabilité (Master, DSCG, diplôme d'expertise comptable)",
                "8 à 10 ans d'expérience minimum dont 3 ans à un poste similaire",
                "Expérience réussie en management d'équipe",
                "Excellente connaissance des normes comptables françaises et internationales",
                "Anglais courant exigé"
            ]
        },
        "Technologie & IT": {
            "junior": [
                "Formation en informatique (Bac+2/3 minimum)",
                "Connaissance des langages de programmation modernes",
                "Bases en algorithmique et structures de données",
                "Pratique des méthodologies Agile",
                "Capacité à travailler en équipe"
            ],
            "standard": [
                "Formation supérieure en informatique (Bac+3/5)",
                "2 à 4 ans d'expérience en développement",
                "Maîtrise des principaux frameworks",
                "Expérience en intégration continue",
                "Anglais technique"
            ],
            "senior": [
                "Formation supérieure en informatique (Bac+5)",
                "5+ ans d'expérience en développement",
                "Expertise technique dans plusieurs technologies",
                "Expérience en conception d'architecture",
                "Capacité à former et encadrer des juniors"
            ],
            "manager": [
                "Formation supérieure en informatique/management (Bac+5)",
                "7+ ans d'expérience dont 3 ans en gestion d'équipe",
                "Connaissance approfondie du cycle de développement logiciel",
                "Excellentes compétences en communication",
                "Certification en gestion de projet (PMP, Prince2, etc.)"
            ]
        }
    }
    
    # Sélectionner le bon ensemble de prérequis selon le secteur
    reqs_by_sector = sector_reqs.get(sector, sector_reqs["Technologie & IT"])
    
    if is_junior:
        return random.sample(reqs_by_sector["junior"], 4)
    elif is_senior:
        return random.sample(reqs_by_sector["senior"], 4)
    elif is_manager:
        return random.sample(reqs_by_sector["manager"], 4)
    else:
        return random.sample(reqs_by_sector["standard"], 4)
