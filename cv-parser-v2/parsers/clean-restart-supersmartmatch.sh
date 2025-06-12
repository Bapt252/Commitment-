#!/bin/bash

# Redémarrage propre de SuperSmartMatch
# Nettoie les processus existants et redémarre sur un port libre

echo "🧹 Nettoyage et redémarrage de SuperSmartMatch"
echo "============================================="

# 1. Arrêter tous les processus SuperSmartMatch existants
echo "1️⃣ Arrêt des processus SuperSmartMatch existants..."

# Trouver et arrêter les processus Python/app.py
PYTHON_PIDS=$(ps aux | grep "python3.*app.py" | grep -v grep | awk '{print $2}')
if [ -n "$PYTHON_PIDS" ]; then
    echo "   Arrêt des processus Python: $PYTHON_PIDS"
    for pid in $PYTHON_PIDS; do
        kill -TERM $pid 2>/dev/null || true
    done
    sleep 2
    
    # Force kill si nécessaire
    for pid in $PYTHON_PIDS; do
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null || true
        fi
    done
fi

# Arrêter tout ce qui occupe le port 5060
PORT_PIDS=$(lsof -ti :5060 2>/dev/null)
if [ -n "$PORT_PIDS" ]; then
    echo "   Libération du port 5060..."
    for pid in $PORT_PIDS; do
        kill -TERM $pid 2>/dev/null || true
    done
    sleep 2
    
    # Force kill si nécessaire
    for pid in $PORT_PIDS; do
        if ps -p $pid > /dev/null 2>&1; then
            kill -9 $pid 2>/dev/null || true
        fi
    done
fi

echo "✅ Nettoyage terminé"

# 2. Trouver un port libre
echo "2️⃣ Recherche d'un port libre..."
FREE_PORT=""
for test_port in 5060 5061 5062 5063 5064; do
    if ! lsof -i :$test_port > /dev/null 2>&1; then
        FREE_PORT=$test_port
        echo "   ✅ Port libre trouvé: $FREE_PORT"
        break
    else
        echo "   ⚠️  Port $test_port occupé"
    fi
done

if [ -z "$FREE_PORT" ]; then
    echo "❌ Aucun port libre trouvé dans la plage 5060-5064"
    exit 1
fi

# 3. Vérifier l'environnement SuperSmartMatch
echo "3️⃣ Vérification de l'environnement..."

if [ ! -d "super-smart-match" ]; then
    echo "❌ Répertoire super-smart-match non trouvé"
    exit 1
fi

cd super-smart-match

if [ ! -f "app.py" ]; then
    echo "❌ app.py non trouvé"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --quiet flask flask-cors
else
    echo "📦 Activation de l'environnement virtuel..."
    source venv/bin/activate
fi

# 4. Démarrage de SuperSmartMatch
echo "4️⃣ Démarrage de SuperSmartMatch..."

# Définir les variables d'environnement
export PYTHONPATH="$(pwd)/..:$PYTHONPATH"
export PORT=$FREE_PORT

echo ""
echo "🎉 SuperSmartMatch prêt !"
echo "🌐 URL: http://localhost:$FREE_PORT"
echo "📊 Endpoints:"
echo "   - Health: http://localhost:$FREE_PORT/api/health"
echo "   - Match: http://localhost:$FREE_PORT/api/match"
echo "   - Algorithmes: http://localhost:$FREE_PORT/api/algorithms"
echo ""
echo "🧪 Test rapide (dans un autre terminal):"
echo "   curl http://localhost:$FREE_PORT/api/health"
echo ""
echo "🔄 Démarrage en cours..."
echo "   (Utilisez Ctrl+C pour arrêter)"
echo ""

# Démarrer SuperSmartMatch
python3 app.py
