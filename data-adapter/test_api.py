#!/usr/bin/env python3
"""
Script de test pour l'adaptateur SmartMatch
------------------------------------------
Ce script teste tous les endpoints de l'API de l'adaptateur SmartMatch.
"""

import requests
import json

# URL de base de l'API
BASE_URL = "http://localhost:5053/api/adapter"

# Données de test pour un CV
cv_data = {
    "nom": "Dupont",
    "prenom": "Jean",
    "poste": "Développeur Python Senior",
    "competences": ["Python", "Django", "Flask", "REST API"],
    "logiciels": ["Git", "Docker", "VS Code", "PyCharm"],
    "soft_skills": ["Communication", "Travail d'équipe", "Autonomie"],
    "email": "jean.dupont@example.com",
    "telephone": "06 12 34 56 78",
    "adresse": "Paris"
}

# Données de test pour une offre d'emploi
job_data = {
    "title": "Développeur Python Senior",
    "company": "Acme Inc.",
    "location": "Paris",
    "contract_type": "CDI",
    "skills": ["Python", "Django", "Flask", "SQL", "Git", "Docker"],
    "experience": "5 ans d'expérience en développement Python",
    "education": "Diplôme d'ingénieur ou équivalent",
    "salary": "45K - 55K",
    "responsibilities": [
        "Développer des applications web avec Django",
        "Maintenir les API REST existantes",
        "Participer à la conception technique"
    ],
    "benefits": [
        "Télétravail partiel",
        "Mutuelle d'entreprise",
        "Tickets restaurant"
    ]
}

def test_health():
    """Teste l'endpoint de santé"""
    response = requests.get(f"{BASE_URL}/health")
    print("\n=== Test de l'endpoint de santé ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_adapt_cv():
    """Teste l'endpoint d'adaptation de CV"""
    response = requests.post(f"{BASE_URL}/adapt-cv", json=cv_data)
    print("\n=== Test de l'adaptation de CV ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_adapt_job():
    """Teste l'endpoint d'adaptation d'offre d'emploi"""
    response = requests.post(f"{BASE_URL}/adapt-job", json=job_data)
    print("\n=== Test de l'adaptation d'offre d'emploi ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_match():
    """Teste l'endpoint de matching"""
    match_data = {
        "cv": cv_data,
        "job": job_data
    }
    response = requests.post(f"{BASE_URL}/match", json=match_data)
    print("\n=== Test du matching ===")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == "__main__":
    # Exécuter tous les tests
    health_ok = test_health()
    cv_ok = test_adapt_cv()
    job_ok = test_adapt_job()
    match_ok = test_match()
    
    # Résumé
    print("\n=== Résumé des tests ===")
    print(f"Endpoint de santé : {'✅ OK' if health_ok else '❌ ÉCHEC'}")
    print(f"Adaptation de CV : {'✅ OK' if cv_ok else '❌ ÉCHEC'}")
    print(f"Adaptation d'offre d'emploi : {'✅ OK' if job_ok else '❌ ÉCHEC'}")
    print(f"Matching : {'✅ OK' if match_ok else '❌ ÉCHEC'}")
    
    if health_ok and cv_ok and job_ok and match_ok:
        print("\n✅ Tous les tests ont réussi ! L'adaptateur SmartMatch fonctionne correctement.")
    else:
        print("\n❌ Certains tests ont échoué. Voir les détails ci-dessus.")