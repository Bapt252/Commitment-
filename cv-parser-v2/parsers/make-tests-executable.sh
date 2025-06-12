#!/bin/bash

# Script pour rendre les tests exécutables

# Rendre les fichiers de test exécutables
chmod +x tests/test_*.py
chmod +x run_tests.py

echo "Les tests sont maintenant exécutables."

# Vérifier si le répertoire test_data existe, sinon le créer
if [ ! -d "test_data" ]; then
    mkdir -p test_data
    echo "Répertoire test_data créé."
fi

# Générer des données de test si le répertoire est vide
if [ -z "$(ls -A test_data 2>/dev/null)" ]; then
    echo "Génération des données de test..."
    python -m tests.test_data_generator
fi

echo "Configuration des tests terminée."
