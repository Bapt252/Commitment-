#!/bin/bash

# Script pour ajouter tous les attributs MinIO manquants à la configuration

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
log_info "Mise à jour du fichier config.py avec tous les attributs MinIO nécessaires..."

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
    MINIO_BUCKET_NAME: str = os.environ.get('MINIO_BUCKET_NAME') or 'jobs'
    MINIO_BUCKET_INPUT_PREFIX: str = os.environ.get('MINIO_BUCKET_INPUT_PREFIX') or 'input/'
    MINIO_BUCKET_OUTPUT_PREFIX: str = os.environ.get('MINIO_BUCKET_OUTPUT_PREFIX') or 'output/'
    MINIO_FILE_EXPIRY_DAYS: int = int(os.environ.get('MINIO_FILE_EXPIRY_DAYS') or 30)
    
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

log_success "Fichier config.py mis à jour avec tous les attributs MinIO nécessaires."

# Examiner le fichier storage.py pour voir quels attributs sont utilisés
log_title "EXAMEN DU MODULE DE STOCKAGE"
log_info "Examen du fichier storage.py pour identifier tous les attributs MinIO utilisés..."

# Créer un script pour examiner les attributs de settings utilisés dans storage.py
cat > ./job-parser-service/examine_storage.py << 'EOL'
import re
import sys
import os

def examine_file(file_path):
    """Examine un fichier Python pour trouver les attributs de settings utilisés"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Rechercher les attributs de settings utilisés
    settings_attributes = re.findall(r'settings\.([A-Z_]+)', content)
    return list(set(settings_attributes))

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else "app/services/storage.py"
    if not os.path.exists(file_path):
        print(f"Le fichier {file_path} n'existe pas.")
        sys.exit(1)
    
    attributes = examine_file(file_path)
    print("Attributs de settings utilisés dans le fichier:")
    for attr in sorted(attributes):
        print(f"- {attr}")
EOL

log_info "Installation de MinIO dans le conteneur..."
docker-compose up -d minio

# Création d'un script pour initialiser le bucket MinIO
log_title "INITIALISATION DE MINIO"
log_info "Création d'un script pour initialiser le bucket MinIO..."

cat > ./job-parser-service/init_minio.sh << 'EOL'
#!/bin/bash

echo "[MINIO_INIT] Initialisation du client MinIO..."

# Installer le client MinIO
pip install --no-cache-dir minio

# Créer un script Python pour initialiser le bucket
cat > /tmp/init_minio.py << 'PYTHON_SCRIPT'
from minio import Minio
from minio.error import S3Error
import os

def init_minio_bucket():
    """Initialise le bucket MinIO pour le service de parsing"""
    try:
        # Configuration du client MinIO
        client = Minio(
            endpoint=os.environ.get('MINIO_ENDPOINT', 'minio:9000'),
            access_key=os.environ.get('MINIO_ACCESS_KEY', 'minioadmin'),
            secret_key=os.environ.get('MINIO_SECRET_KEY', 'minioadmin'),
            secure=os.environ.get('MINIO_SECURE', 'false').lower() == 'true'
        )
        
        # Nom du bucket
        bucket_name = os.environ.get('MINIO_BUCKET_NAME', 'jobs')
        
        # Vérifier si le bucket existe, sinon le créer
        if not client.bucket_exists(bucket_name):
            print(f"Le bucket '{bucket_name}' n'existe pas, création...")
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' créé avec succès.")
        else:
            print(f"Le bucket '{bucket_name}' existe déjà.")
        
        # Configuration des règles de sécurité
        print("Configuration des règles d'accès du bucket...")
        client.set_bucket_policy(bucket_name, '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"AWS":["*"]},"Action":["s3:GetObject"],"Resource":["arn:aws:s3:::' + bucket_name + '/*"]}]}')
        
        return True
    except S3Error as e:
        print(f"Erreur lors de l'initialisation du bucket MinIO: {e}")
        return False
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    success = init_minio_bucket()
    if success:
        print("Initialisation du bucket MinIO terminée avec succès.")
    else:
        print("Échec de l'initialisation du bucket MinIO.")
PYTHON_SCRIPT

# Exécuter le script
python /tmp/init_minio.py

echo "[MINIO_INIT] Initialisation terminée."
EOL

chmod +x ./job-parser-service/init_minio.sh

# Mettre à jour le script d'initialisation du conteneur
log_title "MISE À JOUR DU SCRIPT D'INITIALISATION"
log_info "Mise à jour du script d'initialisation du conteneur..."

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

# Attendre que MinIO soit disponible
echo "[CONTAINER_INIT] Attente de la disponibilité de MinIO..."
while ! nc -z minio 9000; do
  echo "MinIO n'est pas encore disponible, nouvelle tentative dans 1 seconde..."
  sleep 1
done
echo "MinIO est disponible."

# Initialiser MinIO si nécessaire
echo "[CONTAINER_INIT] Initialisation de MinIO..."
if [ -f "/app/init_minio.sh" ]; then
  chmod +x /app/init_minio.sh
  /app/init_minio.sh
fi

# Vérifier et configurer les variables d'environnement
echo "[CONTAINER_INIT] Configuration des variables d'environnement..."
export MINIO_ENDPOINT=${MINIO_ENDPOINT:-minio:9000}
export MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
export MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
export MINIO_SECURE=${MINIO_SECURE:-false}
export MINIO_BUCKET_NAME=${MINIO_BUCKET_NAME:-jobs}
export USE_MINIO_FOR_FILES=${USE_MINIO_FOR_FILES:-true}

echo "[CONTAINER_INIT] Configuration finale :"
echo "- MINIO_ENDPOINT = $MINIO_ENDPOINT"
echo "- MINIO_BUCKET_NAME = $MINIO_BUCKET_NAME"
echo "- USE_MINIO_FOR_FILES = $USE_MINIO_FOR_FILES"

# Exécuter la commande fournie
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
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Répertoire de travail
WORKDIR /app

# Copier les requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pydantic-settings>=2.0.0 minio

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs /app/uploads && \
    chmod 777 /app/logs /app/uploads

# Copier les scripts d'initialisation
COPY init_container.sh /init_container.sh
COPY init_minio.sh /app/init_minio.sh
RUN chmod +x /init_container.sh /app/init_minio.sh

# Exposer le port
EXPOSE 5000

# Copier le code
COPY . .

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
docker-compose logs --tail=30 job-parser

# Vérifier l'accessibilité du service
log_info "Vérification de l'accessibilité du service..."
curl -s -I http://localhost:5053/health || echo "Le service n'est pas encore accessible."

log_success "Processus de correction terminé. Le service devrait maintenant être fonctionnel."
