#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Service de matching entre candidats et offres d'emploi

Ce module implémente les algorithmes de matching pour
trouver les meilleures correspondances entre candidats et offres.
"""

import logging
from typing import Dict, List, Any, Optional
import json

# Import du client de personnalisation
from app.services.personalization_client import PersonalizationClient

logger = logging.getLogger(__name__)

async def nexten_matching_process(candidate_id: int, job_id: int, db: Any, openai_client: Any, 
                                user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Processus complet de matching entre un candidat et une offre d'emploi
    
    Args:
        candidate_id: ID du candidat
        job_id: ID de l'offre d'emploi
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        user_id: ID de l'utilisateur demandant le matching (optionnel)
        
    Returns:
        dict: Résultat du matching
    """
    logger.info(f"Début du processus de matching pour candidat={candidate_id}, job={job_id}")
    
    # Récupérer les données du candidat et de l'offre
    candidate_data = await db.get_candidate_data(candidate_id)
    job_data = await db.get_job_data(job_id)
    
    if not candidate_data or not job_data:
        logger.error(f"Données manquantes pour le matching: candidat={candidate_data is not None}, job={job_data is not None}")
        return {
            'candidate_id': candidate_id,
            'job_id': job_id,
            'score': 0.0,
            'category': 'no_match',
            'details': {
                'error': 'Données manquantes pour le matching'
            }
        }
    
    # Définir les poids par défaut pour les différentes catégories
    # (compétences, expérience, éducation, certifications)
    default_weights = {
        'skills': 0.4,
        'experience': 0.3,
        'education': 0.2,
        'certifications': 0.1
    }
    
    # Si un user_id est fourni, personnaliser les poids
    custom_weights = default_weights
    if user_id:
        try:
            # Créer une instance du client de personnalisation
            personalization_client = PersonalizationClient()
            
            # Récupérer les poids personnalisés
            custom_weights = personalization_client.personalize_matching_weights(
                user_id=user_id,
                job_id=job_id,
                candidate_id=candidate_id,
                original_weights=default_weights
            )
            logger.info(f"Poids personnalisés utilisés pour user_id={user_id}: {custom_weights}")
        except Exception as e:
            logger.warning(f"Erreur lors de la personnalisation des poids: {str(e)}", exc_info=True)
            # En cas d'erreur, utiliser les poids par défaut
            custom_weights = default_weights
    
    # Phase 1: Matching basé sur les compétences
    skills_score, skills_details = await match_skills(candidate_data, job_data, openai_client)
    
    # Phase 2: Matching basé sur l'expérience
    experience_score, experience_details = await match_experience(candidate_data, job_data, openai_client)
    
    # Phase 3: Matching basé sur l'éducation
    education_score, education_details = await match_education(candidate_data, job_data, openai_client)
    
    # Phase 4: Matching basé sur les certifications
    certifications_score, certifications_details = await match_certifications(candidate_data, job_data, openai_client)
    
    # Calcul du score final avec les poids personnalisés
    final_score = (
        skills_score * custom_weights['skills'] +
        experience_score * custom_weights['experience'] +
        education_score * custom_weights['education'] +
        certifications_score * custom_weights['certifications']
    )
    
    # Déterminer la catégorie de matching
    if final_score >= 0.8:
        category = 'excellent_match'
    elif final_score >= 0.6:
        category = 'good_match'
    elif final_score >= 0.4:
        category = 'moderate_match'
    elif final_score >= 0.2:
        category = 'weak_match'
    else:
        category = 'no_match'
    
    # Enregistrer le résultat du matching dans la base de données
    matching_result = {
        'candidate_id': candidate_id,
        'job_id': job_id,
        'score': final_score,
        'category': category,
        'details': {
            'skills': {
                'score': skills_score,
                'weight': custom_weights['skills'],
                'details': skills_details
            },
            'experience': {
                'score': experience_score,
                'weight': custom_weights['experience'],
                'details': experience_details
            },
            'education': {
                'score': education_score,
                'weight': custom_weights['education'],
                'details': education_details
            },
            'certifications': {
                'score': certifications_score,
                'weight': custom_weights['certifications'],
                'details': certifications_details
            },
            'weights_personalized': user_id is not None
        }
    }
    
    # Sauvegarder le résultat dans la base de données
    await db.save_matching_result(matching_result)
    
    logger.info(f"Fin du processus de matching pour candidat={candidate_id}, job={job_id}, score={final_score}")
    
    return matching_result

async def match_skills(candidate_data: Dict[str, Any], job_data: Dict[str, Any], openai_client: Any) -> tuple:
    """Fonction de matching des compétences à implémenter"""
    # Implémentation existante
    pass

async def match_experience(candidate_data: Dict[str, Any], job_data: Dict[str, Any], openai_client: Any) -> tuple:
    """Fonction de matching de l'expérience à implémenter"""
    # Implémentation existante
    pass

async def match_education(candidate_data: Dict[str, Any], job_data: Dict[str, Any], openai_client: Any) -> tuple:
    """Fonction de matching de l'éducation à implémenter"""
    # Implémentation existante
    pass

async def match_certifications(candidate_data: Dict[str, Any], job_data: Dict[str, Any], openai_client: Any) -> tuple:
    """Fonction de matching des certifications à implémenter"""
    # Implémentation existante
    pass

async def bulk_matching_process(candidate_id: int, job_ids: List[int], db: Any, openai_client: Any, 
                              min_score: float = 0.3, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Processus de matching entre un candidat et plusieurs offres d'emploi
    
    Args:
        candidate_id: ID du candidat
        job_ids: Liste des IDs d'offres d'emploi
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        min_score: Score minimum pour inclure un match
        user_id: ID de l'utilisateur demandant le matching (optionnel)
        
    Returns:
        list: Liste des résultats de matching triés par score
    """
    logger.info(f"Début du processus de matching en masse pour candidat={candidate_id}, {len(job_ids)} jobs")
    
    results = []
    
    # Traiter chaque offre d'emploi
    for job_id in job_ids:
        try:
            # Exécuter le matching pour cette paire candidat-job
            match_result = await nexten_matching_process(candidate_id, job_id, db, openai_client, user_id)
            
            # Ne garder que les matches avec un score supérieur au minimum
            if match_result['score'] >= min_score:
                results.append(match_result)
                
        except Exception as e:
            logger.error(f"Erreur lors du matching pour candidat={candidate_id}, job={job_id}: {str(e)}", exc_info=True)
    
    # Trier les résultats par score décroissant
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Si un user_id est fourni, personnaliser l'ordre des résultats
    if user_id and results:
        try:
            # Créer une instance du client de personnalisation
            personalization_client = PersonalizationClient()
            
            # Personnaliser les résultats
            results = personalization_client.personalize_job_search(
                user_id=user_id,
                results=results,
                search_query='',
                context={'source': 'bulk_matching', 'candidate_id': candidate_id}
            )
            logger.info(f"Résultats personnalisés pour user_id={user_id}")
        except Exception as e:
            logger.warning(f"Erreur lors de la personnalisation des résultats: {str(e)}", exc_info=True)
    
    logger.info(f"Fin du processus de matching en masse pour candidat={candidate_id}, {len(results)} matchs trouvés")
    
    return results

async def job_candidates_matching_process(job_id: int, candidate_ids: List[int], db: Any, openai_client: Any, 
                                       limit: int = 10, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Processus de matching entre une offre d'emploi et plusieurs candidats
    
    Args:
        job_id: ID de l'offre d'emploi
        candidate_ids: Liste des IDs de candidats
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        limit: Nombre maximum de résultats à retourner
        user_id: ID de l'utilisateur demandant le matching (optionnel)
        
    Returns:
        list: Liste des résultats de matching triés par score
    """
    logger.info(f"Début du processus de matching pour job={job_id}, {len(candidate_ids)} candidats")
    
    results = []
    
    # Traiter chaque candidat
    for candidate_id in candidate_ids:
        try:
            # Exécuter le matching pour cette paire job-candidat
            match_result = await nexten_matching_process(candidate_id, job_id, db, openai_client, user_id)
            
            # Ajouter le résultat à la liste
            results.append(match_result)
                
        except Exception as e:
            logger.error(f"Erreur lors du matching pour job={job_id}, candidat={candidate_id}: {str(e)}", exc_info=True)
    
    # Trier les résultats par score décroissant
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Si un user_id est fourni, personnaliser l'ordre des résultats
    if user_id and results:
        try:
            # Créer une instance du client de personnalisation
            personalization_client = PersonalizationClient()
            
            # Personnaliser les résultats
            results = personalization_client.personalize_job_search(
                user_id=user_id,
                results=results,
                search_query='',
                context={'source': 'job_candidates_matching', 'job_id': job_id}
            )
            logger.info(f"Résultats personnalisés pour user_id={user_id}")
        except Exception as e:
            logger.warning(f"Erreur lors de la personnalisation des résultats: {str(e)}", exc_info=True)
    
    # Limiter le nombre de résultats
    results = results[:limit]
    
    logger.info(f"Fin du processus de matching pour job={job_id}, {len(results)} candidats trouvés")
    
    return results
