#!/bin/bash

# Arrêter tous les processus uvicorn en cours
echo "Arrêt des processus Uvicorn existants..."
pkill -f "uvicorn app.main:app" || true

# Attendre un peu pour s'assurer que les processus sont arrêtés
sleep 1

# Démarrer le serveur
echo "Démarrage du serveur FastAPI..."
cd "$(dirname "$0")" && cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
