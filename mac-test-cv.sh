#!/bin/bash

# Script simplifié pour tester le parsing CV sur macOS
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CV_FILE="$1"

# Vérifier si un fichier est fourni
if [ -z "$CV_FILE" ]; then
    echo -e "${RED}Erreur: Veuillez fournir un fichier CV${NC}"
    echo -e "Usage: $0 chemin/vers/votre/cv.pdf"
    exit 1
fi

# Vérifier si le fichier existe
if [ ! -f "$CV_FILE" ]; then
    echo -e "${RED}Erreur: Le fichier $CV_FILE n'existe pas${NC}"
    exit 1
fi

echo -e "${BLUE}=== Test de parsing CV avec API locale ===${NC}"

# Vérifier si l'API est accessible
echo -e "${BLUE}Vérification de l'API...${NC}"
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${YELLOW}L'API ne semble pas être accessible sur http://localhost:8000/health${NC}"
    echo -e "${YELLOW}Vérifiez que :${NC}"
    echo -e "1. Les conteneurs Docker sont en cours d'exécution"
    echo -e "2. L'API est correctement configurée"
    echo -e "${YELLOW}Essai de l'API sur le port standard...${NC}"
    
    # Essayer différents ports potentiels
    for PORT in 5000 3000 8080; do
        if curl -s http://localhost:$PORT/health > /dev/null; then
            echo -e "${GREEN}✓ API trouvée sur le port $PORT${NC}"
            API_PORT=$PORT
            break
        fi
    done
    
    if [ -z "$API_PORT" ]; then
        echo -e "${RED}Impossible de trouver l'API. Essai sur le port par défaut (8000)...${NC}"
        API_PORT=8000
    fi
else
    echo -e "${GREEN}✓ API accessible${NC}"
    API_PORT=8000
fi

# Dossier pour les résultats
RESULTS_DIR="parser_results"
mkdir -p "$RESULTS_DIR"
OUTPUT_FILE="$RESULTS_DIR/result.json"

# Tester avec curl
echo -e "${BLUE}Envoi du CV à l'API...${NC}"
API_URL="http://localhost:$API_PORT/api/parse-cv/"
echo -e "${BLUE}Utilisation de l'URL: $API_URL${NC}"

# Essayer d'abord sans l'API/ dans le chemin si ça échoue
curl -s -X POST \
  "$API_URL" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$CV_FILE" > "$OUTPUT_FILE"

# Vérifier si la requête a réussi
if [ $? -eq 0 ] && [ -s "$OUTPUT_FILE" ]; then
    # Vérifier si on a un JSON valide ou une erreur HTML
    if grep -q "<html" "$OUTPUT_FILE"; then
        echo -e "${RED}Réponse HTML reçue au lieu de JSON. Essai avec un autre endpoint...${NC}"
        
        # Essayer sans /api/ dans le chemin
        curl -s -X POST \
          "http://localhost:$API_PORT/parse-cv/" \
          -H "Content-Type: multipart/form-data" \
          -F "file=@$CV_FILE" > "$OUTPUT_FILE"
            
        if [ $? -eq 0 ] && [ -s "$OUTPUT_FILE" ] && ! grep -q "<html" "$OUTPUT_FILE"; then
            echo -e "${GREEN}✓ Parsing réussi avec l'URL: http://localhost:$API_PORT/parse-cv/${NC}"
        else
            echo -e "${RED}Échec avec les différentes URL testées${NC}"
            echo -e "${YELLOW}Veuillez vérifier la configuration de l'API${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✓ Parsing réussi${NC}"
    echo -e "${YELLOW}Résultat du parsing:${NC}"
    
    # Formatage JSON si disponible
    if command -v jq &> /dev/null; then
        cat "$OUTPUT_FILE" | jq
    elif command -v python &> /dev/null; then
        cat "$OUTPUT_FILE" | python -m json.tool
    else
        cat "$OUTPUT_FILE"
    fi
    
    echo -e "${GREEN}Le résultat a été sauvegardé dans $OUTPUT_FILE${NC}"
else
    echo -e "${RED}Échec du parsing ou résultat vide${NC}"
    echo -e "${YELLOW}Vérifiez que:${NC}"
    echo -e "1. Le service d'API est en cours d'exécution"
    echo -e "2. L'API est accessible à $API_URL"
    echo -e "3. Le fichier CV est dans un format supporté (.pdf, .docx, .doc, .txt)"
    echo -e "4. La clé API OpenAI est correctement configurée si vous utilisez le mode réel"
fi
