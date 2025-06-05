#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Script SuperSmartMatch V2
==============================
Script de test rapide pour l'API de matching
avec les bons formats de données.

Usage:
    python3 test_matching_api.py
    python3 test_matching_api.py --custom
"""

import requests
import json
import sys
import argparse
from datetime import datetime

# Configuration de l'API
API_BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{API_BASE_URL}/api/matching/complete"

def test_api_health():
    """Vérifie que l'API est en ligne"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API SuperSmartMatch V2 en ligne")
            return True
        else:
            print(f"❌ API problème - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API non disponible: {e}")
        print("💡 Démarrez l'API avec: python3 data-adapter/api_matching.py")
        return False

def test_matching_basic():
    """Test basique avec données pré-définies"""
    print("\n🎯 Test Matching Basique")
    print("=" * 40)
    
    # Données de test avec les bons types (strings pour id et salaire)
    test_data = {
        "cv_data": {
            "nom": "Baptiste",
            "prenom": "Coma", 
            "email": "baptiste.coma@gmail.com",
            "competences": ["Python", "AI", "FastAPI", "React", "Docker"],
            "annees_experience": 5,
            "formation": "Master Informatique",
            "experience": "5 ans d'expérience en développement"
        },
        "questionnaire_data": {
            "adresse": "Paris",
            "temps_trajet_max": 45,
            "fourchette_salaire": "55000€",
            "types_contrat": ["CDI"],
            "disponibilite": "Immédiatement",
            "teletravail": True
        },
        "jobs_data": [
            {
                "id": "1",  # STRING comme attendu
                "titre": "Senior AI Developer",
                "entreprise": "TechCorp AI",
                "competences": ["Python", "AI", "Machine Learning", "FastAPI"],
                "salaire": "65000",  # STRING comme attendu
                "localisation": "Paris",
                "type_contrat": "CDI",
                "description": "Développement d'applications AI avancées"
            }
        ],
        "options": {
            "limit": 10,
            "min_score": 0,
            "include_details": True
        }
    }
    
    return send_matching_request(test_data)

def test_matching_multiple_jobs():
    """Test avec plusieurs offres d'emploi"""
    print("\n🎯 Test Matching Multiple Jobs")
    print("=" * 40)
    
    test_data = {
        "cv_data": {
            "nom": "Jean",
            "prenom": "Dupont",
            "competences": ["JavaScript", "React", "Node.js"],
            "annees_experience": 3,
            "formation": "Bachelor Informatique"
        },
        "questionnaire_data": {
            "adresse": "Lyon",
            "salaire_min": 45000,
            "contrats_recherches": ["CDI", "CDD"]
        },
        "jobs_data": [
            {
                "id": "1",
                "titre": "Frontend Developer",
                "entreprise": "Startup Lyon",
                "competences": ["React", "JavaScript", "CSS"],
                "salaire": "48000",
                "localisation": "Lyon",
                "type_contrat": "CDI"
            },
            {
                "id": "2", 
                "titre": "Full-Stack Developer",
                "entreprise": "Big Corp",
                "competences": ["Node.js", "React", "MongoDB"],
                "salaire": "55000",
                "localisation": "Paris",
                "type_contrat": "CDI"
            },
            {
                "id": "3",
                "titre": "Senior Backend Developer",
                "entreprise": "TechStart",
                "competences": ["Python", "Django", "PostgreSQL"],
                "salaire": "60000",
                "localisation": "Lyon", 
                "type_contrat": "CDI"
            }
        ]
    }
    
    return send_matching_request(test_data)

def test_matching_bad_match():
    """Test avec un mauvais match pour voir la différence"""
    print("\n🎯 Test Matching Mauvais Match")
    print("=" * 40)
    
    test_data = {
        "cv_data": {
            "competences": ["Python", "AI", "Machine Learning"],
            "annees_experience": 8,
            "formation": "PhD Computer Science"
        },
        "questionnaire_data": {
            "salaire_min": 80000,
            "adresse": "Paris",
            "contrats_recherches": ["CDI"]
        },
        "jobs_data": [
            {
                "id": "1",
                "titre": "Junior PHP Developer",
                "entreprise": "Old Corp",
                "competences": ["PHP", "MySQL", "jQuery"],
                "salaire": "30000",
                "localisation": "Bordeaux",
                "type_contrat": "Stage"
            }
        ]
    }
    
    return send_matching_request(test_data)

def send_matching_request(data):
    """Envoie une requête de matching et affiche les résultats"""
    try:
        print(f"📤 Envoi requête vers: {API_ENDPOINT}")
        print(f"📊 Candidat: {data['cv_data'].get('nom', 'N/A')} {data['cv_data'].get('prenom', '')}")
        print(f"🎯 Compétences: {', '.join(data['cv_data']['competences'])}")
        print(f"🏢 {len(data['jobs_data'])} offre(s) à analyser")
        
        response = requests.post(
            API_ENDPOINT,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📨 Réponse API - Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            display_results(result)
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            try:
                error_detail = response.json()
                print(f"🔍 Détail: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"🔍 Réponse brute: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def display_results(result):
    """Affiche les résultats de matching de manière lisible"""
    print("\n📊 RÉSULTATS SUPERSMARTMATCH V2")
    print("=" * 50)
    
    if result.get('success'):
        data = result.get('data', [])
        stats = result.get('stats', {})
        
        print(f"✅ Succès - {len(data)} résultat(s) trouvé(s)")
        print(f"⏱️  Temps de traitement: {stats.get('processing_time', 'N/A')}s")
        
        for i, match in enumerate(data):
            print(f"\n🎯 Match #{i+1}:")
            print(f"   📋 Poste: {match.get('job_title', 'N/A')}")
            print(f"   🏢 Entreprise: {match.get('company', 'N/A')}")
            print(f"   🏆 Score: {match.get('matching_score', 'N/A')}%")
            
            # Détails du matching s'ils existent
            if match.get('competences_match'):
                print(f"   🎯 Compétences: {match['competences_match']}")
            if match.get('experience_score'):
                print(f"   📈 Expérience: {match['experience_score']}")
            if match.get('salary_match'):
                print(f"   💰 Salaire: {match['salary_match']}")
            if match.get('location_score'):
                print(f"   📍 Localisation: {match['location_score']}")
            
            # Recommandation
            score = match.get('matching_score', 0)
            if score >= 80:
                print(f"   🎉 Recommandation: EXCELLENT MATCH!")
            elif score >= 60:
                print(f"   👍 Recommandation: BON MATCH")
            elif score >= 40:
                print(f"   🤔 Recommandation: MATCH PARTIEL")
            else:
                print(f"   ❌ Recommandation: FAIBLE COMPATIBILITÉ")
        
        # Statistiques globales
        if stats:
            print(f"\n📈 Statistiques:")
            for key, value in stats.items():
                if key not in ['processing_time']:
                    print(f"   • {key}: {value}")
    
    else:
        print(f"❌ Échec: {result.get('message', 'Erreur inconnue')}")
        print(f"🔍 Code: {result.get('error_code', 'UNKNOWN')}")

def interactive_test():
    """Test interactif avec saisie utilisateur"""
    print("\n🎯 Test Interactif SuperSmartMatch V2")
    print("=" * 40)
    
    # Saisie candidat
    print("\n👤 Informations Candidat:")
    nom = input("Nom: ") or "Test"
    competences = input("Compétences (séparées par des virgules): ") or "Python,React"
    experience = input("Années d'expérience: ") or "3"
    formation = input("Formation: ") or "Bachelor"
    
    # Saisie job
    print("\n🏢 Offre d'Emploi:")
    job_titre = input("Titre du poste: ") or "Developer"
    job_competences = input("Compétences requises: ") or "Python,JavaScript"
    job_salaire = input("Salaire (€): ") or "50000"
    job_lieu = input("Localisation: ") or "Paris"
    
    # Construction des données
    test_data = {
        "cv_data": {
            "nom": nom,
            "competences": [c.strip() for c in competences.split(',')],
            "annees_experience": int(experience) if experience.isdigit() else 3,
            "formation": formation
        },
        "questionnaire_data": {
            "adresse": job_lieu,
            "salaire_min": int(job_salaire) if job_salaire.isdigit() else 50000
        },
        "jobs_data": [{
            "id": "1",
            "titre": job_titre,
            "competences": [c.strip() for c in job_competences.split(',')],
            "salaire": str(job_salaire),
            "localisation": job_lieu,
            "type_contrat": "CDI"
        }]
    }
    
    return send_matching_request(test_data)

def main():
    parser = argparse.ArgumentParser(description='Test SuperSmartMatch V2 API')
    parser.add_argument('--custom', action='store_true', help='Test interactif personnalisé')
    parser.add_argument('--url', default=API_BASE_URL, help='URL de base de l\'API')
    args = parser.parse_args()
    
    global API_BASE_URL, API_ENDPOINT
    API_BASE_URL = args.url
    API_ENDPOINT = f"{API_BASE_URL}/api/matching/complete"
    
    print("🚀 SuperSmartMatch V2 - Test Suite")
    print("=" * 50)
    print(f"🌐 API URL: {API_BASE_URL}")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Vérification santé API
    if not test_api_health():
        sys.exit(1)
    
    success_count = 0
    total_tests = 0
    
    if args.custom:
        # Test interactif
        total_tests = 1
        if interactive_test():
            success_count += 1
    else:
        # Suite de tests automatiques
        tests = [
            test_matching_basic,
            test_matching_multiple_jobs,
            test_matching_bad_match
        ]
        
        total_tests = len(tests)
        for test_func in tests:
            if test_func():
                success_count += 1
    
    # Résumé final
    print(f"\n📊 RÉSUMÉ FINAL")
    print("=" * 30)
    print(f"✅ Tests réussis: {success_count}/{total_tests}")
    print(f"📊 Taux de succès: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 Tous les tests sont passés ! SuperSmartMatch V2 fonctionne parfaitement !")
        sys.exit(0)
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
