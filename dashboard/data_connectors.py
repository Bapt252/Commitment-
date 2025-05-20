from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
import json

logger = logging.getLogger(__name__)

class DataConnector:
    def __init__(self, db_config: Dict[str, Any] = None):
        self.db_config = db_config or {}
        self.connection = None
        
    async def connect(self):
        """Connecte au backend de stockage"""
        # À implémenter selon le backend choisi (PostgreSQL, MongoDB, etc.)
        pass
        
    async def disconnect(self):
        """Déconnecte du backend de stockage"""
        # À implémenter selon le backend choisi
        pass
    
    async def count_events(self, event_type: str, since: datetime = None) -> int:
        """Compte le nombre d'événements d'un type spécifique depuis une date"""
        # À implémenter selon le backend choisi
        return 0
        
    async def get_events(self, event_type: str, since: datetime = None, limit: int = 1000) -> List[Dict]:
        """Récupère les événements d'un type spécifique depuis une date"""
        # À implémenter selon le backend choisi
        return []
        
    async def get_accepted_match_ids(self, since: datetime = None) -> List[str]:
        """Récupère les IDs des matchs acceptés depuis une date"""
        # À implémenter selon le backend choisi
        return []
        
    async def get_match_details(self, match_id: str) -> Dict[str, Any]:
        """Récupère les détails d'un match spécifique"""
        # À implémenter selon le backend choisi
        return {}
        
    async def get_user_activity(self, user_id: str, since: datetime = None) -> List[Dict]:
        """Récupère l'activité d'un utilisateur spécifique depuis une date"""
        # À implémenter selon le backend choisi
        return []
        
    async def get_events_by_date_range(self, event_type: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Récupère les événements d'un type spécifique dans une plage de dates"""
        # À implémenter selon le backend choisi
        return []
        
    async def get_aggregate_stats(self, event_type: str, groupby: str, since: datetime = None) -> Dict[str, int]:
        """Récupère des statistiques agrégées pour un type d'événement"""
        # À implémenter selon le backend choisi
        return {}

# Exemple d'implémentation pour PostgreSQL
class PostgreSQLConnector(DataConnector):
    async def connect(self):
        try:
            import asyncpg
            self.connection = await asyncpg.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5432),
                user=self.db_config.get('user', 'postgres'),
                password=self.db_config.get('password', ''),
                database=self.db_config.get('database', 'commitment')
            )
            logger.info(f"Connected to PostgreSQL database {self.db_config.get('database')}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            return False
            
    async def disconnect(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            
    async def count_events(self, event_type: str, since: datetime = None) -> int:
        if not self.connection:
            await self.connect()
            
        query = "SELECT COUNT(*) FROM events WHERE event_type = $1"
        params = [event_type]
        
        if since:
            query += " AND timestamp >= $2"
            params.append(since)
            
        try:
            count = await self.connection.fetchval(query, *params)
            return count
        except Exception as e:
            logger.error(f"Error counting events: {str(e)}")
            return 0
            
    async def get_events(self, event_type: str, since: datetime = None, limit: int = 1000) -> List[Dict]:
        if not self.connection:
            await self.connect()
            
        query = "SELECT * FROM events WHERE event_type = $1"
        params = [event_type]
        
        if since:
            query += " AND timestamp >= $2"
            params.append(since)
            
        query += f" ORDER BY timestamp DESC LIMIT ${len(params) + 1}"
        params.append(limit)
        
        try:
            rows = await self.connection.fetch(query, *params)
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}")
            return []
            
    async def get_accepted_match_ids(self, since: datetime = None) -> List[str]:
        if not self.connection:
            await self.connect()
            
        query = "SELECT match_id FROM events WHERE event_type = 'match_accepted'"
        params = []
        
        if since:
            query += " AND timestamp >= $1"
            params.append(since)
            
        try:
            rows = await self.connection.fetch(query, *params)
            return [row['match_id'] for row in rows]
        except Exception as e:
            logger.error(f"Error fetching accepted match IDs: {str(e)}")
            return []

# Exemple d'implémentation pour MongoDB
class MongoDBConnector(DataConnector):
    async def connect(self):
        try:
            import motor.motor_asyncio
            client = motor.motor_asyncio.AsyncIOMotorClient(
                self.db_config.get('connection_string', 'mongodb://localhost:27017')
            )
            db_name = self.db_config.get('database', 'commitment')
            self.connection = client[db_name]
            logger.info(f"Connected to MongoDB database {db_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
            
    async def count_events(self, event_type: str, since: datetime = None) -> int:
        if not self.connection:
            await self.connect()
            
        collection = self.connection.events
        query = {"event_type": event_type}
        
        if since:
            query["timestamp"] = {"$gte": since}
            
        try:
            count = await collection.count_documents(query)
            return count
        except Exception as e:
            logger.error(f"Error counting events: {str(e)}")
            return 0
            
    async def get_events(self, event_type: str, since: datetime = None, limit: int = 1000) -> List[Dict]:
        if not self.connection:
            await self.connect()
            
        collection = self.connection.events
        query = {"event_type": event_type}
        
        if since:
            query["timestamp"] = {"$gte": since}
            
        try:
            cursor = collection.find(query).sort("timestamp", -1).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error fetching events: {str(e)}")
            return []
            
    async def get_accepted_match_ids(self, since: datetime = None) -> List[str]:
        if not self.connection:
            await self.connect()
            
        collection = self.connection.events
        query = {"event_type": "match_accepted"}
        
        if since:
            query["timestamp"] = {"$gte": since}
            
        try:
            cursor = collection.find(query, {"match_id": 1, "_id": 0})
            documents = await cursor.to_list(length=None)
            return [doc["match_id"] for doc in documents]
        except Exception as e:
            logger.error(f"Error fetching accepted match IDs: {str(e)}")
            return []