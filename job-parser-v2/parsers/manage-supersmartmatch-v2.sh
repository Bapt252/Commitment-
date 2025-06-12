#!/bin/bash
"""
🚀 SuperSmartMatch V2 - Script de Déploiement et Gestion Automatisé

Utilitaire complet pour :
- Déploiement initial et mise à jour
- Gestion des services (start/stop/restart)
- Monitoring et health checks
- Backup et rollback
- Validation et tests automatisés
"""

set -euo pipefail

# Configuration
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="${SCRIPT_DIR}"
readonly LOG_FILE="${PROJECT_ROOT}/logs/deployment.log"
readonly COMPOSE_FILE="docker-compose.supersmartmatch-v2.yml"
readonly VERSION="2.0.0"

# Couleurs pour output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Emojis pour interface
readonly ROCKET="🚀"
readonly CHECK="✅"
readonly CROSS="❌"
readonly WARNING="⚠️"
readonly INFO="ℹ️"
readonly GEAR="⚙️"
readonly MONITOR="📊"

# Configuration par défaut
ENVIRONMENT="production"
DRY_RUN=false
VERBOSE=false
FORCE=false
BACKUP_ENABLED=true

# ===== FONCTIONS UTILITAIRES =====

log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")  echo -e "${BLUE}${INFO}${NC} ${timestamp} - $message" ;;
        "SUCCESS") echo -e "${GREEN}${CHECK}${NC} ${timestamp} - $message" ;;
        "WARNING") echo -e "${YELLOW}${WARNING}${NC} ${timestamp} - $message" ;;
        "ERROR") echo -e "${RED}${CROSS}${NC} ${timestamp} - $message" ;;
        "DEBUG") [[ "$VERBOSE" == "true" ]] && echo -e "${PURPLE}${GEAR}${NC} ${timestamp} - $message" ;;
    esac
    
    # Log vers fichier
    echo "[$level] $timestamp - $message" >> "$LOG_FILE"
}

show_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'
 ____                       ____                       _   __  __       _       _     __     ____  
/ ___| _   _ _ __   ___ _ __/ ___| _ __ ___   __ _ _ __| |_|  \/  | __ _| |_ ___| |__   \ \   / /  \
\___ \| | | | '_ \ / _ \ '__\___ \| '_ ` _ \ / _` | '__| __| |\/| |/ _` | __/ __| '_ \   \ \ / /|  |
 ___) | |_| | |_) |  __/ |   ___) | | | | | | (_| | |  | |_| |  | | (_| | || (__| | | |   \ V / |  |
|____/ \__,_| .__/ \___|_|  |____/|_| |_| |_|\__,_|_|   \__|_|  |_|\__,_|\__\___|_| |_|    \_/  |__|
            |_|                                                                                      
EOF
    echo -e "${NC}"
    echo -e "${GREEN}${ROCKET} SuperSmartMatch V2 - Service Unifié Intelligent${NC}"
    echo -e "${BLUE}Version: $VERSION | Environment: $ENVIRONMENT${NC}"
    echo -e "${PURPLE}===============================================================${NC}"
    echo
}

check_prerequisites() {
    log "INFO" "Vérification des prérequis..."
    
    local missing_tools=()
    
    # Vérification des outils requis
    for tool in docker docker-compose curl jq python3; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        log "ERROR" "Outils manquants: ${missing_tools[*]}"
        log "INFO" "Installation requise:"
        for tool in "${missing_tools[@]}"; do
            case "$tool" in
                "docker") echo "  - Docker: https://docs.docker.com/get-docker/" ;;
                "docker-compose") echo "  - Docker Compose: https://docs.docker.com/compose/install/" ;;
                "curl") echo "  - curl: apt-get install curl (Ubuntu/Debian)" ;;
                "jq") echo "  - jq: apt-get install jq (Ubuntu/Debian)" ;;
                "python3") echo "  - Python 3.11+: https://www.python.org/downloads/" ;;
            esac
        done
        exit 1
    fi
    
    # Vérification des ports
    local required_ports=(5070 5052 5062 6379 9090 3000)
    local busy_ports=()
    
    for port in "${required_ports[@]}"; do
        if lsof -i ":$port" &> /dev/null; then
            busy_ports+=("$port")
        fi
    done
    
    if [[ ${#busy_ports[@]} -gt 0 ]] && [[ "$FORCE" != "true" ]]; then
        log "WARNING" "Ports occupés: ${busy_ports[*]}"
        log "INFO" "Utilisez --force pour continuer ou libérez les ports"
        read -p "Continuer quand même? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log "SUCCESS" "Prérequis validés"
}

create_directories() {
    log "INFO" "Création des répertoires nécessaires..."
    
    local directories=(
        "logs"
        "data/redis"
        "data/prometheus" 
        "data/grafana"
        "config/monitoring"
        "backup"
        "ssl"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$PROJECT_ROOT/$dir"
        log "DEBUG" "Créé: $dir"
    done
    
    # Permissions pour données
    chmod 755 "$PROJECT_ROOT/data"
    chmod 777 "$PROJECT_ROOT/data/grafana" # Grafana needs write access
    
    log "SUCCESS" "Répertoires créés"
}

setup_monitoring_config() {
    log "INFO" "Configuration du monitoring..."
    
    # Configuration Prometheus
    cat > "$PROJECT_ROOT/config/monitoring/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'supersmartmatch-v2'
    static_configs:
      - targets: ['supersmartmatch-v2:5070']
    metrics_path: '/metrics'
    scrape_interval: 10s
    
  - job_name: 'nexten-matcher'
    static_configs:
      - targets: ['nexten-matcher:5052']
    metrics_path: '/metrics'
    scrape_interval: 15s
    
  - job_name: 'supersmartmatch-v1'
    static_configs:
      - targets: ['supersmartmatch-v1:5062']
    metrics_path: '/metrics'
    scrape_interval: 15s
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-cache:6379']
    metrics_path: '/metrics'
    scrape_interval: 30s
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

    # Configuration Grafana datasources
    mkdir -p "$PROJECT_ROOT/config/monitoring/grafana/datasources"
    cat > "$PROJECT_ROOT/config/monitoring/grafana/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    log "SUCCESS" "Monitoring configuré"
}

validate_environment() {
    log "INFO" "Validation de l'environnement..."
    
    # Vérification fichier .env
    if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
        log "WARNING" "Fichier .env manquant, création depuis .env.example"
        if [[ -f "$PROJECT_ROOT/.env.example" ]]; then
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        else
            log "ERROR" "Fichier .env.example manquant"
            exit 1
        fi
    fi
    
    # Vérification variables critiques
    local required_vars=(
        "NEXTEN_URL"
        "SUPERSMARTMATCH_V1_URL" 
        "REDIS_URL"
    )
    
    source "$PROJECT_ROOT/.env"
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log "ERROR" "Variable d'environnement manquante: $var"
            exit 1
        fi
    done
    
    log "SUCCESS" "Environnement validé"
}

backup_current_state() {
    if [[ "$BACKUP_ENABLED" != "true" ]]; then
        return 0
    fi
    
    log "INFO" "Sauvegarde de l'état actuel..."
    
    local backup_dir="$PROJECT_ROOT/backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup configuration
    cp -r "$PROJECT_ROOT/config" "$backup_dir/" 2>/dev/null || true
    cp "$PROJECT_ROOT/.env" "$backup_dir/" 2>/dev/null || true
    
    # Backup données Redis si possible
    if docker ps | grep -q redis-cache; then
        docker exec redis-cache redis-cli BGSAVE
        docker cp redis-cache:/data/dump.rdb "$backup_dir/redis-dump.rdb" 2>/dev/null || true
    fi
    
    # Backup Grafana dashboards
    if docker ps | grep -q grafana; then
        docker cp grafana-dashboard:/var/lib/grafana "$backup_dir/grafana-data" 2>/dev/null || true
    fi
    
    log "SUCCESS" "Backup créé: $backup_dir"
    echo "$backup_dir" > "$PROJECT_ROOT/.last_backup"
}

deploy_services() {
    log "INFO" "Déploiement des services SuperSmartMatch V2..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "INFO" "Mode DRY RUN - Simulation du déploiement"
        docker-compose -f "$COMPOSE_FILE" config
        return 0
    fi
    
    # Pull des images
    log "INFO" "Pull des images Docker..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build si nécessaire
    log "INFO" "Build des services..."
    docker-compose -f "$COMPOSE_FILE" build
    
    # Démarrage des services
    log "INFO" "Démarrage des services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log "SUCCESS" "Services déployés"
}

wait_for_services() {
    log "INFO" "Attente de la disponibilité des services..."
    
    local services=(
        "http://localhost:6379|Redis Cache"
        "http://localhost:5070/health|SuperSmartMatch V2"
        "http://localhost:5052/health|Nexten Matcher"
        "http://localhost:5062/health|SuperSmartMatch V1"
        "http://localhost:9090/-/ready|Prometheus"
        "http://localhost:3000/api/health|Grafana"
    )
    
    local max_attempts=30
    local attempt=1
    
    for service_info in "${services[@]}"; do
        IFS='|' read -r url name <<< "$service_info"
        
        log "INFO" "Vérification: $name"
        
        while [[ $attempt -le $max_attempts ]]; do
            if curl -sf "$url" &>/dev/null; then
                log "SUCCESS" "$name disponible"
                break
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                log "WARNING" "$name non disponible après ${max_attempts}s"
                break
            fi
            
            sleep 1
            ((attempt++))
        done
        
        attempt=1
    done
}

run_validation_tests() {
    log "INFO" "Exécution des tests de validation..."
    
    if [[ -f "$PROJECT_ROOT/validate-supersmartmatch-v2.py" ]]; then
        log "INFO" "Test d'intégration end-to-end..."
        if python3 "$PROJECT_ROOT/validate-supersmartmatch-v2.py" http://localhost:5070; then
            log "SUCCESS" "Tests de validation réussis"
        else
            log "WARNING" "Certains tests ont échoué, vérifiez les logs"
        fi
    else
        log "WARNING" "Script de validation non trouvé"
    fi
    
    # Test API simple
    log "INFO" "Test API de base..."
    local test_data='{"candidate":{"name":"Test"},"offers":[{"id":"1","title":"Test Job"}]}'
    
    if curl -sf -X POST "http://localhost:5070/api/v2/match" \
        -H "Content-Type: application/json" \
        -d "$test_data" | jq '.success' | grep -q true; then
        log "SUCCESS" "API V2 fonctionnelle"
    else
        log "ERROR" "API V2 non fonctionnelle"
    fi
}

show_status() {
    echo
    log "INFO" "État des services SuperSmartMatch V2:"
    echo
    
    # Status Docker containers
    echo -e "${BLUE}${MONITOR} Services Docker:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps
    echo
    
    # Status endpoints
    echo -e "${BLUE}${MONITOR} Endpoints disponibles:${NC}"
    local endpoints=(
        "http://localhost:5070|SuperSmartMatch V2 API"
        "http://localhost:5070/health|Health Check"
        "http://localhost:5070/api/docs|Documentation API"
        "http://localhost:5070/metrics|Métriques"
        "http://localhost:9090|Prometheus"
        "http://localhost:3000|Grafana (admin/supersmartmatch)"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS='|' read -r url description <<< "$endpoint_info"
        if curl -sf "$url" &>/dev/null; then
            echo -e "  ${GREEN}${CHECK}${NC} $description: $url"
        else
            echo -e "  ${RED}${CROSS}${NC} $description: $url"
        fi
    done
    echo
}

stop_services() {
    log "INFO" "Arrêt des services..."
    docker-compose -f "$COMPOSE_FILE" down
    log "SUCCESS" "Services arrêtés"
}

restart_services() {
    log "INFO" "Redémarrage des services..."
    docker-compose -f "$COMPOSE_FILE" restart
    wait_for_services
    log "SUCCESS" "Services redémarrés"
}

cleanup() {
    log "INFO" "Nettoyage des ressources..."
    
    # Arrêt et suppression des containers
    docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans
    
    # Nettoyage des images orphelines
    docker system prune -f
    
    log "SUCCESS" "Nettoyage terminé"
}

rollback() {
    if [[ ! -f "$PROJECT_ROOT/.last_backup" ]]; then
        log "ERROR" "Aucun backup disponible pour rollback"
        exit 1
    fi
    
    local backup_dir=$(cat "$PROJECT_ROOT/.last_backup")
    
    if [[ ! -d "$backup_dir" ]]; then
        log "ERROR" "Répertoire de backup introuvable: $backup_dir"
        exit 1
    fi
    
    log "INFO" "Rollback vers: $backup_dir"
    
    # Arrêt des services
    stop_services
    
    # Restauration configuration
    cp -r "$backup_dir/config/"* "$PROJECT_ROOT/config/" 2>/dev/null || true
    cp "$backup_dir/.env" "$PROJECT_ROOT/.env" 2>/dev/null || true
    
    # Redémarrage
    deploy_services
    wait_for_services
    
    log "SUCCESS" "Rollback terminé"
}

update() {
    log "INFO" "Mise à jour SuperSmartMatch V2..."
    
    # Backup avant mise à jour
    backup_current_state
    
    # Pull nouvelles images
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Rolling update
    docker-compose -f "$COMPOSE_FILE" up -d --no-deps supersmartmatch-v2
    
    # Vérification santé
    sleep 10
    if curl -sf "http://localhost:5070/health" &>/dev/null; then
        log "SUCCESS" "Mise à jour réussie"
        run_validation_tests
    else
        log "ERROR" "Mise à jour échouée, rollback..."
        rollback
    fi
}

show_logs() {
    local service="${1:-supersmartmatch-v2}"
    log "INFO" "Logs du service: $service"
    docker-compose -f "$COMPOSE_FILE" logs -f "$service"
}

show_help() {
    cat << EOF
${ROCKET} SuperSmartMatch V2 - Script de Gestion

USAGE:
    $SCRIPT_NAME [OPTIONS] COMMAND

COMMANDS:
    deploy      Déploiement complet initial
    start       Démarrage des services  
    stop        Arrêt des services
    restart     Redémarrage des services
    status      Affichage du statut
    update      Mise à jour des services
    rollback    Retour à la version précédente
    test        Tests de validation
    logs        Affichage des logs [service]
    cleanup     Nettoyage complet
    help        Affichage de cette aide

OPTIONS:
    --env ENV           Environnement (production/staging/dev)
    --dry-run          Mode simulation sans exécution
    --verbose          Mode verbeux
    --force            Force l'exécution
    --no-backup        Désactive les backups automatiques

EXAMPLES:
    $SCRIPT_NAME deploy                    # Déploiement complet
    $SCRIPT_NAME start --env staging       # Démarrage en staging
    $SCRIPT_NAME logs supersmartmatch-v2   # Logs du service principal
    $SCRIPT_NAME update --verbose          # Mise à jour avec logs détaillés

MONITORING:
    Grafana:     http://localhost:3000 (admin/supersmartmatch)
    Prometheus:  http://localhost:9090
    API Docs:    http://localhost:5070/api/docs
    Health:      http://localhost:5070/health

EOF
}

# ===== PARSING DES ARGUMENTS =====

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            --no-backup)
                BACKUP_ENABLED=false
                shift
                ;;
            deploy|start|stop|restart|status|update|rollback|test|logs|cleanup|help)
                COMMAND="$1"
                shift
                if [[ "$COMMAND" == "logs" && $# -gt 0 ]]; then
                    SERVICE_NAME="$1"
                    shift
                fi
                ;;
            *)
                log "ERROR" "Option inconnue: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# ===== MAIN =====

main() {
    # Création répertoire logs
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Bannière
    show_banner
    
    # Vérification arguments
    if [[ -z "${COMMAND:-}" ]]; then
        show_help
        exit 1
    fi
    
    # Exécution commande
    case "$COMMAND" in
        "deploy")
            check_prerequisites
            create_directories
            setup_monitoring_config
            validate_environment
            backup_current_state
            deploy_services
            wait_for_services
            run_validation_tests
            show_status
            ;;
        "start")
            validate_environment
            deploy_services
            wait_for_services
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            show_status
            ;;
        "status")
            show_status
            ;;
        "update")
            update
            ;;
        "rollback")
            rollback
            ;;
        "test")
            run_validation_tests
            ;;
        "logs")
            show_logs "${SERVICE_NAME:-supersmartmatch-v2}"
            ;;
        "cleanup")
            cleanup
            ;;
        "help")
            show_help
            ;;
        *)
            log "ERROR" "Commande inconnue: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Parse arguments et exécution
COMMAND=""
SERVICE_NAME=""
parse_arguments "$@"
main

log "SUCCESS" "Opération '$COMMAND' terminée avec succès!"
