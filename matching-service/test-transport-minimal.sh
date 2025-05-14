#!/bin/bash
# Script pour tester le système SmartMatch avec l'extension de transport
# Version minimale sans dépendances Flask
# Auteur: Claude/Anthropic
# Date: 14/05/2025

# Définir les couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== TEST MINIMAL DU SYSTÈME NEXTEN SMARTMATCH AVEC EXTENSION DE TRANSPORT ===${NC}"

# Vérifier l'environnement Python
echo -e "${YELLOW}Vérification de l'environnement Python...${NC}"
if ! command -v python &> /dev/null; then
    echo -e "${RED}Python n'est pas installé. Veuillez l'installer pour continuer.${NC}"
    exit 1
fi

# Vérifier le virtualenv
if [ -d "venv" ]; then
    echo -e "${GREEN}Environnement virtuel trouvé.${NC}"
    
    # Activer le virtualenv
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}Impossible d'activer l'environnement virtuel, tentative d'utilisation de Python système.${NC}"
    else
        echo -e "${GREEN}Environnement virtuel activé.${NC}"
    fi
else
    echo -e "${YELLOW}Aucun environnement virtuel trouvé, utilisation de Python système.${NC}"
fi

# Vérifier la clé API Google Maps
echo -e "${YELLOW}Vérification de la clé API Google Maps...${NC}"
if [ -f ".env" ]; then
    if grep -q "GOOGLE_MAPS_API_KEY" .env; then
        echo -e "${GREEN}Clé API Google Maps trouvée dans le fichier .env${NC}"
    else
        echo -e "${YELLOW}Aucune clé API Google Maps trouvée dans le fichier .env${NC}"
        echo -e "${YELLOW}Voulez-vous configurer une clé API maintenant? [y/N]${NC}"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            echo -e "${YELLOW}Entrez votre clé API Google Maps:${NC}"
            read -r api_key
            echo "GOOGLE_MAPS_API_KEY=\"$api_key\"" >> .env
            echo -e "${GREEN}Clé API Google Maps ajoutée au fichier .env${NC}"
        else
            echo -e "${YELLOW}Aucune clé API configurée. Le système utilisera des estimations pour les temps de trajet.${NC}"
        fi
    fi
else
    echo -e "${YELLOW}Fichier .env non trouvé. Création...${NC}"
    echo -e "${YELLOW}Voulez-vous configurer une clé API Google Maps maintenant? [y/N]${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${YELLOW}Entrez votre clé API Google Maps:${NC}"
        read -r api_key
        echo "GOOGLE_MAPS_API_KEY=\"$api_key\"" > .env
        echo -e "${GREEN}Clé API Google Maps ajoutée au fichier .env${NC}"
    else
        touch .env
        echo -e "${YELLOW}Aucune clé API configurée. Le système utilisera des estimations pour les temps de trajet.${NC}"
    fi
fi

# Vérifier les répertoires de test
echo -e "${YELLOW}Vérification des répertoires de test...${NC}"
mkdir -p test_data
mkdir -p test_results

# Vérifier les fichiers de données de test
echo -e "${YELLOW}Vérification des fichiers de données de test...${NC}"
if [ ! -f "test_data/candidates.json" ] || [ ! -f "test_data/companies.json" ]; then
    echo -e "${YELLOW}Fichiers de données de test manquants. Création de fichiers par défaut...${NC}"
    
    # Créer les fichiers s'ils n'existent pas
    if [ ! -f "test_data/candidates.json" ]; then
        echo '[
  {
    "id": "cand001",
    "name": "Jean Dupont",
    "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
    "experience": 4,
    "location": "Paris, France",
    "remote_preference": "hybrid",
    "salary_expectation": 65000,
    "preferred_commute_time": 45,
    "preferred_transport_mode": "transit"
  },
  {
    "id": "cand002",
    "name": "Marie Martin",
    "skills": ["Java", "Spring", "Hibernate", "SQL", "Docker"],
    "experience": 7,
    "location": "Lyon, France",
    "remote_preference": "full",
    "salary_expectation": 72000,
    "preferred_commute_time": 30,
    "preferred_transport_mode": "driving"
  }
]' > test_data/candidates.json
        echo -e "${GREEN}Fichier candidates.json créé${NC}"
    fi
    
    if [ ! -f "test_data/companies.json" ]; then
        echo '[
  {
    "id": "comp001",
    "name": "TechSolutions SAS",
    "required_skills": ["Python", "JavaScript", "React", "Node.js"],
    "location": "Paris, France",
    "remote_policy": "hybrid",
    "salary_range": {"min": 55000, "max": 80000},
    "required_experience": 3,
    "transit_friendly": true,
    "public_transport_access": ["Metro Ligne 1", "RER A"],
    "bicycle_facilities": true
  },
  {
    "id": "comp002",
    "name": "DataInnovate",
    "required_skills": ["Java", "Spring", "SQL", "Big Data"],
    "location": "Lyon, France",
    "remote_policy": "office_only",
    "salary_range": {"min": 60000, "max": 90000},
    "required_experience": 5,
    "transit_friendly": false,
    "bicycle_facilities": false
  }
]' > test_data/companies.json
        echo -e "${GREEN}Fichier companies.json créé${NC}"
    fi
else
    echo -e "${GREEN}Fichiers de données de test trouvés${NC}"
fi

# Vérifier que les modules nécessaires sont installés
echo -e "${YELLOW}Vérification des dépendances Python...${NC}"
python -c "import requests, json, os, logging" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installation des dépendances manquantes...${NC}"
    pip install requests
fi

# Vérifier que le script de test minimal existe
if [ ! -f "test_transport_minimal.py" ]; then
    echo -e "${RED}Script de test minimal non trouvé. Téléchargement depuis GitHub...${NC}"
    curl -s -o test_transport_minimal.py https://raw.githubusercontent.com/Bapt252/Commitment-/main/matching-service/test_transport_minimal.py
    if [ $? -ne 0 ]; then
        echo -e "${RED}Impossible de télécharger le script de test. Veuillez faire un git pull pour récupérer les dernières modifications.${NC}"
        exit 1
    fi
fi

# Rendre le script exécutable
chmod +x test_transport_minimal.py

# Exécuter le test minimal
echo -e "${BLUE}=== EXÉCUTION DU TEST MINIMAL ===${NC}"
python test_transport_minimal.py

# Vérifier si le test a réussi
if [ $? -eq 0 ]; then
    echo -e "${GREEN}=== TEST MINIMAL RÉUSSI ===${NC}"
    echo -e "${GREEN}Les composants de base du système de transport fonctionnent correctement.${NC}"
else
    echo -e "${RED}=== ÉCHEC DU TEST MINIMAL ===${NC}"
    echo -e "${RED}Des problèmes ont été détectés dans les composants de base du système de transport.${NC}"
    exit 1
fi

echo -e "${BLUE}=== PROCHAINES ÉTAPES ===${NC}"
echo -e "${YELLOW}1. Si ce test minimal a réussi, vous pouvez passer à l'intégration complète.${NC}"
echo -e "${YELLOW}2. Pour utiliser l'extension de transport dans votre code:${NC}"
echo -e "${BLUE}   from app.google_maps_client import GoogleMapsClient${NC}"
echo -e "${BLUE}   from app.smartmatch_transport import CommuteMatchExtension${NC}"
echo -e "${BLUE}   maps_client = GoogleMapsClient()${NC}"
echo -e "${BLUE}   extension = CommuteMatchExtension()${NC}"

exit 0