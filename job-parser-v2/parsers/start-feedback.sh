#!/bin/bash

# Script pour démarrer le service de feedback

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
chmod +x start-feedback.sh

# Démarrer uniquement les services nécessaires pour le feedback
echo "Démarrage du service de feedback et des services dépendants..."
docker-compose up -d postgres redis feedback-service

echo "Attendez quelques secondes que le service démarre..."
sleep 5

# Vérifier que le service est actif
if curl -s http://localhost:5058/health | grep -q "healthy"; then
    echo "Le service de feedback est démarré et accessible à l'adresse: http://localhost:5058"
    echo "API disponible à: http://localhost:5058/api"
    echo "Vérifiez la santé du service: curl http://localhost:5058/health"
else
    echo "Le service ne semble pas avoir démarré correctement. Vérifiez les logs:"
    docker-compose logs feedback-service
fi
