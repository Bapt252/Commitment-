from typing import Dict, List, Any, Optional
import json
import asyncio
import aioredis
import logging
import numpy as np
import os
import random
from datetime import datetime, timedelta
from .schema import BaseEvent, EventType

logger = logging.getLogger(__name__)

class MetricsCalculator:
    """Calculateur de métriques de performance des matchs"""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
        
    async def calculate_acceptance_rate(self, time_window_days=30):
        """Calcule le taux d'acceptation des matchs sur une période donnée"""
        async with self.db_pool.acquire() as conn:
            query = """
            SELECT
                COUNT(*) FILTER (WHERE event_type = 'match_accepted') AS accepted,
                COUNT(*) FILTER (WHERE event_type IN ('match_accepted', 'match_rejected')) AS total
            FROM tracking.events
            WHERE event_timestamp >= NOW() - $1::interval
            """
            row = await conn.fetchrow(query, f"{time_window_days} days")
            
            if row and row["total"] > 0:
                return row["accepted"] / row["total"]
            return 0
            
    async def calculate_avg_feedback_rating(self, time_window_days=30):
        """Calcule la note moyenne des feedbacks sur une période donnée"""
        async with self.db_pool.acquire() as conn:
            query = """
            SELECT AVG(fe.rating) AS avg_rating
            FROM tracking.events e
            JOIN tracking.feedback_events fe ON e.event_id = fe.event_id
            WHERE e.event_timestamp >= NOW() - $1::interval
            """
            row = await conn.fetchrow(query, f"{time_window_days} days")
            return row["avg_rating"] if row and row["avg_rating"] is not None else 0
            
    async def calculate_constraint_impact(self, time_window_days=30):
        """Calcule l'impact de chaque contrainte sur les décisions"""
        async with self.db_pool.acquire() as conn:
            query = """
            WITH constraint_data AS (
                SELECT
                    e.event_type,
                    me.constraint_satisfaction::jsonb as constraints,
                    jsonb_object_keys(me.constraint_satisfaction::jsonb) as constraint_name
                FROM tracking.events e
                JOIN tracking.match_events me ON e.event_id = me.event_id
                WHERE e.event_type IN ('match_accepted', 'match_rejected')
                AND e.event_timestamp >= NOW() - $1::interval
            )
            SELECT
                constraint_name,
                event_type,
                AVG((constraints->>constraint_name)::numeric) as avg_value
            FROM constraint_data
            GROUP BY constraint_name, event_type
            """
            rows = await conn.fetch(query, f"{time_window_days} days")
            
            # Organiser les résultats par contrainte
            results = {}
            for row in rows:
                constraint = row["constraint_name"]
                if constraint not in results:
                    results[constraint] = {"accepted": 0, "rejected": 0}
                    
                event_type = row["event_type"]
                if event_type == "match_accepted":
                    results[constraint]["accepted"] = row["avg_value"]
                elif event_type == "match_rejected":
                    results[constraint]["rejected"] = row["avg_value"]
                    
            # Calculer l'impact (différence entre acceptés et refusés)
            for constraint in results:
                results[constraint]["impact"] = (
                    results[constraint]["accepted"] - results[constraint]["rejected"]
                )
                
            return results

class MLFeedbackProcessor:
    """Processeur qui met à jour le modèle ML en fonction des feedbacks"""
    
    def __init__(self, db_pool, model_service_url=None):
        self.db_pool = db_pool
        self.model_service_url = model_service_url or "http://ml-engine:5000"
        
    async def collect_training_data(self, limit=1000):
        """Collecte les données d'entraînement depuis les feedbacks"""
        async with self.db_pool.acquire() as conn:
            query = """
            SELECT
                me.match_id,
                me.match_score,
                me.constraint_satisfaction,
                fe.rating
            FROM tracking.events e
            JOIN tracking.match_events me ON e.event_id = me.event_id
            JOIN tracking.feedback_events fe ON me.match_id = fe.match_id
            WHERE e.event_type = 'match_proposed'
            ORDER BY e.event_timestamp DESC
            LIMIT $1
            """
            rows = await conn.fetch(query, limit)
            
            # Transformer en format adapté pour l'entraînement
            training_data = []
            for row in rows:
                # Extraire les features des contraintes
                constraints = json.loads(row["constraint_satisfaction"])
                features = {f"constraint_{k}": float(v) for k, v in constraints.items()}
                features["match_score"] = row["match_score"]
                
                # Label = note de feedback
                label = row["rating"]
                
                training_data.append({"features": features, "label": label})
                
            return training_data
            
    async def update_model_weights(self):
        """Met à jour les poids du modèle basé sur les feedbacks récents"""
        try:
            # Collecter les données d'entraînement
            training_data = await self.collect_training_data()
            
            if not training_data:
                logger.warning("No training data available for model update")
                return False
                
            # Envoyer les données au service ML pour mise à jour
            # Dans une implémentation réelle, on utiliserait un client HTTP
            # pour communiquer avec le service ML
            logger.info(f"Collected {len(training_data)} samples for model update")
            
            # Calculer les nouveaux poids localement (version simplifiée)
            weights = self.calculate_weights_locally(training_data)
            
            # Stocker les nouveaux poids
            await self.store_model_weights(weights)
            
            return True
        except Exception as e:
            logger.error(f"Error updating model weights: {str(e)}")
            return False
            
    def calculate_weights_locally(self, training_data):
        """Calcule les poids localement (version simplifiée)"""
        # Extraire toutes les clés de features
        all_features = set()
        for sample in training_data:
            all_features.update(sample["features"].keys())
            
        # Initialiser les vecteurs pour la régression
        X = []
        y = []
        
        # Préparer les données pour régression
        for sample in training_data:
            features = [sample["features"].get(f, 0) for f in sorted(all_features)]
            X.append(features)
            y.append(sample["label"])
            
        # Calcul simplifié des poids (utilise numpy)
        X = np.array(X)
        y = np.array(y)
        
        # Ajouter une colonne de 1 pour le biais
        X = np.column_stack((np.ones(X.shape[0]), X))
        
        # Calculer les poids par régression linéaire simple
        # w = (X^T X)^-1 X^T y
        try:
            weights = np.linalg.inv(X.T.dot(X)).dot(X.T).dot(y)
            
            # Convertir en dictionnaire
            weight_dict = {"bias": float(weights[0])}
            for i, feature in enumerate(sorted(all_features)):
                weight_dict[feature] = float(weights[i + 1])
                
            return weight_dict
        except Exception as e:
            logger.error(f"Error in weight calculation: {str(e)}")
            return {}
            
    async def store_model_weights(self, weights):
        """Stocke les poids du modèle en base de données"""
        async with self.db_pool.acquire() as conn:
            # Stocker dans une table de configuration
            await conn.execute(
                """
                INSERT INTO tracking.model_weights (weights_json, created_at)
                VALUES ($1, NOW())
                """,
                json.dumps(weights)
            )
            
            logger.info("Stored updated model weights")

class EventProcessor:
    def __init__(self, storage_backend=None, processing_interval: int = 60, redis_url=None):
        self.storage_backend = storage_backend
        self.processing_interval = processing_interval
        self.event_handlers = {}
        self.redis_url = redis_url or os.environ.get("REDIS_URL", "redis://redis:6379")
        self.metrics_calculator = None
        self.ml_processor = None
        self.redis = None
        
        # Définir une expiration pour les notifications (1 jour)
        self.notification_ttl = 60 * 60 * 24
        
        self.register_default_handlers()
        
    async def initialize(self):
        """Initialise les ressources du processeur"""
        # Connexion Redis pour les notifications temps réel
        try:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
            logger.info(f"Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            
        # Initialiser les calculateurs de métriques si le backend a un pool
        if hasattr(self.storage_backend, "pool"):
            self.metrics_calculator = MetricsCalculator(self.storage_backend.pool)
            self.ml_processor = MLFeedbackProcessor(self.storage_backend.pool)
            logger.info("Metrics calculator and ML processor initialized")
            
    async def close(self):
        """Ferme les ressources du processeur"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            logger.info("Redis connection closed")
        
    def register_handler(self, event_type: EventType, handler_func):
        """Enregistre un handler pour un type d'événement"""
        self.event_handlers[event_type] = handler_func
        
    def register_default_handlers(self):
        """Enregistre les handlers par défaut pour les différents types d'événements"""
        self.register_handler(EventType.MATCH_PROPOSED, self.handle_match_proposed)
        self.register_handler(EventType.MATCH_VIEWED, self.handle_match_viewed)
        self.register_handler(EventType.MATCH_ACCEPTED, self.handle_match_accepted)
        self.register_handler(EventType.MATCH_REJECTED, self.handle_match_rejected)
        self.register_handler(EventType.MATCH_FEEDBACK, self.handle_match_feedback)
        self.register_handler(EventType.MATCH_INTERACTION, self.handle_match_interaction)
        self.register_handler(EventType.MATCH_COMPLETED, self.handle_match_completed)
        self.register_handler(EventType.MATCH_ABANDONED, self.handle_match_abandoned)
        
    async def handle_match_proposed(self, event):
        """Traite un événement de proposition de match"""
        # Envoyer une notification en temps réel
        if self.redis:
            try:
                channel = f"user:{event.user_id}:notifications"
                notification = {
                    "type": "match_proposed",
                    "match_id": event.match_id,
                    "match_score": event.match_score,
                    "timestamp": event.timestamp.isoformat()
                }
                await self.redis.publish(channel, json.dumps(notification))
                logger.debug(f"Published match_proposed notification to {channel}")
            except Exception as e:
                logger.error(f"Error publishing to Redis: {str(e)}")
            
    async def handle_match_viewed(self, event):
        """Traite un événement de visualisation de match"""
        # Stocker la durée de visualisation pour l'analyse
        if hasattr(self.storage_backend, "pool"):
            try:
                async with self.storage_backend.pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO tracking.match_view_metrics 
                        (match_id, user_id, view_duration, view_complete, timestamp)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        event.match_id, event.user_id, event.view_duration_seconds,
                        event.view_complete, event.timestamp
                    )
                    logger.debug(f"Stored match view metrics for {event.match_id}")
            except Exception as e:
                logger.error(f"Error storing match view metrics: {str(e)}")
        
    async def handle_match_accepted(self, event):
        """Traite un événement d'acceptation de match"""
        # Mettre à jour les statistiques d'acceptation
        if hasattr(self.storage_backend, "pool"):
            try:
                async with self.storage_backend.pool.acquire() as conn:
                    # Récupérer les infos du match
                    match_info = await conn.fetchrow(
                        """
                        SELECT match_score, constraint_satisfaction
                        FROM tracking.match_events
                        WHERE match_id = $1
                        """,
                        event.match_id
                    )
                    
                    if match_info:
                        # Incrémenter le compteur d'acceptation pour ce profil de contraintes
                        constraints = json.loads(match_info["constraint_satisfaction"])
                        for constraint, value in constraints.items():
                            # Arrondir à 0.1 près pour le bucketing
                            bucket = round(float(value) * 10) / 10
                            
                            # Incrémenter le compteur
                            await conn.execute(
                                """
                                INSERT INTO tracking.constraint_stats 
                                (constraint_name, value_bucket, acceptances, rejections)
                                VALUES ($1, $2, 1, 0)
                                ON CONFLICT (constraint_name, value_bucket)
                                DO UPDATE SET acceptances = tracking.constraint_stats.acceptances + 1
                                """,
                                constraint, bucket
                            )
                        logger.debug(f"Updated constraint stats for match {event.match_id}")
            except Exception as e:
                logger.error(f"Error updating constraint stats: {str(e)}")
                        
        # Envoyer une notification en temps réel
        if self.redis:
            try:
                # Notification à l'utilisateur
                user_channel = f"user:{event.user_id}:notifications"
                notification = {
                    "type": "match_accepted",
                    "match_id": event.match_id,
                    "timestamp": event.timestamp.isoformat()
                }
                await self.redis.publish(user_channel, json.dumps(notification))
                
                # Notification au système pour les tableaux de bord
                admin_channel = "admin:match_events"
                admin_notification = {
                    "type": "match_accepted",
                    "match_id": event.match_id,
                    "user_id": event.user_id,
                    "decision_time": event.decision_time_seconds,
                    "timestamp": event.timestamp.isoformat()
                }
                await self.redis.publish(admin_channel, json.dumps(admin_notification))
                logger.debug(f"Published match_accepted notifications")
            except Exception as e:
                logger.error(f"Error publishing to Redis: {str(e)}")
        
    async def handle_match_rejected(self, event):
        """Traite un événement de rejet de match"""
        # Mettre à jour les statistiques de rejet
        if hasattr(self.storage_backend, "pool"):
            try:
                async with self.storage_backend.pool.acquire() as conn:
                    # Récupérer les infos du match
                    match_info = await conn.fetchrow(
                        """
                        SELECT match_score, constraint_satisfaction
                        FROM tracking.match_events
                        WHERE match_id = $1
                        """,
                        event.match_id
                    )
                    
                    if match_info:
                        # Incrémenter le compteur de rejet pour ce profil de contraintes
                        constraints = json.loads(match_info["constraint_satisfaction"])
                        for constraint, value in constraints.items():
                            # Arrondir à 0.1 près pour le bucketing
                            bucket = round(float(value) * 10) / 10
                            
                            # Incrémenter le compteur
                            await conn.execute(
                                """
                                INSERT INTO tracking.constraint_stats 
                                (constraint_name, value_bucket, acceptances, rejections)
                                VALUES ($1, $2, 0, 1)
                                ON CONFLICT (constraint_name, value_bucket)
                                DO UPDATE SET rejections = tracking.constraint_stats.rejections + 1
                                """,
                                constraint, bucket
                            )
                        logger.debug(f"Updated constraint stats for rejected match {event.match_id}")
                        
                    # Enregistrer les raisons du rejet
                    if event.reasons:
                        for reason in event.reasons:
                            await conn.execute(
                                """
                                INSERT INTO tracking.rejection_reasons 
                                (match_id, user_id, reason, timestamp)
                                VALUES ($1, $2, $3, $4)
                                """,
                                event.match_id, event.user_id, reason, event.timestamp
                            )
                        logger.debug(f"Stored {len(event.reasons)} rejection reasons for match {event.match_id}")
            except Exception as e:
                logger.error(f"Error processing match rejection: {str(e)}")
        
        # Envoyer notification pour tableaux de bord en temps réel
        if self.redis:
            try:
                admin_channel = "admin:match_events"
                admin_notification = {
                    "type": "match_rejected",
                    "match_id": event.match_id,
                    "user_id": event.user_id,
                    "decision_time": event.decision_time_seconds,
                    "reasons": event.reasons,
                    "timestamp": event.timestamp.isoformat()
                }
                await self.redis.publish(admin_channel, json.dumps(admin_notification))
                logger.debug(f"Published match_rejected notification")
            except Exception as e:
                logger.error(f"Error publishing to Redis: {str(e)}")
        
    async def handle_match_feedback(self, event):
        """Traite un événement de feedback sur un match"""
        # Stocker le feedback structuré
        if hasattr(self.storage_backend, "pool"):
            try:
                async with self.storage_backend.pool.acquire() as conn:
                    # Récupérer le score du match
                    match_score = await conn.fetchval(
                        """
                        SELECT match_score
                        FROM tracking.match_events
                        WHERE match_id = $1
                        """,
                        event.match_id
                    )
                    
                    # Enregistrer la corrélation feedback/score
                    await conn.execute(
                        """
                        INSERT INTO tracking.feedback_correlation 
                        (match_id, user_id, match_score, rating, timestamp)
                        VALUES ($1, $2, $3, $4, $5)
                        """,
                        event.match_id, event.user_id, match_score, 
                        event.rating, event.timestamp
                    )
                    
                    # Stocker les aspects spécifiques
                    if event.specific_aspects:
                        for aspect, rating in event.specific_aspects.items():
                            await conn.execute(
                                """
                                INSERT INTO tracking.feedback_aspects 
                                (match_id, user_id, aspect, rating, timestamp)
                                VALUES ($1, $2, $3, $4, $5)
                                """,
                                event.match_id, event.user_id, aspect, 
                                rating, event.timestamp
                            )
                        logger.debug(f"Stored {len(event.specific_aspects)} feedback aspects for match {event.match_id}")
                    
                    logger.info(f"Processed feedback for match {event.match_id} with rating {event.rating}")
            except Exception as e:
                logger.error(f"Error processing match feedback: {str(e)}")
                        
        # Mise à jour du modèle ML si suffisamment de feedbacks
        if self.ml_processor:
            try:
                # Vérifier si c'est le moment de mettre à jour le modèle
                # (par exemple, tous les 100 feedbacks)
                if hasattr(self.storage_backend, "pool"):
                    async with self.storage_backend.pool.acquire() as conn:
                        feedback_count = await conn.fetchval(
                            "SELECT COUNT(*) FROM tracking.feedback_events"
                        )
                        
                        if feedback_count % 100 == 0:
                            # Lancer la mise à jour en arrière-plan
                            asyncio.create_task(self.ml_processor.update_model_weights())
                            logger.info(f"Scheduled model weight update after {feedback_count} feedbacks")
            except Exception as e:
                logger.error(f"Error scheduling model update: {str(e)}")
    
    async def handle_match_interaction(self, event):
        """Traite un événement d'interaction après matching"""
        # Si besoin de stocker ou traiter les interactions spécifiquement
        if self.redis:
            try:
                # Notification pour le dashboard administrateur
                admin_channel = "admin:match_interactions"
                notification = {
                    "type": "match_interaction",
                    "match_id": event.match_id,
                    "user_id": event.user_id,
                    "interaction_type": event.interaction_type,
                    "interaction_count": event.interaction_count,
                    "timestamp": event.timestamp.isoformat()
                }
                await self.redis.publish(admin_channel, json.dumps(notification))
                logger.debug(f"Published match_interaction notification for {event.interaction_type}")
            except Exception as e:
                logger.error(f"Error publishing interaction to Redis: {str(e)}")
    
    async def handle_match_completed(self, event):
        """Traite un événement de complétion d'engagement"""
        # Mettre à jour les statistiques de complétion
        if hasattr(self.storage_backend, "pool") and self.redis:
            try:
                # Notification pour le dashboard administrateur
                admin_channel = "admin:match_completions"
                notification = {
                    "type": "match_completed",
                    "match_id": event.match_id,
                    "user_id": event.user_id,
                    "duration_days": event.duration_days,
                    "completion_rate": event.completion_rate,
                    "timestamp": event.timestamp.isoformat()
                }
                await self.redis.publish(admin_channel, json.dumps(notification))
                logger.info(f"Match {event.match_id} completed with rate {event.completion_rate}")
            except Exception as e:
                logger.error(f"Error publishing completion to Redis: {str(e)}")
    
    async def handle_match_abandoned(self, event):
        """Traite un événement d'abandon d'engagement"""
        # Analyser les raisons d'abandon
        if hasattr(self.storage_backend, "pool") and self.redis:
            try:
                # Notification pour le dashboard administrateur
                admin_channel = "admin:match_abandonments" 
                notification = {
                    "type": "match_abandoned",
                    "match_id": event.match_id,
                    "user_id": event.user_id,
                    "duration_days": event.duration_days,
                    "completion_rate": event.completion_rate,
                    "timestamp": event.timestamp.isoformat()
                }
                await self.redis.publish(admin_channel, json.dumps(notification))
                logger.info(f"Match {event.match_id} abandoned with partial completion {event.completion_rate}")
            except Exception as e:
                logger.error(f"Error publishing abandonment to Redis: {str(e)}")
                
    async def process_events(self, events: List[BaseEvent]):
        """Traite une liste d'événements"""
        for event in events:
            handler = self.event_handlers.get(event.event_type)
            if handler:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error processing event {event.event_id}: {str(e)}")
            else:
                logger.warning(f"No handler for event type: {event.event_type}")
                
    async def processing_worker(self):
        """Worker qui récupère et traite périodiquement les événements"""
        while True:
            try:
                # Récupérer les événements non traités
                if self.storage_backend and hasattr(self.storage_backend, "get_unprocessed_events"):
                    events = await self.storage_backend.get_unprocessed_events()
                    if events:
                        logger.info(f"Processing {len(events)} unprocessed events")
                        await self.process_events(events)
                        await self.storage_backend.mark_events_processed([e.event_id for e in events])
                        
                # Calculer périodiquement les métriques globales (une fois par heure environ)
                if self.metrics_calculator and self.redis and random.random() < 0.01:  # ~1% des itérations
                    try:
                        # Calculer les métriques
                        acceptance_rate = await self.metrics_calculator.calculate_acceptance_rate()
                        avg_rating = await self.metrics_calculator.calculate_avg_feedback_rating() 
                        constraint_impact = await self.metrics_calculator.calculate_constraint_impact()
                        
                        # Publier les métriques pour le dashboard
                        metrics = {
                            "timestamp": datetime.now().isoformat(),
                            "acceptance_rate": acceptance_rate,
                            "avg_feedback_rating": avg_rating,
                            "constraint_impact": constraint_impact
                        }
                        await self.redis.publish("metrics:dashboard", json.dumps(metrics))
                        logger.info("Published updated metrics to dashboard")
                    except Exception as e:
                        logger.error(f"Error calculating metrics: {str(e)}")
                        
            except Exception as e:
                logger.error(f"Error in processing worker: {str(e)}")
                
            # Attendre avant la prochaine exécution
            await asyncio.sleep(self.processing_interval)
