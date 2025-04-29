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

# Vérification de Docker
if ! command -v docker &> /dev/null; then
  print_message "Docker n'est pas installé ou n'est pas dans votre PATH." "$RED"
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  print_message "Docker Compose n'est pas installé ou n'est pas dans votre PATH." "$RED"
  exit 1
fi

# Arrêt des services
print_message "Arrêt des services en cours..." "$BLUE"
docker-compose stop cv-parser cv-parser-worker redis
print_message "Services arrêtés." "$GREEN"

# Suppression des conteneurs (optionnel)
if [[ "$1" == "--clean" ]]; then
  print_message "Nettoyage des conteneurs..." "$BLUE"
  docker-compose rm -f cv-parser cv-parser-worker
  print_message "Conteneurs nettoyés." "$GREEN"
fi

# Démarrage de Redis en premier
print_message "Démarrage de Redis..." "$BLUE"
docker-compose up -d redis
print_message "Attente que Redis soit prêt..." "$BLUE"
sleep 5

# Vérification que Redis est prêt
max_attempts=10
attempt=1
redis_ready=false

while [ $attempt -le $max_attempts ] && [ "$redis_ready" != true ]; do
  if docker exec nexten-redis redis-cli ping | grep -q "PONG"; then
    print_message "Redis est prêt!" "$GREEN"
    redis_ready=true
  else
    print_message "Tentative $attempt/$max_attempts - Redis n'est pas prêt, attente..." "$YELLOW"
    sleep 2
    attempt=$((attempt+1))
  fi
done

if [ "$redis_ready" != true ]; then
  print_message "Redis n'est pas disponible après $max_attempts tentatives." "$RED"
  print_message "Tentative de démarrage des services quand même..." "$YELLOW"
fi

# Reconstruire et démarrer les services du parser de CV
print_message "Reconstruction et démarrage des services du parser de CV..." "$BLUE"
docker-compose up -d --build cv-parser cv-parser-worker

# Attendre que les services soient prêts
print_message "Attente que les services soient prêts..." "$BLUE"
sleep 10

# Vérification des services
print_message "Vérification des services:" "$BLUE"
docker-compose ps cv-parser cv-parser-worker

# Vérification de l'API
print_message "Test de l'API du parser de CV..." "$BLUE"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5051/health 2>/dev/null || echo "failed")

if [[ "$response" == "200" ]]; then
  print_message "L'API du parser de CV est accessible sur le port 5051!" "$GREEN"
elif [[ "$response" != "failed" ]]; then
  print_message "L'API répond avec le code HTTP: $response" "$YELLOW"
else
  print_message "Impossible d'accéder à l'API sur le port 5051. Vérification des ports alternatifs..." "$YELLOW"
  
  # Vérification sur le port 8000
  alt_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "failed")
  if [[ "$alt_response" == "200" ]]; then
    print_message "L'API du parser de CV est accessible sur le port 8000!" "$GREEN"
  elif [[ "$alt_response" != "failed" ]]; then
    print_message "L'API répond sur le port 8000 avec le code HTTP: $alt_response" "$YELLOW"
  else
    print_message "L'API n'est pas accessible sur les ports standard." "$RED"
  fi
fi

# Affichage des logs du service cv-parser
print_message "Voici les derniers logs du service cv-parser:" "$BLUE"
docker-compose logs --tail=20 cv-parser

print_message "\nRedémarrage des services terminé." "$GREEN"
print_message "Pour tester le parser de CV, utilisez: ./test-mon-cv.sh /chemin/vers/MonSuperCV.pdf" "$GREEN"
print_message "Pour voir les logs en temps réel: docker-compose logs -f cv-parser" "$GREEN"