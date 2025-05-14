#!/bin/bash
# Script d'installation du client hybride avec données réelles

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # Pas de couleur

echo -e "${YELLOW}=== INSTALLATION DU CLIENT GOOGLE MAPS HYBRIDE AVEC DONNÉES RÉELLES ===${NC}"

# Vérifier le répertoire
if [ ! -d "app" ]; then
    echo -e "${YELLOW}Création du répertoire app${NC}"
    mkdir -p app
fi

if [ ! -d "data" ]; then
    echo -e "${YELLOW}Création du répertoire data${NC}"
    mkdir -p data
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
    "app/real_data_hybrid_client.py"
    "preload_maps_data.py"
    "test_real_data_hybrid.py"
    "docs/real-data-hybrid-guide.md"
)

# Télécharger chaque fichier
for file in "${FILES[@]}"; do
    echo -e "${YELLOW}Téléchargement de ${file}...${NC}"
    # Créer le répertoire parent si nécessaire
    mkdir -p "$(dirname "$file")"
    curl -s -o "$file" "${BASE_URL}/${file}"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ ${file} téléchargé avec succès${NC}"
    else
        echo -e "${RED}❌ Erreur lors du téléchargement de ${file}${NC}"
    fi
done

# Donner les permissions d'exécution aux scripts
chmod +x preload_maps_data.py
chmod +x test_real_data_hybrid.py

# Vérifier la clé API Google Maps
if [ -f ".env" ]; then
    if grep -q "GOOGLE_MAPS_API_KEY" ".env"; then
        echo -e "${GREEN}✅ Clé API Google Maps trouvée dans .env${NC}"
    else
        echo -e "${YELLOW}⚠️ Clé API Google Maps non trouvée dans .env${NC}"
        echo -e "${YELLOW}Veuillez ajouter votre clé API à .env :${NC}"
        echo -e "GOOGLE_MAPS_API_KEY=votre_clé_api"
    fi
else
    echo -e "${YELLOW}⚠️ Fichier .env non trouvé${NC}"
    echo -e "${YELLOW}Création d'un fichier .env exemple...${NC}"
    echo "GOOGLE_MAPS_API_KEY=votre_clé_api" > .env
    echo -e "${GREEN}✅ Fichier .env créé${NC}"
    echo -e "${YELLOW}Veuillez modifier le fichier .env avec votre clé API Google Maps${NC}"
fi

echo -e "${GREEN}=== INSTALLATION TERMINÉE ===${NC}"

# Exemple d'utilisation
echo -e "${YELLOW}=== EXEMPLES D'UTILISATION ===${NC}"
echo -e "1. Précharger des données pour des adresses spécifiques :"
echo -e "   python preload_maps_data.py -a \"Paris, France\" \"Lyon, France\" \"Marseille, France\""
echo -e ""
echo -e "2. Tester le client hybride :"
echo -e "   python test_real_data_hybrid.py"
echo -e ""
echo -e "3. Pour plus d'informations, consultez la documentation :"
echo -e "   docs/real-data-hybrid-guide.md"