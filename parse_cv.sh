#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:5051/api"  # URL du service cv-parser selon docker-compose
REFRESH=false

# Fonction pour afficher les messages
print_message() {
  echo -e "${2}${1}${NC}"
}

# Fonction d'aide
show_usage() {
  print_message "❌ Erreur : fichier introuvable → " "$RED"
  print_message "🧾 Utilisation : $0 [--refresh] \n/chemin/vers/fichier.pdf" "$YELLOW"
  print_message "  --refresh  : force le parsing (sans \ncache)" "$YELLOW"
  exit 1
}

# Traitement des arguments
if [ $# -eq 0 ]; then
  # Si aucun argument, utiliser le chemin par défaut
  PDF_PATH="$HOME/Desktop/MonSuperCV.pdf"
else
  # Traiter les arguments
  while [[ $# -gt 0 ]]; do
    case $1 in
      --refresh)
        REFRESH=true
        shift
        ;;
      *)
        PDF_PATH="$1"
        shift
        ;;
    esac
  done
fi

# Vérification de l'existence du fichier PDF
if [ ! -f "$PDF_PATH" ]; then
  show_usage
fi

print_message "Le fichier PDF a été trouvé : $PDF_PATH" "$GREEN"

# Envoi du fichier PDF à l'API
print_message "Envoi du CV à l'API..." "$BLUE"

if [ "$REFRESH" = true ]; then
  response=$(curl -s -X POST -F "file=@$PDF_PATH" -F "force_refresh=true" "$API_URL/queue")
else
  response=$(curl -s -X POST -F "file=@$PDF_PATH" "$API_URL/queue")
fi

# Vérification si la requête a réussi
if [ $? -ne 0 ]; then
  print_message "Erreur : Impossible de se connecter à l'API." "$RED"
  print_message "Vérifiez que le service cv-parser est bien en cours d'exécution sur le port 5051." "$YELLOW"
  exit 1
fi

# Extraction du job_id
job_id=$(echo "$response" | jq -r '.job_id')

if [ -z "$job_id" ] || [ "$job_id" == "null" ]; then
  print_message "Erreur : Impossible d'obtenir le job_id. Réponse de l'API :" "$RED"
  echo "$response" | jq '.'
  exit 1
fi

print_message "CV soumis avec succès! Job ID: $job_id" "$GREEN"

# Attente que le parsing soit terminé
print_message "Attente que le parsing soit terminé..." "$BLUE"
status="pending"
attempts=0
max_attempts=60  # Timeout après 5 minutes (60 * 5 secondes)

while [ "$status" == "pending" ] && [ $attempts -lt $max_attempts ]; do
  sleep 5
  ((attempts++))
  
  status_response=$(curl -s -X GET "$API_URL/status/$job_id")
  
  if [ $? -ne 0 ]; then
    print_message "Erreur lors de la vérification du statut. Nouvel essai..." "$RED"
    continue
  fi
  
  status=$(echo "$status_response" | jq -r '.status')
  
  if [ -z "$status" ] || [ "$status" == "null" ]; then
    print_message "Erreur : Impossible d'obtenir le statut. Réponse de l'API :" "$RED"
    echo "$status_response" | jq '.'
    exit 1
  fi
  
  print_message "Statut actuel : $status (tentative $attempts/$max_attempts)" "$BLUE"
  
  # Si le statut est "error", on arrête et on affiche l'erreur
  if [ "$status" == "error" ]; then
    print_message "Erreur pendant le parsing du CV. Détails :" "$RED"
    echo "$status_response" | jq '.'
    exit 1
  fi
done

# Vérification du timeout
if [ $attempts -ge $max_attempts ]; then
  print_message "Timeout : Le parsing prend trop de temps. Abandon." "$RED"
  exit 1
fi

# Récupération du résultat final
print_message "Parsing terminé ! Récupération du résultat..." "$GREEN"
result=$(curl -s -X GET "$API_URL/result/$job_id")

if [ $? -ne 0 ]; then
  print_message "Erreur : Impossible de récupérer le résultat." "$RED"
  exit 1
fi

# Affichage du résultat
print_message "Résultat du parsing :" "$GREEN"
echo "$result" | jq '.'

# Sauvegarde du résultat dans un fichier
echo "$result" > result_final.json

if [ $? -ne 0 ]; then
  print_message "Erreur : Impossible de sauvegarder le résultat dans 'result_final.json'." "$RED"
  exit 1
fi

print_message "Le résultat a été sauvegardé dans 'result_final.json'" "$GREEN"