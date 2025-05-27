#!/bin/bash

# Script pour rendre exécutables les scripts SuperSmartMatch
echo "🔧 Configuration des permissions pour SuperSmartMatch"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Mise à jour des permissions...${NC}"

# Scripts principaux
chmod +x start-super-smart-match.sh
chmod +x test-super-smart-match.sh

# Vérification
if [ -x "start-super-smart-match.sh" ]; then
    echo -e "${GREEN}✅ start-super-smart-match.sh rendu exécutable${NC}"
else
    echo "❌ Erreur avec start-super-smart-match.sh"
fi

if [ -x "test-super-smart-match.sh" ]; then
    echo -e "${GREEN}✅ test-super-smart-match.sh rendu exécutable${NC}"
else
    echo "❌ Erreur avec test-super-smart-match.sh"
fi

echo -e "${GREEN}🎉 Configuration terminée !${NC}"
echo ""
echo -e "${BLUE}📋 Commandes disponibles :${NC}"
echo "  ./start-super-smart-match.sh  - Démarrer SuperSmartMatch"
echo "  ./test-super-smart-match.sh   - Tester l'API"
