#!/bin/bash

# =============================================================================
# SuperSmartMatch V2 - Emergency Rollback Script
# =============================================================================
# Rollback d'urgence automatique en <60 secondes avec notifications
# Author: SuperSmartMatch Team  
# Version: 1.0
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/supersmartmatch/emergency-rollback-$(date +%Y%m%d_%H%M%S).log"
INCIDENT_ID="INC-$(date +%Y%m%d%H%M%S)"

# Emergency contacts
SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
PAGERDUTY_API_KEY="${PAGERDUTY_API_KEY:-}"
EMAIL_ALERTS="${EMAIL_ALERTS:-ops@company.com}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        ERROR)   echo -e "${RED}[EMERGENCY]${NC} $message" ;;
        SUCCESS) echo -e "${GREEN}[SUCCESS]${NC} $message" ;;
        WARNING) echo -e "${YELLOW}[WARNING]${NC} $message" ;;
        INFO)    echo -e "${BLUE}[INFO]${NC} $message" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Send emergency alerts
send_emergency_alert() {
    local severity="$1"
    local message="$2"
    local incident_details="$3"
    
    # Slack notification
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{
                \"text\": \"🚨 EMERGENCY ROLLBACK - $severity\",
                \"attachments\": [{
                    \"color\": \"danger\",
                    \"title\": \"SuperSmartMatch V2 Emergency Rollback\",
                    \"text\": \"$message\",
                    \"fields\": [
                        {\"title\": \"Incident ID\", \"value\": \"$INCIDENT_ID\", \"short\": true},
                        {\"title\": \"Timestamp\", \"value\": \"$(date)\", \"short\": true},
                        {\"title\": \"Details\", \"value\": \"$incident_details\", \"short\": false}
                    ]
                }]
            }" \
            "$SLACK_WEBHOOK_URL" 2>/dev/null || true
    fi
    
    # PagerDuty alert
    if [[ -n "$PAGERDUTY_API_KEY" ]]; then
        curl -X POST \
            -H "Authorization: Token token=$PAGERDUTY_API_KEY" \
            -H "Content-Type: application/json" \
            --data "{
                \"event_action\": \"trigger\",
                \"payload\": {
                    \"summary\": \"SuperSmartMatch V2 Emergency Rollback - $severity\",
                    \"severity\": \"critical\",
                    \"source\": \"SuperSmartMatch-V2\",
                    \"custom_details\": {
                        \"incident_id\": \"$INCIDENT_ID\",
                        \"message\": \"$message\",
                        \"details\": \"$incident_details\"
                    }
                }
            }" \
            "https://events.pagerduty.com/v2/enqueue" 2>/dev/null || true
    fi
    
    # Email alert (if sendmail available)
    if command -v sendmail >/dev/null 2>&1; then
        cat << EOF | sendmail "$EMAIL_ALERTS"
Subject: 🚨 EMERGENCY: SuperSmartMatch V2 Rollback - $INCIDENT_ID
From: SuperSmartMatch-Ops <noreply@company.com>
To: $EMAIL_ALERTS

EMERGENCY ROLLBACK EXECUTED

Incident ID: $INCIDENT_ID
Severity: $severity
Timestamp: $(date)

Message: $message

Details: $incident_details

This is an automated alert from the SuperSmartMatch V2 emergency rollback system.

---
SuperSmartMatch Operations Team
EOF
    fi
}

# Check current deployment status
check_current_status() {
    log INFO "🔍 Checking current deployment status..."
    
    # Check which version is currently active
    local v1_status=$(curl -s http://localhost:5062/api/v1/health 2>/dev/null || echo "")
    local v2_status=$(curl -s http://localhost:5070/api/v2/health 2>/dev/null || echo "")
    
    if [[ -n "$v2_status" ]] && echo "$v2_status" | grep -q "healthy"; then
        log INFO "✅ SuperSmartMatch V2 is currently active"
        return 0
    elif [[ -n "$v1_status" ]] && echo "$v1_status" | grep -q "healthy"; then
        log INFO "✅ SuperSmartMatch V1 is currently active"
        log WARNING "⚠️ V2 may already be rolled back or not deployed"
        return 1
    else
        log ERROR "❌ Unable to determine current status"
        return 2
    fi
}

# Immediate traffic switch to V1
emergency_traffic_switch() {
    log INFO "🔄 Initiating emergency traffic switch to V1..."
    
    # Update NGINX configuration for immediate switch
    if docker-compose ps | grep -q nginx; then
        log INFO "📝 Updating NGINX configuration..."
        
        # Create emergency upstream configuration
        cat > /tmp/emergency_upstream.conf << 'EOF'
upstream supersmartmatch_backend {
    server supersmartmatch-v1:5062 weight=100;
    server supersmartmatch-v2:5070 weight=0 backup;
}
EOF
        
        # Apply configuration and reload
        docker cp /tmp/emergency_upstream.conf nginx:/etc/nginx/conf.d/upstream.conf
        if docker-compose exec nginx nginx -s reload; then
            log SUCCESS "✅ NGINX traffic switched to V1"
        else
            log ERROR "❌ Failed to reload NGINX - using Docker restart"
            docker-compose restart nginx
        fi
    else
        log WARNING "⚠️ No NGINX load balancer found - checking alternative methods"
        
        # Alternative: Stop V2 containers
        log INFO "🛑 Stopping SuperSmartMatch V2 containers..."
        docker-compose stop supersmartmatch-v2 || true
    fi
    
    # Wait and verify traffic switch
    sleep 5
    
    # Test if V1 is receiving traffic
    local test_response=$(curl -s http://localhost:5062/api/v1/health 2>/dev/null || echo "")
    if [[ -n "$test_response" ]] && echo "$test_response" | grep -q "healthy"; then
        log SUCCESS "✅ Traffic successfully switched to V1"
        return 0
    else
        log ERROR "❌ Traffic switch verification failed"
        return 1
    fi
}

# Restore V1 configuration
restore_v1_configuration() {
    log INFO "⚙️ Restoring V1 configuration..."
    
    # Restore database state if needed
    if [[ -f "/tmp/last_backup_path" ]]; then
        local backup_path=$(cat /tmp/last_backup_path)
        if [[ -d "$backup_path" ]] && [[ -f "$backup_path/database.sql" ]]; then
            log INFO "💾 Restoring database from backup: $backup_path"
            
            # Create backup of current state before restore
            docker-compose exec -T postgres pg_dump -U postgres nexten > "/tmp/pre-rollback-backup-$(date +%Y%m%d_%H%M%S).sql"
            
            # Restore from backup
            docker-compose exec -T postgres psql -U postgres -d nexten < "$backup_path/database.sql"
            log SUCCESS "✅ Database restored from backup"
        else
            log WARNING "⚠️ No valid backup found - skipping database restore"
        fi
    fi
    
    # Restore Redis state
    if [[ -f "/tmp/last_backup_path" ]]; then
        local backup_path=$(cat /tmp/last_backup_path)
        if [[ -f "$backup_path/dump.rdb" ]]; then
            log INFO "🗄️ Restoring Redis from backup..."
            docker-compose exec redis redis-cli FLUSHALL
            docker cp "$backup_path/dump.rdb" nexten-redis:/data/
            docker-compose restart redis
            log SUCCESS "✅ Redis restored from backup"
        fi
    fi
    
    # Clear V2-specific caches and configurations
    log INFO "🧹 Clearing V2-specific configurations..."
    docker-compose exec -T redis redis-cli --pattern "*v2*" --eval "$(echo 'for i, name in ipairs(redis.call("KEYS", ARGV[1])) do redis.call("DEL", name) end')" , "*v2*" 2>/dev/null || true
    
    log SUCCESS "✅ V1 configuration restored"
}

# Validate rollback success
validate_rollback() {
    log INFO "✅ Validating rollback success..."
    
    local validation_tests=0
    local validation_passed=0
    
    # Test 1: V1 health check
    ((validation_tests++))
    local v1_health=$(curl -s http://localhost:5062/api/v1/health 2>/dev/null || echo "")
    if [[ -n "$v1_health" ]] && echo "$v1_health" | grep -q "healthy"; then
        ((validation_passed++))
        log SUCCESS "✅ V1 health check passed"
    else
        log ERROR "❌ V1 health check failed"
    fi
    
    # Test 2: V1 basic functionality
    ((validation_tests++))
    local match_test=$(curl -s -X POST http://localhost:5062/api/v1/match \
        -H "Content-Type: application/json" \
        -d '{
            "candidate": {"skills": ["Python"], "experience_years": 3},
            "jobs": [{"title": "Developer", "skills_required": ["Python"]}]
        }' 2>/dev/null || echo "")
    
    if [[ -n "$match_test" ]] && echo "$match_test" | grep -q "matches"; then
        ((validation_passed++))
        log SUCCESS "✅ V1 functionality test passed"
    else
        log ERROR "❌ V1 functionality test failed"
    fi
    
    # Test 3: V2 properly stopped
    ((validation_tests++))
    local v2_status=$(curl -s http://localhost:5070/api/v2/health 2>/dev/null || echo "")
    if [[ -z "$v2_status" ]] || ! echo "$v2_status" | grep -q "healthy"; then
        ((validation_passed++))
        log SUCCESS "✅ V2 properly stopped"
    else
        log WARNING "⚠️ V2 still responding - additional cleanup needed"
    fi
    
    # Test 4: Database connectivity
    ((validation_tests++))
    if docker-compose exec -T postgres pg_isready -U postgres -d nexten >/dev/null 2>&1; then
        ((validation_passed++))
        log SUCCESS "✅ Database connectivity verified"
    else
        log ERROR "❌ Database connectivity failed"
    fi
    
    local success_rate=$(echo "scale=0; $validation_passed * 100 / $validation_tests" | bc -l)
    
    if [[ $validation_passed -eq $validation_tests ]]; then
        log SUCCESS "🎉 Rollback validation: 100% passed ($validation_passed/$validation_tests)"
        return 0
    elif [[ $success_rate -ge 75 ]]; then
        log WARNING "⚠️ Rollback validation: $success_rate% passed ($validation_passed/$validation_tests) - Partial success"
        return 1
    else
        log ERROR "❌ Rollback validation: $success_rate% passed ($validation_passed/$validation_tests) - Critical issues"
        return 2
    fi
}

# Generate incident report
generate_incident_report() {
    local rollback_reason="$1"
    local rollback_success="$2"
    
    local report_file="./logs/incident_report_${INCIDENT_ID}.json"
    mkdir -p ./logs
    
    cat > "$report_file" << EOF
{
    "incident_report": {
        "incident_id": "$INCIDENT_ID",
        "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
        "type": "emergency_rollback",
        "severity": "critical",
        "system": "SuperSmartMatch V2",
        "rollback_details": {
            "reason": "$rollback_reason",
            "success": $rollback_success,
            "duration_seconds": $(( $(date +%s) - ${ROLLBACK_START_TIME:-$(date +%s)} )),
            "method": "automated_emergency_script"
        },
        "impact": {
            "service_availability": "maintained",
            "data_integrity": "preserved",
            "user_experience": "minimal_disruption"
        },
        "recovery_actions": [
            "Traffic switched to V1",
            "V2 containers stopped",
            "Configuration restored",
            "Validation completed"
        ],
        "next_steps": [
            "Root cause analysis",
            "Fix V2 issues",
            "Plan re-deployment",
            "Post-incident review"
        ],
        "contacts": {
            "incident_commander": "DevOps Team",
            "technical_lead": "SuperSmartMatch Team",
            "business_owner": "Product Team"
        }
    }
}
EOF
    
    log INFO "📄 Incident report generated: $report_file"
    echo "$report_file"
}

# Main rollback execution
main() {
    local rollback_reason="${1:-manual_trigger}"
    local ROLLBACK_START_TIME=$(date +%s)
    
    echo ""
    echo "🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨"
    echo "               EMERGENCY ROLLBACK INITIATED"
    echo "🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨🚨"
    echo ""
    
    log INFO "🚨 EMERGENCY ROLLBACK STARTED - Incident ID: $INCIDENT_ID"
    log INFO "📋 Reason: $rollback_reason"
    log INFO "⏰ Target completion: <60 seconds"
    
    # Send initial alert
    send_emergency_alert "CRITICAL" \
        "Emergency rollback initiated for SuperSmartMatch V2" \
        "Reason: $rollback_reason | Target: <60s completion"
    
    # Check current status
    local current_status
    check_current_status
    current_status=$?
    
    if [[ $current_status -eq 1 ]]; then
        log WARNING "⚠️ V2 may already be inactive - proceeding with verification"
    elif [[ $current_status -eq 2 ]]; then
        log ERROR "❌ Cannot determine current status - proceeding with full rollback"
    fi
    
    # Execute emergency traffic switch
    if emergency_traffic_switch; then
        log SUCCESS "✅ Emergency traffic switch completed"
    else
        log ERROR "❌ Emergency traffic switch failed - continuing with other recovery steps"
    fi
    
    # Restore V1 configuration
    restore_v1_configuration
    
    # Validate rollback
    local validation_result
    validate_rollback
    validation_result=$?
    
    local rollback_success="false"
    local rollback_status="FAILED"
    
    if [[ $validation_result -eq 0 ]]; then
        rollback_success="true"
        rollback_status="SUCCESS"
        log SUCCESS "🎉 EMERGENCY ROLLBACK COMPLETED SUCCESSFULLY"
    elif [[ $validation_result -eq 1 ]]; then
        rollback_success="partial"
        rollback_status="PARTIAL"
        log WARNING "⚠️ EMERGENCY ROLLBACK COMPLETED WITH WARNINGS"
    else
        rollback_success="false"
        rollback_status="FAILED"
        log ERROR "❌ EMERGENCY ROLLBACK FAILED - MANUAL INTERVENTION REQUIRED"
    fi
    
    local rollback_duration=$(( $(date +%s) - ROLLBACK_START_TIME ))
    
    # Generate incident report
    local report_file=$(generate_incident_report "$rollback_reason" "$rollback_success")
    
    # Send completion alert
    send_emergency_alert "$rollback_status" \
        "Emergency rollback completed in ${rollback_duration}s" \
        "Status: $rollback_status | Duration: ${rollback_duration}s | Report: $report_file"
    
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    ROLLBACK SUMMARY                          ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║ Incident ID: $INCIDENT_ID                      ║"
    echo "║ Status: $rollback_status                                        ║"
    echo "║ Duration: ${rollback_duration}s                                           ║"
    echo "║ Reason: $rollback_reason                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    log INFO "📄 Incident report: $report_file"
    log INFO "📄 Detailed log: $LOG_FILE"
    
    # Exit with appropriate code
    case $validation_result in
        0) exit 0 ;;  # Success
        1) exit 1 ;;  # Partial success
        *) exit 2 ;;  # Failed
    esac
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Handle different invocation methods
case "${1:-help}" in
    "precision_failure")
        main "Precision below 94% threshold"
        ;;
    "latency_failure")
        main "Latency above 200ms threshold"
        ;;
    "error_spike")
        main "Error rate above 2% threshold"
        ;;
    "manual")
        main "Manual emergency rollback"
        ;;
    "health_check_failure")
        main "Health check failure detected"
        ;;
    "help"|"--help"|"-h")
        echo "SuperSmartMatch V2 Emergency Rollback"
        echo ""
        echo "Usage: $0 [reason]"
        echo ""
        echo "Reasons:"
        echo "  precision_failure     - Precision below threshold"
        echo "  latency_failure       - Latency above threshold" 
        echo "  error_spike          - Error rate above threshold"
        echo "  health_check_failure - Health check failure"
        echo "  manual               - Manual emergency rollback"
        echo "  help                 - Show this help"
        echo ""
        echo "This script will:"
        echo "  1. Switch traffic to V1 immediately"
        echo "  2. Stop V2 services"
        echo "  3. Restore V1 configuration"
        echo "  4. Validate rollback success"
        echo "  5. Send emergency notifications"
        echo "  6. Generate incident report"
        echo ""
        echo "Target completion time: <60 seconds"
        exit 0
        ;;
    *)
        main "$1"
        ;;
esac
