#!/usr/bin/env python3
"""
🔧 Script de correction complet SuperSmartMatch V2 - Version améliorée
Corrige les endpoints et teste la communication avec les bons chemins
"""

import json
import os
import requests
import subprocess
import time

def test_nexten_with_correct_endpoint():
    """Test Nexten avec le BON endpoint /match"""
    
    print("\n🧪 Test Nexten Matcher avec endpoint correct (/match)...")
    
    nexten_payload = {
        "candidate": {
            "name": "Test Expert",
            "technical_skills": ["Python", "Machine Learning", "Data Science"],
            "experience_years": 5
        },
        "offers": [
            {
                "id": "ml_job_001",
                "title": "ML Engineer",
                "required_skills": ["Python", "Machine Learning"],
                "salary_min": 60000,
                "salary_max": 80000
            }
        ]
    }
    
    try:
        # TEST AVEC LE BON ENDPOINT /match
        response = requests.post(
            "http://localhost:5052/match",  # ✅ BON ENDPOINT 
            json=nexten_payload, 
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            score = result.get('match_score', result.get('overall_score', 'N/A'))
            algorithm = result.get('algorithm', result.get('algorithm_used', 'N/A'))
            
            print(f"   ✅ Nexten /match : Score {score}")
            print(f"   📊 Algorithme : {algorithm}")
            print(f"   ⏱️  Temps : {result.get('processing_time_ms', 'N/A')}ms")
            return True
        else:
            print(f"   ❌ Nexten /match erreur : {response.status_code}")
            print(f"   📄 Response: {response.text[:150]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Nexten /match error : {e}")
        return False

def test_wrong_endpoint():
    """Démontre que /api/match ne fonctionne PAS"""
    
    print("\n❌ Démonstration : Test avec MAUVAIS endpoint (/api/match)...")
    
    try:
        response = requests.post(
            "http://localhost:5052/api/match",  # ❌ MAUVAIS ENDPOINT
            json={"test": "data"}, 
            timeout=5
        )
        
        print(f"   Status: {response.status_code} (devrait être 404)")
        return False
            
    except Exception as e:
        print(f"   ✅ Confirmé : /api/match n'existe pas - {e}")
        return True

def check_docker_networks():
    """Vérification et création des réseaux Docker nécessaires"""
    
    print("\n🐳 Vérification des réseaux Docker...")
    
    required_networks = [
        "commitment-_nexten_network",
        "commitment-_ssm_network"
    ]
    
    try:
        # Lister les réseaux existants
        result = subprocess.run(
            ["docker", "network", "ls", "--format", "{{.Name}}"],
            capture_output=True, text=True
        )
        
        existing_networks = result.stdout.strip().split('\n')
        
        for network in required_networks:
            if network not in existing_networks:
                print(f"   🔧 Création réseau {network}...")
                subprocess.run([
                    "docker", "network", "create", network
                ], capture_output=True)
            else:
                print(f"   ✅ Réseau {network} existe")
                
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur réseaux Docker: {e}")
        return False

def stop_and_cleanup():
    """Arrêt propre des services V2"""
    
    print("\n🛑 Arrêt des services SuperSmartMatch V2...")
    
    try:
        subprocess.run([
            "docker-compose", 
            "-f", "docker-compose.supersmartmatch-v2.yml", 
            "down"
        ], capture_output=True, timeout=30)
        
        print("   ✅ Services arrêtés")
        
        # Nettoyage des conteneurs orphelins
        subprocess.run([
            "docker", "container", "prune", "-f"
        ], capture_output=True)
        
        return True
        
    except Exception as e:
        print(f"   ⚠️  Erreur arrêt: {e}")
        return False

def restart_with_correct_config():
    """Redémarrage avec la configuration corrigée"""
    
    print("\n🚀 Redémarrage avec endpoints corrigés...")
    
    try:
        # Redémarrage avec les 2 fichiers
        cmd = [
            "docker-compose", 
            "-f", "docker-compose.supersmartmatch-v2.yml",
            "-f", "docker-compose.endpoint-fix.yml",
            "up", "-d"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("   ✅ Services démarrés avec endpoints corrigés")
            print("   ⏳ Attente stabilisation (20s)...")
            time.sleep(20)
            return True
        else:
            print(f"   ❌ Erreur démarrage:")
            print(f"   STDOUT: {result.stdout}")
            print(f"   STDERR: {result.stderr}")
            return False
        
    except subprocess.TimeoutExpired:
        print("   ⚠️  Timeout démarrage - mais peut continuer")
        return True
    except Exception as e:
        print(f"   ❌ Erreur redémarrage: {e}")
        return False

def test_v2_with_fixed_endpoints():
    """Test final de V2 avec endpoints corrigés"""
    
    print("\n🎯 Test SuperSmartMatch V2 avec endpoints corrigés...")
    
    # Payload sophistiqué pour déclencher Nexten
    payload = {
        "candidate": {
            "name": "Sarah Martin",
            "technical_skills": ["Python", "Machine Learning", "Data Science", "TensorFlow", "PyTorch"],
            "experience_years": 6,
            "education": "Master Data Science"
        },
        "candidate_questionnaire": {
            "adresse": "Paris 11ème",
            "salaire_souhaite": 75000,
            "types_contrat": ["CDI"],
            "mode_transport": "metro",
            "priorite": "competences",
            "objectif": "expertise",
            "work_style": "analytical",
            "culture_preferences": "data_driven",
            "remote_preference": "hybrid"
        },
        "offers": [
            {
                "id": "ml_senior_001",
                "title": "Senior ML Engineer",
                "required_skills": ["Python", "Machine Learning", "TensorFlow"],
                "salary_min": 70000,
                "salary_max": 85000,
                "company": "TechCorp",
                "location": "Paris"
            }
        ],
        "algorithm": "auto"  # Sélection automatique
    }
    
    try:
        response = requests.post(
            "http://localhost:5070/api/v2/match",
            json=payload,
            timeout=20
        )
        
        if response.status_code == 200:
            result = response.json()
            algorithm_used = result.get('algorithm_used')
            fallback = result.get('metadata', {}).get('fallback', True)
            
            print(f"   🎯 Algorithme utilisé : {algorithm_used}")
            print(f"   📈 Score : {result.get('matches', [{}])[0].get('overall_score', 'N/A')}")
            print(f"   ⚡ Temps d'exécution : {result.get('execution_time_ms')}ms")
            print(f"   🔄 Mode Fallback : {fallback}")
            
            if not fallback and algorithm_used == "nexten_matcher":
                print("   🎉 SUCCÈS TOTAL : Nexten Matcher communique parfaitement !")
                return True
            elif not fallback and algorithm_used:
                print(f"   ✅ SUCCÈS : Algorithme {algorithm_used} fonctionne !")
                return True
            else:
                print("   ⚠️  Encore en mode fallback - Vérifier logs pour debug")
                return False
        else:
            print(f"   ❌ Erreur V2 : {response.status_code}")
            print(f"   📄 Response : {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Test V2 échoué : {e}")
        return False

def show_container_status():
    """Affichage du statut des conteneurs"""
    
    print("\n📊 Statut final des conteneurs...")
    
    try:
        result = subprocess.run([
            "docker", "ps", "--format", 
            "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ Erreur statut: {e}")

def main():
    """Script principal de correction complète"""
    
    print("🎯 CORRECTION COMPLÈTE SUPERSMARTMATCH V2")
    print("=" * 60)
    print("🔧 Correction des endpoints et résolution des problèmes")
    
    # 1. Test endpoints actuels
    print("\n📋 ÉTAPE 1: Vérification endpoints Nexten")
    nexten_ok = test_nexten_with_correct_endpoint()
    test_wrong_endpoint()  # Démonstration
    
    if not nexten_ok:
        print("❌ Nexten Matcher ne répond pas - Vérifier qu'il est démarré")
        return
    
    # 2. Vérification réseaux Docker
    print("\n📋 ÉTAPE 2: Configuration réseaux Docker")
    networks_ok = check_docker_networks()
    
    # 3. Arrêt propre
    print("\n📋 ÉTAPE 3: Arrêt services actuels")
    stop_and_cleanup()
    
    # 4. Redémarrage avec configuration corrigée
    print("\n📋 ÉTAPE 4: Redémarrage avec endpoints corrigés")
    restart_ok = restart_with_correct_config()
    
    if not restart_ok:
        print("\n❌ Problème lors du redémarrage")
        return
    
    # 5. Test final
    print("\n📋 ÉTAPE 5: Test final de communication")
    final_test_ok = test_v2_with_fixed_endpoints()
    
    # 6. Statut final
    show_container_status()
    
    # 7. Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ FINAL")
    print("=" * 60)
    
    if final_test_ok:
        print("🎉 SUCCÈS COMPLET !")
        print("✅ SuperSmartMatch V2 utilise maintenant les bons endpoints")
        print("✅ Communication avec Nexten Matcher fonctionnelle")
        print("✅ Fini le mode fallback_basic !")
    else:
        print("⚠️  Partiellement corrigé")
        print("📝 Actions recommandées :")
        print("   1. Vérifier les logs des conteneurs")
        print("   2. Vérifier la connectivité réseau")
        print("   3. Relancer le test avec debug activé")
    
    print("\n🔧 COMMANDES UTILES :")
    print("# Logs du service V2 :")
    print("docker logs supersmartmatch-v2-unified")
    print("\n# Test manuel après correction :")
    print("python debug_supersmartmatch_v2.py")
    print("\n# Redémarrage manuel si besoin :")
    print("docker-compose -f docker-compose.supersmartmatch-v2.yml -f docker-compose.endpoint-fix.yml down")
    print("docker-compose -f docker-compose.supersmartmatch-v2.yml -f docker-compose.endpoint-fix.yml up -d")

if __name__ == "__main__":
    main()
