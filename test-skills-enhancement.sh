#!/bin/bash

# Script pour rendre exécutable et exécuter le test de comparaison des scores de compétences

# Vérifier si le fichier existe
if [ ! -f "matching-service/test_skills_comparison.py" ]; then
    echo "Erreur: Le fichier test_skills_comparison.py n'existe pas dans le dossier matching-service."
    exit 1
fi

# Rendre le script exécutable
chmod +x matching-service/test_skills_comparison.py
echo "Le script de test est maintenant exécutable."

# Se déplacer dans le dossier matching-service
cd matching-service || exit 1

# Exécuter le test
echo "Exécution du test de comparaison des scores de compétences..."
./test_skills_comparison.py

# Vérifier si l'exécution a réussi
if [ $? -eq 0 ]; then
    echo "Test terminé avec succès."
    
    # Vérifier si l'image du graphique a été générée
    if [ -f "skills_score_comparison.png" ]; then
        echo "Le graphique de comparaison a été généré avec succès."
    else
        echo "Avertissement: Le graphique n'a pas été généré."
    fi
else
    echo "Erreur lors de l'exécution du test."
fi

echo "Pour plus d'informations, consultez matching-service/README-SKILLS-ENHANCEMENT.md"
