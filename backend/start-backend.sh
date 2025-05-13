#!/bin/bash
# start-backend.sh - Script pour démarrer rapidement le backend du job parser

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null
then
    echo "Python 3 n'est pas installé. Veuillez l'installer pour continuer."
    exit 1
fi

# Vérifier si les dépendances sont installées
if ! python3 -c "import flask, flask_cors, requests, PyPDF2, docx" &> /dev/null
then
    echo "Installation des dépendances..."
    pip install flask flask-cors requests PyPDF2 python-docx
fi

# Vérifier si la clé API OpenAI est configurée
if [ -z "$OPENAI_API_KEY" ]
then
    echo "ATTENTION: Aucune clé API OpenAI n'est configurée."
    echo "Le service fonctionnera en mode limité (analyse locale uniquement)."
    echo "Pour utiliser l'API OpenAI, définissez la variable d'environnement OPENAI_API_KEY."
    echo "Exemple: export OPENAI_API_KEY=votre-clé-api"
    echo ""
fi

# Démarrer le serveur
echo "Démarrage du serveur backend..."
python3 job_parser_api.py
