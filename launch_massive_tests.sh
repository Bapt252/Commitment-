#!/bin/bash

echo "🚀 SuperSmartMatch V2.1 Enhanced - Lancement Tests Massifs"
echo "=========================================================="

# 1. Récupérer les dernières modifications
echo "📥 Récupération des modifications GitHub..."
git pull origin main

# 2. Installer pandas si nécessaire
echo "📦 Vérification des dépendances..."
python3 -c "import pandas" 2>/dev/null || pip install pandas

# 3. Vérifier que les 3 services tournent
echo "🔍 Vérification des services..."
echo "   CV Parser V2 (5051):"
curl -s http://localhost:5051/health > /dev/null && echo "   ✅ Opérationnel" || echo "   ❌ Non accessible"

echo "   Job Parser V2 (5053):"
curl -s http://localhost:5053/health > /dev/null && echo "   ✅ Opérationnel" || echo "   ❌ Non accessible"

echo "   Enhanced API V2.1 (5055):"
curl -s http://localhost:5055/health > /dev/null && echo "   ✅ Opérationnel" || echo "   ❌ Non accessible"

echo ""
echo "🎯 PRÊT POUR LES TESTS MASSIFS !"
echo "================================"
echo ""
echo "🚀 Lancement du script de tests massifs..."
echo ""

# 4. Lancer le script de tests massifs
python3 massive_testing_v21_enhanced.py
