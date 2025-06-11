#!/bin/bash
# 🚀 PROMPT 2: Script de déploiement Parsers Ultra v2.0
# SuperSmartMatch V2 - Déploiement production avec streaming temps réel

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/deploy-ultra-$(date +%Y%m%d-%H%M%S).log"
BACKUP_DIR="/tmp/backup-$(date +%Y%m%d-%H%M%S)"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}" | tee -a "$LOG_FILE"
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🚀 SuperSmartMatch V2 - Parsers Ultra v2.0 Deploy       ║
║                                                              ║
║    PROMPT 2: Streaming temps réel + IA + WebSocket          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Vérification des prérequis
check_prerequisites() {
    log "🔍 Vérification des prérequis..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérification des variables d'environnement
    local required_vars=(
        "OPENAI_API_KEY"
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "JWT_SECRET"
        "GRAFANA_ADMIN_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Variable d'environnement $var manquante"
            exit 1
        fi
    done
    
    log_success "Prérequis validés"
}

# Sauvegarde de l'état actuel
backup_current_state() {
    log "💾 Sauvegarde de l'état actuel..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Sauvegarde des volumes Docker
    if docker volume ls | grep -q "supersmartmatch"; then
        log "Sauvegarde des volumes Docker..."
        docker run --rm -v postgres_data:/source -v "$BACKUP_DIR":/backup alpine tar czf /backup/postgres_data.tar.gz -C /source .
        docker run --rm -v redis_data:/source -v "$BACKUP_DIR":/backup alpine tar czf /backup/redis_data.tar.gz -C /source .
        docker run --rm -v grafana_data:/source -v "$BACKUP_DIR":/backup alpine tar czf /backup/grafana_data.tar.gz -C /source .
    fi
    
    # Sauvegarde de la configuration
    cp docker-compose.production.yml "$BACKUP_DIR/" 2>/dev/null || true
    
    log_success "Sauvegarde créée dans $BACKUP_DIR"
}

# Construction des images Docker
build_images() {
    log "🔨 Construction des images Docker Ultra..."
    
    cd "$PROJECT_ROOT"
    
    # CV Parser Ultra
    log "Construction CV Parser Ultra..."
    docker build -t supersmartmatch/cv-parser-ultra:v2.0 \
        -f services/cv-parser-ultra/Dockerfile \
        services/cv-parser-ultra/
    
    # Job Parser Ultra  
    log "Construction Job Parser Ultra..."
    docker build -t supersmartmatch/job-parser-ultra:v2.0 \
        -f services/job-parser-ultra/Dockerfile \
        services/job-parser-ultra/
    
    log_success "Images Docker construites"
}

# Validation des images
validate_images() {
    log "🔍 Validation des images Docker..."
    
    local images=(
        "supersmartmatch/cv-parser-ultra:v2.0"
        "supersmartmatch/job-parser-ultra:v2.0"
    )
    
    for image in "${images[@]}"; do
        if ! docker images | grep -q "$image"; then
            log_error "Image $image manquante"
            exit 1
        fi
        
        # Test basic de l'image
        log "Test de l'image $image..."
        docker run --rm "$image" python -c "print('Image OK')" || {
            log_error "Test de l'image $image échoué"
            exit 1
        }
    done
    
    log_success "Images validées"
}

# Arrêt des anciens services
stop_old_services() {
    log "⏹️  Arrêt des anciens services..."
    
    cd "$PROJECT_ROOT"
    
    # Arrêt gracieux
    if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
        log "Arrêt des services existants..."
        docker-compose -f docker-compose.production.yml down --timeout 30
    fi
    
    log_success "Anciens services arrêtés"
}

# Déploiement des services Ultra
deploy_ultra_services() {
    log "🚀 Déploiement des services Ultra..."
    
    cd "$PROJECT_ROOT"
    
    # Variables d'environnement pour Ultra
    export COMPOSE_PROJECT_NAME="supersmartmatch-ultra"
    export COMPOSE_FILE="docker-compose.ultra.yml"
    
    # Démarrage de l'infrastructure de base d'abord
    log "Démarrage de l'infrastructure..."
    docker-compose up -d postgres redis minio
    
    # Attendre que l'infrastructure soit prête
    log "Attente de l'infrastructure..."
    sleep 30
    
    # Démarrage des services de monitoring
    log "Démarrage du monitoring..."
    docker-compose up -d prometheus grafana
    
    # Attendre monitoring
    sleep 15
    
    # Démarrage des parsers Ultra
    log "Démarrage des parsers Ultra..."
    docker-compose up -d cv-parser-ultra job-parser-ultra
    
    # Attendre parsers
    sleep 20
    
    # Démarrage des autres services
    log "Démarrage des services restants..."
    docker-compose up -d
    
    log_success "Services Ultra déployés"
}

# Tests de santé
health_checks() {
    log "🏥 Tests de santé des services..."
    
    local services=(
        "http://localhost:5051/health:CV Parser Ultra"
        "http://localhost:5053/health:Job Parser Ultra" 
        "http://localhost:5052/health:Matching Service"
        "http://localhost:5050/health:API Gateway"
        "http://localhost:3001/api/health:Grafana"
        "http://localhost:9091/-/healthy:Prometheus"
    )
    
    local max_attempts=30
    local attempt=1
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service_info"
        
        log "Test de santé: $name..."
        attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            if curl -sf "$url" >/dev/null 2>&1; then
                log_success "$name est en bonne santé"
                break
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                log_error "$name ne répond pas après $max_attempts tentatives"
                return 1
            fi
            
            log "Tentative $attempt/$max_attempts pour $name..."
            sleep 5
            ((attempt++))
        done
    done
    
    log_success "Tous les services sont en bonne santé"
}

# Tests fonctionnels des parsers Ultra
test_parsers_functionality() {
    log "🧪 Tests fonctionnels des parsers Ultra..."
    
    # Test CV Parser Ultra avec WebSocket
    log "Test CV Parser Ultra..."
    local cv_test_response=$(curl -s -X POST \
        -F "file=@test-data/sample-cv.pdf" \
        http://localhost:5051/v2/parse/cv/stream)
    
    if echo "$cv_test_response" | grep -q "task_id"; then
        log_success "CV Parser Ultra répond correctement"
    else
        log_error "CV Parser Ultra ne répond pas correctement"
        return 1
    fi
    
    # Test Job Parser Ultra avec WebSocket
    log "Test Job Parser Ultra..."
    local job_test_response=$(curl -s -X POST \
        -F "file=@test-data/sample-job.txt" \
        http://localhost:5053/v2/parse/job/stream)
    
    if echo "$job_test_response" | grep -q "task_id"; then
        log_success "Job Parser Ultra répond correctement"
    else
        log_error "Job Parser Ultra ne répond pas correctement"
        return 1
    fi
    
    log_success "Tests fonctionnels réussis"
}

# Vérification des métriques
verify_metrics() {
    log "📊 Vérification des métriques..."
    
    # Vérifier que Prometheus collecte les métriques des parsers Ultra
    local prometheus_url="http://localhost:9091"
    
    # Métriques CV Parser Ultra
    if curl -s "$prometheus_url/api/v1/query?query=cv_parsing_requests_total" | grep -q "success"; then
        log_success "Métriques CV Parser Ultra collectées"
    else
        log_warning "Métriques CV Parser Ultra non trouvées (normal au démarrage)"
    fi
    
    # Métriques Job Parser Ultra
    if curl -s "$prometheus_url/api/v1/query?query=job_parsing_requests_total" | grep -q "success"; then
        log_success "Métriques Job Parser Ultra collectées"
    else
        log_warning "Métriques Job Parser Ultra non trouvées (normal au démarrage)"
    fi
    
    log_success "Vérification des métriques terminée"
}

# Configuration post-déploiement
post_deployment_setup() {
    log "⚙️  Configuration post-déploiement..."
    
    # Import des dashboards Grafana
    log "Import des dashboards Grafana Ultra..."
    sleep 10  # Attendre que Grafana soit complètement démarré
    
    # Les dashboards sont automatiquement provisionnés via les volumes
    log_success "Dashboards Grafana configurés"
    
    # Configuration des alertes
    log "Configuration des alertes..."
    # Les règles d'alertes sont déjà chargées via prometheus-ultra.yml
    log_success "Alertes configurées"
    
    log_success "Configuration post-déploiement terminée"
}

# Affichage du statut final
show_final_status() {
    log "📋 Statut final du déploiement..."
    
    echo ""
    echo -e "${GREEN}🎉 DÉPLOIEMENT ULTRA v2.0 TERMINÉ AVEC SUCCÈS! 🎉${NC}"
    echo ""
    echo -e "${BLUE}Services accessibles:${NC}"
    echo -e "  🚀 API Gateway:           http://localhost:5050"
    echo -e "  ⚡ CV Parser Ultra:       http://localhost:5051"
    echo -e "  🎯 Job Parser Ultra:      http://localhost:5053"
    echo -e "  🔄 Matching Service:      http://localhost:5052"
    echo -e "  📊 Grafana Ultra:         http://localhost:3001 (admin/admin)"
    echo -e "  📈 Prometheus:            http://localhost:9091"
    echo -e "  💾 MinIO:                 http://localhost:9001"
    echo ""
    echo -e "${YELLOW}Fonctionnalités Ultra v2.0:${NC}"
    echo -e "  ✅ Streaming WebSocket temps réel"
    echo -e "  ✅ Parsing IA avec OpenAI GPT-4"
    echo -e "  ✅ Validation interactive"
    echo -e "  ✅ Fallback manuel intelligent"
    echo -e "  ✅ Métriques Prometheus détaillées"
    echo -e "  ✅ Support multi-formats (PDF, DOCX, JPG, PNG, HTML)"
    echo -e "  ✅ Cache Redis ultra-performant"
    echo -e "  ✅ OCR intégré pour images"
    echo ""
    echo -e "${PURPLE}Logs de déploiement: $LOG_FILE${NC}"
    echo -e "${PURPLE}Sauvegarde: $BACKUP_DIR${NC}"
    echo ""
}

# Fonction de rollback
rollback() {
    log_error "🔄 Rollback en cours..."
    
    # Arrêt des services Ultra
    docker-compose -f docker-compose.ultra.yml down --timeout 30
    
    # Restauration des données si nécessaire
    if [[ -d "$BACKUP_DIR" ]]; then
        log "Restauration des données..."
        # Restauration des volumes
        docker run --rm -v postgres_data:/target -v "$BACKUP_DIR":/backup alpine tar xzf /backup/postgres_data.tar.gz -C /target
        docker run --rm -v redis_data:/target -v "$BACKUP_DIR":/backup alpine tar xzf /backup/redis_data.tar.gz -C /target
        docker run --rm -v grafana_data:/target -v "$BACKUP_DIR":/backup alpine tar xzf /backup/grafana_data.tar.gz -C /target
    fi
    
    # Redémarrage des anciens services
    if [[ -f "$BACKUP_DIR/docker-compose.production.yml" ]]; then
        cp "$BACKUP_DIR/docker-compose.production.yml" docker-compose.production.yml
        docker-compose -f docker-compose.production.yml up -d
    fi
    
    log_success "Rollback terminé"
}

# Gestion des erreurs
trap 'log_error "Erreur détectée à la ligne $LINENO. Arrêt du déploiement."; rollback; exit 1' ERR

# Main function
main() {
    show_banner
    
    log "🚀 Début du déploiement Ultra v2.0..."
    log "📝 Logs détaillés: $LOG_FILE"
    
    check_prerequisites
    backup_current_state
    build_images
    validate_images
    stop_old_services
    deploy_ultra_services
    health_checks
    test_parsers_functionality
    verify_metrics
    post_deployment_setup
    show_final_status
    
    log_success "🎉 Déploiement Ultra v2.0 terminé avec succès!"
}

# Gestion des arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        health_checks
        ;;
    "test")
        test_parsers_functionality
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health|test}"
        exit 1
        ;;
esac
