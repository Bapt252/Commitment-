"""
Configuration centrale pour le service de parsing de fiches de poste.
"""
import os
import logging
from typing import Any, Dict, Optional

# Utilisation du module de compatibilité pour Pydantic v1 et v2
try:
    # Essayer avec la version locale
    from app.core.pydantic_compat import BaseSettings
    from pydantic import validator
except ImportError:
    try:
        # Essayer avec le module à la racine
        from pydantic_compat import BaseSettings
        from pydantic import validator
    except ImportError:
        # Fallback direct pour les versions plus anciennes
        try:
            from pydantic_settings import BaseSettings
            from pydantic import validator
        except ImportError:
            from pydantic import BaseSettings, validator

class Settings(BaseSettings):
    """Paramètres de configuration du service"""
    
    # API Keys et configurations externes
    OPENAI_API_KEY: Optional[str] = os.environ.get('OPENAI_API_KEY') or os.environ.get('OPENAI')
    OPENAI_MODEL: str = os.environ.get('OPENAI_MODEL') or 'gpt-4o-mini'
    
    # Configuration Redis (pour les files d'attente)
    REDIS_HOST: str = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT: int = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB: int = int(os.environ.get('REDIS_DB') or 0)
    REDIS_PASSWORD: Optional[str] = os.environ.get('REDIS_PASSWORD')
    
    # Configuration MinIO (pour le stockage de fichiers)
    MINIO_ENDPOINT: str = os.environ.get('MINIO_ENDPOINT') or 'localhost:9000'
    MINIO_ACCESS_KEY: str = os.environ.get('MINIO_ACCESS_KEY') or 'minioadmin'
    MINIO_SECRET_KEY: str = os.environ.get('MINIO_SECRET_KEY') or 'minioadmin'
    MINIO_SECURE: bool = os.environ.get('MINIO_SECURE', '').lower() == 'true'
    
    # Configuration de l'API
    API_V1_STR: str = "/api"
    SERVICE_NAME: str = "job-parser-service"
    
    # Configuration du service
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
    
    # Mode de simulation/test
    USE_MOCK_PARSER: bool = os.environ.get('USE_MOCK_PARSER', '').lower() == 'true'
    
    # Validation des paramètres
    @validator('OPENAI_API_KEY')
    def validate_openai_api_key(cls, v, values, **kwargs):
        """Valide la clé API OpenAI"""
        if not v and not values.get('USE_MOCK_PARSER'):
            logging.warning("Aucune clé API OpenAI n'a été fournie. Le service utilisera le mode de simulation par défaut.")
            values['USE_MOCK_PARSER'] = True
        return v
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Créer une instance des paramètres
settings = Settings()

# Si aucune clé API n'est définie et que le mode mock n'est pas explicitement activé, 
# activer le mode mock automatiquement
if not settings.OPENAI_API_KEY and not settings.USE_MOCK_PARSER:
    logging.warning("Aucune clé API OpenAI trouvée. Activation automatique du mode de simulation (mock).")
    settings.USE_MOCK_PARSER = True
