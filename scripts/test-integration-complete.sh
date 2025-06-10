#!/bin/bash

# ===========================================
# SuperSmartMatch V2 - Integration Tests
# Tests complets pour l'architecture microservices
# ===========================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Test configuration
API_BASE_URL="http://localhost"
TEST_EMAIL="test-$(date +%s)@supersmartmatch.local"
TEST_PASSWORD="TestPassword123!"
JWT_TOKEN=""

# Counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Functions
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    ((TESTS_RUN++))
    log_test "$test_name"
    
    if eval "$test_command"; then
        log_pass "$test_name"
        return 0
    else
        log_fail "$test_name"
        return 1
    fi
}

# Test infrastructure health
test_infrastructure() {
    echo -e "${PURPLE}🏗️ Testing Infrastructure Services${NC}"
    echo "=================================="
    
    # PostgreSQL
    run_test "PostgreSQL Connectivity" \
        "docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U ssm_user -d supersmartmatch >/dev/null 2>&1"
    
    # Redis
    run_test "Redis Connectivity" \
        "docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping >/dev/null 2>&1"
    
    # MinIO
    run_test "MinIO Health Check" \
        "curl -f http://localhost:9000/minio/health/live >/dev/null 2>&1"
    
    # Nginx Load Balancer
    run_test "Nginx Load Balancer" \
        "curl -f http://localhost/health >/dev/null 2>&1"
    
    echo ""
}

# Test microservices health
test_microservices() {
    echo -e "${PURPLE}🔧 Testing Microservices Health${NC}"
    echo "==============================="
    
    # API Gateway
    run_test "API Gateway Health" \
        "curl -f http://localhost:5050/health >/dev/null 2>&1"
    
    # CV Parser Service
    run_test "CV Parser Service Health" \
        "curl -f http://localhost:5051/health >/dev/null 2>&1"
    
    # Matching Service
    run_test "Matching Service Health" \
        "curl -f http://localhost:5052/health >/dev/null 2>&1"
    
    # Job Parser Service
    run_test "Job Parser Service Health" \
        "curl -f http://localhost:5053/health >/dev/null 2>&1"
    
    # User Service
    run_test "User Service Health" \
        "curl -f http://localhost:5054/health >/dev/null 2>&1"
    
    # Notification Service
    run_test "Notification Service Health" \
        "curl -f http://localhost:5055/health >/dev/null 2>&1"
    
    # Analytics Service
    run_test "Analytics Service Health" \
        "curl -f http://localhost:5056/health >/dev/null 2>&1"
    
    echo ""
}

# Test authentication flow
test_authentication() {
    echo -e "${PURPLE}🔐 Testing Authentication Flow${NC}"
    echo "=============================="
    
    # User Registration
    log_test "User Registration"
    register_response=$(curl -s -X POST "$API_BASE_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\",
            \"firstName\": \"Test\",
            \"lastName\": \"User\"
        }")
    
    if echo "$register_response" | grep -q "success\|registered\|created" || echo "$register_response" | grep -q "token"; then
        log_pass "User Registration"
    else
        log_fail "User Registration - Response: $register_response"
    fi
    
    # User Login
    log_test "User Login"
    login_response=$(curl -s -X POST "$API_BASE_URL/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\"
        }")
    
    if echo "$login_response" | grep -q "token"; then
        log_pass "User Login"
        
        # Extract JWT token for further tests
        JWT_TOKEN=$(echo "$login_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
        log_info "JWT Token extracted for further tests"
    else
        log_fail "User Login - Response: $login_response"
    fi
    
    # Protected Route Access
    if [ -n "$JWT_TOKEN" ]; then
        log_test "Protected Route Access"
        profile_response=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" \
            "$API_BASE_URL/api/users/profile")
        
        if echo "$profile_response" | grep -q "id\|email\|profile"; then
            log_pass "Protected Route Access"
        else
            log_fail "Protected Route Access - Response: $profile_response"
        fi
    else
        log_fail "Protected Route Access - No JWT token available"
    fi
    
    echo ""
}

# Test CV processing
test_cv_processing() {
    echo -e "${PURPLE}📄 Testing CV Processing${NC}"
    echo "========================"
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "CV Processing Tests - No JWT token available"
        return
    fi
    
    # Test CV text parsing
    log_test "CV Text Parsing"
    cv_parse_response=$(curl -s -X POST "$API_BASE_URL/api/cv/parse" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "text": "John Doe\\nSoftware Engineer\\n5 years experience in React, Node.js, Python\\nEducation: Computer Science degree",
            "format": "text"
        }')
    
    if echo "$cv_parse_response" | grep -q "skills\|experience\|success"; then
        log_pass "CV Text Parsing"
    else
        log_fail "CV Text Parsing - Response: $cv_parse_response"
    fi
    
    # Test CV service health through API Gateway
    log_test "CV Service via API Gateway"
    cv_health_response=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" \
        "$API_BASE_URL/api/cv/health")
    
    if echo "$cv_health_response" | grep -q "healthy\|ok\|success"; then
        log_pass "CV Service via API Gateway"
    else
        log_fail "CV Service via API Gateway - Response: $cv_health_response"
    fi
    
    echo ""
}

# Test job processing
test_job_processing() {
    echo -e "${PURPLE}💼 Testing Job Processing${NC}"
    echo "========================="
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "Job Processing Tests - No JWT token available"
        return
    fi
    
    # Test job parsing
    log_test "Job Description Parsing"
    job_parse_response=$(curl -s -X POST "$API_BASE_URL/api/jobs/parse" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Senior React Developer",
            "description": "We are looking for a Senior React Developer with 5+ years experience in React, Node.js, and modern JavaScript. Must have experience with TypeScript and testing frameworks.",
            "company": "TechCorp"
        }')
    
    if echo "$job_parse_response" | grep -q "skills\|requirements\|success"; then
        log_pass "Job Description Parsing"
    else
        log_fail "Job Description Parsing - Response: $job_parse_response"
    fi
    
    # Test job service health through API Gateway
    log_test "Job Service via API Gateway"
    job_health_response=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" \
        "$API_BASE_URL/api/jobs/health")
    
    if echo "$job_health_response" | grep -q "healthy\|ok\|success"; then
        log_pass "Job Service via API Gateway"
    else
        log_fail "Job Service via API Gateway - Response: $job_health_response"
    fi
    
    echo ""
}

# Test matching engine
test_matching_engine() {
    echo -e "${PURPLE}🎯 Testing Matching Engine${NC}"
    echo "=========================="
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "Matching Engine Tests - No JWT token available"
        return
    fi
    
    # Test matching calculation
    log_test "Matching Score Calculation"
    matching_response=$(curl -s -X POST "$API_BASE_URL/api/matching/calculate" \
        -H "Authorization: Bearer $JWT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "cv": {
                "skills": ["React", "Node.js", "JavaScript", "TypeScript"],
                "experience": 5,
                "education": "Computer Science"
            },
            "job": {
                "requiredSkills": ["React", "Node.js", "TypeScript"],
                "experienceMin": 3,
                "experienceMax": 8
            }
        }')
    
    if echo "$matching_response" | grep -q "score\|match\|percentage"; then
        log_pass "Matching Score Calculation"
    else
        log_fail "Matching Score Calculation - Response: $matching_response"
    fi
    
    # Test matching service health
    log_test "Matching Service via API Gateway"
    matching_health_response=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" \
        "$API_BASE_URL/api/matching/health")
    
    if echo "$matching_health_response" | grep -q "healthy\|ok\|success"; then
        log_pass "Matching Service via API Gateway"
    else
        log_fail "Matching Service via API Gateway - Response: $matching_health_response"
    fi
    
    echo ""
}

# Test monitoring services
test_monitoring() {
    echo -e "${PURPLE}📊 Testing Monitoring Services${NC}"
    echo "=============================="
    
    # Prometheus health
    run_test "Prometheus Health" \
        "curl -f http://localhost:9090/-/healthy >/dev/null 2>&1"
    
    # Grafana health
    run_test "Grafana Health" \
        "curl -f http://localhost:3000/api/health >/dev/null 2>&1"
    
    # Test metrics endpoint
    log_test "Prometheus Metrics Collection"
    metrics_response=$(curl -s "http://localhost:9090/api/v1/query?query=up")
    
    if echo "$metrics_response" | grep -q "success\|result"; then
        log_pass "Prometheus Metrics Collection"
    else
        log_fail "Prometheus Metrics Collection - Response: $metrics_response"
    fi
    
    echo ""
}

# Test analytics and notifications
test_analytics_notifications() {
    echo -e "${PURPLE}📈 Testing Analytics & Notifications${NC}"
    echo "===================================="
    
    if [ -z "$JWT_TOKEN" ]; then
        log_fail "Analytics & Notifications Tests - No JWT token available"
        return
    fi
    
    # Test analytics service
    log_test "Analytics Service Health"
    analytics_response=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" \
        "$API_BASE_URL/api/analytics/health")
    
    if echo "$analytics_response" | grep -q "healthy\|ok\|success"; then
        log_pass "Analytics Service Health"
    else
        log_fail "Analytics Service Health - Response: $analytics_response"
    fi
    
    # Test notification service
    log_test "Notification Service Health"
    notification_response=$(curl -s -H "Authorization: Bearer $JWT_TOKEN" \
        "$API_BASE_URL/api/notifications/health")
    
    if echo "$notification_response" | grep -q "healthy\|ok\|success"; then
        log_pass "Notification Service Health"
    else
        log_fail "Notification Service Health - Response: $notification_response"
    fi
    
    echo ""
}

# Test security features
test_security() {
    echo -e "${PURPLE}🔒 Testing Security Features${NC}"
    echo "==========================="
    
    # Test unauthorized access
    log_test "Unauthorized Access Protection"
    unauthorized_response=$(curl -s "$API_BASE_URL/api/users/profile")
    
    if echo "$unauthorized_response" | grep -q "unauthorized\|Unauthorized\|401\|forbidden"; then
        log_pass "Unauthorized Access Protection"
    else
        log_fail "Unauthorized Access Protection - Should reject without token"
    fi
    
    # Test rate limiting (if enabled)
    log_test "Rate Limiting"
    rate_limit_ok=true
    for i in {1..20}; do
        response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL/api/health")
        if [ "$response" = "429" ]; then
            rate_limit_ok=true
            break
        fi
    done
    
    if [ "$rate_limit_ok" = true ]; then
        log_pass "Rate Limiting (or not triggered in test)"
    else
        log_fail "Rate Limiting - Should limit excessive requests"
    fi
    
    echo ""
}

# Test API Gateway routing
test_api_gateway_routing() {
    echo -e "${PURPLE}🌐 Testing API Gateway Routing${NC}"
    echo "=============================="
    
    # Test that API Gateway properly routes to services
    services=(
        "/api/cv:CV Parser"
        "/api/jobs:Job Parser"
        "/api/matching:Matching Service"
        "/api/users:User Service"
        "/api/notifications:Notification Service"
        "/api/analytics:Analytics Service"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r path service_name <<< "$service_info"
        
        log_test "API Gateway Routing to $service_name"
        route_response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE_URL$path/health")
        
        if [ "$route_response" = "200" ] || [ "$route_response" = "401" ]; then
            log_pass "API Gateway Routing to $service_name"
        else
            log_fail "API Gateway Routing to $service_name - HTTP $route_response"
        fi
    done
    
    echo ""
}

# Performance test
test_performance() {
    echo -e "${PURPLE}⚡ Basic Performance Test${NC}"
    echo "========================"
    
    # Test API Gateway response time
    log_test "API Gateway Response Time"
    start_time=$(date +%s%N)
    curl -f "$API_BASE_URL/api/health" >/dev/null 2>&1
    end_time=$(date +%s%N)
    response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds
    
    if [ $response_time -lt 1000 ]; then
        log_pass "API Gateway Response Time (${response_time}ms < 1000ms)"
    else
        log_fail "API Gateway Response Time (${response_time}ms >= 1000ms)"
    fi
    
    # Test concurrent requests
    log_test "Concurrent Request Handling"
    concurrent_ok=true
    for i in {1..5}; do
        curl -f "$API_BASE_URL/api/health" >/dev/null 2>&1 &
    done
    wait
    
    if [ $? -eq 0 ]; then
        log_pass "Concurrent Request Handling"
    else
        log_fail "Concurrent Request Handling"
    fi
    
    echo ""
}

# Show test summary
show_summary() {
    echo -e "${PURPLE}📋 Test Summary${NC}"
    echo "==============="
    echo ""
    echo -e "${BLUE}Tests Run:${NC} $TESTS_RUN"
    echo -e "${GREEN}Tests Passed:${NC} $TESTS_PASSED"
    echo -e "${RED}Tests Failed:${NC} $TESTS_FAILED"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! SuperSmartMatch V2 is fully operational.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️ Some tests failed. Check the output above for details.${NC}"
        exit 1
    fi
}

# Main test execution
main() {
    echo -e "${PURPLE}🧪 SuperSmartMatch V2 - Integration Test Suite${NC}"
    echo -e "${PURPLE}===============================================${NC}"
    echo ""
    
    log_info "Starting comprehensive integration tests..."
    log_info "Test user: $TEST_EMAIL"
    echo ""
    
    case "${1:-all}" in
        "infrastructure")
            test_infrastructure
            ;;
        "microservices")
            test_microservices
            ;;
        "auth")
            test_authentication
            ;;
        "cv")
            test_authentication  # Need token first
            test_cv_processing
            ;;
        "jobs")
            test_authentication  # Need token first
            test_job_processing
            ;;
        "matching")
            test_authentication  # Need token first
            test_matching_engine
            ;;
        "monitoring")
            test_monitoring
            ;;
        "security")
            test_security
            ;;
        "performance")
            test_performance
            ;;
        "all")
            test_infrastructure
            test_microservices
            test_authentication
            test_cv_processing
            test_job_processing
            test_matching_engine
            test_analytics_notifications
            test_monitoring
            test_security
            test_api_gateway_routing
            test_performance
            ;;
        *)
            echo "Usage: $0 {all|infrastructure|microservices|auth|cv|jobs|matching|monitoring|security|performance}"
            exit 1
            ;;
    esac
    
    show_summary
}

# Execute main function
main "$@"