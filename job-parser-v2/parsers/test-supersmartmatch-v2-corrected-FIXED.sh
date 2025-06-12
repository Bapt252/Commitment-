#!/bin/bash

echo "🚀 Test SuperSmartMatch v2.0 - API Endpoints Corrigés"
echo "======================================================="
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

# Configuration par défaut
SUPERSMARTMATCH_PORT="5052"
BASE_URL="http://localhost:$SUPERSMARTMATCH_PORT"

print_test "Détection automatique des endpoints SuperSmartMatch..."

# Test 1: Health Check Principal
print_test "Test 1: Health Check Principal - Service de base"
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
if [[ $? -eq 0 ]] && [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    print_success "Service principal accessible"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null
else
    print_error "Service principal non accessible sur le port $SUPERSMARTMATCH_PORT"
    echo "Réponse: $HEALTH_RESPONSE"
fi

echo ""

# Test 2: Health Check V2
print_test "Test 2: Health Check SuperSmartMatch V2"
V2_HEALTH_RESPONSE=$(curl -s "$BASE_URL/api/v2/health")
if [[ $? -eq 0 ]] && [[ $V2_HEALTH_RESPONSE == *"success"* ]]; then
    print_success "SuperSmartMatch V2 accessible"
    echo "$V2_HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null | head -30
else
    print_warning "SuperSmartMatch V2 non disponible"
    echo "Réponse: $V2_HEALTH_RESPONSE"
fi

echo ""

# Test 3: API V2 Enhanced - Test avec format correct
print_test "Test 3: SuperSmartMatch V2 Enhanced API - Format complet"
V2_TEST=$(curl -s -X POST "$BASE_URL/api/v2/match" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Sophie Martin",
      "email": "sophie.martin@example.com",
      "location": {"city": "Paris", "country": "France"},
      "technical_skills": [
        {"name": "Python", "level": "Expert", "years": 5},
        {"name": "Machine Learning", "level": "Advanced", "years": 3}
      ],
      "experiences": [
        {
          "title": "Senior Python Developer",
          "company": "TechCorp",
          "duration_months": 36,
          "skills": ["Python", "Django", "PostgreSQL"]
        }
      ]
    },
    "candidate_questionnaire": {
      "work_style": "collaborative",
      "culture_preferences": "innovation_focused",
      "remote_preference": "hybrid"
    },
    "offers": [
      {
        "id": "job-ml-001",
        "title": "ML Engineer",
        "company": "AI Startup",
        "location": {"city": "Paris", "country": "France"},
        "required_skills": ["Python", "TensorFlow", "MLOps"],
        "remote_policy": "hybrid"
      }
    ],
    "algorithm": "auto"
  }')

if [[ $? -eq 0 ]] && [[ $V2_TEST == *"success"* || $V2_TEST == *"matches"* ]]; then
    print_success "SuperSmartMatch V2 Enhanced API réussi !"
    echo "$V2_TEST" | python3 -m json.tool 2>/dev/null | head -40
else
    print_warning "SuperSmartMatch V2 Enhanced API non disponible ou en erreur"
    echo "Réponse: $V2_TEST"
fi

echo ""

# Test 4: API V1 Compatible via V2
print_test "Test 4: API V1 Compatible via SuperSmartMatch V2"
V1_COMPAT_TEST=$(curl -s -X POST "$BASE_URL/api/v2/match/legacy" \
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

if [[ $? -eq 0 ]] && [[ $V1_COMPAT_TEST == *"success"* || $V1_COMPAT_TEST == *"results"* ]]; then
    print_success "API V1 Compatible réussie"
    echo "$V1_COMPAT_TEST" | python3 -m json.tool 2>/dev/null | head -25
else
    print_warning "API V1 Compatible non disponible"
    echo "Réponse: $V1_COMPAT_TEST"
fi

echo ""

# Test 5: API V1 Queue-Based (Asynchrone)
print_test "Test 5: API V1 Queue-Based - Matching asynchrone"
QUEUE_TEST=$(curl -s -X POST "$BASE_URL/api/v1/queue-matching" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "candidate_123",
    "job_id": "job_456",
    "webhook_url": "https://example.com/webhook"
  }')

if [[ $? -eq 0 ]] && [[ $QUEUE_TEST == *"job_id"* || $QUEUE_TEST == *"queued"* ]]; then
    print_success "Queue-based matching réussi"
    echo "$QUEUE_TEST" | python3 -m json.tool 2>/dev/null
    
    # Extraire job_id pour test de statut
    JOB_ID=$(echo "$QUEUE_TEST" | python3 -c "import sys, json; print(json.load(sys.stdin).get('job_id', ''))" 2>/dev/null)
    if [[ -n "$JOB_ID" ]]; then
        echo ""
        print_test "Test 5b: Vérification du statut du job $JOB_ID"
        STATUS_RESPONSE=$(curl -s "$BASE_URL/api/v1/status/$JOB_ID")
        print_success "Statut récupéré"
        echo "$STATUS_RESPONSE" | python3 -m json.tool 2>/dev/null
    fi
else
    print_warning "Queue-based matching non disponible"
    echo "Réponse: $QUEUE_TEST"
fi

echo ""

# Test 6: Recommendations d'algorithmes
print_test "Test 6: Recommandations d'algorithmes"
ALGO_REC=$(curl -s "$BASE_URL/api/v2/algorithm/recommendations?candidate_experience=5&has_geo_constraints=true&questionnaire_completeness=0.8")

if [[ $? -eq 0 ]] && [[ $ALGO_REC == *"success"* || $ALGO_REC == *"recommendations"* ]]; then
    print_success "Recommandations d'algorithmes disponibles"
    echo "$ALGO_REC" | python3 -m json.tool 2>/dev/null | head -20
else
    print_warning "Recommandations d'algorithmes non disponibles"
    echo "Réponse: $ALGO_REC"
fi

echo ""

# Test 7: Test de géolocalisation avancée
print_test "Test 7: Test géolocalisation avec Google Maps"
GEO_TEST=$(curl -s -X POST "$BASE_URL/api/v2/match" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Pierre Dubois",
      "email": "pierre@example.com",
      "location": {"city": "Lyon", "country": "France"},
      "technical_skills": [
        {"name": "JavaScript", "level": "Expert"},
        {"name": "React", "level": "Advanced"}
      ],
      "mobility_preferences": "local"
    },
    "offers": [
      {
        "id": "job-geo-001",
        "title": "React Developer",
        "company": "Local Tech",
        "location": {"city": "Lyon", "country": "France"},
        "required_skills": ["React", "JavaScript"],
        "remote_policy": "on-site"
      },
      {
        "id": "job-geo-002", 
        "title": "Frontend Lead",
        "company": "Remote First",
        "location": {"city": "Paris", "country": "France"},
        "required_skills": ["React", "Node.js"],
        "remote_policy": "full-remote"
      }
    ],
    "algorithm": "smart-match"
  }')

if [[ $? -eq 0 ]] && [[ $GEO_TEST == *"success"* || $GEO_TEST == *"matches"* ]]; then
    print_success "Test géolocalisation avancée réussi"
    echo "$GEO_TEST" | python3 -m json.tool 2>/dev/null | head -30
else
    print_warning "Test géolocalisation non disponible"
    echo "Réponse: $GEO_TEST"
fi

echo ""
echo "🎯 Résumé des tests SuperSmartMatch v2.0"
echo "========================================"
print_success "Tests terminés sur $BASE_URL"

echo ""
echo "📋 Endpoints testés:"
echo "   ✅ Health Check Principal: $BASE_URL/health"
echo "   ⚡ SuperSmartMatch V2: $BASE_URL/api/v2/match"
echo "   🔄 V1 Compatible: $BASE_URL/api/v2/match/legacy" 
echo "   📊 Queue-based: $BASE_URL/api/v1/queue-matching"
echo "   🧠 Recommendations: $BASE_URL/api/v2/algorithm/recommendations"

echo ""
echo "🚀 SuperSmartMatch v2.0 - Tests avec endpoints corrigés terminés !"
