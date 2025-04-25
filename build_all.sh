#!/bin/bash

# Couleurs pour le terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Starting NexTen Project Rebuild...${NC}\n"

# Étape 1: Arrêter les services en cours
echo -e "${GREEN}1. Stopping running services...${NC}"
docker-compose down --remove-orphans
echo -e "${GREEN}✓ Services stopped${NC}\n"

# Étape 2: Supprimer les volumes obsolètes
echo -e "${GREEN}2. Removing obsolete volumes...${NC}"
docker volume prune -f
echo -e "${GREEN}✓ Volumes cleaned${NC}\n"

# Étape 3: Supprimer les images existantes
echo -e "${GREEN}3. Removing existing images...${NC}"
docker-compose rm -f
docker image prune -f
echo -e "${GREEN}✓ Images cleaned${NC}\n"

# Étape 4: Vérifier les fichiers requirements.txt
echo -e "${GREEN}4. Checking requirements.txt files...${NC}"
if [ ! -f "cv-parser-service/requirements.txt" ]; then
    echo -e "${RED}❌ cv-parser-service/requirements.txt not found!${NC}"
    exit 1
fi
if [ ! -f "matching-service/requirements.txt" ]; then
    echo -e "${RED}❌ matching-service/requirements.txt not found!${NC}"
    exit 1
fi
if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${RED}❌ backend/requirements.txt not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ All requirements.txt files found${NC}\n"

# Étape 5: Rebuild avec no-cache
echo -e "${GREEN}5. Rebuilding all services (no cache)...${NC}"
docker-compose build --no-cache
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed! Check the logs above.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Build successful${NC}\n"

# Étape 6: Démarrer les services
echo -e "${GREEN}6. Starting services...${NC}"
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start services!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Services started${NC}\n"

# Étape 7: Vérifier le statut des containers
echo -e "${GREEN}7. Checking container status...${NC}"
docker-compose ps
echo ""

# Étape 8: Afficher les logs pour debug (optionnel)
echo -e "${YELLOW}📋 Do you want to see the logs? (y/n)${NC}"
read -r answer
if [ "$answer" = "y" ]; then
    docker-compose logs -f --tail=100
fi

echo -e "\n${GREEN}✅ NexTen Project rebuild completed successfully!${NC}"
echo -e "${YELLOW}🌐 Your services should now be running without errors.${NC}"
echo -e "${YELLOW}📊 Check the container status above.${NC}"