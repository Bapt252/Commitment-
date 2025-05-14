#!/bin/bash

# Script pour reconstruire et redémarrer le service job-parser avec les corrections de journalisation

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

log_info "Début de la reconstruction du service job-parser avec les corrections de journalisation..."

# Mise à jour du dépôt local
log_info "Mise à jour du dépôt local avec les dernières modifications..."
git pull origin main

# Arrêter le service existant
log_info "Arrêt du service job-parser existant..."
docker-compose stop job-parser
docker-compose rm -f job-parser

# Reconstruire l'image avec les nouvelles modifications
log_info "Reconstruction de l'image job-parser..."
docker-compose build job-parser

# Démarrer le service reconstruit
log_info "Démarrage du service job-parser reconstruit..."
docker-compose up -d job-parser

# Vérifier si le service démarre correctement
sleep 5
if docker-compose ps | grep job-parser | grep Up; then
  log_success "Le service job-parser a été démarré avec succès!"
  
  # Afficher les logs pour vérifier le démarrage
  log_info "Affichage des derniers logs du service:"
  docker-compose logs --tail=20 job-parser
else
  log_error "Le service job-parser semble avoir des problèmes de démarrage."
  log_info "Affichage des logs complets pour diagnostic:"
  docker-compose logs job-parser
fi

log_info "Processus de reconstruction terminé."
