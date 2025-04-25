#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Redémarrage du service cv-parser pour activer le port 8000...${NC}"

# Arrêter le service cv-parser s'il est en cours d'exécution
echo -e "${YELLOW}🛑 Arrêt du service cv-parser...${NC}"
docker-compose stop cv-parser

# Reconstruire le service cv-parser pour appliquer les modifications
echo -e "${YELLOW}🏗️ Reconstruction du service cv-parser...${NC}"
docker-compose build cv-parser

# Démarrer le service cv-parser avec la nouvelle configuration
echo -e "${YELLOW}🚀 Démarrage du service cv-parser...${NC}"
docker-compose up -d cv-parser

# Vérifier que le service est bien démarré
echo -e "${YELLOW}🔍 Vérification de l'état du service...${NC}"
sleep 3 # Attendre quelques secondes pour le démarrage
docker-compose ps cv-parser

# Vérifier les ports utilisés
echo -e "${YELLOW}📋 Ports utilisés par le service cv-parser:${NC}"
docker port nexten-cv-parser

# Guide d'utilisation
echo -e "\n${GREEN}✅ Redémarrage terminé!${NC}"
echo -e "${BLUE}🔧 Pour tester le service, utilisez:${NC}"
echo -e "curl http://localhost:8000/health  # Pour vérifier que le service répond"
echo -e "curl -X POST \\
  http://localhost:8000/api/parse-cv/ \\
  -H \"Content-Type: multipart/form-data\" \\
  -F \"file=@/Users/baptistecomas/Desktop/MonSuperCV.pdf\" \\
  -F \"force_refresh=false\"  # Pour tester le parsing de CV"

# Rendre le script exécutable
chmod +x restart-cv-parser.sh
