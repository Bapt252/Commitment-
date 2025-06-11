#!/bin/bash

# 🚀 SuperSmartMatch V2 Deployment Script
# Production-ready deployment with zero-downtime migration

set -euo pipefail

# Configuration
COMPOSE_FILE="configs/docker/docker-compose.production.yml"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="./logs/deployment-$(date +%Y%m%d_%H%M%S).log"
ROLLOUT_PERCENTAGE=${1:-10}  # Default 10% traffic

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Pre-deployment validation
validate_environment() {
    log "🔍 Pre-deployment validation..."
    
    # Check if required files exist
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
    fi
    
    # Validate docker-compose syntax
    log "Validating Docker Compose configuration..."
    if ! docker-compose -f "$COMPOSE_FILE" config >/dev/null 2>&1; then
        error "Invalid Docker Compose configuration"
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 10485760 ]]; then  # 10GB in KB
        error "Insufficient disk space. Minimum 10GB required."
    fi
    
    # Check if required environment variables are set
    if [[ -z "${GRAFANA_ADMIN_PASSWORD:-}" ]]; then
        warning "GRAFANA_ADMIN_PASSWORD not set. Using default password."
        export GRAFANA_ADMIN_PASSWORD="secure_admin_password_change_me"
    fi
    
    # Test external dependencies
    log "Testing external dependencies..."
    if ! ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        error "No internet connectivity detected"
    fi
    
    success "Pre-deployment validation passed"
}

# Create backup of current state
create_backup() {
    log "💾 Creating backup of current state..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Backup Redis data
    if docker ps | grep -q redis-master; then
        log "Backing up Redis data..."
        docker exec redis-master redis-cli BGSAVE
        sleep 5  # Wait for background save to complete
        docker cp redis-master:/data/dump.rdb "$BACKUP_DIR/redis-v1.rdb"
    fi
    
    # Backup current configuration
    log "Backing up configuration files..."
    cp -r configs/ "$BACKUP_DIR/"
    
    # Export current docker-compose state
    if docker-compose -f "$COMPOSE_FILE" ps >/dev/null 2>&1; then
        docker-compose -f "$COMPOSE_FILE" ps > "$BACKUP_DIR/docker-state.txt"
    fi
    
    # Create rollback script
    cat > "$BACKUP_DIR/rollback.sh" << 'EOF'
#!/bin/bash
echo "🚨 Executing emergency rollback..."
cd "$(dirname "$0")"
docker-compose -f ../../configs/docker/docker-compose.production.yml stop supersmartmatch-v2
docker cp redis-v1.rdb redis-master:/data/dump.rdb
docker restart redis-master
docker-compose -f ../../configs/docker/docker-compose.production.yml restart supersmartmatch-v1 nexten
echo "✅ Rollback completed"
EOF
    chmod +x "$BACKUP_DIR/rollback.sh"
    
    success "Backup created in $BACKUP_DIR"
}

# Deploy V2 service
deploy_v2() {
    log "🚀 Deploying SuperSmartMatch V2..."
    
    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" pull supersmartmatch-v2 data-sync
    
    # Start data sync service first
    log "Starting data synchronization service..."
    docker-compose -f "$COMPOSE_FILE" up -d data-sync
    
    # Wait for data sync to initialize
    sleep 10
    
    # Deploy V2 service
    log "Starting SuperSmartMatch V2 service..."
    docker-compose -f "$COMPOSE_FILE" up -d supersmartmatch-v2
    
    # Wait for service to be ready
    log "Waiting for V2 service health check..."
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost:5070/health >/dev/null 2>&1; then
            success "V2 service is healthy"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            error "V2 service failed to start after $max_attempts attempts"
        fi
        
        log "Attempt $attempt/$max_attempts - V2 service not ready yet..."
        sleep 10
        ((attempt++))
    done
}

# Update load balancer configuration
update_load_balancer() {
    log "🔄 Updating load balancer for $ROLLOUT_PERCENTAGE% traffic..."
    
    # Create dynamic nginx configuration based on rollout percentage
    local v2_weight=$((ROLLOUT_PERCENTAGE))
    local v1_weight=$((100 - ROLLOUT_PERCENTAGE))
    
    # Generate nginx upstream configuration
    cat > /tmp/nginx-upstream.conf << EOF
upstream supersmartmatch_weighted {
    server supersmartmatch-v1:5062 weight=$v1_weight max_fails=3 fail_timeout=30s;
    server supersmartmatch-v2:5070 weight=$v2_weight max_fails=3 fail_timeout=30s;
}
EOF
    
    # Update nginx configuration
    docker cp /tmp/nginx-upstream.conf nginx:/etc/nginx/conf.d/upstream.conf
    
    # Reload nginx configuration
    if docker exec nginx nginx -t >/dev/null 2>&1; then
        docker exec nginx nginx -s reload
        success "Load balancer updated - $ROLLOUT_PERCENTAGE% traffic to V2"
    else
        error "Nginx configuration test failed"
    fi
}

# Validate deployment
validate_deployment() {
    log "✅ Validating deployment..."
    
    # Check service health
    local services=("supersmartmatch-v1" "supersmartmatch-v2" "nexten" "nginx" "redis-master")
    
    for service in "${services[@]}"; do
        if ! docker ps | grep -q "$service"; then
            error "Service $service is not running"
        fi
        log "✓ $service is running"
    done
    
    # Test API endpoints
    log "Testing API endpoints..."
    
    # Test V1 endpoint
    if curl -f http://localhost/api/v1/health >/dev/null 2>&1; then
        log "✓ V1 API is responding"
    else
        warning "V1 API is not responding"
    fi
    
    # Test V2 endpoint
    if curl -f http://localhost/api/v2/health >/dev/null 2>&1; then
        log "✓ V2 API is responding"
    else
        warning "V2 API is not responding"
    fi
    
    # Test feature flag routing
    response=$(curl -s -H "X-Feature-Flag: v2_enabled" http://localhost/api/match/health)
    if [[ "$response" == *"v2"* ]]; then
        log "✓ Feature flag routing is working"
    else
        warning "Feature flag routing may not be working correctly"
    fi
    
    # Check monitoring
    if curl -f http://localhost:3000/api/health >/dev/null 2>&1; then
        log "✓ Grafana is accessible"
    else
        warning "Grafana is not accessible"
    fi
    
    if curl -f http://localhost:9090/-/healthy >/dev/null 2>&1; then
        log "✓ Prometheus is healthy"
    else
        warning "Prometheus is not healthy"
    fi
    
    success "Deployment validation completed"
}

# Monitor initial metrics
monitor_initial_metrics() {
    log "📊 Monitoring initial metrics for 5 minutes..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + 300))  # 5 minutes
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check error rates
        local v1_errors=$(curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{version=\"v1\",status=~\"5..\"}[1m])" | jq -r '.data.result[0].value[1] // "0"')
        local v2_errors=$(curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{version=\"v2\",status=~\"5..\"}[1m])" | jq -r '.data.result[0].value[1] // "0"')
        
        # Check response times
        local v1_response_time=$(curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{version=\"v1\"}[1m]))" | jq -r '.data.result[0].value[1] // "0"')
        local v2_response_time=$(curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{version=\"v2\"}[1m]))" | jq -r '.data.result[0].value[1] // "0"')
        
        log "Metrics - V1 errors: $v1_errors, V2 errors: $v2_errors, V1 p95: ${v1_response_time}s, V2 p95: ${v2_response_time}s"
        
        # Check for critical thresholds
        if (( $(echo "$v2_errors > 0.05" | bc -l) )); then
            error "V2 error rate too high: $v2_errors"
        fi
        
        if (( $(echo "$v2_response_time > 0.15" | bc -l) )); then
            error "V2 response time too high: ${v2_response_time}s"
        fi
        
        sleep 60
    done
    
    success "Initial monitoring period completed successfully"
}

# Generate deployment report
generate_report() {
    log "📋 Generating deployment report..."
    
    local report_file="/tmp/deployment-report-$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
🚀 SuperSmartMatch V2 Deployment Report
=====================================

Deployment Time: $(date)
Rollout Percentage: $ROLLOUT_PERCENTAGE%
Backup Location: $BACKUP_DIR

Services Status:
$(docker-compose -f "$COMPOSE_FILE" ps)

Health Checks:
- V1 API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5062/health)
- V2 API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5070/health)
- Nginx: $(curl -s -o /dev/null -w "%{http_code}" http://localhost/health)
- Grafana: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/health)
- Prometheus: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:9090/-/healthy)

Next Steps:
1. Monitor dashboards: http://localhost:3000
2. Check metrics: http://localhost:9090
3. Review logs: docker-compose -f $COMPOSE_FILE logs -f
4. Increase traffic: ./deploy-v2.sh 25
5. Emergency rollback: $BACKUP_DIR/rollback.sh

EOF
    
    cat "$report_file"
    success "Deployment report saved to $report_file"
}

# Main deployment function
main() {
    log "🚀 Starting SuperSmartMatch V2 Deployment (${ROLLOUT_PERCENTAGE}% traffic)"
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Trap to ensure cleanup on error
    trap 'error "Deployment failed! Check log: $LOG_FILE"' ERR
    
    validate_environment
    create_backup
    deploy_v2
    update_load_balancer
    validate_deployment
    monitor_initial_metrics
    generate_report
    
    success "🎉 Deployment completed successfully!"
    log "📊 Monitor your deployment at http://localhost:3000"
    log "🔍 Prometheus metrics at http://localhost:9090"
    log "📧 Emergency rollback: $BACKUP_DIR/rollback.sh"
}

# Script usage
usage() {
    echo "Usage: $0 [rollout_percentage]"
    echo "  rollout_percentage: Percentage of traffic to route to V2 (default: 10)"
    echo "Examples:"
    echo "  $0 10    # Route 10% traffic to V2"
    echo "  $0 25    # Route 25% traffic to V2"
    echo "  $0 100   # Route 100% traffic to V2"
    exit 1
}

# Validate rollout percentage
if [[ ! "$ROLLOUT_PERCENTAGE" =~ ^[0-9]+$ ]] || [[ "$ROLLOUT_PERCENTAGE" -lt 0 ]] || [[ "$ROLLOUT_PERCENTAGE" -gt 100 ]]; then
    echo "Error: Rollout percentage must be a number between 0 and 100"
    usage
fi

# Check if running as root or with docker permissions
if ! docker ps >/dev/null 2>&1; then
    error "Docker access denied. Please run with appropriate permissions."
fi

# Run main function
main "$@"