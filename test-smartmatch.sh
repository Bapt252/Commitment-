#!/bin/bash

# Script pour exécuter les tests SmartMatch

# Vérifier si les fichiers de test sont exécutables, sinon les rendre exécutables
if [ ! -x "run_tests.py" ]; then
    echo "Rendant les tests exécutables..."
    chmod +x make-tests-executable.sh
    ./make-tests-executable.sh
fi

# Vérifier si un argument a été passé (type de test)
if [ -z "$1" ]; then
    # Aucun argument, exécuter tous les tests
    echo "Exécution de tous les tests SmartMatch..."
    python run_tests.py
else
    # Exécuter le type de test spécifié
    echo "Exécution des tests SmartMatch de type $1..."
    python run_tests.py --type "$1"
fi
