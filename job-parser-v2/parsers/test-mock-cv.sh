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

# Vérification de l'existence du fichier CV
if [ ! -f "$CV_PATH" ]; then
  print_message "Le fichier CV n'existe pas: $CV_PATH" "$RED"
  print_message "Veuillez spécifier le chemin vers votre CV:" "$YELLOW"
  print_message "./test-mock-cv.sh /chemin/vers/votre/cv.pdf" "$YELLOW"
  exit 1
fi

print_message "Utilisation du CV: $CV_PATH" "$GREEN"

# Vérification si le service cv-parser est en cours d'exécution
if ! docker ps | grep -q "nexten-cv-parser"; then
  print_message "Le service cv-parser n'est pas en cours d'exécution." "$RED"
  print_message "Activation du mode mock et démarrage du service..." "$YELLOW"
  
  # Création d'un fichier .env temporaire
  TEMP_ENV=$(mktemp)
  cat << EOF > "$TEMP_ENV"
# Configuration temporaire pour le mode mock
USE_MOCK_PARSER=true
OPENAI_API_KEY=not-needed-in-mock-mode
OPENAI=not-needed-in-mock-mode
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/nexten
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=storage:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
WEBHOOK_SECRET=your-webhook-secret-here
EOF

  # Copier le fichier .env temporaire
  cp "$TEMP_ENV" .env
  cp "$TEMP_ENV" cv-parser-service/.env
  
  # Nettoyage
  rm "$TEMP_ENV"
  
  # Redémarrage des services avec le mode mock activé
  print_message "Redémarrage des services avec le mode mock activé..." "$BLUE"
  docker-compose stop cv-parser cv-parser-worker
  docker-compose up -d cv-parser cv-parser-worker
  
  # Attendre que les services soient prêts
  print_message "Attente que les services soient prêts..." "$BLUE"
  sleep 10
else
  print_message "Le service cv-parser est en cours d'exécution." "$GREEN"
  print_message "Activation du mode mock..." "$BLUE"
  
  # Vérifier si le mode mock est déjà activé
  current_mode=$(docker exec nexten-cv-parser cat /app/.env 2>/dev/null | grep USE_MOCK_PARSER || echo "USE_MOCK_PARSER=false")
  
  if [[ "$current_mode" == *"true"* ]]; then
    print_message "Le mode mock est déjà activé!" "$GREEN"
  else
    print_message "Mode mock non activé. Tentative d'activation..." "$YELLOW"
    
    # Création d'un fichier .env temporaire
    TEMP_ENV=$(mktemp)
    cat << EOF > "$TEMP_ENV"
# Configuration temporaire pour le mode mock
USE_MOCK_PARSER=true
OPENAI_API_KEY=not-needed-in-mock-mode
OPENAI=not-needed-in-mock-mode
EOF
    
    # Copier le fichier .env temporaire
    cp "$TEMP_ENV" .env
    cp "$TEMP_ENV" cv-parser-service/.env
    
    # Nettoyage
    rm "$TEMP_ENV"
    
    # Redémarrage des services
    print_message "Redémarrage des services avec le mode mock activé..." "$BLUE"
    docker-compose restart cv-parser cv-parser-worker
    
    # Attendre que les services soient prêts
    print_message "Attente que les services soient prêts..." "$BLUE"
    sleep 10
  fi
fi

# Déterminer l'URL de l'API
print_message "Détermination de l'URL de l'API..." "$BLUE"
API_PORT=""
API_PREFIX=""

# Essayer différents ports
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
    print_message "Service répond sur le port $port (sans endpoint /health)" "$YELLOW"
    API_PORT=$port
    break
  fi
done

if [ -z "$API_PORT" ]; then
  print_message "Impossible de trouver le service sur aucun port." "$RED"
  print_message "Utilisation du port par défaut 5051..." "$YELLOW"
  API_PORT=5051
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

# Tester différents endpoints de parsing
print_message "Envoi du CV au service de parsing en mode mock ($API_URL)..." "$BLUE"

endpoints=("/parse" "/parse-cv" "/parse_cv" "/api/parse" "/api/v1/parse")
success=false

for endpoint in "${endpoints[@]}"; do
  print_message "Tentative avec: $API_URL$endpoint" "$BLUE"
  response=$(curl -s -X POST -F "file=@$CV_PATH" "$API_URL$endpoint" 2>&1)
  
  # Vérifier si la réponse n'est pas vide et ne contient pas d'erreur curl
  if [[ -n "$response" && "$response" != *"curl"* && "$response" != *"Failed"* ]]; then
    # Vérifier si la réponse ressemble à du JSON
    if [[ "$response" == *"{"* && "$response" == *"}"* ]]; then
      print_message "Succès avec endpoint: $endpoint" "$GREEN"
      success=true
      break
    fi
  fi
done

if [ "$success" != true ]; then
  print_message "Échec avec tous les endpoints. Tentative avec l'API directe sur le port 5051..." "$YELLOW"
  response=$(curl -s -X POST -F "file=@$CV_PATH" "http://localhost:5051/api/v1/parse" 2>&1)
  
  if [[ -n "$response" && "$response" != *"curl"* && "$response" != *"Failed"* ]]; then
    if [[ "$response" == *"{"* && "$response" == *"}"* ]]; then
      print_message "Succès avec l'API directe!" "$GREEN"
      success=true
    fi
  fi
fi

if [ "$success" != true ]; then
  print_message "Toutes les tentatives ont échoué." "$RED"
  print_message "Réponse de la dernière tentative:" "$RED"
  echo "$response"
  exit 1
fi

# Afficher le résultat
print_message "\n--- RÉSULTAT DU PARSING (MODE MOCK) ---\n" "$GREEN"
echo "$response"

# Sauvegarder le résultat
output_file="resultat_mock_cv.json"
echo "$response" > "$output_file"
print_message "\nLe résultat a été sauvegardé dans $output_file" "$GREEN"

print_message "\nTest du parser de CV en mode mock terminé avec succès!" "$GREEN"