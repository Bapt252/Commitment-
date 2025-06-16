#!/bin/bash

# 🚀 Script de configuration rapide SuperSmartMatch V2
# Clone et configure tous les dépôts nécessaires

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 SuperSmartMatch V2 - Configuration Rapide${NC}"
echo -e "${BLUE}==============================================${NC}"

# 1. Cloner le dépôt Nexten-Project si nécessaire
if [ ! -d "Nexten-Project" ]; then
    echo -e "${BLUE}📦 Clonage du dépôt Nexten-Project...${NC}"
    git clone https://github.com/Bapt252/Nexten-Project.git
    echo -e "${GREEN}✅ Nexten-Project cloné avec succès${NC}"
else
    echo -e "${GREEN}✅ Nexten-Project déjà présent${NC}"
fi

# 2. Cloner le dépôt SuperSmartMatch-Service si nécessaire
if [ ! -d "../SuperSmartMatch-Service" ]; then
    echo -e "${BLUE}📦 Clonage du dépôt SuperSmartMatch-Service...${NC}"
    cd ..
    git clone https://github.com/Bapt252/SuperSmartMatch-Service.git
    cd Commitment-
    echo -e "${GREEN}✅ SuperSmartMatch-Service cloné avec succès${NC}"
else
    echo -e "${GREEN}✅ SuperSmartMatch-Service déjà présent${NC}"
fi

# 3. Rendre le script de diagnostic exécutable
echo -e "${BLUE}🔧 Configuration des permissions...${NC}"
chmod +x diagnostic-and-fix.sh

# 4. Créer les répertoires manquants s'ils n'existent pas
mkdir -p nexten-backend nexten-data-adapter monitoring

# 5. Afficher la structure
echo -e "\n${BLUE}📁 Structure du projet:${NC}"
ls -la

echo -e "\n${GREEN}✅ Configuration terminée !${NC}"
echo -e "\n${YELLOW}🚀 Prochaines étapes:${NC}"
echo "1. Exécuter le diagnostic: ./diagnostic-and-fix.sh"
echo "2. Ou démarrer manuellement: docker-compose -f docker-compose-integrated.yml up -d"
echo ""
echo -e "${BLUE}📋 Endpoints disponibles après démarrage:${NC}"
echo "• API Gateway: http://localhost:5055/api/gateway/"
echo "• Frontend: http://localhost:3000"
echo "• Documentation: http://localhost:5055/api/gateway/docs"
