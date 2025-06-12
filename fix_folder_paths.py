#!/usr/bin/env python3
"""
🔧 Script de correction des chemins de dossiers
Corrige les espaces en fin de nom pour CV TEST et FDP TEST
"""

import os
import shutil
from pathlib import Path

def fix_folder_names():
    """Corrige les noms de dossiers avec espaces en fin"""
    
    desktop = Path("~/Desktop").expanduser()
    
    # Dossiers à corriger
    folders_to_fix = [
        ("CV TEST ", "CV TEST"),
        ("FDP TEST ", "FDP TEST")
    ]
    
    print("🔧 CORRECTION DES NOMS DE DOSSIERS")
    print("="*40)
    
    for old_name, new_name in folders_to_fix:
        old_path = desktop / old_name
        new_path = desktop / new_name
        
        print(f"📁 Vérification: {old_name}")
        
        if old_path.exists():
            print(f"   ✅ Trouvé: {old_path}")
            
            if new_path.exists():
                print(f"   ⚠️  Le dossier {new_name} existe déjà")
                print(f"   🔄 Fusion des contenus...")
                
                # Déplacer tous les fichiers
                for item in old_path.iterdir():
                    target = new_path / item.name
                    if target.exists():
                        print(f"      ⚠️  Fichier existe déjà: {item.name}")
                    else:
                        shutil.move(str(item), str(target))
                        print(f"      ✅ Déplacé: {item.name}")
                
                # Supprimer l'ancien dossier vide
                old_path.rmdir()
                print(f"   ✅ Ancien dossier supprimé: {old_name}")
            else:
                # Renommer simplement
                old_path.rename(new_path)
                print(f"   ✅ Renommé: {old_name} → {new_name}")
        else:
            print(f"   ❌ Non trouvé: {old_name}")
            
            # Vérifier si le nom correct existe déjà
            if new_path.exists():
                print(f"   ✅ Le dossier {new_name} existe déjà (correct)")
            else:
                print(f"   ❌ Aucun dossier {new_name} trouvé")
    
    print("\n🎯 VÉRIFICATION FINALE:")
    cv_path = desktop / "CV TEST"
    fdp_path = desktop / "FDP TEST"
    
    if cv_path.exists():
        cv_count = len([f for f in cv_path.iterdir() if f.is_file()])
        print(f"   ✅ CV TEST: {cv_count} fichiers")
    else:
        print(f"   ❌ CV TEST: Non trouvé")
    
    if fdp_path.exists():
        fdp_count = len([f for f in fdp_path.iterdir() if f.is_file()])
        print(f"   ✅ FDP TEST: {fdp_count} fichiers")
    else:
        print(f"   ❌ FDP TEST: Non trouvé")

if __name__ == "__main__":
    fix_folder_names()
