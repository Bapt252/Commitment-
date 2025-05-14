#!/bin/bash
# Script pour mettre à jour la clé API Google Maps

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Pas de couleur

echo -e "${BLUE}=== MISE À JOUR DE LA CLÉ API GOOGLE MAPS ===${NC}"

# Vérifier si une clé a été fournie comme argument
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 <votre_clé_api_google_maps>${NC}"
    read -p "Entrez votre clé API Google Maps: " API_KEY
else
    API_KEY=$1
fi

# Vérifier que la clé a été fournie
if [ -z "$API_KEY" ]; then
    echo -e "${RED}Erreur: Aucune clé API fournie${NC}"
    exit 1
fi

# Chemin du fichier .env
ENV_FILE=".env"

# Vérifier si le fichier .env existe
if [ -f "$ENV_FILE" ]; then
    # Vérifier si la variable GOOGLE_MAPS_API_KEY existe déjà dans le fichier
    if grep -q "GOOGLE_MAPS_API_KEY" "$ENV_FILE"; then
        # Remplacer la valeur existante
        sed -i '' "s/GOOGLE_MAPS_API_KEY=.*/GOOGLE_MAPS_API_KEY=$API_KEY/" "$ENV_FILE"
        echo -e "${GREEN}✅ Clé API mise à jour dans $ENV_FILE${NC}"
    else
        # Ajouter la variable si elle n'existe pas
        echo "GOOGLE_MAPS_API_KEY=$API_KEY" >> "$ENV_FILE"
        echo -e "${GREEN}✅ Clé API ajoutée à $ENV_FILE${NC}"
    fi
else
    # Créer le fichier .env s'il n'existe pas
    echo "GOOGLE_MAPS_API_KEY=$API_KEY" > "$ENV_FILE"
    echo -e "${GREEN}✅ Fichier $ENV_FILE créé avec la clé API${NC}"
fi

echo -e "${BLUE}=== VÉRIFICATION DE LA CLÉ ===${NC}"
echo -e "${YELLOW}Pour tester la clé, exécutez:${NC}"
echo -e "  ./test-transport-minimal.sh"
echo -e "  python test_maps_api.py"

echo -e "${BLUE}=== IMPORTANT ===${NC}"
echo -e "${YELLOW}Assurez-vous d'avoir activé les APIs suivantes dans la console Google Cloud:${NC}"
echo -e "  - Directions API"
echo -e "  - Distance Matrix API"
echo -e "  - Geocoding API"
