#!/bin/bash

# Script de test pour SuperSmartMatch
# Auteur: Nexten Team

echo "🧪 Tests SuperSmartMatch - Service Unifié de Matching"
echo "======================================================================"

# Configuration
API_URL=${API_URL:-"http://localhost:5070"}
TEST_TIMEOUT=10

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Fonction pour tester un endpoint
test_endpoint() {
    local endpoint=$1
    local method=${2:-GET}
    local data=${3:-""}
    local expected_status=${4:-200}
    
    echo -e "${BLUE}Testing $method $endpoint${NC}"
    
    if [ "$method" = "POST" ] && [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$data" \
            --max-time $TEST_TIMEOUT \
            "$API_URL$endpoint" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" \
            --max-time $TEST_TIMEOUT \
            "$API_URL$endpoint" 2>/dev/null)
    fi
    
    if [ $? -eq 0 ]; then
        status_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n -1)
        
        if [ "$status_code" = "$expected_status" ]; then
            print_result 0 "$endpoint - Status: $status_code"
            return 0
        else
            print_result 1 "$endpoint - Expected: $expected_status, Got: $status_code"
            return 1
        fi
    else
        print_result 1 "$endpoint - Timeout ou erreur de connexion"
        return 1
    fi
}

# Vérification que le service est démarré
echo "🔍 Vérification de la disponibilité du service..."
if ! curl -s --max-time 5 "$API_URL/health" >/dev/null 2>&1; then
    echo -e "${RED}❌ Service non disponible sur $API_URL${NC}"
    echo "🛠️  Veuillez démarrer le service avec: ./start-supersmartmatch.sh"
    exit 1
fi

echo -e "${GREEN}✅ Service disponible${NC}"
echo ""

# Test 1: Health Check
echo "🩺 Test 1: Health Check"
test_endpoint "/health"
echo ""

# Test 2: Root endpoint
echo "🏠 Test 2: Root endpoint"
test_endpoint "/"
echo ""

# Test 3: Liste des algorithmes
echo "🧠 Test 3: Liste des algorithmes"
test_endpoint "/algorithms"
echo ""

# Test 4: Info d'un algorithme spécifique
echo "📊 Test 4: Info algorithme Enhanced"
test_endpoint "/algorithms/enhanced"
echo ""

# Test 5: Matching basique
echo "🎯 Test 5: Matching basique"
matching_data='{
  "candidate": {
    "competences": ["Python", "Django", "SQL"],
    "annees_experience": 3,
    "adresse": "Paris",
    "contrats_recherches": ["CDI"]
  },
  "jobs": [
    {
      "id": 1,
      "titre": "Développeur Python",
      "competences": ["Python", "Django", "PostgreSQL"],
      "type_contrat": "CDI",
      "localisation": "Paris"
    },
    {
      "id": 2,
      "titre": "Data Scientist",
      "competences": ["Python", "Machine Learning"],
      "type_contrat": "CDI",
      "localisation": "Lyon"
    }
  ],
  "algorithm": "auto",
  "limit": 5
}'
test_endpoint "/api/v1/match" "POST" "$matching_data"
echo ""

# Test 6: Sélection automatique d'algorithme
echo "🤖 Test 6: Recommandation d'algorithme"
recommendation_data='{
  "candidate": {
    "competences": ["JavaScript", "React", "Node.js"],
    "annees_experience": 5,
    "adresse": "Lyon"
  },
  "jobs": [
    {
      "id": 1,
      "titre": "Frontend Developer",
      "competences": ["JavaScript", "React"]
    }
  ]
}'
test_endpoint "/api/v1/recommend-algorithm" "POST" "$recommendation_data"
echo ""

# Test 7: Matching avec algorithme spécifique
echo "🔧 Test 7: Matching avec algorithme Enhanced"
enhanced_data='{
  "candidate": {
    "competences": ["Java", "Spring", "MySQL"],
    "annees_experience": 7,
    "adresse": "Marseille",
    "salaire_souhaite": 60000
  },
  "jobs": [
    {
      "id": 1,
      "titre": "Senior Java Developer",
      "competences": ["Java", "Spring Boot", "MySQL"],
      "type_contrat": "CDI",
      "localisation": "Marseille",
      "salaire": "55K-70K€"
    }
  ],
  "algorithm": "enhanced",
  "limit": 3
}'
test_endpoint "/api/v1/match" "POST" "$enhanced_data"
echo ""

# Test 8: Statistiques du service
echo "📊 Test 8: Statistiques du service"
test_endpoint "/api/v1/stats"
echo ""

# Test 9: Endpoint de test
echo "🧪 Test 9: Endpoint de test"
test_data='{
  "candidate": {
    "competences": ["Test"]
  },
  "jobs": [{
    "id": 1,
    "titre": "Test Job"
  }],
  "algorithm": "auto"
}'
test_endpoint "/api/v1/test" "POST" "$test_data"
echo ""

# Test 10: Gestion d'erreur (données invalides)
echo "⚠️  Test 10: Gestion d'erreur (données invalides)"
invalid_data='{
  "candidate": {},
  "jobs": [],
  "algorithm": "invalid"
}'
test_endpoint "/api/v1/match" "POST" "$invalid_data" "400"
echo ""

# Résumé des tests
echo "======================================================================"
echo -e "${BLUE}📊 Résumé des Tests SuperSmartMatch${NC}"
echo "======================================================================"
echo "✅ Tests de base: Health, Root, Algorithms"
echo "🧠 Tests algorithmes: Auto-sélection, Enhanced, Recommandation"
echo "📊 Tests avannés: Stats, Gestion d'erreur"
echo "🧪 Test endpoint: Validation des données"
echo ""
echo -e "${GREEN}🎉 Tests terminés !${NC}"
echo "🌐 Interface Swagger: $API_URL/docs"
echo "📄 Documentation ReDoc: $API_URL/redoc"
echo ""
