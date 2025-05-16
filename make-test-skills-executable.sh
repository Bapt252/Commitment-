#!/bin/bash

# Script pour rendre le script de test des compétences exécutable
echo "Rendre le script de test exécutable..."
chmod +x test-skills-enhancement.sh
echo "Script test-skills-enhancement.sh est maintenant exécutable"

# Exécuter le script d'installation des dépendances
echo "Installation des dépendances nécessaires..."
pip install sentence-transformers scikit-learn pandas matplotlib tabulate

echo "Vous pouvez maintenant exécuter le test avec:"
echo "./test-skills-enhancement.sh"
