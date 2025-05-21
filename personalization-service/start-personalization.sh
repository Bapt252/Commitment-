#!/bin/bash

# Script pour démarrer le service de personnalisation

echo "Démarrage du service de personnalisation..."

# Création des répertoires nécessaires s'ils n'existent pas
mkdir -p logs

# Vérification des variables d'environnement
if [ -z "$PORT" ]; then
    export PORT=5060
    echo "La variable PORT n'est pas définie, utilisation de la valeur par défaut: 5060"
fi

if [ -z "$DATABASE_URL" ]; then
    export DATABASE_URL="postgresql://postgres:postgres@postgres:5432/nexten"
    echo "La variable DATABASE_URL n'est pas définie, utilisation de la valeur par défaut"
fi

if [ -z "$REDIS_HOST" ]; then
    export REDIS_HOST="redis"
    echo "La variable REDIS_HOST n'est pas définie, utilisation de la valeur par défaut: redis"
fi

if [ -z "$MATCHING_SERVICE_URL" ]; then
    export MATCHING_SERVICE_URL="http://matching-api:5000"
    echo "La variable MATCHING_SERVICE_URL n'est pas définie, utilisation de la valeur par défaut"
fi

# Démarrage du service
echo "Lancement du service de personnalisation sur le port $PORT"
python api.py
