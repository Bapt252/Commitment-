#!/bin/bash

# Script pour ajouter l'attribut USE_MINIO_FOR_FILES à la configuration

# Fonction pour afficher des messages avec couleurs
log_info() {
  echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
  echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_error() {
  echo -e "\033[0;31m[ERROR]\033[0m $1"
}

log_title() {
  echo -e "\n\033[1;36m=== $1 ===\033[0m\n"
}

# Arrêter le conteneur existant
log_title "ARRÊT DU CONTENEUR"
log_info "Arrêt du conteneur job-parser..."
docker-compose stop job-parser
docker-compose rm -f job-parser

# Mettre à jour le fichier config.py
log_title "MISE À JOUR DE LA CONFIGURATION"
log_info "Mise à jour du fichier config.py avec l'attribut USE_MINIO_FOR_FILES..."

# Créer un nouveau fichier config.py complet
cat > ./job-parser-service/app/core/config.py << 'EOL'
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
    USE_MINIO_FOR_FILES: bool = os.environ.get('USE_MINIO_FOR_FILES', 'true').lower() == 'true'
    
    # Configuration de l'API
    API_V1_STR: str = "/api"
    SERVICE_NAME: str = "job-parser-service"
    
    # Configuration du service
    UPLOAD_FOLDER: str = "uploads"
    MAX_CONTENT_LENGTH: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
    
    # Configuration de journalisation
    LOG_DIR: str = os.environ.get('LOG_DIR') or 'logs'
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FORMAT: str = os.environ.get('LOG_FORMAT') or 'text'  # 'text' ou 'json'
    
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

log_success "Fichier config.py mis à jour avec l'attribut USE_MINIO_FOR_FILES."

# Mettre à jour le script d'initialisation
log_title "MISE À JOUR DU SCRIPT D'INITIALISATION"
log_info "Création d'un script d'initialisation amélioré..."

cat > ./job-parser-service/init_container.sh << 'EOL'
#!/bin/bash
set -e

echo "[CONTAINER_INIT] Démarrage de l'initialisation du conteneur..."

# Créer les répertoires nécessaires
mkdir -p /app/logs /app/uploads
chmod 777 /app/logs /app/uploads

echo "[CONTAINER_INIT] Répertoires créés avec succès"

# Vérifier si pydantic-settings est installé
echo "[CONTAINER_INIT] Installation de pydantic-settings..."
pip install --no-cache-dir pydantic-settings>=2.0.0

# Vérifier la présence des attributs essentiels
echo "[CONTAINER_INIT] Vérification des attributs essentiels..."
python - << 'PYTHON_SCRIPT'
import sys
sys.path.append('/app')
try:
    from app.core.config import settings
    missing_attrs = []
    essential_attrs = ['LOG_DIR', 'USE_MINIO_FOR_FILES']
    
    for attr in essential_attrs:
        if not hasattr(settings, attr):
            missing_attrs.append(attr)
    
    if missing_attrs:
        print(f"ATTENTION: Attributs manquants dans settings: {', '.join(missing_attrs)}")
        
        # Ajouter les attributs manquants dynamiquement
        if 'LOG_DIR' not in missing_attrs:
            print("LOG_DIR est présent")
        else:
            setattr(settings, 'LOG_DIR', 'logs')
            print("LOG_DIR a été ajouté dynamiquement")
            
        if 'USE_MINIO_FOR_FILES' not in missing_attrs:
            print("USE_MINIO_FOR_FILES est présent")
        else:
            setattr(settings, 'USE_MINIO_FOR_FILES', True)
            print("USE_MINIO_FOR_FILES a été ajouté dynamiquement")
    else:
        print("Tous les attributs essentiels sont présents")
    
    # Vérifier que tout est bien configuré
    print(f"LOG_DIR = {settings.LOG_DIR}")
    print(f"USE_MINIO_FOR_FILES = {settings.USE_MINIO_FOR_FILES}")
    
except Exception as e:
    print(f"Erreur lors de la vérification: {e}")
    sys.exit(1)
PYTHON_SCRIPT

echo "[CONTAINER_INIT] Initialisation terminée, démarrage de l'application..."
exec "$@"
EOL

log_info "Rendre le script d'initialisation exécutable..."
chmod +x ./job-parser-service/init_container.sh

# Mettre à jour le Dockerfile
log_title "MISE À JOUR DU DOCKERFILE"
log_info "Modification du Dockerfile..."

cat > ./job-parser-service/Dockerfile.simple << 'EOL'
FROM python:3.11-slim

# Dépendances runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    curl \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pydantic-settings>=2.0.0

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs /app/uploads && \
    chmod 777 /app/logs /app/uploads

# Copier le script d'initialisation
COPY init_container.sh /init_container.sh
RUN chmod +x /init_container.sh

# Copier le code
COPY . .

# Exposer le port
EXPOSE 5000

# Démarrer l'application
ENTRYPOINT ["/init_container.sh"]
CMD ["python", "main.py"]
EOL

# Reconstruire l'image
log_title "RECONSTRUCTION DE L'IMAGE"
log_info "Reconstruction de l'image job-parser..."
docker-compose build job-parser

# Démarrer le service
log_title "DÉMARRAGE DU SERVICE"
log_info "Démarrage du service job-parser..."
docker-compose up -d job-parser

# Attendre que le service démarre
log_info "Attente du démarrage du service..."
sleep 10

# Vérifier l'état du service
log_title "VÉRIFICATION DU SERVICE"
log_info "Vérification de l'état du service..."
docker-compose ps job-parser

# Afficher les logs
log_info "Affichage des logs du service..."
docker-compose logs --tail=20 job-parser

# Vérifier l'accessibilité du service
log_info "Vérification de l'accessibilité du service..."
curl -s -I http://localhost:5053/health || echo "Le service n'est pas encore accessible."

log_success "Processus de correction terminé."
