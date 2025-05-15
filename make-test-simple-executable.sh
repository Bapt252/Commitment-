#!/bin/bash
#
# Script pour rendre le script de test d'intégration exécutable
#

# Rendre le script de test exécutable
chmod +x test_smartmatch_simple.py

echo "Le script de test d'intégration est maintenant exécutable."
echo "Vous pouvez l'exécuter avec: ./test_smartmatch_simple.py --cv path/to/cv.pdf --job 'Description du poste'"
echo "Ou avec un fichier de poste: ./test_smartmatch_simple.py --cv path/to/cv.pdf --job-file path/to/job.txt"
