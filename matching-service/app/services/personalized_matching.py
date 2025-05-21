"""
Adaptateur pour le service de matching qui intègre la personnalisation.

Ce module étend les fonctionnalités du service de matching en y ajoutant
la personnalisation des résultats pour chaque utilisateur.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

from app.core.matching import calculate_match, get_matches_for_job, get_matches_for_candidate
from app.utils.personalization_client import get_personalization_client

# Configuration du logger
logger = logging.getLogger(__name__)

def calculate_personalized_match(conn, candidate_id: int, job_id: int, 
                                user_id: str, algorithm_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Calcule un score de matching personnalisé entre un candidat et une offre d'emploi.
    
    Args:
        conn: Connexion à la base de données
        candidate_id: ID du candidat
        job_id: ID de l'offre d'emploi
        user_id: ID de l'utilisateur pour la personnalisation
        algorithm_id: ID de l'algorithme à utiliser (optionnel)
        
    Returns:
        Résultat du matching personnalisé
    """
    # Obtenir les poids de base d'abord
    default_result = calculate_match(conn, candidate_id, job_id, algorithm_id)
    
    # Extraire les poids par défaut des critères
    default_weights = {}
    if 'breakdown' in default_result and isinstance(default_result['breakdown'], dict):
        for key, value in default_result['breakdown'].items():
            if isinstance(value, dict) and 'weight' in value:
                default_weights[key] = value['weight']
    
    # Utiliser les poids de base si aucun poids n'a été extrait
    if not default_weights:
        default_weights = {
            "skills": 0.4,
            "experience": 0.3,
            "education": 0.2,
            "certifications": 0.1
        }
    
    # Obtenir des poids personnalisés
    personalization_client = get_personalization_client()
    personalized_weights = personalization_client.get_personalized_weights(
        user_id=user_id,
        job_id=job_id,
        candidate_id=candidate_id,
        original_weights=default_weights
    )
    
    # Log pour le débogage
    logger.debug(f"Poids par défaut: {default_weights}")
    logger.debug(f"Poids personnalisés: {personalized_weights}")
    
    # Maintenant, nous devons recalculer le score avec les poids personnalisés
    # Pour cela, nous allons utiliser la fonction interne de matching mais avec des poids personnalisés
    
    # Si les poids n'ont pas changé, retourner simplement le résultat par défaut
    if personalized_weights == default_weights:
        logger.debug("Poids identiques, aucune personnalisation nécessaire")
        return default_result
    
    # Sinon, recalculer le score avec les poids personnalisés
    # Nous pouvons soit appeler une procédure stockée spécifique, soit le faire ici
    # Pour cet exemple, nous allons simplement ajuster le score final
    
    # Recalcul simplifié du score global (dans une vraie application, ce serait plus sophistiqué)
    original_breakdown = default_result.get('breakdown', {})
    
    # Initialisation du nouveau breakdown
    new_breakdown = {}
    total_weighted_score = 0.0
    total_weight = 0.0
    
    # Calculer le nouveau score pour chaque critère avec les poids personnalisés
    for criterion, details in original_breakdown.items():
        if criterion in personalized_weights:
            new_weight = personalized_weights[criterion]
            
            # Copier les détails et mettre à jour le poids
            new_details = details.copy() if isinstance(details, dict) else {"score": details, "weight": 0}
            original_weight = new_details.get('weight', 0)
            new_details['weight'] = new_weight
            
            # Si nous avons un score pour ce critère
            if 'score' in new_details:
                score = new_details['score']
                weighted_score = score * new_weight
                total_weighted_score += weighted_score
                total_weight += new_weight
                new_details['weighted_score'] = weighted_score
                
            new_breakdown[criterion] = new_details
    
    # Calculer le nouveau score global
    new_score = total_weighted_score / total_weight if total_weight > 0 else 0
    
    # Créer le résultat personnalisé
    personalized_result = default_result.copy()
    personalized_result['score'] = new_score
    personalized_result['breakdown'] = new_breakdown
    personalized_result['personalized'] = True
    
    return personalized_result

def get_personalized_matches_for_job(conn, job_id: int, user_id: str, 
                                    algorithm_id: Optional[int] = None, 
                                    limit: int = 50) -> List[Dict[str, Any]]:
    """
    Récupère les meilleurs candidats pour une offre d'emploi avec personnalisation.
    
    Args:
        conn: Connexion à la base de données
        job_id: ID de l'offre d'emploi
        user_id: ID de l'utilisateur pour la personnalisation
        algorithm_id: ID de l'algorithme à utiliser (optionnel)
        limit: Nombre maximal de résultats
        
    Returns:
        Liste des candidats correspondants, triés par score personnalisé
    """
    # Obtenir les matches de base
    basic_matches = get_matches_for_job(conn, job_id, algorithm_id, limit)
    
    # Si aucun résultat, retourner une liste vide
    if not basic_matches:
        return []
    
    # Personnaliser les résultats
    personalization_client = get_personalization_client()
    personalized_matches = personalization_client.personalize_results(
        user_id=user_id,
        results=basic_matches
    )
    
    # Enregistrer le feedback pour améliorer les recommandations futures
    # (impression des résultats)
    feedback_data = {
        "job_id": job_id,
        "action": "view_candidates",
        "context": {
            "source": "job_page",
            "results_count": len(personalized_matches)
        }
    }
    personalization_client.record_feedback(user_id, feedback_data)
    
    return personalized_matches

def get_personalized_matches_for_candidate(conn, candidate_id: int, user_id: str, 
                                         algorithm_id: Optional[int] = None, 
                                         limit: int = 50) -> List[Dict[str, Any]]:
    """
    Récupère les meilleures offres d'emploi pour un candidat avec personnalisation.
    
    Args:
        conn: Connexion à la base de données
        candidate_id: ID du candidat
        user_id: ID de l'utilisateur pour la personnalisation
        algorithm_id: ID de l'algorithme à utiliser (optionnel)
        limit: Nombre maximal de résultats
        
    Returns:
        Liste des offres correspondantes, triées par score personnalisé
    """
    # Obtenir les matches de base
    basic_matches = get_matches_for_candidate(conn, candidate_id, algorithm_id, limit)
    
    # Si aucun résultat, retourner une liste vide
    if not basic_matches:
        return []
    
    # Personnaliser les résultats
    personalization_client = get_personalization_client()
    personalized_matches = personalization_client.personalize_results(
        user_id=user_id,
        results=basic_matches
    )
    
    # Enregistrer le feedback pour améliorer les recommandations futures
    # (impression des résultats)
    feedback_data = {
        "candidate_id": candidate_id,
        "action": "view_jobs",
        "context": {
            "source": "candidate_page",
            "results_count": len(personalized_matches)
        }
    }
    personalization_client.record_feedback(user_id, feedback_data)
    
    return personalized_matches

def record_match_interaction(user_id: str, job_id: Optional[int] = None, 
                           candidate_id: Optional[int] = None, 
                           action: str = "view", 
                           context: Optional[Dict[str, Any]] = None) -> bool:
    """
    Enregistre une interaction avec un match pour améliorer la personnalisation.
    
    Args:
        user_id: ID de l'utilisateur
        job_id: ID de l'offre d'emploi (optionnel)
        candidate_id: ID du candidat (optionnel)
        action: Type d'action (view, like, dislike, etc.)
        context: Contexte de l'interaction (optionnel)
        
    Returns:
        True si l'interaction a été enregistrée avec succès, False sinon
    """
    # Vérifie que nous avons au moins un job_id ou un candidate_id
    if not job_id and not candidate_id:
        logger.error("Au moins job_id ou candidate_id doit être fourni")
        return False
    
    # Prépare les données de feedback
    feedback_data = {
        "action": action
    }
    
    if job_id:
        feedback_data["job_id"] = job_id
    
    if candidate_id:
        feedback_data["candidate_id"] = candidate_id
    
    if context:
        feedback_data["context"] = context
    
    # Enregistre le feedback
    personalization_client = get_personalization_client()
    return personalization_client.record_feedback(user_id, feedback_data)
