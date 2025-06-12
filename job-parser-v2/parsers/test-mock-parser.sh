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
  print_message "🔍 Veuillez spécifier le chemin correct de votre CV en modifiant CV_PATH dans ce script." "$YELLOW"
  exit 1
fi

print_message "✅ Le fichier CV a été trouvé : $CV_PATH" "$GREEN"

# Test de connectivité avec le service
print_message "🔄 Test de connectivité avec le service cv-parser..." "$BLUE"
health_check=$(curl -s --connect-timeout 5 $API_URL/health || echo "failed")

if [[ "$health_check" == "failed" ]]; then
  print_message "❌ Erreur : Impossible de se connecter au service cv-parser." "$RED"
  print_message "🔍 Vérifiez que le service est bien démarré avec la commande:" "$YELLOW"
  print_message "   docker-compose ps cv-parser" "$YELLOW"
  print_message "🔄 Si nécessaire, redémarrez le service avec:" "$YELLOW"
  print_message "   ./restart-cv-parser.sh" "$YELLOW"
  exit 1
fi

print_message "✅ Service cv-parser accessible!" "$GREEN"

# Envoi du fichier CV directement à l'API avec mode mock
print_message "📤 Envoi du CV à l'API directe de parsing (mode mock)..." "$BLUE"

# Assurez-vous que le mode mock est activé dans le conteneur
print_message "🔧 Configuration du mode mock..." "$BLUE"
docker exec nexten-cv-parser sh -c "echo 'USE_MOCK_PARSER=true' >> /app/.env"

# Envoi du CV pour parsing avec le mode mock activé
response=$(curl -s -X POST \
  $API_URL/api/parse-cv \
  -F "file=@$CV_PATH" \
  -F "force_refresh=true")

# Vérifier si la réponse contient une erreur
if [[ "$response" == *"\"detail\""* ]]; then
  print_message "❌ Erreur lors du parsing du CV:" "$RED"
  print_message "$response" "$YELLOW"
  exit 1
fi

# Affichage de la réponse
print_message "✅ Réponse du service de parsing (mode mock):" "$GREEN"
echo "$response" | jq '.' || echo "$response"

# Sauvegarde du résultat dans un fichier
echo "$response" > mock_parsing_result.json

print_message "💾 Le résultat a été sauvegardé dans 'mock_parsing_result.json'" "$GREEN"
print_message "📝 Note: Ce résultat a été généré avec le mode mock qui simule l'analyse sans appeler l'API OpenAI." "$YELLOW"
