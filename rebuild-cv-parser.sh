#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Reconstruction complète du service CV Parser...${NC}"

# 1. Arrêter le service existant
echo -e "${YELLOW}🛑 Arrêt du service existant...${NC}"
docker-compose stop cv-parser
docker-compose rm -f cv-parser

# 2. Reconstruire l'image
echo -e "${YELLOW}🏗️ Reconstruction de l'image Docker...${NC}"
docker-compose build --no-cache cv-parser

# 3. Démarrer le nouveau service
echo -e "${YELLOW}🚀 Démarrage du nouveau service...${NC}"
docker-compose up -d cv-parser

# 4. Vérifier l'état du service
echo -e "${YELLOW}🔍 Vérification de l'état du service...${NC}"
docker-compose ps cv-parser

# 5. Afficher les ports
echo -e "${YELLOW}📋 Ports utilisés par le service cv-parser:${NC}"
docker-compose port cv-parser 5000

echo -e "${GREEN}✅ Reconstruction terminée!${NC}"
echo -e "${BLUE}🔧 Pour tester le service, utilisez:${NC}"
echo "curl http://localhost:8000/health  # Pour vérifier que le service répond"
echo "curl -X POST \\
  http://localhost:8000/api/parse-cv \\
  -H \"Content-Type: multipart/form-data\" \\
  -F \"file=@/Users/baptistecomas/Desktop/MonSuperCV.pdf\" \\
  -F \"force_refresh=true\"  # Pour tester le parsing de CV"
