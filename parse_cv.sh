#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8000/api"  # Remplacez par l'URL de votre API
PDF_PATH="/Users/baptistecomas/Desktop/MonSuperCV.pdf"  # Chemin vers le fichier PDF

# Fonction pour afficher les messages
print_message() {
  echo -e "${2}${1}${NC}"
}

# Vérification de l'existence du fichier PDF
if [ ! -f "$PDF_PATH" ]; then
  print_message "Erreur : Le fichier '$PDF_PATH' n'existe pas." "$RED"
  exit 1
fi

print_message "Le fichier PDF a été trouvé : $PDF_PATH" "$GREEN"

# Envoi du fichier PDF à l'API
print_message "Envoi du CV à l'API..." "$BLUE"
response=$(curl -s -X POST -F "file=@$PDF_PATH" "$API_URL/queue")

# Vérification si la requête a réussi
if [ $? -ne 0 ]; then
  print_message "Erreur : Impossible de se connecter à l'API." "$RED"
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