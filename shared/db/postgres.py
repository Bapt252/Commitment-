import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import psycopg2
import psycopg2.extras

Base = declarative_base()

def get_db_url(service_name):
    """Construit l'URL de connexion PostgreSQL basée sur l'environnement et le service"""
    user = os.environ.get(f"{service_name.upper()}_DB_USER")
    password = os.environ.get(f"{service_name.upper()}_DB_PASSWORD")
    host = os.environ.get("DB_HOST", "postgres")
    port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "nexten")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

def setup_db_session(service_name, schema=None):
    """Configure la session de base de données pour un service spécifique"""
    engine = create_engine(
        get_db_url(service_name),
        pool_size=int(os.environ.get("DB_POOL_SIZE", "5")),
        max_overflow=int(os.environ.get("DB_MAX_OVERFLOW", "10")),
        pool_timeout=int(os.environ.get("DB_POOL_TIMEOUT", "30")),
        pool_recycle=int(os.environ.get("DB_POOL_RECYCLE", "300"))
    )
    session_factory = sessionmaker(bind=engine)
    session = scoped_session(session_factory)
    
    # Configuration du schéma PostgreSQL
    if schema:
        Base.metadata.schema = schema
        # Définir le schéma de recherche par défaut
        with engine.connect() as conn:
            conn.execute(f"SET search_path TO {schema}, public")
    
    return engine, session

@contextmanager
def session_scope(session):
    """Gestionnaire de contexte qui gère les sessions et les transactions"""
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def setup_audit_context(session, user_id, ip_address=None, app_user=None):
    """Configure le contexte d'audit pour enregistrer l'identité des modifications"""
    with session.begin():
        session.execute(
            "SELECT set_app_context(:user_id, :ip_address, :app_user)",
            {
                "user_id": str(user_id) if user_id else None,
                "ip_address": ip_address,
                "app_user": app_user or "api"
            }
        )

def get_connection(service_name):
    """Obtient une connexion psycopg2 directe pour les requêtes complexes"""
    user = os.environ.get(f"{service_name.upper()}_DB_USER")
    password = os.environ.get(f"{service_name.upper()}_DB_PASSWORD")
    host = os.environ.get("DB_HOST", "postgres")
    port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "nexten")
    
    conn = psycopg2.connect(
        dbname=db_name,
        user=user,
        password=password,
        host=host,
        port=port
    )
    
    # Configuration pour renvoyer des dictionnaires
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    
    return conn