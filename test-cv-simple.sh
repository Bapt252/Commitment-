#!/bin/bash
# Script simplifié pour tester le système de parsing CV
# Usage: ./test-cv-simple.sh <chemin_vers_le_cv.pdf>

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

if [ $# -eq 0 ]; then
    echo -e "${RED}Erreur: Aucun fichier spécifié.${NC}"
    echo "Usage: $0 <chemin_vers_le_cv.pdf>"
    exit 1
fi

CV_FILE="$1"

if [ ! -f "$CV_FILE" ]; then
    echo -e "${RED}Erreur: Le fichier '$CV_FILE' n'existe pas.${NC}"
    exit 1
fi

# Vérifier l'extension du fichier
file_extension="${CV_FILE##*.}"
file_extension_lower=$(echo "$file_extension" | tr '[:upper:]' '[:lower:]')

if [ "$file_extension_lower" != "pdf" ] && [ "$file_extension_lower" != "docx" ]; then
    echo -e "${RED}Erreur: Format de fichier non supporté. Utilisez .pdf ou .docx${NC}"
    exit 1
fi

# Vérifier si le service de parsing est en cours d'exécution
echo -e "${YELLOW}Vérification du service de parsing CV...${NC}"

if ! curl -s http://localhost:5051/api/v1/health > /dev/null; then
    echo -e "${RED}Erreur: Le service de parsing CV n'est pas accessible sur le port 5051.${NC}"
    echo "Assurez-vous que les conteneurs Docker sont en cours d'exécution."
    exit 1
fi

echo -e "${GREEN}Service de parsing CV détecté et fonctionnel!${NC}"

# Vérifier si le script Python existe et est exécutable
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/cv-parser-service/test_parser_simple.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${YELLOW}Le script Python n'est pas trouvé au chemin attendu.${NC}"
    echo -e "${YELLOW}Essai de connexion directe à l'API via curl...${NC}"
    
    # Utiliser curl comme alternative
    echo -e "${GREEN}Envoi du CV pour parsing...${NC}"
    
    FILENAME=$(basename "$CV_FILE")
    RESULT=$(curl -s -X POST http://localhost:5051/api/v1/parse \
         -F "file=@$CV_FILE" \
         -H "Content-Type: multipart/form-data")
    
    # Vérifier si la réponse est un JSON valide
    if echo "$RESULT" | jq empty 2>/dev/null; then
        echo -e "${GREEN}Résultat du parsing (données brutes):${NC}"
        echo "$RESULT" | jq '.'
    else
        echo -e "${RED}Erreur lors du parsing:${NC}"
        echo "$RESULT"
        exit 1
    fi
else
    # Rendre le script exécutable si nécessaire
    if [ ! -x "$PYTHON_SCRIPT" ]; then
        chmod +x "$PYTHON_SCRIPT"
    fi
    
    echo -e "${GREEN}Utilisation du script Python pour le parsing...${NC}"
    
    # Vérifier si Python est disponible
    if ! command -v python3 &> /dev/null; then
        echo -e "${YELLOW}Python3 n'est pas installé ou n'est pas dans le PATH.${NC}"
        echo -e "${YELLOW}Installation des dépendances requises...${NC}"
        pip install requests
    fi
    
    # Exécuter le script Python
    python3 "$PYTHON_SCRIPT" "$CV_FILE"
fi

echo -e "${GREEN}Opération terminée.${NC}"
