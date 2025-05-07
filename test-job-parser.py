#!/usr/bin/env python3
"""
Script utilitaire pour tester le parsing de fiches de poste (job descriptions).
Utilise temporairement le service CV parser comme alternative au job-parser.

Usage:
    python test-job-parser.py /chemin/vers/fichier.pdf
    
Ce script envoie une fiche de poste au service CV parser et affiche le résultat
sous forme structurée. Il peut être utilisé comme solution temporaire en 
attendant que le service job-parser soit complètement opérationnel.
"""

import os
import sys
import requests
import json
import argparse
import time
from datetime import datetime


def parse_job_file(file_path, use_cv_parser=True, output_file=None, verbose=False):
    """
    Analyse une fiche de poste en utilisant l'un des services de parsing.
    
    Args:
        file_path (str): Chemin vers le fichier à analyser
        use_cv_parser (bool): Si True, utilise le service CV parser (port 5051)
                             Si False, tente d'utiliser le service job-parser (port 5053)
        output_file (str): Chemin du fichier où sauvegarder le résultat (optionnel)
        verbose (bool): Affiche des informations supplémentaires pendant le traitement
    
    Returns:
        dict: Résultat du parsing ou None en cas d'erreur
    """
    if verbose:
        print(f"Analyse du fichier: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas")
        return None
    
    # Déterminer l'URL du service à utiliser
    service_name = "CV parser" if use_cv_parser else "job-parser"
    port = "5051" if use_cv_parser else "5053"
    endpoint = "/api/parse-cv/" if use_cv_parser else "/api/parse-job"
    url = f"http://localhost:{port}{endpoint}"
    
    # Création du formulaire multipart avec le fichier
    with open(file_path, 'rb') as f:
        file_content = f.read()
        file_size = len(file_content)
    
    if verbose:
        print(f"Taille du fichier: {file_size / 1024:.2f} KB")
        print(f"Utilisation du service: {service_name} ({url})")
    
    # Création de la requête
    files = {'file': open(file_path, 'rb')}
    data = {'force_refresh': 'true'}
    
    print(f"Envoi de la requête au service {service_name}...")
    start_time = time.time()
    
    try:
        # Envoyer la requête
        response = requests.post(url, files=files, data=data, timeout=120)  # 2 minutes timeout
        
        # Calculer le temps de traitement
        processing_time = time.time() - start_time
        
        # Vérifier le code de statut
        if response.status_code == 200:
            result = response.json()
            print(f"Parsing réussi en {processing_time:.2f} secondes")
            
            # Affichage du résultat
            print("\n--- Informations extraites ---")
            
            # Extraction des données principales selon le service utilisé
            if use_cv_parser:
                # Pour le service CV parser
                parsed_data = result.get('data', {})
                display_cv_result(parsed_data)
            else:
                # Pour le service job-parser
                parsed_data = result.get('data', {})
                display_job_result(parsed_data)
            
            # Sauvegarde dans un fichier si demandé
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\nRésultat sauvegardé dans: {output_file}")
            
            return result
        else:
            print(f"Erreur: Le service a retourné le code {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.ConnectionError:
        print(f"Erreur de connexion: Impossible de se connecter au service {service_name}")
        print(f"Vérifiez que le service est bien démarré sur le port {port}")
        if use_cv_parser:
            print("\nVoulez-vous tenter avec le service job-parser à la place? (o/n)")
            choice = input().lower()
            if choice.startswith('o'):
                return parse_job_file(file_path, use_cv_parser=False, output_file=output_file, verbose=verbose)
        return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None


def display_cv_result(data):
    """Affiche les informations extraites d'un CV de manière structurée"""
    print(f"Nom: {data.get('name', 'Non détecté')}")
    print(f"Email: {data.get('email', 'Non détecté')}")
    print(f"Téléphone: {data.get('phone', 'Non détecté')}")
    
    # Compétences
    skills = data.get('skills', [])
    if skills:
        print("\nCompétences:")
        for skill in skills[:10]:  # Limiter pour la lisibilité
            print(f"- {skill}")
        if len(skills) > 10:
            print(f"... et {len(skills) - 10} autres compétences")
    
    # Expériences
    experiences = data.get('experience', [])
    if experiences:
        print("\nExpériences professionnelles:")
        for exp in experiences[:3]:  # Limiter pour la lisibilité
            print(f"- {exp.get('title', 'Poste inconnu')} chez {exp.get('company', 'Entreprise inconnue')}")
        if len(experiences) > 3:
            print(f"... et {len(experiences) - 3} autres expériences")


def display_job_result(data):
    """Affiche les informations extraites d'une fiche de poste de manière structurée"""
    print(f"Titre du poste: {data.get('title', 'Non détecté')}")
    print(f"Entreprise: {data.get('company', 'Non détecté')}")
    print(f"Localisation: {data.get('location', 'Non détecté')}")
    print(f"Type de contrat: {data.get('contract_type', 'Non détecté')}")
    
    # Compétences requises
    required_skills = data.get('required_skills', [])
    if required_skills:
        print("\nCompétences requises:")
        for skill in required_skills:
            print(f"- {skill}")
    
    # Compétences souhaitées
    preferred_skills = data.get('preferred_skills', [])
    if preferred_skills:
        print("\nCompétences souhaitées:")
        for skill in preferred_skills:
            print(f"- {skill}")
    
    # Responsabilités
    responsibilities = data.get('responsibilities', [])
    if responsibilities:
        print("\nResponsabilités:")
        for resp in responsibilities[:5]:  # Limiter pour la lisibilité
            print(f"- {resp}")
        if len(responsibilities) > 5:
            print(f"... et {len(responsibilities) - 5} autres responsabilités")


if __name__ == "__main__":
    # Configurer le parser d'arguments
    parser = argparse.ArgumentParser(description='Tester le parsing de fiches de poste')
    parser.add_argument('file_path', help='Chemin vers le fichier à analyser')
    parser.add_argument('--service', choices=['cv', 'job'], default='cv', 
                        help='Service à utiliser (cv=CV parser, job=job-parser)')
    parser.add_argument('--output', '-o', help='Sauvegarder le résultat dans un fichier')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux')
    
    # Parser les arguments
    args = parser.parse_args()
    
    # Générer un nom de fichier de sortie par défaut si non spécifié
    if not args.output:
        file_name = os.path.basename(args.file_path)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_file = f"parsing-result-{timestamp}-{file_name}.json"
    else:
        output_file = args.output
    
    # Appeler la fonction de parsing
    use_cv_parser = args.service == 'cv'
    parse_job_file(args.file_path, use_cv_parser=use_cv_parser, output_file=output_file, verbose=args.verbose)
