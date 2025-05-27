#!/bin/bash

# Script de démarrage rapide SuperSmartMatch
# Usage: ./start-supersmartmatch.sh

echo "🚀 Démarrage de SuperSmartMatch - Algorithme intelligent côté entreprise"
echo "======================================================================="

# Configuration
SUPERSMARTMATCH_DIR="super-smart-match"
PORT=5061
PYTHON_CMD="python3"

# Vérifications préalables
echo "🔍 Vérifications préalables..."

# Vérifier Python
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "❌ Python 3 n'est pas installé ou accessible"
    echo "💡 Installez Python 3 : sudo apt install python3 python3-pip"
    exit 1
fi

echo "✅ Python 3 trouvé : $(python3 --version)"

# Vérifier pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 n'est pas installé"
    echo "💡 Installez pip3 : sudo apt install python3-pip"
    exit 1
fi

echo "✅ pip3 trouvé"

# Vérifier le répertoire SuperSmartMatch
if [ ! -d "$SUPERSMARTMATCH_DIR" ]; then
    echo "❌ Répertoire $SUPERSMARTMATCH_DIR non trouvé"
    echo "💡 Assurez-vous d'être dans le répertoire racine du projet"
    exit 1
fi

echo "✅ Répertoire SuperSmartMatch trouvé"

# Vérifier le port
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Le port $PORT est déjà utilisé"
    echo "🔄 Tentative d'arrêt du processus existant..."
    
    # Tenter d'arrêter le processus
    PID=$(lsof -Pi :$PORT -sTCP:LISTEN -t)
    if [ ! -z "$PID" ]; then
        kill $PID 2>/dev/null
        sleep 2
        
        # Vérifier si le processus est toujours actif
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
            echo "❌ Impossible d'arrêter le processus sur le port $PORT"
            echo "💡 Arrêtez manuellement avec: kill -9 $(lsof -Pi :$PORT -sTCP:LISTEN -t)"
            exit 1
        fi
    fi
    
    echo "✅ Port $PORT libéré"
fi

# Installation des dépendances
echo -e "\n📦 Installation des dépendances..."

cd $SUPERSMARTMATCH_DIR

# Vérifier requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "📝 Création du fichier requirements.txt..."
    cat > requirements.txt << EOF
flask>=2.0.0
flask-cors>=3.0.0
numpy>=1.20.0
scikit-learn>=1.0.0
EOF
fi

# Installer les dépendances
echo "📥 Installation des packages Python..."
pip3 install -r requirements.txt --quiet || {
    echo "❌ Erreur lors de l'installation des dépendances"
    echo "💡 Essayez: pip3 install --user flask flask-cors numpy scikit-learn"
    exit 1
}

echo "✅ Dépendances installées"

# Vérifier la structure des algorithmes
echo -e "\n🔧 Vérification de la structure..."

if [ ! -f "algorithms/supersmartmatch.py" ]; then
    echo "❌ Fichier algorithms/supersmartmatch.py manquant"
    echo "💡 Assurez-vous que tous les fichiers ont été créés correctement"
    exit 1
fi

if [ ! -f "app.py" ]; then
    echo "❌ Fichier app.py manquant"
    exit 1
fi

echo "✅ Structure validée"

# Créer les répertoires de logs si nécessaires
mkdir -p logs
mkdir -p temp

# Démarrage du serveur
echo -e "\n🚀 Démarrage du serveur SuperSmartMatch..."
echo "📍 URL: http://localhost:$PORT"
echo "🔄 Appuyez sur Ctrl+C pour arrêter"
echo ""

# Démarrer en arrière-plan ou en premier plan selon l'option
if [ "$1" = "--background" ] || [ "$1" = "-b" ]; then
    echo "🔧 Démarrage en arrière-plan..."
    nohup $PYTHON_CMD app.py > logs/supersmartmatch.log 2>&1 &
    SERVER_PID=$!
    echo "✅ Serveur démarré en arrière-plan (PID: $SERVER_PID)"
    echo "📋 Logs: tail -f $SUPERSMARTMATCH_DIR/logs/supersmartmatch.log"
    echo "🛑 Arrêt: kill $SERVER_PID"
    
    # Attendre que le serveur soit prêt
    echo "⏳ Attente du démarrage du serveur..."
    sleep 3
    
    # Test de connexion
    if curl -s http://localhost:$PORT/api/health > /dev/null; then
        echo "✅ Serveur SuperSmartMatch opérationnel !"
        echo ""
        echo "🎯 COMMANDES UTILES:"
        echo "• Tester: ../test-supersmartmatch.sh"
        echo "• Health: curl http://localhost:$PORT/api/health"
        echo "• Logs: tail -f logs/supersmartmatch.log"
        echo "• Arrêt: kill $SERVER_PID"
    else
        echo "❌ Erreur de démarrage du serveur"
        echo "📋 Vérifiez les logs: cat logs/supersmartmatch.log"
    fi
    
else
    echo "🔧 Démarrage en premier plan..."
    echo "💡 Utilisez --background pour démarrer en arrière-plan"
    echo ""
    
    # Gérer l'arrêt propre
    trap 'echo ""; echo "🛑 Arrêt de SuperSmartMatch..."; exit 0' INT
    
    # Démarrer le serveur
    $PYTHON_CMD app.py
fi
