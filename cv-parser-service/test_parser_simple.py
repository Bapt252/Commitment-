#!/usr/bin/env python3
"""
Script de test simple pour le parser CV
Ce script permet de tester facilement le service de parsing de CV en envoyant
un fichier directement à l'API locale du service.
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path

def parse_cv(file_path, port=5051):
    """
    Envoie un CV à l'API locale du parser et affiche le résultat.
    
    Args:
        file_path (str): Chemin vers le fichier CV à analyser (PDF ou DOCX)
        port (int): Port sur lequel le service de parsing est exposé
    
    Returns:
        dict: Le résultat du parsing ou None en cas d'erreur
    """
    # Vérifier que le fichier existe
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        return None
    
    # Vérifier l'extension du fichier
    file_extension = Path(file_path).suffix.lower()
    if file_extension not in ['.pdf', '.docx']:
        print(f"Erreur: Le format de fichier {file_extension} n'est pas supporté. Utilisez PDF ou DOCX.")
        return None
    
    # Préparer la requête
    url = f"http://localhost:{port}/api/v1/parse"
    
    try:
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file, 'application/octet-stream')}
            
            print(f"Envoi du fichier {file_path} à {url}...")
            response = requests.post(url, files=files)
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"Erreur: La requête a échoué avec le code {response.status_code}")
                print(f"Détails: {response.text}")
                return None
                
    except Exception as e:
        print(f"Erreur lors de l'envoi du fichier: {str(e)}")
        return None

def pretty_print_result(result):
    """Affiche le résultat du parsing de manière lisible."""
    if not result:
        return
    
    print("\n=== RÉSULTATS DU PARSING ===\n")
    
    # Informations personnelles
    if 'personal_info' in result:
        info = result['personal_info']
        print("INFORMATIONS PERSONNELLES:")
        print(f"  Nom: {info.get('name', 'Non détecté')}")
        print(f"  Email: {info.get('email', 'Non détecté')}")
        print(f"  Téléphone: {info.get('phone', 'Non détecté')}")
        print(f"  Localisation: {info.get('location', 'Non détectée')}")
        print()
    
    # Compétences
    if 'skills' in result and result['skills']:
        print("COMPÉTENCES:")
        for skill in result['skills']:
            print(f"  - {skill}")
        print()
    
    # Expériences professionnelles
    if 'work_experience' in result and result['work_experience']:
        print("EXPÉRIENCES PROFESSIONNELLES:")
        for job in result['work_experience']:
            print(f"  • {job.get('title', 'Poste non spécifié')} chez {job.get('company', 'Entreprise non spécifiée')}")
            dates = f"{job.get('start_date', '?')} - {job.get('end_date', 'Présent')}"
            print(f"    {dates}")
            if 'description' in job and job['description']:
                print(f"    {job['description'][:100]}...")
            print()
    
    # Formation
    if 'education' in result and result['education']:
        print("FORMATION:")
        for edu in result['education']:
            print(f"  • {edu.get('degree', 'Diplôme non spécifié')} - {edu.get('institution', 'Institution non spécifiée')}")
            dates = f"{edu.get('start_date', '?')} - {edu.get('end_date', 'Présent')}"
            print(f"    {dates}")
            print()
    
    # Langues
    if 'languages' in result and result['languages']:
        print("LANGUES:")
        for lang in result['languages']:
            print(f"  - {lang.get('language', 'Non spécifiée')}: {lang.get('level', 'Niveau non spécifié')}")
        print()
    
    # Données brutes (optionnel)
    print("\nPour voir les données brutes complètes, utilisez l'option --raw")

def main():
    parser = argparse.ArgumentParser(description='Test du service de parsing de CV')
    parser.add_argument('file', help='Chemin vers le fichier CV à analyser (PDF ou DOCX)')
    parser.add_argument('--port', type=int, default=5051, help='Port sur lequel le service est exposé (défaut: 5051)')
    parser.add_argument('--raw', action='store_true', help='Afficher les données brutes complètes')
    parser.add_argument('--output', help='Enregistrer les résultats dans un fichier JSON')
    
    args = parser.parse_args()
    
    result = parse_cv(args.file, args.port)
    
    if result:
        if args.raw:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            pretty_print_result(result)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nLes résultats ont été enregistrés dans {args.output}")
        
        print("\nParsing CV terminé avec succès!")
        return 0
    else:
        print("\nLe parsing du CV a échoué.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
