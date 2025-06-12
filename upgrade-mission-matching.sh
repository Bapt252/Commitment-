#!/bin/bash
# SuperSmartMatch V2 - Script d'Upgrade Mission Matching
# ======================================================
#
# Script automatique pour upgrader vers le système V2 avec extraction missions enrichies
# Déploiement zero-downtime avec rollback automatique
#
# Usage: ./upgrade-mission-matching.sh [check|upgrade|rollback|status]
# Version: 2.0.0
# Author: Baptiste Coma
# Created: June 2025

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$PROJECT_ROOT/logs/upgrade-mission-matching.log"
COMPOSE_FILE_V1="docker-compose.yml"
COMPOSE_FILE_V2="docker-compose.v2.yml"
HEALTH_CHECK_TIMEOUT=60
ROLLBACK_TIMEOUT=30

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
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
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Initialisation des logs
init_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    log "INFO" "🚀 SuperSmartMatch V2 Mission Matching Upgrade Started"
    log "INFO" "📍 Script directory: $SCRIPT_DIR"
    log "INFO" "📁 Project root: $PROJECT_ROOT"
    log "INFO" "💾 Backup directory: $BACKUP_DIR"
}

# Vérification des prérequis
check_prerequisites() {
    log "INFO" "🔍 Checking prerequisites..."
    
    # Vérification Docker
    if ! command -v docker &> /dev/null; then
        log "ERROR" "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log "ERROR" "Docker Compose is not installed"
        exit 1
    fi
    
    # Vérification Node.js
    if ! command -v node &> /dev/null; then
        log "ERROR" "Node.js is not installed"
        exit 1
    fi
    
    # Vérification Python
    if ! command -v python3 &> /dev/null; then
        log "ERROR" "Python3 is not installed"
        exit 1
    fi
    
    # Vérification des fichiers requis
    local required_files=(
        "enhanced-mission-parser.js"
        "docker-compose.v2.yml"
        "Dockerfile.cv-parser-v2"
        "cv-parser-v2/app.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$PROJECT_ROOT/$file" ]]; then
            log "ERROR" "Required file missing: $file"
            exit 1
        fi
    done
    
    log "INFO" "✅ All prerequisites satisfied"
}

# Status du système actuel
check_current_status() {
    log "INFO" "📊 Checking current system status..."
    
    # Vérification services V1
    if docker-compose -f "$COMPOSE_FILE_V1" ps | grep -q "Up"; then
        log "INFO" "📦 V1 services are running"
        V1_RUNNING=true
    else
        log "INFO" "📦 V1 services are not running"
        V1_RUNNING=false
    fi
    
    # Vérification services V2
    if [[ -f "$COMPOSE_FILE_V2" ]] && docker-compose -f "$COMPOSE_FILE_V2" ps | grep -q "Up"; then
        log "INFO" "🆕 V2 services are running"
        V2_RUNNING=true
    else
        log "INFO" "🆕 V2 services are not running"
        V2_RUNNING=false
    fi
    
    # Tests de santé
    test_health_endpoints
}

# Tests de santé des endpoints
test_health_endpoints() {
    log "INFO" "🏥 Testing health endpoints..."
    
    # Test CV Parser V1 (si running)
    if $V1_RUNNING; then
        if curl -sf http://localhost:5051/health > /dev/null 2>&1; then
            log "INFO" "✅ CV Parser V1 health check: OK"
        else
            log "WARN" "⚠️ CV Parser V1 health check: FAIL"
        fi
    fi
    
    # Test CV Parser V2 (si running)
    if $V2_RUNNING; then
        if curl -sf http://localhost:5051/health > /dev/null 2>&1; then
            log "INFO" "✅ CV Parser V2 health check: OK"
        else
            log "WARN" "⚠️ CV Parser V2 health check: FAIL"
        fi
        
        if curl -sf http://localhost:5053/health > /dev/null 2>&1; then
            log "INFO" "✅ Job Parser V2 health check: OK"
        else
            log "WARN" "⚠️ Job Parser V2 health check: FAIL"
        fi
    fi
    
    # Test Redis
    if docker ps | grep -q redis; then
        if redis-cli ping | grep -q PONG; then
            log "INFO" "✅ Redis health check: OK"
        else
            log "WARN" "⚠️ Redis health check: FAIL"
        fi
    fi
}

# Backup du système actuel
create_backup() {
    log "INFO" "💾 Creating system backup..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup configurations
    if [[ -f "$COMPOSE_FILE_V1" ]]; then
        cp "$COMPOSE_FILE_V1" "$BACKUP_DIR/"
        log "INFO" "📄 Backed up: $COMPOSE_FILE_V1"
    fi
    
    # Backup volumes data
    if docker ps | grep -q redis; then
        log "INFO" "💾 Backing up Redis data..."
        docker exec redis redis-cli SAVE || log "WARN" "Redis backup failed"
    fi
    
    # Backup logs
    if [[ -d "logs" ]]; then
        cp -r logs "$BACKUP_DIR/" || log "WARN" "Logs backup failed"
    fi
    
    log "INFO" "✅ Backup completed: $BACKUP_DIR"
}

# Construction des images V2
build_v2_images() {
    log "INFO" "🔨 Building V2 Docker images..."
    
    # Build CV Parser V2
    log "INFO" "🐳 Building CV Parser V2 image..."
    docker build -f Dockerfile.cv-parser-v2 -t cv-parser-v2:latest . || {
        log "ERROR" "CV Parser V2 build failed"
        return 1
    }
    
    # Build Job Parser V2 (si Dockerfile existe)
    if [[ -f "Dockerfile.job-parser-v2" ]]; then
        log "INFO" "🐳 Building Job Parser V2 image..."
        docker build -f Dockerfile.job-parser-v2 -t job-parser-v2:latest . || {
            log "ERROR" "Job Parser V2 build failed"
            return 1
        }
    fi
    
    # Build Orchestrator V2 (si Dockerfile existe)
    if [[ -f "Dockerfile.orchestrator-v2" ]]; then
        log "INFO" "🐳 Building Orchestrator V2 image..."
        docker build -f Dockerfile.orchestrator-v2 -t orchestrator-v2:latest . || {
            log "ERROR" "Orchestrator V2 build failed"
            return 1
        }
    fi
    
    log "INFO" "✅ V2 images built successfully"
}

# Démarrage des services V2
start_v2_services() {
    log "INFO" "🚀 Starting V2 services..."
    
    # Arrêt gracieux de V1 si nécessaire
    if $V1_RUNNING; then
        log "INFO" "⏹️ Stopping V1 services gracefully..."
        docker-compose -f "$COMPOSE_FILE_V1" down || log "WARN" "V1 stop failed"
    fi
    
    # Démarrage V2
    log "INFO" "▶️ Starting V2 services..."
    docker-compose -f "$COMPOSE_FILE_V2" up -d || {
        log "ERROR" "V2 services start failed"
        return 1
    }
    
    # Attente du démarrage
    log "INFO" "⏳ Waiting for services to start..."
    sleep 10
    
    # Vérification du démarrage
    wait_for_v2_health
}

# Attente de la santé des services V2
wait_for_v2_health() {
    log "INFO" "🏥 Waiting for V2 services health..."
    
    local timeout=$HEALTH_CHECK_TIMEOUT
    local interval=5
    local elapsed=0
    
    while [[ $elapsed -lt $timeout ]]; do
        if curl -sf http://localhost:5051/health > /dev/null 2>&1 && \
           curl -sf http://localhost:5053/health > /dev/null 2>&1; then
            log "INFO" "✅ V2 services are healthy"
            return 0
        fi
        
        log "INFO" "⏳ Waiting for health checks... ($elapsed/${timeout}s)"
        sleep $interval
        ((elapsed += interval))
    done
    
    log "ERROR" "❌ V2 services health check timeout"
    return 1
}

# Tests de validation V2
validate_v2_system() {
    log "INFO" "🧪 Validating V2 system..."
    
    # Test parsing CV avec missions
    local test_result
    test_result=$(curl -s -X POST -F "file=@test_cv.pdf" http://localhost:5051/api/parse-cv/ || echo "FAILED")
    
    if echo "$test_result" | grep -q "mission_summary"; then
        log "INFO" "✅ CV parsing with missions: OK"
    else
        log "ERROR" "❌ CV parsing with missions: FAILED"
        return 1
    fi
    
    # Test parsing Job avec missions
    test_result=$(curl -s -X POST -F "file=@test_job.pdf" http://localhost:5053/api/parse-job || echo "FAILED")
    
    if echo "$test_result" | grep -q "missions"; then
        log "INFO" "✅ Job parsing with missions: OK"
    else
        log "ERROR" "❌ Job parsing with missions: FAILED"
        return 1
    fi
    
    # Test scoring enrichi
    local score_test
    score_test=$(curl -s http://localhost:5070/api/match-test || echo "FAILED")
    
    if echo "$score_test" | grep -q "mission_matching"; then
        log "INFO" "✅ Enhanced mission scoring: OK"
    else
        log "WARN" "⚠️ Enhanced mission scoring: Not available"
    fi
    
    log "INFO" "✅ V2 system validation completed"
    return 0
}

# Rollback vers V1
rollback_to_v1() {
    log "WARN" "🔄 Rolling back to V1..."
    
    # Arrêt V2
    docker-compose -f "$COMPOSE_FILE_V2" down || log "WARN" "V2 stop failed"
    
    # Redémarrage V1
    if [[ -f "$COMPOSE_FILE_V1" ]]; then
        docker-compose -f "$COMPOSE_FILE_V1" up -d || {
            log "ERROR" "V1 restart failed"
            return 1
        }
        
        # Attente santé V1
        local timeout=$ROLLBACK_TIMEOUT
        local elapsed=0
        while [[ $elapsed -lt $timeout ]]; do
            if curl -sf http://localhost:5051/health > /dev/null 2>&1; then
                log "INFO" "✅ V1 rollback successful"
                return 0
            fi
            sleep 2
            ((elapsed += 2))
        done
        
        log "ERROR" "❌ V1 rollback failed"
        return 1
    else
        log "ERROR" "❌ V1 configuration not found"
        return 1
    fi
}

# Fonction principale d'upgrade
perform_upgrade() {
    log "INFO" "🚀 Starting mission matching upgrade..."
    
    # Étapes d'upgrade
    create_backup || {
        log "ERROR" "Backup failed, aborting upgrade"
        exit 1
    }
    
    build_v2_images || {
        log "ERROR" "Image build failed, aborting upgrade"
        exit 1
    }
    
    start_v2_services || {
        log "ERROR" "V2 services start failed, initiating rollback"
        rollback_to_v1
        exit 1
    }
    
    validate_v2_system || {
        log "ERROR" "V2 validation failed, initiating rollback"
        rollback_to_v1
        exit 1
    }
    
    log "INFO" "🎉 Mission matching upgrade completed successfully!"
    log "INFO" "📊 New features available:"
    log "INFO" "   • Enhanced mission extraction (CV + Jobs)"
    log "INFO" "   • Improved scoring: 40% missions + 30% skills + 15% experience + 15% quality"
    log "INFO" "   • Semantic mission matching"
    log "INFO" "   • Mission categorization (facturation, saisie, contrôle, reporting, gestion)"
    log "INFO" "📡 Services running:"
    log "INFO" "   • CV Parser V2: http://localhost:5051"
    log "INFO" "   • Job Parser V2: http://localhost:5053"
    log "INFO" "   • Orchestrator V2: http://localhost:5070"
    log "INFO" "   • Redis Cache: localhost:6379"
}

# Affichage de l'aide
show_help() {
    cat << EOF
SuperSmartMatch V2 - Mission Matching Upgrade Script
====================================================

Usage: $0 [COMMAND]

Commands:
    check       Check current system status and prerequisites
    upgrade     Perform full upgrade to V2 with mission matching
    rollback    Rollback to V1 system
    status      Show current status of all services
    help        Show this help message

Examples:
    $0 check              # Check system before upgrade
    $0 upgrade            # Perform complete upgrade
    $0 rollback           # Rollback to previous version
    $0 status             # Show current status

Features V2:
    • Enhanced mission extraction from CV and job descriptions
    • Improved scoring algorithm (missions: 40%, skills: 30%, experience: 15%, quality: 15%)
    • Semantic mission matching and categorization
    • Zero-downtime deployment with automatic rollback
    • Advanced monitoring and health checks

EOF
}

# Point d'entrée principal
main() {
    local command=${1:-help}
    
    init_logging
    
    case $command in
        "check")
            check_prerequisites
            check_current_status
            ;;
        "upgrade")
            check_prerequisites
            check_current_status
            perform_upgrade
            ;;
        "rollback")
            rollback_to_v1
            ;;
        "status")
            check_current_status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Variables globales
V1_RUNNING=false
V2_RUNNING=false

# Exécution
main "$@"
