#!/bin/bash

# Script pour tester le service de parsing de fiches de poste

# Vérifier si un argument a été fourni
if [ -z "$1" ]; then
  echo "Usage: $0 <chemin_vers_fichier_poste>"
  echo "Exemple: $0 ~/Desktop/fiche_poste.pdf"
  exit 1
fi

# Vérifier que le fichier existe
if [ ! -f "$1" ]; then
  echo "Erreur: Le fichier '$1' n'existe pas."
  exit 1
fi

echo "Test du service de parsing de fiches de poste"

# Vérifier si le service est en cours d'exécution
echo "Vérification de la santé du service..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5053/health || echo "000")

if [ "$HEALTH_CHECK" != "200" ]; then
  echo "Erreur: Le service ne répond pas (code HTTP: $HEALTH_CHECK)."
  echo "Assurez-vous que le service est démarré avec docker-compose up -d job-parser"
  exit 1
fi

# Tester le parsing
echo "Test du parsing d'une fiche de poste..."
curl -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$1" \
  -F "force_refresh=false"

echo "Test terminé."