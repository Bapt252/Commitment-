#!/bin/bash

# Script pour résoudre les problèmes de Git et reconstruire le service job-parser

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

log_warning() {
  echo -e "\033[0;33m[WARNING]\033[0m $1"
}

# Détecter si nous sommes dans un état de merge non conclu
if [ -f ".git/MERGE_HEAD" ]; then
  log_warning "État de merge Git détecté. Nous allons résoudre ce problème."
  
  # Option 1: Sauvegarder les modifications non commises
  TIMESTAMP=$(date +"%Y%m%d%H%M%S")
  BACKUP_DIR="git-backup-$TIMESTAMP"
  
  log_info "Sauvegarde des modifications non commises dans $BACKUP_DIR/"
  mkdir -p "$BACKUP_DIR"
  
  # Copier les fichiers modifiés
  git status --porcelain | grep -E '^( M|\?\?|A |AM)' | awk '{print $2}' | xargs -I{} cp --parents {} "$BACKUP_DIR/" 2>/dev/null || true
  
  log_info "Modifications sauvegardées dans $BACKUP_DIR/"
  
  # Annuler le merge
  log_info "Annulation du merge en cours..."
  git merge --abort
  
  log_success "Merge annulé avec succès."
fi

# Mettre à jour depuis GitHub
log_info "Récupération des dernières modifications depuis GitHub..."
git fetch origin main

# Remettre à jour la branche locale
log_info "Mise à jour de la branche locale..."
git reset --hard origin/main

log_success "Votre dépôt local est maintenant synchronisé avec GitHub."

# Rendre les scripts exécutables
log_info "Préparation des scripts..."
chmod +x rebuild-job-parser-fixed.sh
chmod +x job-parser-service/fix-indentation.sh
chmod +x job-parser-service/entrypoint.sh

# Reconstruire le service
log_info "Reconstruction du service job-parser..."

# Arrêter le service existant
log_info "Arrêt du service job-parser existant..."
docker-compose stop job-parser
docker-compose rm -f job-parser

# Reconstruire l'image
log_info "Reconstruction de l'image job-parser..."
docker-compose build job-parser

# Démarrer le service
log_info "Démarrage du service job-parser..."
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
  log_info "Affichage des logs pour diagnostic:"
  docker-compose logs job-parser
fi

log_success "Processus de récupération et reconstruction terminé."
