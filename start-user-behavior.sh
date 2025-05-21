#!/bin/bash

# Script pour démarrer le service d'analyse comportementale

# Vérifier si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Veuillez installer Docker et réessayer."
    exit 1
fi

# Vérifier si Docker Compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose n'est pas installé. Veuillez installer Docker Compose et réessayer."
    exit 1
fi

# Rendre le script exécutable
chmod +x start-user-behavior.sh

# Démarrer uniquement le service d'analyse comportementale
echo "Démarrage du service d'analyse comportementale..."
docker-compose up -d postgres redis user-behavior-api

echo "Attendez quelques secondes que le service démarre..."
sleep 5

# Vérifier que le service est actif
if curl -s http://localhost:5054/health | grep -q "healthy"; then
    echo "Le service d'analyse comportementale est démarré et accessible à l'adresse: http://localhost:5054"
    echo "API disponible à: http://localhost:5054/api"
    echo "Vérifiez la santé du service: curl http://localhost:5054/health"
    echo "Documentation API et exemples: voir user-behavior-guide.md"
else
    echo "Le service ne semble pas avoir démarré correctement. Vérifiez les logs:"
    docker-compose logs user-behavior-api
fi