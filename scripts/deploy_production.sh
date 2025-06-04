#!/bin/bash

# =============================================================================
# SuperSmartMatch V2 - Production Deployment Manager
# =============================================================================
# Déploiement progressif sécurisé avec rollback automatique
# Author: SuperSmartMatch Team
# Version: 1.0
# =============================================================================

set -euo pipefail

# Configuration
DEPLOYMENT_VERSION="v2.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/supersmartmatch/deployment-$(date +%Y%m%d_%H%M%S).log"
METRICS_ENDPOINT="http://localhost:3001/metrics"
ROLLBACK_THRESHOLD_PRECISION=94.0
ROLLBACK_THRESHOLD_LATENCY=200
ROLLBACK_THRESHOLD_ERROR_RATE=2.0

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        ERROR)   echo -e "${RED}[ERROR]${NC} $message" ;;
        SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        WARNING) echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        INFO)    echo -e "${BLUE}[INFO]${NC} $message" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Pre-deployment checks
pre_deployment_check() {
    log INFO "🔍 Running pre-deployment checks..."
    
    # Check if services are healthy
    local services=("postgres" "redis" "storage" "api")
    for service in "${services[@]}"; do
        if ! docker-compose ps | grep -q "$service.*Up"; then
            log ERROR "❌ Service $service is not running"
            return 1
        fi
    done
    
    # Check resource availability
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        log WARNING "⚠️ High CPU usage: ${cpu_usage}%"
    fi
    
    # Check disk space
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 85 ]]; then
        log ERROR "❌ Insufficient disk space: ${disk_usage}%"
        return 1
    fi
    
    # Validate PROMPT 5 compliance
    log INFO "🏆 Validating PROMPT 5 compliance..."
    local compliance_score=$(curl -s "$METRICS_ENDPOINT/prompt5" | jq -r '.compliance_score')
    if (( $(echo "$compliance_score < 100" | bc -l) )); then
        log ERROR "❌ PROMPT 5 compliance not met: ${compliance_score}%"
        return 1
    fi
    
    log SUCCESS "✅ All pre-deployment checks passed"
    return 0
}

# Backup current state
backup_current_state() {
    log INFO "💾 Creating backup of current state..."
    
    local backup_dir="/backup/supersmartmatch/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Database backup
    docker-compose exec -T postgres pg_dump -U postgres nexten > "$backup_dir/database.sql"
    
    # Configuration backup
    cp -r . "$backup_dir/config"
    
    # Redis backup
    docker-compose exec -T redis redis-cli BGSAVE
    docker cp nexten-redis:/data/dump.rdb "$backup_dir/"
    
    log SUCCESS "✅ Backup created: $backup_dir"
    echo "$backup_dir" > /tmp/last_backup_path
}

# Deploy with traffic percentage
deploy_with_traffic() {
    local traffic_percentage=$1
    local phase_name=$2
    local duration_hours=$3
    
    log INFO "🚀 Starting $phase_name deployment ($traffic_percentage% traffic)"
    
    # Update load balancer configuration
    cat > /tmp/nginx_upstream.conf << EOF
upstream supersmartmatch_backend {
    server supersmartmatch-v1:5062 weight=$((100 - traffic_percentage));
    server supersmartmatch-v2:5070 weight=$traffic_percentage;
}
EOF
    
    # Reload NGINX
    docker-compose exec nginx nginx -s reload
    
    # Monitor deployment
    local end_time=$(($(date +%s) + duration_hours * 3600))
    
    while [[ $(date +%s) -lt $end_time ]]; do
        if ! check_health_metrics; then
            log ERROR "❌ Health metrics failed, initiating rollback"
            emergency_rollback
            return 1
        fi
        
        log INFO "📊 Deployment monitoring... $(date)"
        sleep 300  # Check every 5 minutes
    done
    
    log SUCCESS "✅ $phase_name deployment completed successfully"
    return 0
}

# Check health metrics
check_health_metrics() {
    local metrics=$(curl -s "$METRICS_ENDPOINT/health" | jq -r '.')
    
    local precision=$(echo "$metrics" | jq -r '.precision')
    local latency_p95=$(echo "$metrics" | jq -r '.latency_p95')
    local error_rate=$(echo "$metrics" | jq -r '.error_rate')
    local uptime=$(echo "$metrics" | jq -r '.uptime')
    
    log INFO "📈 Current metrics: Precision=${precision}%, Latency=${latency_p95}ms, Error=${error_rate}%, Uptime=${uptime}%"
    
    # Check rollback conditions
    if (( $(echo "$precision < $ROLLBACK_THRESHOLD_PRECISION" | bc -l) )); then
        log ERROR "❌ Precision below threshold: ${precision}% < ${ROLLBACK_THRESHOLD_PRECISION}%"
        return 1
    fi
    
    if (( $(echo "$latency_p95 > $ROLLBACK_THRESHOLD_LATENCY" | bc -l) )); then
        log ERROR "❌ Latency above threshold: ${latency_p95}ms > ${ROLLBACK_THRESHOLD_LATENCY}ms"
        return 1
    fi
    
    if (( $(echo "$error_rate > $ROLLBACK_THRESHOLD_ERROR_RATE" | bc -l) )); then
        log ERROR "❌ Error rate above threshold: ${error_rate}% > ${ROLLBACK_THRESHOLD_ERROR_RATE}%"
        return 1
    fi
    
    return 0
}

# Emergency rollback
emergency_rollback() {
    log WARNING "🔄 Initiating emergency rollback to V1..."
    
    # Immediate traffic switch to V1
    cat > /tmp/nginx_upstream.conf << EOF
upstream supersmartmatch_backend {
    server supersmartmatch-v1:5062 weight=100;
    server supersmartmatch-v2:5070 weight=0;
}
EOF
    
    docker-compose exec nginx nginx -s reload
    
    # Send alerts
    send_alert "CRITICAL" "SuperSmartMatch V2 deployment rolled back automatically"
    
    log SUCCESS "✅ Emergency rollback completed in <60 seconds"
}

# Send alert notifications
send_alert() {
    local severity=$1
    local message=$2
    
    # Slack notification
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"[$severity] $message\"}" \
        "$SLACK_WEBHOOK_URL" 2>/dev/null || true
    
    # PagerDuty notification for critical alerts
    if [[ "$severity" == "CRITICAL" ]]; then
        curl -X POST \
            -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
            -H "Content-Type: application/json" \
            --data "{\"event_action\":\"trigger\",\"payload\":{\"summary\":\"$message\",\"severity\":\"critical\"}}" \
            "https://events.pagerduty.com/v2/enqueue" 2>/dev/null || true
    fi
}

# Validate business metrics
validate_business_metrics() {
    log INFO "💰 Validating business metrics..."
    
    local business_metrics=$(curl -s "$METRICS_ENDPOINT/business" | jq -r '.')
    local roi_annual=$(echo "$business_metrics" | jq -r '.roi_annual')
    local conversion_rate=$(echo "$business_metrics" | jq -r '.conversion_rate')
    local user_satisfaction=$(echo "$business_metrics" | jq -r '.user_satisfaction')
    
    log INFO "💼 Business Metrics: ROI=€${roi_annual}, Conversion=${conversion_rate}%, Satisfaction=${user_satisfaction}%"
    
    # Validate ROI target
    if (( $(echo "$roi_annual < 175000" | bc -l) )); then
        log WARNING "⚠️ ROI below minimum target: €${roi_annual} < €175,000"
    fi
    
    log SUCCESS "✅ Business metrics validation completed"
}

# Main deployment orchestrator
main() {
    local action=${1:-"help"}
    
    case $action in
        "check")
            pre_deployment_check
            ;;
        "backup")
            backup_current_state
            ;;
        "canary")
            pre_deployment_check || exit 1
            backup_current_state
            deploy_with_traffic 5 "Canary" 2
            ;;
        "extended")
            check_health_metrics || exit 1
            deploy_with_traffic 25 "Extended" 6
            validate_business_metrics
            ;;
        "full")
            check_health_metrics || exit 1
            deploy_with_traffic 100 "Full Production" 4
            validate_business_metrics
            ;;
        "rollback")
            emergency_rollback
            ;;
        "status")
            check_health_metrics
            validate_business_metrics
            ;;
        "complete")
            log INFO "🎯 Starting complete progressive deployment..."
            pre_deployment_check || exit 1
            backup_current_state
            
            # Phase 1: Canary
            deploy_with_traffic 5 "Canary" 2 || exit 1
            
            # Phase 2: Extended
            deploy_with_traffic 25 "Extended" 6 || exit 1
            validate_business_metrics
            
            # Phase 3: Full
            deploy_with_traffic 100 "Full Production" 4 || exit 1
            validate_business_metrics
            
            log SUCCESS "🎉 Complete progressive deployment finished successfully!"
            send_alert "INFO" "SuperSmartMatch V2 deployment completed successfully"
            ;;
        *)
            echo "Usage: $0 {check|backup|canary|extended|full|rollback|status|complete}"
            echo ""
            echo "Commands:"
            echo "  check     - Run pre-deployment checks"
            echo "  backup    - Create backup of current state"
            echo "  canary    - Deploy with 5% traffic (2h)"
            echo "  extended  - Deploy with 25% traffic (6h)"
            echo "  full      - Deploy with 100% traffic (4h)"
            echo "  rollback  - Emergency rollback to V1"
            echo "  status    - Check current health metrics"
            echo "  complete  - Run full progressive deployment"
            exit 1
            ;;
    esac
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"
