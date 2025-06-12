#!/bin/bash

# Script très simple pour tester le service job-parser

# Fonction pour afficher des messages avec couleurs
log_info() {
  echo -e "\033[0;34m[INFO]\033[0m $1"
}

log_success() {
  echo -e "\033[0;32m[SUCCESS]\033[0m $1"
}

log_error() {
  echo -e "\033[0;31m[ERROR]\033[0m $1"
}

# Créer un fichier de test très simple
log_info "Création d'un fichier de test simple..."
echo "Titre: Développeur Python" > simple-job.txt

# Tester l'API avec curl de base
log_info "Test de l'API avec curl sans formatage..."
curl -v -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@simple-job.txt" \
  -F "force_refresh=false"

# Nettoyage
log_info "Nettoyage..."
rm simple-job.txt

log_info "Test terminé."
