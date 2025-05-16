#!/bin/bash

# Script pour exécuter les tests SmartMatch simplifiés

echo "==================================="
echo "Tests SmartMatch - Guide d'utilisation"
echo "==================================="
echo ""
echo "Ce script vous permet de tester l'algorithme SmartMatch avec différentes options."
echo ""
echo "Usage:"
echo "./run_smartmatch_tests.sh [option]"
echo ""
echo "Options:"
echo "  functional    Exécute le test fonctionnel de base (par défaut)"
echo "  unit          Exécute les tests unitaires complets"
echo ""
echo "==================================="

# Vérifier si le répertoire est correct
if [ ! -d "matching-service" ] && [ ! -f "app/smartmatch.py" ]; then
    echo "Erreur: Vous devez exécuter ce script depuis le répertoire racine du projet."
    echo "Ou depuis le sous-répertoire matching-service."
    exit 1
fi

# Vérifier si les scripts de test existent
if [ -d "matching-service" ] && [ ! -f "matching-service/test_functional.py" ]; then
    echo "Erreur: Scripts de test non trouvés."
    echo "Assurez-vous que les fichiers test_functional.py et test_smartmatch_unit_fixed.py existent."
    exit 1
fi

# Vérifier si un argument a été passé (type de test)
if [ -z "$1" ] || [ "$1" = "functional" ]; then
    # Exécuter le test fonctionnel (par défaut)
    echo "Exécution du test fonctionnel SmartMatch..."
    
    if [ -d "matching-service" ]; then
        cd matching-service
    fi
    
    python test_functional.py
elif [ "$1" = "unit" ]; then
    # Exécuter les tests unitaires
    echo "Exécution des tests unitaires SmartMatch..."
    
    if [ -d "matching-service" ]; then
        cd matching-service
    fi
    
    python test_smartmatch_unit_fixed.py
else
    echo "Option non reconnue: $1"
    echo "Utilisez 'functional' ou 'unit'."
    exit 1
fi