#!/bin/bash
# Script d'installation du client hybride Google Maps

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Pas de couleur

echo -e "${YELLOW}=== INSTALLATION DU CLIENT GOOGLE MAPS HYBRIDE ===${NC}"

# Vérifier le répertoire
if [ ! -d "app" ]; then
    echo -e "${YELLOW}Création du répertoire app${NC}"
    mkdir -p app
fi

if [ ! -d "docs" ]; then
    echo -e "${YELLOW}Création du répertoire docs${NC}"
    mkdir -p docs
fi

# Télécharger les fichiers depuis GitHub
echo -e "${YELLOW}Téléchargement des fichiers depuis GitHub...${NC}"

# URL de base pour les fichiers
BASE_URL="https://raw.githubusercontent.com/Bapt252/Commitment-/simple-hybrid-solution/matching-service"

# Fichiers à télécharger
FILES=(
    "app/hybrid_maps_client.py"
    "test_hybrid_standalone.py"
    "docs/hybrid-guide.md"
)

# Télécharger chaque fichier
for file in "${FILES[@]}"; do
    echo -e "${YELLOW}Téléchargement de ${file}...${NC}"
    curl -s -o "$file" "${BASE_URL}/${file}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${file} téléchargé avec succès${NC}"
    else
        echo -e "${RED}❌ Erreur lors du téléchargement de ${file}${NC}"
    fi
done

# Donner les permissions d'exécution au script de test
chmod +x test_hybrid_standalone.py

echo -e "${GREEN}=== INSTALLATION TERMINÉE ===${NC}"
echo -e "${YELLOW}Pour tester le client hybride, exécutez :${NC}"
echo -e "python test_hybrid_standalone.py"

echo -e "${YELLOW}Pour plus d'informations, consultez docs/hybrid-guide.md${NC}"