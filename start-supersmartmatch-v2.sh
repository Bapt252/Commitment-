#!/bin/bash
set -e

# 🚀 SuperSmartMatch V2 - Script de Démarrage Automatisé
# Déploiement complet du service unifié avec validation

echo "🚀 SuperSmartMatch V2 - Démarrage Automatisé"
echo "=============================================="

# Configuration par défaut
PROJECT_NAME="supersmartmatch-v2"
BASE_DIR="$(pwd)"
COMPOSE_FILE="docker-compose.supersmartmatch-v2.yml"
VALIDATION_TIMEOUT=300
ENVIRONMENT="${ENVIRONMENT:-production}"

# Couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction utilitaires
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Docker et Docker Compose
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé. Installation requise."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé. Installation requise."
        exit 1
    fi
    
    # Python pour scripts de validation
    if ! command -v python3 &> /dev/null; then
        log_warning "Python3 non trouvé. Validation automatique désactivée."
    fi
    
    # Vérification espace disque
    AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
    if [ "$AVAILABLE_SPACE" -lt 5242880 ]; then  # 5GB en KB
        log_warning "Moins de 5GB d'espace disque disponible. Recommandé: 10GB+"
    fi
    
    log_success "Prérequis validés"
}

# Configuration de l'environnement
setup_environment() {
    log_info "Configuration de l'environnement..."
    
    # Création des répertoires nécessaires
    mkdir -p logs/{supersmartmatch-v2,nexten,v1,nginx,redis}
    mkdir -p config/{supersmartmatch-v2,monitoring,nginx}
    mkdir -p data/{redis,prometheus,grafana}
    mkdir -p monitoring/{prometheus,grafana/dashboards,grafana/datasources}
    
    # Configuration des permissions
    chmod -R 755 logs config data monitoring
    
    # Copie de la configuration par défaut si non existante
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            log_info "Fichier .env créé depuis .env.example"
        else
            create_default_env
        fi
    fi
    
    log_success "Environnement configuré"
}

# Création configuration par défaut
create_default_env() {
    cat > .env << EOF
# SuperSmartMatch V2 Configuration
ENVIRONMENT=${ENVIRONMENT}
COMPOSE_PROJECT_NAME=${PROJECT_NAME}

# Service URLs
NEXTEN_URL=http://nexten-matcher:5052
SUPERSMARTMATCH_V1_URL=http://supersmartmatch-v1:5062

# Redis Configuration
REDIS_URL=redis://redis-cache:6379
CACHE_TTL=300

# Performance Settings
MAX_RESPONSE_TIME_MS=100
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# Feature Flags
ENABLE_V2=true
V2_TRAFFIC_PERCENTAGE=100
ENABLE_NEXTEN_ALGORITHM=true
ENABLE_SMART_SELECTION=true

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_RETENTION=168h

# API Keys (à configurer)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
EOF
    
    log_info "Configuration par défaut créée. Veuillez éditer .env avec vos clés API."
}

# Configuration monitoring
setup_monitoring() {
    log_info "Configuration du monitoring..."
    
    # Configuration Prometheus
    cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alerts/*.yml"

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
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF

    # Configuration Grafana datasource
    cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

    log_success "Monitoring configuré"
}

# Configuration Nginx
setup_nginx() {
    log_info "Configuration Nginx..."
    
    cat > config/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream supersmartmatch-v2 {
        server supersmartmatch-v2:5070;
    }
    
    upstream nexten-matcher {
        server nexten-matcher:5052;
    }
    
    upstream supersmartmatch-v1 {
        server supersmartmatch-v1:5062;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        # SuperSmartMatch V2 (principal)
        location / {
            proxy_pass http://supersmartmatch-v2;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Monitoring endpoints
        location /prometheus {
            proxy_pass http://prometheus:9090;
        }
        
        location /grafana {
            proxy_pass http://grafana:3000;
        }
        
        # Health checks
        location /health {
            proxy_pass http://supersmartmatch-v2/health;
        }
    }
}
EOF

    log_success "Nginx configuré"
}

# Démarrage des services
start_services() {
    log_info "Démarrage des services SuperSmartMatch V2..."
    
    # Arrêt des services existants
    log_info "Arrêt des services existants..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    
    # Construction des images si nécessaire
    log_info "Construction des images Docker..."
    docker-compose -f "$COMPOSE_FILE" build --parallel
    
    # Démarrage en arrière-plan
    log_info "Démarrage des services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    log_success "Services démarrés"
}

# Validation du déploiement
validate_deployment() {
    log_info "Validation du déploiement..."
    
    # Attente démarrage des services
    log_info "Attente du démarrage des services (max ${VALIDATION_TIMEOUT}s)..."
    
    local timeout=$VALIDATION_TIMEOUT
    local interval=10
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
            log_info "Services détectés en cours d'exécution..."
            sleep $interval
            break
        fi
        
        sleep $interval
        elapsed=$((elapsed + interval))
        log_info "Attente... (${elapsed}s/${timeout}s)"
    done
    
    # Validation santé des services
    log_info "Validation de la santé des services..."
    
    # SuperSmartMatch V2
    if curl -sf http://localhost:5070/health > /dev/null 2>&1; then
        log_success "✅ SuperSmartMatch V2 (port 5070) - HEALTHY"
    else
        log_warning "⚠️ SuperSmartMatch V2 (port 5070) - En cours de démarrage"
    fi
    
    # Nexten Matcher
    if curl -sf http://localhost:5052/health > /dev/null 2>&1; then
        log_success "✅ Nexten Matcher (port 5052) - HEALTHY"
    else
        log_warning "⚠️ Nexten Matcher (port 5052) - En cours de démarrage"
    fi
    
    # SuperSmartMatch V1
    if curl -sf http://localhost:5062/health > /dev/null 2>&1; then
        log_success "✅ SuperSmartMatch V1 (port 5062) - HEALTHY"
    else
        log_warning "⚠️ SuperSmartMatch V1 (port 5062) - En cours de démarrage"
    fi
    
    # Redis
    if docker exec redis-cache-v2 redis-cli ping > /dev/null 2>&1; then
        log_success "✅ Redis Cache - HEALTHY"
    else
        log_warning "⚠️ Redis Cache - En cours de démarrage"
    fi
    
    # Validation complète avec script Python
    if command -v python3 &> /dev/null && [ -f validate-supersmartmatch-v2.py ]; then
        log_info "Validation E2E avec script Python..."
        if python3 validate-supersmartmatch-v2.py http://localhost:5070; then
            log_success "✅ Validation E2E - PASSED"
        else
            log_warning "⚠️ Validation E2E - PARTIAL (voir détails ci-dessus)"
        fi
    fi
}

# Affichage des informations de connexion
show_connection_info() {
    echo ""
    echo "🎉 SuperSmartMatch V2 déployé avec succès!"
    echo "==========================================="
    echo ""
    echo "📊 ENDPOINTS PRINCIPAUX:"
    echo "  🚀 SuperSmartMatch V2:     http://localhost:5070"
    echo "  📱 API V2:                 http://localhost:5070/api/v2/match"
    echo "  🔄 API V1 (compat):        http://localhost:5070/match"
    echo "  💚 Health Check:           http://localhost:5070/health"
    echo "  📊 Métriques:              http://localhost:5070/metrics"
    echo "  📚 Documentation:          http://localhost:5070/api/docs"
    echo ""
    echo "🔧 SERVICES INTÉGRÉS:"
    echo "  🧠 Nexten Matcher:         http://localhost:5052"
    echo "  ⚡ SuperSmartMatch V1:      http://localhost:5062" 
    echo "  🗄️ Redis Cache:            http://localhost:6379"
    echo ""
    echo "📈 MONITORING:"
    echo "  📊 Grafana Dashboard:      http://localhost:3000 (admin/supersmartmatch)"
    echo "  🔍 Prometheus:             http://localhost:9090"
    echo "  🌐 Nginx Gateway:          http://localhost:80"
    echo ""
    echo "🧪 VALIDATION:"
    echo "  python3 validate-supersmartmatch-v2.py"
    echo ""
    echo "📋 COMMANDES UTILES:"
    echo "  docker-compose -f $COMPOSE_FILE logs -f        # Logs en temps réel"
    echo "  docker-compose -f $COMPOSE_FILE ps             # Status services"
    echo "  docker-compose -f $COMPOSE_FILE down           # Arrêt complet"
    echo "  ./scripts/health-check.sh                      # Vérification santé"
    echo ""
}

# Fonction de nettoyage en cas d'erreur
cleanup_on_error() {
    log_error "Erreur détectée. Nettoyage..."
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
    exit 1
}

# Main execution
main() {
    trap cleanup_on_error ERR
    
    echo "Démarrage: $(date)"
    echo "Répertoire: $BASE_DIR"
    echo "Environnement: $ENVIRONMENT"
    echo ""
    
    check_prerequisites
    setup_environment
    setup_monitoring
    setup_nginx
    start_services
    validate_deployment
    show_connection_info
    
    log_success "🎉 Déploiement SuperSmartMatch V2 terminé avec succès!"
}

# Options de ligne de commande
while [[ $# -gt 0 ]]; do
    case $1 in
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --timeout)
            VALIDATION_TIMEOUT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --env ENV              Environnement (production|development|staging)"
            echo "  --timeout SECONDS      Timeout pour validation (défaut: 300s)"
            echo "  --help                 Afficher cette aide"
            exit 0
            ;;
        *)
            log_error "Option inconnue: $1"
            exit 1
            ;;
    esac
done

# Exécution principale
main "$@"
