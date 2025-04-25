#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Chemin du fichier PDF à tester
CV_PATH="/Users/baptistecomas/Desktop/MonSuperCV.pdf"

echo -e "${BLUE}🔍 Test du service CV Parser sur le port 8000...${NC}"

# 1. Vérifier que le fichier CV existe
if [ ! -f "$CV_PATH" ]; then
  echo -e "${RED}❌ Erreur: Le fichier CV n'existe pas à l'emplacement spécifié: $CV_PATH${NC}"
  echo -e "${YELLOW}👉 Veuillez modifier le chemin dans ce script ou placer un fichier PDF à cet emplacement.${NC}"
  exit 1
fi

# 2. Tester d'abord l'endpoint health
echo -e "\n${YELLOW}🏥 Test de l'endpoint health...${NC}"
HEALTH_RESULT=$(curl -s http://localhost:8000/health)
if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Service en ligne! Réponse:${NC}"
  echo $HEALTH_RESULT
else
  echo -e "${RED}❌ Erreur: Impossible de contacter le service sur le port 8000${NC}"
  echo -e "${YELLOW}👉 Assurez-vous que le service cv-parser est bien démarré et que le port 8000 est exposé.${NC}"
  echo -e "${YELLOW}👉 Exécutez ./restart-cv-parser.sh pour redémarrer le service.${NC}"
  exit 1
fi

# 3. Tester l'endpoint de parsing
echo -e "\n${YELLOW}📄 Test de l'endpoint parse-cv avec le fichier: $CV_PATH${NC}"
echo -e "${BLUE}🔄 Envoi de la requête...${NC}"

curl -X POST \
  http://localhost:8000/api/parse-cv/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$CV_PATH" \
  -F "force_refresh=false"

echo -e "\n\n${GREEN}✅ Test terminé!${NC}"
