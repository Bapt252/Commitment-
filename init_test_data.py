#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script d'initialisation pour le système de matching candidat-emploi

Ce script initialise les données de test et lance un matching pour créer 
des résultats pré-calculés, ce qui permet aux utilisateurs de tester le système 
sans avoir à attendre que l'API soit lancée.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Tenter d'importer le moteur de matching
try:
    from matching_engine import match_candidate_with_jobs
    MATCHING_ENGINE_AVAILABLE = True
    logger.info("Moteur de matching disponible")
except ImportError:
    MATCHING_ENGINE_AVAILABLE = False
    logger.warning("Moteur de matching non disponible, les résultats seront simulés")

def load_json_file(file_path: str) -> Any:
    """
    Charge un fichier JSON
    
    Args:
        file_path: Chemin vers le fichier JSON
        
    Returns:
        Données chargées depuis le fichier JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Erreur lors du chargement du fichier {file_path}: {str(e)}")
        return None

def save_json_file(file_path: str, data: Any) -> bool:
    """
    Sauvegarde des données au format JSON
    
    Args:
        file_path: Chemin où sauvegarder le fichier
        data: Données à sauvegarder
        
    Returns:
        True si la sauvegarde a réussi, False sinon
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier {file_path}: {str(e)}")
        return False

def generate_mock_matching_scores(candidate_data: Dict[str, Any], jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Génère des scores de matching simulés pour les tests
    
    Args:
        candidate_data: Données du candidat
        jobs_data: Liste des offres d'emploi
        
    Returns:
        Liste des offres avec des scores de matching simulés
    """
    import random
    
    # Récupérer les compétences du candidat
    candidate_skills = set(s.lower() for s in candidate_data["cv_data"].get("competences", []))
    
    # Résultats avec scores simulés
    results = []
    
    for job in jobs_data:
        job_copy = job.copy()
        
        # Calculer un score basé sur l'intersection des compétences
        job_skills = set(s.lower() for s in job.get("competences", []))
        skill_overlap = len(candidate_skills.intersection(job_skills))
        
        # Score de base entre 50 et 95%
        base_score = random.randint(50, 95)
        
        # Bonus pour les compétences communes
        skill_bonus = min(30, skill_overlap * 5)
        
        # Score total (max 98%)
        total_score = min(98, base_score + skill_bonus)
        
        # Ajouter le score
        job_copy["matching_score"] = total_score
        
        # Détails des critères
        job_copy["matching_details"] = {
            "skills": random.randint(70, 100) if skill_overlap > 0 else random.randint(30, 60),
            "contract": random.randint(80, 100) if job["type_contrat"] in ["CDI", "CDD"] else random.randint(40, 70),
            "location": random.randint(70, 95),  # Simulation du temps de trajet
            "date": random.randint(80, 100),     # Simulation disponibilité
            "salary": random.randint(70, 95),    # Simulation salaire
            "experience": random.randint(75, 95) # Simulation expérience
        }
        
        results.append(job_copy)
    
    # Trier par score décroissant
    results.sort(key=lambda x: x["matching_score"], reverse=True)
    
    return results

def main():
    """
    Fonction principale d'initialisation
    """
    # Récupérer les chemins des fichiers
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    candidate_path = os.path.join(current_dir, "test-data", "candidate.json")
    jobs_path = os.path.join(current_dir, "jobs_data.json")
    results_path = os.path.join(current_dir, "static", "js", "matching_results.json")
    
    # Créer le répertoire static/js si nécessaire
    os.makedirs(os.path.join(current_dir, "static", "js"), exist_ok=True)
    
    # Charger les données
    candidate_data = load_json_file(candidate_path)
    jobs_data = load_json_file(jobs_path)
    
    if not candidate_data or not jobs_data:
        logger.error("Impossible de charger les données nécessaires")
        return 1
    
    # Calculer les scores de matching
    if MATCHING_ENGINE_AVAILABLE:
        logger.info("Calcul des scores de matching avec le moteur...")
        matching_results = match_candidate_with_jobs(
            candidate_data["cv_data"],
            candidate_data["questionnaire_data"],
            jobs_data,
            limit=10
        )
    else:
        logger.info("Génération de scores de matching simulés...")
        matching_results = generate_mock_matching_scores(candidate_data, jobs_data)
    
    # Sauvegarder les résultats
    if save_json_file(results_path, matching_results):
        logger.info(f"Résultats de matching sauvegardés dans {results_path}")
    else:
        logger.error("Erreur lors de la sauvegarde des résultats")
        return 1
    
    # Créer un fichier localStorage_init.js pour initialiser localStorage
    localStorage_init_path = os.path.join(current_dir, "static", "js", "localStorage_init.js")
    
    try:
        with open(localStorage_init_path, 'w', encoding='utf-8') as f:
            f.write("""// Script d'initialisation du localStorage pour le mode démo
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initialisation des données de démo dans localStorage...');
    
    // Email du candidat de démo
    localStorage.setItem('user_email', 'demo.utilisateur@nexten.fr');
    
    // Adresse du candidat pour le calcul des temps de trajet
    localStorage.setItem('candidate_address', '123 Rue de Paris, 75015 Paris');
    
    // Vérifier si les résultats de matching sont déjà chargés
    if (!localStorage.getItem('matching_jobs')) {
        // Charger les résultats pré-calculés si disponibles
        fetch('../static/js/matching_results.json')
            .then(response => response.json())
            .then(data => {
                localStorage.setItem('matching_jobs', JSON.stringify(data));
                console.log('Données de matching chargées dans localStorage');
            })
            .catch(error => {
                console.error('Erreur lors du chargement des données de matching:', error);
            });
    }
});""")
        
        logger.info(f"Script d'initialisation localStorage créé: {localStorage_init_path}")
    except Exception as e:
        logger.error(f"Erreur lors de la création du script d'initialisation localStorage: {str(e)}")
        return 1
    
    logger.info("Initialisation des données de test terminée avec succès")
    return 0

if __name__ == "__main__":
    sys.exit(main())
