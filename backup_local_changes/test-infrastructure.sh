#!/bin/bash

# =============================================================================
# SuperSmartMatch V2 - Infrastructure Testing Suite
# =============================================================================
# Tests complets d'infrastructure avant et après déploiement
# Author: SuperSmartMatch Team
# Version: 1.0
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="/var/log/supersmartmatch/infrastructure-test-$(date +%Y%m%d_%H%M%S).log"
TEST_TIMEOUT=30
MAX_RETRIES=3

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Test results tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        ERROR)   echo -e "${RED}[FAIL]${NC} $message" ;;
        SUCCESS) echo -e "${GREEN}[PASS]${NC} $message" ;;
        WARNING) echo -e "${YELLOW}[WARN]${NC} $message" ;;
        INFO)    echo -e "${BLUE}[INFO]${NC} $message" ;;
        TEST)    echo -e "${PURPLE}[TEST]${NC} $message" ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Test function wrapper
run_test() {
    local test_name="$1"
    local test_function="$2"
    
    ((TOTAL_TESTS++))
    log TEST "Running: $test_name"
    
    if $test_function; then
        ((PASSED_TESTS++))
        log SUCCESS "$test_name"
        return 0
    else
        ((FAILED_TESTS++))
        log ERROR "$test_name"
        return 1
    fi
}

# Test Docker services
test_docker_services() {
    local required_services=("postgres" "redis" "storage" "api")
    
    for service in "${required_services[@]}"; do
        if ! docker-compose ps | grep -q "$service.*Up"; then
            log ERROR "Service $service is not running"
            return 1
        fi
    done
    
    # Test Docker Compose version compatibility
    local compose_version=$(docker-compose version --short)
    log INFO "Docker Compose version: $compose_version"
    
    return 0
}

# Test database connectivity and performance
test_database() {
    local db_host="localhost"
    local db_port="5432"
    local db_name="nexten"
    local db_user="postgres"
    
    # Connection test
    if ! timeout $TEST_TIMEOUT docker-compose exec -T postgres pg_isready -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name"; then
        return 1
    fi
    
    # Performance test - simple query
    local start_time=$(date +%s%N)
    docker-compose exec -T postgres psql -U "$db_user" -d "$db_name" -c "SELECT COUNT(*) FROM information_schema.tables;" > /dev/null
    local end_time=$(date +%s%N)
    local query_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [[ $query_time -gt 1000 ]]; then  # 1 second threshold
        log WARNING "Database query took ${query_time}ms (>1000ms)"
    else
        log INFO "Database query time: ${query_time}ms"
    fi
    
    # Test database size and connections
    local db_size=$(docker-compose exec -T postgres psql -U "$db_user" -d "$db_name" -t -c "SELECT pg_size_pretty(pg_database_size('$db_name'));")
    local active_connections=$(docker-compose exec -T postgres psql -U "$db_user" -d "$db_name" -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';")
    
    log INFO "Database size: $db_size"
    log INFO "Active connections: $active_connections"
    
    return 0
}

# Test Redis connectivity and performance
test_redis() {
    # Connection test
    if ! timeout $TEST_TIMEOUT docker-compose exec -T redis redis-cli ping | grep -q "PONG"; then
        return 1
    fi
    
    # Performance test - set/get operations
    local start_time=$(date +%s%N)
    docker-compose exec -T redis redis-cli set test_key test_value > /dev/null
    docker-compose exec -T redis redis-cli get test_key > /dev/null
    docker-compose exec -T redis redis-cli del test_key > /dev/null
    local end_time=$(date +%s%N)
    local operation_time=$(( (end_time - start_time) / 1000000 ))
    
    log INFO "Redis operation time: ${operation_time}ms"
    
    # Test Redis memory usage
    local memory_usage=$(docker-compose exec -T redis redis-cli info memory | grep "used_memory_human" | cut -d: -f2 | tr -d '\r')
    local max_memory=$(docker-compose exec -T redis redis-cli config get maxmemory | tail -1 | tr -d '\r')
    
    log INFO "Redis memory usage: $memory_usage"
    log INFO "Redis max memory: $max_memory"
    
    return 0
}

# Test MinIO storage
test_storage() {
    local storage_endpoint="http://localhost:9000"
    
    # Health check
    if ! timeout $TEST_TIMEOUT curl -f "$storage_endpoint/minio/health/live" > /dev/null 2>&1; then
        return 1
    fi
    
    # Test bucket operations (requires mc client)
    if command -v mc >/dev/null 2>&1; then
        log INFO "Testing MinIO bucket operations..."
        # Note: This would require MinIO client configuration
        # mc alias set local http://localhost:9000 minioadmin minioadmin
        # mc ls local/
    else
        log WARNING "MinIO client (mc) not available for advanced testing"
    fi
    
    return 0
}

# Test SuperSmartMatch V1 service
test_supersmartmatch_v1() {
    local v1_endpoint="http://localhost:5062"
    
    # Health check
    if ! timeout $TEST_TIMEOUT curl -f "$v1_endpoint/api/v1/health" > /dev/null 2>&1; then
        return 1
    fi
    
    # Performance test
    local start_time=$(date +%s%N)
    local response=$(curl -s -X POST "$v1_endpoint/api/v1/match" \
        -H "Content-Type: application/json" \
        -d '{
            "candidate": {
                "skills": ["Python", "JavaScript"],
                "experience_years": 3,
                "location": "Paris"
            },
            "jobs": [{
                "title": "Developer",
                "skills_required": ["Python", "React"],
                "location": "Paris",
                "experience_required": 2
            }]
        }' 2>/dev/null)
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    log INFO "SuperSmartMatch V1 response time: ${response_time}ms"
    
    # Validate response format
    if echo "$response" | jq -e '.matches' > /dev/null 2>&1; then
        log INFO "SuperSmartMatch V1 response format valid"
        return 0
    else
        log ERROR "SuperSmartMatch V1 response format invalid"
        return 1
    fi
}

# Test SuperSmartMatch V2 service
test_supersmartmatch_v2() {
    local v2_endpoint="http://localhost:5070"
    
    # Health check
    if ! timeout $TEST_TIMEOUT curl -f "$v2_endpoint/api/v2/health" > /dev/null 2>&1; then
        log WARNING "SuperSmartMatch V2 not available (expected if not deployed yet)"
        return 0  # Don't fail if V2 is not deployed yet
    fi
    
    # Performance test
    local start_time=$(date +%s%N)
    local response=$(curl -s -X POST "$v2_endpoint/api/v2/match" \
        -H "Content-Type: application/json" \
        -d '{
            "candidate": {
                "skills": ["Python", "JavaScript"],
                "experience_years": 3,
                "location": "Paris"
            },
            "jobs": [{
                "title": "Developer",
                "skills_required": ["Python", "React"],
                "location": "Paris",
                "experience_required": 2
            }]
        }' 2>/dev/null)
    local end_time=$(date +%s%N)
    local response_time=$(( (end_time - start_time) / 1000000 ))
    
    log INFO "SuperSmartMatch V2 response time: ${response_time}ms"
    
    # Validate response format and new V2 features
    if echo "$response" | jq -e '.matches' > /dev/null 2>&1; then
        # Check for V2-specific fields
        if echo "$response" | jq -e '.metadata.prompt5_compliance' > /dev/null 2>&1; then
            log INFO "SuperSmartMatch V2 PROMPT 5 compliance detected"
        fi
        
        log INFO "SuperSmartMatch V2 response format valid"
        return 0
    else
        log ERROR "SuperSmartMatch V2 response format invalid"
        return 1
    fi
}

# Test network connectivity
test_network() {
    local services=("postgres:5432" "redis:6379" "storage:9000")
    
    for service in "${services[@]}"; do
        local host=$(echo $service | cut -d: -f1)
        local port=$(echo $service | cut -d: -f2)
        
        if ! timeout 5 docker-compose exec -T api nc -z "$host" "$port" 2>/dev/null; then
            log ERROR "Cannot connect to $host:$port"
            return 1
        fi
    done
    
    log INFO "All internal network connections OK"
    return 0
}

# Test load balancer configuration
test_load_balancer() {
    # Check if NGINX is configured (if using NGINX)
    if docker-compose ps | grep -q nginx; then
        log INFO "NGINX load balancer detected"
        
        # Test configuration
        if docker-compose exec -T nginx nginx -t 2>/dev/null; then
            log INFO "NGINX configuration valid"
        else
            log ERROR "NGINX configuration invalid"
            return 1
        fi
    else
        log INFO "No NGINX load balancer configured"
    fi
    
    return 0
}

# Test monitoring infrastructure
test_monitoring() {
    local monitoring_services=("prometheus" "grafana" "alertmanager")
    local optional_count=0
    local running_count=0
    
    for service in "${monitoring_services[@]}"; do
        ((optional_count++))
        if docker-compose ps 2>/dev/null | grep -q "$service.*Up"; then
            ((running_count++))
            log INFO "Monitoring service $service is running"
        else
            log WARNING "Monitoring service $service not running"
        fi
    done
    
    if [[ $running_count -gt 0 ]]; then
        log INFO "Monitoring infrastructure: $running_count/$optional_count services running"
        return 0
    else
        log WARNING "No monitoring services detected"
        return 0  # Don't fail, monitoring is optional
    fi
}

# Test security configurations
test_security() {
    # Check if services are running with security best practices
    local security_checks=0
    local security_passed=0
    
    # Check if secrets are not in plain text (basic check)
    if [[ -f ".env" ]]; then
        ((security_checks++))
        if ! grep -q "password123\|admin\|secret" .env 2>/dev/null; then
            ((security_passed++))
            log INFO "Environment variables security check passed"
        else
            log WARNING "Environment variables may contain weak credentials"
        fi
    fi
    
    # Check Docker container security
    ((security_checks++))
    local privileged_containers=$(docker-compose ps -q | xargs docker inspect --format '{{.Name}} {{.HostConfig.Privileged}}' | grep true | wc -l)
    if [[ $privileged_containers -eq 0 ]]; then
        ((security_passed++))
        log INFO "No privileged containers detected"
    else
        log WARNING "$privileged_containers privileged containers detected"
    fi
    
    log INFO "Security checks: $security_passed/$security_checks passed"
    return 0
}

# Test resource utilization
test_resources() {
    # Check system resources
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' | cut -d% -f1)
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100}')
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    
    log INFO "System resources: CPU=${cpu_usage}%, Memory=${memory_usage}%, Disk=${disk_usage}%"
    
    # Check Docker resource usage
    local docker_stats=$(docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | tail -n +2)
    if [[ -n "$docker_stats" ]]; then
        log INFO "Docker containers resource usage:"
        echo "$docker_stats" | while read -r line; do
            log INFO "  $line"
        done
    fi
    
    # Warn if resources are high
    if [[ ${cpu_usage%.*} -gt 80 ]]; then
        log WARNING "High CPU usage: ${cpu_usage}%"
    fi
    
    if [[ ${memory_usage%.*} -gt 80 ]]; then
        log WARNING "High memory usage: ${memory_usage}%"
    fi
    
    if [[ $disk_usage -gt 85 ]]; then
        log ERROR "High disk usage: ${disk_usage}%"
        return 1
    fi
    
    return 0
}

# Generate test report
generate_report() {
    local report_file="./logs/infrastructure_test_report_$(date +%Y%m%d_%H%M%S).json"
    
    mkdir -p ./logs
    
    cat > "$report_file" << EOF
{
    "infrastructure_test_report": {
        "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
        "version": "SuperSmartMatch V2",
        "test_summary": {
            "total_tests": $TOTAL_TESTS,
            "passed_tests": $PASSED_TESTS,
            "failed_tests": $FAILED_TESTS,
            "success_rate": $(echo "scale=2; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc -l)
        },
        "environment": {
            "docker_compose_version": "$(docker-compose version --short 2>/dev/null || echo 'unknown')",
            "docker_version": "$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo 'unknown')",
            "system_info": {
                "os": "$(uname -s)",
                "kernel": "$(uname -r)",
                "architecture": "$(uname -m)"
            }
        },
        "test_results": {
            "infrastructure_ready": $([ $FAILED_TESTS -eq 0 ] && echo "true" || echo "false"),
            "critical_services_status": "$([ $FAILED_TESTS -eq 0 ] && echo 'healthy' || echo 'degraded')",
            "recommendation": "$([ $FAILED_TESTS -eq 0 ] && echo 'Ready for deployment' || echo 'Fix issues before deployment')"
        },
        "log_file": "$LOG_FILE"
    }
}
EOF
    
    log INFO "Test report generated: $report_file"
    echo "$report_file"
}

# Display summary
display_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   🔧 INFRASTRUCTURE TEST SUMMARY 🔧          ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║ Total Tests: $TOTAL_TESTS                                          ║"
    echo "║ Passed: $PASSED_TESTS                                              ║"
    echo "║ Failed: $FAILED_TESTS                                              ║"
    echo "║ Success Rate: $(echo "scale=1; $PASSED_TESTS * 100 / $TOTAL_TESTS" | bc -l)%                                      ║"
    
    if [[ $FAILED_TESTS -eq 0 ]]; then
        echo "║ Status: ✅ READY FOR DEPLOYMENT                            ║"
    else
        echo "║ Status: ❌ ISSUES DETECTED - FIX BEFORE DEPLOYMENT        ║"
    fi
    
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Main execution
main() {
    local test_suite=${1:-"all"}
    
    log INFO "🚀 Starting SuperSmartMatch V2 Infrastructure Test Suite"
    log INFO "Test suite: $test_suite"
    log INFO "Timeout per test: ${TEST_TIMEOUT}s"
    
    case $test_suite in
        "basic")
            run_test "Docker Services" test_docker_services
            run_test "Database Connectivity" test_database
            run_test "Redis Connectivity" test_redis
            run_test "Storage Connectivity" test_storage
            ;;
        "services")
            run_test "SuperSmartMatch V1" test_supersmartmatch_v1
            run_test "SuperSmartMatch V2" test_supersmartmatch_v2
            ;;
        "network")
            run_test "Network Connectivity" test_network
            run_test "Load Balancer" test_load_balancer
            ;;
        "monitoring")
            run_test "Monitoring Infrastructure" test_monitoring
            ;;
        "security")
            run_test "Security Configuration" test_security
            ;;
        "resources")
            run_test "Resource Utilization" test_resources
            ;;
        "all")
            # Run all tests
            run_test "Docker Services" test_docker_services
            run_test "Database Connectivity" test_database
            run_test "Redis Connectivity" test_redis
            run_test "Storage Connectivity" test_storage
            run_test "Network Connectivity" test_network
            run_test "SuperSmartMatch V1" test_supersmartmatch_v1
            run_test "SuperSmartMatch V2" test_supersmartmatch_v2
            run_test "Load Balancer" test_load_balancer
            run_test "Monitoring Infrastructure" test_monitoring
            run_test "Security Configuration" test_security
            run_test "Resource Utilization" test_resources
            ;;
        *)
            echo "Usage: $0 {basic|services|network|monitoring|security|resources|all}"
            echo ""
            echo "Test suites:"
            echo "  basic      - Core infrastructure (Docker, DB, Redis, Storage)"
            echo "  services   - SuperSmartMatch services (V1, V2)"
            echo "  network    - Network connectivity and load balancing"
            echo "  monitoring - Monitoring infrastructure"
            echo "  security   - Security configurations"
            echo "  resources  - Resource utilization"
            echo "  all        - Run all test suites"
            exit 1
            ;;
    esac
    
    # Generate report and display summary
    local report_file=$(generate_report)
    display_summary
    
    log INFO "Detailed log: $LOG_FILE"
    log INFO "JSON report: $report_file"
    
    # Exit with appropriate code
    if [[ $FAILED_TESTS -eq 0 ]]; then
        log SUCCESS "🎉 All infrastructure tests passed!"
        exit 0
    else
        log ERROR "❌ $FAILED_TESTS test(s) failed. Fix issues before deployment."
        exit 1
    fi
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"
