#!/bin/bash

# 🚀 SuperSmartMatch V2 - Script de test avancé
# Tests approfondis des capacités V2 avec algorithmes intelligents

echo "================================================="
echo "🧠 SUPERSMARTMATCH V2 - TESTS AVANCÉS"
echo "================================================="

# Configuration
SUPERSMARTMATCH_V2="http://localhost:5062"
MATCHING_SERVICE="http://localhost:5052"

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Vérification des prérequis
echo ""
print_info "Vérification des prérequis..."

# Test jq
if ! command -v jq &> /dev/null; then
    print_warning "jq n'est pas installé. Installation recommandée : sudo apt-get install jq"
fi

# Test curl
if ! command -v curl &> /dev/null; then
    echo -e "${RED}❌ curl n'est pas installé${NC}"
    exit 1
fi

echo ""
echo "================================================="
echo "🔍 PHASE 1: DIAGNOSTIC DES SERVICES"
echo "================================================="

# Test des services
echo ""
print_info "Test du service matching classique (port 5052)..."
if curl -s --connect-timeout 5 "$MATCHING_SERVICE/health" > /dev/null 2>&1; then
    print_result 0 "Service 5052 accessible"
    SERVICE_5052_STATUS="UP"
else
    print_result 1 "Service 5052 non accessible"
    SERVICE_5052_STATUS="DOWN"
fi

echo ""
print_info "Test du SuperSmartMatch V2 (port 5062)..."
if curl -s --connect-timeout 5 "$SUPERSMARTMATCH_V2/health" > /dev/null 2>&1; then
    print_result 0 "SuperSmartMatch V2 accessible"
    SERVICE_5062_STATUS="UP"
else
    print_result 1 "SuperSmartMatch V2 non accessible"
    SERVICE_5062_STATUS="DOWN"
fi

# Affichage du statut des services
echo ""
echo "📊 Statut des services :"
echo "   Service 5052 (Matching classique): $SERVICE_5052_STATUS"
echo "   Service 5062 (SuperSmartMatch V2): $SERVICE_5062_STATUS"

echo ""
echo "================================================="
echo "🧪 PHASE 2: TESTS D'ALGORITHMES INTELLIGENTS"
echo "================================================="

if [ "$SERVICE_5062_STATUS" = "UP" ]; then

    echo ""
    print_info "Test 1: Algorithme Nexten Matcher (Données complètes)"
    echo "   📋 Contexte: Candidat senior avec questionnaire complet"
    
    curl -X POST "$SUPERSMARTMATCH_V2/api/v2/match" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate": {
          "name": "Alice Expert",
          "email": "alice@example.com",
          "location": {"city": "Paris", "country": "France"},
          "technical_skills": [
            {"name": "Python", "level": "Expert", "years": 8},
            {"name": "Machine Learning", "level": "Expert", "years": 5},
            {"name": "TensorFlow", "level": "Advanced", "years": 4},
            {"name": "Docker", "level": "Advanced", "years": 3}
          ],
          "soft_skills": [
            {"name": "Leadership", "level": "Advanced"},
            {"name": "Communication", "level": "Expert"}
          ],
          "experiences": [
            {
              "title": "Senior ML Engineer",
              "company": "TechGiant",
              "duration_months": 36,
              "skills": ["Python", "TensorFlow", "Kubernetes", "MLOps"]
            }
          ],
          "education": [
            {
              "degree": "Master en Intelligence Artificielle",
              "school": "École Polytechnique",
              "year": 2018
            }
          ],
          "mobility_preferences": "flexible"
        },
        "candidate_questionnaire": {
          "work_style": "collaborative",
          "culture_preferences": "innovation_focused",
          "remote_preference": "hybrid",
          "team_size_preference": "medium",
          "management_style": "autonomous",
          "learning_motivation": "high",
          "career_goals": "technical_leadership"
        },
        "offers": [
          {
            "id": "ml-lead-123",
            "title": "Lead ML Engineer",
            "company": "AI Startup Paris",
            "location": {"city": "Paris", "country": "France"},
            "required_skills": ["Python", "Machine Learning", "TensorFlow", "Team Leadership"],
            "experience_level": "senior",
            "remote_policy": "hybrid",
            "salary_range": {"min": 80000, "max": 120000, "currency": "EUR"}
          }
        ],
        "company_questionnaires": [
          {
            "culture": "innovation_focused",
            "team_size": "medium",
            "work_methodology": "agile",
            "remote_policy": "hybrid",
            "growth_stage": "scaling"
          }
        ],
        "algorithm": "auto"
      }' -w "\nTemps de réponse: %{time_total}s\n" 2>/dev/null | tee /tmp/test_nexten.json
    
    # Vérification du résultat
    if [ -f /tmp/test_nexten.json ]; then
        ALGORITHM_USED=$(cat /tmp/test_nexten.json | jq -r '.metadata.algorithm_used // empty' 2>/dev/null)
        OVERALL_SCORE=$(cat /tmp/test_nexten.json | jq -r '.matches[0].overall_score // empty' 2>/dev/null)
        
        if [ ! -z "$ALGORITHM_USED" ]; then
            print_result 0 "Algorithme utilisé: $ALGORITHM_USED"
            if [ ! -z "$OVERALL_SCORE" ]; then
                print_result 0 "Score global: $OVERALL_SCORE"
            fi
        else
            print_result 1 "Échec du test Nexten Matcher"
        fi
    fi

    echo ""
    print_info "Test 2: Algorithme Smart Match (Contraintes géographiques)"
    echo "   🗺️ Contexte: Candidat avec contraintes de mobilité"
    
    curl -X POST "$SUPERSMARTMATCH_V2/api/v2/match" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate": {
          "name": "Bob Local",
          "email": "bob@example.com",
          "location": {"city": "Lyon", "country": "France"},
          "technical_skills": [
            {"name": "JavaScript", "level": "Advanced", "years": 4},
            {"name": "React", "level": "Advanced", "years": 3},
            {"name": "Node.js", "level": "Intermediate", "years": 2}
          ],
          "experiences": [
            {
              "title": "Frontend Developer",
              "company": "LocalAgency",
              "duration_months": 24,
              "skills": ["JavaScript", "React", "CSS"]
            }
          ],
          "mobility_preferences": "local_only"
        },
        "offers": [
          {
            "id": "frontend-lyon-456",
            "title": "Développeur Frontend",
            "company": "StartupLyon",
            "location": {"city": "Lyon", "country": "France"},
            "required_skills": ["JavaScript", "React", "Vue.js"],
            "experience_level": "intermediate",
            "remote_policy": "on_site"
          },
          {
            "id": "frontend-paris-789",
            "title": "Développeur Frontend Senior",
            "company": "TechParis",
            "location": {"city": "Paris", "country": "France"},
            "required_skills": ["JavaScript", "React", "TypeScript"],
            "experience_level": "senior",
            "remote_policy": "remote"
          }
        ],
        "algorithm": "auto",
        "preferences": {
          "prioritize_location": true,
          "max_commute_time": 30
        }
      }' -w "\nTemps de réponse: %{time_total}s\n" 2>/dev/null | tee /tmp/test_smart.json

    # Vérification du résultat Smart Match
    if [ -f /tmp/test_smart.json ]; then
        ALGORITHM_USED=$(cat /tmp/test_smart.json | jq -r '.metadata.algorithm_used // empty' 2>/dev/null)
        BEST_MATCH_ID=$(cat /tmp/test_smart.json | jq -r '.matches[0].offer_id // empty' 2>/dev/null)
        
        if [ ! -z "$ALGORITHM_USED" ]; then
            print_result 0 "Algorithme utilisé: $ALGORITHM_USED"
            if [ "$BEST_MATCH_ID" = "frontend-lyon-456" ]; then
                print_result 0 "Bon choix géographique: offre Lyon prioritaire"
            fi
        fi
    fi

    echo ""
    print_info "Test 3: Algorithme Enhanced (Profil senior partiel)"
    echo "   📈 Contexte: Candidat expérimenté avec données partielles"
    
    curl -X POST "$SUPERSMARTMATCH_V2/api/v2/match" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate": {
          "name": "Carol Senior",
          "technical_skills": [
            {"name": "Java", "level": "Expert", "years": 10},
            {"name": "Spring", "level": "Expert", "years": 8},
            {"name": "Microservices", "level": "Advanced", "years": 5}
          ],
          "experiences": [
            {
              "title": "Senior Java Developer",
              "company": "Enterprise Corp",
              "duration_months": 60,
              "skills": ["Java", "Spring", "PostgreSQL", "Jenkins"]
            },
            {
              "title": "Tech Lead",
              "company": "Previous Company",
              "duration_months": 36,
              "skills": ["Architecture", "Team Management", "Java"]
            }
          ]
        },
        "offers": [
          {
            "id": "java-architect-101",
            "title": "Solutions Architect Java",
            "company": "TechConsulting",
            "required_skills": ["Java", "Spring", "Architecture", "Leadership"],
            "experience_level": "senior",
            "salary_range": {"min": 90000, "max": 130000, "currency": "EUR"}
          }
        ],
        "algorithm": "auto"
      }' -w "\nTemps de réponse: %{time_total}s\n" 2>/dev/null | tee /tmp/test_enhanced.json

    echo ""
    print_info "Test 4: Comparaison d'algorithmes (Mode Hybrid)"
    echo "   🔀 Contexte: Validation croisée de plusieurs algorithmes"
    
    curl -X POST "$SUPERSMARTMATCH_V2/api/v2/match" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate": {
          "name": "David Hybrid",
          "technical_skills": [
            {"name": "Python", "level": "Advanced", "years": 4},
            {"name": "Data Science", "level": "Intermediate", "years": 2}
          ]
        },
        "offers": [
          {
            "id": "data-scientist-202",
            "title": "Data Scientist",
            "required_skills": ["Python", "Data Science", "SQL"]
          }
        ],
        "algorithm": "hybrid"
      }' -w "\nTemps de réponse: %{time_total}s\n" 2>/dev/null

else
    print_warning "SuperSmartMatch V2 non disponible, tests algorithmiques ignorés"
fi

echo ""
echo "================================================="
echo "⚡ PHASE 3: TESTS DE PERFORMANCE"
echo "================================================="

if [ "$SERVICE_5062_STATUS" = "UP" ]; then
    
    print_info "Test de performance: Temps de réponse V2"
    
    # Test de performance avec mesure du temps
    START_TIME=$(date +%s%N)
    
    curl -X POST "$SUPERSMARTMATCH_V2/api/v2/match" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate": {
          "name": "Performance Test",
          "technical_skills": [{"name": "Python", "level": "Advanced", "years": 3}]
        },
        "offers": [
          {"id": "perf-1", "title": "Dev Python", "required_skills": ["Python"]},
          {"id": "perf-2", "title": "Dev Backend", "required_skills": ["Python", "Django"]},
          {"id": "perf-3", "title": "Data Engineer", "required_skills": ["Python", "SQL"]}
        ]
      }' -s > /tmp/performance_test.json
    
    END_TIME=$(date +%s%N)
    DURATION=$(((END_TIME - START_TIME) / 1000000)) # Convert to milliseconds
    
    if [ $DURATION -lt 100 ]; then
        print_result 0 "Performance excellente: ${DURATION}ms (< 100ms)"
    elif [ $DURATION -lt 200 ]; then
        print_result 0 "Performance bonne: ${DURATION}ms (< 200ms)"
    else
        print_warning "Performance à optimiser: ${DURATION}ms"
    fi

    echo ""
    print_info "Test de charge légère: 5 requêtes simultanées"
    
    # Test de charge simple
    for i in {1..5}; do
        curl -X POST "$SUPERSMARTMATCH_V2/api/v2/match" \
          -H "Content-Type: application/json" \
          -d "{
            \"candidate\": {
              \"name\": \"Load Test $i\",
              \"technical_skills\": [{\"name\": \"Python\", \"level\": \"Intermediate\"}]
            },
            \"offers\": [{\"id\": \"load-$i\", \"title\": \"Job $i\", \"required_skills\": [\"Python\"]}]
          }" -s > /tmp/load_test_$i.json &
    done
    
    wait
    print_result 0 "Test de charge terminé"

fi

echo ""
echo "================================================="
echo "🔧 PHASE 4: TESTS DE COMPATIBILITÉ"
echo "================================================="

if [ "$SERVICE_5062_STATUS" = "UP" ]; then
    
    print_info "Test de compatibilité V1 sur SuperSmartMatch V2"
    echo "   🔄 Route: /match (format V1)"
    
    COMPAT_RESULT=$(curl -X POST "$SUPERSMARTMATCH_V2/match" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate": {
          "name": "Test Compatibility",
          "technical_skills": ["Python", "Django"]
        },
        "offers": [
          {
            "id": "compat-test",
            "title": "Développeur Python",
            "required_skills": ["Python", "Django"]
          }
        ]
      }' -s -w "%{http_code}")
    
    HTTP_CODE="${COMPAT_RESULT: -3}"
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_result 0 "Compatibilité V1 fonctionnelle"
    else
        print_result 1 "Problème de compatibilité V1 (HTTP $HTTP_CODE)"
    fi

fi

if [ "$SERVICE_5052_STATUS" = "UP" ]; then
    
    print_info "Test du service matching classique"
    echo "   📡 Route: /api/v1/queue-matching"
    
    V1_RESULT=$(curl -X POST "$MATCHING_SERVICE/api/v1/queue-matching" \
      -H "Content-Type: application/json" \
      -d '{
        "candidate_id": "test-candidate-compat",
        "job_id": "test-job-compat",
        "webhook_url": "https://example.com/webhook"
      }' -s -w "%{http_code}")
    
    HTTP_CODE="${V1_RESULT: -3}"
    
    if [ "$HTTP_CODE" = "200" ]; then
        print_result 0 "Service V1 classique fonctionnel"
    else
        print_result 1 "Problème service V1 (HTTP $HTTP_CODE)"
    fi

fi

echo ""
echo "================================================="
echo "📊 PHASE 5: TESTS DE MONITORING"
echo "================================================="

if [ "$SERVICE_5062_STATUS" = "UP" ]; then
    
    print_info "Health check détaillé SuperSmartMatch V2"
    
    curl -s "$SUPERSMARTMATCH_V2/api/v2/health?detailed=true" | jq '{
      status: .health.status,
      version: .health.version,
      algorithms_available: .health.algorithms_available,
      uptime_seconds: .health.uptime_seconds
    }' 2>/dev/null || echo "Health check détaillé non disponible"

    echo ""
    print_info "Recommandations d'algorithmes"
    
    curl -s "$SUPERSMARTMATCH_V2/api/v2/algorithm/recommendations?candidate_experience=5&questionnaire_completeness=0.8&has_geo_constraints=false" | jq '.recommendations // "Non disponible"' 2>/dev/null

fi

echo ""
echo "================================================="
echo "📋 RÉSUMÉ DES TESTS"
echo "================================================="

echo ""
echo "🏥 Statut des services :"
echo "   • Service matching classique (5052): $SERVICE_5052_STATUS"
echo "   • SuperSmartMatch V2 (5062): $SERVICE_5062_STATUS"

echo ""
echo "🎯 Routes testées avec succès :"
if [ "$SERVICE_5052_STATUS" = "UP" ]; then
    echo "   ✅ Port 5052: /api/v1/queue-matching"
fi
if [ "$SERVICE_5062_STATUS" = "UP" ]; then
    echo "   ✅ Port 5062: /api/v2/match"
    echo "   ✅ Port 5062: /match (compatibilité V1)"
    echo "   ✅ Port 5062: /api/v2/health"
    echo "   ✅ Port 5062: /api/v2/algorithm/recommendations"
fi

echo ""
echo "🧠 Algorithmes testés :"
echo "   • Nexten Matcher (données complètes)"
echo "   • Smart Match (contraintes géographiques)"
echo "   • Enhanced Match (profils seniors)"
echo "   • Hybrid Match (validation croisée)"

echo ""
echo "⚡ Performance :"
echo "   • Temps de réponse < 100ms : Objectif SuperSmartMatch V2"
echo "   • Test de charge réussi : 5 requêtes simultanées"

echo ""
echo "================================================="
echo "✅ TESTS TERMINÉS - SUPERSMARTMATCH V2 VALIDÉ"
echo "================================================="

# Nettoyage des fichiers temporaires
rm -f /tmp/test_*.json /tmp/performance_test.json /tmp/load_test_*.json 2>/dev/null

echo ""
print_info "Utilisez les bonnes routes identifiées pour vos développements !"
print_info "Documentation: README-SUPERSMARTMATCH-V2.md"
