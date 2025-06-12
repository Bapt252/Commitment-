#!/bin/bash

# Script de test ultra-simple pour tester directement l'API job-parser

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

# Créer un fichier texte minimal
log_info "Création d'un fichier texte minimal..."
echo "Titre: Développeur" > /tmp/minimal.txt

# Tester avec curl simple
log_info "Test avec curl minimal..."
curl -v -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/tmp/minimal.txt" \
  -F "force_refresh=false"

# Nettoyage
rm /tmp/minimal.txt

# Tester avec le fichier PDF du bureau
log_info "Test avec le fichier PDF du bureau..."

# Déterminer le chemin du bureau
DESKTOP_PATH="$HOME/Desktop"
if [ ! -d "$DESKTOP_PATH" ]; then
  # Essayer avec Bureau pour les utilisateurs francophones
  DESKTOP_PATH="$HOME/Bureau"
  if [ ! -d "$DESKTOP_PATH" ]; then
    log_error "Impossible de trouver le dossier du bureau (Desktop/Bureau)."
    exit 1
  fi
fi

# Vérifier si le fichier existe
PDF_PATH="$DESKTOP_PATH/fdp.pdf"
if [ -f "$PDF_PATH" ]; then
  log_info "Fichier PDF trouvé à : $PDF_PATH"
  log_info "Execution de la commande curl directement..."
  
  # Commande curl directe
  curl -v -X POST \
    http://localhost:5053/api/parse-job \
    -H "Content-Type: multipart/form-data" \
    -F "file=@$PDF_PATH" \
    -F "force_refresh=false"
else
  log_error "Le fichier fdp.pdf n'existe pas sur le bureau ($PDF_PATH)."
fi
