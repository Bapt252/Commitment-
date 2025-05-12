#!/bin/bash
set -e

# Fonction pour afficher des messages
log_message() {
  echo "[ENTRYPOINT] $1"
}

log_message "Démarrage du service job-parser..."

# Créer le fichier pydantic_compat.py si nécessaire
mkdir -p /app/app/core
COMPAT_FILE="/app/app/core/pydantic_compat.py"

if [ ! -f "$COMPAT_FILE" ]; then
  log_message "Création du fichier pydantic_compat.py..."
  cat > "$COMPAT_FILE" << 'EOL'
"""
Module de compatibilité pour Pydantic v1 et v2.
Permet d'utiliser le code avec les deux versions de Pydantic.
"""
import sys
import importlib.util
import logging

logger = logging.getLogger(__name__)

def is_pydantic_v2():
    """Vérifie si Pydantic v2 est installé"""
    import pydantic
    return pydantic.__version__.startswith('2')

# Classes et fonctions compatibles avec les deux versions
def get_base_settings():
    """Retourne la classe BaseSettings appropriée selon la version de Pydantic"""
    if is_pydantic_v2():
        try:
            from pydantic_settings import BaseSettings
            logger.info("Utilisation de BaseSettings depuis pydantic_settings (Pydantic v2)")
            return BaseSettings
        except ImportError:
            logger.warning("pydantic_settings non trouvé, utilisation de la classe BaseSettings de Pydantic v1")
            from pydantic import BaseSettings
            return BaseSettings
    else:
        from pydantic import BaseSettings
        logger.info("Utilisation de BaseSettings depuis pydantic (Pydantic v1)")
        return BaseSettings

# Exporter les classes et fonctions
BaseSettings = get_base_settings()
EOL
  log_message "Fichier pydantic_compat.py créé avec succès"
fi

# Vérifier si config.py existe
CONFIG_FILE="/app/app/core/config.py"
if [ ! -f "$CONFIG_FILE" ]; then
  log_message "ERREUR: Le fichier config.py n'existe pas!"
  exit 1
fi

# Remplacer le fichier config.py entier plutôt que de modifier avec sed
# Cela évite les problèmes d'indentation
log_message "Modification du fichier config.py pour utiliser pydantic_compat..."
cat > "$CONFIG_FILE" << 'EOL'
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
        from pydantic_settings import BaseSettings
        from pydantic import validator
    except ImportError:
        # Fallback direct pour les versions plus anciennes
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
EOL

# Vérifier si pydantic-settings est installé
log_message "Vérification de l'installation de pydantic-settings..."
pip install --no-cache-dir pydantic-settings>=2.0.0

# Exécuter le script de correction d'indentation pour s'assurer que tout est correct
if [ -f "/app/fix-indentation.sh" ]; then
  log_message "Exécution du script de correction d'indentation..."
  chmod +x /app/fix-indentation.sh
  /app/fix-indentation.sh
fi

# Activer le mode mock si pas de clé OpenAI
if [ -z "${OPENAI_API_KEY}" ] && [ -z "${OPENAI}" ]; then
    log_message "Aucune clé API OpenAI trouvée. Activation du mode simulation..."
    export USE_MOCK_PARSER=true
fi

# Exécuter la commande fournie
log_message "Exécution de la commande: $@"
exec "$@"
