"""
Utilitaires pour la gestion de la base de données.
"""
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configuration du moteur SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycler les connexions après 1 heure
    pool_size=10,       # Taille du pool de connexions
    max_overflow=20     # Nombre maximum de connexions supplémentaires
)

# Session locale pour les workers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles SQLAlchemy
Base = declarative_base()

def init_db():
    """Initialise la base de données et crée les tables si nécessaire"""
    try:
        # Import ici pour éviter les imports circulaires
        from app.models.matching import Base
        
        # Création des tables
        Base.metadata.create_all(bind=engine)
        logger.info("Base de données initialisée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        raise

def get_db():
    """
    Dépendance pour obtenir une session de base de données dans FastAPI
    À utiliser avec Depends() dans les routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """
    Context manager pour obtenir une session de base de données
    À utiliser avec with get_db_session() as db:
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de l'utilisation de la session DB: {str(e)}")
        raise
    finally:
        db.close()
