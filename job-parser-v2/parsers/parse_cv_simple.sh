#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:8000/api"  # URL du service cv-parser sur le port 8000
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

# Test de connectivité avec le service
print_message "Test de connectivité avec le service cv-parser..." "$BLUE"
health_check=$(curl -s --connect-timeout 5 http://localhost:8000/health || echo "failed")

if [[ "$health_check" == "failed" ]]; then
  print_message "Erreur : Impossible de se connecter au service cv-parser." "$RED"
  print_message "Vérifiez que le service est bien démarré avec la commande:" "$YELLOW"
  print_message "docker-compose ps cv-parser" "$YELLOW"
  print_message "Si nécessaire, redémarrez le service avec:" "$YELLOW"
  print_message "./restart-cv-parser.sh" "$YELLOW"
  exit 1
fi

print_message "Service cv-parser accessible!" "$GREEN"

# Envoi du fichier PDF à l'API
print_message "Envoi du CV à l'API..." "$BLUE"

if [ "$REFRESH" = true ]; then
  print_message "Mode refresh activé: traitement sans cache" "$YELLOW"
  response=$(curl -s -X POST -F "file=@$PDF_PATH" -F "force_refresh=true" "$API_URL/parse-cv/")
else
  response=$(curl -s -X POST -F "file=@$PDF_PATH" "$API_URL/parse-cv/")
fi

# Vérification si la requête a réussi
if [ $? -ne 0 ]; then
  print_message "Erreur : Impossible de se connecter à l'API." "$RED"
  exit 1
fi

# Affichage du résultat
print_message "Résultat du parsing :" "$GREEN"
echo "$response" | jq '.'

# Sauvegarde du résultat dans un fichier
echo "$response" > result_final.json

if [ $? -ne 0 ]; then
  print_message "Erreur : Impossible de sauvegarder le résultat dans 'result_final.json'." "$RED"
  exit 1
fi

print_message "Le résultat a été sauvegardé dans 'result_final.json'" "$GREEN"