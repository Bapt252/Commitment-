#!/bin/bash
# Script de démarrage du service de personnalisation

# Définir les variables d'environnement par défaut
export PORT=${PORT:-5000}
export DB_HOST=${DB_HOST:-localhost}
export DB_PORT=${DB_PORT:-5432}
export DB_NAME=${DB_NAME:-commitment}
export DB_USER=${DB_USER:-postgres}
export DB_PASSWORD=${DB_PASSWORD:-postgres}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

# Activer l'environnement virtuel si présent
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Installer les dépendances si nécessaire
echo "Checking dependencies..."
pip install -r requirements-session10.txt

# Initialiser la base de données si demandé
if [ "$1" = "--init-db" ]; then
    echo "Initializing database..."
    python scripts/init_personalization_db.py --seed-data
fi

# Démarrer le service API
echo "Starting personalization service on port $PORT..."
python -m user_personalization.api
