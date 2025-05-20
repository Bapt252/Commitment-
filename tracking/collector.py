from typing import Dict, Any, Optional, List
from .schema import BaseEvent, EventType
from .privacy import PrivacyManager
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EventCollector:
    def __init__(self, privacy_manager: PrivacyManager, batch_size: int = 50):
        self.privacy_manager = privacy_manager
        self.event_queue = asyncio.Queue()
        self.batch_size = batch_size
        self.storage_backend = None  # À configurer (DB, fichier, etc.)
        
    async def collect_event(self, event: BaseEvent) -> bool:
        """Collecte un événement si l'utilisateur a donné son consentement"""
        required_consent = {"analytics"}
        
        # Vérifier le consentement
        if not self.privacy_manager.has_valid_consent(event.user_id, required_consent):
            logger.warning(f"Event ignored - no consent for user_id: {event.user_id}")
            return False
            
        # Ajouter à la queue pour traitement
        await self.event_queue.put(event)
        return True
    
    async def process_events_worker(self):
        """Worker qui traite les événements par lots"""
        while True:
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
                
    async def store_events_batch(self, events: List[BaseEvent]):
        """Stocke un lot d'événements dans le backend"""
        # Filtrer les données sensibles avant stockage
        sanitized_events = []
        for event in events:
            # Convertir en dict et supprimer/anonymiser les champs sensibles
            event_dict = event.dict()
            # Logique d'anonymisation supplémentaire si nécessaire...
            sanitized_events.append(event_dict)
            
        # Stocker dans le backend
        if self.storage_backend:
            try:
                await self.storage_backend.store_batch(sanitized_events)
            except Exception as e:
                logger.error(f"Failed to store events batch: {str(e)}")