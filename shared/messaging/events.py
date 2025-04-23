import json
import logging
import os
from typing import Dict, Any, Callable, List, Optional
import redis

class EventBus:
    """Bus d'événements pour la communication asynchrone entre services"""
    
    def __init__(self, service_name: str):
        """Initialise le bus d'événements.
        
        Args:
            service_name: Nom du service utilisant le bus
        """
        self.service_name = service_name
        self.redis_client = self._get_redis_client()
        self.logger = logging.getLogger(f"{service_name}.event_bus")
        self.handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def _get_redis_client(self) -> redis.Redis:
        """Obtient un client Redis pour la publication et la consommation d'événements."""
        host = os.environ.get("REDIS_HOST", "redis")
        port = int(os.environ.get("REDIS_PORT", "6379"))
        db = int(os.environ.get("REDIS_EVENTS_DB", "1"))  # DB différente du cache
        password = os.environ.get("REDIS_PASSWORD", None)
        
        return redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True
        )
    
    def publish(self, event_type: str, payload: Dict[str, Any], routing_key: Optional[str] = None) -> bool:
        """Publie un événement sur le bus.
        
        Args:
            event_type: Type d'événement (ex: 'user.created', 'job.updated')
            payload: Données associées à l'événement
            routing_key: Clé de routage optionnelle (ex: 'company.123')
            
        Returns:
            True si l'événement a été publié avec succès
        """
        try:
            # Préparation du message
            message = {
                "type": event_type,
                "service": self.service_name,
                "payload": payload,
                "timestamp": int(time.time())
            }
            
            # Canal de publication
            channel = f"events:{event_type}"
            if routing_key:
                channel = f"{channel}:{routing_key}"
            
            # Publication du message
            self.redis_client.publish(channel, json.dumps(message))
            
            # Log pour le debugging
            self.logger.debug(f"Published event {event_type} to {channel}")
            
            return True
        except Exception as e:
            self.logger.error(f"Error publishing event {event_type}: {str(e)}")
            return False
    
    def subscribe(self, event_type: str, handler: Callable[[Dict[str, Any]], None], routing_key: Optional[str] = None):
        """Inscrit un gestionnaire pour un type d'événement.
        
        Args:
            event_type: Type d'événement à écouter
            handler: Fonction à appeler quand l'événement est reçu
            routing_key: Clé de routage optionnelle pour filtrer les événements
        """
        # Définir le canal d'abonnement
        channel = f"events:{event_type}"
        if routing_key:
            channel = f"{channel}:{routing_key}"
        
        # Ajouter le gestionnaire à la liste des abonnés
        if channel not in self.handlers:
            self.handlers[channel] = []
        
        self.handlers[channel].append(handler)
        
        self.logger.debug(f"Subscribed to {channel}")
    
    def start_listening(self):
        """Démarre l'écoute des événements dans un thread séparé."""
        import threading
        listener_thread = threading.Thread(target=self._listen_for_events, daemon=True)
        listener_thread.start()
        self.logger.info("Event listener started")
        return listener_thread
    
    def _listen_for_events(self):
        """Méthode interne pour écouter les événements."""
        if not self.handlers:
            self.logger.warning("No event handlers registered, not starting listener")
            return
        
        pubsub = self.redis_client.pubsub()
        
        # S'abonner à tous les canaux enregistrés
        for channel in self.handlers.keys():
            pubsub.subscribe(channel)
        
        # Boucle d'écoute des événements
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    # Décoder le message
                    data = json.loads(message['data'])
                    channel = message['channel']
                    
                    # Appeler tous les gestionnaires pour ce canal
                    if channel in self.handlers:
                        for handler in self.handlers[channel]:
                            try:
                                handler(data)
                            except Exception as e:
                                self.logger.error(f"Error in event handler for {channel}: {str(e)}")
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON in message: {message['data']}")
                except Exception as e:
                    self.logger.error(f"Error processing message: {str(e)}")