"""
Tâches pour le matching bidirectionnel
--------------------------------------
Tâches RQ pour exécuter l'algorithme de matching bidirectionnel.

Auteur: Claude/Anthropic
Date: 14/05/2025
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from rq import get_current_job
from app.algorithms.nexten_bidirectional_matcher import NextenBidirectionalMatcher
from app.core.notification import send_webhook_notification

logger = logging.getLogger(__name__)

async def bidirectional_matching_single_task(
    candidate_id: int, 
    job_id: int, 
    with_commute_time: bool,
    db: Any, 
    openai_client: Any
) -> Dict[str, Any]:
    """
    Tâche RQ pour calculer le matching bidirectionnel entre un candidat et une offre d'emploi
    
    Args:
        candidate_id: ID du candidat
        job_id: ID de l'offre d'emploi
        with_commute_time: Calculer le temps de trajet entre le candidat et l'entreprise
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        
    Returns:
        Résultat du matching
    """
    job = get_current_job()
    
    try:
        logger.info(f"Début du calcul de matching bidirectionnel pour candidat={candidate_id}, job={job_id}")
        
        # Récupération des données
        candidate_record = await db.get_candidate(candidate_id)
        job_record = await db.get_job(job_id)
        
        # Obtenir les données des questionnaires
        candidate_questionnaire = await db.get_candidate_questionnaire(candidate_id)
        company_questionnaire = await db.get_job_questionnaire(job_id)
        
        # Construire les structures de données complètes
        candidate_data = {
            'id': candidate_id,
            'cv': candidate_record.get('cv_parsed_data', {}),
            'questionnaire': candidate_questionnaire
        }
        
        job_data = {
            'id': job_id,
            'description': job_record,
            'questionnaire': company_questionnaire
        }
        
        # Initialiser l'algorithme de matching bidirectionnel
        matcher = NextenBidirectionalMatcher()
        
        # Calcul du matching
        result = await matcher.calculate_match(candidate_data, job_data)
        
        # Sauvegarder le résultat dans la base de données
        match_id = await db.save_bidirectional_matching_result(candidate_id, job_id, result)
        
        # Enrichir le résultat avec des informations supplémentaires
        enriched_result = {
            **result,
            'match_id': match_id,
            'candidate': {
                'id': candidate_id,
                'name': candidate_record.get('name', ''),
                'job_title': candidate_record.get('job_title', '')
            },
            'job': {
                'id': job_id,
                'title': job_record.get('title', ''),
                'company': job_record.get('company', ''),
                'location': job_record.get('location', '')
            }
        }
        
        # Mettre à jour les métadonnées du job
        if job:
            job.meta['status'] = 'completed'
            job.meta['score'] = result['score']
            job.meta['category'] = result['category']
            job.save_meta()
        
        # Envoyer une notification webhook si configurée
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            notification_data = {
                'job_id': job.id if job else None,
                'status': 'completed',
                'candidate_id': candidate_id,
                'job_id': job_id,
                'score': result['score'],
                'category': result['category'],
                'timestamp': datetime.now().isoformat()
            }
            await send_webhook_notification(webhook_url, notification_data)
        
        logger.info(f"Fin du calcul de matching bidirectionnel pour candidat={candidate_id}, job={job_id}, score={result['score']}")
        
        return enriched_result
    
    except Exception as e:
        logger.error(f"Erreur lors du calcul de matching bidirectionnel: {str(e)}", exc_info=True)
        
        # Mettre à jour les métadonnées du job en cas d'erreur
        if job:
            job.meta['status'] = 'failed'
            job.meta['error'] = str(e)
            job.save_meta()
        
        # Envoyer une notification webhook en cas d'erreur
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            notification_data = {
                'job_id': job.id if job else None,
                'status': 'failed',
                'candidate_id': candidate_id,
                'job_id': job_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            await send_webhook_notification(webhook_url, notification_data)
        
        # Relancer l'exception pour que la tâche soit marquée comme échouée
        raise

async def find_jobs_for_candidate_task(
    candidate_id: int, 
    limit: int, 
    min_score: float,
    with_commute_time: bool,
    db: Any, 
    openai_client: Any
) -> Dict[str, Any]:
    """
    Tâche RQ pour trouver les meilleures offres d'emploi pour un candidat
    
    Args:
        candidate_id: ID du candidat
        limit: Nombre maximum de résultats à retourner
        min_score: Score minimum pour inclure un match
        with_commute_time: Calculer le temps de trajet
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        
    Returns:
        Liste des offres d'emploi correspondantes
    """
    job = get_current_job()
    
    try:
        logger.info(f"Début de la recherche d'offres pour le candidat {candidate_id}")
        
        # Récupération des données du candidat
        candidate_record = await db.get_candidate(candidate_id)
        candidate_questionnaire = await db.get_candidate_questionnaire(candidate_id)
        
        # Construction de la structure de données du candidat
        candidate_data = {
            'id': candidate_id,
            'cv': candidate_record.get('cv_parsed_data', {}),
            'questionnaire': candidate_questionnaire
        }
        
        # Récupération de toutes les offres d'emploi actives
        jobs_data = await db.get_active_jobs()
        
        # Préparation des structures de données pour les offres
        job_list = []
        for job_record in jobs_data:
            job_id = job_record.get('id')
            company_questionnaire = await db.get_job_questionnaire(job_id)
            
            job_data = {
                'id': job_id,
                'description': job_record,
                'questionnaire': company_questionnaire
            }
            
            job_list.append(job_data)
        
        # Initialiser l'algorithme de matching bidirectionnel
        matcher = NextenBidirectionalMatcher()
        
        # Trouver les meilleures offres pour le candidat
        matches = await matcher.find_jobs_for_candidate(
            candidate_data, job_list, limit, min_score
        )
        
        # Enrichir les résultats
        enriched_matches = []
        for match in matches:
            job_data = match['job']
            job_id = job_data['id']
            
            # Sauvegarder le résultat dans la base de données
            match_id = await db.save_bidirectional_matching_result(
                candidate_id, job_id, {
                    'score': match['score'],
                    'category': match['category'],
                    'details': match['details'],
                    'insights': match['insights']
                }
            )
            
            # Ajouter des informations de base
            enriched_match = {
                'match_id': match_id,
                'job': {
                    'id': job_id,
                    'title': job_data['description'].get('title', ''),
                    'company': job_data['description'].get('company', ''),
                    'location': job_data['description'].get('location', '')
                },
                'score': match['score'],
                'category': match['category'],
                'details': match['details'],
                'insights': match['insights']
            }
            
            enriched_matches.append(enriched_match)
        
        # Résultat final
        result = {
            'count': len(enriched_matches),
            'results': enriched_matches,
            'timestamp': datetime.now().isoformat(),
            'query_parameters': {
                'candidate_id': candidate_id,
                'limit': limit,
                'min_score': min_score,
                'with_commute_time': with_commute_time
            }
        }
        
        # Mettre à jour les métadonnées du job
        if job:
            job.meta['status'] = 'completed'
            job.meta['count'] = len(enriched_matches)
            job.save_meta()
        
        # Envoyer une notification webhook si configurée
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            notification_data = {
                'job_id': job.id if job else None,
                'status': 'completed',
                'candidate_id': candidate_id,
                'count': len(enriched_matches),
                'timestamp': datetime.now().isoformat()
            }
            await send_webhook_notification(webhook_url, notification_data)
        
        logger.info(f"Fin de la recherche d'offres pour le candidat {candidate_id}, {len(enriched_matches)} résultats trouvés")
        
        return result
    
    except Exception as e:
        logger.error(f"Erreur lors de la recherche d'offres pour le candidat {candidate_id}: {str(e)}", exc_info=True)
        
        # Mettre à jour les métadonnées du job en cas d'erreur
        if job:
            job.meta['status'] = 'failed'
            job.meta['error'] = str(e)
            job.save_meta()
        
        # Envoyer une notification webhook en cas d'erreur
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            notification_data = {
                'job_id': job.id if job else None,
                'status': 'failed',
                'candidate_id': candidate_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            await send_webhook_notification(webhook_url, notification_data)
        
        # Relancer l'exception pour que la tâche soit marquée comme échouée
        raise

async def find_candidates_for_job_task(
    job_id: int, 
    limit: int, 
    min_score: float,
    with_commute_time: bool,
    db: Any, 
    openai_client: Any
) -> Dict[str, Any]:
    """
    Tâche RQ pour trouver les meilleurs candidats pour une offre d'emploi
    
    Args:
        job_id: ID de l'offre d'emploi
        limit: Nombre maximum de résultats à retourner
        min_score: Score minimum pour inclure un match
        with_commute_time: Calculer le temps de trajet
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        
    Returns:
        Liste des candidats correspondants
    """
    job = get_current_job()
    
    try:
        logger.info(f"Début de la recherche de candidats pour l'offre {job_id}")
        
        # Récupération des données de l'offre
        job_record = await db.get_job(job_id)
        company_questionnaire = await db.get_job_questionnaire(job_id)
        
        # Construction de la structure de données de l'offre
        job_data = {
            'id': job_id,
            'description': job_record,
            'questionnaire': company_questionnaire
        }
        
        # Récupération de tous les candidats actifs
        candidates_data = await db.get_active_candidates()
        
        # Préparation des structures de données pour les candidats
        candidate_list = []
        for candidate_record in candidates_data:
            candidate_id = candidate_record.get('id')
            candidate_questionnaire = await db.get_candidate_questionnaire(candidate_id)
            
            candidate_data = {
                'id': candidate_id,
                'cv': candidate_record.get('cv_parsed_data', {}),
                'questionnaire': candidate_questionnaire
            }
            
            candidate_list.append(candidate_data)
        
        # Initialiser l'algorithme de matching bidirectionnel
        matcher = NextenBidirectionalMatcher()
        
        # Trouver les meilleurs candidats pour l'offre
        matches = await matcher.find_candidates_for_job(
            job_data, candidate_list, limit, min_score
        )
        
        # Enrichir les résultats
        enriched_matches = []
        for match in matches:
            candidate_data = match['candidate']
            candidate_id = candidate_data['id']
            
            # Sauvegarder le résultat dans la base de données
            match_id = await db.save_bidirectional_matching_result(
                candidate_id, job_id, {
                    'score': match['score'],
                    'category': match['category'],
                    'details': match['details'],
                    'insights': match['insights']
                }
            )
            
            # Ajouter des informations de base
            candidate_record = await db.get_candidate(candidate_id)
            
            enriched_match = {
                'match_id': match_id,
                'candidate': {
                    'id': candidate_id,
                    'name': candidate_record.get('name', ''),
                    'job_title': candidate_record.get('job_title', '')
                },
                'score': match['score'],
                'category': match['category'],
                'details': match['details'],
                'insights': match['insights']
            }
            
            enriched_matches.append(enriched_match)
        
        # Résultat final
        result = {
            'count': len(enriched_matches),
            'results': enriched_matches,
            'timestamp': datetime.now().isoformat(),
            'query_parameters': {
                'job_id': job_id,
                'limit': limit,
                'min_score': min_score,
                'with_commute_time': with_commute_time
            }
        }
        
        # Mettre à jour les métadonnées du job
        if job:
            job.meta['status'] = 'completed'
            job.meta['count'] = len(enriched_matches)
            job.save_meta()
        
        # Envoyer une notification webhook si configurée
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            notification_data = {
                'job_id': job.id if job else None,
                'status': 'completed',
                'offre_id': job_id,
                'count': len(enriched_matches),
                'timestamp': datetime.now().isoformat()
            }
            await send_webhook_notification(webhook_url, notification_data)
        
        logger.info(f"Fin de la recherche de candidats pour l'offre {job_id}, {len(enriched_matches)} résultats trouvés")
        
        return result
    
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de candidats pour l'offre {job_id}: {str(e)}", exc_info=True)
        
        # Mettre à jour les métadonnées du job en cas d'erreur
        if job:
            job.meta['status'] = 'failed'
            job.meta['error'] = str(e)
            job.save_meta()
        
        # Envoyer une notification webhook en cas d'erreur
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            notification_data = {
                'job_id': job.id if job else None,
                'status': 'failed',
                'offre_id': job_id,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            await send_webhook_notification(webhook_url, notification_data)
        
        # Relancer l'exception pour que la tâche soit marquée comme échouée
        raise
