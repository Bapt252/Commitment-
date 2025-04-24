"""
Utilitaires pour le chaînage de jobs entre le service de parsing CV et le service de matching.
"""
import requests
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def chain_cv_parsing_with_matching(
    candidate_id: int,
    job_ids: List[int],
    parsing_job_id: str,
    matching_api_url: str,
    webhook_url: Optional[str] = None,
    priority: str = "matching_high"
) -> Dict[str, Any]:
    """
    Chaîne un job de parsing CV avec un ou plusieurs jobs de matching
    
    Args:
        candidate_id: ID du candidat
        job_ids: Liste des IDs d'offres à matcher
        parsing_job_id: ID du job de parsing à utiliser comme dépendance
        matching_api_url: URL de l'API du service de matching
        webhook_url: URL de webhook optionnelle
        priority: Priorité de la file d'attente de matching
        
    Returns:
        dict: Réponse de l'API de matching
    """
    if not job_ids:
        logger.warning(f"Aucun ID d'offre fourni pour le chaînage avec le candidat {candidate_id}")
        return {"message": "Aucun ID d'offre fourni", "jobs": []}
    
    logger.info(f"Chaînage du parsing {parsing_job_id} avec le matching pour le candidat {candidate_id} contre {len(job_ids)} offres")
    
    payload = {
        "candidate_id": candidate_id,
        "job_ids": job_ids,
        "webhook_url": webhook_url
    }
    
    try:
        response = requests.post(
            f"{matching_api_url}/api/v1/queue-matching/bulk",
            json=payload,
            params={
                "priority": priority,
                "depends_on": parsing_job_id
            },
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        logger.info(f"Chaînage réussi : job de parsing {parsing_job_id} avec {len(result)} jobs de matching")
        return {
            "message": f"Chaînage réussi avec {len(result)} jobs de matching",
            "jobs": result
        }
        
    except Exception as e:
        logger.error(f"Échec du chaînage du parsing avec le matching: {str(e)}")
        return {
            "message": f"Échec du chaînage: {str(e)}",
            "jobs": []
        }
