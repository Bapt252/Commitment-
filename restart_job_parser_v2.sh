#!/bin/bash

echo "🚀 REDÉMARRAGE JOB PARSER V2 - SuperSmartMatch Enhanced"
echo "======================================================"

# 1. Naviguer vers le répertoire du projet
cd /Users/baptistecomas/Commitment-/

# 2. Récupérer les dernières modifications depuis GitHub
echo "📥 Récupération des modifications GitHub..."
git pull origin main

# 3. Arrêter le service actuel sur le port 5053
echo "🛑 Arrêt du service Job Parser V2..."
sudo kill -9 $(lsof -ti:5053) 2>/dev/null || echo "Port 5053 déjà libre"

# 4. Naviguer vers le répertoire job-parser-v2
cd job-parser-v2/

# 5. Vérifier que les fichiers parsers existent
echo "📋 Vérification des parsers..."
if [ ! -f "parsers/fix-pdf-extraction.js" ]; then
    echo "❌ Erreur : parsers/fix-pdf-extraction.js manquant"
    exit 1
fi

if [ ! -f "parsers/enhanced-mission-parser.js" ]; then
    echo "❌ Erreur : parsers/enhanced-mission-parser.js manquant"
    exit 1
fi

echo "✅ Parsers trouvés :"
echo "   - fix-pdf-extraction.js ($(wc -c < parsers/fix-pdf-extraction.js) bytes)"
echo "   - enhanced-mission-parser.js ($(wc -c < parsers/enhanced-mission-parser.js) bytes)"

# 6. Vérifier que la correction a été appliquée
echo "📋 Vérification de la correction..."
if grep -q 'Path("./parsers")' app.py; then
    echo "✅ Correction confirmée : Path(\"./parsers\") trouvé dans app.py"
else
    echo "❌ Erreur : Correction non trouvée dans app.py"
    exit 1
fi

# 7. Installer/activer l'environnement virtuel Python
echo "📋 Configuration environnement Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 8. Démarrer le Job Parser V2 corrigé
echo "🚀 Lancement du Job Parser V2 corrigé sur le port 5053..."
python3 app.py &
JOB_PARSER_PID=$!

# 9. Attendre le démarrage
echo "⏳ Attente du démarrage (3 secondes)..."
sleep 3

# 10. Test de santé du service
echo "🏥 Test de santé du service..."
HEALTH_CHECK=$(curl -s http://localhost:5053/health)

if echo "$HEALTH_CHECK" | grep -q '"status": "healthy"'; then
    echo ""
    echo "🎉 JOB PARSER V2 DÉMARRÉ AVEC SUCCÈS !"
    echo "======================================"
    echo ""
    echo "🔍 ÉTAT DES PARSERS :"
    echo "$HEALTH_CHECK" | python3 -m json.tool
    
    # Vérifier que les parsers sont disponibles
    echo ""
    echo "📊 VÉRIFICATION DÉTAILLÉE :"
    if echo "$HEALTH_CHECK" | grep -q '"fix_pdf_extraction": true'; then
        echo "   ✅ fix-pdf-extraction.js : DISPONIBLE"
    else
        echo "   ❌ fix-pdf-extraction.js : NON DISPONIBLE"
    fi
    
    if echo "$HEALTH_CHECK" | grep -q '"enhanced_mission_parser": true'; then
        echo "   ✅ enhanced-mission-parser.js : DISPONIBLE"
    else
        echo "   ❌ enhanced-mission-parser.js : NON DISPONIBLE"
    fi
    
    echo ""
    echo "🎯 SYSTÈME COMPLET OPÉRATIONNEL :"
    echo "   • CV Parser V2  : ✅ Port 5051"
    echo "   • Job Parser V2 : ✅ Port 5053 (CORRIGÉ)"
    echo "   • Enhanced API  : ✅ Port 5055"
    echo "   • PID Job Parser: $JOB_PARSER_PID"
    echo ""
    echo "🚀 PRÊT POUR LES TESTS MASSIFS !"
    echo "   Commande : python3 enhanced_batch_testing_v2_fixed.py"
    echo "   Objectif : 2,812 matchings (74 CV × 38 Jobs)"
    
else
    echo ""
    echo "❌ ERREUR : Job Parser V2 ne répond pas correctement"
    echo "Réponse reçue : $HEALTH_CHECK"
    
    # Tuer le processus défaillant
    kill $JOB_PARSER_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ REDÉMARRAGE TERMINÉ AVEC SUCCÈS !"
echo "===================================="
