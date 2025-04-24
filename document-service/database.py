from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
from loguru import logger
from contextlib import contextmanager

# Création de l'URL de connexion
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Création du moteur avec les options pour PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Vérifie la connexion avant utilisation
    pool_size=10,        # Taille du pool de connexion
    max_overflow=20,     # Nombre max de connexions supplémentaires
    echo=settings.DEBUG  # Activer les logs SQL en mode debug
)

# Création de la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """
    Gère le cycle de vie d'une session de base de données
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Version contextmanager de get_db pour utilisation dans des workers ou scripts
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()


def init_db():
    """
    Initialise la base de données avec les tables nécessaires
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def check_db_connection():
    """
    Vérifie la connexion à la base de données
    """
    try:
        with get_db_context() as db:
            db.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False
