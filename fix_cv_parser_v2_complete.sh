#!/bin/bash
# 🚀 Script de mise à jour CV Parser V2 - SuperSmartMatch V2.1
# Corrige les problèmes de chemins et fichiers manquants

echo "🚀 MISE À JOUR CV PARSER V2 - SuperSmartMatch V2.1"
echo "=================================================="

# Aller dans le dossier cv-parser-v2
cd cv-parser-v2 || {
    echo "❌ Dossier cv-parser-v2 non trouvé"
    echo "💡 Exécutez ce script depuis le dossier racine du projet"
    exit 1
}

echo "📁 Dossier actuel: $(pwd)"

# Sauvegarder l'ancien app.py
if [ -f "app.py" ]; then
    cp app.py app.py.backup
    echo "💾 Sauvegarde: app.py.backup créée"
fi

# Télécharger le nouveau app.py corrigé
echo "📥 Téléchargement app.py corrigé..."
curl -s -o app.py https://raw.githubusercontent.com/Bapt252/Commitment-/main/cv-parser-v2/app.py

if [ $? -eq 0 ]; then
    echo "✅ app.py mis à jour"
else
    echo "❌ Erreur téléchargement app.py"
    if [ -f "app.py.backup" ]; then
        mv app.py.backup app.py
        echo "↩️ Restauration de la sauvegarde"
    fi
    exit 1
fi

# Créer le dossier parsers s'il n'existe pas
mkdir -p parsers

# Télécharger enhanced-mission-parser.js
echo "📥 Téléchargement enhanced-mission-parser.js..."
curl -s -o parsers/enhanced-mission-parser.js https://raw.githubusercontent.com/Bapt252/Commitment-/main/cv-parser-v2/parsers/enhanced-mission-parser.js

if [ $? -eq 0 ]; then
    echo "✅ enhanced-mission-parser.js créé"
else
    echo "❌ Erreur téléchargement enhanced-mission-parser.js"
fi

# Vérifier si fix-pdf-extraction.js existe déjà
if [ ! -f "parsers/fix-pdf-extraction.js" ]; then
    echo "📥 Téléchargement fix-pdf-extraction.js..."
    curl -s -o parsers/fix-pdf-extraction.js https://raw.githubusercontent.com/Bapt252/Commitment-/main/cv-parser-v2/parsers/fix-pdf-extraction.js
    
    if [ $? -eq 0 ]; then
        echo "✅ fix-pdf-extraction.js créé"
    else
        echo "❌ Erreur téléchargement fix-pdf-extraction.js"
    fi
else
    echo "✅ fix-pdf-extraction.js existe déjà"
fi

# Rendre les fichiers exécutables
chmod +x parsers/*.js

# Vérifier les dépendances Node.js
echo "📦 Vérification des dépendances Node.js..."
if [ ! -f "package.json" ]; then
    echo "🔧 Initialisation npm..."
    npm init -y > /dev/null 2>&1
fi

echo "📦 Installation pdf-parse..."
npm install pdf-parse > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Dépendances Node.js installées"
else
    echo "⚠️ Problème avec les dépendances Node.js"
fi

# Vérification finale
echo ""
echo "🔍 VÉRIFICATION FINALE"
echo "======================"

if [ -f "app.py" ]; then
    echo "✅ app.py: OK"
else
    echo "❌ app.py: MANQUANT"
fi

if [ -f "parsers/fix-pdf-extraction.js" ]; then
    echo "✅ fix-pdf-extraction.js: OK"
else
    echo "❌ fix-pdf-extraction.js: MANQUANT"
fi

if [ -f "parsers/enhanced-mission-parser.js" ]; then
    echo "✅ enhanced-mission-parser.js: OK"
else
    echo "❌ enhanced-mission-parser.js: MANQUANT"
fi

if [ -d "node_modules" ]; then
    echo "✅ Node.js dependencies: OK"
else
    echo "⚠️ Node.js dependencies: PROBLÈME"
fi

echo ""
echo "🎯 PROCHAINES ÉTAPES"
echo "==================="
echo "1. Redémarrer le service CV Parser:"
echo "   python app.py"
echo ""
echo "2. Dans un autre terminal, tester:"
echo "   curl http://localhost:5051/health"
echo ""
echo "3. Tester parsing CV:"
echo "   curl -X POST -F \"file=@~/Desktop/CV\\ TEST/Bcom\\ HR\\ -\\ Candidature\\ de\\ Sam.pdf\" \\"
echo "        -F \"force_refresh=true\" http://localhost:5051/api/parse-cv/"
echo ""
echo "4. Relancer les tests massifs:"
echo "   cd ../  # Retour au dossier racine"
echo "   python enhanced_batch_testing_v2_fixed.py --test-problematic"

echo ""
echo "✅ MISE À JOUR TERMINÉE!"
echo "📋 Logs de sauvegarde disponibles: app.py.backup"
