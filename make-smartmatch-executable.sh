#!/bin/bash

# Script pour rendre les fichiers du système SmartMatch exécutables

# Rendre le script de test exécutable
chmod +x test_smartmatch.py
echo "Le script de test test_smartmatch.py est maintenant exécutable."

# Rendre le fichier principal exécutable
chmod +x main.py
echo "Le fichier main.py est maintenant exécutable."

# Vérifier si le dossier test_results existe, sinon le créer
if [ ! -d "test_results" ]; then
    mkdir -p test_results
    echo "Le dossier test_results a été créé."
fi

# Vérifier si le dossier test_data existe, sinon le créer
if [ ! -d "test_data" ]; then
    mkdir -p test_data
    echo "Le dossier test_data a été créé."
fi

echo "Configuration terminée. Vous pouvez maintenant exécuter './test_smartmatch.py' pour tester le système."