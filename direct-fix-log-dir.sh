#!/bin/bash

# Script pour corriger directement le problème LOG_DIR dans le conteneur sans reconstruire l'image

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

# Vérifier si le conteneur est en cours d'exécution
if ! docker ps | grep -q nexten-job-parser; then
  log_error "Le conteneur nexten-job-parser n'est pas en cours d'exécution."
  log_info "Démarrage du service job-parser..."
  docker-compose up -d job-parser
  sleep 3
fi

# Créer un fichier temporaire avec les paramètres de configuration de journalisation
log_info "Préparation des paramètres de configuration de journalisation..."
cat > /tmp/log_config.txt << 'EOL'

# Configuration de journalisation
LOG_DIR: str = os.environ.get('LOG_DIR') or 'logs'
LOG_LEVEL: str = os.environ.get('LOG_LEVEL') or 'INFO'
LOG_FORMAT: str = os.environ.get('LOG_FORMAT') or 'text'  # 'text' ou 'json'
EOL

# Copier le fichier dans le conteneur
log_info "Copie des paramètres de configuration dans le conteneur..."
docker cp /tmp/log_config.txt nexten-job-parser:/tmp/log_config.txt

# Créer le répertoire de logs dans le conteneur
log_info "Création du répertoire de logs dans le conteneur..."
docker exec nexten-job-parser bash -c 'mkdir -p /app/logs && chmod 777 /app/logs'

# Ajouter les paramètres de configuration au fichier config.py
log_info "Ajout des paramètres de configuration au fichier config.py..."
docker exec nexten-job-parser bash -c 'cat /tmp/log_config.txt >> /app/app/core/config.py'

# Nettoyer le fichier temporaire
rm /tmp/log_config.txt

# Redémarrer le service
log_info "Redémarrage du service job-parser..."
docker-compose restart job-parser

# Attendre que le service démarre
sleep 5

# Vérifier si le service démarre correctement
if docker ps | grep -q nexten-job-parser; then
  log_success "Le service job-parser a été redémarré avec succès!"
  
  # Afficher les logs pour vérifier le démarrage
  log_info "Affichage des derniers logs du service:"
  docker-compose logs --tail=20 job-parser
else
  log_error "Le service job-parser semble avoir des problèmes de démarrage."
  log_info "Affichage des logs complets pour diagnostic:"
  docker-compose logs job-parser
fi

log_success "Correction terminée. Vous pouvez maintenant tester le service avec le script test-job-parser.sh."
