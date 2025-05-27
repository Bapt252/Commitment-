#!/bin/bash

# Diagnostic et Redémarrage Automatique de SuperSmartMatch

echo "🔍 Diagnostic SuperSmartMatch"
echo "============================"

# 1. Vérifier les processus SuperSmartMatch
echo "1️⃣ Processus SuperSmartMatch :"
PROCESSES=$(ps aux | grep "python3.*app.py" | grep -v grep)
if [ -n "$PROCESSES" ]; then
    echo "✅ SuperSmartMatch en cours :"
    echo "$PROCESSES"
else
    echo "❌ Aucun processus SuperSmartMatch détecté"
fi

echo ""

# 2. Vérifier les ports
echo "2️⃣ État des ports :"
for port in 5060 5061 5062; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "   Port $port: OCCUPÉ"
        lsof -i :$port | head -2
    else
        echo "   Port $port: LIBRE"
    fi
done

echo ""

# 3. Test de connexion rapide
echo "3️⃣ Test de connexion :"
for port in 5060 5061 5062; do
    if curl -s --max-time 2 "http://localhost:$port/api/health" > /dev/null 2>&1; then
        echo "✅ SuperSmartMatch répond sur le port $port"
        curl -s "http://localhost:$port/api/health" | head -200
        echo ""
        echo "🎯 URL active: http://localhost:$port"
        exit 0
    fi
done

echo "❌ SuperSmartMatch ne répond sur aucun port"
echo ""

# 4. Nettoyage et redémarrage automatique
echo "4️⃣ Redémarrage automatique..."

# Nettoyer les processus restants
pkill -f "python3.*app.py" 2>/dev/null || true
sleep 2

# Redémarrer
echo "🚀 Redémarrage de SuperSmartMatch..."

if [ ! -d "super-smart-match" ]; then
    echo "❌ Répertoire super-smart-match non trouvé"
    exit 1
fi

cd super-smart-match

# Vérifier l'environnement virtuel
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --quiet flask flask-cors requests numpy pandas
else
    source venv/bin/activate
fi

# Trouver un port libre
FREE_PORT=5060
for test_port in 5060 5061 5062 5063; do
    if ! lsof -i :$test_port > /dev/null 2>&1; then
        FREE_PORT=$test_port
        break
    fi
done

echo "🎯 Utilisation du port $FREE_PORT"

# Variables d'environnement
export PYTHONPATH="$(pwd)/..:$PYTHONPATH"
export PORT=$FREE_PORT

# Démarrage en arrière-plan pour test
echo "🔄 Test de démarrage..."
timeout 10s python3 app.py &
PID=$!

# Attendre un peu
sleep 5

# Tester la connexion
if curl -s --max-time 3 "http://localhost:$FREE_PORT/api/health" > /dev/null 2>&1; then
    echo "✅ SuperSmartMatch fonctionne !"
    echo "🌐 URL: http://localhost:$FREE_PORT"
    
    # Arrêter le test et redémarrer en mode normal
    kill $PID 2>/dev/null
    
    echo ""
    echo "🚀 Démarrage en mode normal..."
    echo "📊 Endpoints disponibles :"
    echo "   - Health: http://localhost:$FREE_PORT/api/health"
    echo "   - Match: http://localhost:$FREE_PORT/api/match"
    echo "   - Algorithmes: http://localhost:$FREE_PORT/api/algorithms"
    echo ""
    echo "🧪 Test dans un autre terminal :"
    echo "   curl http://localhost:$FREE_PORT/api/health"
    echo ""
    
    # Démarrage normal
    python3 app.py
else
    echo "❌ Échec du test de démarrage"
    kill $PID 2>/dev/null
    
    echo ""
    echo "🛠️ Solutions possibles :"
    echo "   1. Vérifier les dépendances : pip install flask flask-cors requests numpy"
    echo "   2. Vérifier app.py : ls -la app.py"
    echo "   3. Vérifier les logs d'erreur ci-dessus"
    
    cd ..
    exit 1
fi
