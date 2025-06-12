#!/usr/bin/env python3
"""
🔧 Test direct CV Parser - Script de diagnostic simple
Utilise exactement la même méthode que curl qui fonctionne
"""

import requests
from pathlib import Path

def test_cv_parsing_direct(file_path: str):
    """Test parsing CV avec la méthode qui fonctionne (comme curl)"""
    print(f"🔍 Test parsing direct: {file_path}")
    
    try:
        file_path_obj = Path(file_path).expanduser()
        
        if not file_path_obj.exists():
            print(f"❌ Fichier non trouvé: {file_path_obj}")
            return None
        
        print(f"📏 Taille: {file_path_obj.stat().st_size} bytes")
        print(f"📋 Format: {file_path_obj.suffix}")
        
        # Utiliser exactement la même méthode que curl
        with open(file_path_obj, 'rb') as f:
            response = requests.post(
                "http://localhost:5051/api/parse-cv/",  # Endpoint exact
                files={'file': f},
                data={'force_refresh': 'true'},
                timeout=30
            )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.ok:
            try:
                data = response.json()
                
                # Analyser les résultats
                status = data.get('status')
                cv_data = data.get('data', {})
                metadata = cv_data.get('_metadata', {})
                
                print(f"✅ Status: {status}")
                print(f"📝 Texte extrait: {metadata.get('text_length', 0)} caractères")
                print(f"🔧 Parser version: {metadata.get('parser_version', 'unknown')}")
                
                # Info détaillées
                personal_info = cv_data.get('personal_info', {})
                experience = cv_data.get('professional_experience', [])
                skills = cv_data.get('skills', [])
                
                print(f"👤 Nom: {personal_info.get('name', 'Non trouvé')}")
                print(f"💼 Expériences: {len(experience)}")
                print(f"🛠️ Compétences: {len(skills)}")
                
                if experience:
                    print(f"🎯 Missions première exp: {len(experience[0].get('missions', []))}")
                
                return data
                
            except Exception as e:
                print(f"❌ Erreur parsing JSON: {e}")
                print(f"📄 Réponse brute: {response.text[:200]}...")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📄 Erreur: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def main():
    print("🔍 TEST DIRECT CV PARSER - Méthode curl")
    print("=" * 50)
    
    # Tester les fichiers problématiques
    files_to_test = [
        "/Users/baptistecomas/Desktop/BATU Sam.pdf",
        "/Users/baptistecomas/Desktop/CV TEST/Bcom HR - Candidature de Sam.pdf", 
        "/Users/baptistecomas/Desktop/CV TEST/SALVAT Hugo_CV.pdf"
    ]
    
    for file_path in files_to_test:
        print(f"\n{'='*60}")
        result = test_cv_parsing_direct(file_path)
        
        if result:
            print("✅ Parsing réussi")
        else:
            print("❌ Parsing échoué")

if __name__ == "__main__":
    main()
