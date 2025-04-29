#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
  echo -e "${2}${1}${NC}"
}

# Configuration par défaut
DEFAULT_CV_PATH="$HOME/Desktop/MonSuperCV.pdf"
CV_PATH="${1:-$DEFAULT_CV_PATH}"

# Vérification si jq est installé
if ! command -v jq &> /dev/null; then
  print_message "jq n'est pas installé. Installation..." "$YELLOW"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew install jq || { print_message "Erreur lors de l'installation de jq. Veuillez l'installer manuellement." "$RED"; exit 1; }
  elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sudo apt-get update && sudo apt-get install -y jq || { print_message "Erreur lors de l'installation de jq. Veuillez l'installer manuellement." "$RED"; exit 1; }
  else
    print_message "Système d'exploitation non supporté pour l'installation automatique de jq. Veuillez l'installer manuellement." "$RED"
    exit 1
  fi
fi

# Vérification de l'existence du fichier CV
if [ ! -f "$CV_PATH" ]; then
  print_message "Le fichier CV n'existe pas: $CV_PATH" "$RED"
  print_message "Veuillez spécifier le chemin vers votre CV:" "$YELLOW"
  print_message "./test-mon-cv.sh /chemin/vers/votre/cv.pdf" "$YELLOW"
  exit 1
fi

print_message "Utilisation du CV: $CV_PATH" "$GREEN"

# Vérification des services Docker
print_message "Vérification des services Docker..." "$BLUE"
if ! docker ps > /dev/null 2>&1; then
  print_message "Docker n'est pas en cours d'exécution ou vous n'avez pas les permissions nécessaires." "$RED"
  exit 1
fi

# Vérifier si le service cv-parser est en cours d'exécution
if ! docker ps | grep -q "nexten-cv-parser"; then
  print_message "Le service cv-parser n'est pas en cours d'exécution." "$RED"
  print_message "Démarrage des services..." "$YELLOW"
  docker-compose up -d cv-parser cv-parser-worker
  sleep 5
else
  print_message "Le service cv-parser est en cours d'exécution." "$GREEN"
fi

# Attendre que le service soit prêt
print_message "Attente que le service soit prêt..." "$BLUE"
max_attempts=10
attempt=1
while [ $attempt -le $max_attempts ]; do
  if curl -s http://localhost:5051/health > /dev/null 2>&1 || curl -s http://localhost:8000/health > /dev/null 2>&1; then
    print_message "Le service cv-parser est prêt!" "$GREEN"
    break
  fi
  
  print_message "Tentative $attempt/$max_attempts - Service non prêt, attente..." "$YELLOW"
  sleep 3
  attempt=$((attempt+1))
done

if [ $attempt -gt $max_attempts ]; then
  print_message "Le service cv-parser n'est pas disponible après $max_attempts tentatives." "$RED"
  print_message "Vérification des ports alternatifs..." "$YELLOW"
  
  # Chercher sur quels ports le service pourrait être accessible
  ports_to_try=(5051 8000 5000)
  for port in "${ports_to_try[@]}"; do
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
      print_message "Service trouvé sur le port $port!" "$GREEN"
      API_PORT=$port
      break
    elif curl -s http://localhost:$port/api/v1/health > /dev/null 2>&1; then
      print_message "Service trouvé sur le port $port avec le préfixe /api/v1!" "$GREEN"
      API_PORT=$port
      API_PREFIX="/api/v1"
      break
    elif curl -s http://localhost:$port > /dev/null 2>&1; then
      print_message "Service répond sur le port $port mais sans endpoint /health" "$YELLOW"
      API_PORT=$port
      break
    fi
  done
  
  if [ -z "$API_PORT" ]; then
    print_message "Impossible de trouver le service sur aucun port." "$RED"
    exit 1
  fi
else
  # Déterminer le port utilisé
  if curl -s http://localhost:5051/health > /dev/null 2>&1; then
    API_PORT=5051
  elif curl -s http://localhost:8000/health > /dev/null 2>&1; then
    API_PORT=8000
  fi
fi

# Configuration de l'API
if [ -z "$API_PREFIX" ]; then
  # Tester différents préfixes possibles
  if curl -s http://localhost:$API_PORT/api/v1/health > /dev/null 2>&1; then
    API_PREFIX="/api/v1"
  elif curl -s http://localhost:$API_PORT/api/health > /dev/null 2>&1; then
    API_PREFIX="/api"
  else
    API_PREFIX=""
  fi
fi

API_URL="http://localhost:$API_PORT$API_PREFIX"

print_message "Envoi du CV au service de parsing ($API_URL/parse)..." "$BLUE"

# Tester l'endpoint principal de parsing
response=$(curl -s -X POST -F "file=@$CV_PATH" "$API_URL/parse" 2>&1)
if [[ $response == *"curl"* && $response == *"Failed"* ]]; then
  print_message "Erreur lors de l'envoi du CV à $API_URL/parse" "$RED"
  print_message "Essai avec un autre endpoint..." "$YELLOW"
  
  # Essayer d'autres endpoints possibles
  endpoints=("/parse-cv" "/parse_cv" "/api/parse" "/api/v1/parse" "/parse")
  for endpoint in "${endpoints[@]}"; do
    print_message "Tentative avec: $API_URL$endpoint" "$BLUE"
    response=$(curl -s -X POST -F "file=@$CV_PATH" "$API_URL$endpoint" 2>&1)
    
    # Vérifier si la réponse est du JSON valide
    if echo "$response" | jq . > /dev/null 2>&1; then
      print_message "Succès avec endpoint: $endpoint" "$GREEN"
      break
    fi
  done
else
  print_message "CV envoyé avec succès!" "$GREEN"
fi

# Vérifier si la réponse est du JSON valide
if ! echo "$response" | jq . > /dev/null 2>&1; then
  print_message "La réponse n'est pas du JSON valide. Réponse brute:" "$RED"
  echo "$response"
  print_message "\nEssai avec l'API directe..." "$YELLOW"
  
  # Dernier recours: essayer avec l'API directe du cv-parser-service
  direct_response=$(curl -s -X POST -F "file=@$CV_PATH" "http://localhost:5051/api/v1/parse" 2>&1)
  if echo "$direct_response" | jq . > /dev/null 2>&1; then
    print_message "Succès avec l'API directe!" "$GREEN"
    response=$direct_response
  else
    print_message "Échec également avec l'API directe. Réponse:" "$RED"
    echo "$direct_response"
    exit 1
  fi
fi

# Afficher le résultat
print_message "\n--- RÉSULTAT DU PARSING ---\n" "$GREEN"
echo "$response" | jq .

# Sauvegarder le résultat
output_file="resultat_mon_cv.json"
echo "$response" > "$output_file"
print_message "\nLe résultat a été sauvegardé dans $output_file" "$GREEN"

# Instructions pour les problèmes
print_message "\nSi vous rencontrez des problèmes:" "$YELLOW"
print_message "1. Vérifiez que vous avez une clé API OpenAI valide dans le fichier .env" "$YELLOW"
print_message "2. Redémarrez les services avec: docker-compose restart cv-parser cv-parser-worker" "$YELLOW"
print_message "3. Consultez les logs avec: docker-compose logs cv-parser" "$YELLOW"