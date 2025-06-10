#!/usr/bin/env python3
"""
Script de correction des URLs de services pour SuperSmartMatch V2
Corrige la configuration pour permettre la communication inter-services
"""

import json
import os
import requests

def fix_service_urls():
    """Corrige les URLs des services externes"""
    
    # Configuration des URLs correctes
    config = {
        "NEXTEN_URL": "http://localhost:5052",
        "SUPERSMARTMATCH_V1_URL": "http://localhost:5062", 
        "REDIS_URL": "redis://localhost:6379",
        "SERVICE_PORT": "5070"
    }
    
    print("🔧 Correction des URLs de services...")
    
    # Si on est dans Docker, utiliser les noms de services
    if os.path.exists("/.dockerenv"):
        config.update({
            "NEXTEN_URL": "http://nexten-matcher:5052",
            "SUPERSMARTMATCH_V1_URL": "http://ssm_v1:5062",
            "REDIS_URL": "redis://redis-cache-v2-local:6379"
        })
        print("📦 Environnement Docker détecté")
    else:
        print("🖥️  Environnement local détecté")
    
    # Écrire la configuration dans un fichier .env
    env_content = "\n".join([f"{key}={value}" for key, value in config.items()])
    
    with open(".env.supersmartmatch_v2", "w") as f:
        f.write(env_content)
    
    print("✅ Configuration écrite dans .env.supersmartmatch_v2")
    
    return config

def test_connectivity_with_config(config):
    """Test la connectivité avec la nouvelle configuration"""
    
    print("\n🧪 Test de connectivité avec nouvelle config...")
    
    services = {
        "Nexten": config["NEXTEN_URL"],
        "V1": config["SUPERSMARTMATCH_V1_URL"]
    }
    
    results = {}
    
    for name, url in services.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Accessible via {url}")
                results[name] = True
            else:
                print(f"❌ {name}: HTTP {response.status_code} via {url}")
                results[name] = False
        except Exception as e:
            print(f"❌ {name}: Erreur {e} via {url}")
            results[name] = False
    
    return results

def create_docker_override():
    """Crée un override Docker pour corriger les URLs"""
    
    override_content = """version: '3.8'

services:
  supersmartmatch-v2-unified:
    environment:
      - NEXTEN_URL=http://nexten-matcher:5052
      - SUPERSMARTMATCH_V1_URL=http://ssm_v1:5062
      - REDIS_URL=redis://redis-cache-v2-local:6379
      - SERVICE_PORT=5070
      - ENVIRONMENT=production
      - LOG_LEVEL=DEBUG
    depends_on:
      - redis-cache-v2-local
    networks:
      - default
      - nexten_default
      
  ssm_v2:
    environment:
      - NEXTEN_URL=http://nexten-matcher:5052
      - SUPERSMARTMATCH_V1_URL=http://ssm_v1:5062
      - REDIS_URL=redis://redis-cache-v2-local:6379
    depends_on:
      - redis-cache-v2-local
    networks:
      - default
      - nexten_default

networks:
  nexten_default:
    external: true
    
"""
    
    with open("docker-compose.override.yml", "w") as f:
        f.write(override_content)
    
    print("✅ Fichier docker-compose.override.yml créé")

def restart_services():
    """Redémarre les services avec la nouvelle configuration"""
    import subprocess
    
    print("\n🔄 Redémarrage des services...")
    
    try:
        # Arrêt des services V2
        subprocess.run([
            "docker-compose", "-f", "docker-compose.supersmartmatch-v2.yml", 
            "down"
        ], check=True)
        
        print("⏸️  Services arrêtés")
        
        # Redémarrage avec override
        subprocess.run([
            "docker-compose", "-f", "docker-compose.supersmartmatch-v2.yml",
            "-f", "docker-compose.override.yml",
            "up", "-d"
        ], check=True)
        
        print("▶️  Services redémarrés avec nouvelle config")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du redémarrage: {e}")
        return False

def main():
    """Script principal de correction"""
    print("🛠️  CORRECTION SUPERSMARTMATCH V2")
    print("=" * 50)
    
    # 1. Correction des URLs
    config = fix_service_urls()
    
    # 2. Test de connectivité
    connectivity = test_connectivity_with_config(config)
    
    # 3. Création de l'override Docker
    create_docker_override()
    
    # 4. Proposition de redémarrage
    if not all(connectivity.values()):
        print("\n⚠️  Problèmes de connectivité détectés")
        print("🔄 Recommandation: Redémarrer avec la nouvelle configuration")
        
        response = input("\nRedémarrer les services maintenant? (y/N): ")
        if response.lower() in ['y', 'yes', 'o', 'oui']:
            restart_services()
    else:
        print("\n✅ Connectivité OK - Pas besoin de redémarrage")
    
    print("\n📋 INSTRUCTIONS MANUELLES:")
    print("1. Pour redémarrer manuellement:")
    print("   docker-compose -f docker-compose.supersmartmatch-v2.yml down")
    print("   docker-compose -f docker-compose.supersmartmatch-v2.yml -f docker-compose.override.yml up -d")
    print("\n2. Pour tester après redémarrage:")
    print("   python debug_supersmartmatch_v2.py")

if __name__ == "__main__":
    main()
