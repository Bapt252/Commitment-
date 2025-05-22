#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Client pour le service de personnalisation

Ce module permet d'interagir avec le service de personnalisation
pour obtenir des résultats personnalisés en fonction des préférences utilisateur.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class PersonalizationClient:
    """
    Client pour interagir avec le service de personnalisation
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialise le client de personnalisation
        
        Args:
            base_url: URL de base du service de personnalisation (optionnel)
        """
        self.base_url = base_url or os.getenv('PERSONALIZATION_SERVICE_URL', 'http://personalization-service:5060')
        self.timeout = 5.0  # Timeout en secondes
        
    def personalize_job_search(self, user_id: str, results: List[Dict[str, Any]], 
                              search_query: str = '', context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Personnalise les résultats de recherche d'offres d'emploi
        
        Args:
            user_id: ID de l'utilisateur
            results: Liste des résultats originaux
            search_query: Requête de recherche (optionnelle)
            context: Contexte de la recherche (optionnel)
            
        Returns:
            List: Résultats personnalisés
        """
        if not results:
            return []
        
        try:
            url = f"{self.base_url}/api/v1/personalize/job-search"
            
            payload = {
                'user_id': user_id,
                'results': results,
                'search_query': search_query or '',
                'context': context or {}
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                personalized_data = response.json()
                return personalized_data.get('results', results)
            else:
                logger.warning(f"Erreur lors de la personnalisation des résultats: {response.status_code}")
                return results
                
        except RequestException as e:
            logger.error(f"Erreur de connexion au service de personnalisation: {str(e)}", exc_info=True)
            return results
        except Exception as e:
            logger.error(f"Erreur lors de la personnalisation des résultats: {str(e)}", exc_info=True)
            return results
    
    def personalize_matching_weights(self, user_id: str, job_id: Optional[int] = None, 
                                   candidate_id: Optional[int] = None,
                                   original_weights: Dict[str, float] = None) -> Dict[str, float]:
        """
        Personnalise les poids de matching pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            job_id: ID de l'offre d'emploi (optionnel)
            candidate_id: ID du candidat (optionnel)
            original_weights: Poids originaux (optionnel)
            
        Returns:
            Dict: Poids personnalisés
        """
        if not original_weights:
            original_weights = {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'certifications': 0.1
            }
        
        try:
            url = f"{self.base_url}/api/v1/personalize/matching"
            
            payload = {
                'user_id': user_id,
                'job_id': job_id,
                'candidate_id': candidate_id,
                'original_weights': original_weights
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                personalized_data = response.json()
                return personalized_data.get('weights', original_weights)
            else:
                logger.warning(f"Erreur lors de la personnalisation des poids: {response.status_code}")
                return original_weights
                
        except RequestException as e:
            logger.error(f"Erreur de connexion au service de personnalisation: {str(e)}", exc_info=True)
            return original_weights
        except Exception as e:
            logger.error(f"Erreur lors de la personnalisation des poids: {str(e)}", exc_info=True)
            return original_weights
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les préférences d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict: Préférences de l'utilisateur ou None en cas d'erreur
        """
        try:
            url = f"{self.base_url}/api/v1/preferences/{user_id}"
            
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('preferences')
            else:
                logger.warning(f"Erreur lors de la récupération des préférences: {response.status_code}")
                return None
                
        except RequestException as e:
            logger.error(f"Erreur de connexion au service de personnalisation: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des préférences: {str(e)}", exc_info=True)
            return None
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Sauvegarde les préférences d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            preferences: Préférences à sauvegarder
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            url = f"{self.base_url}/api/v1/preferences"
            
            payload = {
                'user_id': user_id,
                'preferences': preferences
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'success'
            else:
                logger.warning(f"Erreur lors de la sauvegarde des préférences: {response.status_code}")
                return False
                
        except RequestException as e:
            logger.error(f"Erreur de connexion au service de personnalisation: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des préférences: {str(e)}", exc_info=True)
            return False
    
    def record_feedback(self, user_id: str, job_id: Optional[int] = None, 
                       candidate_id: Optional[int] = None, action: str = '', 
                       context: Dict[str, Any] = None) -> bool:
        """
        Enregistre un feedback utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            job_id: ID de l'offre d'emploi (optionnel)
            candidate_id: ID du candidat (optionnel)
            action: Type d'action (like, dislike, etc.)
            context: Contexte du feedback (optionnel)
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            url = f"{self.base_url}/api/v1/feedback"
            
            payload = {
                'user_id': user_id,
                'job_id': job_id,
                'candidate_id': candidate_id,
                'action': action,
                'context': context or {}
            }
            
            response = requests.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'success'
            else:
                logger.warning(f"Erreur lors de l'enregistrement du feedback: {response.status_code}")
                return False
                
        except RequestException as e:
            logger.error(f"Erreur de connexion au service de personnalisation: {str(e)}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}", exc_info=True)
            return False
    
    def check_health(self) -> bool:
        """
        Vérifie la santé du service de personnalisation
        
        Returns:
            bool: True si le service est en bonne santé, False sinon
        """
        try:
            url = f"{self.base_url}/health"
            
            response = requests.get(url, timeout=self.timeout)
            
            return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Erreur lors de la vérification de la santé du service: {str(e)}", exc_info=True)
            return False
