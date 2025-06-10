#!/usr/bin/env python3
"""
Script de diagnostic pour SuperSmartMatch V2
Vérifie la communication entre services
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

def test_nexten_direct():
    """Test direct de Nexten Matcher"""
    nexten_url = "http://localhost:5052"
    
    # Test simple de matching
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
        print("\n🧪 Test direct Nexten Matcher...")
        response = requests.post(f"{nexten_url}/api/match", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Nexten répond - Matches: {len(result.get('matches', []))}")
            return True
        else:
            print(f"❌ Nexten erreur - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Nexten inaccessible - {e}")
        return False

def test_v1_direct():
    """Test direct de SuperSmartMatch V1"""
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
        print("\n🧪 Test direct SuperSmartMatch V1...")
        response = requests.post(f"{v1_url}/match", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ V1 répond - Matches: {len(result.get('matches', []))}")
            return True
        else:
            print(f"❌ V1 erreur - Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ V1 inaccessible - {e}")
        return False

def test_v2_internal_routing():
    """Test de routage interne V2"""
    v2_url = "http://localhost:5070"
    
    # Test avec force algorithm pour bypasser la sélection auto
    payload = {
        "candidate": {
            "name": "Test User",
            "technical_skills": ["Python", "Machine Learning"]
        },
        "offers": [
            {
                "id": "test_001",
                "title": "ML Engineer",
                "required_skills": ["Python", "Machine Learning"]
            }
        ],
        "algorithm": "nexten"  # Force Nexten
    }
    
    try:
        print("\n🧪 Test V2 avec algorithm=nexten forcé...")
        response = requests.post(f"{v2_url}/api/v2/match", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            algorithm_used = result.get('algorithm_used')
            fallback = result.get('metadata', {}).get('fallback', False)
            
            print(f"   Algorithme utilisé: {algorithm_used}")
            print(f"   Fallback: {fallback}")
            
            if not fallback and algorithm_used == "nexten_matcher":
                print("✅ Communication V2 → Nexten OK")
                return True
            else:
                print("❌ Communication V2 → Nexten KO")
                return False
        else:
            print(f"❌ V2 erreur - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ V2 test failed - {e}")
        return False

def check_docker_network():
    """Vérification du réseau Docker"""
    import subprocess
    
    try:
        print("\n🐳 Vérification réseau Docker...")
        
        # Lister les conteneurs
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Ports}}"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("📋 Conteneurs actifs:")
            print(result.stdout)
        
        # Vérifier le réseau
        result = subprocess.run(
            ["docker", "network", "ls"],
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            print("\n🌐 Réseaux Docker:")
            print(result.stdout)
            
    except Exception as e:
        print(f"❌ Erreur Docker - {e}")

def main():
    """Diagnostic complet"""
    print("🔍 Diagnostic SuperSmartMatch V2")
    print("=" * 50)
    
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
        return False
    
    # 2. Tests directs
    print("\n2️⃣ Tests de communication directe")
    nexten_ok = test_nexten_direct()
    v1_ok = test_v1_direct()
    
    # 3. Test routage V2
    print("\n3️⃣ Test routage interne V2")
    routing_ok = test_v2_internal_routing()
    
    # 4. Diagnostic Docker
    check_docker_network()
    
    # 5. Résumé
    print("\n📊 RÉSUMÉ")
    print("=" * 30)
    print(f"Services UP: {'✅' if all_healthy else '❌'}")
    print(f"Nexten direct: {'✅' if nexten_ok else '❌'}")
    print(f"V1 direct: {'✅' if v1_ok else '❌'}")
    print(f"V2 routing: {'✅' if routing_ok else '❌'}")
    
    if all_healthy and nexten_ok and v1_ok and routing_ok:
        print("\n🎉 Tout fonctionne parfaitement !")
    elif all_healthy and (nexten_ok or v1_ok):
        print("\n⚠️  Services UP mais problème de communication V2")
        print("   → Vérifier la configuration des URLs dans V2")
    else:
        print("\n❌ Problèmes détectés")
        print("   → Vérifier la configuration Docker")

if __name__ == "__main__":
    main()
