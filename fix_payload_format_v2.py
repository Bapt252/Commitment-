#!/usr/bin/env python3
"""
Script pour diagnostiquer et corriger le format des payloads SuperSmartMatch V2
Résout l'erreur 422 - format de location incorrect
"""

import requests
import json
from datetime import datetime

# Configuration des endpoints
SUPERSMARTMATCH_V2_URL = "http://localhost:5070"
NEXTEN_URL = "http://localhost:5052"

def test_location_formats():
    """Teste différents formats pour le champ location"""
    
    print("🔍 DIAGNOSTIC - Test des formats de location pour SuperSmartMatch V2")
    print("=" * 80)
    
    # Format de base du CV (structure attendue)
    base_cv = {
        "personal_info": {
            "name": "Jean Dupont",
            "email": "jean.dupont@email.com",
            "phone": "+33123456789"
        },
        "skills": ["Python", "FastAPI", "Docker", "Machine Learning"],
        "experience": [
            {
                "title": "Développeur Senior",
                "company": "TechCorp",
                "duration": "2020-2023",
                "description": "Développement d'applications Python et ML"
            }
        ],
        "education": [
            {
                "degree": "Master Informatique",
                "school": "École Supérieure",
                "year": "2020"
            }
        ]
    }
    
    # Différents formats à tester pour les offers
    location_formats = [
        {
            "name": "String simple",
            "location": "Paris"
        },
        {
            "name": "Objet basique",
            "location": {
                "city": "Paris",
                "country": "France"
            }
        },
        {
            "name": "Objet détaillé",
            "location": {
                "city": "Paris",
                "region": "Île-de-France", 
                "country": "France",
                "postal_code": "75000"
            }
        },
        {
            "name": "Objet avec coordonnées",
            "location": {
                "city": "Paris",
                "country": "France",
                "latitude": 48.8566,
                "longitude": 2.3522
            }
        }
    ]
    
    for i, loc_format in enumerate(location_formats, 1):
        print(f"\n🧪 Test {i}: Format {loc_format['name']}")
        print(f"Location format: {json.dumps(loc_format['location'], indent=2)}")
        
        # Créer l'offer avec ce format de location
        offer = {
            "title": "Développeur Python Senior",
            "company": "Innovation Tech",
            "description": "Nous recherchons un développeur Python expérimenté...",
            "requirements": ["Python", "FastAPI", "Docker"],
            "salary_range": "45000-65000",
            "contract_type": "CDI",
            "location": loc_format['location']  # Format variable
        }
        
        # Payload complet pour SuperSmartMatch V2
        payload = {
            "cv": base_cv,
            "offers": [offer]
        }
        
        try:
            print(f"📤 Envoi requête à SuperSmartMatch V2...")
            response = requests.post(
                f"{SUPERSMARTMATCH_V2_URL}/match",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"📥 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCÈS ! Format accepté")
                print(f"Algorithm used: {result.get('algorithm_used', 'N/A')}")
                if 'matches' in result:
                    for match in result['matches']:
                        print(f"Score: {match.get('score', 'N/A')}")
                break
            elif response.status_code == 422:
                error_detail = response.json()
                print(f"❌ Erreur 422 - Validation failed")
                print(f"Détail: {json.dumps(error_detail, indent=2)}")
            else:
                print(f"❌ Erreur {response.status_code}")
                print(f"Response: {response.text[:500]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de connexion: {e}")
    
    print("\n" + "=" * 80)

def test_corrected_payload():
    """Teste avec le format de payload corrigé"""
    
    print("\n🎯 TEST FINAL - Payload avec format corrigé")
    print("=" * 80)
    
    # Payload avec format location corrigé (basé sur les tests précédents)
    corrected_payload = {
        "cv": {
            "personal_info": {
                "name": "Marie Martin",
                "email": "marie.martin@email.com",
                "phone": "+33123456789",
                "location": {
                    "city": "Lyon",
                    "country": "France"
                }
            },
            "skills": ["Python", "FastAPI", "Docker", "PostgreSQL", "Machine Learning"],
            "experience": [
                {
                    "title": "Développeur Full Stack",
                    "company": "WebCorp",
                    "duration": "2021-2024",
                    "description": "Développement d'applications web avec Python/FastAPI et React"
                },
                {
                    "title": "Développeur Junior",
                    "company": "StartupTech",
                    "duration": "2019-2021", 
                    "description": "Première expérience en développement Python"
                }
            ],
            "education": [
                {
                    "degree": "Master Informatique",
                    "school": "Université de Lyon",
                    "year": "2019"
                }
            ]
        },
        "offers": [
            {
                "title": "Développeur Python Senior",
                "company": "Innovation Tech",
                "description": "Nous recherchons un développeur Python expérimenté pour rejoindre notre équipe de développement d'applications web et d'intelligence artificielle.",
                "requirements": ["Python", "FastAPI", "Docker", "PostgreSQL"],
                "salary_range": "50000-70000",
                "contract_type": "CDI",
                "location": {
                    "city": "Paris",
                    "region": "Île-de-France",
                    "country": "France"
                }
            },
            {
                "title": "Lead Developer Python",
                "company": "DataCorp",
                "description": "Poste de lead developer pour diriger une équipe de développement Python spécialisée en machine learning.",
                "requirements": ["Python", "Machine Learning", "Docker", "Leadership"],
                "salary_range": "60000-80000",
                "contract_type": "CDI",
                "location": {
                    "city": "Lyon",
                    "country": "France"
                }
            }
        ]
    }
    
    try:
        print(f"📤 Test avec payload corrigé...")
        print(f"📊 CV: {corrected_payload['cv']['personal_info']['name']}")
        print(f"📊 Nombre d'offres: {len(corrected_payload['offers'])}")
        
        response = requests.post(
            f"{SUPERSMARTMATCH_V2_URL}/match",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎉 SUCCÈS TOTAL ! SuperSmartMatch V2 fonctionne parfaitement")
            print(f"\n📈 Résultats:")
            print(f"Algorithm used: {result.get('algorithm_used', 'N/A')}")
            print(f"Processing time: {result.get('processing_time', 'N/A')} seconds")
            
            if 'matches' in result:
                print(f"\n🎯 Matches trouvés:")
                for i, match in enumerate(result['matches'], 1):
                    print(f"  {i}. {match.get('offer_title', 'N/A')}")
                    print(f"     Score: {match.get('score', 'N/A')}")
                    print(f"     Company: {match.get('company', 'N/A')}")
                    print(f"     Reasons: {', '.join(match.get('reasons', []))}")
                    print()
            
            return True
            
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"❌ Erreur 422 persistante")
            print(f"Détail: {json.dumps(error_detail, indent=2)}")
            return False
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def verify_nexten_still_works():
    """Vérifie que Nexten fonctionne toujours correctement"""
    
    print("\n🔍 VÉRIFICATION - Nexten Matcher toujours opérationnel")
    print("=" * 80)
    
    payload = {
        "cv_text": "Jean Dupont, développeur Python senior avec 5 ans d'expérience en FastAPI, Docker et Machine Learning. Compétences: Python, FastAPI, Docker, PostgreSQL, ML.",
        "job_description": "Nous recherchons un développeur Python senior pour notre équipe. Compétences requises: Python, FastAPI, Docker."
    }
    
    try:
        response = requests.post(
            f"{NEXTEN_URL}/match",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Nexten OK - Score: {result.get('score', 'N/A')}")
            print(f"✅ Algorithm: {result.get('algorithm', 'N/A')}")
            return True
        else:
            print(f"❌ Nexten Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Nexten Connection Error: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 SUPERSMARTMATCH V2 - CORRECTION FORMAT PAYLOAD")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Vérifier que Nexten fonctionne
    nexten_ok = verify_nexten_still_works()
    
    if not nexten_ok:
        print("⚠️  Nexten ne répond pas. Vérifiez d'abord les services.")
        return
    
    # 2. Tester les formats de location
    test_location_formats()
    
    # 3. Test final avec payload corrigé
    success = test_corrected_payload()
    
    # 4. Résumé
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ")
    print("=" * 80)
    
    if success:
        print("🎉 PROBLÈME RÉSOLU !")
        print("✅ SuperSmartMatch V2 accepte maintenant les payloads")
        print("✅ Format de location corrigé")
        print("✅ Integration avec Nexten fonctionnelle")
        print("\n💡 Prochaines étapes:")
        print("   1. Mettre à jour tous les scripts de test avec le bon format")
        print("   2. Tester avec des données réelles de CV")
        print("   3. Valider la performance de l'ensemble")
    else:
        print("❌ Problème persistant")
        print("💡 Actions recommandées:")
        print("   1. Vérifier les logs de SuperSmartMatch V2")
        print("   2. Examiner la structure exacte des modèles Pydantic")
        print("   3. Adapter le format selon les erreurs détectées")

if __name__ == "__main__":
    main()
