#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Client pour le service de personnalisation

Ce module fournit une interface pour communiquer avec le service de personnalisation.
Il permet d'obtenir des poids personnalisés pour le matching et de personnaliser 
les résultats de recherche en fonction des préférences utilisateur.
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional
from app.core.resilience import retry_with_backoff
from app.utils.cache import cache_result

# Configuration du logger
logger = logging.getLogger(__name__)

class PersonalizationClient:
    """Client pour le service de personnalisation."""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialise le client.
        
        Args:
            base_url: URL de base du service de personnalisation. 
                     Si None, utilise l'URL depuis les variables d'environnement.
        """
        self.base_url = base_url or os.environ.get('PERSONALIZATION_SERVICE_URL', 'http://personalization-service:5060')
        self.session = requests.Session()
        logger.info(f"PersonalizationClient initialisé avec l'URL: {self.base_url}")
    
    @retry_with_backoff(max_retries=3, delay=1)
    def get_personalized_weights(self, user_id: str, job_id: Optional[int] = None, 
                                candidate_id: Optional[int] = None, 
                                original_weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        Obtient des poids personnalisés pour le matching.
        
        Args:
            user_id: Identifiant de l'utilisateur
            job_id: Identifiant de l'offre (optionnel)
            candidate_id: Identifiant du candidat (optionnel)
            original_weights: Poids originaux non personnalisés
            
        Returns:
            Dictionnaire des poids personnalisés
        """
        if original_weights is None:
            original_weights = {
                "skills": 0.4,
                "experience": 0.3,
                "education": 0.2,
                "certifications": 0.1
            }
            
        try:
            url = f"{self.base_url}/api/v1/personalize/matching"
            payload = {
                "user_id": user_id,
                "original_weights": original_weights
            }
            
            if job_id:
                payload["job_id"] = job_id
                
            if candidate_id:
                payload["candidate_id"] = candidate_id
                
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get("weights", original_weights)
            
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la personnalisation des poids: {str(e)}")
            logger.info("Utilisation des poids par défaut")
            return original_weights
    
    @retry_with_backoff(max_retries=3, delay=1)
    def personalize_results(self, user_id: str, results: List[Dict[str, Any]], 
                           search_query: Optional[str] = None, 
                           context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Personnalise l'ordre des résultats de recherche pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            results: Liste des résultats à réordonner
            search_query: Requête de recherche (optionnel)
            context: Contexte de la recherche (optionnel)
            
        Returns:
            Liste des résultats personnalisés
        """
        if not results:
            return []
            
        try:
            url = f"{self.base_url}/api/v1/personalize/job-search"
            payload = {
                "user_id": user_id,
                "results": results
            }
            
            if search_query:
                payload["search_query"] = search_query
                
            if context:
                payload["context"] = context
                
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get("results", results)
            
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la personnalisation des résultats: {str(e)}")
            logger.info("Utilisation des résultats non personnalisés")
            return results
    
    @retry_with_backoff(max_retries=3, delay=1)
    def record_feedback(self, user_id: str, feedback_data: Dict[str, Any]) -> bool:
        """
        Enregistre un feedback utilisateur pour améliorer la personnalisation.
        
        Args:
            user_id: Identifiant de l'utilisateur
            feedback_data: Données du feedback (doit contenir job_id ou candidate_id et action)
            
        Returns:
            True si le feedback a été enregistré avec succès, False sinon
        """
        try:
            url = f"{self.base_url}/api/v1/feedback"
            
            # S'assurer que le user_id est dans les données
            feedback_data["user_id"] = user_id
            
            response = self.session.post(url, json=feedback_data)
            response.raise_for_status()
            
            return True
            
        except requests.RequestException as e:
            logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}")
            return False
    
    @retry_with_backoff(max_retries=3, delay=1)
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère les préférences d'un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Dictionnaire des préférences utilisateur
        """
        try:
            url = f"{self.base_url}/api/v1/preferences/{user_id}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            return data.get("preferences", {})
            
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la récupération des préférences: {str(e)}")
            return {}
    
    def health_check(self) -> bool:
        """
        Vérifie si le service de personnalisation est disponible.
        
        Returns:
            True si le service est disponible, False sinon
        """
        try:
            url = f"{self.base_url}/health"
            response = self.session.get(url, timeout=2)
            return response.status_code == 200
        except:
            return False


# Instance singleton du client
_personalization_client = None

def get_personalization_client() -> PersonalizationClient:
    """
    Obtient l'instance singleton du client de personnalisation.
    
    Returns:
        Instance du client
    """
    global _personalization_client
    if _personalization_client is None:
        _personalization_client = PersonalizationClient()
    return _personalization_client
