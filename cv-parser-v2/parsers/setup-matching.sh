#!/bin/bash

# Script d'installation et de configuration du service de matching SmartMatch

echo "Installation des dépendances pour le service de matching SmartMatch..."
pip install -r requirements-matching.txt

# Créer le répertoire des résultats s'il n'existe pas
mkdir -p matching_results

# Rendre les scripts exécutables
chmod +x run_matching_api.py

echo "Installation terminée avec succès !"
echo "Pour démarrer le service de matching, exécutez la commande :"
echo "python run_matching_api.py"
echo ""
echo "Options disponibles :"
echo "--host : Adresse d'hôte (défaut: 0.0.0.0)"
echo "--port : Port d'écoute (défaut: 5052)"
echo "--debug : Activer le mode debug"
echo "--cv-parser-url : URL du service de parsing de CV (défaut: http://localhost:5051)"
echo "--job-parser-url : URL du service de parsing de fiches de poste (défaut: http://localhost:5055)"
echo "--results-dir : Répertoire pour stocker les résultats (défaut: matching_results)"
