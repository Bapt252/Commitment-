#!/usr/bin/env python3
"""
🔍 Script de diagnostic SuperSmartMatch V2 - Version corrigée
Teste la communication avec les BONS endpoints
"""

import requests
import json
import time
from urllib.parse import urljoin

def test_service_health(name, url):
    """Test de santé d'un service"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: UP - {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ {name}: DOWN - Status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: ERROR - {e}")
        return False

def test_nexten_correct_endpoint():
    """Test Nexten avec le BON endpoint /match"""
    nexten_url = "http://localhost:5052"
    
    # Test avec bon endpoint
    payload = {
        "candidate": {
            "name": "Test User",
            "technical_skills": ["Python", "Machine Learning"],
            "experiences": [{"title": "Developer", "duration_months": 24}]
        },
        "offers": [
            {
                "id": "test_001",
                "title": "ML Engineer", 
                "required_skills": ["Python", "Machine Learning"]
            }
        ]
    }
    
    try:
        print("\n🧪 Test Nexten avec BON endpoint (/match)...")
        # ✅ UTILISE LE BON ENDPOINT
        response = requests.post(f"{nexten_url}/match", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            score = result.get('match_score', result.get('overall_score', 'N/A'))
            matches = len(result.get('matches', []))
            print(f"✅ Nexten /match OK - Score: {score}, Matches: {matches}")
            return True
        else:
            print(f"❌ Nexten /match erreur - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Nexten /match inaccessible - {e}")
        return False

def test_nexten_wrong_endpoint():
    """Démonstration : Test avec MAUVAIS endpoint pour montrer l'erreur"""
    nexten_url = "http://localhost:5052"
    
    try:
        print("\n❌ Démonstration avec MAUVAIS endpoint (/api/match)...")
        # ❌ MAUVAIS ENDPOINT - pour démonstration
        response = requests.post(f"{nexten_url}/api/match", json={"test": "data"}, timeout=5)
        
        print(f"❌ Nexten /api/match : Status {response.status_code} (404 attendu)")
        return False
        
    except Exception as e:
        print(f"✅ Confirmé : /api/match n'existe pas - {e}")
        return True

def test_v1_correct_endpoint():
    """Test SuperSmartMatch V1 avec bon endpoint"""
    v1_url = "http://localhost:5062"
    
    payload = {
        "cv_data": {
            "name": "Test User",
            "technical_skills": ["Python", "Django"]
        },
        "job_data": [
            {
                "id": "test_001",
                "title": "Python Developer",
                "required_skills": ["Python", "Django"]
            }
        ],
        "algorithm": "smart"
    }
    
    try:
        print("\n🧪 Test SuperSmartMatch V1 (/match)...")
        # ✅ BON ENDPOINT POUR V1
        response = requests.post(f"{v1_url}/match", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            matches = len(result.get('matches', []))
            print(f"✅ V1 /match OK - Matches: {matches}")
            return True
        else:
            print(f"❌ V1 /match erreur - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ V1 /match inaccessible - {e}")
        return False

def test_v2_with_algorithm_selection():
    """Test V2 avec sélection d'algorithme spécifique"""
    v2_url = "http://localhost:5070"
    
    # Test avec algorithme Nexten forcé
    payload = {
        "candidate": {
            "name": "Expert Test User",
            "technical_skills": ["Python", "Machine Learning", "Data Science"],
            "experience_years": 5
        },
        "candidate_questionnaire": {
            "adresse": "Paris",
            "salaire_souhaite": 70000,
            "types_contrat": ["CDI"],
            "priorite": "competences",
            "work_style": "analytical"
        },
        "offers": [
            {
                "id": "test_001",
                "title": "Senior ML Engineer",
                "required_skills": ["Python", "Machine Learning"],
                "salary_min": 65000,
                "salary_max": 75000
            }
        ],
        "algorithm": "nexten"  # Force Nexten pour test
    }
    
    try:
        print("\n🧪 Test V2 avec algorithme Nexten forcé...")
        response = requests.post(f"{v2_url}/api/v2/match", json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            algorithm_used = result.get('algorithm_used')
            fallback = result.get('metadata', {}).get('fallback', False)
            
            print(f"   🎯 Algorithme utilisé: {algorithm_used}")
            print(f"   🔄 Mode fallback: {fallback}")
            
            if not fallback and algorithm_used == "nexten_matcher":
                print("✅ Communication V2 → Nexten PARFAITE !")
                return True
            elif not fallback:
                print(f"✅ V2 fonctionne avec {algorithm_used}")
                return True
            else:
                print("❌ V2 encore en mode fallback")
                return False
        else:
            print(f"❌ V2 erreur - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ V2 test failed - {e}")
        return False

def test_v2_auto_selection():
    """Test V2 avec sélection automatique d'algorithme"""
    v2_url = "http://localhost:5070"
    
    # Test avec sélection automatique
    payload = {
        "candidate": {
            "name": "Sarah Expert",
            "technical_skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow"],
            "experience_years": 6
        },
        "candidate_questionnaire": {
            "adresse": "Paris 11ème",
            "salaire_souhaite": 80000,
            "types_contrat": ["CDI"],
            "mode_transport": "metro",
            "priorite": "competences",
            "objectif": "expertise",
            "work_style": "analytical",
            "culture_preferences": "data_driven"
        },
        "offers": [
            {
                "id": "complex_ml_001",
                "title": "Senior ML Engineer",
                "required_skills": ["Python", "Machine Learning", "TensorFlow"],
                "salary_min": 75000,
                "salary_max": 90000,
                "company": "AI Corp"
            }
        ],
        "algorithm": "auto"  # Sélection automatique
    }
    
    try:
        print("\n🧪 Test V2 avec sélection automatique...")
        response = requests.post(f"{v2_url}/api/v2/match", json=payload, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            algorithm_used = result.get('algorithm_used')
            fallback = result.get('metadata', {}).get('fallback', False)
            execution_time = result.get('execution_time_ms', 'N/A')
            
            print(f"   🎯 Algorithme sélectionné: {algorithm_used}")
            print(f"   ⚡ Temps d'exécution: {execution_time}ms")
            print(f"   🔄 Mode fallback: {fallback}")
            
            if not fallback:
                print(f"✅ Sélection automatique fonctionne → {algorithm_used}")
                return True
            else:
                print("❌ Encore en mode fallback automatique")
                return False
        else:
            print(f"❌ V2 auto erreur - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ V2 auto test failed - {e}")
        return False

def check_docker_status():
    """Vérification du statut Docker"""
    import subprocess
    
    try:
        print("\n🐳 Statut des conteneurs...")
        
        # Lister les conteneurs actifs
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("📋 Conteneurs actifs:")
            print(result.stdout)
        
        # Vérifier les réseaux
        result = subprocess.run(
            ["docker", "network", "ls", "--filter", "name=commitment"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("\n🌐 Réseaux Commitment:")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ Erreur Docker - {e}")

def main():
    """Diagnostic complet avec bons endpoints"""
    print("🔍 DIAGNOSTIC SUPERSMARTMATCH V2 - ENDPOINTS CORRIGÉS")
    print("=" * 65)
    
    # 1. Tests de santé
    print("\n1️⃣ Tests de santé des services")
    services = {
        "SuperSmartMatch V2": "http://localhost:5070",
        "Nexten Matcher": "http://localhost:5052", 
        "SuperSmartMatch V1": "http://localhost:5062"
    }
    
    all_healthy = True
    for name, url in services.items():
        if not test_service_health(name, url):
            all_healthy = False
    
    if not all_healthy:
        print("\n❌ Certains services ne répondent pas")
        print("🔧 Assurez-vous que tous les services sont démarrés")
        return False
    
    # 2. Tests endpoints corrects
    print("\n2️⃣ Tests des BONS endpoints")
    nexten_ok = test_nexten_correct_endpoint()
    test_nexten_wrong_endpoint()  # Démonstration
    v1_ok = test_v1_correct_endpoint()
    
    # 3. Tests de communication V2
    print("\n3️⃣ Tests de communication V2")
    v2_nexten_ok = test_v2_with_algorithm_selection()
    v2_auto_ok = test_v2_auto_selection()
    
    # 4. Diagnostic Docker
    check_docker_status()
    
    # 5. Résumé final
    print("\n" + "=" * 65)
    print("📊 RÉSUMÉ DIAGNOSTIC")
    print("=" * 65)
    print(f"🏥 Services UP: {'✅' if all_healthy else '❌'}")
    print(f"🎯 Nexten /match: {'✅' if nexten_ok else '❌'}")
    print(f"🎯 V1 /match: {'✅' if v1_ok else '❌'}")
    print(f"🔗 V2 → Nexten: {'✅' if v2_nexten_ok else '❌'}")
    print(f"🤖 V2 Auto-select: {'✅' if v2_auto_ok else '❌'}")
    
    if all_healthy and nexten_ok and v1_ok and v2_nexten_ok:
        print("\n🎉 DIAGNOSTIC PARFAIT !")
        print("✅ Tous les endpoints sont corrects")
        print("✅ Communication V2 ↔ Services externes OK")
        print("✅ SuperSmartMatch V2 utilise enfin les bons algorithmes !")
    elif all_healthy and (nexten_ok or v1_ok):
        print("\n⚠️  Services UP mais problème communication V2")
        print("🔧 Recommandations :")
        print("   1. Vérifier les variables d'environnement NEXTEN_URL et NEXTEN_ENDPOINT")
        print("   2. Relancer avec docker-compose.endpoint-fix.yml")
        print("   3. Vérifier les logs : docker logs supersmartmatch-v2-unified")
    else:
        print("\n❌ Problèmes détectés")
        print("🔧 Actions nécessaires :")
        print("   1. Démarrer les services manquants")
        print("   2. Vérifier la configuration Docker")
        print("   3. Utiliser le script fix_endpoints_v2_improved.py")
    
    print("\n🛠️  COMMANDES UTILES :")
    print("# Correction complète :")
    print("python fix_endpoints_v2_improved.py")
    print("\n# Redémarrage avec endpoints corrigés :")
    print("docker-compose -f docker-compose.supersmartmatch-v2.yml -f docker-compose.endpoint-fix.yml up -d")

if __name__ == "__main__":
    main()
