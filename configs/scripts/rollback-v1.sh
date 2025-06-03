#!/bin/bash

# 🚨 SuperSmartMatch Emergency Rollback Script
# Automatic rollback to V1 with data restoration

set -euo pipefail

# Configuration
COMPOSE_FILE="configs/docker/docker-compose.production.yml"
LOG_FILE="/var/log/supersmartmatch/rollback-$(date +%Y%m%d_%H%M%S).log"
BACKUP_DIR=${1:-"/backups/latest"}  # Use provided backup or latest
ROLLBACK_REASON=${2:-"manual"}      # manual, automatic, or emergency

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

# Send alert notifications
send_alert() {
    local message="$1"
    local severity="$2"
    
    log "📢 Sending $severity alert: $message"
    
    # Slack notification (if webhook configured)
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"🚨 ROLLBACK ALERT: '"$message"'"}' \
            "$SLACK_WEBHOOK_URL" >/dev/null 2>&1 || true
    fi
    
    # Email notification (if configured)
    if command -v mail >/dev/null 2>&1 && [[ -n "${ALERT_EMAIL:-}" ]]; then
        echo "$message" | mail -s "🚨 SuperSmartMatch Rollback Alert" "$ALERT_EMAIL" || true
    fi
    
    # Log to monitoring system
    if command -v logger >/dev/null 2>&1; then
        logger -t "supersmartmatch-rollback" "$severity: $message"
    fi
}

# Pre-rollback validation
validate_rollback() {
    log "🔍 Validating rollback prerequisites..."
    
    # Check if backup directory exists
    if [[ ! -d "$BACKUP_DIR" ]]; then
        error "Backup directory not found: $BACKUP_DIR"
    fi
    
    # Check if required backup files exist
    local required_files=("redis-v1.rdb" "docker-state.txt")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$BACKUP_DIR/$file" ]]; then
            error "Required backup file not found: $BACKUP_DIR/$file"
        fi
    done
    
    # Check if V1 services are available
    if ! docker-compose -f "$COMPOSE_FILE" ps supersmartmatch-v1 | grep -q "Up"; then
        warning "V1 service is not running - will be started during rollback"
    fi
    
    success "Rollback validation passed"
}

# Stop V2 services immediately
stop_v2_services() {
    log "🛑 Stopping V2 services immediately..."
    
    # Stop V2 service
    docker-compose -f "$COMPOSE_FILE" stop supersmartmatch-v2 || true
    
    # Stop data sync service
    docker-compose -f "$COMPOSE_FILE" stop data-sync || true
    
    # Remove V2 from load balancer immediately
    switch_traffic_to_v1
    
    success "V2 services stopped"
}

# Switch all traffic to V1
switch_traffic_to_v1() {
    log "🔄 Switching all traffic to V1..."
    
    # Create emergency nginx configuration
    cat > /tmp/emergency-nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream supersmartmatch_v1_only {
        server supersmartmatch-v1:5062;
    }

    upstream nexten_only {
        server nexten:5052;
    }

    server {
        listen 80;
        
        # Health check
        location /health {
            return 200 "V1 Emergency Mode\n";
            add_header Content-Type text/plain;
        }
        
        # All API traffic to V1
        location /api/ {
            proxy_pass http://supersmartmatch_v1_only;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            add_header X-Service-Version "v1-rollback" always;
        }

        # Nexten traffic
        location /api/nexten/ {
            proxy_pass http://nexten_only;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF
    
    # Apply emergency configuration
    docker cp /tmp/emergency-nginx.conf nginx:/etc/nginx/nginx.conf
    
    # Test and reload nginx
    if docker exec nginx nginx -t >/dev/null 2>&1; then
        docker exec nginx nginx -s reload
        success "Traffic switched to V1 - Emergency mode active"
    else
        error "Failed to update nginx configuration"
    fi
}

# Restore data from backup
restore_data() {
    log "💾 Restoring data from backup..."
    
    # Stop Redis briefly for data restoration
    docker-compose -f "$COMPOSE_FILE" stop redis-master
    
    # Restore Redis data
    if [[ -f "$BACKUP_DIR/redis-v1.rdb" ]]; then
        log "Restoring Redis backup..."
        docker cp "$BACKUP_DIR/redis-v1.rdb" redis-master:/data/dump.rdb
        docker-compose -f "$COMPOSE_FILE" start redis-master
        
        # Wait for Redis to be available
        local max_attempts=30
        local attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            if docker exec redis-master redis-cli ping | grep -q PONG; then
                success "Redis restored and available"
                break
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                error "Redis failed to start after restoration"
            fi
            
            log "Waiting for Redis to be available... ($attempt/$max_attempts)"
            sleep 2
            ((attempt++))
        done
    else
        warning "No Redis backup found - starting with empty cache"
        docker-compose -f "$COMPOSE_FILE" start redis-master
    fi
    
    # Clear any V2-specific data
    log "Cleaning V2-specific data..."
    docker exec redis-master redis-cli --scan --pattern "*v2*" | while read -r key; do
        docker exec redis-master redis-cli DEL "$key" || true
    done
    
    success "Data restoration completed"
}

# Restart V1 services
restart_v1_services() {
    log "🔄 Restarting V1 services..."
    
    # Restart V1 services with fresh configuration
    docker-compose -f "$COMPOSE_FILE" restart supersmartmatch-v1 nexten
    
    # Wait for services to be healthy
    local services=("supersmartmatch-v1" "nexten")
    
    for service in "${services[@]}"; do
        log "Waiting for $service to be healthy..."
        local max_attempts=30
        local attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            local port
            case $service in
                "supersmartmatch-v1") port=5062 ;;
                "nexten") port=5052 ;;
            esac
            
            if curl -f "http://localhost:$port/health" >/dev/null 2>&1; then
                success "$service is healthy"
                break
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                error "$service failed to become healthy"
            fi
            
            log "$service not ready yet... ($attempt/$max_attempts)"
            sleep 5
            ((attempt++))
        done
    done
    
    success "V1 services restarted and healthy"
}

# Validate rollback success
validate_rollback_success() {
    log "✅ Validating rollback success..."
    
    # Test API endpoints
    local endpoints=(
        "http://localhost/api/v1/health"
        "http://localhost/api/nexten/health"
        "http://localhost/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if curl -f "$endpoint" >/dev/null 2>&1; then
            log "✓ $endpoint is responding"
        else
            error "✗ $endpoint is not responding"
        fi
    done
    
    # Check that V2 traffic is actually stopped
    local v2_response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5070/health || echo "000")
    if [[ "$v2_response" == "000" ]] || [[ "$v2_response" == "404" ]]; then
        log "✓ V2 service is properly stopped"
    else
        warning "V2 service might still be accessible"
    fi
    
    # Verify load balancer is routing correctly
    local response_header=$(curl -s -I http://localhost/api/health | grep -i "x-service-version" || echo "")
    if [[ "$response_header" == *"v1-rollback"* ]]; then
        log "✓ Load balancer is routing to V1"
    else
        warning "Load balancer routing might not be correct"
    fi
    
    # Check Redis connectivity
    if docker exec redis-master redis-cli ping | grep -q PONG; then
        log "✓ Redis is responding"
    else
        error "✗ Redis is not responding"
    fi
    
    success "Rollback validation completed successfully"
}

# Monitor post-rollback metrics
monitor_post_rollback() {
    log "📊 Monitoring post-rollback metrics for 3 minutes..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + 180))  # 3 minutes
    
    while [[ $(date +%s) -lt $end_time ]]; do
        # Check error rates
        local v1_errors=$(curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{version=\"v1\",status=~\"5..\"}[1m])" | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")
        
        # Check response times
        local v1_response_time=$(curl -s "http://localhost:9090/api/v1/query?query=histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{version=\"v1\"}[1m]))" | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")
        
        # Check request rate
        local request_rate=$(curl -s "http://localhost:9090/api/v1/query?query=rate(http_requests_total{version=\"v1\"}[1m])" | jq -r '.data.result[0].value[1] // "0"' 2>/dev/null || echo "0")
        
        log "Post-rollback metrics - Errors: $v1_errors, P95: ${v1_response_time}s, Rate: $request_rate req/s"
        
        sleep 30
    done
    
    success "Post-rollback monitoring completed"
}

# Generate rollback report
generate_rollback_report() {
    log "📋 Generating rollback report..."
    
    local report_file="/tmp/rollback-report-$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
🚨 SuperSmartMatch V2 Rollback Report
===================================

Rollback Time: $(date)
Rollback Reason: $ROLLBACK_REASON
Backup Used: $BACKUP_DIR
Total Rollback Duration: $(( $(date +%s) - rollback_start_time )) seconds

Services Status After Rollback:
$(docker-compose -f "$COMPOSE_FILE" ps)

Health Checks:
- V1 API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5062/health)
- Nexten API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5052/health)
- Load Balancer: $(curl -s -o /dev/null -w "%{http_code}" http://localhost/health)
- Redis: $(docker exec redis-master redis-cli ping 2>/dev/null || echo "FAILED")

V2 Services (Should be stopped):
- V2 API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:5070/health 2>/dev/null || echo "STOPPED")
- Data Sync: $(docker-compose -f "$COMPOSE_FILE" ps data-sync | grep -q "Exit" && echo "STOPPED" || echo "RUNNING")

Traffic Routing:
- All traffic is now routed to V1 (emergency mode)
- V2 service is stopped and isolated
- Load balancer configured for V1-only

Actions Taken:
1. V2 services stopped immediately
2. Traffic switched to V1 emergency mode  
3. Data restored from backup: $BACKUP_DIR
4. V1 services restarted and validated
5. Post-rollback monitoring completed

Next Steps:
1. Investigate root cause of rollback
2. Review logs: docker-compose -f $COMPOSE_FILE logs
3. Monitor dashboards: http://localhost:3000
4. Plan V2 fixes and re-deployment
5. Consider gradual re-introduction when ready

IMPORTANT: System is now in V1-only emergency mode.
All V2 improvements are temporarily unavailable.
EOF
    
    cat "$report_file"
    success "Rollback report saved to $report_file"
}

# Main rollback function
main() {
    local rollback_start_time=$(date +%s)
    
    log "🚨 EMERGENCY ROLLBACK INITIATED - Reason: $ROLLBACK_REASON"
    send_alert "Emergency rollback initiated - Reason: $ROLLBACK_REASON" "CRITICAL"
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Trap to ensure notifications on error
    trap 'send_alert "Rollback failed! Manual intervention required." "CRITICAL"' ERR
    
    validate_rollback
    stop_v2_services
    restore_data
    restart_v1_services
    validate_rollback_success
    monitor_post_rollback
    generate_rollback_report
    
    local rollback_duration=$(($(date +%s) - rollback_start_time))
    
    success "🎯 ROLLBACK COMPLETED SUCCESSFULLY in ${rollback_duration} seconds"
    send_alert "Rollback completed successfully in ${rollback_duration}s. System stable on V1." "INFO"
    
    log "📊 Monitor system: http://localhost:3000"
    log "🔍 Check logs: docker-compose -f $COMPOSE_FILE logs"
    log "📧 Report saved: Check /tmp/rollback-report-*.txt"
}

# Script usage
usage() {
    echo "Usage: $0 [backup_directory] [rollback_reason]"
    echo "  backup_directory: Path to backup (default: /backups/latest)"
    echo "  rollback_reason: Reason for rollback (default: manual)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use latest backup, manual reason"
    echo "  $0 /backups/20250603_150000           # Use specific backup"
    echo "  $0 /backups/latest performance_issue  # Specific reason"
    echo ""
    echo "Environment Variables:"
    echo "  SLACK_WEBHOOK_URL  - Slack webhook for notifications"
    echo "  ALERT_EMAIL        - Email address for alerts"
    exit 1
}

# Confirmation for manual rollbacks
if [[ "$ROLLBACK_REASON" == "manual" ]] && [[ -t 0 ]]; then
    echo "⚠️  WARNING: You are about to rollback SuperSmartMatch V2 to V1"
    echo "This will:"
    echo "  - Stop all V2 services immediately"
    echo "  - Switch all traffic to V1"
    echo "  - Restore data from backup: $BACKUP_DIR"
    echo "  - Put system in emergency V1-only mode"
    echo ""
    read -p "Are you sure you want to proceed? (yes/no): " confirm
    if [[ "$confirm" != "yes" ]]; then
        echo "Rollback cancelled."
        exit 0
    fi
fi

# Check if running as root or with docker permissions
if ! docker ps >/dev/null 2>&1; then
    error "Docker access denied. Please run with appropriate permissions."
fi

# Run main function
main "$@"