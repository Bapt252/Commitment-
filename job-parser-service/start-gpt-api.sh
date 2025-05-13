#!/bin/bash

# Script pour démarrer l'API d'analyse GPT des fiches de poste

# Répertoire du script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================================${NC}"
echo -e "${BLUE}   Démarrage de l'API d'analyse GPT des fiches de poste   ${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Vérifier la présence de la clé API OpenAI
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  Aucune clé API OpenAI trouvée dans l'environnement.${NC}"
    echo -e "${YELLOW}Veuillez entrer votre clé API OpenAI (commençant par 'sk-'):${NC}"
    read -p " > " OPENAI_API_KEY
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}❌ Aucune clé API fournie. Impossible de démarrer le service.${NC}"
        exit 1
    fi
    
    # Exporter la clé pour le script Python
    export OPENAI_API_KEY
fi

# Vérifier l'installation de Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé. Veuillez l'installer pour continuer.${NC}"
    exit 1
fi

# Vérifier les dépendances Python
echo -e "${BLUE}Vérification des dépendances...${NC}"
cd "$SCRIPT_DIR"

# Créer un environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Création d'un environnement virtuel Python...${NC}"
    python3 -m venv venv || { echo -e "${RED}❌ Échec de la création de l'environnement virtuel.${NC}"; exit 1; }
fi

# Activer l'environnement virtuel
source venv/bin/activate || { echo -e "${RED}❌ Échec de l'activation de l'environnement virtuel.${NC}"; exit 1; }

# Installer les dépendances
echo -e "${BLUE}Installation des dépendances...${NC}"
pip install -r requirements.txt || { echo -e "${RED}❌ Échec de l'installation des dépendances.${NC}"; exit 1; }

# Démarrer l'API
echo -e "${GREEN}✓ Tout est prêt! Démarrage de l'API...${NC}"
echo -e "${YELLOW}L'API sera accessible à http://localhost:5055${NC}"
echo -e "${YELLOW}Appuyez sur Ctrl+C pour arrêter l'API${NC}"
echo -e "${BLUE}=========================================================${NC}"

# Exécuter le serveur
python3 gpt_parser_api.py
