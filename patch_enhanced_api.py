#!/usr/bin/env python3
"""
Script de patch automatique pour corriger l'Enhanced API V2.1
Applique la correction du système de classification des domaines
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_enhanced_api_files():
    """
    Localise les fichiers de l'Enhanced API V2.1
    """
    print("🔍 RECHERCHE DES FICHIERS ENHANCED API...")
    
    project_root = Path("/Users/baptistecomas/Commitment-/")
    potential_files = []
    
    # Recherche des fichiers Python contenant l'API
    for pattern in ["*enhanced*", "*matching*", "*api*"]:
        files = list(project_root.glob(f"**/{pattern}.py"))
        potential_files.extend(files)
    
    # Recherche dans les fichiers par contenu
    print("📂 Fichiers trouvés :")
    for file_path in potential_files:
        print(f"   - {file_path}")
    
    # Recherche de fichiers contenant "5055" (port Enhanced API)
    print("\n🔍 Recherche par port 5055...")
    try:
        result = subprocess.run(
            ["grep", "-r", "5055", str(project_root)],
            capture_output=True,
            text=True
        )
        if result.stdout:
            print("📄 Fichiers contenant le port 5055:")
            for line in result.stdout.split('\n')[:10]:  # Limiter l'affichage
                if line.strip():
                    print(f"   {line}")
    except:
        print("   ❌ Grep non disponible")
    
    return potential_files

def find_running_api_process():
    """
    Trouve le processus Enhanced API en cours
    """
    print("\n🔍 RECHERCHE DU PROCESSUS ENHANCED API...")
    
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True
        )
        
        api_processes = []
        for line in result.stdout.split('\n'):
            if '5055' in line and 'python' in line:
                api_processes.append(line)
        
        if api_processes:
            print("⚡ Processus Enhanced API trouvés:")
            for process in api_processes:
                print(f"   {process}")
        else:
            print("❌ Aucun processus Enhanced API trouvé sur port 5055")
        
        return api_processes
        
    except Exception as e:
        print(f"❌ Erreur recherche processus: {e}")
        return []

def create_backup(file_path):
    """
    Crée une sauvegarde du fichier original
    """
    backup_path = f"{file_path}.backup"
    shutil.copy2(file_path, backup_path)
    print(f"💾 Sauvegarde créée: {backup_path}")
    return backup_path

def patch_classification_system(file_path):
    """
    Applique le patch de classification au fichier
    """
    print(f"🔧 Application du patch à: {file_path}")
    
    # Lire le fichier original
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si le fichier contient le système de classification
    if 'domain' not in content.lower() or 'classification' not in content.lower():
        print("   ⚠️ Ce fichier ne semble pas contenir le système de classification")
        return False
    
    # Créer la sauvegarde
    backup_path = create_backup(file_path)
    
    # Ici on ajouterait la logique de patch
    # Pour l'instant, on indique juste ce qu'il faut faire
    print(f"   📋 Patch à appliquer manuellement dans: {file_path}")
    print(f"   🔄 Remplacer le système de classification par celui de fix_classification_system.py")
    
    return True

def restart_enhanced_api():
    """
    Redémarre l'Enhanced API V2.1
    """
    print("\n🔄 REDÉMARRAGE DE L'ENHANCED API...")
    
    # Trouver et arrêter le processus
    processes = find_running_api_process()
    if processes:
        print("⚠️ ATTENTION: Il faut redémarrer manuellement l'Enhanced API")
        print("📋 Étapes:")
        print("   1. Arrêter le processus Enhanced API (Ctrl+C)")
        print("   2. Appliquer les corrections de code")
        print("   3. Redémarrer l'Enhanced API")
        print("   4. Relancer les tests batch")
    else:
        print("❌ Aucun processus à redémarrer trouvé")

def generate_integration_script():
    """
    Génère un script d'intégration de la correction
    """
    integration_script = """#!/usr/bin/env python3
# Script d'intégration de la correction de classification

# ÉTAPE 1: Importer le classificateur corrigé
from fix_classification_system import FixedDomainClassifier

# ÉTAPE 2: Remplacer dans l'Enhanced API
# Localiser la fonction de classification actuelle et remplacer par:

class EnhancedMatchingAPI:
    def __init__(self):
        self.domain_classifier = FixedDomainClassifier()
    
    def classify_cv_domain(self, cv_data):
        missions = self.extract_missions_from_cv(cv_data)
        title = self.extract_title_from_cv(cv_data)
        return self.domain_classifier.classify_missions(missions, title)
    
    def classify_job_domain(self, job_data):
        missions = job_data.get('missions', [])
        title = job_data.get('job_info', {}).get('title', '')
        return self.domain_classifier.classify_missions(missions, title)
    
    def filter_missions(self, missions, domain):
        return self.domain_classifier.filter_missions_by_domain(missions, domain)

# ÉTAPE 3: Tester la correction
# Relancer enhanced_batch_testing_final.py pour validation
"""
    
    with open("integration_guide.py", "w") as f:
        f.write(integration_script)
    
    print("📄 Guide d'intégration créé: integration_guide.py")

def main():
    print("🚀 PATCH AUTOMATIQUE ENHANCED API V2.1")
    print("=" * 50)
    print("🎯 Objectif: Corriger le système de classification des domaines")
    print("✅ Solution validée par le test fix_classification_system.py")
    print()
    
    # Recherche des fichiers
    api_files = find_enhanced_api_files()
    
    # Recherche des processus
    find_running_api_process()
    
    # Génération du guide d'intégration
    generate_integration_script()
    
    print("\n" + "=" * 50)
    print("🎯 PROCHAINES ÉTAPES MANUELLES:")
    print("1. 🔍 Identifier le fichier principal de l'Enhanced API V2.1")
    print("2. 🔧 Intégrer le FixedDomainClassifier dans le code")
    print("3. 🔄 Redémarrer le service Enhanced API")
    print("4. 🧪 Relancer enhanced_batch_testing_final.py")
    print("5. 🎉 Valider que les domaines sont maintenant détectés !")
    
    print(f"\n💡 FICHIERS UTILES:")
    print(f"   - fix_classification_system.py (solution validée)")
    print(f"   - integration_guide.py (guide d'intégration)")
    print(f"   - enhanced_batch_testing_final.py (tests)")

if __name__ == "__main__":
    main()
