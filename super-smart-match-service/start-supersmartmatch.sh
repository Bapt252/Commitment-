#!/bin/bash

# Script de démarrage pour SuperSmartMatch
# Auteur: Nexten Team

echo "🚀 Démarrage de SuperSmartMatch - Service Unifié de Matching"
echo "======================================================================"

# Configuration par défaut
PORT=${PORT:-5070}
HOST=${HOST:-0.0.0.0}
ENVIRONMENT=${ENVIRONMENT:-development}

# Vérification des dépendances
echo "🔍 Vérification des dépendances..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 non trouvé. Veuillez l'installer."
    exit 1
fi

# Vérification de la version Python
PYTHON_VERSION=$(python3 -c 'import sys; print(sys.version_info[:2])')
echo "✅ Python version: $PYTHON_VERSION"

# Création du répertoire des logs
echo "📁 Création du répertoire des logs..."
mkdir -p logs

# Installation des dépendances si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "📦 Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Vérification de la disponibilité du port
echo "🔌 Vérification du port $PORT..."
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port $PORT déjà utilisé. Tentative d'arrêt du processus..."
    pkill -f "python.*app.py" || true
    sleep 2
fi

# Vérification des algorithmes disponibles
echo "🧠 Vérification des algorithmes..."
ALGOS_FOUND=0

if [ -f "../matching_engine.py" ]; then
    echo "✅ Algorithme Original trouvé"
    ((ALGOS_FOUND++))
else
    echo "⚠️  Algorithme Original non trouvé"
fi

if [ -f "../enhanced_matching_engine.py" ]; then
    echo "✅ Enhanced Matching Engine trouvé"
    ((ALGOS_FOUND++))
else
    echo "⚠️  Enhanced Matching Engine non trouvé"
fi

if [ -f "../my_matching_engine.py" ]; then
    echo "✅ Algorithme Personnalisé trouvé"
    ((ALGOS_FOUND++))
else
    echo "⚠️  Algorithme Personnalisé non trouvé"
fi

echo "📊 $ALGOS_FOUND algorithmes disponibles"

# Configuration des variables d'environnement
echo "⚙️  Configuration de l'environnement..."
export PORT=$PORT
export HOST=$HOST
export ENVIRONMENT=$ENVIRONMENT
export PYTHONPATH="$PWD:$PWD/..:$PYTHONPATH"

echo "   - Port: $PORT"
echo "   - Host: $HOST"
echo "   - Environnement: $ENVIRONMENT"
echo "   - PYTHONPATH: $PYTHONPATH"

# Démarrage du service
echo "
🚀 Démarrage de SuperSmartMatch..."
echo "======================================================================"
echo "🌐 Service disponible sur: http://$HOST:$PORT"
echo "📄 Documentation API: http://$HOST:$PORT/docs"
echo "🔍 Health Check: http://$HOST:$PORT/health"
echo "🧠 Algorithmes: http://$HOST:$PORT/algorithms"
echo "======================================================================"

# Démarrage avec auto-reload en mode développement
if [ "$ENVIRONMENT" = "development" ]; then
    echo "🛠️  Mode développement activé (auto-reload)"
    python3 app.py
else
    echo "💼 Mode production"
    python3 app.py
fi
