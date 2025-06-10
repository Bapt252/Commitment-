#!/usr/bin/env python3
"""
Script pour mettre à jour les fichiers de test avec le format de payload corrigé
Corrige le problème de format location pour SuperSmartMatch V2
"""

import json
import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Crée une sauvegarde du fichier original"""
    backup_path = f"{filepath}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"📁 Backup créé: {backup_path}")
    return backup_path

def fix_location_format(data):
    """Convertit les locations string en format objet"""
    
    def convert_location(location_value):
        """Convertit une location selon son type"""
        if isinstance(location_value, str):
            # Conversion intelligent basée sur le contenu
            if "," in location_value:
                parts = [part.strip() for part in location_value.split(",")]
                if len(parts) == 2:
                    return {
                        "city": parts[0],
                        "country": parts[1]
                    }
                elif len(parts) >= 3:
                    return {
                        "city": parts[0],
                        "region": parts[1], 
                        "country": parts[2]
                    }
            else:
                # Location simple - assumons que c'est une ville en France
                return {
                    "city": location_value,
                    "country": "France"
                }
        elif isinstance(location_value, dict):
            # Déjà au bon format
            return location_value
        else:
            # Fallback
            return {
                "city": str(location_value),
                "country": "France"
            }
    
    # Fixer les locations dans CV
    if "cv" in data:
        cv = data["cv"]
        if "personal_info" in cv and "location" in cv["personal_info"]:
            cv["personal_info"]["location"] = convert_location(cv["personal_info"]["location"])
    
    # Fixer les locations dans offers
    if "offers" in data:
        for offer in data["offers"]:
            if "location" in offer:
                offer["location"] = convert_location(offer["location"])
    
    # Fixer les locations dans job_offers (autre format possible)
    if "job_offers" in data:
        for offer in data["job_offers"]:
            if "location" in offer:
                offer["location"] = convert_location(offer["location"])
    
    return data

def update_test_file(filepath):
    """Met à jour un fichier de test Python"""
    
    print(f"\n🔧 Traitement: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"❌ Fichier non trouvé: {filepath}")
        return False
    
    try:
        # Backup
        backup_path = backup_file(filepath)
        
        # Lire le fichier
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patterns à corriger
        corrections = [
            # Location simple avec guillemets
            ('"location": "Paris"', '"location": {"city": "Paris", "country": "France"}'),
            ('"location": "Lyon"', '"location": {"city": "Lyon", "country": "France"}'),
            ('"location": "Marseille"', '"location": {"city": "Marseille", "country": "France"}'),
            ('"location": "Toulouse"', '"location": {"city": "Toulouse", "country": "France"}'),
            ('"location": "Nice"', '"location": {"city": "Nice", "country": "France"}'),
            ('"location": "Bordeaux"', '"location": {"city": "Bordeaux", "country": "France"}'),
            ('"location": "Lille"', '"location": {"city": "Lille", "country": "France"}'),
            ('"location": "Strasbourg"', '"location": {"city": "Strasbourg", "country": "France"}'),
            ('"location": "Nantes"', '"location": {"city": "Nantes", "country": "France"}'),
            ('"location": "Montpellier"', '"location": {"city": "Montpellier", "country": "France"}'),
            
            # Location avec apostrophes
            ("'location': 'Paris'", "'location': {'city': 'Paris', 'country': 'France'}"),
            ("'location': 'Lyon'", "'location': {'city': 'Lyon', 'country': 'France'}"),
            ("'location': 'Marseille'", "'location': {'city': 'Marseille', 'country': 'France'}"),
            
            # Patterns avec virgule (ville, pays)
            ('"location": "Paris, France"', '"location": {"city": "Paris", "country": "France"}'),
            ('"location": "Lyon, France"', '"location": {"city": "Lyon", "country": "France"}'),
            ('"location": "Berlin, Germany"', '"location": {"city": "Berlin", "country": "Germany"}'),
            ('"location": "London, UK"', '"location": {"city": "London", "country": "UK"}'),
        ]
        
        # Appliquer les corrections
        updated_content = content
        changes_made = 0
        
        for old_pattern, new_pattern in corrections:
            if old_pattern in updated_content:
                updated_content = updated_content.replace(old_pattern, new_pattern)
                changes_made += 1
                print(f"  ✅ Corrigé: {old_pattern}")
        
        # Si pas de changement avec les patterns, chercher les blocs JSON
        if changes_made == 0:
            print("  🔍 Recherche de blocs JSON à corriger...")
            # Cette partie nécessiterait une analyse plus sophistiquée
            # Pour l'instant, on signale que le fichier peut nécessiter une correction manuelle
            print("  ⚠️  Aucun pattern automatique trouvé - correction manuelle peut être nécessaire")
        
        # Sauvegarder le fichier corrigé
        if changes_made > 0:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"  ✅ {changes_made} corrections appliquées")
            return True
        else:
            print("  ℹ️  Aucune correction nécessaire")
            return True
            
    except Exception as e:
        print(f"  ❌ Erreur: {e}")
        return False

def create_corrected_payload_template():
    """Crée un template de payload corrigé"""
    
    template = {
        "cv": {
            "personal_info": {
                "name": "Prénom Nom",
                "email": "email@example.com",
                "phone": "+33123456789",
                "location": {
                    "city": "Paris",
                    "country": "France"
                }
            },
            "skills": ["Python", "FastAPI", "Docker", "PostgreSQL"],
            "experience": [
                {
                    "title": "Développeur Senior",
                    "company": "Entreprise",
                    "duration": "2020-2023",
                    "description": "Description de l'expérience"
                }
            ],
            "education": [
                {
                    "degree": "Master Informatique",
                    "school": "École",
                    "year": "2020"
                }
            ]
        },
        "offers": [
            {
                "title": "Développeur Python Senior",
                "company": "TechCorp",
                "description": "Description du poste...",
                "requirements": ["Python", "FastAPI", "Docker"],
                "salary_range": "50000-70000",
                "contract_type": "CDI",
                "location": {
                    "city": "Paris",
                    "region": "Île-de-France",
                    "country": "France"
                }
            }
        ]
    }
    
    template_file = "payload_template_corrected.json"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"📝 Template créé: {template_file}")
    return template_file

def main():
    """Fonction principale"""
    print("🔧 MISE À JOUR DES FICHIERS DE TEST - SuperSmartMatch V2")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fichiers à traiter
    test_files = [
        "test_real_data_v2.py",
        "debug_supersmartmatch_v2.py",
        "fix_endpoints_v2_improved.py"
    ]
    
    print(f"\n📋 Fichiers à traiter: {len(test_files)}")
    
    results = {}
    
    for filepath in test_files:
        results[filepath] = update_test_file(filepath)
    
    # Créer le template corrigé
    print(f"\n📝 Création du template de payload corrigé...")
    template_file = create_corrected_payload_template()
    
    # Résumé
    print(f"\n" + "=" * 80)
    print("📋 RÉSUMÉ DES CORRECTIONS")
    print("=" * 80)
    
    success_count = sum(1 for success in results.values() if success)
    
    for filepath, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {filepath}")
    
    print(f"\n📊 Résultats: {success_count}/{len(test_files)} fichiers traités avec succès")
    print(f"📝 Template disponible: {template_file}")
    
    print(f"\n💡 Étapes suivantes:")
    print(f"1. Exécuter fix_payload_format_v2.py pour tester les formats")
    print(f"2. Vérifier les fichiers de backup si besoin")
    print(f"3. Utiliser le template pour créer de nouveaux tests")
    print(f"4. Valider que SuperSmartMatch V2 utilise algorithm_used: 'nexten_matcher'")

if __name__ == "__main__":
    main()
