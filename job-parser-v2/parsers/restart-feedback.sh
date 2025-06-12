#!/bin/bash

# Script pour redémarrer le service de feedback

echo "Arrêt du service de feedback (s'il est en cours d'exécution)..."
docker stop nexten-feedback || true
docker rm nexten-feedback || true

echo "Reconstruction de l'image Docker..."
docker-compose build feedback-service

echo "Démarrage du service de feedback..."
docker-compose up -d --no-deps feedback-service

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
