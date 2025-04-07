"""
Module pour le moteur de matching amélioré qui intègre les données des questionnaires.
Ce moteur combine l'algorithme original basé sur les compétences/expérience avec
le nouvel algorithme basé sur le questionnaire pour de meilleurs résultats.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging
import json

# Importer les modules existants et nouveaux
from app.ml.matching_engine import (
    generate_matches as generate_original_matches,
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
    identify_strengths,
    identify_gaps,
    generate_recommendations
)
from app.ml.questionnaire_matcher import (
    evaluate_questionnaire_match,
    integrate_questionnaire_data
)
from app.ml.questionnaire_parser import (
    extract_questionnaire_data_from_form
)

# Configurer le logging
logger = logging.getLogger(__name__)

async def generate_enhanced_matches(
    job_post_id: int, 
    candidate_ids: List[int], 
    min_score: float = 0.0,
    job_questionnaire: Optional[Dict[str, Any]] = None,
    candidate_questionnaires: Optional[Dict[int, Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Génère des matchings améliorés en combinant l'algorithme original avec les données des questionnaires.
    
    Args:
        job_post_id: ID de la fiche de poste
        candidate_ids: Liste des IDs des candidats
        min_score: Score minimum pour retenir un matching
        job_questionnaire: Données du questionnaire de l'entreprise (facultatif)
        candidate_questionnaires: Dictionnaire des questionnaires des candidats (facultatif)
        
    Returns:
        Liste des résultats de matching enrichis
    """
    try:
        # Générer les matchings avec l'algorithme original
        original_results = await generate_original_matches(job_post_id, candidate_ids, 0.0)  # Aucun filtre min_score
        
        # Si aucun questionnaire n'est fourni, retourner les résultats originaux
        if job_questionnaire is None and (candidate_questionnaires is None or not candidate_questionnaires):
            logger.info("Aucune donnée de questionnaire fournie, utilisation de l'algorithme de matching standard")
            return [result for result in original_results if result["overall_score"] >= min_score]
        
        # Enrichir les résultats avec les données des questionnaires
        enhanced_results = []
        
        for original_result in original_results:
            candidate_id = original_result["candidate_id"]
            
            # Récupérer les questionnaires
            candidate_questionnaire = None
            if candidate_questionnaires and candidate_id in candidate_questionnaires:
                candidate_questionnaire = candidate_questionnaires[candidate_id]
            
            # Si les deux questionnaires sont disponibles, intégrer les résultats
            if job_questionnaire and candidate_questionnaire:
                # Évaluer le matching basé sur le questionnaire
                questionnaire_result = evaluate_questionnaire_match(
                    candidate_questionnaire,
                    job_questionnaire
                )
                
                # Intégrer les résultats
                enhanced_result = integrate_questionnaire_data(
                    original_result,
                    questionnaire_result
                )
                
                # Vérifier le score minimum
                if enhanced_result["overall_score"] >= min_score:
                    enhanced_results.append(enhanced_result)
            else:
                # Si les questionnaires ne sont pas disponibles, utiliser le résultat original
                if original_result["overall_score"] >= min_score:
                    enhanced_results.append(original_result)
        
        logger.info(f"Matching amélioré générés pour la fiche de poste {job_post_id} et {len(enhanced_results)} candidats")
        return enhanced_results
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération des matchings améliorés: {str(e)}")
        # En cas d'erreur, essayer de retourner les résultats originaux
        try:
            original_results = await generate_original_matches(job_post_id, candidate_ids, min_score)
            return original_results
        except:
            # Si tout échoue, retourner une liste vide
            return []

async def process_questionnaire_and_match(
    job_post_id: int,
    candidate_ids: List[int],
    job_form_data: Dict[str, Any],
    candidate_form_data: Dict[int, Dict[str, Any]],
    min_score: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Traite les données de formulaire des questionnaires et génère des matchings.
    
    Args:
        job_post_id: ID de la fiche de poste
        candidate_ids: Liste des IDs des candidats
        job_form_data: Données brutes du formulaire de l'entreprise
        candidate_form_data: Dictionnaire des données de formulaire des candidats
        min_score: Score minimum pour retenir un matching
        
    Returns:
        Liste des résultats de matching enrichis
    """
    try:
        # Extraire les données structurées des questionnaires
        job_questionnaire = extract_questionnaire_data_from_form(job_form_data, is_company=True)
        
        candidate_questionnaires = {}
        for candidate_id, form_data in candidate_form_data.items():
            candidate_questionnaires[candidate_id] = extract_questionnaire_data_from_form(
                form_data, 
                is_company=False
            )
        
        # Générer les matchings améliorés
        return await generate_enhanced_matches(
            job_post_id,
            candidate_ids,
            min_score,
            job_questionnaire,
            candidate_questionnaires
        )
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement des questionnaires: {str(e)}")
        # En cas d'erreur, utiliser l'algorithme original
        return await generate_original_matches(job_post_id, candidate_ids, min_score)

def get_questionnaire_compatibility_summary(
    job_questionnaire: Dict[str, Any],
    candidate_questionnaire: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Génère un résumé de la compatibilité basée sur les questionnaires.
    Utile pour l'affichage détaillé des résultats.
    
    Args:
        job_questionnaire: Données du questionnaire de l'entreprise
        candidate_questionnaire: Données du questionnaire du candidat
        
    Returns:
        Dictionnaire avec le résumé de compatibilité
    """
    try:
        # Évaluer le matching basé sur les questionnaires
        match_result = evaluate_questionnaire_match(
            candidate_questionnaire,
            job_questionnaire
        )
        
        # Extraire des détails supplémentaires pour l'affichage
        category_details = []
        for category, score in match_result["category_scores"].items():
            detail = {
                "category": category.replace("_", " ").title(),
                "score": score,
                "description": get_category_description(category, score)
            }
            category_details.append(detail)
        
        # Construire le résumé
        summary = {
            "overall_score": match_result["overall_score"],
            "category_details": category_details,
            "key_alignments": get_key_alignments(job_questionnaire, candidate_questionnaire),
            "potential_challenges": get_potential_challenges(job_questionnaire, candidate_questionnaire),
            "success_factors": get_success_factors(match_result)
        }
        
        return summary
    
    except Exception as e:
        logger.error(f"Erreur lors de la génération du résumé de compatibilité: {str(e)}")
        # Retourner un résumé minimal
        return {
            "overall_score": 0.5,
            "category_details": [
                {"category": "Compatibilité générale", "score": 0.5, "description": "Compatibilité moyenne"}
            ],
            "key_alignments": ["Données insuffisantes pour l'analyse détaillée"],
            "potential_challenges": ["Données insuffisantes pour l'analyse détaillée"],
            "success_factors": ["Données insuffisantes pour l'analyse détaillée"]
        }

def get_category_description(category: str, score: float) -> str:
    """
    Génère une description textuelle pour une catégorie et un score donnés.
    
    Args:
        category: Nom de la catégorie
        score: Score obtenu
        
    Returns:
        Description textuelle
    """
    if category == "work_environment":
        if score >= 0.8:
            return "Excellente compatibilité avec l'environnement de travail proposé"
        elif score >= 0.6:
            return "Bonne compatibilité avec l'environnement de travail"
        elif score >= 0.4:
            return "Compatibilité moyenne avec l'environnement de travail"
        else:
            return "Potentiel désalignement avec l'environnement de travail"
    
    elif category == "work_style":
        if score >= 0.8:
            return "Très bon alignement avec le style de travail de l'équipe"
        elif score >= 0.6:
            return "Style de travail généralement compatible"
        elif score >= 0.4:
            return "Adaptations nécessaires dans le style de travail"
        else:
            return "Style de travail potentiellement incompatible"
    
    elif category == "values_culture":
        if score >= 0.8:
            return "Forte résonance avec les valeurs et la culture de l'entreprise"
        elif score >= 0.6:
            return "Bonnes correspondances de valeurs et culture"
        elif score >= 0.4:
            return "Certaines valeurs communes, d'autres divergentes"
        else:
            return "Potentiel désalignement des valeurs fondamentales"
    
    elif category == "career_goals":
        if score >= 0.8:
            return "Excellente correspondance avec les opportunités de carrière"
        elif score >= 0.6:
            return "Bonne adéquation avec les perspectives d'évolution"
        elif score >= 0.4:
            return "Certaines aspirations de carrière pourront être satisfaites"
        else:
            return "Écart significatif entre les aspirations et les opportunités"
    
    elif category == "technical_skills":
        if score >= 0.8:
            return "Profil technique très bien adapté aux besoins du poste"
        elif score >= 0.6:
            return "Bonnes compétences techniques pour le poste"
        elif score >= 0.4:
            return "Compétences techniques partiellement adaptées"
        else:
            return "Écart significatif dans les compétences techniques"
    
    # Description par défaut
    if score >= 0.8:
        return "Excellente compatibilité"
    elif score >= 0.6:
        return "Bonne compatibilité"
    elif score >= 0.4:
        return "Compatibilité moyenne"
    else:
        return "Compatibilité faible"

def get_key_alignments(
    job_questionnaire: Dict[str, Any],
    candidate_questionnaire: Dict[str, Any]
) -> List[str]:
    """
    Identifie les principaux points d'alignement entre le candidat et l'entreprise.
    
    Args:
        job_questionnaire: Données du questionnaire de l'entreprise
        candidate_questionnaire: Données du questionnaire du candidat
        
    Returns:
        Liste des points d'alignement clés
    """
    alignments = []
    
    # Environnement de travail
    if ("environment_preference" in candidate_questionnaire and 
        "environment_offered" in job_questionnaire and
        candidate_questionnaire["environment_preference"] == job_questionnaire["environment_offered"]):
        alignments.append(f"Environnement de travail : {candidate_questionnaire['environment_preference']}")
    
    # Mode de travail
    if ("work_mode_preference" in candidate_questionnaire and 
        "work_mode_offered" in job_questionnaire and
        candidate_questionnaire["work_mode_preference"] == job_questionnaire["work_mode_offered"]):
        alignments.append(f"Mode de travail : {candidate_questionnaire['work_mode_preference']}")
    
    # Valeurs communes
    if ("values_important" in candidate_questionnaire and 
        "company_values" in job_questionnaire):
        common_values = set(candidate_questionnaire["values_important"]) & set(job_questionnaire["company_values"])
        if common_values:
            alignments.append(f"Valeurs communes : {', '.join(common_values)}")
    
    # Si pas assez d'alignements spécifiques
    if len(alignments) < 2:
        alignments.append("Potentiel d'intégration positive dans l'équipe")
    
    return alignments

def get_potential_challenges(
    job_questionnaire: Dict[str, Any],
    candidate_questionnaire: Dict[str, Any]
) -> List[str]:
    """
    Identifie les défis potentiels de l'intégration du candidat.
    
    Args:
        job_questionnaire: Données du questionnaire de l'entreprise
        candidate_questionnaire: Données du questionnaire du candidat
        
    Returns:
        Liste des défis potentiels
    """
    challenges = []
    
    # Environnement de travail
    if ("environment_preference" in candidate_questionnaire and 
        "environment_offered" in job_questionnaire and
        candidate_questionnaire["environment_preference"] != job_questionnaire["environment_offered"]):
        challenges.append(
            f"Adaptation à l'environnement : préférence pour {candidate_questionnaire['environment_preference']} " +
            f"vs {job_questionnaire['environment_offered']} proposé"
        )
    
    # Mode de travail
    if ("work_mode_preference" in candidate_questionnaire and 
        "work_mode_offered" in job_questionnaire and
        candidate_questionnaire["work_mode_preference"] != job_questionnaire["work_mode_offered"]):
        challenges.append(
            f"Mode de travail : préférence pour {candidate_questionnaire['work_mode_preference']} " +
            f"vs {job_questionnaire['work_mode_offered']} proposé"
        )
    
    # Si pas de défis spécifiques
    if not challenges:
        challenges.append("Aucun défi majeur identifié")
    
    return challenges

def get_success_factors(match_result: Dict[str, Any]) -> List[str]:
    """
    Identifie les facteurs clés de succès pour l'intégration du candidat.
    
    Args:
        match_result: Résultat du matching par questionnaire
        
    Returns:
        Liste des facteurs de succès
    """
    factors = []
    
    # Identifier les catégories fortes
    strong_categories = []
    for category, score in match_result["category_scores"].items():
        if score >= 0.7:
            if category == "work_environment":
                strong_categories.append("environnement de travail")
            elif category == "work_style":
                strong_categories.append("style de travail")
            elif category == "values_culture":
                strong_categories.append("culture d'entreprise")
            elif category == "career_goals":
                strong_categories.append("objectifs de carrière")
    
    if strong_categories:
        factors.append(f"Fort alignement sur: {', '.join(strong_categories)}")
    
    # Ajouter des recommandations générales
    factors.append("Communication claire des attentes et objectifs")
    factors.append("Rencontres régulières de suivi pendant la période d'intégration")
    
    return factors
