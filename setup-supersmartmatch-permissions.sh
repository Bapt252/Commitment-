#!/bin/bash

# Rendre tous les scripts SuperSmartMatch exécutables

echo "🔧 Configuration des permissions pour SuperSmartMatch..."

# Scripts principaux
chmod +x fix-supersmartmatch.sh
chmod +x test-integration-nexten.sh

echo "✅ Scripts SuperSmartMatch configurés"
echo ""
echo "🚀 Utilisation:"
echo "   1. ./fix-supersmartmatch.sh           # Corriger et installer SuperSmartMatch"
echo "   2. ./start-supersmartmatch.sh         # Démarrer le service (créé par le script fix)"
echo "   3. ./test-integration-nexten.sh       # Tester l'intégration avec Nexten"
echo ""
echo "📖 Guide complet: SUPERSMARTMATCH-QUICKSTART.md"
