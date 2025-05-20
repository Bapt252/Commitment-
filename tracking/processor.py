from typing import Dict, List, Any, Optional
from .schema import BaseEvent, EventType
import json
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class EventProcessor:
    def __init__(self, storage_backend=None, processing_interval: int = 60):
        self.storage_backend = storage_backend
        self.processing_interval = processing_interval
        self.event_handlers = {}
        self.register_default_handlers()
        
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
        
    async def handle_match_proposed(self, event):
        """Traite un événement de proposition de match"""
        # Logique spécifique pour les propositions de match
        pass
        
    async def handle_match_viewed(self, event):
        """Traite un événement de visualisation de match"""
        # Logique spécifique pour les visualisations de match
        pass
        
    async def handle_match_accepted(self, event):
        """Traite un événement d'acceptation de match"""
        # Logique spécifique pour les acceptations de match
        pass
        
    async def handle_match_rejected(self, event):
        """Traite un événement de rejet de match"""
        # Logique spécifique pour les rejets de match
        pass
        
    async def handle_match_feedback(self, event):
        """Traite un événement de feedback sur un match"""
        # Logique spécifique pour les feedbacks de match
        pass
        
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
                if self.storage_backend:
                    events = await self.storage_backend.get_unprocessed_events()
                    if events:
                        await self.process_events(events)
                        await self.storage_backend.mark_events_processed([e.event_id for e in events])
            except Exception as e:
                logger.error(f"Error in processing worker: {str(e)}")
                
            # Attendre avant la prochaine exécution
            await asyncio.sleep(self.processing_interval)