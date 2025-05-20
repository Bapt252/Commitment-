from typing import Dict, List, Set, Optional, Any
import sqlite3
import json
import logging
from datetime import datetime
from .schema import BaseEvent, EventType
from .privacy import PrivacyManager

logger = logging.getLogger(__name__)

class EventCollector:
    def __init__(self, privacy_manager: PrivacyManager, db_path: str = 'data/tracking.db'):
        self.privacy_manager = privacy_manager
        self.db_path = db_path
    
    def collect_event(self, event: BaseEvent) -> bool:
        """Collecte un événement si l'utilisateur a donné son consentement"""
        required_consent = {"analytics"}
        
        # Vérifier le consentement
        if not self.privacy_manager.has_valid_consent(event.user_id, required_consent):
            logger.warning(f"Event ignored - no consent for user_id: {event.user_id}")
            return False
            
        # Anonymiser l'ID utilisateur si nécessaire
        anon_user_id = self.privacy_manager.anonymize_user_id(event.user_id, "secret_salt_key")
        event.user_id = anon_user_id
            
        # Enregistrer l'événement dans la base de données
        try:
            self._store_event(event)
            return True
        except Exception as e:
            logger.error(f"Failed to store event: {str(e)}")
            return False
    
    def _store_event(self, event: BaseEvent):
        """Stocke un événement dans la base de données SQLite"""
        event_dict = event.to_dict()
        match_id = event_dict.get("match_id")
        
        # Extraire les champs communs
        data = {k: v for k, v in event_dict.items() 
                if k not in ["event_id", "user_id", "timestamp", "event_type", "session_id", "match_id"]}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO events (event_id, user_id, event_type, timestamp, session_id, match_id, data) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (event_dict["event_id"], event_dict["user_id"], event_dict["event_type"], 
                 event_dict["timestamp"], event_dict["session_id"], match_id, json.dumps(data))
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()