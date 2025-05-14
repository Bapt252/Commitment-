#!/bin/bash
# Script pour rendre test-smartmatch-simple.sh exécutable
# Auteur: Claude/Anthropic
# Date: 14/05/2025

echo "Rendre les scripts SmartMatch exécutables..."

# Rendre le script de test simplifié exécutable
chmod +x test-smartmatch-simple.sh
echo "Script test-smartmatch-simple.sh rendu exécutable."

# Si le script de test complet existe, le rendre exécutable aussi
if [ -f "test-smartmatch.sh" ]; then
  chmod +x test-smartmatch.sh
  echo "Script test-smartmatch.sh rendu exécutable."
fi

echo "Terminé!"
echo "Vous pouvez maintenant exécuter ./test-smartmatch-simple.sh pour tester rapidement le système SmartMatch."
