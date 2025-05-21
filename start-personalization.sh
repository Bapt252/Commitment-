#!/bin/bash

# Script principal pour démarrer le service de personnalisation
echo "Démarrage du service de personnalisation..."

# Rendre le script exécutable
chmod +x personalization-service/start-personalization.sh

# Vérifier les variables d'environnement nécessaires
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

# Créer les tables nécessaires dans la base de données
echo "Création des tables dans la base de données..."
psql $DATABASE_URL -f personalization-service/migrations/init_db.sql

# Démarrer le service
echo "Lancement du service de personnalisation..."
cd personalization-service && ./start-personalization.sh
