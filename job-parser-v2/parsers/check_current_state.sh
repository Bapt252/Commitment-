#!/bin/bash
# Vérification de l'état actuel SuperSmartMatch

echo "🔍 Vérification de l'état actuel SuperSmartMatch"
echo "=============================================="

echo ""
echo "📁 Structure des fichiers:"
echo "========================="
ls -la

echo ""
echo "🧪 Fichiers parsers autonomes:"
echo "=============================="
echo -n "fix-pdf-extraction.js: "
[ -f "fix-pdf-extraction.js" ] && echo "✅ Présent" || echo "❌ Absent"

echo -n "super-optimized-parser.js: "
[ -f "super-optimized-parser.js" ] && echo "✅ Présent" || echo "❌ Absent"

echo -n "install-pdf-tools.sh: "
[ -f "install-pdf-tools.sh" ] && echo "✅ Présent" || echo "❌ Absent"

echo ""
echo "🐳 Services Docker actuels:"
echo "==========================="
if command -v docker-compose &> /dev/null; then
    if [ -f "docker-compose.yml" ]; then
        echo "docker-compose.yml trouvé"
        docker-compose ps 2>/dev/null || echo "Aucun service en cours d'exécution"
    else
        echo "❌ docker-compose.yml non trouvé"
    fi
else
    echo "❌ Docker Compose non installé"
fi

echo ""
echo "🔧 Configuration:"
echo "================"
echo -n ".env: "
[ -f ".env" ] && echo "✅ Présent" || echo "❌ Absent"

echo -n ".env.example: "
[ -f ".env.example" ] && echo "✅ Présent" || echo "❌ Absent"

echo ""
echo "📄 Fichiers de test:"
echo "==================="
echo -n "cv_christine.pdf: "
[ -f "cv_christine.pdf" ] && echo "✅ Présent" || echo "❌ Absent"

echo -n "fdp.pdf: "
[ -f "fdp.pdf" ] && echo "✅ Présent" || echo "❌ Absent"

echo ""
echo "🌐 Ports actuellement utilisés:"
echo "==============================="
netstat -an | grep LISTEN | grep -E ":505[0-3]|:5070|:3000" 2>/dev/null || echo "Aucun port SuperSmartMatch actif"

echo ""
echo "✅ Vérification terminée!"
