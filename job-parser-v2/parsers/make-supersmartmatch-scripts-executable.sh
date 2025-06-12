#!/bin/bash

# Script pour rendre exécutables les scripts d'intégration SuperSmartMatch
# Usage: ./make-supersmartmatch-scripts-executable.sh

echo "🔧 Configuration des permissions des scripts SuperSmartMatch..."

# Scripts d'intégration SuperSmartMatch
scripts=(
    "quick-supersmartmatch-integration.sh"
    "test-supersmartmatch-integration.sh"
    "make-supersmartmatch-scripts-executable.sh"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "✅ $script rendu exécutable"
    else
        echo "⚠️  $script non trouvé"
    fi
done

echo ""
echo "🎉 Configuration terminée !"
echo ""
echo "💡 Vous pouvez maintenant utiliser :"
echo "   ./quick-supersmartmatch-integration.sh  # Intégration automatique"
echo "   ./test-supersmartmatch-integration.sh   # Tests d'intégration"