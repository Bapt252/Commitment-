#!/bin/bash

# Script pour démarrer l'API du Job Parser
echo "Démarrage de l'API du Job Parser..."

# Vérifier si Python est disponible
if ! command -v python &> /dev/null; then
    echo "Python n'est pas disponible. Vérifiez votre installation."
    exit 1
fi

# Vérifier si les dépendances sont installées
if ! python -c "import flask, flask_cors, PyPDF2" &> /dev/null; then
    echo "Installation des dépendances..."
    pip install flask flask-cors PyPDF2
fi

# Démarrer l'API
echo "Lancement de l'API..."
python templates/job-parser-api.py "$@"
