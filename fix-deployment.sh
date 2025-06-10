#!/bin/bash

# ===========================================
# SuperSmartMatch V2 - Fix Deployment Script
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}===========================================\n$1\n===========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Load environment variables
load_env_vars() {
    if [ -f .env.production ]; then
        print_info "Chargement des variables d'environnement..."
        set -a  # Automatically export all variables
        source .env.production
        set +a
        print_success "Variables d'environnement chargées"
        
        # Verify key variables are loaded
        if [ -z "$POSTGRES_PASSWORD" ] || [ -z "$REDIS_PASSWORD" ]; then
            print_error "Variables critiques manquantes dans .env.production"
            exit 1
        fi
    else
        print_error "Fichier .env.production non trouvé"
        exit 1
    fi
}

# Check if Docker and Docker Compose are installed
check_prerequisites() {
    print_header "Vérification des prérequis"
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    print_success "Docker trouvé"
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    print_success "Docker Compose trouvé"
    
    # Load environment variables
    load_env_vars
}

# Stop all services
stop_services() {
    print_header "Arrêt des services existants"
    
    if docker-compose -f docker-compose.production.yml --env-file .env.production ps -q | grep -q .; then
        print_info "Arrêt des conteneurs..."
        docker-compose -f docker-compose.production.yml --env-file .env.production down
        print_success "Services arrêtés"
    else
        print_info "Aucun service en cours d'exécution"
    fi
}

# Clean up containers and volumes if needed
cleanup_if_needed() {
    print_header "Nettoyage (optionnel)"
    
    read -p "Voulez-vous nettoyer les volumes existants? (y/N): " cleanup_volumes
    if [[ $cleanup_volumes =~ ^[Yy]$ ]]; then
        print_warning "Suppression des volumes (toutes les données seront perdues)..."
        docker-compose -f docker-compose.production.yml --env-file .env.production down -v
        docker volume prune -f
        print_success "Volumes nettoyés"
    fi
    
    read -p "Voulez-vous rebuild tous les images? (y/N): " rebuild_images
    if [[ $rebuild_images =~ ^[Yy]$ ]]; then
        print_info "Suppression des images existantes..."
        docker-compose -f docker-compose.production.yml --env-file .env.production down --rmi all 2>/dev/null || true
        print_success "Images supprimées"
    fi
}

# Create necessary directories
create_directories() {
    print_header "Création des répertoires nécessaires"
    
    # Log directories
    mkdir -p logs/{api-gateway,cv-parser,job-parser,matching,user,notification,analytics,nginx}
    
    # Temp directories
    mkdir -p temp/{cv-uploads,job-uploads}
    
    # Monitoring directories
    mkdir -p monitoring/{prometheus,grafana}/{dashboards,datasources,rules}
    
    # Database backup directory
    mkdir -p database/backups
    
    print_success "Répertoires créés"
}

# Fix file permissions
fix_permissions() {
    print_header "Correction des permissions"
    
    # Make database init script executable
    chmod +x database/init/01-init-databases.sh
    
    # Fix log directories permissions
    sudo chown -R $USER:$USER logs/ temp/ 2>/dev/null || {
        print_warning "Impossible de changer les permissions avec sudo, continuant..."
    }
    
    print_success "Permissions corrigées"
}

# Create basic monitoring configuration if missing
create_monitoring_config() {
    print_header "Configuration du monitoring"
    
    # Basic Prometheus config
    if [ ! -f monitoring/prometheus/prometheus.yml ]; then
        cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:5050']
    metrics_path: '/metrics'

  - job_name: 'microservices'
    static_configs:
      - targets: 
          - 'cv-parser-service:5051'
          - 'job-parser-service:5053'
          - 'matching-service:5052'
          - 'user-service:5054'
          - 'notification-service:5055'
          - 'analytics-service:5056'
EOF
        print_success "Configuration Prometheus créée"
    fi
    
    # Basic Grafana datasource
    if [ ! -f monitoring/grafana/datasources/prometheus.yml ]; then
        mkdir -p monitoring/grafana/datasources
        cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
        print_success "Configuration Grafana créée"
    fi
}

# Deploy services step by step
deploy_services() {
    print_header "Déploiement des services"
    
    print_info "Étape 1: Infrastructure (PostgreSQL, Redis, MinIO)"
    docker-compose -f docker-compose.production.yml --env-file .env.production up -d postgres redis minio
    
    print_info "Attente que l'infrastructure soit prête..."
    sleep 30
    
    # Check infrastructure health
    wait_for_service "postgres" "5432"
    wait_for_service "redis" "6379" 
    wait_for_service "minio" "9000"
    
    print_info "Étape 2: Services métiers"
    docker-compose -f docker-compose.production.yml --env-file .env.production up -d \
        cv-parser-service \
        job-parser-service \
        matching-service \
        user-service \
        notification-service \
        analytics-service
    
    print_info "Attente que les services soient prêts..."
    sleep 20
    
    print_info "Étape 3: API Gateway"
    docker-compose -f docker-compose.production.yml --env-file .env.production up -d api-gateway
    
    sleep 10
    
    print_info "Étape 4: Reverse Proxy et Monitoring"
    docker-compose -f docker-compose.production.yml --env-file .env.production up -d nginx prometheus grafana
    
    print_success "Déploiement terminé"
}

# Wait for a service to be ready
wait_for_service() {
    local service=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    print_info "Attente du service $service sur le port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z localhost $port 2>/dev/null; then
            print_success "Service $service prêt"
            return 0
        fi
        
        if [ $((attempt % 5)) -eq 0 ]; then
            print_info "Tentative $attempt/$max_attempts pour $service..."
        fi
        
        sleep 5
        attempt=$((attempt + 1))
    done
    
    print_warning "Service $service n'est pas prêt après $max_attempts tentatives"
    return 1
}

# Check services health
check_health() {
    print_header "Vérification de l'état des services"
    
    # Infrastructure
    check_service_health "PostgreSQL" "postgres" "5432"
    check_service_health "Redis" "redis" "6379"
    check_service_health "MinIO" "minio" "9000"
    
    # Services
    check_service_health "CV Parser" "cv-parser-service" "5051"
    check_service_health "Job Parser" "job-parser-service" "5053"
    check_service_health "Matching Service" "matching-service" "5052"
    check_service_health "User Service" "user-service" "5054"
    check_service_health "Notification Service" "notification-service" "5055"
    check_service_health "Analytics Service" "analytics-service" "5056"
    
    # Gateway & Monitoring
    check_service_health "API Gateway" "api-gateway" "5050"
    check_service_health "Nginx" "nginx" "80"
    check_service_health "Prometheus" "prometheus" "9091"
    check_service_health "Grafana" "grafana" "3000"
}

check_service_health() {
    local name=$1
    local container=$2
    local port=$3
    
    if docker-compose -f docker-compose.production.yml --env-file .env.production ps $container | grep -q "Up"; then
        if curl -s --max-time 5 http://localhost:$port/health > /dev/null 2>&1 || \
           curl -s --max-time 5 http://localhost:$port > /dev/null 2>&1; then
            print_success "$name - ✅ OK"
        else
            print_warning "$name - ⚠️  Service démarré mais health check échoué"
        fi
    else
        print_error "$name - ❌ Service arrêté"
    fi
}

# Display useful information
show_info() {
    print_header "Informations de connexion"
    
    echo -e "${GREEN}🌐 Services Web:${NC}"
    echo "  • API Gateway:      http://localhost:5050"
    echo "  • CV Parser:        http://localhost:5051"
    echo "  • Matching Service: http://localhost:5052"
    echo "  • Job Parser:       http://localhost:5053"
    echo "  • User Service:     http://localhost:5054"
    echo "  • Notification:     http://localhost:5055"
    echo "  • Analytics:        http://localhost:5056"
    echo ""
    echo -e "${BLUE}🔧 Infrastructure:${NC}"
    echo "  • PostgreSQL:       localhost:5432"
    echo "  • Redis:            localhost:6379"
    echo "  • MinIO Console:    http://localhost:9001"
    echo ""
    echo -e "${YELLOW}📊 Monitoring:${NC}"
    echo "  • Grafana:          http://localhost:3000 (admin/$GRAFANA_ADMIN_PASSWORD)"
    echo "  • Prometheus:       http://localhost:9091"
    echo ""
    echo -e "${GREEN}🚀 Tests rapides:${NC}"
    echo "  curl http://localhost:5050/health"
    echo "  curl http://localhost/api/health"
    echo "  docker-compose -f docker-compose.production.yml --env-file .env.production logs -f api-gateway"
}

# Show logs for troubleshooting
show_logs() {
    print_header "Affichage des logs (Ctrl+C pour quitter)"
    
    echo "Choisissez un service pour voir les logs:"
    echo "1) Tous les services"
    echo "2) PostgreSQL"
    echo "3) Redis"
    echo "4) API Gateway"
    echo "5) CV Parser"
    echo "6) Matching Service"
    
    read -p "Votre choix (1-6): " log_choice
    
    case $log_choice in
        1) docker-compose -f docker-compose.production.yml --env-file .env.production logs -f ;;
        2) docker-compose -f docker-compose.production.yml --env-file .env.production logs -f postgres ;;
        3) docker-compose -f docker-compose.production.yml --env-file .env.production logs -f redis ;;
        4) docker-compose -f docker-compose.production.yml --env-file .env.production logs -f api-gateway ;;
        5) docker-compose -f docker-compose.production.yml --env-file .env.production logs -f cv-parser-service ;;
        6) docker-compose -f docker-compose.production.yml --env-file .env.production logs -f matching-service ;;
        *) print_error "Choix invalide" ;;
    esac
}

# Main menu
main_menu() {
    while true; do
        print_header "SuperSmartMatch V2 - Menu de Déploiement"
        echo "1) 🔧 Redéploiement complet (recommandé)"
        echo "2) 🚀 Déploiement rapide"
        echo "3) 📊 Vérifier l'état des services"
        echo "4) 📜 Voir les logs"
        echo "5) 🛑 Arrêter tous les services"
        echo "6) ℹ️  Afficher les informations de connexion"
        echo "7) 🚪 Quitter"
        echo ""
        read -p "Votre choix (1-7): " choice
        
        case $choice in
            1)
                check_prerequisites
                stop_services
                cleanup_if_needed
                create_directories
                fix_permissions
                create_monitoring_config
                deploy_services
                sleep 5
                check_health
                show_info
                ;;
            2)
                check_prerequisites
                create_directories
                fix_permissions
                deploy_services
                check_health
                show_info
                ;;
            3)
                load_env_vars
                check_health
                ;;
            4)
                load_env_vars
                show_logs
                ;;
            5)
                load_env_vars
                stop_services
                ;;
            6)
                load_env_vars
                show_info
                ;;
            7)
                print_success "Au revoir!"
                exit 0
                ;;
            *)
                print_error "Choix invalide"
                ;;
        esac
        
        echo ""
        read -p "Appuyez sur Entrée pour continuer..."
    done
}

# Run main menu
main_menu
