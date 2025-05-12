#!/bin/bash

# Script pour redémarrer le service job-parser

echo "Arrêt du service job-parser..."
docker-compose stop job-parser job-parser-worker

echo "Reconstruction du service job-parser..."
docker-compose build job-parser job-parser-worker

echo "Démarrage du service job-parser..."
docker-compose up -d job-parser job-parser-worker

echo "Affichage des logs (Ctrl+C pour sortir)..."
docker-compose logs -f job-parser
