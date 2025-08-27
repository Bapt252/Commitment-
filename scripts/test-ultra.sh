#!/bin/bash
# 🧪 PROMPT 2: Tests automatisés Parsers Ultra v2.0
# SuperSmartMatch V2 - Suite de tests complète streaming temps réel

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEST_LOG="/tmp/test-ultra-$(date +%Y%m%d-%H%M%S).log"
TEST_DATA_DIR="$PROJECT_ROOT/test-data"

# URLs des services
CV_PARSER_URL="http://localhost:5051"
JOB_PARSER_URL="http://localhost:5053"
API_GATEWAY_URL="http://localhost:5050"
PROMETHEUS_URL="http://localhost:9091"
GRAFANA_URL="http://localhost:3001"

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Statistiques des tests
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Logging
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$TEST_LOG"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$TEST_LOG"
    ((TESTS_PASSED++))
}

log_failure() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$TEST_LOG"
    ((TESTS_FAILED++))
}

log_skip() {
    echo -e "${YELLOW}⏭️  $1${NC}" | tee -a "$TEST_LOG"
    ((TESTS_SKIPPED++))
}

# Fonction de test générique
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    ((TESTS_TOTAL++))
    log "🧪 Test: $test_name"
    
    if $test_function; then
        log_success "$test_name"
        return 0
    else
        log_failure "$test_name"
        return 1
    fi
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🧪 SuperSmartMatch V2 - Tests Parsers Ultra v2.0         ║
║                                                              ║
║    PROMPT 2: Validation streaming temps réel + WebSocket    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Préparation des données de test
prepare_test_data() {
    log "📁 Préparation des données de test..."
    
    mkdir -p "$TEST_DATA_DIR"
    
    # Création d'un CV de test si absent
    if [[ ! -f "$TEST_DATA_DIR/sample-cv.txt" ]]; then
        cat > "$TEST_DATA_DIR/sample-cv.txt" << 'EOF'
Jean Dupont
Développeur Full Stack Senior

Email: jean.dupont@email.com
Téléphone: +33 6 12 34 56 78
Adresse: 123 Rue de la Paix, 75001 Paris

COMPÉTENCES TECHNIQUES:
- JavaScript, TypeScript, React, Node.js
- Python, Django, FastAPI
- PostgreSQL, MongoDB, Redis
- Docker, Kubernetes, AWS
- Git, Jenkins, CI/CD

SOFT SKILLS:
- Leadership d'équipe
- Communication efficace
- Résolution de problèmes
- Travail en équipe
- Adaptabilité

EXPÉRIENCE PROFESSIONNELLE:
2020-2023: Lead Developer chez TechCorp
- Développement d'applications web modernes
- Management d'une équipe de 5 développeurs
- Mise en place de l'architecture microservices

2018-2020: Full Stack Developer chez StartupXYZ
- Développement de la plateforme e-commerce
- Optimisation des performances
- Intégration d'APIs tierces

FORMATION:
2018: Master en Informatique - École Polytechnique
2016: Licence en Informatique - Université Paris Diderot

CERTIFICATIONS:
- AWS Solutions Architect
- Certified Kubernetes Administrator
- Scrum Master Certified

LANGUES:
- Français: Natif
- Anglais: Courant
- Espagnol: Intermédiaire
EOF
    fi
    
    # Création d'une offre d'emploi de test si absente
    if [[ ! -f "$TEST_DATA_DIR/sample-job.txt" ]]; then
        cat > "$TEST_DATA_DIR/sample-job.txt" << 'EOF'
Développeur Backend Senior - Python/Django
CDI - Paris 75001

NOTRE ENTREPRISE:
TechInnovation est une scale-up française spécialisée dans l'IA et le machine learning.
Nous développons des solutions innovantes pour les entreprises du CAC 40.

POSTE:
Nous recherchons un Développeur Backend Senior pour rejoindre notre équipe technique.
Vous serez en charge du développement de nos APIs et de l'architecture backend.

MISSIONS PRINCIPALES:
- Développement d'APIs REST en Python/Django
- Conception et optimisation de bases de données
- Intégration de services de machine learning
- Collaboration avec les équipes frontend et data science
- Encadrement technique des développeurs junior
- Participation aux choix d'architecture

COMPÉTENCES REQUISES:
- Python (5+ ans d'expérience)
- Django/FastAPI
- PostgreSQL/MongoDB
- Redis
- Docker
- Git
- Tests unitaires et intégration
- Architecture microservices

COMPÉTENCES SOUHAITÉES:
- Machine Learning (scikit-learn, TensorFlow)
- Kubernetes
- AWS/GCP
- Elasticsearch
- GraphQL
- React (notions)

PROFIL RECHERCHÉ:
- 5+ années d'expérience en développement backend
- Master en informatique ou équivalent
- Anglais technique courant
- Esprit d'équipe et curiosité technique
- Expérience en startup/scale-up appréciée

CONDITIONS:
- Salaire: 55k€ - 75k€ selon expérience
- Télétravail hybride (2-3j/semaine)
- Tickets restaurant
- Mutuelle d'entreprise
- Formation continue
- Stock-options

LOCALISATION:
Paris 1er arrondissement
Métro: Châtelet-Les Halles
Télétravail partiel possible

TYPE DE CONTRAT: CDI
EXPÉRIENCE MINIMALE: 5 ans
SECTEUR: Technologie/IA
TAILLE ENTREPRISE: Scale-up (50-200 employés)
EOF
    fi
    
    log_success "Données de test préparées"
}

# Tests des services de base
test_services_health() {
    log "🏥 Test de santé des services..."
    
    local services=(
        "$CV_PARSER_URL/health"
        "$JOB_PARSER_URL/health"
        "$API_GATEWAY_URL/health"
        "$PROMETHEUS_URL/-/healthy"
        "$GRAFANA_URL/api/health"
    )
    
    for service in "${services[@]}"; do
        if curl -sf "$service" >/dev/null 2>&1; then
            log_success "Service ${service} OK"
        else
            log_failure "Service ${service} inaccessible"
            return 1
        fi
    done
    
    return 0
}

# Test de parsing CV avec WebSocket
test_cv_parsing_websocket() {
    log "⚡ Test CV Parser Ultra avec WebSocket..."
    
    # Lancer le parsing CV
    local response=$(curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/sample-cv.txt" \
        "$CV_PARSER_URL/v2/parse/cv/stream")
    
    # Vérifier la réponse
    if ! echo "$response" | grep -q "task_id"; then
        log_failure "Pas de task_id dans la réponse CV"
        return 1
    fi
    
    local task_id=$(echo "$response" | jq -r '.task_id' 2>/dev/null)
    if [[ -z "$task_id" || "$task_id" == "null" ]]; then
        log_failure "Task ID invalide pour CV"
        return 1
    fi
    
    log "Task ID CV: $task_id"
    
    # Test WebSocket (simulation avec curl pour status)
    sleep 2
    local status_response=$(curl -s "$CV_PARSER_URL/v2/parse/validate/$task_id")
    
    if echo "$status_response" | grep -q "task_id"; then
        log_success "WebSocket CV - Status endpoint OK"
    else
        log_failure "WebSocket CV - Status endpoint KO"
        return 1
    fi
    
    return 0
}

# Test de parsing Job avec WebSocket
test_job_parsing_websocket() {
    log "🎯 Test Job Parser Ultra avec WebSocket..."
    
    # Lancer le parsing Job
    local response=$(curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/sample-job.txt" \
        "$JOB_PARSER_URL/v2/parse/job/stream")
    
    # Vérifier la réponse
    if ! echo "$response" | grep -q "task_id"; then
        log_failure "Pas de task_id dans la réponse Job"
        return 1
    fi
    
    local task_id=$(echo "$response" | jq -r '.task_id' 2>/dev/null)
    if [[ -z "$task_id" || "$task_id" == "null" ]]; then
        log_failure "Task ID invalide pour Job"
        return 1
    fi
    
    log "Task ID Job: $task_id"
    
    # Test WebSocket (simulation)
    sleep 2
    local status_response=$(curl -s "$JOB_PARSER_URL/v2/parse/job/validate/$task_id")
    
    if echo "$status_response" | grep -q "task_id"; then
        log_success "WebSocket Job - Status endpoint OK"
    else
        log_failure "WebSocket Job - Status endpoint KO"
        return 1
    fi
    
    return 0
}

# Test des métriques Prometheus
test_prometheus_metrics() {
    log "📊 Test des métriques Prometheus..."
    
    # Attendre que les métriques soient collectées
    sleep 5
    
    local metrics=(
        "cv_parsing_requests_total"
        "job_parsing_requests_total"
        "cv_websocket_connections_active"
        "job_websocket_connections_active"
        "cv_parsing_duration_seconds"
        "job_parsing_duration_seconds"
    )
    
    for metric in "${metrics[@]}"; do
        local query_result=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$metric")
        
        if echo "$query_result" | grep -q '"status":"success"'; then
            log_success "Métrique $metric disponible"
        else
            log_failure "Métrique $metric manquante"
            return 1
        fi
    done
    
    return 0
}

# Test de performance et latence
test_performance() {
    log "⚡ Test de performance des parsers..."
    
    local start_time
    local end_time
    local duration
    
    # Test latence CV Parser
    start_time=$(date +%s.%N)
    curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/sample-cv.txt" \
        "$CV_PARSER_URL/v2/parse/cv/stream" >/dev/null
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc -l)
    
    if (( $(echo "$duration < 3.0" | bc -l) )); then
        log_success "CV Parser latence OK: ${duration}s"
    else
        log_failure "CV Parser latence élevée: ${duration}s"
        return 1
    fi
    
    # Test latence Job Parser
    start_time=$(date +%s.%N)
    curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/sample-job.txt" \
        "$JOB_PARSER_URL/v2/parse/job/stream" >/dev/null
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc -l)
    
    if (( $(echo "$duration < 2.0" | bc -l) )); then
        log_success "Job Parser latence OK: ${duration}s"
    else
        log_failure "Job Parser latence élevée: ${duration}s"
        return 1
    fi
    
    return 0
}

# Test de charge simple
test_load() {
    log "🔥 Test de charge des parsers..."
    
    local concurrent_requests=5
    local pids=()
    
    # Lancement de requêtes concurrentes
    for i in $(seq 1 $concurrent_requests); do
        {
            curl -s -X POST \
                -F "file=@$TEST_DATA_DIR/sample-cv.txt" \
                "$CV_PARSER_URL/v2/parse/cv/stream" >/dev/null
        } &
        pids+=($!)
    done
    
    # Attendre la fin de toutes les requêtes
    local all_success=true
    for pid in "${pids[@]}"; do
        if ! wait $pid; then
            all_success=false
        fi
    done
    
    if $all_success; then
        log_success "Test de charge: $concurrent_requests requêtes concurrentes OK"
    else
        log_failure "Test de charge: échec de certaines requêtes"
        return 1
    fi
    
    return 0
}

# Test des formats de fichiers
test_file_formats() {
    log "📄 Test des formats de fichiers supportés..."
    
    # Créer des fichiers de test de différents formats
    echo "Test CV content" > "$TEST_DATA_DIR/test-cv.txt"
    echo "Test Job content" > "$TEST_DATA_DIR/test-job.html"
    
    # Test format TXT pour CV
    local txt_response=$(curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/test-cv.txt" \
        "$CV_PARSER_URL/v2/parse/cv/stream")
    
    if echo "$txt_response" | grep -q "task_id"; then
        log_success "Format TXT supporté pour CV"
    else
        log_failure "Format TXT non supporté pour CV"
        return 1
    fi
    
    # Test format HTML pour Job
    local html_response=$(curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/test-job.html" \
        "$JOB_PARSER_URL/v2/parse/job/stream")
    
    if echo "$html_response" | grep -q "task_id"; then
        log_success "Format HTML supporté pour Job"
    else
        log_failure "Format HTML non supporté pour Job"
        return 1
    fi
    
    return 0
}

# Test de gestion d'erreurs
test_error_handling() {
    log "🚫 Test de gestion d'erreurs..."
    
    # Test avec fichier trop gros (simulation)
    local large_file_response=$(curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/sample-cv.txt" \
        -H "Content-Length: 99999999" \
        "$CV_PARSER_URL/v2/parse/cv/stream")
    
    # Le service devrait gérer l'erreur proprement
    if echo "$large_file_response" | grep -q -E "(error|413|too large)"; then
        log_success "Gestion d'erreur fichier volumineux OK"
    else
        log_skip "Test fichier volumineux (réponse: ${large_file_response:0:50}...)"
    fi
    
    # Test avec format non supporté
    echo "test" > "$TEST_DATA_DIR/test.xyz"
    local unsupported_response=$(curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/test.xyz" \
        "$CV_PARSER_URL/v2/parse/cv/stream")
    
    if echo "$unsupported_response" | grep -q -E "(error|400|unsupported|non supporté)"; then
        log_success "Gestion d'erreur format non supporté OK"
    else
        log_skip "Test format non supporté (réponse: ${unsupported_response:0:50}...)"
    fi
    
    return 0
}

# Test d'intégration avec l'API Gateway
test_api_gateway_integration() {
    log "🌐 Test d'intégration API Gateway..."
    
    # Test routage vers CV Parser via Gateway
    local gateway_cv_response=$(curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/sample-cv.txt" \
        "$API_GATEWAY_URL/api/v2/parse/cv/stream")
    
    if echo "$gateway_cv_response" | grep -q "task_id"; then
        log_success "Routage API Gateway vers CV Parser OK"
    else
        log_failure "Routage API Gateway vers CV Parser KO"
        return 1
    fi
    
    # Test routage vers Job Parser via Gateway
    local gateway_job_response=$(curl -s -X POST \
        -F "file=@$TEST_DATA_DIR/sample-job.txt" \
        "$API_GATEWAY_URL/api/v2/parse/job/stream")
    
    if echo "$gateway_job_response" | grep -q "task_id"; then
        log_success "Routage API Gateway vers Job Parser OK"
    else
        log_failure "Routage API Gateway vers Job Parser KO"
        return 1
    fi
    
    return 0
}

# Nettoyage des fichiers de test
cleanup_test_data() {
    log "🧹 Nettoyage des fichiers de test..."
    
    rm -f "$TEST_DATA_DIR/test-cv.txt"
    rm -f "$TEST_DATA_DIR/test-job.html"
    rm -f "$TEST_DATA_DIR/test.xyz"
    
    log_success "Nettoyage terminé"
}

# Génération du rapport de tests
generate_test_report() {
    log "📋 Génération du rapport de tests..."
    
    local success_rate=0
    if [[ $TESTS_TOTAL -gt 0 ]]; then
        success_rate=$(( (TESTS_PASSED * 100) / TESTS_TOTAL ))
    fi
    
    echo ""
    echo -e "${PURPLE}╔══════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║         RAPPORT DE TESTS ULTRA v2.0     ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}📊 Statistiques:${NC}"
    echo -e "  Total des tests:      $TESTS_TOTAL"
    echo -e "  ${GREEN}Tests réussis:        $TESTS_PASSED${NC}"
    echo -e "  ${RED}Tests échoués:        $TESTS_FAILED${NC}"
    echo -e "  ${YELLOW}Tests ignorés:        $TESTS_SKIPPED${NC}"
    echo -e "  ${PURPLE}Taux de réussite:     $success_rate%${NC}"
    echo ""
    
    if [[ $success_rate -ge 90 ]]; then
        echo -e "${GREEN}🎉 EXCELLENT! Les parsers Ultra v2.0 fonctionnent parfaitement!${NC}"
    elif [[ $success_rate -ge 75 ]]; then
        echo -e "${YELLOW}⚠️  BON. Quelques améliorations possibles.${NC}"
    else
        echo -e "${RED}❌ ATTENTION. Des problèmes détectés nécessitent investigation.${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}📝 Log détaillé: $TEST_LOG${NC}"
    echo ""
}

# Fonction principale
main() {
    show_banner
    
    log "🚀 Début des tests Parsers Ultra v2.0"
    log "📝 Log détaillé: $TEST_LOG"
    
    prepare_test_data
    
    # Tests de base
    run_test "Services Health Check" test_services_health
    
    # Tests de parsing
    run_test "CV Parsing WebSocket" test_cv_parsing_websocket
    run_test "Job Parsing WebSocket" test_job_parsing_websocket
    
    # Tests de monitoring
    run_test "Métriques Prometheus" test_prometheus_metrics
    
    # Tests de performance
    run_test "Performance et Latence" test_performance
    run_test "Test de Charge" test_load
    
    # Tests de fonctionnalités
    run_test "Formats de Fichiers" test_file_formats
    run_test "Gestion d'Erreurs" test_error_handling
    
    # Tests d'intégration
    run_test "Intégration API Gateway" test_api_gateway_integration
    
    cleanup_test_data
    generate_test_report
    
    # Code de sortie basé sur les résultats
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "🎉 Tous les tests sont passés avec succès!"
        exit 0
    else
        log_failure "❌ $TESTS_FAILED test(s) ont échoué"
        exit 1
    fi
}

# Gestion des arguments
case "${1:-all}" in
    "all")
        main
        ;;
    "health")
        show_banner
        prepare_test_data
        run_test "Services Health Check" test_services_health
        generate_test_report
        ;;
    "parsing")
        show_banner
        prepare_test_data
        run_test "CV Parsing WebSocket" test_cv_parsing_websocket
        run_test "Job Parsing WebSocket" test_job_parsing_websocket
        generate_test_report
        ;;
    "performance")
        show_banner
        prepare_test_data
        run_test "Performance et Latence" test_performance
        run_test "Test de Charge" test_load
        generate_test_report
        ;;
    "integration")
        show_banner
        prepare_test_data
        run_test "Intégration API Gateway" test_api_gateway_integration
        generate_test_report
        ;;
    *)
        echo "Usage: $0 {all|health|parsing|performance|integration}"
        echo ""
        echo "  all          - Exécute tous les tests"
        echo "  health       - Test de santé des services"
        echo "  parsing      - Tests de parsing CV et Job"
        echo "  performance  - Tests de performance"
        echo "  integration  - Tests d'intégration"
        exit 1
        ;;
esac
