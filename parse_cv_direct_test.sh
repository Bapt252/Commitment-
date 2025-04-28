#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configuration
CV_PATH="$HOME/Desktop/MonSuperCV.pdf"
API_URL="http://localhost:8000"  # URL du service cv-parser

# Fonction pour afficher les messages
print_message() {
  echo -e "${2}${1}${NC}"
}

# Vérification de l'existence du fichier
if [ ! -f "$CV_PATH" ]; then
  print_message "❌ Erreur : fichier CV introuvable : $CV_PATH" "$RED"
  exit 1
fi

print_message "Le fichier CV a été trouvé : $CV_PATH" "$GREEN"

# Test de connectivité avec le service
print_message "Test de connectivité avec le service cv-parser..." "$BLUE"
health_check=$(curl -s --connect-timeout 5 $API_URL/health || echo "failed")

if [[ "$health_check" == "failed" ]]; then
  print_message "Erreur : Impossible de se connecter au service cv-parser." "$RED"
  print_message "Vérifiez que le service est bien démarré." "$YELLOW"
  exit 1
fi

print_message "Service cv-parser accessible!" "$GREEN"

# Création d'un fichier temporaire avec la commande curl
print_message "Préparation de l'appel API..." "$BLUE"

# Créer un fichier temporaire pour stocker le résultat
TMP_FILE=$(mktemp)

# Etape 1: Envoi du CV au service pour mise en file d'attente
print_message "Etape 1: Mise en file d'attente du CV..." "$BLUE"
response=$(curl -s -X POST \
  $API_URL/api/queue \
  -F "file=@$CV_PATH" \
  -F "priority=premium")  # Priorité premium pour traitement rapide

# Extraire le job_id de la réponse
job_id=$(echo $response | grep -o '"job_id":"[^"]*' | cut -d'"' -f4)

if [ -z "$job_id" ]; then
  print_message "Erreur : Impossible d'obtenir un job_id valide." "$RED"
  print_message "Réponse reçue : $response" "$YELLOW"
  exit 1
fi

print_message "Job ID obtenu : $job_id" "$GREEN"

# Etape 2: Attente et récupération du résultat
print_message "Etape 2: Attente du traitement et récupération du résultat..." "$BLUE"

attempts=0
max_attempts=30  # 30 essais (30 secondes)
status="pending"

while [ "$status" == "pending" ] || [ "$status" == "queued" ] || [ "$status" == "running" ]; do
  # Incrémenter le nombre de tentatives
  attempts=$((attempts+1))
  
  if [ $attempts -gt $max_attempts ]; then
    print_message "Timeout: le traitement prend trop de temps." "$RED"
    exit 1
  fi
  
  # Vérifier l'état du job
  result=$(curl -s $API_URL/api/result/$job_id)
  status=$(echo $result | grep -o '"status":"[^"]*' | cut -d'"' -f4)
  
  if [ "$status" == "failed" ]; then
    print_message "Le job a échoué!" "$RED"
    print_message "Détails: $result" "$YELLOW"
    exit 1
  elif [ "$status" == "done" ]; then
    print_message "Le job est terminé!" "$GREEN"
    break
  else
    print_message "Statut actuel: $status (tentative $attempts/$max_attempts)" "$BLUE"
    sleep 1  # Attendre 1 seconde avant de réessayer
  fi
done

# Formater et afficher le résultat final
print_message "Résultat du parsing:" "$GREEN"
echo $result | jq '.' || echo $result

# Sauvegarde du résultat dans un fichier
echo $result > cv_parsing_result.json

print_message "Le résultat a été sauvegardé dans 'cv_parsing_result.json'" "$GREEN"
