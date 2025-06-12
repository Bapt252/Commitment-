#!/bin/bash

# Redémarrage simple et robuste de SuperSmartMatch

echo "🚀 Redémarrage de SuperSmartMatch"
echo "=================================="

# Vérifier que le répertoire existe
if [ ! -d "super-smart-match" ]; then
    echo "❌ Répertoire super-smart-match non trouvé"
    echo "   Exécutez d'abord: ./fix-supersmartmatch-quick.sh"
    exit 1
fi

# Aller dans le répertoire
cd super-smart-match

# Vérifier l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --quiet flask flask-cors
else
    echo "📦 Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# Vérifier que app.py existe
if [ ! -f "app.py" ]; then
    echo "❌ app.py non trouvé"
    cd ..
    echo "   Exécutez: ./fix-supersmartmatch-dependencies.sh"
    exit 1
fi

# Définir les variables d'environnement
export PYTHONPATH="$(pwd)/..:$PYTHONPATH"
export PORT=5060

echo "✅ Environnement configuré"
echo "🌐 SuperSmartMatch sera disponible sur: http://localhost:5060"
echo "📊 Endpoints:"
echo "   - Health: http://localhost:5060/api/health"
echo "   - Match: http://localhost:5060/api/match"
echo "   - Algorithmes: http://localhost:5060/api/algorithms"
echo ""
echo "🔄 Démarrage en cours..."
echo "   (Utilisez Ctrl+C pour arrêter)"
echo ""

# Démarrer SuperSmartMatch
python3 app.py
