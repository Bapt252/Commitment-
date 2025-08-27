#!/usr/bin/env python3
"""
Script de test pour l'analyse améliorée de CV
---------------------------------------------

Ce script permet de tester le parsing amélioré des CV, 
notamment pour les détails des expériences professionnelles.

Usage:
    python test_enhanced_parser.py chemin/vers/MonSuperCV.pdf

Options:
    -h, --help          Affiche cette aide
    -v, --verbose       Active le mode verbeux
    -f, --force         Force le rafraîchissement du cache
    -r, --raw           Affiche le JSON brut au lieu du format formaté
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, Optional

# Ajouter le répertoire parent au chemin Python pour importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import corrigé pour les fonctions du service cv_parser
from services.cv_parser import extract_text, parse_cv_with_openai, normalize_date, refine_experiences

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cv_test")

def extract_text_from_file(file_path: str) -> Optional[str]:
    """
    Extraire le texte d'un fichier CV.
    
    Args:
        file_path: Chemin vers le fichier CV
        
    Returns:
        Le texte extrait du CV ou None en cas d'erreur
    """
    try:
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            logger.error(f"Le fichier {file_path} n'existe pas")
            return None
            
        # Obtenir l'extension du fichier
        _, file_extension = os.path.splitext(file_path)
        
        # Vérifier que l'extension est supportée
        if file_extension.lower() not in ['.pdf', '.docx', '.doc']:
            logger.error(f"Format de fichier non supporté: {file_extension}")
            return None
            
        # Extraire le texte
        with open(file_path, 'rb') as f:
            return extract_text(f, file_extension)
    
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
        return None

def analyze_cv(cv_text: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """
    Analyse un CV avec le modèle amélioré.
    
    Args:
        cv_text: Texte du CV
        verbose: Afficher les détails d'exécution
        
    Returns:
        Dictionnaire avec les informations extraites ou None en cas d'erreur
    """
    try:
        if verbose:
            logger.info("Analyse du CV avec le modèle GPT-4o-mini")
            
        # Afficher un extrait du texte en mode verbeux
        if verbose:
            excerpt = cv_text[:500] + "..." if len(cv_text) > 500 else cv_text
            logger.info(f"Extrait du texte CV:\n{excerpt}")
            
        # Appeler l'API d'extraction améliorée
        cv_data = parse_cv_with_openai(cv_text)
            
        # Normaliser les dates des expériences pour être sûr
        if "experiences" in cv_data and cv_data["experiences"]:
            for exp in cv_data["experiences"]:
                if "date_debut" in exp:
                    exp["date_debut"] = normalize_date(exp["date_debut"])
                if "date_fin" in exp and exp["date_fin"].lower() != "present":
                    exp["date_fin"] = normalize_date(exp["date_fin"])
                    
        return cv_data
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du CV: {str(e)}")
        return None

def format_experience(exp: Dict[str, Any]) -> str:
    """
    Formater une expérience professionnelle pour l'affichage console.
    
    Args:
        exp: Dictionnaire représentant une expérience
        
    Returns:
        Chaîne formatée pour l'affichage
    """
    result = []
    
    # Informations principales
    title_line = f"{exp.get('titre', '')} - {exp.get('entreprise', '')}"
    if exp.get('lieu'):
        title_line += f" ({exp.get('lieu')})"
    result.append(title_line)
    
    # Dates
    date_line = f"{exp.get('date_debut', '')} → {exp.get('date_fin', 'Present')}"
    if exp.get('type_contrat'):
        date_line += f" | {exp.get('type_contrat')}"
    result.append(date_line)
    
    # Description
    if exp.get('description'):
        result.append(f"Description: {exp.get('description')}")
        
    # Responsabilités
    if exp.get('responsabilites'):
        result.append("\nResponsabilités:")
        for resp in exp.get('responsabilites', []):
            result.append(f"  • {resp}")
            
    # Réalisations
    if exp.get('realisations'):
        result.append("\nRéalisations:")
        for real in exp.get('realisations', []):
            result.append(f"  • {real}")
            
    # Technologies
    if exp.get('technologies'):
        result.append("\nTechnologies: " + ", ".join(exp.get('technologies', [])))
        
    # Taille d'équipe
    if exp.get('taille_equipe'):
        result.append(f"Taille d'équipe: {exp.get('taille_equipe')}")
        
    return "\n".join(result)

def main():
    """Fonction principale."""
    # Parser les arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Test du parsing amélioré de CV")
    parser.add_argument("file_path", help="Chemin vers le fichier CV à analyser")
    parser.add_argument("-v", "--verbose", action="store_true", help="Mode verbeux")
    parser.add_argument("-f", "--force", action="store_true", help="Forcer le rafraîchissement du cache")
    parser.add_argument("-r", "--raw", action="store_true", help="Afficher le JSON brut")
    args = parser.parse_args()
    
    # Configurer le niveau de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Extraire le texte du CV
    logger.info(f"Extraction du texte de {args.file_path}")
    cv_text = extract_text_from_file(args.file_path)
    
    if not cv_text:
        logger.error("Échec de l'extraction du texte. Arrêt du programme.")
        sys.exit(1)
        
    logger.info(f"Texte extrait avec succès ({len(cv_text)} caractères)")
    
    # Analyser le CV
    cv_data = analyze_cv(cv_text, args.verbose)
    
    if not cv_data:
        logger.error("Échec de l'analyse du CV. Arrêt du programme.")
        sys.exit(1)
        
    # Préparer le chemin pour le fichier de sortie
    output_path = os.path.splitext(args.file_path)[0] + "_parsed.json"
    
    # Enregistrer les résultats dans un fichier JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(cv_data, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Résultats enregistrés dans {output_path}")
    
    # Afficher les résultats
    if args.raw:
        # Afficher le JSON brut
        print(json.dumps(cv_data, ensure_ascii=False, indent=2))
    else:
        # Afficher les informations principales
        print("\n" + "="*80)
        print(f"RÉSULTATS DU PARSING DE CV: {os.path.basename(args.file_path)}")
        print("="*80)
        
        print(f"\nNom: {cv_data.get('prenom', '')} {cv_data.get('nom', '')}")
        print(f"Poste: {cv_data.get('poste', '')}")
        print(f"Contact: {cv_data.get('email', '')} | {cv_data.get('telephone', '')}")
        print(f"Adresse: {cv_data.get('adresse', '')}")
        
        # Compétences
        print("\nCOMPÉTENCES:")
        print(f"Techniques: {', '.join(cv_data.get('competences', []))}")
        print(f"Logiciels: {', '.join(cv_data.get('logiciels', []))}")
        print(f"Soft Skills: {', '.join(cv_data.get('soft_skills', []))}")
        
        # Expériences
        print("\nEXPÉRIENCES PROFESSIONNELLES:")
        if not cv_data.get('experiences'):
            print("  Aucune expérience n'a été extraite")
        else:
            for i, exp in enumerate(cv_data.get('experiences', []), 1):
                print(f"\n--- Expérience {i} ---")
                print(format_experience(exp))
                print("-"*40)
        
        # Formation
        print("\nFORMATION:")
        if not cv_data.get('formation'):
            print("  Aucune formation n'a été extraite")
        else:
            for edu in cv_data.get('formation', []):
                print(f"• {edu.get('diplome', '')} - {edu.get('etablissement', '')}")
                print(f"  {edu.get('date_debut', '')} → {edu.get('date_fin', '')}")
                if edu.get('description'):
                    print(f"  {edu.get('description')}")
                print()
        
        print("\n" + "="*80)
        print(f"Pour plus de détails, consultez le fichier: {output_path}")
        print("="*80 + "\n")

if __name__ == "__main__":
    main()
