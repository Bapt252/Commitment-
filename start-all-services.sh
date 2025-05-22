#!/bin/bash

# Script de démarrage global pour Commitment
# Auteur: Claude
# Date: Mai 2025

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Démarrage des services Commitment ===${NC}"

# Vérification de l'environnement
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}[WARNING] Fichier .env manquant. Création d'un fichier .env par défaut.${NC}"
  cp .env.example .env || (echo -e "${RED}[ERROR] Impossible de créer .env${NC}" && exit 1)
  echo -e "${YELLOW}[INFO] Veuillez éditer le fichier .env et ajouter votre clé API OpenAI.${NC}"
  sleep 2
fi

# Vérification de Docker
if ! command -v docker >/dev/null 2>&1; then
  echo -e "${RED}[ERROR] Docker n'est pas installé. Veuillez installer Docker avant de continuer.${NC}"
  exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
  echo -e "${RED}[ERROR] Docker Compose n'est pas installé. Veuillez installer Docker Compose avant de continuer.${NC}"
  exit 1
fi

# Variables d'environnement
source .env

if [ -z "$OPENAI" ]; then
  echo -e "${YELLOW}[WARNING] Clé API OpenAI non définie dans .env${NC}"
  read -p "Veuillez entrer votre clé API OpenAI: " OPENAI
  echo "OPENAI=$OPENAI" >> .env
fi

# Arrêter les services existants qui pourraient causer des conflits de port
echo -e "${YELLOW}[INFO] Arrêt des services existants qui pourraient causer des conflits...${NC}"
docker-compose down || true

# Démarrage des services principaux via Docker Compose
echo -e "${YELLOW}[INFO] Démarrage des services principaux via Docker Compose...${NC}"
docker-compose up -d

# Attendre que les services soient prêts
echo -e "${YELLOW}[INFO] Attente du démarrage complet des services...${NC}"
sleep 10

# Fonction pour vérifier l'état d'un service
check_service() {
  local service_url=$1
  local service_name=$2
  local max_retries=$3
  local retry_count=0
  
  echo -e "${YELLOW}[INFO] Vérification du service $service_name ($service_url)...${NC}"
  
  while [ $retry_count -lt $max_retries ]; do
    if curl -s "$service_url/health" > /dev/null; then
      echo -e "${GREEN}[SUCCESS] Service $service_name démarré avec succès!${NC}"
      return 0
    fi
    
    retry_count=$((retry_count+1))
    if [ $retry_count -lt $max_retries ]; then
      echo -e "${YELLOW}[INFO] Tentative $retry_count/$max_retries... Attente de 5 secondes.${NC}"
      sleep 5
    fi
  done
  
  echo -e "${RED}[ERROR] Le service $service_name n'a pas démarré correctement après $max_retries tentatives.${NC}"
  return 1
}

# Vérifier les services principaux
check_service "http://localhost:5051" "Parsing CV" 5 || true
check_service "http://localhost:5055" "Parsing Fiches de Poste" 5 || true
check_service "http://localhost:5052" "Matching" 5 || true
check_service "http://localhost:5060" "Personnalisation" 5 || true
check_service "http://localhost:5057" "Analyse Comportementale" 5 || true

# Afficher l'état des services Docker
echo -e "${YELLOW}[INFO] État des services Docker:${NC}"
docker-compose ps

# Afficher les logs des services qui n'ont pas démarré correctement
if ! check_service "http://localhost:5060" "Personnalisation" 1; then
  echo -e "${YELLOW}[INFO] Logs du service de personnalisation:${NC}"
  docker logs nexten-personalization
fi

if ! check_service "http://localhost:5057" "Analyse Comportementale" 1; then
  echo -e "${YELLOW}[INFO] Logs du service d'analyse comportementale:${NC}"
  docker logs nexten-user-behavior
fi

echo -e "${GREEN}[SUCCESS] Configuration de démarrage de Commitment terminée!${NC}"
echo ""
echo -e "${BLUE}=== Services disponibles ===${NC}"
echo -e "Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "API principale: ${GREEN}http://localhost:5050${NC}"
echo -e "Service de parsing CV: ${GREEN}http://localhost:5051${NC}"
echo -e "Service de parsing fiches de poste: ${GREEN}http://localhost:5055${NC}"
echo -e "Service de matching: ${GREEN}http://localhost:5052${NC}"
echo -e "Service d'analyse comportementale: ${GREEN}http://localhost:5057${NC}"
echo -e "Service de personnalisation: ${GREEN}http://localhost:5060${NC}"
echo -e "MinIO (stockage): ${GREEN}http://localhost:9000${NC} (API) et ${GREEN}http://localhost:9001${NC} (Console)"
echo -e "Redis Commander: ${GREEN}http://localhost:8081${NC}"
echo -e "RQ Dashboard: ${GREEN}http://localhost:9181${NC}"
echo ""
echo -e "Pour plus d'informations, consultez le fichier README.md"
