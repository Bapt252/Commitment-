#!/usr/bin/env python3
"""
Diagnostic : Pourquoi SuperSmartMatch V2 utilise le fallback au lieu de Nexten ?
Analyse la logique de routing et configuration de V2
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Configuration
SUPERSMARTMATCH_V2_URL = "http://localhost:5070"
NEXTEN_URL = "http://localhost:5052"

def check_v2_health_and_config():
    """Vérifie la santé et configuration de SuperSmartMatch V2"""
    
    print("🏥 DIAGNOSTIC - SuperSmartMatch V2 Health & Config")
    print("=" * 80)
    
    endpoints_to_check = [
        "/health",
        "/",
        "/docs",
        "/config",
        "/status",
        "/info"
    ]
    
    for endpoint in endpoints_to_check:
        try:
            url = f"{SUPERSMARTMATCH_V2_URL}{endpoint}"
            print(f"📡 Test {endpoint}...")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - OK")
                if endpoint == "/health":
                    try:
                        health_data = response.json()
                        print(f"   📊 Health: {json.dumps(health_data, indent=6)}")
                    except:
                        print(f"   📊 Health: {response.text[:200]}")
                elif endpoint in ["/config", "/status", "/info"]:
                    try:
                        config_data = response.json()
                        print(f"   📊 Config: {json.dumps(config_data, indent=6)}")
                    except:
                        print(f"   📊 Response: {response.text[:200]}")
            else:
                print(f"   ❌ {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
    
    print()

def test_v2_routing_decision():
    """Teste différents payloads pour comprendre la logique de routing"""
    
    print("🎯 DIAGNOSTIC - Logique de Routing SuperSmartMatch V2")
    print("=" * 80)
    
    # Différents types de tests pour déclencher Nexten
    test_cases = [
        {
            "name": "Payload simple",
            "payload": {
                "candidate": {
                    "name": "Test Simple",
                    "email": "simple@test.com",
                    "skills": ["Python"]
                },
                "offers": [{
                    "id": str(uuid.uuid4()),
                    "title": "Python Dev",
                    "company": "TechCorp",
                    "description": "Python developer needed",
                    "location": {"city": "Paris", "country": "France"}
                }]
            }
        },
        {
            "name": "Payload complexe",
            "payload": {
                "candidate": {
                    "name": "Test Complex",
                    "email": "complex@test.com",
                    "skills": ["Python", "FastAPI", "Docker", "Machine Learning", "PostgreSQL"],
                    "experience": [
                        {
                            "title": "Senior Developer",
                            "company": "BigTech",
                            "duration": "2020-2024",
                            "description": "Advanced Python development with ML focus"
                        }
                    ],
                    "education": [
                        {
                            "degree": "Master Computer Science",
                            "school": "Engineering School",
                            "year": "2020"
                        }
                    ]
                },
                "offers": [
                    {
                        "id": str(uuid.uuid4()),
                        "title": "Senior Python Developer",
                        "company": "InnovCorp",
                        "description": "We need an experienced Python developer with ML background for our AI team",
                        "requirements": ["Python", "FastAPI", "Machine Learning", "Docker"],
                        "salary_range": "60000-80000",
                        "contract_type": "CDI",
                        "location": {"city": "Paris", "region": "Île-de-France", "country": "France"}
                    },
                    {
                        "id": str(uuid.uuid4()),
                        "title": "ML Engineer",
                        "company": "DataCorp",
                        "description": "Machine learning engineer position for advanced AI projects",
                        "requirements": ["Python", "Machine Learning", "TensorFlow", "Docker"],
                        "salary_range": "70000-90000",
                        "contract_type": "CDI",
                        "location": {"city": "Lyon", "country": "France"}
                    }
                ]
            }
        },
        {
            "name": "Payload avec flag explicite",
            "payload": {
                "candidate": {
                    "name": "Test Nexten",
                    "email": "nexten@test.com",
                    "skills": ["Python", "FastAPI"]
                },
                "offers": [{
                    "id": str(uuid.uuid4()),
                    "title": "Python Developer",
                    "company": "TechCorp",
                    "description": "Python development position",
                    "location": {"city": "Paris", "country": "France"}
                }],
                "algorithm_preference": "nexten",  # Flag explicite
                "use_nexten": True,  # Flag alternatif
                "force_nexten": True  # Flag de force
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print(f"Payload size: {len(json.dumps(test_case['payload']))} chars")
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{SUPERSMARTMATCH_V2_URL}/match",
                json=test_case['payload'],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            end_time = time.time()
            
            print(f"📥 Status: {response.status_code}")
            print(f"⏱️  Temps: {(end_time - start_time)*1000:.1f}ms")
            
            if response.status_code == 200:
                result = response.json()
                algorithm = result.get('algorithm_used', 'N/A')
                print(f"🔧 Algorithm: {algorithm}")
                
                if 'nexten' in algorithm.lower():
                    print(f"   🎉 SUCCÈS ! Nexten utilisé !")
                else:
                    print(f"   ⚠️  Fallback utilisé: {algorithm}")
                
                # Analyser les détails de la réponse
                if 'processing_details' in result:
                    print(f"   📊 Details: {result['processing_details']}")
                if 'routing_info' in result:
                    print(f"   🛣️  Routing: {result['routing_info']}")
                    
            else:
                print(f"❌ Erreur: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur: {e}")

def test_nexten_connectivity_from_v2():
    """Teste si V2 peut accéder à Nexten (problème de réseau Docker ?)"""
    
    print(f"\n🌐 DIAGNOSTIC - Connectivité V2 → Nexten")
    print("=" * 80)
    
    # URLs possibles que V2 pourrait utiliser pour Nexten
    nexten_urls = [
        "http://localhost:5052/match",
        "http://nexten_matcher:80/match",
        "http://nexten_matcher:5052/match", 
        "http://127.0.0.1:5052/match",
        "http://nexten:80/match",
        "http://nexten:5052/match"
    ]
    
    test_payload = {
        "cv_text": "Python developer with FastAPI experience",
        "job_description": "We need Python developer for our team"
    }
    
    print("🔍 Test des URLs possibles pour Nexten:")
    
    for url in nexten_urls:
        try:
            print(f"   📡 Test {url}...")
            response = requests.post(
                url,
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"      ✅ OK - Score: {result.get('score', 'N/A')}")
            else:
                print(f"      ❌ {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print(f"      ❌ Connexion impossible")
        except Exception as e:
            print(f"      ❌ Erreur: {str(e)[:50]}")

def analyze_docker_networks():
    """Analyse les réseaux Docker pour identifier les problèmes de communication"""
    
    print(f"\n🐳 DIAGNOSTIC - Réseaux Docker")
    print("=" * 80)
    
    import subprocess
    
    try:
        # Liste des conteneurs
        print("📋 Conteneurs actifs:")
        result = subprocess.run(["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"], 
                              capture_output=True, text=True)
        print(result.stdout)
        
        print("\n🌐 Réseaux Docker:")
        result = subprocess.run(["docker", "network", "ls"], capture_output=True, text=True)
        print(result.stdout)
        
        # Inspect des réseaux commitment
        print("\n🔍 Réseau commitment- (détail):")
        result = subprocess.run(["docker", "network", "inspect", "commitment-_default"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            network_info = json.loads(result.stdout)
            containers = network_info[0].get('Containers', {})
            for container_id, info in containers.items():
                print(f"   📦 {info.get('Name', 'N/A')}: {info.get('IPv4Address', 'N/A')}")
        else:
            print("   ❌ Réseau commitment-_default non trouvé")
            
    except Exception as e:
        print(f"❌ Erreur Docker: {e}")

def main():
    """Fonction principale de diagnostic"""
    print("🔍 DIAGNOSTIC COMPLET - SuperSmartMatch V2 Routing vers Nexten")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Vérifier la santé de V2
    check_v2_health_and_config()
    
    # 2. Tester la logique de routing
    test_v2_routing_decision()
    
    # 3. Tester la connectivité V2 → Nexten
    test_nexten_connectivity_from_v2()
    
    # 4. Analyser les réseaux Docker
    analyze_docker_networks()
    
    # 5. Résumé et recommandations
    print(f"\n" + "=" * 80)
    print("📋 RÉSUMÉ DIAGNOSTIC")
    print("=" * 80)
    
    print("🎯 Problème identifié:")
    print("   ✅ SuperSmartMatch V2 répond (Status 200)")
    print("   ✅ Structure payload correcte")
    print("   ❌ V2 utilise 'v2_routed_fallback_basic' au lieu de 'nexten_matcher'")
    
    print(f"\n💡 Causes possibles:")
    print("   1. Configuration de routing incorrecte dans V2")
    print("   2. Problème de connectivité V2 → Nexten (Docker network)")
    print("   3. Critères de sélection d'algorithme trop restrictifs")
    print("   4. URL Nexten incorrecte dans la config V2")
    print("   5. Variables d'environnement manquantes")
    
    print(f"\n🛠️  Actions recommandées:")
    print("   1. Vérifier les logs de SuperSmartMatch V2:")
    print("      docker logs supersmartmatch-v2-unified")
    print("   2. Vérifier la configuration de V2 (endpoints Nexten)")
    print("   3. Tester la connectivité réseau entre conteneurs")
    print("   4. Ajuster la logique de routing si nécessaire")

if __name__ == "__main__":
    main()
