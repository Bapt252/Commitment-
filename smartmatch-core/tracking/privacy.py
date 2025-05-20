from typing import Dict, List, Set, Optional
import hashlib
import json
from datetime import datetime, timedelta
import sqlite3
import logging

logger = logging.getLogger(__name__)

class ConsentOptions:
    def __init__(self, analytics: bool = False, preferences: bool = False, improvement: bool = False):
        self.analytics = analytics  # Consentement pour l'analyse des performances
        self.preferences = preferences  # Consentement pour stocker les préférences
        self.improvement = improvement  # Consentement pour amélioration du produit
    
    def to_dict(self):
        return {
            "analytics": self.analytics,
            "preferences": self.preferences,
            "improvement": self.improvement
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            analytics=data.get("analytics", False),
            preferences=data.get("preferences", False),
            improvement=data.get("improvement", False)
        )

class PrivacyManager:
    def __init__(self, retention_days: int = 90, db_path: str = 'data/tracking.db'):
        self.retention_days = retention_days
        self.db_path = db_path
        self.consent_cache = {}  # Cache en mémoire pour les consentements
        
    def anonymize_user_id(self, real_id: str, salt: str) -> str:
        """Anonymisation irréversible de l'ID utilisateur avec un sel"""
        return hashlib.sha256(f"{real_id}:{salt}".encode()).hexdigest()
    
    def has_valid_consent(self, user_id: str, required_consent: Set[str]) -> bool:
        """Vérifie si l'utilisateur a donné son consentement pour les options requises"""
        # Vérifier d'abord dans le cache
        if user_id in self.consent_cache:
            consent = self.consent_cache[user_id]
        else:
            # Sinon, vérifier dans la base de données
            consent = self._get_consent_from_db(user_id)
            if consent:
                self.consent_cache[user_id] = consent
        
        if not consent:
            return False
            
        # Vérifier les consentements requis
        for option in required_consent:
            if not getattr(consent, option, False):
                return False
        return True
    
    def record_consent(self, user_id: str, options: ConsentOptions, ip_hash: Optional[str] = None) -> str:
        """Enregistre le consentement utilisateur"""
        import uuid
        
        consent_id = str(uuid.uuid4())
        
        # Mettre à jour le cache
        self.consent_cache[user_id] = options
        
        # Enregistrer dans la base de données
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO consents (consent_id, user_id, analytics, preferences, improvement, ip_hash) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (consent_id, user_id, int(options.analytics), int(options.preferences), 
                 int(options.improvement), ip_hash)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to record consent: {str(e)}")
            raise e
        finally:
            conn.close()
            
        return consent_id
    
    def _get_consent_from_db(self, user_id: str) -> Optional[ConsentOptions]:
        """Récupère le consentement depuis la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT analytics, preferences, improvement FROM consents "
                "WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1",
                (user_id,)
            )
            result = cursor.fetchone()
            
            if result:
                return ConsentOptions(
                    analytics=bool(result[0]),
                    preferences=bool(result[1]),
                    improvement=bool(result[2])
                )
            return None
        except Exception as e:
            logger.error(f"Error getting consent: {str(e)}")
            return None
        finally:
            conn.close()
    
    def clean_expired_data(self):
        """Supprime les données plus anciennes que la période de rétention"""
        cutoff_date = (datetime.utcnow() - timedelta(days=self.retention_days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Supprimer les événements expirés
            cursor.execute(
                "DELETE FROM events WHERE timestamp < ?",
                (cutoff_date,)
            )
            
            # Garder uniquement le consentement le plus récent par utilisateur
            # (Cette requête est plus complexe et dépend du support SQL de SQLite)
            # Cette logique pourrait être implémentée différemment si nécessaire
            
            conn.commit()
            logger.info(f"Cleaned up {cursor.rowcount} expired data records")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to clean expired data: {str(e)}")
        finally:
            conn.close()