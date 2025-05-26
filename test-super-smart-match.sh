#!/bin/bash

# Script de test pour SuperSmartMatch
echo "🧪 Test de SuperSmartMatch - Service unifié de matching"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# URL de base de l'API
BASE_URL="http://localhost:5060"

# Fonction pour tester un endpoint
test_endpoint() {
    local endpoint=$1
    local method=$2
    local data=$3
    local description=$4
    
    echo -e "${BLUE}🔬 Test: ${description}${NC}"
    echo -e "${YELLOW}   Endpoint: ${method} ${endpoint}${NC}"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "${BASE_URL}${endpoint}")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "${BASE_URL}${endpoint}")
    fi
    
    # Séparer la réponse du code HTTP
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n -1)
    
    if [ "$http_code" -eq 200 ]; then
        echo -e "${GREEN}   ✅ Succès (HTTP $http_code)${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "${RED}   ❌ Échec (HTTP $http_code)${NC}"
        echo "$body"
    fi
    
    echo ""
}

# Vérifier que l'API est accessible
echo -e "${BLUE}📡 Vérification de la disponibilité de l'API...${NC}"
if ! curl -s "$BASE_URL" >/dev/null; then
    echo -e "${RED}❌ L'API n'est pas accessible sur $BASE_URL${NC}"
    echo -e "${YELLOW}💡 Veuillez démarrer SuperSmartMatch avec: ./start-super-smart-match.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API accessible${NC}"
echo ""

# Test 1: Health check
test_endpoint "/api/health" "GET" "" "Health check"

# Test 2: Liste des algorithmes
test_endpoint "/api/algorithms" "GET" "" "Liste des algorithmes disponibles"

# Test 3: Page d'accueil
test_endpoint "/" "GET" "" "Page d'accueil du service"

# Données de test pour le matching
CV_DATA='{
    "competences": ["Python", "JavaScript", "React", "Django"],
    "annees_experience": 3,
    "formation": "Master Informatique"
}'

QUESTIONNAIRE_DATA='{
    "contrats_recherches": ["CDI"],
    "adresse": "Paris",
    "salaire_souhaite": 50000,
    "mobilite": "hybrid"
}'

JOB_DATA='[
    {
        "id": 1,
        "titre": "Développeur Full Stack",
        "competences": ["Python", "React", "Django"],
        "type_contrat": "CDI",
        "salaire": "45K-55K€",
        "localisation": "Paris",
        "politique_remote": "hybrid"
    },
    {
        "id": 2,
        "titre": "Développeur Frontend",
        "competences": ["JavaScript", "React", "Vue.js"],
        "type_contrat": "CDI",
        "salaire": "40K-50K€",
        "localisation": "Lyon",
        "politique_remote": "remote"
    },
    {
        "id": 3,
        "titre": "Data Scientist",
        "competences": ["Python", "Machine Learning", "Pandas"],
        "type_contrat": "CDI",
        "salaire": "55K-65K€",
        "localisation": "Paris",
        "politique_remote": "on_site"
    }
]'

# Test 4: Matching automatique
MATCHING_DATA="{
    \"cv_data\": $CV_DATA,
    \"questionnaire_data\": $QUESTIONNAIRE_DATA,
    \"job_data\": $JOB_DATA,
    \"algorithm\": \"auto\",
    \"limit\": 5
}"

test_endpoint "/api/match" "POST" "$MATCHING_DATA" "Matching automatique"

# Test 5: Algorithme Enhanced
ENHANCED_DATA="{
    \"cv_data\": $CV_DATA,
    \"questionnaire_data\": $QUESTIONNAIRE_DATA,
    \"job_data\": $JOB_DATA,
    \"algorithm\": \"enhanced\",
    \"limit\": 3
}"

test_endpoint "/api/match" "POST" "$ENHANCED_DATA" "Algorithme Enhanced"

# Test 6: Algorithme Hybride
HYBRID_DATA="{
    \"cv_data\": $CV_DATA,
    \"questionnaire_data\": $QUESTIONNAIRE_DATA,
    \"job_data\": $JOB_DATA,
    \"algorithm\": \"hybrid\",
    \"limit\": 3
}"

test_endpoint "/api/match" "POST" "$HYBRID_DATA" "Algorithme Hybride"

# Test 7: Mode Comparaison
COMPARISON_DATA="{
    \"cv_data\": $CV_DATA,
    \"questionnaire_data\": $QUESTIONNAIRE_DATA,
    \"job_data\": $JOB_DATA,
    \"algorithm\": \"comparison\",
    \"limit\": 3
}"

test_endpoint "/api/match" "POST" "$COMPARISON_DATA" "Mode Comparaison"

# Test 8: Test d'erreur (algorithme inexistant)
ERROR_DATA="{
    \"cv_data\": $CV_DATA,
    \"questionnaire_data\": $QUESTIONNAIRE_DATA,
    \"job_data\": $JOB_DATA,
    \"algorithm\": \"inexistant\",
    \"limit\": 3
}"

test_endpoint "/api/match" "POST" "$ERROR_DATA" "Test d'erreur (algorithme inexistant)"

# Test 9: Test avec données manquantes
INVALID_DATA='{"cv_data": {}, "job_data": []}'

test_endpoint "/api/match" "POST" "$INVALID_DATA" "Test avec données invalides"

echo -e "${GREEN}🎉 Tests terminés !${NC}"
echo ""
echo -e "${BLUE}📋 Résumé des endpoints disponibles:${NC}"
echo "• GET  $BASE_URL/               - Page d'accueil"
echo "• GET  $BASE_URL/api/health     - Status de santé"
echo "• GET  $BASE_URL/api/algorithms - Liste des algorithmes"
echo "• POST $BASE_URL/api/match      - Endpoint de matching principal"
echo ""
echo -e "${YELLOW}💡 Pour plus de détails, consultez la documentation de l'API${NC}"
