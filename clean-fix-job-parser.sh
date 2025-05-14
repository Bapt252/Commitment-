#!/bin/bash

# Script pour reconstruire complètement le service job-parser de zéro

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

# Arrêter et supprimer tous les conteneurs liés au job-parser
log_title "NETTOYAGE DES CONTENEURS"
log_info "Arrêt et suppression des conteneurs existants..."
docker-compose stop job-parser
docker-compose rm -f job-parser
docker ps -a | grep job-parser | awk '{print $1}' | xargs -r docker rm -f

# Nettoyer les images
log_title "NETTOYAGE DES IMAGES"
log_info "Suppression des images job-parser existantes..."
docker images | grep job-parser | awk '{print $3}' | xargs -r docker rmi -f
docker images | grep commitment--job-parser | awk '{print $3}' | xargs -r docker rmi -f

# Recréer le fichier config.py avec les paramètres de journalisation
log_title "MODIFICATION DES FICHIERS SOURCE"
log_info "Création d'un fichier config.py complet..."

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

# Créer un script d'initialisation dans le conteneur
log_info "Création d'un script d'initialisation..."

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

echo "[CONTAINER_INIT] Vérification du fichier config.py..."
cat /app/app/core/config.py | grep LOG_DIR || echo "ERREUR: LOG_DIR non trouvé dans config.py"

echo "[CONTAINER_INIT] Initialisation terminée, démarrage de l'application..."
exec "$@"
EOL

log_info "Rendre le script d'initialisation exécutable..."
chmod +x ./job-parser-service/init_container.sh

# Mettre à jour le Dockerfile.simple
log_title "MISE À JOUR DU DOCKERFILE"
log_info "Création d'un nouveau Dockerfile..."

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

# Vérifier la présence de LOG_DIR dans config.py
RUN grep -q "LOG_DIR" /app/app/core/config.py || echo "AVERTISSEMENT: LOG_DIR non trouvé dans config.py"

# Port exposé
EXPOSE 5000

# Exécuter le script d'initialisation
ENTRYPOINT ["/init_container.sh"]
CMD ["python", "main.py"]
EOL

# Reconstruire le service
log_title "RECONSTRUCTION DU SERVICE"
log_info "Reconstruction du service job-parser..."
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
log_info "Vérification du statut du service..."
docker-compose ps

# Afficher les logs
log_info "Affichage des logs du service..."
docker-compose logs job-parser

# Créer un fichier de test simple
log_title "TEST DU SERVICE"
log_info "Création d'un fichier de test simple..."
echo "Titre: Développeur Python" > simple-job.txt

# Tester le service
log_info "Test du service avec curl..."
curl -v -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@simple-job.txt" \
  -F "force_refresh=false"

# Nettoyage
log_info "Nettoyage..."
rm simple-job.txt

log_success "Opération terminée."
