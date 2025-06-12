#!/bin/bash
# Script pour reconstruire tous les services Docker proprement, sans utiliser le cache

# Définir les couleurs pour la sortie
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}= Rebuilding all Docker services clean =${NC}"
echo -e "${BLUE}=========================================${NC}"

# Arrêt des containers
echo -e "${YELLOW}Stopping all containers...${NC}"
docker-compose down
echo -e "${GREEN}Containers stopped.${NC}"

# Suppression des images
echo -e "${YELLOW}Removing related Docker images...${NC}"
docker rmi $(docker images | grep 'commitment-' | awk '{print $3}') 2>/dev/null || true
echo -e "${GREEN}Images removed.${NC}"

# Nettoyage du cache Docker
echo -e "${YELLOW}Cleaning Docker build cache...${NC}"
docker builder prune -f
echo -e "${GREEN}Docker cache cleaned.${NC}"

# Reconstruction de tous les services sans cache
echo -e "${YELLOW}Rebuilding all services without cache...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}Services rebuilt without cache.${NC}"

# Démarrage des containers
echo -e "${YELLOW}Starting all containers...${NC}"
docker-compose up -d
echo -e "${GREEN}All containers started.${NC}"

# Vérification de l'état
echo -e "${YELLOW}Checking container status...${NC}"
docker-compose ps

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}= Rebuild completed. Check logs for any errors.  =${NC}"
echo -e "${BLUE}=================================================${NC}"
