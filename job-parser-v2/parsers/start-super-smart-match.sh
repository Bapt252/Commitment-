#!/bin/bash

# Script de démarrage pour SuperSmartMatch
echo "🚀 Démarrage de SuperSmartMatch - Service unifié de matching"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Vérification de l'environnement
echo -e "${BLUE}📋 Vérification de l'environnement...${NC}"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 n'est pas installé${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python et pip détectés${NC}"

# Aller dans le répertoire SuperSmartMatch
cd super-smart-match 2>/dev/null || {
    echo -e "${RED}❌ Répertoire super-smart-match non trouvé${NC}"
    echo -e "${YELLOW}💡 Veuillez exécuter ce script depuis la racine du projet${NC}"
    exit 1
}

# Installation des dépendances
echo -e "${BLUE}📦 Installation des dépendances...${NC}"
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dépendances installées avec succès${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation des dépendances${NC}"
    exit 1
fi

# Vérification des algorithmes disponibles
echo -e "${BLUE}🔍 Vérification des algorithmes...${NC}"

algorithms_found=0

if [ -f "../matching_engine.py" ]; then
    echo -e "${GREEN}✅ Algorithme original trouvé${NC}"
    algorithms_found=$((algorithms_found + 1))
else
    echo -e "${YELLOW}⚠️  Algorithme original non trouvé${NC}"
fi

if [ -f "../matching_engine_enhanced.py" ]; then
    echo -e "${GREEN}✅ Algorithme enhanced trouvé${NC}"
    algorithms_found=$((algorithms_found + 1))
else
    echo -e "${YELLOW}⚠️  Algorithme enhanced non trouvé${NC}"
fi

if [ -f "../my_matching_engine.py" ]; then
    echo -e "${GREEN}✅ Algorithme personnalisé trouvé${NC}"
    algorithms_found=$((algorithms_found + 1))
else
    echo -e "${YELLOW}⚠️  Algorithme personnalisé non trouvé${NC}"
fi

if [ -f "../compare_algorithms.py" ]; then
    echo -e "${GREEN}✅ Module de comparaison trouvé${NC}"
    algorithms_found=$((algorithms_found + 1))
else
    echo -e "${YELLOW}⚠️  Module de comparaison non trouvé${NC}"
fi

echo -e "${BLUE}📊 Total: ${algorithms_found} algorithmes détectés${NC}"

# Configuration des variables d'environnement
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/.."
export FLASK_APP=app.py
export FLASK_ENV=development

# Choix du mode de démarrage
echo -e "${BLUE}🔧 Mode de démarrage:${NC}"
echo "1. Mode développement (Flask dev server)"
echo "2. Mode production (Gunicorn)"
echo "3. Test de l'API uniquement"

read -p "Choisissez une option (1-3) [1]: " choice
choice=${choice:-1}

case $choice in
    1)
        echo -e "${GREEN}🔥 Démarrage en mode développement...${NC}"
        echo -e "${YELLOW}📍 Service disponible sur: http://localhost:5060${NC}"
        echo -e "${YELLOW}📍 API de matching: http://localhost:5060/api/match${NC}"
        echo -e "${YELLOW}📍 Health check: http://localhost:5060/api/health${NC}"
        echo ""
        echo -e "${BLUE}🛑 Appuyez sur Ctrl+C pour arrêter${NC}"
        echo ""
        python3 app.py
        ;;
    2)
        echo -e "${GREEN}🚀 Démarrage en mode production...${NC}"
        echo -e "${YELLOW}📍 Service disponible sur: http://localhost:5060${NC}"
        echo ""
        echo -e "${BLUE}🛑 Appuyez sur Ctrl+C pour arrêter${NC}"
        echo ""
        gunicorn --bind 0.0.0.0:5060 --workers 4 app:app
        ;;
    3)
        echo -e "${GREEN}🧪 Test de l'API...${NC}"
        python3 -c "
import requests
import json

try:
    response = requests.get('http://localhost:5060/api/health')
    print('✅ API accessible')
    print(json.dumps(response.json(), indent=2))
except:
    print('❌ API non accessible - veuillez la démarrer d\\'abord')
"
        ;;
    *)
        echo -e "${RED}❌ Option invalide${NC}"
        exit 1
        ;;
esac
