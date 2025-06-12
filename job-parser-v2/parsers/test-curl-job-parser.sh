#!/bin/bash

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier si un chemin de fichier a été fourni
if [ -z "$1" ]; then
  echo -e "${RED}Aucun fichier spécifié.${NC}"
  echo -e "${YELLOW}Usage: $0 <chemin_vers_fichier_fiche_de_poste>${NC}"
  exit 1
fi

# Vérifier si le fichier existe
if [ ! -f "$1" ]; then
  echo -e "${RED}Le fichier $1 n'existe pas.${NC}"
  exit 1
fi

# Récupérer le port du service
port=$(docker-compose port job-parser 5000 | cut -d ':' -f 2 || echo "5053")

echo -e "${GREEN}=== TEST DU SERVICE DE PARSING DE FICHES DE POSTE ===${NC}"

# Vérifier si le service est en ligne
echo -e "${YELLOW}Vérification de la santé du service...${NC}"
health_response=$(curl -s http://localhost:${port}/health || echo "error")

if [[ "$health_response" == *"healthy"* ]]; then
  echo -e "${GREEN}Service en ligne!${NC}"
else
  echo -e "${RED}Le service ne répond pas. Vérifiez qu'il est démarré.${NC}"
  echo -e "${YELLOW}Réponse: $health_response${NC}"
  echo -e "${YELLOW}Essayez d'abord de lancer: ./fix-parser.sh${NC}"
  exit 1
fi

# Tester le parsing d'une fiche de poste
echo -e "${YELLOW}Test du parsing d'une fiche de poste...${NC}"
echo -e "${YELLOW}Fichier: $1${NC}"
echo -e "${YELLOW}Endpoint: http://localhost:${port}/api/parse-job${NC}"

response=$(curl -s -X POST \
  http://localhost:${port}/api/parse-job \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$1" \
  -F "force_refresh=true")

# Vérifier si la requête a réussi
if [ $? -ne 0 ]; then
  echo -e "${RED}Erreur lors de la requête curl.${NC}"
  exit 1
fi

# Afficher le résultat
echo -e "${GREEN}Résultat du parsing:${NC}"
echo "$response" | python -m json.tool || echo "$response"

echo -e "${GREEN}Test terminé.${NC}"
