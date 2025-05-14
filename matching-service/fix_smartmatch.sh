#!/bin/bash

# Script pour corriger manuellement l'erreur d'indentation dans smartmatch.py
# À utiliser lorsque les mises à jour Git n'ont pas été synchronisées correctement

echo "Correction de l'erreur d'indentation dans app/smartmatch.py..."

# Vérifier si le fichier existe
if [ ! -f "app/smartmatch.py" ]; then
    echo "Erreur: Le fichier app/smartmatch.py n'existe pas dans le répertoire actuel"
    exit 1
fi

# Créer une sauvegarde du fichier original
cp app/smartmatch.py app/smartmatch.py.bak
echo "Sauvegarde du fichier créée: app/smartmatch.py.bak"

# Rechercher et remplacer la section problématique
sed -i.tmp '/"""/ {
    N
    /"""\ndef load_test_data():/,/"""/ {
        s/"""\ndef load_test_data():\n    """\n    Fonction de compatibilité avec l'\''ancien code\n    """/def load_test_data():\n    """\n    Fonction de compatibilité avec l'\''ancien code\n    """/
    }
}' app/smartmatch.py

echo "Correction terminée"
echo "Vous pouvez maintenant exécuter: ./test_smartmatch.py"
