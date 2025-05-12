#!/bin/bash

echo "=== Script de correction du service job-parser ==="
echo "Vérification des services en cours d'exécution..."

# Vérifier si les conteneurs sont en cours d'exécution
if ! docker ps | grep -q "nexten-job-parser"; then
  echo "Le conteneur nexten-job-parser n'est pas en cours d'exécution."
  echo "Démarrage des services..."
  docker-compose up -d job-parser job-parser-worker
fi

echo "Création du fichier entrypoint.sh corrigé..."
cat > /tmp/entrypoint.sh.new << 'EOL'
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
  cat > "$COMPAT_FILE" << 'EOLL'
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
EOLL
  log_message "Fichier pydantic_compat.py créé avec succès"
fi

# Vérifier si config.py existe
CONFIG_FILE="/app/app/core/config.py"
if [ ! -f "$CONFIG_FILE" ]; then
  log_message "ERREUR: Le fichier config.py n'existe pas!"
  exit 1
fi

# Modifier le fichier config.py
log_message "Modification du fichier config.py pour utiliser pydantic_compat..."
sed -i.bak 's/from pydantic import BaseSettings/try:\n    from app.core.pydantic_compat import BaseSettings\n    from pydantic import validator\nexcept ImportError:\n    try:\n        from pydantic_settings import BaseSettings\n        from pydantic import validator\n    except ImportError:\n        from pydantic import BaseSettings, validator/g' "$CONFIG_FILE"

# Vérifier si pydantic-settings est installé
log_message "Vérification de l'installation de pydantic-settings..."
pip install --no-cache-dir pydantic-settings>=2.0.0

# Activer le mode mock si pas de clé OpenAI
if [ -z "${OPENAI_API_KEY}" ] && [ -z "${OPENAI}" ]; then
    log_message "Aucune clé API OpenAI trouvée. Activation du mode simulation..."
    export USE_MOCK_PARSER=true
fi

# Exécuter la commande fournie
log_message "Exécution de la commande: $@"
exec "$@"
EOL

echo "Application des corrections sur les conteneurs..."
docker cp /tmp/entrypoint.sh.new nexten-job-parser:/entrypoint.sh
docker exec nexten-job-parser chmod +x /entrypoint.sh

# Appliquer aussi aux workers si nécessaire
if docker ps | grep -q "commitment--job-parser-worker-1"; then
  docker cp /tmp/entrypoint.sh.new commitment--job-parser-worker-1:/entrypoint.sh
  docker exec commitment--job-parser-worker-1 chmod +x /entrypoint.sh
fi

if docker ps | grep -q "commitment--job-parser-worker-2"; then
  docker cp /tmp/entrypoint.sh.new commitment--job-parser-worker-2:/entrypoint.sh
  docker exec commitment--job-parser-worker-2 chmod +x /entrypoint.sh
fi

echo "Installation des dépendances dans le conteneur..."
docker exec nexten-job-parser pip install pydantic-settings>=2.0.0

echo "Mise à jour du fichier .env dans le conteneur..."
if [ -f ".env" ]; then
  docker cp .env nexten-job-parser:/app/.env
  echo "Fichier .env copié dans le conteneur."
else
  echo "ATTENTION: Fichier .env non trouvé. Vous devriez en créer un avec votre clé API OpenAI."
fi

echo "Redémarrage des services..."
docker-compose restart job-parser job-parser-worker

echo "=== Correction terminée ==="
echo "Attendez quelques secondes pour que les services redémarrent, puis testez avec :"
echo "curl -X POST http://localhost:5053/api/parse-job -H \"Content-Type: multipart/form-data\" -F \"file=@~/Desktop/fdp.pdf\" -F \"force_refresh=false\""

# Afficher les logs
echo "Affichage des logs (Ctrl+C pour quitter)..."
sleep 2
docker-compose logs -f job-parser