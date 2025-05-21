#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chargeur de données pour le service de personnalisation

Ce module fournit des méthodes pour charger et sauvegarder les données
utilisées par le service de personnalisation, comme les préférences
utilisateur, les interactions, et les données de CV et d'offres d'emploi.
"""

import logging
import json
import psycopg2
import redis
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

class DataLoader:
    """
    Classe pour charger et sauvegarder les données du service de personnalisation
    """
    
    def __init__(self, db_url: str, redis_client: redis.Redis):
        """
        Initialise le chargeur de données
        
        Args:
            db_url: URL de connexion à la base de données PostgreSQL
            redis_client: Instance de client Redis
        """
        self.db_url = db_url
        self.redis_client = redis_client
        
        # Configuration du cache Redis
        self.cache_ttl = 3600  # 1 heure en secondes
        
        # Configuration des requêtes HTTP
        self.request_timeout = 10  # 10 secondes
        
        # URL du service de matching
        self.matching_service_url = "http://matching-api:5000"
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les préférences d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Dict: Préférences utilisateur ou None si non trouvées
        """
        # Vérifier d'abord dans le cache Redis
        cache_key = f"user_preferences:{user_id}"
        cached_preferences = self.redis_client.get(cache_key)
        
        if cached_preferences:
            try:
                return json.loads(cached_preferences)
            except Exception as e:
                logger.warning(f"Erreur de décodage du cache de préférences: {str(e)}")
        
        # Si pas en cache, chercher dans la base de données
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            query = """
                SELECT preferences FROM user_preferences WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result and result[0]:
                preferences = result[0]
                # Mettre en cache pour les prochaines requêtes
                self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(preferences))
                return preferences
            
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
            # Convertir les préférences en JSON pour stockage
            preferences_json = json.dumps(preferences)
            
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            # Insertion ou mise à jour (upsert) avec ON CONFLICT
            query = """
                INSERT INTO user_preferences (user_id, preferences, updated_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET preferences = EXCLUDED.preferences, updated_at = EXCLUDED.updated_at
            """
            cursor.execute(query, (user_id, preferences_json, datetime.now()))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # Mettre à jour le cache Redis
            cache_key = f"user_preferences:{user_id}"
            self.redis_client.setex(cache_key, self.cache_ttl, preferences_json)
            
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des préférences: {str(e)}", exc_info=True)
            return False
    
    def get_user_interactions(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des interactions d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            List: Liste des interactions
        """
        # Vérifier d'abord dans le cache Redis
        cache_key = f"user_interactions:{user_id}"
        cached_interactions = self.redis_client.get(cache_key)
        
        if cached_interactions:
            try:
                return json.loads(cached_interactions)
            except Exception as e:
                logger.warning(f"Erreur de décodage du cache d'interactions: {str(e)}")
        
        # Si pas en cache, chercher dans la base de données
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            query = """
                SELECT action_type, details, created_at
                FROM user_interactions
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 100
            """
            cursor.execute(query, (user_id,))
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            interactions = []
            for row in rows:
                action_type, details, timestamp = row
                interaction = {
                    'action_type': action_type,
                    'details': details if isinstance(details, dict) else json.loads(details) if details else {},
                    'timestamp': timestamp.isoformat() if timestamp else None
                }
                interactions.append(interaction)
            
            # Mettre en cache pour les prochaines requêtes
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(interactions))
            
            return interactions
        
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des interactions: {str(e)}", exc_info=True)
            return []
    
    def save_interaction(self, user_id: str, action_type: str, details: Dict[str, Any]) -> bool:
        """
        Sauvegarde une interaction utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            action_type: Type d'action (search_jobs, view_job, etc.)
            details: Détails de l'interaction
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            # Convertir les détails en JSON pour stockage
            details_json = json.dumps(details)
            
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO user_interactions (user_id, action_type, details, created_at)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, action_type, details_json, datetime.now()))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # Invalider le cache des interactions
            cache_key = f"user_interactions:{user_id}"
            self.redis_client.delete(cache_key)
            
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'interaction: {str(e)}", exc_info=True)
            return False
    
    def save_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde le feedback utilisateur
        
        Args:
            feedback_data: Données de feedback (user_id, job_id, action, etc.)
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            user_id = feedback_data.get('user_id')
            job_id = feedback_data.get('job_id')
            candidate_id = feedback_data.get('candidate_id')
            action = feedback_data.get('action')
            context = feedback_data.get('context', {})
            
            if not user_id or not action or (not job_id and not candidate_id):
                logger.warning("Données de feedback incomplètes")
                return False
            
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO user_feedback (user_id, job_id, candidate_id, action, context, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (user_id, job_id, candidate_id, action, json.dumps(context), datetime.now()))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # Enregistrer également comme interaction
            interaction_details = {
                'job_id': job_id,
                'candidate_id': candidate_id,
                'action': action,
                'context': context
            }
            self.save_interaction(user_id, f"feedback_{action}", interaction_details)
            
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du feedback: {str(e)}", exc_info=True)
            return False
    
    def get_job_data(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les données d'une offre d'emploi
        
        Args:
            job_id: ID de l'offre d'emploi
            
        Returns:
            Dict: Données de l'offre ou None si non trouvée
        """
        # Vérifier d'abord dans le cache Redis
        cache_key = f"job_data:{job_id}"
        cached_job = self.redis_client.get(cache_key)
        
        if cached_job:
            try:
                return json.loads(cached_job)
            except Exception as e:
                logger.warning(f"Erreur de décodage du cache de job: {str(e)}")
        
        try:
            # Récupérer depuis la base de données
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            query = """
                SELECT title, description, location, company, job_type, company_size, industry,
                       skills, experience_years, education_level, certifications, parsed_data
                FROM jobs
                WHERE id = %s
            """
            cursor.execute(query, (job_id,))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not row:
                # Si pas dans la base de données, essayer de récupérer via l'API du service de matching
                return self._get_job_from_matching_service(job_id)
            
            # Construire l'objet job
            title, description, location, company, job_type, company_size, industry, \
            skills, experience_years, education_level, certifications, parsed_data = row
            
            job_data = {
                'id': job_id,
                'title': title,
                'description': description,
                'location': location,
                'company': company,
                'job_type': job_type,
                'company_size': company_size,
                'industry': industry,
                'skills': skills.split(',') if isinstance(skills, str) else skills or [],
                'experience_years': experience_years,
                'education_level': education_level,
                'certifications': certifications.split(',') if isinstance(certifications, str) else certifications or [],
                'parsed_data': parsed_data if isinstance(parsed_data, dict) else json.loads(parsed_data) if parsed_data else {}
            }
            
            # Mettre en cache pour les prochaines requêtes
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(job_data))
            
            return job_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données de l'offre: {str(e)}", exc_info=True)
            # Essayer de récupérer via l'API du service de matching en cas d'erreur
            return self._get_job_from_matching_service(job_id)
    
    def _get_job_from_matching_service(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les données d'une offre d'emploi via l'API du service de matching
        
        Args:
            job_id: ID de l'offre d'emploi
            
        Returns:
            Dict: Données de l'offre ou None si non trouvée
        """
        try:
            url = f"{self.matching_service_url}/api/v1/jobs/{job_id}"
            response = requests.get(url, timeout=self.request_timeout)
            
            if response.status_code == 200:
                job_data = response.json()
                
                # Mettre en cache pour les prochaines requêtes
                cache_key = f"job_data:{job_id}"
                self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(job_data))
                
                return job_data
                
            logger.warning(f"Impossible de récupérer le job {job_id} du service de matching: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du job depuis l'API: {str(e)}", exc_info=True)
            return None
    
    def get_candidate_data(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les données d'un candidat
        
        Args:
            candidate_id: ID du candidat
            
        Returns:
            Dict: Données du candidat ou None si non trouvé
        """
        # Vérifier d'abord dans le cache Redis
        cache_key = f"candidate_data:{candidate_id}"
        cached_candidate = self.redis_client.get(cache_key)
        
        if cached_candidate:
            try:
                return json.loads(cached_candidate)
            except Exception as e:
                logger.warning(f"Erreur de décodage du cache de candidat: {str(e)}")
        
        try:
            # Récupérer depuis la base de données
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            query = """
                SELECT name, title, experience, experience_years, education, education_level,
                       skills, certifications, location, parsed_data
                FROM candidates
                WHERE id = %s
            """
            cursor.execute(query, (candidate_id,))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not row:
                # Si pas dans la base de données, essayer de récupérer via l'API du service de matching
                return self._get_candidate_from_matching_service(candidate_id)
            
            # Construire l'objet candidat
            name, title, experience, experience_years, education, education_level, \
            skills, certifications, location, parsed_data = row
            
            candidate_data = {
                'id': candidate_id,
                'name': name,
                'title': title,
                'experience': experience,
                'experience_years': experience_years,
                'education': education,
                'education_level': education_level,
                'skills': skills.split(',') if isinstance(skills, str) else skills or [],
                'certifications': certifications.split(',') if isinstance(certifications, str) else certifications or [],
                'location': location,
                'parsed_data': parsed_data if isinstance(parsed_data, dict) else json.loads(parsed_data) if parsed_data else {}
            }
            
            # Mettre en cache pour les prochaines requêtes
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(candidate_data))
            
            return candidate_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des données du candidat: {str(e)}", exc_info=True)
            # Essayer de récupérer via l'API du service de matching en cas d'erreur
            return self._get_candidate_from_matching_service(candidate_id)
    
    def _get_candidate_from_matching_service(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """
        Récupère les données d'un candidat via l'API du service de matching
        
        Args:
            candidate_id: ID du candidat
            
        Returns:
            Dict: Données du candidat ou None si non trouvé
        """
        try:
            url = f"{self.matching_service_url}/api/v1/candidates/{candidate_id}"
            response = requests.get(url, timeout=self.request_timeout)
            
            if response.status_code == 200:
                candidate_data = response.json()
                
                # Mettre en cache pour les prochaines requêtes
                cache_key = f"candidate_data:{candidate_id}"
                self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(candidate_data))
                
                return candidate_data
                
            logger.warning(f"Impossible de récupérer le candidat {candidate_id} du service de matching: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du candidat depuis l'API: {str(e)}", exc_info=True)
            return None
    
    def get_all_interactions_for_collaborative_filtering(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les interactions pertinentes pour le filtrage collaboratif
        
        Returns:
            List: Liste des interactions formatées pour le filtrage collaboratif
        """
        try:
            # Vérifier d'abord dans le cache Redis
            cache_key = "all_interactions_for_collab_filtering"
            cached_interactions = self.redis_client.get(cache_key)
            
            if cached_interactions:
                try:
                    return json.loads(cached_interactions)
                except Exception as e:
                    logger.warning(f"Erreur de décodage du cache des interactions: {str(e)}")
            
            # Si pas en cache, récupérer depuis la base de données
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            
            query = """
                SELECT user_id, action_type, details, created_at
                FROM user_interactions
                WHERE action_type IN ('view_job', 'bookmark_job', 'apply_job', 'dislike_job',
                                      'view_candidate', 'bookmark_candidate', 'contact_candidate', 'dislike_candidate')
                ORDER BY created_at DESC
                LIMIT 10000
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            # Transformer les données au format requis pour le filtrage collaboratif
            interactions = []
            
            for row in rows:
                user_id, action_type, details, timestamp = row
                
                if isinstance(details, str):
                    try:
                        details = json.loads(details)
                    except:
                        details = {}
                
                # Déterminer l'item_id et la valeur de l'interaction
                item_id = None
                value = 0.0
                
                if action_type in ['view_job', 'bookmark_job', 'apply_job', 'dislike_job']:
                    job_id = details.get('job_id')
                    if job_id:
                        item_id = f"job_{job_id}"
                        item_type = 'job'
                        
                        # Valeur de l'interaction en fonction de l'action
                        if action_type == 'view_job':
                            value = 0.5
                        elif action_type == 'bookmark_job':
                            value = 1.5
                        elif action_type == 'apply_job':
                            value = 2.0
                        elif action_type == 'dislike_job':
                            value = -0.5
                
                elif action_type in ['view_candidate', 'bookmark_candidate', 'contact_candidate', 'dislike_candidate']:
                    candidate_id = details.get('candidate_id')
                    if candidate_id:
                        item_id = f"candidate_{candidate_id}"
                        item_type = 'candidate'
                        
                        # Valeur de l'interaction en fonction de l'action
                        if action_type == 'view_candidate':
                            value = 0.5
                        elif action_type == 'bookmark_candidate':
                            value = 1.5
                        elif action_type == 'contact_candidate':
                            value = 2.0
                        elif action_type == 'dislike_candidate':
                            value = -0.5
                
                if item_id and value != 0.0:
                    interaction = {
                        'user_id': user_id,
                        'item_id': item_id,
                        'item_type': item_type,
                        'action': action_type,
                        'value': value,
                        'timestamp': timestamp.isoformat() if timestamp else None
                    }
                    interactions.append(interaction)
            
            # Mettre en cache pour les prochaines requêtes
            self.redis_client.setex(cache_key, 3600, json.dumps(interactions))  # 1 heure de TTL
            
            return interactions
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des interactions pour le filtrage collaboratif: {str(e)}", exc_info=True)
            return []
