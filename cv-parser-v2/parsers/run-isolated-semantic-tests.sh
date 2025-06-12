#!/usr/bin/env bash
# Script pour exécuter les tests isolés de l'analyseur sémantique

# S'assurer que le répertoire test_isolated existe
if [ ! -d "test_isolated" ]; then
    mkdir -p test_isolated
    echo "Répertoire test_isolated créé"
fi

# Rendre le script de test exécutable
chmod +x test_isolated/test_semantic.py

# Exécuter le test
echo "=== Exécution des tests isolés de l'analyseur sémantique ==="
cd test_isolated
python3 test_semantic.py

# Vérifier le code de retour
if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Tous les tests ont réussi!"
    echo ""
    echo "Pour intégrer l'analyseur sémantique au moteur de matching, veuillez suivre les instructions dans README-SEMANTIC-INTEGRATION.md"
else
    echo ""
    echo "✗ Certains tests ont échoué. Veuillez consulter les messages d'erreur ci-dessus."
fi
