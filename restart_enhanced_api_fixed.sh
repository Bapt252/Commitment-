#!/bin/bash

# 🚀 SuperSmartMatch V2.1 Enhanced - Script de Redémarrage Corrigé
# Arrête l'ancienne Enhanced API et démarre la version corrigée

echo "🚀 REDÉMARRAGE ENHANCED API V2.1 CORRIGÉE"
echo "=========================================="
echo "🎯 Objectif: Corriger le problème des scores à 0%"
echo "✅ Solution: Nouvelle API avec matching_score, confidence, recommendation"
echo ""

# Fonction pour vérifier si un port est utilisé
check_port() {
    local port=$1
    if lsof -i :$port >/dev/null 2>&1; then
        return 0  # Port utilisé
    else
        return 1  # Port libre
    fi
}

# Fonction pour arrêter un processus sur un port
stop_port() {
    local port=$1
    local service_name=$2
    
    echo "🔍 Vérification du port $port ($service_name)..."
    
    if check_port $port; then
        echo "⚠️ Service détecté sur le port $port"
        
        # Trouver le PID
        PID=$(lsof -ti :$port)
        
        if [ ! -z "$PID" ]; then
            echo "🔄 Arrêt du processus $PID sur le port $port..."
            kill -TERM $PID 2>/dev/null
            
            # Attendre 3 secondes
            sleep 3
            
            # Vérifier si le processus s'est arrêté
            if check_port $port; then
                echo "⚡ Arrêt forcé du processus..."
                kill -KILL $PID 2>/dev/null
                sleep 2
            fi
            
            if check_port $port; then
                echo "❌ Impossible d'arrêter le service sur le port $port"
                return 1
            else
                echo "✅ Service arrêté avec succès"
                return 0
            fi
        else
            echo "❌ Impossible de trouver le PID pour le port $port"
            return 1
        fi
    else
        echo "✅ Port $port libre"
        return 0
    fi
}

# Étape 1: Arrêter l'ancienne Enhanced API (port 5055)
echo "📋 ÉTAPE 1: Arrêt de l'ancienne Enhanced API"
echo "--------------------------------------------"

stop_port 5055 "Enhanced API"

# Étape 2: Vérifier que les autres services sont opérationnels
echo ""
echo "📋 ÉTAPE 2: Vérification des services requis"
echo "--------------------------------------------"

services_ok=true

# Vérifier CV Parser V2 (port 5051)
echo "🔍 CV Parser V2 (port 5051)..."
if check_port 5051; then
    # Tester la connexion
    if curl -s "http://localhost:5051/health" > /dev/null; then
        echo "   ✅ CV Parser V2 opérationnel"
    else
        echo "   ⚠️ CV Parser V2 détecté mais ne répond pas"
        services_ok=false
    fi
else
    echo "   ❌ CV Parser V2 non démarré"
    services_ok=false
fi

# Vérifier Job Parser V2 (port 5053)
echo "🔍 Job Parser V2 (port 5053)..."
if check_port 5053; then
    # Tester la connexion
    if curl -s "http://localhost:5053/health" > /dev/null; then
        echo "   ✅ Job Parser V2 opérationnel"
    else
        echo "   ⚠️ Job Parser V2 détecté mais ne répond pas"
        services_ok=false
    fi
else
    echo "   ❌ Job Parser V2 non démarré"
    services_ok=false
fi

# Étape 3: Démarrer la nouvelle Enhanced API
echo ""
echo "📋 ÉTAPE 3: Démarrage de la nouvelle Enhanced API"
echo "-------------------------------------------------"

if [ "$services_ok" = true ]; then
    echo "✅ Tous les services prérequis sont opérationnels"
    echo ""
    echo "🚀 Démarrage de l'Enhanced API V2.1 corrigée..."
    echo "📄 Fichier: api-matching-enhanced-v2.1-fixed.py"
    echo "🌐 URL: http://localhost:5055"
    echo ""
    echo "⚡ DÉMARRAGE EN COURS..."
    echo "   (Ctrl+C pour arrêter)"
    echo ""
    
    # Démarrer la nouvelle API
    cd /Users/baptistecomas/Commitment-/
    python3 api-matching-enhanced-v2.1-fixed.py
    
else
    echo "❌ Certains services prérequis ne sont pas opérationnels"
    echo ""
    echo "💡 DÉMARRAGE MANUEL REQUIS:"
    echo ""
    
    if ! check_port 5051; then
        echo "🔧 CV Parser V2:"
        echo "   cd /Users/baptistecomas/Commitment-/"
        echo "   python3 cv-parser-v2.py"
        echo ""
    fi
    
    if ! check_port 5053; then
        echo "🔧 Job Parser V2:"
        echo "   cd /Users/baptistecomas/Commitment-/"
        echo "   python3 job-parser-v2.py"
        echo ""
    fi
    
    echo "🔧 Enhanced API V2.1 (après démarrage des autres services):"
    echo "   cd /Users/baptistecomas/Commitment-/"
    echo "   python3 api-matching-enhanced-v2.1-fixed.py"
    echo ""
    
    echo "🧪 Test de validation (optionnel):"
    echo "   python3 test_enhanced_api_fix.py"
    echo ""
    
    echo "🚀 Tests massifs (une fois tout démarré):"
    echo "   python3 massive_testing_complete.py"
fi

echo ""
echo "=" * 50
echo "🎯 OBJECTIF: Résoudre le problème des scores à 0%"
echo "✅ SOLUTION: API corrigée avec matching_score, confidence, recommendation"
echo "🎉 RÉSULTAT ATTENDU: 213 tests avec scores réalistes (60-80% bons matches)"
echo "=" * 50
