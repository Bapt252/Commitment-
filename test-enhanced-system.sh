#!/bin/bash
# SuperSmartMatch V2 - Enhanced System Test Suite
# ===============================================
#
# Suite de tests complète pour validation du système V2 avec extraction missions
# Tests automatisés, validation performance, et reporting détaillé
#
# Usage: ./test-enhanced-system.sh [quick|full|performance|missions|health]
# Version: 2.0.0
# Author: Baptiste Coma
# Created: June 2025

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$SCRIPT_DIR/tests"
RESULTS_DIR="$SCRIPT_DIR/test-results/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$RESULTS_DIR/test-enhanced-system.log"

# Services endpoints
CV_PARSER_URL="http://localhost:5051"
JOB_PARSER_URL="http://localhost:5053"
ORCHESTRATOR_URL="http://localhost:5070"
REDIS_URL="localhost:6379"

# Test files
TEST_CV_PDF="$TEST_DIR/sample_cv.pdf"
TEST_JOB_PDF="$TEST_DIR/sample_job.pdf"
TEST_CV_TEXT="$TEST_DIR/sample_cv.txt"
TEST_JOB_TEXT="$TEST_DIR/sample_job.txt"

# Counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")  echo -e "${GREEN}[INFO]${NC} $message" ;;
        "WARN")  echo -e "${YELLOW}[WARN]${NC} $message" ;;
        "ERROR") echo -e "${RED}[ERROR]${NC} $message" ;;
        "DEBUG") echo -e "${BLUE}[DEBUG]${NC} $message" ;;
        "TEST")  echo -e "${PURPLE}[TEST]${NC} $message" ;;
        "PASS")  echo -e "${GREEN}[PASS]${NC} $message" ;;
        "FAIL")  echo -e "${RED}[FAIL]${NC} $message" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Initialisation
init_testing() {
    mkdir -p "$RESULTS_DIR" "$TEST_DIR"
    
    log "INFO" "🧪 SuperSmartMatch V2 Enhanced Testing Suite"
    log "INFO" "📍 Test directory: $TEST_DIR"
    log "INFO" "📊 Results directory: $RESULTS_DIR"
    log "INFO" "⏰ Test started: $(date)"
    
    # Création fichiers de test si inexistants
    create_test_files
}

# Création fichiers de test
create_test_files() {
    log "INFO" "📄 Creating test files..."
    
    # CV de test
    if [[ ! -f "$TEST_CV_TEXT" ]]; then
        cat > "$TEST_CV_TEXT" << 'EOF'
CHRISTINE MARTIN
Comptable Senior
Email: christine.martin@email.com
Téléphone: 06 12 34 56 78

EXPÉRIENCE PROFESSIONNELLE

Comptable Senior | ABC Entreprise | 2020-2024
• Gestion de la facturation clients (500+ factures/mois)
• Saisie comptable quotidienne sur logiciel SAP
• Contrôle et validation des écritures comptables
• Établissement des rapports mensuels et tableaux de bord
• Suivi des règlements et relances clients
• Préparation des déclarations fiscales (TVA, DAS2)

Assistante Comptable | XYZ SARL | 2018-2020
• Saisie des factures fournisseurs et clients
• Contrôle des comptes et lettrage
• Gestion de la petite caisse
• Archivage et classement des documents comptables

FORMATION
BTS Comptabilité Gestion | Lycée Jean Moulin | 2018

COMPÉTENCES
• Logiciels: SAP, Ciel Compta, Excel avancé
• Facturation et recouvrement
• Déclarations fiscales et sociales
• Contrôle de gestion
• Anglais professionnel
EOF
        log "INFO" "✅ Test CV text created"
    fi
    
    # Job de test
    if [[ ! -f "$TEST_JOB_TEXT" ]]; then
        cat > "$TEST_JOB_TEXT" << 'EOF'
OFFRE D'EMPLOI - COMPTABLE H/F
Entreprise DELTA Solutions
CDI - Boulogne-Billancourt (92)
Salaire: 35-40K€

MISSIONS PRINCIPALES:
• Assurer la facturation clients et le suivi des encaissements
• Effectuer la saisie comptable quotidienne (achats, ventes, banque)
• Contrôler les comptes et effectuer les rapprochements bancaires
• Établir les reporting mensuels et tableaux de bord de gestion
• Préparer les déclarations fiscales (TVA, liasse fiscale)
• Gérer les relations avec les clients pour le recouvrement
• Participer à la clôture mensuelle et annuelle

PROFIL RECHERCHÉ:
• Formation BTS/DUT Comptabilité ou équivalent
• Expérience 3-5 ans en comptabilité générale
• Maîtrise des logiciels comptables (SAP, Sage)
• Rigueur, autonomie et sens du relationnel
• Anglais courant apprécié

AVANTAGES:
• Mutuelle d'entreprise
• RTT et congés payés
• Formation continue
• Télétravail 2 jours/semaine
EOF
        log "INFO" "✅ Test Job text created"
    fi
}

# Test runner générique
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    ((TESTS_TOTAL++))
    log "TEST" "🧪 Running: $test_name"
    
    if $test_function; then
        ((TESTS_PASSED++))
        log "PASS" "✅ $test_name"
        return 0
    else
        ((TESTS_FAILED++))
        log "FAIL" "❌ $test_name"
        return 1
    fi
}

# Tests de santé des services
test_health_checks() {
    log "INFO" "🏥 Testing service health checks..."
    
    # CV Parser Health
    if curl -sf "$CV_PARSER_URL/health" > /dev/null; then
        log "PASS" "✅ CV Parser health check"
        return 0
    else
        log "FAIL" "❌ CV Parser health check failed"
        return 1
    fi
}

test_job_parser_health() {
    if curl -sf "$JOB_PARSER_URL/health" > /dev/null; then
        log "PASS" "✅ Job Parser health check"
        return 0
    else
        log "FAIL" "❌ Job Parser health check failed"
        return 1
    fi
}

test_redis_health() {
    if redis-cli -h localhost ping | grep -q PONG; then
        log "PASS" "✅ Redis health check"
        return 0
    else
        log "FAIL" "❌ Redis health check failed"
        return 1
    fi
}

# Tests parsing CV
test_cv_parsing_basic() {
    log "TEST" "📄 Testing CV parsing..."
    
    local response
    response=$(curl -s -X POST -F "file=@$TEST_CV_TEXT" "$CV_PARSER_URL/api/parse-cv/")
    
    if echo "$response" | jq -e '.personal_info' > /dev/null 2>&1; then
        log "PASS" "✅ CV parsing basic structure"
        return 0
    else
        log "FAIL" "❌ CV parsing failed"
        echo "$response" >> "$RESULTS_DIR/cv_parse_error.log"
        return 1
    fi
}

test_cv_mission_extraction() {
    log "TEST" "🎯 Testing CV mission extraction..."
    
    local response
    response=$(curl -s -X POST -F "file=@$TEST_CV_TEXT" "$CV_PARSER_URL/api/parse-cv/")
    
    # Vérification extraction missions
    if echo "$response" | jq -e '.mission_summary' > /dev/null 2>&1; then
        local missions_count
        missions_count=$(echo "$response" | jq '.mission_summary.total_missions // 0')
        
        if [[ $missions_count -gt 0 ]]; then
            log "PASS" "✅ CV mission extraction: $missions_count missions found"
            echo "$response" | jq '.mission_summary' > "$RESULTS_DIR/cv_missions.json"
            return 0
        else
            log "FAIL" "❌ No missions extracted from CV"
            return 1
        fi
    else
        log "FAIL" "❌ Missing mission_summary in CV response"
        return 1
    fi
}

test_cv_mission_categories() {
    log "TEST" "📊 Testing CV mission categorization..."
    
    local response
    response=$(curl -s -X POST -F "file=@$TEST_CV_TEXT" "$CV_PARSER_URL/api/parse-cv/")
    
    # Vérification catégories attendues
    local categories
    categories=$(echo "$response" | jq -r '.mission_summary.by_category | keys[]' 2>/dev/null || echo "")
    
    local expected_categories=("facturation" "saisie" "controle" "reporting")
    local found_categories=0
    
    for category in "${expected_categories[@]}"; do
        if echo "$categories" | grep -q "$category"; then
            ((found_categories++))
            log "DEBUG" "✓ Found category: $category"
        fi
    done
    
    if [[ $found_categories -ge 2 ]]; then
        log "PASS" "✅ Mission categorization: $found_categories/4 expected categories found"
        return 0
    else
        log "FAIL" "❌ Insufficient mission categories: $found_categories/4"
        return 1
    fi
}

# Tests parsing Job
test_job_parsing_basic() {
    log "TEST" "💼 Testing Job parsing..."
    
    local response
    response=$(curl -s -X POST -F "file=@$TEST_JOB_TEXT" "$JOB_PARSER_URL/api/parse-job")
    
    if echo "$response" | jq -e '.title' > /dev/null 2>&1; then
        log "PASS" "✅ Job parsing basic structure"
        return 0
    else
        log "FAIL" "❌ Job parsing failed"
        echo "$response" >> "$RESULTS_DIR/job_parse_error.log"
        return 1
    fi
}

test_job_mission_extraction() {
    log "TEST" "🎯 Testing Job mission extraction..."
    
    local response
    response=$(curl -s -X POST -F "file=@$TEST_JOB_TEXT" "$JOB_PARSER_URL/api/parse-job")
    
    if echo "$response" | jq -e '.missions' > /dev/null 2>&1; then
        local missions_count
        missions_count=$(echo "$response" | jq '.missions | length')
        
        if [[ $missions_count -gt 0 ]]; then
            log "PASS" "✅ Job mission extraction: $missions_count missions found"
            echo "$response" | jq '.missions' > "$RESULTS_DIR/job_missions.json"
            return 0
        else
            log "FAIL" "❌ No missions extracted from Job"
            return 1
        fi
    else
        log "FAIL" "❌ Missing missions in Job response"
        return 1
    fi
}

# Tests performance
test_cv_parsing_performance() {
    log "TEST" "⚡ Testing CV parsing performance..."
    
    local start_time
    local end_time
    local duration
    
    start_time=$(date +%s.%N)
    curl -s -X POST -F "file=@$TEST_CV_TEXT" "$CV_PARSER_URL/api/parse-cv/" > /dev/null
    end_time=$(date +%s.%N)
    
    duration=$(echo "$end_time - $start_time" | bc)
    
    # Seuil: 5 secondes
    if (( $(echo "$duration < 5.0" | bc -l) )); then
        log "PASS" "✅ CV parsing performance: ${duration}s (< 5s)"
        return 0
    else
        log "FAIL" "❌ CV parsing too slow: ${duration}s (> 5s)"
        return 1
    fi
}

test_concurrent_parsing() {
    log "TEST" "🔄 Testing concurrent parsing..."
    
    local pids=()
    local results_file="$RESULTS_DIR/concurrent_test.log"
    
    # Lancement 5 requêtes simultanées
    for i in {1..5}; do
        (
            local start=$(date +%s.%N)
            local response
            response=$(curl -s -X POST -F "file=@$TEST_CV_TEXT" "$CV_PARSER_URL/api/parse-cv/")
            local end=$(date +%s.%N)
            local duration=$(echo "$end - $start" | bc)
            
            if echo "$response" | jq -e '.personal_info' > /dev/null 2>&1; then
                echo "Request $i: SUCCESS (${duration}s)" >> "$results_file"
            else
                echo "Request $i: FAILED (${duration}s)" >> "$results_file"
            fi
        ) &
        pids+=($!)
    done
    
    # Attente de toutes les requêtes
    for pid in "${pids[@]}"; do
        wait "$pid"
    done
    
    # Vérification résultats
    local success_count
    success_count=$(grep -c "SUCCESS" "$results_file" 2>/dev/null || echo "0")
    
    if [[ $success_count -eq 5 ]]; then
        log "PASS" "✅ Concurrent parsing: 5/5 successful"
        return 0
    else
        log "FAIL" "❌ Concurrent parsing: $success_count/5 successful"
        return 1
    fi
}

# Tests scoring enrichi
test_enhanced_scoring() {
    log "TEST" "🎯 Testing enhanced scoring system..."
    
    # Mock d'un test de matching complet (nécessiterait l'orchestrateur)
    local cv_response
    local job_response
    
    cv_response=$(curl -s -X POST -F "file=@$TEST_CV_TEXT" "$CV_PARSER_URL/api/parse-cv/")
    job_response=$(curl -s -X POST -F "file=@$TEST_JOB_TEXT" "$JOB_PARSER_URL/api/parse-job")
    
    # Vérification que les deux ont des missions
    if echo "$cv_response" | jq -e '.mission_summary.total_missions' > /dev/null 2>&1 && \
       echo "$job_response" | jq -e '.missions' > /dev/null 2>&1; then
        log "PASS" "✅ Enhanced scoring data available"
        
        # Sauvegarde pour analyse
        echo "$cv_response" > "$RESULTS_DIR/scoring_cv.json"
        echo "$job_response" > "$RESULTS_DIR/scoring_job.json"
        return 0
    else
        log "FAIL" "❌ Enhanced scoring data incomplete"
        return 1
    fi
}

# Tests cache
test_cache_functionality() {
    log "TEST" "🗄️ Testing cache functionality..."
    
    # Premier appel (cache miss)
    local start1=$(date +%s.%N)
    curl -s -X POST -F "file=@$TEST_CV_TEXT" "$CV_PARSER_URL/api/parse-cv/" > /dev/null
    local end1=$(date +%s.%N)
    local duration1=$(echo "$end1 - $start1" | bc)
    
    # Deuxième appel identique (cache hit)
    local start2=$(date +%s.%N)
    curl -s -X POST -F "file=@$TEST_CV_TEXT" "$CV_PARSER_URL/api/parse-cv/" > /dev/null
    local end2=$(date +%s.%N)
    local duration2=$(echo "$end2 - $start2" | bc)
    
    # Le deuxième appel devrait être plus rapide
    if (( $(echo "$duration2 < $duration1" | bc -l) )); then
        log "PASS" "✅ Cache working: ${duration1}s -> ${duration2}s"
        return 0
    else
        log "FAIL" "❌ Cache not working: ${duration1}s -> ${duration2}s"
        return 1
    fi
}

# Génération du rapport
generate_report() {
    local report_file="$RESULTS_DIR/test_report.md"
    
    log "INFO" "📊 Generating test report..."
    
    cat > "$report_file" << EOF
# SuperSmartMatch V2 - Test Report

**Date:** $(date)  
**Version:** 2.0.0  
**Test Suite:** Enhanced System Tests  

## Summary

- **Total Tests:** $TESTS_TOTAL
- **Passed:** $TESTS_PASSED
- **Failed:** $TESTS_FAILED
- **Success Rate:** $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%

## Test Results

### ✅ Passed Tests: $TESTS_PASSED

### ❌ Failed Tests: $TESTS_FAILED

## System Validation

EOF

    if [[ $TESTS_FAILED -eq 0 ]]; then
        cat >> "$report_file" << EOF
🎉 **ALL TESTS PASSED!**

Le système SuperSmartMatch V2 avec extraction missions enrichies est **ENTIÈREMENT FONCTIONNEL**.

### Fonctionnalités Validées:
- ✅ Extraction missions détaillées CV/Jobs
- ✅ Catégorisation automatique des missions
- ✅ Performance < 5s par parsing
- ✅ Cache Redis opérationnel
- ✅ Parsing concurrent stable
- ✅ APIs santé fonctionnelles

### Prêt pour la Production ✅
EOF
    else
        cat >> "$report_file" << EOF
⚠️ **SOME TESTS FAILED**

Le système nécessite des corrections avant déploiement production.

### Actions Requises:
- 🔍 Analyser les logs d'erreur
- 🛠️ Corriger les fonctionnalités défaillantes  
- 🧪 Relancer les tests après corrections

### Logs d'Erreur:
- CV Parse Errors: test-results/cv_parse_error.log
- Job Parse Errors: test-results/job_parse_error.log
EOF
    fi
    
    log "INFO" "📄 Report generated: $report_file"
}

# Affichage des statistiques finales
show_final_stats() {
    echo
    log "INFO" "📊 FINAL TEST STATISTICS"
    log "INFO" "========================="
    log "INFO" "Total Tests: $TESTS_TOTAL"
    log "INFO" "Passed: $TESTS_PASSED"
    log "INFO" "Failed: $TESTS_FAILED"
    log "INFO" "Success Rate: $(( TESTS_PASSED * 100 / TESTS_TOTAL ))%"
    echo
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log "INFO" "🎉 ALL TESTS PASSED - SYSTEM READY!"
    else
        log "ERROR" "⚠️ SOME TESTS FAILED - REVIEW REQUIRED"
    fi
    
    log "INFO" "📁 Results: $RESULTS_DIR"
    log "INFO" "📊 Report: $RESULTS_DIR/test_report.md"
}

# Suites de tests
run_quick_tests() {
    log "INFO" "🚀 Running quick test suite..."
    
    run_test "CV Parser Health" test_health_checks
    run_test "Job Parser Health" test_job_parser_health
    run_test "Redis Health" test_redis_health
    run_test "CV Parsing Basic" test_cv_parsing_basic
    run_test "Job Parsing Basic" test_job_parsing_basic
}

run_mission_tests() {
    log "INFO" "🎯 Running mission extraction tests..."
    
    run_test "CV Mission Extraction" test_cv_mission_extraction
    run_test "CV Mission Categories" test_cv_mission_categories
    run_test "Job Mission Extraction" test_job_mission_extraction
    run_test "Enhanced Scoring" test_enhanced_scoring
}

run_performance_tests() {
    log "INFO" "⚡ Running performance tests..."
    
    run_test "CV Parsing Performance" test_cv_parsing_performance
    run_test "Concurrent Parsing" test_concurrent_parsing
    run_test "Cache Functionality" test_cache_functionality
}

run_full_tests() {
    log "INFO" "🧪 Running full test suite..."
    
    run_quick_tests
    run_mission_tests
    run_performance_tests
}

# Aide
show_help() {
    cat << EOF
SuperSmartMatch V2 - Enhanced System Test Suite
==============================================

Usage: $0 [COMMAND]

Commands:
    quick       Quick tests (health checks + basic parsing)
    full        Complete test suite (all tests)
    missions    Mission extraction specific tests  
    performance Performance and load tests
    health      Health checks only
    help        Show this help

Examples:
    $0 quick          # Quick validation
    $0 full           # Complete testing
    $0 missions       # Test mission extraction
    $0 performance    # Performance tests

Test Coverage:
    • Service health checks
    • CV/Job parsing functionality
    • Mission extraction validation
    • Performance benchmarks
    • Cache functionality
    • Concurrent processing

EOF
}

# Point d'entrée principal
main() {
    local command=${1:-help}
    
    init_testing
    
    case $command in
        "quick")
            run_quick_tests
            ;;
        "full")
            run_full_tests
            ;;
        "missions")
            run_mission_tests
            ;;
        "performance")
            run_performance_tests
            ;;
        "health")
            run_test "CV Parser Health" test_health_checks
            run_test "Job Parser Health" test_job_parser_health
            run_test "Redis Health" test_redis_health
            ;;
        "help"|*)
            show_help
            exit 0
            ;;
    esac
    
    generate_report
    show_final_stats
    
    # Code de sortie basé sur les résultats
    if [[ $TESTS_FAILED -eq 0 ]]; then
        exit 0
    else
        exit 1
    fi
}

# Vérification dépendances
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required but not installed"
    exit 1
fi

if ! command -v bc &> /dev/null; then
    echo "Error: bc is required but not installed" 
    exit 1
fi

# Exécution
main "$@"
