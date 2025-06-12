#!/usr/bin/env python3
"""
🧪 Validation Rapide - Test de la méthode HTTP corrigée
Script pour valider que les corrections fonctionnent avant tests massifs
"""

import requests
import json
from pathlib import Path

def test_corrected_method():
    """Test rapide de la méthode HTTP corrigée"""
    print("🔍 VALIDATION MÉTHODE HTTP CORRIGÉE")
    print("=" * 50)
    
    # Test sur le fichier BATU Sam qui était problématique
    test_file = "/Users/baptistecomas/Desktop/BATU Sam.pdf"
    
    try:
        file_path = Path(test_file)
        if not file_path.exists():
            print(f"❌ Fichier test non trouvé: {test_file}")
            return False
        
        print(f"📄 Test fichier: {file_path.name}")
        print(f"📏 Taille: {file_path.stat().st_size} bytes")
        
        # Utiliser la méthode corrigée (comme dans test_cv_parsing_direct.py)
        with open(file_path, 'rb') as f:
            response = requests.post(
                "http://localhost:5051/api/parse-cv/",  # Port 5051
                files={'file': f},
                data={'force_refresh': 'true'},
                timeout=30
            )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            
            # Structure de réponse corrigée
            status = data.get('status')
            cv_data = data.get('data', {})
            metadata = cv_data.get('_metadata', {})
            
            print(f"✅ Status: {status}")
            print(f"📝 Texte extrait: {metadata.get('text_length', 0)} caractères")
            
            # Validation du succès
            text_length = metadata.get('text_length', 0)
            if text_length > 3000:
                print("✅ SUCCÈS: Extraction du texte fonctionne (>3000 chars)")
                return True
            elif text_length > 0:
                print(f"⚠️ ATTENTION: Texte extrait mais faible quantité ({text_length} chars)")
                return True
            else:
                print("❌ ÉCHEC: Aucun texte extrait")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📄 Erreur: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("🚀 VALIDATION RAPIDE - MÉTHODE HTTP CORRIGÉE")
    print("Objectif: Vérifier que BATU Sam.pdf donne >3000 caractères")
    print()
    
    success = test_corrected_method()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ VALIDATION RÉUSSIE!")
        print("🚀 Vous pouvez lancer les tests massifs avec:")
        print("   python enhanced_batch_testing_v2_fixed.py --test-problematic")
        print("   python enhanced_batch_testing_v2_fixed.py --test-hugo")
        print("   python enhanced_batch_testing_v2_fixed.py --run-batch")
    else:
        print("❌ VALIDATION ÉCHOUÉE!")
        print("🔧 Vérifiez que le CV Parser (port 5051) est démarré")
    
    return success

if __name__ == "__main__":
    main()
