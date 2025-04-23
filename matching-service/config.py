import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

class Config:
    """Configuration de base pour l'application."""
    # Configuration Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-not-for-production')
    DEBUG = False
    TESTING = False
    API_PREFIX = os.getenv('API_PREFIX', '/api')
    
    # Configuration JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-not-for-production')
    JWT_ACCESS_TOKEN_EXPIRES = 24 * 60 * 60  # 24 heures en secondes
    
    # Configuration PostgreSQL
    POSTGRES_USER = os.getenv('POSTGRES_USER', 'matching_service')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'matching_password')
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_DB = os.getenv('POSTGRES_DB', 'nexten')
    SQLALCHEMY_DATABASE_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuration Redis pour le cache et Celery
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = os.getenv('REDIS_PORT', '6379')
    REDIS_DB = os.getenv('REDIS_DB', '0')
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    
    # Configuration Celery
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
    
    # Configuration de la connexion à la base de données
    DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
    DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    DB_POOL_RECYCLE = int(os.getenv('DB_POOL_RECYCLE', '300'))
    
    # Configuration des limites d'API
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    RATELIMIT_STORAGE_URL = REDIS_URL
    
    # Configuration des services externes
    PROFILES_SERVICE_URL = os.getenv('PROFILES_SERVICE_URL', 'http://profiles-service:5000')
    JOBS_SERVICE_URL = os.getenv('JOBS_SERVICE_URL', 'http://jobs-service:5000')

class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')

class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/nexten_test'
    )

class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    RATELIMIT_DEFAULT = "1000 per day, 100 per hour"

# Dictionnaire des configurations
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}