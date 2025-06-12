#!/bin/bash

# 🔧 Script de configuration - Rendre tous les scripts exécutables
# SuperSmartMatch V2.1 Enhanced - Fix CV Parser V2

echo "🔧 === CONFIGURATION SCRIPTS SUPERSMARTMATCH V2.1 ==="
echo "Mise à jour des permissions pour tous les scripts de résolution..."
echo ""

# Scripts principaux de résolution
echo "📋 Scripts de résolution CV Parser V2:"

SCRIPTS=(
    "diagnose_cv_parser_v2.sh"
    "fix_cv_parser_v2.sh" 
    "test_system_complete.sh"
    "fix_and_test_complete.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "✅ $script : Rendu exécutable"
    else
        echo "⚠️  $script : Fichier non trouvé"
    fi
done

# Scripts existants dans le projet
echo ""
echo "📋 Scripts existants du projet:"

# start_enhanced_system.sh
if [ -f "start_enhanced_system.sh" ]; then
    chmod +x "start_enhanced_system.sh"
    echo "✅ start_enhanced_system.sh : Rendu exécutable"
fi

# test_matching_system.py
if [ -f "test_matching_system.py" ]; then
    chmod +x "test_matching_system.py"
    echo "✅ test_matching_system.py : Rendu exécutable"
fi

# Répertoire cv-parser-v2/parsers
echo ""
echo "📁 Scripts dans cv-parser-v2/parsers/:"

if [ -d "cv-parser-v2/parsers" ]; then
    find cv-parser-v2/parsers -name "*.sh" -exec chmod +x {} \;
    echo "✅ Tous les scripts .sh dans cv-parser-v2/parsers/ rendus exécutables"
    
    # Compter les scripts
    SCRIPT_COUNT=$(find cv-parser-v2/parsers -name "*.sh" | wc -l)
    echo "   Total: $SCRIPT_COUNT scripts traités"
else
    echo "⚠️  Répertoire cv-parser-v2/parsers/ non trouvé"
fi

echo ""
echo "🎯 === GUIDE D'UTILISATION RAPIDE ==="
echo ""

echo "Pour résoudre le problème CV Parser V2 (port 5051):"
echo ""
echo "1. 🔍 DIAGNOSTIC COMPLET:"
echo "   ./diagnose_cv_parser_v2.sh"
echo ""
echo "2. 🔧 RÉPARATION RAPIDE:"
echo "   ./fix_cv_parser_v2.sh"
echo ""
echo "3. 🧪 TESTS COMPLETS:"
echo "   ./test_system_complete.sh"
echo ""
echo "4. 🎯 SOLUTION TOUT-EN-UN (RECOMMANDÉ):"
echo "   ./fix_and_test_complete.sh"
echo ""

echo "Autres commandes utiles:"
echo ""
echo "5. 📊 Test Enhanced API V2.1:"
echo "   curl http://localhost:5055/api/test/hugo-salvat"
echo ""
echo "6. 🔍 Statut des services:"
echo "   curl http://localhost:5051/health  # CV Parser V2"
echo "   curl http://localhost:5053/health  # Job Parser V2"
echo "   curl http://localhost:5055/health  # Enhanced API V2.1"
echo ""
echo "7. 📄 Tests avec fichiers:"
echo "   python test_matching_system.py --cv '~/Desktop/BATU Sam.pdf' --job '~/Desktop/IT .pdf'"
echo ""

echo "🚀 === DÉMARRAGE RAPIDE ==="
echo ""
echo "Si vous voulez tout résoudre en une commande:"
echo ""
echo "   chmod +x fix_and_test_complete.sh && ./fix_and_test_complete.sh"
echo ""

echo "✅ Configuration terminée ! Tous les scripts sont prêts à être utilisés."
