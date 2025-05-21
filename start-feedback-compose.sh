#!/bin/bash

# Script pour démarrer le service de feedback simplifié avec docker-compose

echo "Arrêt des services de feedback existants (s'ils sont en cours d'exécution)..."
docker stop nexten-feedback nexten-feedback-simple 2>/dev/null || true
docker rm nexten-feedback nexten-feedback-simple 2>/dev/null || true

echo "Démarrage du service de feedback simplifié avec docker-compose..."
docker-compose -f docker-compose.simple.yml up -d --build

echo "Attendez quelques secondes que le service démarre..."
sleep 3

# Vérifier que le service est actif
if curl -s http://localhost:5058/health | grep -q "healthy"; then
    echo "Le service de feedback simplifié est démarré et accessible à l'adresse: http://localhost:5058"
    echo "API disponible à: http://localhost:5058/api"
    echo "Vérifiez la santé du service: curl http://localhost:5058/health"
    echo "Testez l'API: curl -X POST http://localhost:5058/api/feedback -H 'Content-Type: application/json' -d '{\"content\":\"Test de feedback\"}'"
else
    echo "Le service ne semble pas avoir démarré correctement. Vérifiez les logs:"
    docker-compose -f docker-compose.simple.yml logs
fi
