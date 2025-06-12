#!/bin/bash
# Script pour configurer la clé API OpenAI sur macOS

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fichier .env
ENV_FILE="cv-parser-service/.env"

# Vérifier si le fichier .env existe
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}Erreur: Le fichier $ENV_FILE n'existe pas.${NC}"
    echo -e "${YELLOW}Assurez-vous d'être dans le répertoire racine du projet.${NC}"
    exit 1
fi

echo -e "${BLUE}=== Configuration de la clé API OpenAI ===${NC}"

# Demander la clé API
read -p "Entrez votre clé API OpenAI: " API_KEY

if [ -z "$API_KEY" ]; then
    echo -e "${RED}Erreur: Aucune clé API fournie.${NC}"
    exit 1
fi

# Sauvegarder la clé dans l'environnement
export OPENAI_API_KEY="$API_KEY"
echo -e "${GREEN}✓ Clé API définie dans la variable d'environnement OPENAI_API_KEY${NC}"

# Mettre à jour le fichier .env
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|^OPENAI_API_KEY=.*$|OPENAI_API_KEY=$API_KEY|" "$ENV_FILE"
    sed -i '' "s|^USE_MOCK_PARSER=true|USE_MOCK_PARSER=false|" "$ENV_FILE"
else
    # Linux
    sed -i "s|^OPENAI_API_KEY=.*$|OPENAI_API_KEY=$API_KEY|" "$ENV_FILE"
    sed -i "s|^USE_MOCK_PARSER=true|USE_MOCK_PARSER=false|" "$ENV_FILE"
fi

echo -e "${GREEN}✓ Clé API enregistrée dans $ENV_FILE${NC}"

# Déterminer si Docker est utilisé
if command -v docker &> /dev/null && docker ps | grep -q "cv-parser"; then
    echo -e "${BLUE}Docker détecté. Redémarrage du service...${NC}"
    
    # Essayer de redémarrer avec docker-compose
    if command -v docker-compose &> /dev/null; then
        docker-compose restart 2>/dev/null || {
            # Si échec, essayer de trouver le conteneur et le redémarrer
            CONTAINER=$(docker ps | grep "cv-parser" | awk '{print $1}')
            if [ -n "$CONTAINER" ]; then
                docker restart $CONTAINER
            fi
        }
    else
        # Si docker-compose n'est pas disponible
        CONTAINER=$(docker ps | grep "cv-parser" | awk '{print $1}')
        if [ -n "$CONTAINER" ]; then
            docker restart $CONTAINER
        fi
    fi
    
    echo -e "${GREEN}✓ Service redémarré${NC}"
    echo -e "${YELLOW}Attente de 5 secondes pour que le service se stabilise...${NC}"
    sleep 5
fi

echo -e "${BLUE}Configuration terminée. Vous pouvez maintenant utiliser:${NC}"
echo -e "${GREEN}./mac-test-cv.sh MonSuperCV.pdf${NC}"
echo -e "${YELLOW}pour tester le parser avec votre CV.${NC}"
