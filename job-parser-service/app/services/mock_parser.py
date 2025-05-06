"""
Module de mock parser pour le service de parsing de fiches de poste.
Utilisé pour les tests et le développement sans dépendance à OpenAI.
"""

import logging
import random
import hashlib
import os
from typing import Dict, Any, List

# Setup logging
logger = logging.getLogger(__name__)

# Données fictives pour les mocks
MOCK_TITLES = [
    "Comptable général", "Auditeur financier", "Contrôleur de gestion",
    "Directeur financier", "Comptable fournisseurs", "Comptable clients",
    "Responsable comptabilité", "Fiscaliste", "Comptable unique",
    "Analyste financier", "Trésorier"
]

MOCK_COMPANIES = [
    "FinTech Solutions", "Mondial Audit", "Comptex", "Groupe Finance Plus",
    "EuroFisc", "Gestion & Stratégie", "Audit Expert", "CompTrust",
    "Finance Consulting", "Expertise Comptable Pro"
]

MOCK_LOCATIONS = [
    "Paris", "Lyon", "Bordeaux", "Marseille", "Lille", "Toulouse",
    "Nantes", "Strasbourg", "Montpellier", "Nice"
]

MOCK_CONTRACT_TYPES = [
    "CDI", "CDD", "Freelance", "Stage", "Alternance",
    "Temps partiel", "Temps plein"
]

MOCK_SKILLS = [
    "Comptabilité générale", "Comptabilité analytique", "Normes IFRS",
    "Audit financier", "Fiscalité", "Reporting", "Consolidation",
    "ERP financiers", "Contrôle de gestion", "Gestion de trésorerie",
    "Analyse financière", "Excel avancé", "Clôture comptable",
    "Bilan", "Liasse fiscale", "Budgétisation", "Analyse des coûts",
    "Déclarations fiscales", "Rapprochement bancaire"
]

MOCK_REQUIREMENTS = [
    "DCG / DSCG", "Master CCA", "Diplôme de comptabilité", "Expertise comptable",
    "3-5 ans d'expérience", "Anglais professionnel", "Expérience en cabinet",
    "Connaissance de SAP", "Maîtrise d'Excel", "Rigueur et organisation"
]

MOCK_BENEFITS = [
    "Tickets restaurant", "Mutuelle d'entreprise", "RTT",
    "Possibilité de télétravail", "Participation", "Intéressement",
    "Prime annuelle", "Formation continue", "Plan d'épargne entreprise",
    "Horaires flexibles", "13ème mois", "Bonus annuel"
]

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
    
    # Simuler différents types d'offres
    is_junior = random.random() < 0.3
    is_senior = random.random() < 0.3
    is_manager = random.random() < 0.2
    
    # Générer un titre cohérent avec le niveau
    base_title = random.choice(MOCK_TITLES)
    if is_junior:
        title = f"Assistant {base_title}" if random.random() < 0.5 else f"{base_title} Junior"
    elif is_senior:
        title = f"{base_title} Senior" if random.random() < 0.5 else f"{base_title} Confirmé"
    elif is_manager:
        title = f"Responsable {base_title}" if random.random() < 0.5 else f"Manager {base_title}"
    else:
        title = base_title
        
    # Générer des compétences requises et souhaitées
    num_required = random.randint(3, 6)
    num_preferred = random.randint(2, 5)
    
    all_skills = list(MOCK_SKILLS)
    random.shuffle(all_skills)
    
    required_skills = all_skills[:num_required]
    preferred_skills = [skill for skill in all_skills[num_required:num_required+num_preferred] 
                       if skill not in required_skills]
    
    # Générer des responsabilités basées sur le titre et le niveau
    responsibilities = generate_responsibilities(title, is_junior, is_senior, is_manager)
    
    # Générer des prérequis cohérents avec le niveau
    requirements = generate_requirements(is_junior, is_senior, is_manager)
    
    # Générer des avantages
    num_benefits = random.randint(3, 7)
    benefits = random.sample(MOCK_BENEFITS, num_benefits)
    
    # Politique de télétravail et salaire
    remote_options = ["Pas de télétravail", "1 jour par semaine", "2 jours par semaine", 
                     "3 jours par semaine", "Télétravail possible", "Full remote"]
    remote_policy = random.choice(remote_options)
    
    # Fourchette de salaire basée sur le niveau
    if is_junior:
        base_salary = random.randint(25, 35) * 1000
    elif is_senior:
        base_salary = random.randint(45, 60) * 1000
    elif is_manager:
        base_salary = random.randint(65, 95) * 1000
    else:
        base_salary = random.randint(35, 50) * 1000
        
    max_salary = base_salary + random.randint(5, 15) * 1000
    salary_range = f"{base_salary // 1000}K€ - {max_salary // 1000}K€"
    
    # Assembler le tout
    mock_data = {
        "title": title,
        "company": random.choice(MOCK_COMPANIES),
        "location": random.choice(MOCK_LOCATIONS),
        "contract_type": random.choice(MOCK_CONTRACT_TYPES),
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "responsibilities": responsibilities,
        "requirements": requirements,
        "benefits": benefits,
        "salary_range": salary_range,
        "remote_policy": remote_policy,
        "application_process": "Envoyer CV et lettre de motivation",
        "company_description": f"Entreprise spécialisée dans le secteur financier."
    }
    
    logger.info(f"Données mock générées pour {filename or 'une fiche de poste'}")
    return mock_data

def generate_responsibilities(title: str, is_junior: bool, is_senior: bool, is_manager: bool) -> List[str]:
    """Génère des responsabilités cohérentes avec le titre et le niveau"""
    common_tasks = [
        "Comptabilisation des factures",
        "Suivi des comptes fournisseurs/clients",
        "Préparation des déclarations fiscales",
        "Participation aux clôtures mensuelles et annuelles",
        "Rapprochements bancaires",
        "Suivi de la trésorerie"
    ]
    
    senior_tasks = [
        "Supervision de l'équipe comptable",
        "Mise en place de procédures comptables",
        "Optimisation des processus financiers",
        "Collaboration avec les commissaires aux comptes",
        "Gestion de la relation avec l'administration fiscale",
        "Élaboration du reporting mensuel"
    ]
    
    manager_tasks = [
        "Management d'une équipe de comptables",
        "Définition de la stratégie financière",
        "Pilotage des clôtures",
        "Relations avec les partenaires financiers",
        "Prise de décisions stratégiques",
        "Présentation des résultats financiers à la direction"
    ]
    
    audit_tasks = [
        "Réalisation de missions d'audit",
        "Analyse des risques financiers",
        "Contrôle interne",
        "Revue des procédures comptables",
        "Vérification de la conformité réglementaire"
    ]
    
    if "auditeur" in title.lower():
        base_tasks = audit_tasks
    else:
        base_tasks = common_tasks
    
    if is_junior:
        # Les juniors ont principalement des tâches de base
        return random.sample(base_tasks, min(4, len(base_tasks)))
    elif is_senior:
        # Les seniors ont des tâches de base et des tâches avancées
        return random.sample(base_tasks, 2) + random.sample(senior_tasks, 3)
    elif is_manager:
        # Les managers ont principalement des tâches de management
        return random.sample(manager_tasks, 4) + random.sample(senior_tasks, 2)
    else:
        # Les profils intermédiaires ont un mix de tâches
        return random.sample(base_tasks, 3) + random.sample(senior_tasks, 2)

def generate_requirements(is_junior: bool, is_senior: bool, is_manager: bool) -> List[str]:
    """Génère des prérequis cohérents avec le niveau"""
    junior_reqs = [
        "Formation en comptabilité/gestion (DCG, BTS...)",
        "Première expérience en comptabilité souhaitée",
        "Maîtrise des outils bureautiques",
        "Connaissance des principes comptables",
        "Anglais niveau intermédiaire"
    ]
    
    standard_reqs = [
        "Formation supérieure en comptabilité (DCG/DSCG)",
        "3 à 5 ans d'expérience en comptabilité",
        "Maîtrise des outils informatiques comptables",
        "Connaissance des normes comptables",
        "Anglais professionnel"
    ]
    
    senior_reqs = [
        "Formation supérieure en comptabilité (DSCG, Master CCA)",
        "Minimum 5 ans d'expérience en comptabilité",
        "Expertise en fiscalité d'entreprise",
        "Maîtrise d'un ERP financier (SAP, Oracle...)",
        "Anglais courant indispensable"
    ]
    
    manager_reqs = [
        "Formation supérieure en finance/comptabilité (Master, DSCG, diplôme d'expertise comptable)",
        "8 à 10 ans d'expérience minimum dont 3 ans à un poste similaire",
        "Expérience réussie en management d'équipe",
        "Excellente connaissance des normes comptables françaises et internationales",
        "Anglais courant exigé"
    ]
    
    if is_junior:
        return random.sample(junior_reqs, 4)
    elif is_senior:
        return random.sample(senior_reqs, 4)
    elif is_manager:
        return random.sample(manager_reqs, 4)
    else:
        return random.sample(standard_reqs, 4)
