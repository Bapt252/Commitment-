
"""
Nexten Matching Tasks
--------------------
Tâches asynchrones de matching pour l'algorithme Nexten

Auteur: Claude/Anthropic
Date: 24/04/2025
"""

import logging
import json
from typing import Dict, List, Any, Optional, Union

from rq import get_current_job
from app.services.matching_service import nexten_matching_process, bulk_matching_process, job_candidates_matching_process
from app.core.notification import send_webhook_notification

# Configuration du logger
logger = logging.getLogger(__name__)

async def calculate_matching_score_task(candidate_id: int, job_id: int, db: Any, openai_client: Any, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Tâche RQ pour calculer le score de matching entre un candidat et une offre
    
    Args:
        candidate_id: ID du candidat
        job_id: ID de l'offre d'emploi
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        user_id: ID de l'utilisateur demandant le matching (pour personnalisation)
        
    Returns:
        dict: Résultat du matching
    """
    job = get_current_job()
    
    try:
        logger.info(f"Début du calcul de matching pour candidat={candidate_id}, job={job_id}")
        
        # Processus complet avec les 3 phases
        result = await nexten_matching_process(candidate_id, job_id, db, openai_client, user_id)
        
        # Mise à jour des métadonnées du job
        if job:
            job.meta['status'] = 'completed'
            job.meta['score'] = result['score']
            job.meta['category'] = result['category']
            job.save_meta()
        
        # Notification webhook si configurée
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            await send_webhook_notification(webhook_url, {
                'job_id': job.id if job else None,
                'status': 'completed',
                'candidate_id': candidate_id,
                'job_id': job_id,
                'score': result['score'],
                'category': result['category']
            })
        
        logger.info(f"Fin du calcul de matching pour candidat={candidate_id}, job={job_id}, score={result['score']}")
        
        return result
    
    except Exception as e:
        logger.error(f"Erreur lors du calcul de matching: {str(e)}", exc_info=True)
        
        # Mise à jour des métadonnées du job en cas d'erreur
        if job:
            job.meta['status'] = 'failed'
            job.meta['error'] = str(e)
            job.save_meta()
        
        # Notification webhook en cas d'erreur
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            await send_webhook_notification(webhook_url, {
                'job_id': job.id if job else None,
                'status': 'failed',
                'candidate_id': candidate_id,
                'job_id': job_id,
                'error': str(e)
            })
        
        # Relancer l'exception pour que la tâche soit marquée comme échouée
        raise

async def calculate_bulk_matching_task(candidate_id: int, job_ids: List[int], db: Any, openai_client: Any, min_score: float = 0.3, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tâche RQ pour calculer le matching entre un candidat et plusieurs offres
    
    Args:
        candidate_id: ID du candidat
        job_ids: Liste des IDs d'offres d'emploi
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        min_score: Score minimum pour inclure un match
        user_id: ID de l'utilisateur demandant le matching (pour personnalisation)
        
    Returns:
        list: Liste des résultats de matching triés par score
    """
    job = get_current_job()
    
    try:
        logger.info(f"Début du calcul de matching en masse pour candidat={candidate_id}, {len(job_ids)} jobs")
        
        # Processus de matching en masse
        results = await bulk_matching_process(candidate_id, job_ids, db, openai_client, min_score, user_id)
        
        # Mise à jour des métadonnées du job
        if job:
            job.meta['status'] = 'completed'
            job.meta['matches_count'] = len(results)
            job.save_meta()
        
        # Notification webhook si configurée
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            await send_webhook_notification(webhook_url, {
                'job_id': job.id if job else None,
                'status': 'completed',
                'candidate_id': candidate_id,
                'matches_count': len(results),
                'top_match': results[0] if results else None
            })
        
        logger.info(f"Fin du calcul de matching en masse pour candidat={candidate_id}, {len(results)} matchs trouvés")
        
        return results
    
    except Exception as e:
        logger.error(f"Erreur lors du calcul de matching en masse: {str(e)}", exc_info=True)
        
        # Mise à jour des métadonnées du job en cas d'erreur
        if job:
            job.meta['status'] = 'failed'
            job.meta['error'] = str(e)
            job.save_meta()
        
        # Notification webhook en cas d'erreur
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            await send_webhook_notification(webhook_url, {
                'job_id': job.id if job else None,
                'status': 'failed',
                'candidate_id': candidate_id,
                'error': str(e)
            })
        
        # Relancer l'exception pour que la tâche soit marquée comme échouée
        raise

async def find_candidates_for_job_task(job_id: int, candidate_ids: List[int], db: Any, openai_client: Any, limit: int = 10, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Tâche RQ pour trouver les meilleurs candidats pour une offre d'emploi
    
    Args:
        job_id: ID de l'offre d'emploi
        candidate_ids: Liste des IDs de candidats à évaluer
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        limit: Nombre maximum de résultats à retourner
        user_id: ID de l'utilisateur demandant le matching (pour personnalisation)
        
    Returns:
        list: Liste des candidats correspondants triés par score
    """
    job = get_current_job()
    
    try:
        logger.info(f"Début de la recherche de candidats pour job={job_id}, {len(candidate_ids)} candidats")
        
        # Processus de matching pour trouver les meilleurs candidats
        results = await job_candidates_matching_process(job_id, candidate_ids, db, openai_client, limit, user_id)
        
        # Mise à jour des métadonnées du job
        if job:
            job.meta['status'] = 'completed'
            job.meta['matches_count'] = len(results)
            job.save_meta()
        
        # Notification webhook si configurée
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            await send_webhook_notification(webhook_url, {
                'job_id': job.id if job else None,
                'status': 'completed',
                'job_id': job_id,
                'matches_count': len(results),
                'top_candidates': [result['candidate'] for result in results[:3]] if results else []
            })
        
        logger.info(f"Fin de la recherche de candidats pour job={job_id}, {len(results)} candidats trouvés")
        
        return results
    
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de candidats: {str(e)}", exc_info=True)
        
        # Mise à jour des métadonnées du job en cas d'erreur
        if job:
            job.meta['status'] = 'failed'
            job.meta['error'] = str(e)
            job.save_meta()
        
        # Notification webhook en cas d'erreur
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            await send_webhook_notification(webhook_url, {
                'job_id': job.id if job else None,
                'status': 'failed',
                'job_id': job_id,
                'error': str(e)
            })
        
        # Relancer l'exception pour que la tâche soit marquée comme échouée
        raise

async def process_cv_and_match_task(candidate_id: int, cv_file_path: str, job_ids: List[int], db: Any, openai_client: Any, user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Tâche RQ qui combine le parsing d'un CV et le matching avec plusieurs offres
    
    Args:
        candidate_id: ID du candidat
        cv_file_path: Chemin vers le fichier CV
        job_ids: Liste des IDs d'offres d'emploi à matcher
        db: Connexion à la base de données
        openai_client: Client OpenAI configuré
        user_id: ID de l'utilisateur demandant le matching (pour personnalisation)
        
    Returns:
        dict: Résultats du parsing et du matching
    """
    job = get_current_job()
    
    try:
        logger.info(f"Début du traitement CV et matching pour candidat={candidate_id}")
        
        # 1. Parsing du CV
        from app.services.matching_service import parse_cv_with_openai
        cv_data = await parse_cv_with_openai(cv_file_path, openai_client)
        
        # 2. Mise à jour des données du candidat
        await db.update_candidate_cv_data(candidate_id, cv_data)
        
        # 3. Matching avec les offres spécifiées
        results = await bulk_matching_process(candidate_id, job_ids, db, openai_client, user_id=user_id)
        
        # Mise à jour des métadonnées du job
        if job:
            job.meta['status'] = 'completed'
            job.meta['cv_parsed'] = True
            job.meta['matches_count'] = len(results)
            job.save_meta()
        
        # Notification webhook si configurée
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            await send_webhook_notification(webhook_url, {
                'job_id': job.id if job else None,
                'status': 'completed',
                'candidate_id': candidate_id,
                'cv_parsed': True,
                'matches_count': len(results),
                'top_matches': results[:3] if results else []
            })
        
        logger.info(f"Fin du traitement CV et matching pour candidat={candidate_id}, {len(results)} matchs trouvés")
        
        return {
            'cv_data': cv_data,
            'matching_results': results
        }
    
    except Exception as e:
        logger.error(f"Erreur lors du traitement CV et matching: {str(e)}", exc_info=True)
        
        # Mise à jour des métadonnées du job en cas d'erreur
        if job:
            job.meta['status'] = 'failed'
            job.meta['error'] = str(e)
            job.save_meta()
        
        # Notification webhook en cas d'erreur
        webhook_url = job.meta.get('webhook_url') if job else None
        if webhook_url:
            await send_webhook_notification(webhook_url, {
                'job_id': job.id if job else None,
                'status': 'failed',
                'candidate_id': candidate_id,
                'error': str(e)
            })
        
        # Relancer l'exception pour que la tâche soit marquée comme échouée
        raise
