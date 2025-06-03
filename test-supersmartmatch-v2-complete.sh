#!/bin/bash

# 🧪 SuperSmartMatch V2 - Script de Test Complet
# Tests automatisés pour validation de l'implémentation

set -euo pipefail

# Configuration couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Emojis
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
GEAR="⚙️"
TEST="🧪"

# Variables
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
TEST_RESULTS=()

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}${INFO} [INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}${SUCCESS} [SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}${ERROR} [ERROR]${NC} $1"
}

log_test() {
    echo -e "${CYAN}${TEST} [TEST]${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_test "Test: $test_name"
    
    if result=$(eval "$test_command" 2>&1); then
        if echo "$result" | grep -q "$expected_pattern"; then
            PASSED_TESTS=$((PASSED_TESTS + 1))
            log_success "$test_name - PASSED"
            TEST_RESULTS+=("✅ $test_name")
            return 0
        else
            FAILED_TESTS=$((FAILED_TESTS + 1))
            log_error "$test_name - FAILED (pattern not found)"
            log_error "Expected pattern: $expected_pattern"
            log_error "Actual result: $result"
            TEST_RESULTS+=("❌ $test_name - Pattern not found")
            return 1
        fi
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        log_error "$test_name - FAILED (command error)"
        log_error "Error: $result"
        TEST_RESULTS+=("❌ $test_name - Command failed")
        return 1
    fi
}

print_banner() {
    echo -e "${PURPLE}"
    echo "════════════════════════════════════════════════════════════════"
    echo "🧪 SuperSmartMatch V2 - Tests Automatisés Complets"
    echo "   Validation de l'implémentation prototype"
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Tests de santé des services
test_service_health() {
    log_info "Tests de santé des services..."
    
    run_test "SuperSmartMatch V2 Health" \
        "curl -s http://localhost:5070/health" \
        "healthy"
    
    run_test "Nexten Matcher Health" \
        "curl -s http://localhost:5052/health" \
        "health"
    
    run_test "SuperSmartMatch V1 Health" \
        "curl -s http://localhost:5062/health" \
        "health"
}

# Tests API V2 native
test_api_v2() {
    log_info "Tests API V2 native..."
    
    # Test sélection auto -> Nexten
    local nexten_payload='{
        "candidate": {
            "name": "Expert ML",
            "technical_skills": [{"name": "Python", "level": "Expert", "years": 7}]
        },
        "candidate_questionnaire": {
            "work_style": "analytical",
            "culture_preferences": "data_driven"
        },
        "offers": [{"id": "ml_job", "title": "ML Engineer"}],
        "algorithm": "auto"
    }'
    
    run_test "API V2 - Sélection Nexten Auto" \
        "curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '$nexten_payload'" \
        "success"
    
    # Test sélection géographique -> Smart
    local geo_payload='{
        "candidate": {
            "name": "Dev Mobile",
            "technical_skills": ["JavaScript", "React"],
            "localisation": "Lyon"
        },
        "offers": [{"id": "job_paris", "localisation": "Paris"}],
        "algorithm": "auto"
    }'
    
    run_test "API V2 - Sélection Smart Géo" \
        "curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '$geo_payload'" \
        "success"
    
    # Test profil sénior -> Enhanced
    local senior_payload='{
        "candidate": {
            "name": "Tech Lead",
            "technical_skills": ["Java", "Architecture"],
            "experiences": [
                {"duration_months": 48, "title": "Tech Lead"},
                {"duration_months": 36, "title": "Senior Dev"}
            ]
        },
        "offers": [{"id": "lead_job", "title": "Engineering Manager"}],
        "algorithm": "auto"
    }'
    
    run_test "API V2 - Sélection Enhanced Sénior" \
        "curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '$senior_payload'" \
        "success"
}

# Tests compatibilité V1
test_api_v1_compatibility() {
    log_info "Tests compatibilité API V1..."
    
    local v1_payload='{
        "candidate": {
            "name": "Marie Martin",
            "technical_skills": ["Python", "Django", "React"]
        },
        "offers": [
            {
                "id": "dev-python-123",
                "title": "Développeur Full Stack",
                "required_skills": ["Python", "Django", "JavaScript"]
            }
        ],
        "algorithm": "smart"
    }'
    
    run_test "API V1 Compatible - Match Legacy" \
        "curl -s -X POST http://localhost:5070/match -H 'Content-Type: application/json' -d '$v1_payload'" \
        "matches"
}

# Tests de performance
test_performance() {
    log_info "Tests de performance..."
    
    local quick_payload='{"candidate":{"name":"Test"},"offers":[{"id":"1"}]}'
    
    # Test temps de réponse
    run_test "Performance - Response Time < 1s" \
        "timeout 1 curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '$quick_payload'" \
        "success"
    
    # Test métriques
    run_test "Métriques - Disponibles" \
        "curl -s http://localhost:5070/metrics" \
        "supersmartmatch"
}

# Tests algorithmes spécifiques
test_algorithms() {
    log_info "Tests algorithmes spécifiques..."
    
    local base_payload='{"candidate":{"name":"Test"},"offers":[{"id":"1"}]}'
    
    # Test forçage Nexten
    run_test "Algorithme - Force Nexten" \
        "curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '{\"candidate\":{\"name\":\"Test\"},\"offers\":[{\"id\":\"1\"}],\"algorithm\":\"nexten\"}'" \
        "success"
    
    # Test forçage Smart
    run_test "Algorithme - Force Smart" \
        "curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '{\"candidate\":{\"name\":\"Test\"},\"offers\":[{\"id\":\"1\"}],\"algorithm\":\"smart\"}'" \
        "success"
    
    # Test forçage Enhanced
    run_test "Algorithme - Force Enhanced" \
        "curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '{\"candidate\":{\"name\":\"Test\"},\"offers\":[{\"id\":\"1\"}],\"algorithm\":\"enhanced\"}'" \
        "success"
}

# Tests d'intégration
test_integration() {
    log_info "Tests d'intégration services..."
    
    # Test Redis cache
    run_test "Redis Cache - Connectivity" \
        "redis-cli ping" \
        "PONG"
    
    # Test connectivité Nexten
    run_test "Nexten Integration - Direct Test" \
        "curl -s -X POST http://localhost:5052/api/v1/queue-matching -H 'Content-Type: application/json' -d '{\"candidate_id\":\"test\",\"job_id\":\"test\",\"webhook_url\":\"https://example.com\"}'" \
        "job_id"
}

# Tests de charge légers
test_load() {
    log_info "Tests de charge légers..."
    
    local simple_payload='{"candidate":{"name":"Load Test"},"offers":[{"id":"load_1"}]}'
    
    # Test 5 requêtes simultanées
    run_test "Load Test - 5 Requêtes Concurrentes" \
        "for i in {1..5}; do curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '$simple_payload' & done; wait" \
        "success"
}

# Tests cas d'usage réels
test_real_cases() {
    log_info "Tests cas d'usage réels..."
    
    # Cas ML Engineer complet
    local ml_case='{
        "candidate": {
            "name": "Alice Chen",
            "email": "alice@example.com",
            "technical_skills": [
                {"name": "Python", "level": "Expert", "years": 6},
                {"name": "TensorFlow", "level": "Advanced", "years": 4},
                {"name": "MLOps", "level": "Intermediate", "years": 2}
            ],
            "experiences": [
                {
                    "title": "Senior ML Engineer",
                    "company": "DataCorp",
                    "duration_months": 24,
                    "skills": ["Python", "TensorFlow", "AWS"]
                }
            ]
        },
        "candidate_questionnaire": {
            "work_style": "analytical",
            "culture_preferences": "data_driven",
            "remote_preference": "hybrid"
        },
        "offers": [
            {
                "id": "ml_engineer_001",
                "title": "Senior ML Engineer",
                "company": "AI Startup",
                "required_skills": ["Python", "TensorFlow", "AWS"],
                "location": {"city": "Paris", "country": "France"},
                "remote_policy": "hybrid"
            }
        ],
        "company_questionnaires": [
            {
                "culture": "data_driven",
                "team_size": "medium",
                "work_methodology": "agile"
            }
        ],
        "algorithm": "auto"
    }'
    
    run_test "Cas Réel - ML Engineer Complet" \
        "curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '$ml_case'" \
        "success"
    
    # Cas géolocalisation
    local geo_case='{
        "candidate": {
            "name": "Pierre Durand",
            "technical_skills": ["JavaScript", "React", "Node.js"],
            "localisation": "Lyon",
            "mobility": true
        },
        "offers": [
            {"id": "js_paris", "localisation": "Paris", "title": "Dev Frontend"},
            {"id": "js_marseille", "localisation": "Marseille", "title": "Dev Frontend"}
        ],
        "algorithm": "auto"
    }'
    
    run_test "Cas Réel - Contraintes Géographiques" \
        "curl -s -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '$geo_case'" \
        "success"
}

# Résumé des tests
show_test_summary() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}${ROCKET} Résumé des Tests SuperSmartMatch V2${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    
    echo -e "\n${CYAN}📊 Statistiques:${NC}"
    echo -e "  Total tests: ${WHITE}${TOTAL_TESTS}${NC}"
    echo -e "  Réussis: ${GREEN}${PASSED_TESTS}${NC}"
    echo -e "  Échoués: ${RED}${FAILED_TESTS}${NC}"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "  Taux de réussite: ${GREEN}100%${NC} ${SUCCESS}"
    else
        local success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
        echo -e "  Taux de réussite: ${YELLOW}${success_rate}%${NC}"
    fi
    
    echo -e "\n${CYAN}📋 Détail des résultats:${NC}"
    for result in "${TEST_RESULTS[@]}"; do
        echo "  $result"
    done
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${SUCCESS} ${GREEN}Tous les tests sont passés ! SuperSmartMatch V2 est opérationnel.${NC}"
    else
        echo -e "\n${WARNING} ${YELLOW}Certains tests ont échoué. Vérifiez la configuration.${NC}"
    fi
    
    echo -e "\n${INFO} ${BLUE}Services accessibles:${NC}"
    echo -e "  • SuperSmartMatch V2: http://localhost:5070"
    echo -e "  • Dashboard: http://localhost:5070/dashboard"
    echo -e "  • Métriques: http://localhost:5070/metrics"
    echo -e "  • Documentation API: http://localhost:5070/docs"
}

# Vérification prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    if ! command -v curl &> /dev/null; then
        log_error "curl non installé"
        exit 1
    fi
    
    if ! command -v redis-cli &> /dev/null; then
        log_info "redis-cli non trouvé, tests Redis ignorés"
    fi
    
    # Test connectivité service principal
    if ! curl -s http://localhost:5070/health > /dev/null; then
        log_error "SuperSmartMatch V2 non accessible sur le port 5070"
        log_info "Démarrez les services avec: ./deploy-supersmartmatch-v2.sh"
        exit 1
    fi
    
    log_success "Prérequis satisfaits"
}

# Fonction principale
main() {
    print_banner
    
    check_prerequisites
    
    # Exécution des tests
    test_service_health
    test_api_v2
    test_api_v1_compatibility
    test_algorithms
    test_performance
    test_integration
    test_load
    test_real_cases
    
    show_test_summary
    
    # Code de sortie
    if [ $FAILED_TESTS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Gestion des signaux
cleanup() {
    log_info "Nettoyage des processus de test..."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Exécution
main "$@"
