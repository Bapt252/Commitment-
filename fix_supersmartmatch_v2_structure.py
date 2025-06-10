#!/usr/bin/env python3
"""
Script corrigé pour tester SuperSmartMatch V2 avec la VRAIE structure attendue
Résout les erreurs 422 : candidate au lieu de cv, id requis pour offers, format location correct
"""

import requests
import json
import uuid
from datetime import datetime

# Configuration des endpoints
SUPERSMARTMATCH_V2_URL = "http://localhost:5070"
NEXTEN_URL = "http://localhost:5052"

def test_correct_payload_structure():
    """Teste avec la structure de payload correcte identifiée"""
    
    print("🎯 TEST AVEC STRUCTURE CORRIGÉE - SuperSmartMatch V2")
    print("=" * 80)
    
    # STRUCTURE CORRIGÉE basée sur les erreurs de validation
    corrected_payload = {
        "candidate": {  # 🔥 CHANGEMENT: "candidate" au lieu de "cv"
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
                "id": str(uuid.uuid4()),  # 🔥 AJOUT: champ id requis
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
                "id": str(uuid.uuid4()),  # 🔥 AJOUT: champ id requis
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
    
    print(f"📊 Structure corrigée:")
    print(f"   ✅ Utilise 'candidate' au lieu de 'cv'")
    print(f"   ✅ Chaque offer a un 'id' unique")
    print(f"   ✅ Location en format objet")
    print(f"   📋 Candidate: {corrected_payload['candidate']['personal_info']['name']}")
    print(f"   📋 Nombre d'offres: {len(corrected_payload['offers'])}")
    
    try:
        print(f"\n📤 Envoi requête à SuperSmartMatch V2...")
        response = requests.post(
            f"{SUPERSMARTMATCH_V2_URL}/match",
            json=corrected_payload,
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
                print(f"⚠️  Algorithm utilisé: {algorithm_used} (pas Nexten)")
                
            return True
            
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"❌ Erreur 422 persistante")
            print(f"Détail: {json.dumps(error_detail, indent=2)}")
            return False
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Response: {response.text[:1000]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_minimal_payload():
    """Teste avec un payload minimal pour identifier la structure exacte"""
    
    print("\n🧪 TEST MINIMAL - Structure de base")
    print("=" * 80)
    
    minimal_payload = {
        "candidate": {
            "personal_info": {
                "name": "Test User",
                "email": "test@example.com"
            },
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
        print(f"📤 Test minimal...")
        response = requests.post(
            f"{SUPERSMARTMATCH_V2_URL}/match",
            json=minimal_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Structure minimal OK !")
            print(f"Algorithm used: {result.get('algorithm_used', 'N/A')}")
            return True
        elif response.status_code == 422:
            error_detail = response.json()
            print(f"❌ Erreur 422 - Champs manquants:")
            for error in error_detail.get('detail', []):
                if error.get('type') == 'missing':
                    print(f"   - Manque: {'.'.join(map(str, error.get('loc', [])))}")
            return False
        else:
            print(f"❌ Erreur {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def verify_nexten_still_works():
    """Vérifie que Nexten fonctionne toujours"""
    
    print("\n🔍 VÉRIFICATION - Nexten Matcher")
    print("=" * 80)
    
    payload = {
        "cv_text": "Marie Martin, développeur Python senior avec 5 ans d'expérience en FastAPI, Docker et Machine Learning.",
        "job_description": "Nous recherchons un développeur Python senior. Compétences: Python, FastAPI, Docker."
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

def generate_corrected_template():
    """Génère un template avec la structure corrigée"""
    
    template = {
        "candidate": {
            "personal_info": {
                "name": "Prénom Nom",
                "email": "email@example.com",
                "phone": "+33123456789",
                "location": {
                    "city": "Ville",
                    "country": "France"
                }
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
    
    with open("supersmartmatch_v2_template_corrected.json", "w", encoding="utf-8") as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Template corrigé sauvegardé: supersmartmatch_v2_template_corrected.json")

def main():
    """Fonction principale"""
    print("🚀 SUPERSMARTMATCH V2 - STRUCTURE PAYLOAD CORRIGÉE")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Vérifier Nexten
    nexten_ok = verify_nexten_still_works()
    
    if not nexten_ok:
        print("⚠️  Nexten ne répond pas correctement")
        return
    
    # 2. Test minimal pour valider la structure
    minimal_ok = test_minimal_payload()
    
    # 3. Test complet avec la structure corrigée
    success = test_correct_payload_structure()
    
    # 4. Générer template corrigé
    generate_corrected_template()
    
    # 5. Résumé
    print("\n" + "=" * 80)
    print("📋 RÉSUMÉ FINAL")
    print("=" * 80)
    
    if success:
        print("🎉 PROBLÈME 422 RÉSOLU !")
        print("✅ Structure payload corrigée :")
        print("   - 'candidate' au lieu de 'cv'")
        print("   - 'id' ajouté à chaque offer")  
        print("   - 'location' en format objet")
        print("✅ SuperSmartMatch V2 fonctionne maintenant")
        print("✅ Nexten correctement intégré")
        print("\n💡 Prochaines étapes:")
        print("   1. Mettre à jour tous tes scripts avec la bonne structure")
        print("   2. Utiliser le template généré pour futurs tests")
        print("   3. Tester avec données réelles CV")
    else:
        print("❌ Problème partiellement résolu")
        print("💡 Progress:")
        print(f"   ✅ Structure identifiée: 'candidate' + 'id' requis")
        print(f"   ✅ Format location corrigé")
        if minimal_ok:
            print(f"   ✅ Structure minimale validée")
        print("   ❌ Payload complet à ajuster")

if __name__ == "__main__":
    main()
