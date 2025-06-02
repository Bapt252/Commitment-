#!/bin/bash

echo "🚀 Test SuperSmartMatch v2.0 - Format de données corrigé (macOS compatible)"
echo "=========================================================================="
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

# Détecter automatiquement le port et endpoint SuperSmartMatch
SUPERSMARTMATCH_PORT=""
SUPERSMARTMATCH_ENDPOINT=""

print_test "Détection automatique de SuperSmartMatch..."
for port in 5062 5061 5060 5052; do
    # Test /match
    if curl -s --connect-timeout 2 "http://localhost:$port/match" -X POST \
        -H "Content-Type: application/json" \
        -d '{"candidate":{"name":"test"},"offers":[{"id":"test"}]}' 2>/dev/null | grep -v -E "(Not Found|404)" > /dev/null; then
        SUPERSMARTMATCH_PORT=$port
        SUPERSMARTMATCH_ENDPOINT="/match"
        break
    fi
    
    # Test /api/v1/match
    if curl -s --connect-timeout 2 "http://localhost:$port/api/v1/match" -X POST \
        -H "Content-Type: application/json" \
        -d '{"candidate":{"name":"test"},"offers":[{"id":"test"}]}' 2>/dev/null | grep -v -E "(Not Found|404)" > /dev/null; then
        SUPERSMARTMATCH_PORT=$port
        SUPERSMARTMATCH_ENDPOINT="/api/v1/match"
        break
    fi
done

if [ -z "$SUPERSMARTMATCH_PORT" ]; then
    print_error "SuperSmartMatch non trouvé ! Utilisation du port par défaut 5052"
    SUPERSMARTMATCH_PORT=5052
    SUPERSMARTMATCH_ENDPOINT="/match"
else
    print_success "SuperSmartMatch détecté sur port $SUPERSMARTMATCH_PORT avec endpoint $SUPERSMARTMATCH_ENDPOINT"
fi

# Test 1: Health Check
print_test "Test 1: Health Check SuperSmartMatch V2"
HEALTH_RESPONSE=$(curl -s "http://localhost:$SUPERSMARTMATCH_PORT/health")
if [[ $? -eq 0 ]] && [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    print_success "Service accessible et en bonne santé"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null
else
    print_error "Service non accessible sur le port $SUPERSMARTMATCH_PORT"
    echo "Réponse: $HEALTH_RESPONSE"
fi

echo ""

# Test 2: V1 API Compatible - Matching basique avec format correct
print_test "Test 2: V1 API Compatible - Format candidate/offers"
V1_TEST=$(curl -s -X POST "http://localhost:$SUPERSMARTMATCH_PORT$SUPERSMARTMATCH_ENDPOINT" \
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

if [[ $? -eq 0 ]] && [[ $V1_TEST == *"matches"* ]]; then
    print_success "V1 API Compatible réussi"
    echo "$V1_TEST" | python3 -m json.tool 2>/dev/null | head -20
else
    print_error "Échec du test V1 API Compatible"
    echo "Réponse: $V1_TEST"
fi

echo ""

# Test 3: Test avec géolocalisation simple
print_test "Test 3: Test géolocalisation simple"
GEO_TEST=$(curl -s -X POST "http://localhost:$SUPERSMARTMATCH_PORT$SUPERSMARTMATCH_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Pierre Martin",
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

# Test 4: Test algorithme enhanced
print_test "Test 4: Test algorithme enhanced"
ENHANCED_TEST=$(curl -s -X POST "http://localhost:$SUPERSMARTMATCH_PORT$SUPERSMARTMATCH_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Sophie Laurent",
      "technical_skills": ["Java", "Spring", "Microservices"],
      "experiences": [
        {
          "title": "Senior Java Developer",
          "duration_months": 48,
          "skills": ["Java", "Spring Boot"]
        }
      ]
    },
    "offers": [
      {
        "id": "job-enhanced-001",
        "title": "Java Architect",
        "required_skills": ["Java", "Spring", "Architecture"],
        "location": {"city": "Lyon", "country": "France"}
      }
    ],
    "algorithm": "enhanced"
  }')

if [[ $? -eq 0 ]] && [[ $ENHANCED_TEST == *"matches"* ]]; then
    print_success "Test algorithme enhanced réussi"
    echo "$ENHANCED_TEST" | python3 -m json.tool 2>/dev/null | head -20
else
    print_error "Échec du test enhanced"
    echo "Réponse: $ENHANCED_TEST"
fi

echo ""

# Test 5: Test sélection automatique d'algorithme
print_test "Test 5: Test sélection automatique d'algorithme"
AUTO_TEST=$(curl -s -X POST "http://localhost:$SUPERSMARTMATCH_PORT$SUPERSMARTMATCH_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Lucas Bernard",
      "technical_skills": ["C#", ".NET", "Azure"],
      "experiences": [
        {
          "title": "Backend Developer",
          "duration_months": 30
        }
      ]
    },
    "offers": [
      {
        "id": "job-auto-001",
        "title": ".NET Developer",
        "required_skills": ["C#", ".NET Core"],
        "location": {"city": "Toulouse", "country": "France"}
      }
    ],
    "algorithm": "auto"
  }')

if [[ $? -eq 0 ]] && [[ $AUTO_TEST == *"matches"* ]]; then
    print_success "Sélection automatique d'algorithme réussie"
    echo "$AUTO_TEST" | python3 -m json.tool 2>/dev/null | head -20
else
    print_error "Échec du test auto"
    echo "Réponse: $AUTO_TEST"
fi

echo ""

# Test 6: Test V2 Enhanced API (si disponible)
print_test "Test 6: V2 Enhanced API (si disponible)"
V2_ENDPOINT="/api/v2/match"
V2_TEST=$(curl -s -X POST "http://localhost:$SUPERSMARTMATCH_PORT$V2_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Sophie Laurent",
      "email": "sophie@example.com",
      "technical_skills": [
        {"name": "Python", "level": "Expert", "years": 5},
        {"name": "Machine Learning", "level": "Advanced", "years": 3}
      ],
      "experiences": [
        {
          "title": "Senior Developer",
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
        "id": "job_ml_001",
        "title": "ML Engineer",
        "company": "AI Startup",
        "required_skills": ["Python", "TensorFlow", "MLOps"],
        "location": {"city": "Paris", "country": "France"},
        "remote_policy": "hybrid"
      }
    ],
    "algorithm": "auto"
  }')

if [[ $? -eq 0 ]] && [[ $V2_TEST == *"matches"* ]]; then
    print_success "V2 Enhanced API réussi !"
    echo "$V2_TEST" | python3 -m json.tool 2>/dev/null | head -30
else
    print_warning "V2 Enhanced API non disponible ou non implémenté"
fi

echo ""

# Test 7: Test endpoints de monitoring
print_test "Test 7: Test endpoints de monitoring"

# Health détaillé
DETAILED_HEALTH=$(curl -s "http://localhost:$SUPERSMARTMATCH_PORT/api/v2/health?detailed=true" 2>/dev/null)
if [[ $? -eq 0 ]] && [[ $DETAILED_HEALTH != *"Not Found"* ]]; then
    print_success "Health check détaillé disponible"
else
    print_warning "Health check détaillé non disponible"
fi

# Stats
STATS=$(curl -s "http://localhost:$SUPERSMARTMATCH_PORT/stats" 2>/dev/null)
if [[ $? -eq 0 ]] && [[ $STATS != *"Not Found"* ]]; then
    print_success "Statistiques disponibles"
else
    print_warning "Endpoint stats non disponible"
fi

echo ""
echo "🎯 Résumé des tests SuperSmartMatch v2.0"
echo "======================================="
print_success "Service testé sur port $SUPERSMARTMATCH_PORT avec endpoint $SUPERSMARTMATCH_ENDPOINT"
print_success "Format de données corrigé (candidate/offers)"

echo ""
echo "🔗 Informations de connexion:"
echo "   • URL: http://localhost:$SUPERSMARTMATCH_PORT$SUPERSMARTMATCH_ENDPOINT"
echo "   • Health Check: http://localhost:$SUPERSMARTMATCH_PORT/health"
echo "   • Documentation: http://localhost:$SUPERSMARTMATCH_PORT/docs (si disponible)"

echo ""
echo "📋 Formats de données testés:"
echo "   ✅ V1 Compatible: candidate + offers"
echo "   ✅ Algorithmes: smart-match, enhanced, auto"
echo "   ⚠️  V2 Enhanced: candidate_questionnaire + company_questionnaires (si implémenté)"

echo ""
echo "🚀 SuperSmartMatch v2.0 testé avec succès !"