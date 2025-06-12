#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier si un argument a été fourni
if [ $# -eq 0 ]; then
    echo -e "${RED}Erreur: Aucun fichier CV spécifié${NC}"
    echo -e "Usage: $0 <chemin_vers_cv.pdf>"
    exit 1
fi

CV_FILE="$1"

# Vérifier que le fichier existe
if [ ! -f "$CV_FILE" ]; then
    echo -e "${RED}Erreur: Le fichier $CV_FILE n'existe pas${NC}"
    exit 1
fi

# Vérifier que le service est accessible
echo -e "${YELLOW}🔍 Vérification de l'accessibilité du service...${NC}"
if ! curl -s "http://localhost:8000/health" > /dev/null; then
    echo -e "${RED}Erreur: Le service n'est pas accessible sur http://localhost:8000/health${NC}"
    echo -e "${YELLOW}Essayez d'abord de redémarrer le service avec:${NC}"
    echo -e "./restart-cv-parser-real.sh"
    exit 1
fi

echo -e "${GREEN}✅ Le service est accessible!${NC}"

# Effectuer une requête avec force_refresh à true pour éviter le cache
echo -e "${YELLOW}🚀 Envoi du fichier pour parsing (mode non-mock)...${NC}"
RESPONSE=$(curl -s -X POST \
    -F "file=@$CV_FILE" \
    -F "force_refresh=true" \
    http://localhost:8000/api/parse-cv/)

# Vérifier que la réponse n'est pas vide
if [ -z "$RESPONSE" ]; then
    echo -e "${RED}Erreur: Aucune réponse reçue du service${NC}"
    exit 1
fi

# Sauvegarder la réponse dans un fichier JSON
echo "$RESPONSE" > real_parser_result.json

# Vérifier si nous sommes en mode mock ou réel
IS_MOCK=$(echo "$RESPONSE" | grep -o '"model":"mock"' || echo "not_found")

if [ "$IS_MOCK" != "not_found" ]; then
    echo -e "${RED}⚠️ Le service utilise toujours le mock parser!${NC}"
    echo -e "${YELLOW}Vérifiez que le fichier .env a été correctement modifié avec USE_MOCK_PARSER=false${NC}"
    echo -e "${YELLOW}Et que le service a été redémarré avec ./restart-cv-parser-real.sh${NC}"
else
    echo -e "${GREEN}✅ Le service utilise le vrai parser (non-mock)!${NC}"
fi

# Afficher un résumé des résultats
echo -e "${BLUE}📊 Résumé du parsing:${NC}"
echo -e "${YELLOW}Le fichier complet a été sauvegardé dans real_parser_result.json${NC}"

# Utiliser jq pour extraire les informations importantes si disponible
if command -v jq &> /dev/null; then
    echo -e "${BLUE}Informations personnelles:${NC}"
    echo "$RESPONSE" | jq -r '.data.informations_personnelles // .data.personal_info // empty'
    
    echo -e "${BLUE}Compétences:${NC}"
    echo "$RESPONSE" | jq -r '.data.competences_techniques // .data.skills // empty'
    
    echo -e "${BLUE}Expériences:${NC}"
    echo "$RESPONSE" | jq -r '.data.experiences_professionnelles // .data.work_experience // empty'
else
    echo -e "${YELLOW}Pour un affichage plus détaillé, installez jq avec:${NC}"
    echo -e "brew install jq"
    echo -e "${YELLOW}Ou consultez le fichier real_parser_result.json directement.${NC}"
fi

echo -e "${GREEN}✅ Test terminé!${NC}"
