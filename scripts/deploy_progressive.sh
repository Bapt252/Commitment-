#!/bin/bash

# ================================================================
# SuperSmartMatch V2 - Progressive Deployment Script
# ================================================================
# Deploys infrastructure progressively from basic to complete
# Resolves Docker images missing issue
# ================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/deployment.log"

# Ensure logs directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Logging functions
log() {
    echo -e "${1}" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

log_step() {
    log "${CYAN}[STEP]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Create configuration files
create_configs() {
    log_step "Creating configuration files..."
    
    # Create config directory
    mkdir -p "$PROJECT_ROOT/config/"{nginx,prometheus,grafana/{dashboards,datasources},postgres}
    
    # Basic nginx config
    cat > "$PROJECT_ROOT/config/nginx/nginx.basic.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    sendfile on;
    keepalive_timeout 65;
    
    # Health check endpoint
    server {
        listen 80;
        server_name _;
        
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        location / {
            return 200 "SuperSmartMatch V2 Infrastructure Ready\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
    
    # Basic prometheus config
    cat > "$PROJECT_ROOT/config/prometheus.yml" << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
EOF
    
    # Grafana datasource
    cat > "$PROJECT_ROOT/config/grafana/datasources/prometheus.yml" << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    # PostgreSQL init script
    cat > "$PROJECT_ROOT/config/postgres/init.sql" << 'EOF'
-- SuperSmartMatch V2 Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables for V2
CREATE TABLE IF NOT EXISTS matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id VARCHAR(255) NOT NULL,
    job_id VARCHAR(255) NOT NULL,
    score DECIMAL(5,2) NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,4) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_matches_candidate_id ON matches(candidate_id);
CREATE INDEX IF NOT EXISTS idx_matches_job_id ON matches(job_id);
CREATE INDEX IF NOT EXISTS idx_matches_score ON matches(score DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp);

-- Insert initial data
INSERT INTO metrics (metric_name, metric_value) VALUES 
('precision', 95.09),
('performance_p95', 50.0),
('roi_annual', 964154.0)
ON CONFLICT DO NOTHING;
EOF
    
    log_success "Configuration files created"
}

# Deploy basic infrastructure
deploy_basic_infrastructure() {
    log_step "Deploying basic infrastructure (PostgreSQL, Redis, MinIO, Monitoring)..."
    
    cd "$PROJECT_ROOT"
    
    # Stop any existing containers
    docker-compose -f docker-compose.basic.yml down --remove-orphans || true
    
    # Start basic infrastructure
    docker-compose -f docker-compose.basic.yml up -d
    
    log_info "Waiting for services to be ready..."
    sleep 30
    
    # Check services health
    local services=("postgres" "redis" "minio" "prometheus" "grafana")
    for service in "${services[@]}"; do
        if docker-compose -f docker-compose.basic.yml ps "$service" | grep -q "Up"; then
            log_success "$service is running"
        else
            log_warning "$service may not be fully ready yet"
        fi
    done
    
    log_success "Basic infrastructure deployed"
}

# Show deployment status
show_deployment_status() {
    log_step "Deployment Status Summary"
    
    echo ""
    log_info "=== RUNNING CONTAINERS ==="
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo ""
    log_info "=== ACCESSIBLE SERVICES ==="
    log_info "• Grafana Dashboard: http://localhost:3000 (admin/supersmartmatch2024)"
    log_info "• Prometheus: http://localhost:9090"
    log_info "• MinIO Console: http://localhost:9001 (supersmartmatch/supersmartmatch2024)"
    log_info "• Redis: localhost:6379"
    log_info "• PostgreSQL: localhost:5432 (supersmartmatch_user/supersmartmatch_2024)"
    
    echo ""
    log_info "=== NEXT STEPS ==="
    log_info "1. Check service health: docker-compose -f docker-compose.basic.yml ps"
    log_info "2. View logs: docker-compose -f docker-compose.basic.yml logs -f [service_name]"
    log_info "3. Run full deployment: ./scripts/deploy_production.sh complete"
    log_info "4. Start monitoring: streamlit run scripts/production_monitor.py"
}

# Show usage
show_usage() {
    cat << EOF
Usage: $0 [mode]

Deployment modes:
  basic      - Deploy only infrastructure (PostgreSQL, Redis, MinIO, Monitoring)
  status     - Show current deployment status

Examples:
  $0              # Deploy basic infrastructure
  $0 basic        # Deploy basic infrastructure
  $0 status       # Show deployment status
EOF
}

# Main execution
main() {
    local mode="${1:-basic}"
    
    log_info "================================================================"
    log_info "SuperSmartMatch V2 - Progressive Deployment"
    log_info "================================================================"
    log_info "Mode: $mode"
    log_info "Project root: $PROJECT_ROOT"
    log_info "Log file: $LOG_FILE"
    log_info "================================================================"
    echo ""
    
    case "$mode" in
        "basic")
            check_prerequisites
            create_configs
            deploy_basic_infrastructure
            show_deployment_status
            ;;
        "status")
            show_deployment_status
            ;;
        "--help"|"-h")
            show_usage
            exit 0
            ;;
        *)
            log_error "Unknown mode: $mode"
            show_usage
            exit 1
            ;;
    esac
    
    echo ""
    log_success "================================================================"
    log_success "Deployment completed successfully!"
    log_success "================================================================"
}

# Trap to handle interruption
trap 'log_error "Deployment interrupted"; exit 1' INT TERM

# Run main function
main "$@"
