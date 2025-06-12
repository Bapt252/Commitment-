#!/bin/bash

echo "🚀 Test SuperSmartMatch - Correction macOS et détection automatique du port"
echo "========================================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_test() {
    echo -e "${BLUE}🧪 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Variables
SUPERSMARTMATCH_PORT=""
SUPERSMARTMATCH_ENDPOINT=""

# Fonction pour détecter SuperSmartMatch
detect_supersmartmatch() {
    print_test "Détection automatique de SuperSmartMatch..."
    
    # Test des ports courants
    for port in 5062 5061 5060 5052 5051 5050; do
        # Test endpoint /match
        match_response=$(curl -s --connect-timeout 2 "http://localhost:$port/match" -X POST \
            -H "Content-Type: application/json" \
            -d '{"candidate":{"name":"test"},"offers":[{"id":"test"}]}' 2>/dev/null)
        
        if [[ $? -eq 0 ]] && [[ "$match_response" != *"Not Found"* ]] && [[ "$match_response" != *"404"* ]]; then
            SUPERSMARTMATCH_PORT=$port
            SUPERSMARTMATCH_ENDPOINT="/match"
            print_success "SuperSmartMatch trouvé sur port $port avec endpoint /match"
            return 0
        fi
        
        # Test endpoint /api/v1/match
        match_v1_response=$(curl -s --connect-timeout 2 "http://localhost:$port/api/v1/match" -X POST \
            -H "Content-Type: application/json" \
            -d '{"candidate":{"name":"test"},"offers":[{"id":"test"}]}' 2>/dev/null)
            
        if [[ $? -eq 0 ]] && [[ "$match_v1_response" != *"Not Found"* ]] && [[ "$match_v1_response" != *"404"* ]]; then
            SUPERSMARTMATCH_PORT=$port
            SUPERSMARTMATCH_ENDPOINT="/api/v1/match"
            print_success "SuperSmartMatch trouvé sur port $port avec endpoint /api/v1/match"
            return 0
        fi
        
        # Test endpoint /api/v2/match
        match_v2_response=$(curl -s --connect-timeout 2 "http://localhost:$port/api/v2/match" -X POST \
            -H "Content-Type: application/json" \
            -d '{"candidate":{"name":"test"},"offers":[{"id":"test"}]}' 2>/dev/null)
            
        if [[ $? -eq 0 ]] && [[ "$match_v2_response" != *"Not Found"* ]] && [[ "$match_v2_response" != *"404"* ]]; then
            SUPERSMARTMATCH_PORT=$port
            SUPERSMARTMATCH_ENDPOINT="/api/v2/match"
            print_success "SuperSmartMatch trouvé sur port $port avec endpoint /api/v2/match"
            return 0
        fi
    done
    
    print_error "SuperSmartMatch non trouvé sur les ports courants"
    return 1
}

# Test du service de matching alternatif sur 5052
test_alternative_matching_service() {
    print_test "Test du service de matching sur port 5052"
    
    health_response=$(curl -s http://localhost:5052/health 2>/dev/null)
    if [[ $? -eq 0 ]] && [[ "$health_response" == *"healthy"* ]]; then
        print_success "Service de matching actif sur port 5052"
        echo "$health_response" | python3 -m json.tool 2>/dev/null
        
        print_test "Test de l'endpoint queue-matching..."
        queue_response=$(curl -s -X POST http://localhost:5052/api/v1/queue-matching \
            -H "Content-Type: application/json" \
            -d '{
                "candidate_id": "test-candidate-123",
                "job_id": "test-job-456",
                "webhook_url": "http://example.com/webhook"
            }' 2>/dev/null)
            
        if [[ $? -eq 0 ]] && [[ "$queue_response" != *"Not Found"* ]]; then
            print_success "Service de matching asynchrone disponible"
            echo "$queue_response" | python3 -m json.tool 2>/dev/null | head -10
        else
            print_warning "Service de matching asynchrone non disponible"
        fi
    else
        print_error "Service de matching sur 5052 non accessible"
    fi
}

# Détecter SuperSmartMatch
if detect_supersmartmatch; then
    # Test avec SuperSmartMatch détecté
    print_test "Test 1: Health Check SuperSmartMatch"
    HEALTH_RESPONSE=$(curl -s "http://localhost:$SUPERSMARTMATCH_PORT/health")
    if [[ $? -eq 0 ]] && [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
        print_success "Service accessible et en bonne santé"
        echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null
    else
        print_error "Health check échoué"
    fi

    echo ""
    print_test "Test 2: Matching basique avec format candidate/offers"
    BASIC_TEST=$(curl -s -X POST "http://localhost:$SUPERSMARTMATCH_PORT$SUPERSMARTMATCH_ENDPOINT" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate": {
          "name": "John Doe",
          "technical_skills": ["Python", "Django", "PostgreSQL"],
          "experiences": [
            {
              "title": "Développeur Full Stack",
              "company": "TechCorp",
              "duration_months": 24,
              "skills": ["Python", "Django"]
            }
          ]
        },
        "offers": [
          {
            "id": "job-001",
            "title": "Développeur Python Senior",
            "company": "TechCorp",
            "required_skills": ["Python", "Django"],
            "location": {"city": "Paris", "country": "France"}
          }
        ]
      }')

    if [[ $? -eq 0 ]] && [[ $BASIC_TEST == *"matches"* ]]; then
        print_success "Matching basique réussi !"
        echo "$BASIC_TEST" | python3 -m json.tool 2>/dev/null | head -30
    else
        print_error "Échec du matching basique"
        echo "Réponse: $BASIC_TEST"
    fi

    echo ""
    print_test "Test 3: Matching avec géolocalisation"
    GEO_TEST=$(curl -s -X POST "http://localhost:$SUPERSMARTMATCH_PORT$SUPERSMARTMATCH_ENDPOINT" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate": {
          "name": "Marie Martin",
          "technical_skills": ["JavaScript", "React", "Node.js"],
          "experiences": [
            {
              "title": "Frontend Developer",
              "duration_months": 18
            }
          ]
        },
        "offers": [
          {
            "id": "job-geo-001",
            "title": "React Developer",
            "required_skills": ["React", "JavaScript"],
            "location": {"city": "Paris", "country": "France"}
          },
          {
            "id": "job-geo-002",
            "title": "Frontend Lead",
            "required_skills": ["React", "Node.js"],
            "location": {"city": "Marseille", "country": "France"}
          }
        ],
        "algorithm": "smart-match"
      }')

    if [[ $? -eq 0 ]] && [[ $GEO_TEST == *"matches"* ]]; then
        print_success "Test géolocalisation réussi"
        echo "$GEO_TEST" | python3 -m json.tool 2>/dev/null | head -25
    else
        print_error "Échec du test géolocalisation"
        echo "Réponse: $GEO_TEST"
    fi

    echo ""
    echo "🎯 SuperSmartMatch fonctionne !"
    echo "Port: $SUPERSMARTMATCH_PORT"
    echo "Endpoint: $SUPERSMARTMATCH_ENDPOINT"
    echo "URL complète: http://localhost:$SUPERSMARTMATCH_PORT$SUPERSMARTMATCH_ENDPOINT"
    
else
    print_warning "SuperSmartMatch non trouvé, test du service alternatif"
    test_alternative_matching_service
    
    echo ""
    print_warning "SuperSmartMatch pourrait ne pas être démarré"
    echo "Solutions possibles:"
    echo "1. Démarrer SuperSmartMatch: docker-compose up -d supersmartmatch-service"
    echo "2. Vérifier les conteneurs: docker ps | grep smart"
    echo "3. Voir les logs: docker-compose logs supersmartmatch-service"
fi

echo ""
echo "🔗 Ports testés: 5062, 5061, 5060, 5052, 5051, 5050"
echo "🔗 Endpoints testés: /match, /api/v1/match, /api/v2/match"
echo "📋 Format testé: {candidate: {...}, offers: [...]}"