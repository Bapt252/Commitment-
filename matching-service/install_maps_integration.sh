#!/bin/bash
# Script d'installation et de configuration pour l'intégration Google Maps

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Pas de couleur

echo -e "${BLUE}=== INSTALLATION DE L'INTÉGRATION GOOGLE MAPS ===${NC}"

# Vérification de l'environnement virtuel Python
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Environnement virtuel Python détecté${NC}"
    # Activer l'environnement virtuel
    source venv/bin/activate
else
    echo -e "${YELLOW}⚠️ Environnement virtuel Python non détecté, création...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${GREEN}✅ Environnement virtuel Python créé et activé${NC}"
fi

# Installation des dépendances
echo -e "${BLUE}=== INSTALLATION DES DÉPENDANCES ===${NC}"
pip install --upgrade pip
pip install googlemaps redis

# Vérification que les modules sont installés correctement
if python -c "import googlemaps" 2>/dev/null; then
    echo -e "${GREEN}✅ Module 'googlemaps' installé avec succès${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation du module 'googlemaps'${NC}"
    exit 1
fi

if python -c "import redis" 2>/dev/null; then
    echo -e "${GREEN}✅ Module 'redis' installé avec succès${NC}"
else
    echo -e "${YELLOW}⚠️ Module 'redis' non installé, le cache fonctionnera en mode fichier uniquement${NC}"
fi

# Mise à jour du fichier requirements.txt
echo -e "${BLUE}=== MISE À JOUR DU FICHIER REQUIREMENTS.TXT ===${NC}"

if [ -f "requirements.txt" ]; then
    # Vérifier si les modules sont déjà dans requirements.txt
    if ! grep -q "googlemaps" requirements.txt; then
        echo "googlemaps>=4.10.0" >> requirements.txt
        echo -e "${GREEN}✅ Module 'googlemaps' ajouté à requirements.txt${NC}"
    else
        echo -e "${GREEN}✅ Module 'googlemaps' déjà présent dans requirements.txt${NC}"
    fi
    
    if ! grep -q "redis" requirements.txt; then
        echo "redis>=4.5.0" >> requirements.txt
        echo -e "${GREEN}✅ Module 'redis' ajouté à requirements.txt${NC}"
    else
        echo -e "${GREEN}✅ Module 'redis' déjà présent dans requirements.txt${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ Fichier requirements.txt non trouvé, création...${NC}"
    cat > requirements.txt << EOF
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
googlemaps>=4.10.0
redis>=4.5.0
python-dotenv>=0.21.0
EOF
    echo -e "${GREEN}✅ Fichier requirements.txt créé${NC}"
fi

# Configuration de la clé API Google Maps
echo -e "${BLUE}=== CONFIGURATION DE LA CLÉ API GOOGLE MAPS ===${NC}"

API_KEY=""

# Vérifier si une clé existe déjà dans .env
if [ -f ".env" ]; then
    if grep -q "GOOGLE_MAPS_API_KEY" .env; then
        API_KEY=$(grep "GOOGLE_MAPS_API_KEY" .env | cut -d '=' -f2)
        echo -e "${GREEN}✅ Clé API Google Maps existante trouvée${NC}"
    fi
fi

# Si aucune clé n'est trouvée, demander à l'utilisateur
if [ -z "$API_KEY" ]; then
    echo -e "${YELLOW}Aucune clé API Google Maps n'a été trouvée.${NC}"
    read -p "Veuillez entrer votre clé API Google Maps (appuyez sur Entrée pour ignorer): " API_KEY
    
    if [ -n "$API_KEY" ]; then
        # Mise à jour ou création du fichier .env
        if [ -f ".env" ]; then
            if grep -q "GOOGLE_MAPS_API_KEY" .env; then
                # Mettre à jour la clé existante
                sed -i '' "s/GOOGLE_MAPS_API_KEY=.*/GOOGLE_MAPS_API_KEY=$API_KEY/" .env
            else
                # Ajouter la clé
                echo "GOOGLE_MAPS_API_KEY=$API_KEY" >> .env
            fi
        else
            # Créer le fichier .env
            echo "GOOGLE_MAPS_API_KEY=$API_KEY" > .env
        fi
        echo -e "${GREEN}✅ Clé API Google Maps configurée dans le fichier .env${NC}"
    else
        echo -e "${YELLOW}⚠️ Aucune clé API fournie. Le système fonctionnera en mode simulation${NC}"
    fi
fi

# Informations importantes
echo -e "${BLUE}=== INFORMATIONS IMPORTANTES ===${NC}"
echo -e "${YELLOW}Pour utiliser l'API Google Maps, vous devez:${NC}"
echo -e "1. Activer les APIs suivantes dans la console Google Cloud:"
echo -e "   - Directions API"
echo -e "   - Distance Matrix API"
echo -e "   - Geocoding API"
echo -e "2. S'assurer que la facturation est activée pour votre projet"
echo -e "3. Configurer les restrictions appropriées pour votre clé API"

# Test de la configuration
echo -e "${BLUE}=== TEST DE LA CONFIGURATION ===${NC}"
echo -e "${YELLOW}Pour tester la configuration, exécutez:${NC}"
echo -e "  python test_maps_api.py"

echo -e "${BLUE}=== INSTALLATION TERMINÉE ===${NC}"
