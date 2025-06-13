#!/usr/bin/env python3
"""
🔧 Script de diagnostic pour le problème Zachary CV
Teste étape par étape le parsing du CV de Zachary
"""

import requests
import os
import json
from pathlib import Path

# Configuration
CV_PARSER_URL = "http://localhost:5051"
ZACHARY_CV_PATH = "/Users/baptistecomas/Desktop/CV TEST/Zachary.pdf"

def test_service_health():
    """Test la santé du service CV Parser"""
    print("🔍 Test de santé du CV Parser...")
    try:
        response = requests.get(f"{CV_PARSER_URL}/health", timeout=10)
        if response.ok:
            print(f"   ✅ Service OK: {response.json()}")
            return True
        else:
            print(f"   ❌ Service KO: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Service inaccessible: {e}")
        return False

def test_file_properties():
    """Vérifie les propriétés du fichier Zachary"""
    print("📄 Vérification du fichier Zachary.pdf...")
    
    if not os.path.exists(ZACHARY_CV_PATH):
        print(f"   ❌ Fichier introuvable: {ZACHARY_CV_PATH}")
        return False
    
    file_size = os.path.getsize(ZACHARY_CV_PATH)
    print(f"   📊 Taille: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    
    if file_size == 0:
        print("   ❌ Fichier vide!")
        return False
    elif file_size > 10 * 1024 * 1024:  # 10MB
        print("   ⚠️ Fichier très volumineux (>10MB)")
    
    # Test de lecture
    try:
        with open(ZACHARY_CV_PATH, 'rb') as f:
            header = f.read(10)
            if header.startswith(b'%PDF'):
                print("   ✅ Format PDF valide")
                return True
            else:
                print(f"   ❌ Format PDF invalide: {header}")
                return False
    except Exception as e:
        print(f"   ❌ Erreur lecture fichier: {e}")
        return False

def test_cv_parsing_simple():
    """Test simple du parsing CV"""
    print("🧪 Test parsing CV simple...")
    
    try:
        with open(ZACHARY_CV_PATH, 'rb') as cv_file:
            files = {'file': ('zachary.pdf', cv_file, 'application/pdf')}
            data = {'force_refresh': 'false'}
            
            response = requests.post(
                f"{CV_PARSER_URL}/api/parse-cv/",
                files=files,
                data=data,
                timeout=30
            )
            
            print(f"   📡 Status Code: {response.status_code}")
            print(f"   📝 Headers: {dict(response.headers)}")
            
            if response.ok:
                result = response.json()
                print("   ✅ Parsing réussi!")
                candidate_name = result.get('data', {}).get('personal_info', {}).get('name', 'Non détecté')
                print(f"   👤 Candidat: {candidate_name}")
                
                # Afficher quelques détails
                data = result.get('data', {})
                skills = data.get('technical_skills', [])
                print(f"   💼 Compétences: {len(skills)} techniques")
                
                return True, result
            else:
                print(f"   ❌ Erreur: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   📄 Détail: {error_detail}")
                except:
                    print(f"   📄 Réponse brute: {response.text[:200]}...")
                return False, None
                
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False, None

def main():
    print("🚀 DIAGNOSTIC ZACHARY CV PARSING")
    print("=" * 50)
    
    # 1. Test santé service
    if not test_service_health():
        print("\n❌ Service CV Parser inaccessible - Arrêt du diagnostic")
        return
    
    # 2. Test propriétés fichier
    if not test_file_properties():
        print("\n❌ Problème avec le fichier Zachary.pdf - Arrêt du diagnostic")
        return
    
    # 3. Test parsing simple
    success, result = test_cv_parsing_simple()
    if success:
        print("\n✅ DIAGNOSTIC: Le parsing fonctionne parfaitement!")
        print("💡 Le problème était dans votre script Python original")
        print("\n📋 DONNÉES EXTRAITES:")
        
        data = result.get('data', {})
        personal_info = data.get('personal_info', {})
        
        print(f"   👤 Nom: {personal_info.get('name', 'Non détecté')}")
        print(f"   📧 Email: {personal_info.get('email', 'Non détecté')}")
        print(f"   📱 Téléphone: {personal_info.get('phone', 'Non détecté')}")
        
        exp = data.get('professional_experience', [])
        print(f"   💼 Expériences: {len(exp)}")
        
        tech_skills = data.get('technical_skills', [])
        soft_skills = data.get('soft_skills', [])
        print(f"   🔧 Compétences techniques: {tech_skills}")
        print(f"   🤝 Compétences soft: {soft_skills}")
        
        print("\n🎯 PROCHAINE ÉTAPE:")
        print("   Utilisez: python3 test_zachary_test_fpf_fixed_v2.py")
        
        return
    
    print("\n🔧 RECOMMANDATIONS:")
    print("1. Redémarrer le service CV Parser:")
    print("   cd cv-parser-v2 && python app.py")
    print("2. Vérifier les logs du service pour erreurs")
    print("3. Tester avec un autre fichier PDF")

if __name__ == "__main__":
    main()
