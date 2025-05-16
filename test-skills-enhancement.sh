#!/bin/bash

# Script pour exécuter les tests de comparaison des scores de compétences

# Afficher un en-tête informatif
echo "==============================================================="
echo "  Test de comparaison des scores de compétences pour SmartMatch"
echo "==============================================================="
echo ""
echo "Ce script compare les performances de l'algorithme original et"
echo "de l'algorithme amélioré de calcul des scores de compétences."
echo ""

# Vérifier si nous sommes dans le bon répertoire
if [ ! -d "matching-service" ]; then
    echo "Erreur: Vous devez exécuter ce script depuis la racine du projet."
    echo "Aucun répertoire 'matching-service' trouvé."
    exit 1
fi

cd matching-service || exit 1

# Vérifier si le fichier de test existe
if [ ! -f "test_skills_comparison.py" ]; then
    echo "Erreur: Le fichier test_skills_comparison.py n'existe pas."
    exit 1
fi

# Installez les dépendances requises
echo "Installation des dépendances requises..."
pip install -q sentence-transformers scikit-learn pandas matplotlib tabulate

# Rendre le script exécutable
chmod +x test_skills_comparison.py

# Exécuter le test
echo "Exécution du test de comparaison..."
./test_skills_comparison.py

# Vérifier si le graphique a été généré
if [ -f "skills_score_comparison.png" ]; then
    echo ""
    echo "Le graphique de comparaison a été généré avec succès: skills_score_comparison.png"
    
    # Tenter d'afficher l'image sur macOS ou Linux
    if [ "$(uname)" = "Darwin" ]; then
        # macOS
        open skills_score_comparison.png
    elif [ "$(uname)" = "Linux" ]; then
        # Linux avec xdg-open
        if command -v xdg-open &> /dev/null; then
            xdg-open skills_score_comparison.png
        else
            echo "Pour visualiser le graphique, ouvrez le fichier manuellement."
        fi
    else
        echo "Pour visualiser le graphique, ouvrez le fichier manuellement."
    fi
else
    echo ""
    echo "Remarque: Le graphique de comparaison n'a pas été généré."
    echo "Cela peut être dû à un problème avec matplotlib ou pandas."
fi

echo ""
echo "Pour plus d'informations, consultez README-SKILLS-ENHANCEMENT.md"
echo ""
echo "==============================================================="