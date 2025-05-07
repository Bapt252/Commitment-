#!/usr/bin/env python3
"""
Script simple pour tester le parsing de fiches de poste via le service CV parser.
Ce script est une solution temporaire en attendant que le service job-parser soit opérationnel.

Usage:
    python simple-job-parser.py /chemin/vers/fichier.pdf
"""

import os
import sys
import requests
import json
from datetime import datetime

def parse_job_file(file_path):
    """Parse une fiche de poste en utilisant le service CV parser"""
    print(f"Analyse du fichier: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas")
        return None
    
    # URL du service CV parser (qui fonctionne)
    url = "http://localhost:5051/api/parse-cv/"
    
    # Création du formulaire multipart avec le fichier
    files = {'file': open(file_path, 'rb')}
    data = {'force_refresh': 'true'}
    
    print("Envoi de la requête au service CV parser...")
    try:
        # Envoyer la requête
        response = requests.post(url, files=files, data=data, timeout=120)
        
        # Vérifier le code de statut
        if response.status_code == 200:
            result = response.json()
            print("\n--- Résultat du parsing ---")
            
            # Extraction des données
            data = result.get('data', {})
            
            # Afficher les informations principales
            if data:
                display_extracted_info(data)
                
                # Sauvegarder le résultat dans un fichier
                save_to_file(result, file_path)
            
            return result
        else:
            print(f"Erreur: Le service a retourné le code {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print("Erreur: Impossible de se connecter au service CV parser")
        print("Vérifiez que le service est bien démarré sur le port 5051")
        return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def display_extracted_info(data):
    """Affiche les informations extraites de manière structurée"""
    # Informations personnelles
    print(f"Nom: {data.get('name', 'Non détecté')}")
    if 'email' in data:
        print(f"Email: {data.get('email')}")
    if 'phone' in data:
        print(f"Téléphone: {data.get('phone')}")
    
    # Compétences
    skills = data.get('skills', [])
    if skills:
        print("\nCompétences détectées:")
        for skill in skills[:10]:  # Limiter pour la lisibilité
            print(f"- {skill}")
        if len(skills) > 10:
            print(f"... et {len(skills) - 10} autres compétences")
    
    # Expériences
    experiences = data.get('experience', [])
    if experiences:
        print("\nExpériences professionnelles:")
        for exp in experiences[:3]:  # Limiter pour la lisibilité
            company = exp.get('company', 'Entreprise inconnue')
            title = exp.get('title', 'Poste inconnu')
            print(f"- {title} chez {company}")
        if len(experiences) > 3:
            print(f"... et {len(experiences) - 3} autres expériences")

def save_to_file(result, original_file_path):
    """Sauvegarde le résultat dans un fichier JSON"""
    # Créer un nom de fichier basé sur le fichier original
    filename = os.path.basename(original_file_path)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = f"parsing-result-{timestamp}-{filename}.json"
    
    # Sauvegarder le résultat
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"\nRésultat complet sauvegardé dans: {output_file}")

if __name__ == "__main__":
    # Vérifier si un fichier est passé en argument
    if len(sys.argv) < 2:
        print("Usage: python simple-job-parser.py /chemin/vers/fichier.pdf")
        sys.exit(1)
    
    file_path = sys.argv[1]
    parse_job_file(file_path)
