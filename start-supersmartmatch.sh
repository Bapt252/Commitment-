#!/bin/bash
echo "🚀 Démarrage de SuperSmartMatch..."

# S'assurer que le répertoire existe
mkdir -p super-smart-match
cd super-smart-match

# Installer les dépendances si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors
else
    source venv/bin/activate
fi

export PYTHONPATH="$(pwd)/..:$PYTHONPATH"

echo "🌐 Service disponible sur http://localhost:5060"
echo "📊 Endpoints:"
echo "   - Health: http://localhost:5060/api/health"
echo "   - Algorithmes: http://localhost:5060/api/algorithms"
echo "   - Matching: http://localhost:5060/api/match"
echo ""

python3 app.py
