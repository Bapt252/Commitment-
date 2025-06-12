#!/bin/bash

# ===========================================
# SuperSmartMatch V2 - Production Deployment Script
# ===========================================

set -e

echo "🚀 SuperSmartMatch V2 - Microservices Production Deployment"
echo "============================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.production.yml"
ENV_FILE=".env.production"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Functions
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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Environment file $ENV_FILE not found. Creating from template..."
        if [ -f ".env.production.template" ]; then
            cp .env.production.template $ENV_FILE
            log_warning "Please edit $ENV_FILE with your production values before continuing!"
            exit 1
        else
            log_error "Environment template not found"
            exit 1
        fi
    fi
    
    # Check compose file
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker compose file $COMPOSE_FILE not found"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

validate_environment() {
    log_info "Validating environment configuration..."
    
    # Source environment file
    source $ENV_FILE
    
    # Check required variables
    required_vars=(
        "JWT_SECRET"
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "MINIO_ACCESS_KEY"
        "MINIO_SECRET_KEY"
        "GRAFANA_ADMIN_PASSWORD"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check secret strength
    if [ ${#JWT_SECRET} -lt 32 ]; then
        log_error "JWT_SECRET must be at least 32 characters long"
        exit 1
    fi
    
    log_success "Environment validation passed"
}

create_directories() {
    log_info "Creating required directories..."
    
    # Create directories
    mkdir -p logs/{api-gateway,cv-parser,job-parser,matching,user,notification,analytics,nginx}
    mkdir -p temp/{cv-uploads,job-uploads}
    mkdir -p database/backups
    mkdir -p monitoring/{prometheus,grafana}
    mkdir -p ssl
    mkdir -p $BACKUP_DIR
    
    # Set permissions
    chmod 755 logs/*
    chmod 755 temp/*
    chmod 700 database/backups
    
    log_success "Directories created successfully"
}

build_services() {
    log_info "Building microservices..."
    
    # Pull latest base images
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE pull
    
    # Build custom services
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE build --no-cache
    
    log_success "Services built successfully"
}

backup_existing_data() {
    log_info "Creating backup of existing data..."
    
    # Check if containers are running
    if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps | grep -q "Up"; then
        log_info "Backing up database..."
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec -T postgres pg_dumpall -U ssm_user > "$BACKUP_DIR/database_backup.sql"
        
        log_info "Backing up Redis data..."
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec -T redis redis-cli --rdb - > "$BACKUP_DIR/redis_backup.rdb"
        
        log_success "Backup completed: $BACKUP_DIR"
    else
        log_info "No running containers found, skipping backup"
    fi
}

deploy_infrastructure() {
    log_info "Deploying infrastructure services..."
    
    # Start infrastructure first
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d postgres redis minio
    
    # Wait for database to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    until docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec postgres pg_isready -U ssm_user -d supersmartmatch; do
        sleep 2
    done
    
    # Wait for Redis to be ready
    log_info "Waiting for Redis to be ready..."
    until docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec redis redis-cli ping; do
        sleep 2
    done
    
    # Initialize MinIO buckets
    log_info "Initializing MinIO buckets..."
    sleep 5  # Wait for MinIO to start
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec minio mc mb /data/cv-documents || true
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec minio mc mb /data/job-descriptions || true
    
    log_success "Infrastructure deployed successfully"
}

deploy_microservices() {
    log_info "Deploying microservices..."
    
    # Deploy services in order
    services=(
        "user-service"
        "cv-parser-service"
        "job-parser-service" 
        "matching-service"
        "notification-service"
        "analytics-service"
        "api-gateway"
    )
    
    for service in "${services[@]}"; do
        log_info "Starting $service..."
        docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d $service
        
        # Wait for health check
        sleep 10
        
        # Check if service is healthy
        if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps $service | grep -q "healthy"; then
            log_success "$service started successfully"
        else
            log_warning "$service may not be fully ready yet"
        fi
    done
    
    log_success "All microservices deployed"
}

deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    # Start monitoring services
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d prometheus grafana
    
    # Wait for services to be ready
    sleep 15
    
    log_success "Monitoring stack deployed"
}

deploy_load_balancer() {
    log_info "Deploying load balancer..."
    
    # Start Nginx
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE up -d nginx
    
    # Wait and check
    sleep 10
    
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "Load balancer deployed and healthy"
    else
        log_warning "Load balancer may not be fully ready"
    fi
}

run_health_checks() {
    log_info "Running comprehensive health checks..."
    
    # API Gateway health
    if curl -f http://localhost/api/health > /dev/null 2>&1; then
        log_success "✅ API Gateway is healthy"
    else
        log_error "❌ API Gateway health check failed"
        return 1
    fi
    
    # Individual service health checks
    services=(
        "api-gateway:5050"
        "cv-parser-service:5051"
        "matching-service:5052"
        "job-parser-service:5053"
        "user-service:5054"
        "notification-service:5055"
        "analytics-service:5056"
    )
    
    for service_port in "${services[@]}"; do
        IFS=':' read -r service port <<< "$service_port"
        if curl -f http://localhost:$port/health > /dev/null 2>&1; then
            log_success "✅ $service is healthy"
        else
            log_error "❌ $service health check failed"
        fi
    done
    
    # Database connectivity
    if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec postgres pg_isready -U ssm_user -d supersmartmatch > /dev/null 2>&1; then
        log_success "✅ PostgreSQL is healthy"
    else
        log_error "❌ PostgreSQL health check failed"
    fi
    
    # Redis connectivity
    if docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE exec redis redis-cli ping > /dev/null 2>&1; then
        log_success "✅ Redis is healthy"
    else
        log_error "❌ Redis health check failed"
    fi
    
    log_success "Health checks completed"
}

run_integration_tests() {
    log_info "Running integration tests..."
    
    # Test authentication flow
    log_info "Testing authentication..."
    
    # Register test user
    register_response=$(curl -s -X POST http://localhost/api/auth/register \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@supersmartmatch.com",
            "password": "TestPassword123!",
            "firstName": "Test",
            "lastName": "User"
        }' || echo "error")
    
    if echo "$register_response" | grep -q "registered successfully"; then
        log_success "✅ User registration test passed"
    else
        log_warning "⚠️ User registration test failed (user may already exist)"
    fi
    
    # Login test user
    login_response=$(curl -s -X POST http://localhost/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@supersmartmatch.com",
            "password": "TestPassword123!"
        }')
    
    if echo "$login_response" | grep -q "token"; then
        log_success "✅ User login test passed"
        
        # Extract token for further tests
        token=$(echo "$login_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
        
        # Test protected endpoint
        protected_response=$(curl -s -H "Authorization: Bearer $token" http://localhost/api/users/profile)
        
        if echo "$protected_response" | grep -q "id"; then
            log_success "✅ Protected endpoint test passed"
        else
            log_error "❌ Protected endpoint test failed"
        fi
    else
        log_error "❌ User login test failed"
    fi
    
    log_success "Integration tests completed"
}

show_deployment_summary() {
    echo ""
    echo "🎉 SuperSmartMatch V2 Deployment Complete!"
    echo "=========================================="
    echo ""
    echo "📊 Services Status:"
    docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps
    echo ""
    echo "🌐 Access Points:"
    echo "  • Main Application: http://localhost"
    echo "  • API Gateway: http://localhost/api"
    echo "  • Grafana Dashboard: http://localhost:3000 (admin/[your_password])"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • MinIO Console: http://localhost:9001"
    echo ""
    echo "📋 Service Health Checks:"
    echo "  • API Gateway: http://localhost/health/api-gateway"
    echo "  • CV Parser: http://localhost/health/cv-parser"
    echo "  • Matching: http://localhost/health/matching"
    echo ""
    echo "📁 Important Directories:"
    echo "  • Logs: ./logs/"
    echo "  • Backups: $BACKUP_DIR"
    echo "  • Database Data: Docker volume 'postgres_data'"
    echo ""
    echo "🔧 Next Steps:"
    echo "  1. Update DNS/SSL certificates for production domain"
    echo "  2. Configure monitoring alerts"
    echo "  3. Set up automated backups"
    echo "  4. Review security settings"
    echo ""
}

# Main deployment flow
main() {
    case "${1:-deploy}" in
        "check")
            check_prerequisites
            validate_environment
            ;;
        "build")
            check_prerequisites
            validate_environment
            build_services
            ;;
        "deploy")
            check_prerequisites
            validate_environment
            create_directories
            build_services
            backup_existing_data
            deploy_infrastructure
            deploy_microservices
            deploy_monitoring
            deploy_load_balancer
            run_health_checks
            run_integration_tests
            show_deployment_summary
            ;;
        "restart")
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
            main deploy
            ;;
        "stop")
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down
            ;;
        "logs")
            docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f
            ;;
        *)
            echo "Usage: $0 {check|build|deploy|restart|stop|logs}"
            echo ""
            echo "Commands:"
            echo "  check   - Check prerequisites and configuration"
            echo "  build   - Build services only"
            echo "  deploy  - Full production deployment"
            echo "  restart - Stop and redeploy"
            echo "  stop    - Stop all services"
            echo "  logs    - Show service logs"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
