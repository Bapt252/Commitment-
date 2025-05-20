"""
Service de traitement des événements en tâche de fond
"""

import asyncio
import logging
import os
import sys
import signal
import aioredis
import asyncpg
from tracking.processor import EventProcessor
from tracking.collector import PostgresStorageBackend

# Configuration des logs
logging.basicConfig(
    level=logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class ProcessorService:
    def __init__(self):
        self.db_pool = None
        self.redis = None
        self.processor = None
        self.storage_backend = None
        self.processing_interval = int(os.getenv("PROCESSING_INTERVAL", "30"))
        self.running = False
        
    async def initialize(self):
        """Initialiser les connexions et ressources"""
        # Connexion PostgreSQL
        try:
            self.db_pool = await asyncpg.create_pool(
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                port=int(os.environ.get("POSTGRES_PORT", "5432")),
                user=os.environ.get("POSTGRES_USER", "postgres"),
                password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
                database=os.environ.get("POSTGRES_DB", "commitment"),
                min_size=5,
                max_size=20
            )
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Error connecting to PostgreSQL: {str(e)}")
            raise
            
        # Connexion Redis
        try:
            redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
            self.redis = await aioredis.create_redis_pool(redis_url)
            logger.info(f"Connected to Redis at {redis_url}")
        except Exception as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            self.redis = None
            
        # Initialiser le backend de stockage
        self.storage_backend = PostgresStorageBackend(pool=self.db_pool)
        await self.storage_backend.initialize()
        
        # Initialiser le processeur d'événements
        self.processor = EventProcessor(
            storage_backend=self.storage_backend,
            processing_interval=self.processing_interval,
            redis_url=os.getenv("REDIS_URL", "redis://redis:6379")
        )
        await self.processor.initialize()
        
        logger.info("Processor service initialized")
        
    async def shutdown(self):
        """Fermer proprement les connexions"""
        if self.processor:
            await self.processor.close()
            
        if self.storage_backend:
            await self.storage_backend.close()
            
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            
        if self.db_pool:
            await self.db_pool.close()
            
        logger.info("Processor service shutdown complete")
        
    async def run(self):
        """Exécuter le service de traitement"""
        self.running = True
        
        # Configurer les gestionnaires de signaux
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
            
        try:
            logger.info("Starting processor worker...")
            await self.processor.processing_worker()
        except asyncio.CancelledError:
            logger.info("Processor worker cancelled")
        except Exception as e:
            logger.error(f"Error in processor worker: {str(e)}")
        finally:
            self.running = False
            
    async def stop(self):
        """Arrêter le service"""
        if self.running:
            logger.info("Stopping processor service...")
            self.running = False
            await self.shutdown()
            
async def main():
    """Point d'entrée principal"""
    service = ProcessorService()
    
    try:
        await service.initialize()
        await service.run()
    except Exception as e:
        logger.error(f"Fatal error in processor service: {str(e)}")
        await service.shutdown()
        sys.exit(1)
        
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
