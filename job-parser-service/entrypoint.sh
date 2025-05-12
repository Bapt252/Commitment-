#!/bin/bash
set -e

# Script de démarrage pour le service job-parser

# Fonction pour l'affichage des logs
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
