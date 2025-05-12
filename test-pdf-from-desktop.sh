#!/bin/bash

# Script pour tester le service job-parser avec un fichier PDF du bureau

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
if [ ! -f "$PDF_PATH" ]; then
  log_error "Le fichier fdp.pdf n'existe pas sur le bureau."
  log_info "Veuillez vérifier que le fichier existe à l'emplacement : $PDF_PATH"
  exit 1
fi

# Vérifier si le conteneur est en cours d'exécution
if ! docker ps | grep -q nexten-job-parser; then
  log_error "Le conteneur nexten-job-parser n'est pas en cours d'exécution."
  log_info "Démarrage du service job-parser..."
  docker-compose up -d job-parser
  sleep 5
fi

# Tester l'API avec le fichier PDF
log_info "Test de l'API job-parser avec le fichier PDF du bureau..."
log_info "Utilisation du fichier : $PDF_PATH"

# Envoyer la requête
log_info "Envoi de la requête au service job-parser..."
response=$(curl -s -X POST \
  http://localhost:5053/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$PDF_PATH" \
  -F "force_refresh=false")

# Vérifier si la requête a réussi
if [ $? -eq 0 ]; then
  log_success "Requête envoyée avec succès."
  
  # Afficher la réponse de manière formatée
  echo -e "\n\033[0;36m--- Réponse de l'API ---\033[0m"
  echo "$response" | python -m json.tool 2>/dev/null || echo "$response"
  echo -e "\033[0;36m-----------------------\033[0m\n"

  # Sauvegarder la réponse dans un fichier
  echo "$response" > "$DESKTOP_PATH/job_parser_result.json"
  log_info "La réponse a été sauvegardée dans le fichier: $DESKTOP_PATH/job_parser_result.json"
else
  log_error "Échec de la requête."
  echo "$response"
fi

log_info "Test terminé."
