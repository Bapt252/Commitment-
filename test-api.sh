#!/bin/bash

# Script pour lancer les tests de l'API

cd "$(dirname "$0")" && cd backend
echo "Lancement des tests..."
python -m pytest

# Pour générer un rapport de couverture, décommentez les lignes suivantes
# echo "Lancement des tests avec couverture..."
# python -m pytest --cov=app tests/ -v
# python -m pytest --cov=app --cov-report=html tests/
