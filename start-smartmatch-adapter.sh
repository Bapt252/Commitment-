#!/bin/bash

# Script pour démarrer le service adaptateur SmartMatch

# Couleurs pour le texte
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  SmartMatch Adapter Service Launcher    ${NC}"
echo -e "${BLUE}==========================================${NC}"

# Vérifier si docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi

# Vérifier si docker-compose est installé
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
    exit 1
fi

# Définir le répertoire du projet comme le répertoire courant
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo -e "${YELLOW}Démarrage du service adaptateur SmartMatch...${NC}"

# Si un fichier override existe déjà, le sauvegarder
if [ -f docker-compose.override.yml ]; then
    echo -e "${YELLOW}Sauvegarde du fichier docker-compose.override.yml existant...${NC}"
    mv docker-compose.override.yml docker-compose.override.yml.bak
fi

# Copier le fichier override de l'adaptateur
echo -e "${YELLOW}Utilisation du fichier de configuration spécifique à l'adaptateur...${NC}"
cp data-adapter/docker-compose.override.yml .

# Construire et démarrer le service
echo -e "${YELLOW}Construction de l'image Docker...${NC}"
docker-compose build smartmatch-adapter

echo -e "${YELLOW}Démarrage du service...${NC}"
docker-compose up -d smartmatch-adapter

# Vérifier si le service a démarré avec succès
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Le service adaptateur SmartMatch a démarré avec succès!${NC}"
    echo -e "${GREEN}Il est accessible à l'adresse: http://localhost:5053${NC}"
    echo -e "${GREEN}Endpoints disponibles:${NC}"
    echo -e "${GREEN}- GET  /api/adapter/health: Vérifier la disponibilité du service${NC}"
    echo -e "${GREEN}- POST /api/adapter/adapt-cv: Adapter un CV${NC}"
    echo -e "${GREEN}- POST /api/adapter/adapt-job: Adapter une offre d'emploi${NC}"
    echo -e "${GREEN}- POST /api/adapter/batch-adapt-cv: Adapter plusieurs CVs${NC}"
    echo -e "${GREEN}- POST /api/adapter/batch-adapt-job: Adapter plusieurs offres d'emploi${NC}"
    echo -e "${GREEN}- POST /api/adapter/match: Adapter les données puis lancer le matching${NC}"
else
    echo -e "${RED}Erreur lors du démarrage du service.${NC}"
    echo -e "${YELLOW}Consultez les logs pour plus d'informations:${NC}"
    echo -e "${YELLOW}docker-compose logs smartmatch-adapter${NC}"
fi

# Restaurer le fichier override original si nécessaire
if [ -f docker-compose.override.yml.bak ]; then
    echo -e "${YELLOW}Restauration du fichier docker-compose.override.yml original...${NC}"
    mv docker-compose.override.yml.bak docker-compose.override.yml
fi

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Opération terminée                     ${NC}"
echo -e "${BLUE}==========================================${NC}"
