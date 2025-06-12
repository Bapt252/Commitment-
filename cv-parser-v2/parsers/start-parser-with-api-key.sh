#!/bin/bash
# Script pour démarrer le service de parsing CV avec la clé API depuis GitHub Secrets

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Démarrage du service de parsing CV avec la clé API OpenAI ===${NC}"

# Vérifier si la variable d'environnement OPENAI_API_KEY est définie
if [ -z "${OPENAI_API_KEY}" ]; then
    echo -e "${RED}Erreur: La variable OPENAI_API_KEY n'est pas définie.${NC}"
    echo -e "${YELLOW}Assurez-vous d'avoir configuré la clé API OpenAI dans les secrets GitHub.${NC}"
    echo -e "Vous pouvez la définir manuellement avec:"
    echo -e "${GREEN}export OPENAI_API_KEY=votre_clé_api_ici${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Clé API OpenAI trouvée${NC}"

# Mettre à jour le fichier .env avec la clé API
ENV_FILE="cv-parser-service/.env"

# Vérifier si le fichier .env existe
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Erreur: Le fichier $ENV_FILE n'existe pas.${NC}"
    exit 1
fi

# Désactiver le mock parser et définir la clé API
sed -i "s/USE_MOCK_PARSER=true/USE_MOCK_PARSER=false/" "$ENV_FILE"
sed -i "s/^# OPENAI_API_KEY=.*$/OPENAI_API_KEY=$OPENAI_API_KEY/" "$ENV_FILE"

echo -e "${GREEN}✓ Fichier .env mis à jour avec la clé API${NC}"

# Redémarrer le conteneur Docker du parser CV
echo -e "${BLUE}Redémarrage du service de parsing CV...${NC}"
docker-compose -f docker-compose.yml restart nexten-cv-parser

echo -e "${GREEN}✓ Service redémarré avec succès${NC}"
echo -e "${YELLOW}Attente de 5 secondes pour que le service se stabilise...${NC}"
sleep 5

# Vérifier que le service est bien démarré
if docker ps | grep -q nexten-cv-parser; then
    echo -e "${GREEN}✓ Le service de parsing CV est opérationnel${NC}"
    echo -e "${BLUE}Vous pouvez maintenant tester le parser avec:${NC}"
    echo -e "${GREEN}./test-real-parser.sh${NC}"
else
    echo -e "${RED}Erreur: Le service de parsing CV n'est pas démarré correctement.${NC}"
    echo -e "${YELLOW}Vérifiez les logs avec:${NC}"
    echo -e "${GREEN}docker logs nexten-cv-parser${NC}"
fi
