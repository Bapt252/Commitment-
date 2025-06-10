#!/usr/bin/env python3
"""
Fix SuperSmartMatch V2 Endpoints Configuration
Corrige les URLs d'endpoints utilisées par V2 pour router vers Nexten et SSM V1
"""

import os
import re
import shutil
import subprocess
from datetime import datetime

def find_v2_config_files():
    """Trouve les fichiers de configuration de SuperSmartMatch V2"""
    
    print("🔍 RECHERCHE - Fichiers de configuration SuperSmartMatch V2")
    print("=" * 80)
    
    # Chemins possibles pour les configs
    possible_paths = [
        "./supersmartmatch-v2/",
        "./services/supersmartmatch-v2/", 
        "./src/supersmartmatch-v2/",
        "./v2/",
        "./"
    ]
    
    config_files = []
    
    for base_path in possible_paths:
        if os.path.exists(base_path):
            print(f"📁 Exploration: {base_path}")
            
            for root, dirs, files in os.walk(base_path):
                for file in files:
                    if file.endswith(('.py', '.yaml', '.yml', '.json', '.env', '.conf')):
                        filepath = os.path.join(root, file)
                        
                        # Lire le contenu pour chercher les endpoints
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            # Chercher les patterns d'endpoints incorrects
                            if any(pattern in content for pattern in [
                                'api/v1/queue-matching',
                                'api/v1/match',
                                'nexten_matcher',
                                'ssm_v1'
                            ]):
                                config_files.append(filepath)
                                print(f"   📄 Trouvé: {filepath}")
                                
                        except Exception as e:
                            pass
    
    print(f"\n📊 Total fichiers trouvés: {len(config_files)}")
    return config_files

def fix_endpoints_in_file(filepath):
    """Corrige les endpoints dans un fichier"""
    
    print(f"\n🔧 CORRECTION: {filepath}")
    
    # Créer backup
    backup_path = f"{filepath}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"   📁 Backup: {backup_path}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corrections des endpoints
        corrections = [
            # Nexten endpoints
            (r'http://nexten_matcher/api/v1/queue-matching', 'http://nexten_matcher/match'),
            (r'nexten_matcher/api/v1/queue-matching', 'nexten_matcher/match'),
            (r'/api/v1/queue-matching', '/match'),
            
            # SSM V1 endpoints  
            (r'http://ssm_v1/api/v1/match', 'http://ssm_v1/match'),
            (r'ssm_v1/api/v1/match', 'ssm_v1/match'),
            
            # URLs avec variables d'environnement
            (r'\${NEXTEN_URL}/api/v1/queue-matching', '${NEXTEN_URL}/match'),
            (r'\${SSM_V1_URL}/api/v1/match', '${SSM_V1_URL}/match'),
            
            # Configuration YAML/JSON
            (r'"api/v1/queue-matching"', '"/match"'),
            (r"'api/v1/queue-matching'", "'/match'"),
            (r'api/v1/queue-matching', 'match'),
            
            # Patterns Python avec f-strings
            (r'f".*?/api/v1/queue-matching"', lambda m: m.group(0).replace('/api/v1/queue-matching', '/match')),
            (r"f'.*?/api/v1/queue-matching'", lambda m: m.group(0).replace('/api/v1/queue-matching', '/match')),
        ]
        
        changes_made = 0
        
        for pattern, replacement in corrections:
            if callable(replacement):
                # Pour les lambda functions
                content, count = re.subn(pattern, replacement, content)
            else:
                # Pour les replacements simples
                if pattern in content:
                    content = content.replace(pattern, replacement)
                    count = 1
                else:
                    count = 0
                    
            if count > 0:
                changes_made += count
                print(f"   ✅ Corrigé: {pattern} -> {replacement if not callable(replacement) else 'function'}")
        
        # Sauvegarder si changements
        if changes_made > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   📝 {changes_made} corrections appliquées")
            return True
        else:
            print(f"   ℹ️  Aucune correction nécessaire")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def restart_v2_service():
    """Redémarre le service SuperSmartMatch V2"""
    
    print(f"\n🔄 REDÉMARRAGE - SuperSmartMatch V2")
    print("=" * 80)
    
    try:
        # Arrêter le conteneur
        print("⏹️  Arrêt du conteneur...")
        result = subprocess.run(["docker", "stop", "supersmartmatch-v2-unified"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Conteneur arrêté")
        else:
            print(f"   ⚠️  Arrêt: {result.stderr}")
        
        # Démarrer le conteneur
        print("▶️  Démarrage du conteneur...")
        result = subprocess.run(["docker", "start", "supersmartmatch-v2-unified"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Conteneur démarré")
            
            # Attendre un peu
            import time
            print("   ⏳ Attente stabilisation (10s)...")
            time.sleep(10)
            
            # Vérifier health
            print("   🏥 Vérification health...")
            import requests
            try:
                response = requests.get("http://localhost:5070/health", timeout=5)
                if response.status_code == 200:
                    print("   ✅ Service healthy")
                    return True
                else:
                    print(f"   ❌ Health check failed: {response.status_code}")
                    return False
            except Exception as e:
                print(f"   ❌ Health check error: {e}")
                return False
        else:
            print(f"   ❌ Démarrage échoué: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur redémarrage: {e}")
        return False

def test_corrected_endpoints():
    """Teste les endpoints corrigés"""
    
    print(f"\n🧪 TEST - Endpoints corrigés")
    print("=" * 80)
    
    import requests
    import uuid
    
    # Payload de test
    test_payload = {
        "candidate": {
            "name": "Test User",
            "email": "test@example.com",
            "skills": ["Python", "FastAPI"]
        },
        "offers": [{
            "id": str(uuid.uuid4()),
            "title": "Python Developer",
            "company": "TestCorp",
            "description": "Test job description",
            "location": {
                "city": "Paris",
                "country": "France"
            }
        }]
    }
    
    try:
        print("📤 Test SuperSmartMatch V2...")
        response = requests.post(
            "http://localhost:5070/match",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            algorithm = result.get('algorithm_used', 'N/A')
            print(f"🔧 Algorithm: {algorithm}")
            
            if 'nexten' in algorithm.lower():
                print("🎉 SUCCÈS ! Nexten utilisé !")
                return True
            else:
                print(f"⚠️  Fallback encore utilisé: {algorithm}")
                return False
        else:
            print(f"❌ Erreur: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔧 CORRECTION ENDPOINTS SUPERSMARTMATCH V2")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Trouver les fichiers de config
    config_files = find_v2_config_files()
    
    if not config_files:
        print("❌ Aucun fichier de configuration trouvé")
        print("💡 Actions manuelles nécessaires:")
        print("   1. Localiser le code source de SuperSmartMatch V2")
        print("   2. Chercher 'api/v1/queue-matching' et '/api/v1/match'")
        print("   3. Remplacer par '/match'")
        print("   4. Redémarrer le conteneur")
        return
    
    # 2. Corriger les fichiers
    print(f"\n🔧 CORRECTION DES FICHIERS")
    print("=" * 80)
    
    files_corrected = 0
    
    for filepath in config_files:
        if fix_endpoints_in_file(filepath):
            files_corrected += 1
    
    print(f"\n📊 Résumé corrections: {files_corrected}/{len(config_files)} fichiers corrigés")
    
    # 3. Redémarrer le service
    if files_corrected > 0:
        restart_success = restart_v2_service()
        
        if restart_success:
            # 4. Tester
            test_success = test_corrected_endpoints()
            
            print(f"\n" + "=" * 80)
            print("📋 RÉSUMÉ FINAL")
            print("=" * 80)
            
            if test_success:
                print("🎉 SUCCÈS TOTAL !")
                print("✅ Endpoints corrigés")
                print("✅ Service redémarré")
                print("✅ Nexten maintenant utilisé")
                print("\n💡 Prochaines étapes:")
                print("   1. Tester avec données réelles")
                print("   2. Valider performance complète")
            else:
                print("⚠️  Corrections appliquées mais test échoué")
                print("💡 Actions additionnelles:")
                print("   1. Vérifier les logs: docker logs supersmartmatch-v2-unified")
                print("   2. Vérifier si d'autres fichiers nécessitent correction")
        else:
            print("❌ Erreur redémarrage service")
    else:
        print("ℹ️  Aucune correction appliquée - fichiers déjà corrects ou corrections manuelles nécessaires")

if __name__ == "__main__":
    main()
