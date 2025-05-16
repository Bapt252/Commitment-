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

# Définir le répertoire du projet comme le répertoire courant
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo -e "${YELLOW}Démarrage du service adaptateur SmartMatch...${NC}"

# Arrêter et supprimer le conteneur s'il existe déjà
if docker ps -a | grep -q "smartmatch-adapter-service"; then
    echo -e "${YELLOW}Arrêt et suppression du conteneur existant...${NC}"
    docker stop smartmatch-adapter-service > /dev/null 2>&1
    docker rm smartmatch-adapter-service > /dev/null 2>&1
fi

# Construire l'image Docker
echo -e "${YELLOW}Construction de l'image Docker...${NC}"
docker build -t smartmatch-adapter ./data-adapter

# Démarrer le conteneur
echo -e "${YELLOW}Démarrage du service...${NC}"
docker run -d -p 5053:5053 --name smartmatch-adapter-service smartmatch-adapter

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
    
    # Attendre quelques secondes pour s'assurer que le service est prêt
    sleep 2
    
    # Tester le point de terminaison de santé
    echo -e "${YELLOW}Test du point de terminaison de santé...${NC}"
    HEALTH_RESPONSE=$(curl -s http://localhost:5053/api/adapter/health)
    if [[ $HEALTH_RESPONSE == *"\"status\":\"ok\""* ]]; then
        echo -e "${GREEN}Le service répond correctement aux requêtes!${NC}"
    else
        echo -e "${RED}Le service ne répond pas correctement. Réponse: ${HEALTH_RESPONSE}${NC}"
        echo -e "${YELLOW}Consultez les logs pour plus d'informations:${NC}"
        echo -e "${YELLOW}docker logs smartmatch-adapter-service${NC}"
    fi
else
    echo -e "${RED}Erreur lors du démarrage du service.${NC}"
    echo -e "${YELLOW}Consultez les logs pour plus d'informations:${NC}"
    echo -e "${YELLOW}docker logs smartmatch-adapter-service${NC}"
fi

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Opération terminée                     ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo -e "${YELLOW}Pour tester l'API, exécutez:${NC}"
echo -e "${YELLOW}python data-adapter/test_api.py${NC}"