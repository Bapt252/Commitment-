#!/usr/bin/env python3
"""
Script FINAL corrigé pour SuperSmartMatch V2 avec la structure EXACTE attendue
Résout TOUS les problèmes 422 identifiés
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration des endpoints
SUPERSMARTMATCH_V2_URL = "http://localhost:5070"
NEXTEN_URL = "http://localhost:5052"

def test_final_correct_structure():
    """Teste avec la structure FINALE corrigée"""
    
    print("🎯 TEST FINAL - Structure EXACTE SuperSmartMatch V2")
    print("=" * 80)
    
    # STRUCTURE FINALE CORRIGÉE
    final_payload = {
        "candidate": {
            "name": "Marie Martin",  # 🔥 CHANGEMENT: name directement dans candidate
            "email": "marie.martin@email.com",
            "phone": "+33123456789",
            "location": {
                "city": "Lyon",
                "country": "France"
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
                "id": str(uuid.uuid4()),
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
                "id": str(uuid.uuid4()),
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
    
    print(f"📊 Structure FINALE corrigée:")
    print(f"   ✅ 'candidate' avec 'name' direct")
    print(f"   ✅ Chaque offer a un 'id' unique")
    print(f"   ✅ Location en format objet")
    print(f"   📋 Candidate: {final_payload['candidate']['name']}")
    print(f"   📋 Email: {final_payload['candidate']['email']}")
    print(f"   📋 Nombre d'offres: {len(final_payload['offers'])}")
    
    try:
        print(f"\n📤 Envoi requête FINALE à SuperSmartMatch V2...")
        response = requests.post(
            f"{SUPERSMARTMATCH_V2_URL}/match",
            json=final_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🎉 SUCCÈS TOTAL ! SuperSmartMatch V2 fonctionne parfaitement !")
            print(f"\n📈 Résultats:")
            print(f"Algorithm used: {result.get('algorithm_used', 'N/A')}")
            print(f"Processing time: {result.get('processing_time', 'N/A')} seconds")
            
            if 'matches' in result:
                print(f"\n🎯 Matches trouvés:")
                for i, match in enumerate(result['matches'], 1):
                    print(f"  {i}. {match.get('offer_title', match.get('title', 'N/A'))}")
                    print(f"     Score: {match.get('score', 'N/A')}")
                    print(f"     Company: {match.get('company', 'N/A')}")
                    if 'reasons' in match:
                        print(f"     Reasons: {', '.join(match.get('reasons', []))}")
                    print()
            
            # Vérifier si Nexten est utilisé
            algorithm_used = result.get('algorithm_used', '')
            if 'nexten' in algorithm_used.lower():
                print(f"🔥 PARFAIT ! SuperSmartMatch V2 utilise bien Nexten : {algorithm_used}")
            else:
                print(f"⚠️  Algorithm utilisé: {algorithm_used}")
                
            return True, result
            
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"❌ Erreur 422 - Champs encore manquants:")
            for error in error_detail.get('detail', []):
                if error.get('type') == 'missing':
                    field_path = '.'.join(map(str, error.get('loc', [])))
                    print(f"   - Manque: {field_path}")
            print(f"\nDétail complet: {json.dumps(error_detail, indent=2)}")
            return False, None
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Response: {response.text[:1000]}")
            return False, None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False, None

def test_minimal_working():
    """Teste avec un payload minimal pour valider la structure exacte"""
    
    print("\n🧪 TEST MINIMAL FINAL - Structure minimale")
    print("=" * 80)
    
    minimal_payload = {
        "candidate": {
            "name": "Test User",  # Direct dans candidate
            "email": "test@example.com",
            "skills": ["Python"]
        },
        "offers": [
            {
                "id": str(uuid.uuid4()),
                "title": "Test Job",
                "company": "Test Company",
                "description": "Test description",
                "location": {
                    "city": "Paris",
                    "country": "France"
                }
            }
        ]
    }
    
    try:
        print(f"📤 Test structure minimale...")
        response = requests.post(
            f"{SUPERSMARTMATCH_V2_URL}/match",
            json=minimal_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Structure minimale OK !")
            print(f"Algorithm used: {result.get('algorithm_used', 'N/A')}")
            return True
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"❌ Erreur 422 - Champs encore manquants:")
            for error in error_detail.get('detail', []):
                if error.get('type') == 'missing':
                    field_path = '.'.join(map(str, error.get('loc', [])))
                    print(f"   - Manque: {field_path}")
            return False
        else:
            print(f"❌ Erreur {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verify_nexten_direct():
    """Test direct de Nexten pour comparison"""
    
    print("\n🔍 TEST DIRECT NEXTEN - Référence")
    print("=" * 80)
    
    payload = {
        "cv_text": "Marie Martin, développeur Python senior avec 5 ans d'expérience en FastAPI, Docker et Machine Learning.",
        "job_description": "Développeur Python senior pour équipe. Compétences: Python, FastAPI, Docker, PostgreSQL."
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
            print(f"✅ Nexten direct - Score: {result.get('score', 'N/A')}")
            print(f"✅ Algorithm: {result.get('algorithm', 'N/A')}")
            print(f"✅ Temps: {result.get('processing_time', 'N/A')} ms")
            return True, result
        else:
            print(f"❌ Nexten Error: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Nexten Error: {e}")
        return False, None

def generate_final_template():
    """Génère le template FINAL avec la structure correcte"""
    
    template = {
        "candidate": {
            "name": "Prénom Nom",
            "email": "email@example.com", 
            "phone": "+33123456789",
            "location": {
                "city": "Ville",
                "country": "France"
            },
            "skills": ["Compétence1", "Compétence2"],
            "experience": [
                {
                    "title": "Poste",
                    "company": "Entreprise",
                    "duration": "2020-2023",
                    "description": "Description"
                }
            ],
            "education": [
                {
                    "degree": "Diplôme",
                    "school": "École",
                    "year": "2020"
                }
            ]
        },
        "offers": [
            {
                "id": "REMPLACER_PAR_UUID",
                "title": "Titre du poste",
                "company": "Entreprise",
                "description": "Description du poste",
                "requirements": ["Compétence1", "Compétence2"],
                "salary_range": "40000-60000",
                "contract_type": "CDI",
                "location": {
                    "city": "Ville",
                    "region": "Région",
                    "country": "France"
                }
            }
        ]
    }
    
    template_file = "supersmartmatch_v2_FINAL_template.json"
    with open(template_file, "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Template FINAL sauvegardé: {template_file}")
    return template_file

def main():
    """Fonction principale"""
    print("🚀 SUPERSMARTMATCH V2 - TEST FINAL STRUCTURE CORRIGÉE")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Test Nexten direct (référence)
    nexten_ok, nexten_result = verify_nexten_direct()
    
    # 2. Test minimal SuperSmartMatch V2
    minimal_ok = test_minimal_working()
    
    # 3. Test complet FINAL
    success, v2_result = test_final_correct_structure()
    
    # 4. Générer template final
    template_file = generate_final_template()
    
    # 5. Résumé et comparaison
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ FINAL - SUPERSMARTMATCH V2")
    print("=" * 80)
    
    if success and v2_result:
        print("🎉 VICTOIRE TOTALE ! PROBLÈME 422 RÉSOLU !")
        print("\n✅ Structure payload FINALE identifiée:")
        print("   - 'candidate' avec 'name' direct (pas dans personal_info)")
        print("   - 'id' unique pour chaque offer")  
        print("   - 'location' en format objet")
        print("\n🔥 SuperSmartMatch V2 vs Nexten Direct:")
        if nexten_ok and nexten_result:
            print(f"   📊 Nexten direct  : Score {nexten_result.get('score', 'N/A')}")
        print(f"   📊 SuperSmartMatch: Algorithm {v2_result.get('algorithm_used', 'N/A')}")
        
        if 'nexten' in v2_result.get('algorithm_used', '').lower():
            print("   🎯 PARFAIT ! SuperSmartMatch V2 utilise bien Nexten !")
        
        print(f"\n📝 Template final: {template_file}")
        print("\n💡 Prochaines étapes:")
        print("   1. Mettre à jour TOUS tes scripts avec cette structure")
        print("   2. Utiliser le template final pour nouveaux tests")
        print("   3. Tester avec vraies données CV/questionnaires")
        print("   4. Valider performance end-to-end")
    else:
        print("❌ Problème en cours de résolution")
        print("💡 Progress:")
        print(f"   ✅ Nexten fonctionne: {nexten_ok}")
        print(f"   ✅ Structure minimale: {minimal_ok}")
        print(f"   ❌ Structure complète: en cours")
        
        if not success:
            print("\n🔍 Actions suivantes:")
            print("   1. Analyser les derniers champs manquants")
            print("   2. Ajuster structure selon erreurs")
            print("   3. Re-tester étape par étape")

if __name__ == "__main__":
    main()
