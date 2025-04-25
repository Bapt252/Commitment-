#!/bin/bash

# Script pour reconstruire les services matching

echo "Arrêt des services..."
docker-compose down

echo "Suppression des images des services matching..."
docker rmi -f $(docker images | grep 'commitment_matching' | awk '{print $1}')

echo "Reconstruction des services matching sans utiliser le cache..."
docker-compose build --no-cache matching-api matching-worker-high matching-worker-standard matching-worker-bulk

echo "Démarrage des services..."
docker-compose up -d

echo "Affichage des logs des services matching..."
docker-compose logs -f matching-api matching-worker-high matching-worker-standard matching-worker-bulk
