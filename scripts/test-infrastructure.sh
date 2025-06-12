#!/bin/bash
set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"; }
log_success() { echo -e "${GREEN}[$(date +'%H:%M:%S')] ✅ $1${NC}"; }
log_error() { echo -e "${RED}[$(date +'%H:%M:%S')] ❌ $1${NC}"; }
log_warning() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] ⚠️ $1${NC}"; }

check_prerequisites() {
    log "🔍 Vérification prérequis..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker non trouvé. Installez Docker Desktop"
        exit 1
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose non trouvé"
        exit 1
    fi
    
    # Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 non trouvé"
        exit 1
    fi
    
    log_success "Prérequis OK"
}

start_infrastructure() {
    log "🚀 Démarrage infrastructure de test..."
    
    # Récupérer dernières modifications
    git pull origin main 2>/dev/null || log_warning "Impossible de faire git pull"
    
    # Nettoyer l'ancien setup
    docker-compose -f docker-compose.test.yml down 2>/dev/null || true
    
    # Démarrer services
    log "Démarrage des services..."
    if docker-compose -f docker-compose.test.yml up -d; then
        log_success "Services démarrés"
    else
        log_error "Erreur démarrage services"
        return 1
    fi
    
    # Attendre que tout soit prêt
    log "Attente initialisation (30 secondes)..."
    sleep 30
    
    log_success "Infrastructure prête"
}

test_services() {
    log "🧪 Tests des services..."
    
    local failed=0
    
    # Test V1 API
    log "Test SuperSmartMatch V1..."
    if curl -sf http://localhost:5062/health > /dev/null; then
        log_success "V1 service OK"
    else
        log_error "V1 service KO"
        failed=1
    fi
    
    # Test V2 API
    log "Test SuperSmartMatch V2..."
    if curl -sf http://localhost:5070/health > /dev/null; then
        log_success "V2 service OK"
    else
        log_error "V2 service KO"
        failed=1
    fi
    
    # Test Nexten API
    log "Test Nexten Matcher..."
    if curl -sf http://localhost:5052/health > /dev/null; then
        log_success "Nexten service OK"
    else
        log_error "Nexten service KO"
        failed=1
    fi
    
    # Test Redis
    log "Test Redis..."
    if docker exec ssm_redis redis-cli ping | grep -q PONG; then
        log_success "Redis OK"
    else
        log_error "Redis KO"
        failed=1
    fi
    
    # Test Prometheus
    log "Test Prometheus..."
    if curl -sf http://localhost:9090/api/v1/targets > /dev/null; then
        log_success "Prometheus OK"
    else
        log_error "Prometheus KO"
        failed=1
    fi
    
    # Test Grafana
    log "Test Grafana..."
    if curl -sf http://localhost:3000/api/health > /dev/null; then
        log_success "Grafana OK"
    else
        log_warning "Grafana en cours de démarrage..."
    fi
    
    return $failed
}

test_apis() {
    log "🎯 Tests API de matching..."
    
    local test_payload='{
        "candidate_profile": {
            "skills": ["python", "javascript"],
            "experience_years": 3
        },
        "job_requirements": {
            "required_skills": ["python"],
            "min_experience": 2
        }
    }'
    
    # Test V1 Match
    log "Test V1 matching..."
    local v1_response=$(curl -s -X POST http://localhost:5062/match \
        -H "Content-Type: application/json" \
        -d "$test_payload")
    
    if echo "$v1_response" | grep -q "match_score"; then
        local v1_score=$(echo "$v1_response" | grep -o '"match_score":[0-9.]*' | cut -d: -f2)
        log_success "V1 Match OK - Score: ${v1_score}%"
    else
        log_error "V1 Match KO"
        return 1
    fi
    
    # Test V2 Match
    log "Test V2 matching..."
    local v2_response=$(curl -s -X POST http://localhost:5070/match \
        -H "Content-Type: application/json" \
        -d "$test_payload")
    
    if echo "$v2_response" | grep -q "match_score"; then
        local v2_score=$(echo "$v2_response" | grep -o '"match_score":[0-9.]*' | cut -d: -f2)
        log_success "V2 Match OK - Score: ${v2_score}%"
        
        # Vérifier amélioration
        if (( $(echo "$v2_score > $v1_score" | bc -l) )); then
            log_success "V2 amélioration validée: ${v2_score}% > ${v1_score}%"
        else
            log_warning "V2 amélioration non visible dans la simulation"
        fi
    else
        log_error "V2 Match KO"
        return 1
    fi
    
    log_success "Tests API OK"
}

run_quick_validation() {
    log "⚡ Validation rapide..."
    
    # Dashboard métrique (test court)
    if python3 scripts/validation_metrics_dashboard.py --help > /dev/null 2>&1; then
        log_success "Dashboard validation disponible"
    else
        log_warning "Dashboard validation non disponible"
    fi
    
    # Benchmark rapide
    if command -v python3 scripts/benchmark_suite.py --quick > /dev/null 2>&1; then
        log "Lancement benchmark rapide..."
        if timeout 60 python3 scripts/benchmark_suite.py --quick --no-visualizations 2>/dev/null; then
            log_success "Benchmark rapide OK"
        else
            log_warning "Benchmark rapide timeout/erreur"
        fi
    fi
    
    log_success "Validation rapide terminée"
}

show_status() {
    log "📊 Status final..."
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🎯 SUPERSMARTMATCH V2 - INFRASTRUCTURE DE TEST PRÊTE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "🔗 SERVICES DISPONIBLES:"
    echo "  • SuperSmartMatch V1: http://localhost:5062/health"
    echo "  • SuperSmartMatch V2: http://localhost:5070/health"  
    echo "  • Nexten Matcher:     http://localhost:5052/health"
    echo "  • Load Balancer:      http://localhost/"
    echo "  • Redis Cache:        localhost:6379"
    echo ""
    echo "📊 MONITORING:"
    echo "  • Prometheus:         http://localhost:9090"
    echo "  • Grafana:            http://localhost:3000 (admin/admin)"
    echo ""
    echo "🧪 TESTS DISPONIBLES:"
    echo "  ./scripts/smoke-tests.sh               # Tests rapides"
    echo "  python3 scripts/benchmark_suite.py --quick          # Benchmark"
    echo "  python3 scripts/validation_metrics_dashboard.py     # Dashboard"
    echo "  python3 scripts/ab_testing_automation.py --quick-test   # A/B tests"
    echo ""
    echo "📋 COMMANDES UTILES:"
    echo "  docker-compose -f docker-compose.test.yml logs -f   # Logs temps réel"
    echo "  docker-compose -f docker-compose.test.yml ps        # Status services"
    echo "  docker-compose -f docker-compose.test.yml down      # Arrêter tout"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

cleanup() {
    log "🧹 Nettoyage..."
    docker-compose -f docker-compose.test.yml down 2>/dev/null || true
    log_success "Nettoyage terminé"
}

main() {
    case "${1:-start}" in
        "check")
            check_prerequisites
            ;;
        "start")
            check_prerequisites
            start_infrastructure
            test_services
            test_apis
            run_quick_validation
            show_status
            ;;
        "test")
            test_services
            test_apis
            ;;
        "status")
            show_status
            ;;
        "stop"|"cleanup")
            cleanup
            ;;
        *)
            echo "Usage: $0 {check|start|test|status|stop}"
            echo ""
            echo "  check   - Vérifier prérequis"
            echo "  start   - Démarrer infrastructure complète + tests"
            echo "  test    - Tester services existants"
            echo "  status  - Afficher status et URLs"
            echo "  stop    - Arrêter et nettoyer"
            ;;
    esac
}

main "$@"
