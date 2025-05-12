#!/bin/bash

# Script pour inspecter et corriger en profondeur le service job-parser

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

# Vérifier si le conteneur existe, sinon le démarrer
if ! docker ps -a | grep -q nexten-job-parser; then
  log_info "Le conteneur nexten-job-parser n'existe pas."
  log_info "Démarrage du service job-parser..."
  docker-compose up -d job-parser
  sleep 3
fi

# Redémarrer le conteneur s'il est arrêté
if ! docker ps | grep -q nexten-job-parser; then
  log_info "Le conteneur nexten-job-parser est arrêté."
  log_info "Démarrage du conteneur..."
  docker-compose start job-parser
  sleep 3
fi

log_title "INSPECTION DU CONTENEUR"

# Vérifier l'existence du répertoire de logs
log_info "Vérification du répertoire de logs..."
docker exec nexten-job-parser bash -c 'mkdir -p /app/logs && chmod 777 /app/logs && echo "Répertoire logs: $(ls -la /app | grep logs)"'

# Examiner le fichier config.py
log_info "Examen du fichier config.py..."
docker exec nexten-job-parser bash -c 'cat /app/app/core/config.py'

# Créer un fichier de remplacement complet pour config.py
log_title "CRÉATION D'UN NOUVEAU FICHIER CONFIG.PY"
log_info "Préparation d'un nouveau fichier config.py..."

cat > /tmp/new_config.py << 'EOL'
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

# Remplacer complètement le fichier config.py
log_info "Remplacement complet du fichier config.py..."
docker cp /tmp/new_config.py nexten-job-parser:/app/app/core/config.py

# Examiner le fichier logging.py
log_title "EXAMEN DU FICHIER LOGGING.PY"
log_info "Inspection du fichier logging.py..."
docker exec nexten-job-parser bash -c 'cat /app/app/core/logging.py'

# Créer un patch pour la journalisation
log_title "CRÉATION D'UNE SOLUTION DE CONTOURNEMENT"
log_info "Création d'un script de patch pour la journalisation..."

cat > /tmp/patch_logging.py << 'EOL'
import os
import sys
import logging

# Ajouter les attributs manquants directement aux settings
try:
    from app.core.config import settings
    if not hasattr(settings, 'LOG_DIR'):
        setattr(settings, 'LOG_DIR', 'logs')
    if not hasattr(settings, 'LOG_LEVEL'):
        setattr(settings, 'LOG_LEVEL', 'INFO')
    if not hasattr(settings, 'LOG_FORMAT'):
        setattr(settings, 'LOG_FORMAT', 'text')
    
    # Créer le répertoire de logs
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # Configurer un logger de base
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(settings.LOG_DIR, f"{settings.SERVICE_NAME}.log"))
        ]
    )
    
    print("Patch de journalisation appliqué avec succès")
except Exception as e:
    print(f"Erreur lors de l'application du patch: {e}")
EOL

# Copier et exécuter le script de patch
log_info "Exécution du script de patch..."
docker cp /tmp/patch_logging.py nexten-job-parser:/app/patch_logging.py
docker exec nexten-job-parser bash -c 'cd /app && python patch_logging.py'

# Créer un script d'initialisation pour le service
log_title "CRÉATION D'UN SCRIPT D'INITIALISATION"
log_info "Préparation d'un script d'initialisation..."

cat > /tmp/init_service.sh << 'EOL'
#!/bin/bash

# Créer le répertoire logs s'il n'existe pas
mkdir -p /app/logs
chmod 777 /app/logs

# Vérifier si les attributs de journalisation sont présents dans config.py
if ! grep -q "LOG_DIR" /app/app/core/config.py; then
  echo "Ajout des attributs de journalisation à config.py..."
  cat >> /app/app/core/config.py << 'INNER'

# Configuration de journalisation
LOG_DIR: str = os.environ.get('LOG_DIR') or 'logs'
LOG_LEVEL: str = os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FORMAT: str = os.environ.get('LOG_FORMAT') or 'text'  # 'text' ou 'json'
INNER
fi

# Appliquer le patch de journalisation
cd /app && python patch_logging.py

echo "Initialisation terminée, lancement du service..."
exec "$@"
EOL

# Copier le script d'initialisation
log_info "Copie du script d'initialisation..."
docker cp /tmp/init_service.sh nexten-job-parser:/app/init_service.sh
docker exec nexten-job-parser bash -c 'chmod +x /app/init_service.sh'

# Redémarrer le service avec le script d'initialisation
log_title "REDÉMARRAGE DU SERVICE"
log_info "Arrêt du service..."
docker-compose stop job-parser

log_info "Redémarrage avec le script d'initialisation..."
docker run --rm --network=commitment-_default -p 5053:5000 --name nexten-job-parser-fixed -v $(pwd)/job-parser-service:/app commitment--job-parser:latest /app/init_service.sh python main.py &

# Attendre que le service démarre
log_info "Attente du démarrage du service..."
sleep 10

# Tester le service avec curl
log_title "TEST DU SERVICE"
log_info "Création d'un fichier de test..."
echo "Titre: Développeur Python" > /tmp/test_job.txt

log_info "Test du service avec curl..."
curl -v -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/tmp/test_job.txt" \
  -F "force_refresh=false"

# Nettoyage
log_title "NETTOYAGE"
log_info "Nettoyage des fichiers temporaires..."
rm /tmp/new_config.py /tmp/patch_logging.py /tmp/init_service.sh /tmp/test_job.txt

log_success "Opération terminée."
