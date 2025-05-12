#!/bin/bash

# Script pour corriger la configuration de journalisation dans le conteneur Docker

echo "Correction de la configuration de journalisation dans le conteneur..."

# Accéder au répertoire du service job-parser
cd /app

# Vérifier si le fichier config.py existe
if [ -f "/app/app/core/config.py" ]; then
  echo "Fichier config.py trouvé, ajout des paramètres de journalisation manquants..."
  
  # Ajouter les paramètres de journalisation après la section des extensions autorisées
  sed -i '/ALLOWED_EXTENSIONS/a \    # Configuration de journalisation\n    LOG_DIR: str = os.environ.get('"'"'LOG_DIR'"'"') or '"'"'logs'"'"'\n    LOG_LEVEL: str = os.environ.get('"'"'LOG_LEVEL'"'"') or '"'"'INFO'"'"'\n    LOG_FORMAT: str = os.environ.get('"'"'LOG_FORMAT'"'"') or '"'"'text'"'"'  # '"'"'text'"'"' ou '"'"'json'"'"'' /app/app/core/config.py
  
  echo "Paramètres de journalisation ajoutés."
else
  echo "Erreur: Le fichier config.py n'a pas été trouvé à l'emplacement attendu."
  exit 1
fi

# Créer le répertoire de logs s'il n'existe pas
mkdir -p /app/logs
chmod 777 /app/logs

echo "Correction terminée."
