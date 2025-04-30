#!/bin/bash

echo "Test du service de parsing de fiches de poste"

# Vérifier si le service est en ligne
echo "Vérification de la santé du service..."
curl -s http://localhost:5053/health
echo ""

# Vérifier si un fichier a été spécifié en argument
if [ -z "$1" ]; then
  echo "Aucun fichier spécifié. Usage: $0 <chemin_vers_fichier_fiche_de_poste>"
  exit 1
fi

# Tester le parsing d'une fiche de poste
echo "Test du parsing d'une fiche de poste..."
curl -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$1" \
  -F "force_refresh=true"

echo ""
echo "Test terminé."
