#!/usr/bin/env bash
# Script pour rendre exécutables les scripts de test sémantique

echo "Rendre exécutables les scripts de test sémantique..."

# Rendre le fichier de test principal exécutable
chmod +x semantic_analyzer_test.py
echo "✓ semantic_analyzer_test.py est maintenant exécutable"

# Rendre le script shell exécutable
chmod +x test-semantic-analyzer.sh
echo "✓ test-semantic-analyzer.sh est maintenant exécutable"

echo "Tous les scripts sont maintenant exécutables."
