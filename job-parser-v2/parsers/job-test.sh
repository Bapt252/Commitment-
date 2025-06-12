#!/bin/bash

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== TEST DU SYSTÈME JOB-PARSER ===${NC}"

# Vérifier si un argument a été fourni
if [ "$#" -ne 1 ]; then
    echo -e "${RED}Usage: $0 <chemin/vers/fichier.pdf>${NC}"
    exit 1
fi

# Vérifier si le fichier existe
if [ ! -f "$1" ]; then
    echo -e "${RED}Le fichier '$1' n'existe pas.${NC}"
    exit 1
fi

echo -e "${YELLOW}Arrêt des services existants...${NC}"
docker-compose stop job-parser job-parser-worker

echo -e "${YELLOW}Suppression des conteneurs...${NC}"
docker-compose rm -f job-parser job-parser-worker

echo -e "${YELLOW}Démarrage des services avec configuration corrigée...${NC}"
docker-compose up -d job-parser job-parser-worker

echo -e "${YELLOW}Attente du démarrage des services (10 secondes)...${NC}"
sleep 10

# Tester la santé du service
echo -e "${YELLOW}Test de la santé du service...${NC}"
PORT=$(docker port nexten-job-parser | grep 5000/tcp | cut -d ':' -f 2 || echo "5053")

if curl -s http://localhost:$PORT/health | grep -q "healthy"; then
    echo -e "${GREEN}Le service est en ligne et répond correctement!${NC}"
else
    echo -e "${RED}Le service ne répond pas correctement. Vérification des logs...${NC}"
    docker logs nexten-job-parser
    exit 1
fi

# Tester le parsing du fichier
echo -e "${YELLOW}Test du parsing du fichier '$1'...${NC}"
RESPONSE=$(curl -s -X POST \
    http://localhost:$PORT/api/parse-job \
    -H "Content-Type: multipart/form-data" \
    -F "file=@$1" \
    -F "force_refresh=true")

# Vérifier si la réponse est valide (JSON)
if echo "$RESPONSE" | python -m json.tool >/dev/null 2>&1; then
    echo -e "${GREEN}Parsing réussi! Voici le résultat:${NC}"
    echo "$RESPONSE" | python -m json.tool | grep -v "content\|parsed_text" | head -n 30
    
    # Afficher un message si le résultat est plus long
    if [ "$(echo "$RESPONSE" | wc -l)" -gt 30 ]; then
        echo -e "${YELLOW}...(résultat tronqué)${NC}"
    fi
    
    echo -e "${GREEN}===========================================${NC}"
    echo -e "${GREEN}Le système job-parser fonctionne correctement!${NC}"
    echo -e "${GREEN}===========================================${NC}"
else
    echo -e "${RED}Erreur lors du parsing:${NC}"
    echo "$RESPONSE"
fi