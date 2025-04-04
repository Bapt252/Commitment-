from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import pandas as pd
import numpy as np
import json
import os

# Configurer le logging
logger = logging.getLogger(__name__)

# Chemin vers le fichier de stockage des feedbacks pour l'amélioration continue
FEEDBACK_STORAGE_PATH = os.path.join(os.path.dirname(__file__), '../../data/feedback/')

async def process_feedback(feedback: Dict[str, Any]) -> bool:
    """
    Traite un feedback pour améliorer les modèles ML.
    
    Args:
        feedback (Dict[str, Any]): Le feedback à traiter
        
    Returns:
        bool: True si le traitement a réussi, False sinon
    """
    try:
        # Vérifier que le dossier de stockage existe
        os.makedirs(FEEDBACK_STORAGE_PATH, exist_ok=True)
        
        # Extraire le type d'entité et l'ID
        entity_type = feedback.get("entity_type")
        entity_id = feedback.get("entity_id")
        
        # Stocker le feedback pour utilisation ultérieure dans l'entraînement
        feedback_with_timestamp = feedback.copy()
        feedback_with_timestamp["processed_at"] = datetime.now().isoformat()
        
        # Ajouter le feedback au fichier correspondant
        feedback_file = os.path.join(FEEDBACK_STORAGE_PATH, f"{entity_type}_feedback.jsonl")
        
        with open(feedback_file, "a") as f:
            f.write(json.dumps(feedback_with_timestamp) + "\n")
        
        # Traitement spécifique selon le type d'entité
        if entity_type == "job_parsing":
            await process_job_parsing_feedback(feedback)
        elif entity_type == "matching":
            await process_matching_feedback(feedback)
        elif entity_type == "questionnaire":
            await process_questionnaire_feedback(feedback)
        
        logger.info(f"Feedback traité avec succès: {entity_type} ID {entity_id}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du traitement du feedback: {str(e)}")
        return False

async def process_job_parsing_feedback(feedback: Dict[str, Any]) -> None:
    """
    Traite un feedback sur le parsing de fiche de poste.
    
    Si la note est basse, signale le problème pour revue manuelle.
    Si des aspects spécifiques sont mentionnés, les utilise pour améliorer les règles d'extraction.
    """
    entity_id = feedback.get("entity_id")
    rating = feedback.get("rating", 0)
    aspects = feedback.get("aspects", {})
    comments = feedback.get("comments", "")
    
    # Si la note est basse, signaler pour revue manuelle
    if rating <= 2:
        await flag_for_manual_review(
            "job_parsing", 
            entity_id, 
            f"Note basse: {rating}/5. Commentaires: {comments}"
        )
    
    # Si des aspects spécifiques sont mal notés, les traiter
    for aspect, aspect_rating in aspects.items():
        if aspect_rating <= 2:
            if aspect == "skills":
                await improve_skills_extraction(entity_id, comments)
            elif aspect == "experience":
                await improve_experience_extraction(entity_id, comments)
            elif aspect == "education":
                await improve_education_extraction(entity_id, comments)

async def process_matching_feedback(feedback: Dict[str, Any]) -> None:
    """
    Traite un feedback sur le matching.
    
    Ajuste les poids des différents critères de matching en fonction du feedback.
    """
    entity_id = feedback.get("entity_id")
    rating = feedback.get("rating", 0)
    aspects = feedback.get("aspects", {})
    
    # Ajuster les poids si nécessaire
    if aspects:
        # Charger les poids actuels (simulation)
        current_weights = {
            "skills": 0.5,
            "experience": 0.3,
            "education": 0.2
        }
        
        # Ajuster les poids en fonction du feedback
        # Exemple simple: augmenter légèrement le poids des aspects bien notés
        for aspect, aspect_rating in aspects.items():
            if aspect in current_weights:
                # Ajustement très léger basé sur l'évaluation
                adjustment = (aspect_rating - 3) * 0.01
                current_weights[aspect] += adjustment
        
        # Normaliser les poids pour qu'ils somment à 1
        total = sum(current_weights.values())
        normalized_weights = {k: v/total for k, v in current_weights.items()}
        
        # Sauvegarder les nouveaux poids (simulation)
        await save_updated_matching_weights(normalized_weights)

async def process_questionnaire_feedback(feedback: Dict[str, Any]) -> None:
    """
    Traite un feedback sur le questionnaire.
    
    Améliore l'analyse des réponses aux questionnaires.
    """
    entity_id = feedback.get("entity_id")
    rating = feedback.get("rating", 0)
    comments = feedback.get("comments", "")
    
    # Si la note est basse, signaler pour revue manuelle
    if rating <= 2:
        await flag_for_manual_review(
            "questionnaire", 
            entity_id, 
            f"Note basse: {rating}/5. Commentaires: {comments}"
        )

async def flag_for_manual_review(entity_type: str, entity_id: int, reason: str) -> None:
    """
    Signale une entité pour revue manuelle.
    """
    manual_review_file = os.path.join(FEEDBACK_STORAGE_PATH, "manual_review.jsonl")
    
    review_entry = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "reason": reason,
        "flagged_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    with open(manual_review_file, "a") as f:
        f.write(json.dumps(review_entry) + "\n")
    
    logger.info(f"Entité signalée pour revue manuelle: {entity_type} ID {entity_id}")

async def improve_skills_extraction(entity_id: int, comments: str) -> None:
    """
    Améliore l'extraction des compétences basée sur le feedback.
    """
    # Cette fonction pourrait analyser les commentaires pour extraire des indications
    # sur les compétences manquées, puis mettre à jour les règles d'extraction
    logger.info(f"Amélioration de l'extraction des compétences pour l'entité {entity_id}")

async def improve_experience_extraction(entity_id: int, comments: str) -> None:
    """
    Améliore l'extraction de l'expérience basée sur le feedback.
    """
    logger.info(f"Amélioration de l'extraction de l'expérience pour l'entité {entity_id}")

async def improve_education_extraction(entity_id: int, comments: str) -> None:
    """
    Améliore l'extraction de l'éducation basée sur le feedback.
    """
    logger.info(f"Amélioration de l'extraction de l'éducation pour l'entité {entity_id}")

async def save_updated_matching_weights(weights: Dict[str, float]) -> None:
    """
    Sauvegarde les poids mis à jour pour le matching.
    """
    weights_file = os.path.join(FEEDBACK_STORAGE_PATH, "matching_weights.json")
    
    # Dans une implémentation réelle, on pourrait avoir un verrou
    # pour éviter les problèmes de concurrence
    with open(weights_file, "w") as f:
        json.dump({
            "weights": weights,
            "updated_at": datetime.now().isoformat()
        }, f)
    
    logger.info(f"Poids de matching mis à jour: {weights}")
