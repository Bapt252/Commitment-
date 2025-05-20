from typing import Dict, Any, Optional, List
from .schema import BaseEvent, EventType
from .privacy import PrivacyManager
import json
import asyncio
import asyncpg
from datetime import datetime
import logging
import os
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class StorageBackend:
    """Interface abstraite pour le stockage des événements"""
    async def initialize(self):
        """Initialise le backend de stockage"""
        pass
        
    async def close(self):
        """Ferme la connexion au backend de stockage"""
        pass
        
    async def store_batch(self, events: List[Dict[str, Any]]):
        """Stocke un lot d'événements"""
        raise NotImplementedError("Subclasses must implement store_batch")


class PostgresStorageBackend(StorageBackend):
    """Backend de stockage PostgreSQL pour les événements"""
    
    def __init__(self, dsn: Optional[str] = None, 
                 host: str = None, 
                 port: int = 5432, 
                 user: str = None, 
                 password: str = None, 
                 database: str = None,
                 schema: str = "tracking",
                 min_connections: int = 5,
                 max_connections: int = 20):
        """
        Initialise le backend de stockage PostgreSQL
        
        Utilise soit un DSN complet, soit les paramètres de connexion individuels.
        Si le DSN est fourni, il a priorité sur les autres paramètres.
        """
        self.dsn = dsn or os.environ.get("POSTGRES_DSN")
        self.host = host or os.environ.get("POSTGRES_HOST", "localhost")
        self.port = port or int(os.environ.get("POSTGRES_PORT", "5432"))
        self.user = user or os.environ.get("POSTGRES_USER", "postgres")
        self.password = password or os.environ.get("POSTGRES_PASSWORD", "")
        self.database = database or os.environ.get("POSTGRES_DB", "commitment")
        self.schema = schema
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.pool = None
        
    async def initialize(self):
        """Initialise le pool de connexions PostgreSQL"""
        if self.pool is not None:
            return
            
        connection_kwargs = {}
        if self.dsn:
            connection_kwargs["dsn"] = self.dsn
        else:
            connection_kwargs.update({
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "password": self.password,
                "database": self.database
            })
            
        try:
            self.pool = await asyncpg.create_pool(
                min_size=self.min_connections,
                max_size=self.max_connections,
                **connection_kwargs
            )
            logger.info(f"PostgreSQL connection pool initialized: {self.host}:{self.port}/{self.database}")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL connection pool: {str(e)}")
            raise
            
    async def close(self):
        """Ferme le pool de connexions PostgreSQL"""
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("PostgreSQL connection pool closed")
            
    @asynccontextmanager
    async def connection(self):
        """Contexte asynchrone pour obtenir une connexion du pool"""
        if not self.pool:
            await self.initialize()
            
        async with self.pool.acquire() as conn:
            yield conn
            
    async def store_batch(self, events: List[Dict[str, Any]]):
        """
        Stocke un lot d'événements dans PostgreSQL
        
        Utilise des transactions pour garantir l'atomicité et gère les différents
        types d'événements en stockant les données dans les tables appropriées.
        """
        if not events:
            return
            
        try:
            async with self.connection() as conn:
                # Démarrer une transaction
                async with conn.transaction():
                    # Insérer les événements de base
                    base_values = [(
                        event["event_id"],
                        event["user_id"],
                        event.get("session_id"),
                        event["event_type"],
                        event["timestamp"],
                        event.get("client_timestamp"),
                        event.get("ip_address"),
                        event.get("device_type"),
                        event.get("os_name"),
                        event.get("browser_name"),
                        event.get("app_version"),
                        event.get("referrer_url"),
                        event.get("user_agent"),
                        json.dumps(event.get("metadata", {}))
                    ) for event in events]
                    
                    await conn.executemany(
                        f"""
                        INSERT INTO {self.schema}.events (
                            event_id, user_id, session_id, event_type, event_timestamp,
                            client_timestamp, ip_address, device_type, os_name, browser_name,
                            app_version, referrer_url, user_agent, metadata
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                        ON CONFLICT (event_id) DO NOTHING
                        """,
                        base_values
                    )
                    
                    # Regrouper les événements par type
                    match_events = []
                    feedback_events = []
                    interaction_events = []
                    completion_events = []
                    
                    for event in events:
                        event_type = event["event_type"]
                        
                        # Match events (proposed, viewed, accepted, rejected)
                        if event_type in [
                            EventType.MATCH_PROPOSED.value, 
                            EventType.MATCH_VIEWED.value,
                            EventType.MATCH_ACCEPTED.value,
                            EventType.MATCH_REJECTED.value
                        ]:
                            match_events.append((
                                event["event_id"],
                                event.get("match_id"),
                                event.get("match_score"),
                                json.dumps(event.get("constraint_satisfaction", {})),
                                json.dumps(event.get("match_parameters", {})),
                                event.get("alternatives_count"),
                                event.get("view_duration_seconds"),
                                event.get("decision_time_seconds"),
                                event.get("reasons", [])
                            ))
                            
                        # Feedback events
                        elif event_type == EventType.MATCH_FEEDBACK.value:
                            feedback_events.append((
                                event["event_id"],
                                event.get("match_id"),
                                event.get("rating"),
                                event.get("feedback_text"),
                                json.dumps(event.get("specific_aspects", {}))
                            ))
                            
                        # Interaction events
                        elif event_type == EventType.MATCH_INTERACTION.value:
                            interaction_events.append((
                                event["event_id"],
                                event.get("match_id"),
                                event.get("interaction_type"),
                                event.get("interaction_count"),
                                json.dumps(event.get("details", {}))
                            ))
                            
                        # Completion events
                        elif event_type in [
                            EventType.MATCH_COMPLETED.value,
                            EventType.MATCH_ABANDONED.value
                        ]:
                            completion_events.append((
                                event["event_id"],
                                event.get("match_id"),
                                event.get("duration_days"),
                                event.get("completion_rate"),
                                json.dumps(event.get("success_indicators", {}))
                            ))
                    
                    # Insérer dans les tables spécifiques
                    if match_events:
                        await conn.executemany(
                            f"""
                            INSERT INTO {self.schema}.match_events (
                                event_id, match_id, match_score, constraint_satisfaction,
                                parameters, alternatives_count, view_duration_seconds,
                                decision_time_seconds, reasons
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                            ON CONFLICT (event_id) DO NOTHING
                            """,
                            match_events
                        )
                        
                    if feedback_events:
                        await conn.executemany(
                            f"""
                            INSERT INTO {self.schema}.feedback_events (
                                event_id, match_id, rating, feedback_text, specific_aspects
                            ) VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (event_id) DO NOTHING
                            """,
                            feedback_events
                        )
                        
                    if interaction_events:
                        await conn.executemany(
                            f"""
                            INSERT INTO {self.schema}.interaction_events (
                                event_id, match_id, interaction_type, interaction_count, details
                            ) VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (event_id) DO NOTHING
                            """,
                            interaction_events
                        )
                        
                    if completion_events:
                        await conn.executemany(
                            f"""
                            INSERT INTO {self.schema}.completion_events (
                                event_id, match_id, duration_days, completion_rate, success_indicators
                            ) VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (event_id) DO NOTHING
                            """,
                            completion_events
                        )
                    
                    # Mise à jour des métriques quotidiennes
                    # On utilise une requête unique qui gère l'insertion ou mise à jour
                    await conn.execute(
                        f"""
                        INSERT INTO {self.schema}.daily_metrics (
                            metric_date, 
                            total_matches,
                            viewed_matches,
                            accepted_matches,
                            rejected_matches,
                            updated_at
                        )
                        SELECT
                            CURRENT_DATE,
                            (SELECT COUNT(*) FROM {self.schema}.events WHERE event_type = 'match_proposed' AND event_timestamp::DATE = CURRENT_DATE),
                            (SELECT COUNT(*) FROM {self.schema}.events WHERE event_type = 'match_viewed' AND event_timestamp::DATE = CURRENT_DATE),
                            (SELECT COUNT(*) FROM {self.schema}.events WHERE event_type = 'match_accepted' AND event_timestamp::DATE = CURRENT_DATE),
                            (SELECT COUNT(*) FROM {self.schema}.events WHERE event_type = 'match_rejected' AND event_timestamp::DATE = CURRENT_DATE),
                            NOW()
                        ON CONFLICT (metric_date) DO UPDATE
                        SET
                            total_matches = (SELECT COUNT(*) FROM {self.schema}.events WHERE event_type = 'match_proposed' AND event_timestamp::DATE = CURRENT_DATE),
                            viewed_matches = (SELECT COUNT(*) FROM {self.schema}.events WHERE event_type = 'match_viewed' AND event_timestamp::DATE = CURRENT_DATE),
                            accepted_matches = (SELECT COUNT(*) FROM {self.schema}.events WHERE event_type = 'match_accepted' AND event_timestamp::DATE = CURRENT_DATE),
                            rejected_matches = (SELECT COUNT(*) FROM {self.schema}.events WHERE event_type = 'match_rejected' AND event_timestamp::DATE = CURRENT_DATE),
                            updated_at = NOW()
                        """
                    )
                    
            logger.info(f"Successfully stored batch of {len(events)} events in PostgreSQL")
            return True
        except Exception as e:
            logger.error(f"Failed to store event batch in PostgreSQL: {str(e)}")
            # En cas d'erreur, on pourrait implémenter une stratégie de retry ou de fallback
            # Par exemple, stocker les événements dans un fichier local pour les réessayer plus tard
            return False


class LoggingStorageBackend(StorageBackend):
    """Simple backend qui journalise les événements, utile pour le développement et le débogage"""
    
    def __init__(self, log_level=logging.INFO):
        self.log_level = log_level
        
    async def store_batch(self, events: List[Dict[str, Any]]):
        """Journalise les événements"""
        for event in events:
            logger.log(self.log_level, f"EVENT: {json.dumps(event)}")
        return True


class EventCollector:
    def __init__(self, privacy_manager: PrivacyManager, batch_size: int = 50, storage_backend: Optional[StorageBackend] = None):
        self.privacy_manager = privacy_manager
        self.event_queue = asyncio.Queue()
        self.batch_size = batch_size
        
        # Utilise le backend de stockage fourni ou crée un backend par défaut
        if storage_backend:
            self.storage_backend = storage_backend
        else:
            # Par défaut, on utilise PostgreSQL en production et le logging en développement
            if os.environ.get("ENVIRONMENT", "development") == "production":
                self.storage_backend = PostgresStorageBackend()
            else:
                self.storage_backend = LoggingStorageBackend()
        
        # Démarrer le worker de traitement
        self.worker_task = None
        
    async def start(self):
        """Démarre le collecteur d'événements et initialise le backend"""
        await self.storage_backend.initialize()
        self.worker_task = asyncio.create_task(self.process_events_worker())
        logger.info("Event collector started")
        
    async def stop(self):
        """Arrête le collecteur d'événements et ferme le backend"""
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        await self.storage_backend.close()
        logger.info("Event collector stopped")
        
    async def collect_event(self, event: BaseEvent) -> bool:
        """Collecte un événement si l'utilisateur a donné son consentement"""
        required_consent = {"analytics"}
        
        # Vérifier le consentement
        if not self.privacy_manager.has_valid_consent(event.user_id, required_consent):
            logger.warning(f"Event ignored - no consent for user_id: {event.user_id}")
            return False
            
        # Enrichir l'événement avec des métadonnées supplémentaires
        if hasattr(event, "metadata") and event.metadata is None:
            event.metadata = {}
        
        # Ajouter à la queue pour traitement
        await self.event_queue.put(event.dict())
        return True
    
    async def process_events_worker(self):
        """Worker qui traite les événements par lots"""
        while True:
            try:
                # Collecter un lot d'événements
                batch = []
                for _ in range(self.batch_size):
                    try:
                        event = await asyncio.wait_for(self.event_queue.get(), timeout=5.0)
                        batch.append(event)
                        self.event_queue.task_done()
                    except asyncio.TimeoutError:
                        break
                        
                if batch:
                    await self.store_events_batch(batch)
            except asyncio.CancelledError:
                # Gestion propre de l'arrêt du worker
                logger.info("Event processing worker stopped")
                raise
            except Exception as e:
                # Capture toutes les autres exceptions pour éviter que le worker ne s'arrête
                logger.error(f"Error in event processing worker: {str(e)}")
                # Attendre un peu avant de réessayer en cas d'erreur
                await asyncio.sleep(1)
                
    async def store_events_batch(self, events: List[Dict[str, Any]]):
        """Stocke un lot d'événements dans le backend"""
        # Filtrer les données sensibles avant stockage
        sanitized_events = []
        for event in events:
            # Filtrer les données sensibles avant stockage si nécessaire
            sanitized_event = self.privacy_manager.sanitize_event(event)
            sanitized_events.append(sanitized_event)
            
        # Stocker dans le backend
        await self.storage_backend.store_batch(sanitized_events)
