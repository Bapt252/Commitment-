#!/usr/bin/env python3
"""
Script de correction spécialisé pour les endpoints SuperSmartMatch V2
Corrige les URLs des services avec les bons endpoints
"""

import json
import os
import requests
import subprocess

def create_fixed_docker_override():
    """Crée un override Docker avec les bons endpoints"""
    
    override_content = """version: '3.8'

services:
  supersmartmatch-v2-unified:
    environment:
      # URLs des services avec bons endpoints
      - NEXTEN_URL=http://nexten_matcher:80
      - NEXTEN_ENDPOINT=/match
      - SUPERSMARTMATCH_V1_URL=http://ssm_v1:80
      - SUPERSMARTMATCH_V1_ENDPOINT=/match
      - REDIS_URL=redis://redis-cache-v2-local:6379
      - SERVICE_PORT=5070
      - ENVIRONMENT=production
      - LOG_LEVEL=DEBUG
      # Configuration des timeouts
      - NEXTEN_TIMEOUT_MS=5000
      - V1_TIMEOUT_MS=3000
      - CACHE_TTL=300
    networks:
      - default
      - commitment-_nexten_network
      - commitment-_ssm_network
    depends_on:
      - redis-cache-v2-local
      
  ssm_v2:
    environment:
      - NEXTEN_URL=http://nexten_matcher:80
      - NEXTEN_ENDPOINT=/match
      - SUPERSMARTMATCH_V1_URL=http://ssm_v1:80
      - SUPERSMARTMATCH_V1_ENDPOINT=/match
      - REDIS_URL=redis://redis-cache-v2-local:6379
      - LOG_LEVEL=DEBUG
    networks:
      - default
      - commitment-_nexten_network
      - commitment-_ssm_network
    depends_on:
      - redis-cache-v2-local

networks:
  commitment-_nexten_network:
    external: true
  commitment-_ssm_network:
    external: true
"""
    
    with open("docker-compose.endpoint-fix.yml", "w") as f:
        f.write(override_content)
    
    print("✅ Fichier docker-compose.endpoint-fix.yml créé avec bons endpoints")

def test_correct_endpoints():
    """Test des bons endpoints"""
    
    print("\n🧪 Test des bons endpoints...")
    
    # Test Nexten avec bon endpoint
    nexten_payload = {
        "candidate": {
            "name": "Test Expert",
            "technical_skills": ["Python", "Machine Learning", "Data Science"]
        },
        "offers": [
            {
                "id": "ml_job_001",
                "title": "ML Engineer",
                "required_skills": ["Python", "Machine Learning"]
            }
        ]
    }
    
    try:
        print("   Testing Nexten /match...")
        response = requests.post(
            "http://localhost:5052/match", 
            json=nexten_payload, 
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Nexten répond : Score {result.get('match_score', 'N/A')}")
            print(f"   📊 Algorithme : {result.get('algorithm', 'N/A')}")
            print(f"   ⏱️  Temps : {result.get('processing_time_ms', 'N/A')}ms")
            return True
        else:
            print(f"   ❌ Nexten erreur : {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Nexten error : {e}")
        return False

def restart_with_fix():
    """Redémarre avec la correction des endpoints"""
    
    print("\n🔄 Redémarrage avec endpoints corrigés...")
    
    try:
        # Arrêt des services
        subprocess.run([
            "docker-compose", "-f", "docker-compose.supersmartmatch-v2.yml", 
            "down"
        ], check=True, capture_output=True)
        
        print("   ⏸️  Services arrêtés")
        
        # Redémarrage avec la correction
        subprocess.run([
            "docker-compose", 
            "-f", "docker-compose.supersmartmatch-v2.yml",
            "-f", "docker-compose.endpoint-fix.yml",
            "up", "-d"
        ], check=True, capture_output=True)
        
        print("   ▶️  Services redémarrés avec endpoints corrigés")
        print("   ⏳ Attente stabilisation (15s)...")
        
        import time
        time.sleep(15)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur redémarrage : {e}")
        return False

def test_v2_after_fix():
    """Test V2 après correction"""
    
    print("\n🎯 Test SuperSmartMatch V2 après correction...")
    
    # Test avec questionnaire complet pour déclencher Nexten
    payload = {
        "candidate": {
            "name": "Sarah Martin",
            "technical_skills": ["Python", "Machine Learning", "Data Science", "TensorFlow"],
            "experience_years": 6
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
                "salary_max": 85000
            }
        ],
        "algorithm": "auto"
    }
    
    try:
        response = requests.post(
            "http://localhost:5070/api/v2/match",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            algorithm_used = result.get('algorithm_used')
            fallback = result.get('metadata', {}).get('fallback', True)
            
            print(f"   🎯 Algorithme : {algorithm_used}")
            print(f"   📈 Score : {result.get('matches', [{}])[0].get('overall_score', 'N/A')}")
            print(f"   ⚡ Temps : {result.get('execution_time_ms')}ms")
            print(f"   🔄 Fallback : {fallback}")
            
            if not fallback and algorithm_used == "nexten_matcher":
                print("   🎉 SUCCESS : Nexten Matcher fonctionne parfaitement !")
                return True
            elif not fallback:
                print(f"   ✅ SUCCESS : Algorithme {algorithm_used} fonctionne !")
                return True
            else:
                print("   ⚠️  Encore en fallback - Need more investigation")
                return False
        else:
            print(f"   ❌ V2 error : {response.status_code}")
            print(f"   Response : {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ V2 test failed : {e}")
        return False

def main():
    """Script principal de correction des endpoints"""
    print("🎯 CORRECTION ENDPOINTS SUPERSMARTMATCH V2")
    print("=" * 55)
    
    # 1. Test endpoints actuels
    nexten_ok = test_correct_endpoints()
    
    # 2. Création de la configuration corrigée
    create_fixed_docker_override()
    
    # 3. Redémarrage avec correction
    if nexten_ok:
        print("\n💡 Nexten endpoint fonctionne - Redémarrage avec correction...")
        restart_ok = restart_with_fix()
        
        if restart_ok:
            # 4. Test final
            v2_ok = test_v2_after_fix()
            
            if v2_ok:
                print("\n🎉 SUCCÈS COMPLET !")
                print("SuperSmartMatch V2 utilise maintenant les bons endpoints")
            else:
                print("\n⚠️  Partiellement corrigé - Besoin d'investigation supplémentaire")
        else:
            print("\n❌ Problème lors du redémarrage")
    else:
        print("\n❌ Nexten endpoint ne fonctionne pas")
    
    print("\n📋 COMMANDES MANUELLES :")
    print("# Redémarrage manuel avec endpoints corrigés :")
    print("docker-compose -f docker-compose.supersmartmatch-v2.yml down")
    print("docker-compose -f docker-compose.supersmartmatch-v2.yml -f docker-compose.endpoint-fix.yml up -d")
    print("\n# Test final :")
    print("python debug_supersmartmatch_v2.py")

if __name__ == "__main__":
    main()
