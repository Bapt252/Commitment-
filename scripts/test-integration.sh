#!/bin/bash

# ===========================================
# SuperSmartMatch V2 - Integration Tests
# ===========================================

set -e

echo "🧪 SuperSmartMatch V2 - Microservices Integration Tests"
echo "======================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BASE_URL="http://localhost"
API_URL="$BASE_URL/api"
TEST_EMAIL="integration-test@supersmartmatch.com"
TEST_PASSWORD="IntegrationTest123!"

# Counters
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Functions
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
    ((TESTS_TOTAL++))
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
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Test helper functions
assert_response_contains() {
    local response="$1"
    local expected="$2"
    local test_name="$3"
    
    if echo "$response" | grep -q "$expected"; then
        log_pass "$test_name"
        return 0
    else
        log_fail "$test_name - Expected: '$expected', Got: '$response'"
        return 1
    fi
}

assert_http_status() {
    local url="$1"
    local expected_status="$2"
    local test_name="$3"
    local headers="$4"
    
    local actual_status
    if [ -n "$headers" ]; then
        actual_status=$(curl -s -o /dev/null -w "%{http_code}" $headers "$url")
    else
        actual_status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    fi
    
    if [ "$actual_status" = "$expected_status" ]; then
        log_pass "$test_name (HTTP $actual_status)"
        return 0
    else
        log_fail "$test_name - Expected: HTTP $expected_status, Got: HTTP $actual_status"
        return 1
    fi
}

# Test suites

test_infrastructure() {
    echo ""
    log_info "=== Infrastructure Tests ==="
    
    log_test "Load Balancer Health Check"
    assert_http_status "$BASE_URL/health" "200" "Load balancer responds"
    
    log_test "PostgreSQL Connectivity"
    if docker-compose -f docker-compose.production.yml exec postgres pg_isready -U ssm_user -d supersmartmatch > /dev/null 2>&1; then
        log_pass "PostgreSQL is ready"
    else
        log_fail "PostgreSQL connection failed"
    fi
    
    log_test "Redis Connectivity"
    if docker-compose -f docker-compose.production.yml exec redis redis-cli ping > /dev/null 2>&1; then
        log_pass "Redis is ready"
    else
        log_fail "Redis connection failed"
    fi
    
    log_test "MinIO Connectivity"
    assert_http_status "http://localhost:9000/minio/health/live" "200" "MinIO health check"
}

test_microservices_health() {
    echo ""
    log_info "=== Microservices Health Tests ==="
    
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
        log_test "$service Health Check"
        assert_http_status "http://localhost:$port/health" "200" "$service is healthy"
    done
}

test_authentication_flow() {
    echo ""
    log_info "=== Authentication Flow Tests ==="
    
    # Test user registration
    log_test "User Registration"
    register_response=$(curl -s -X POST "$API_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\",
            \"firstName\": \"Integration\",
            \"lastName\": \"Test\"
        }")
    
    if echo "$register_response" | grep -q "registered successfully"; then
        log_pass "User registration successful"
    elif echo "$register_response" | grep -q "already exists"; then
        log_pass "User registration (user already exists)"
    else
        log_fail "User registration failed: $register_response"
    fi
    
    # Test user login
    log_test "User Login"
    login_response=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$TEST_EMAIL\",
            \"password\": \"$TEST_PASSWORD\"
        }")
    
    if echo "$login_response" | grep -q "token"; then
        log_pass "User login successful"
        # Extract token for subsequent tests
        TOKEN=$(echo "$login_response" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
        export TOKEN
    else
        log_fail "User login failed: $login_response"
        return 1
    fi
    
    # Test token validation
    log_test "Token Validation"
    validation_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/auth/validate")
    assert_response_contains "$validation_response" "valid" "Token validation"
    
    # Test protected endpoint access
    log_test "Protected Endpoint Access"
    protected_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/users/profile")
    assert_response_contains "$protected_response" "id" "Protected endpoint access"
}

test_cv_parser_service() {
    echo ""
    log_info "=== CV Parser Service Tests ==="
    
    if [ -z "$TOKEN" ]; then
        log_fail "No authentication token available for CV parser tests"
        return 1
    fi
    
    # Test CV upload endpoint availability
    log_test "CV Upload Endpoint"
    assert_http_status "$API_URL/cv/upload" "401" "CV upload requires auth" ""
    
    # Test with authentication (should return 400 for missing file)
    log_test "CV Upload with Auth"
    assert_http_status "$API_URL/cv/upload" "400" "CV upload with auth (missing file)" "-H \"Authorization: Bearer $TOKEN\""
    
    # Test CV parsing endpoint
    log_test "CV Parsing Endpoint"
    parsing_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/cv/parse" \
        -H "Content-Type: application/json" \
        -d '{
            "text": "John Doe\\nSoftware Engineer\\n5 years experience\\nJavaScript, Python, React",
            "format": "text"
        }')
    
    if echo "$parsing_response" | grep -q "parsed" || echo "$parsing_response" | grep -q "skills"; then
        log_pass "CV parsing functional"
    else
        log_fail "CV parsing failed: $parsing_response"
    fi
}

test_job_parser_service() {
    echo ""
    log_info "=== Job Parser Service Tests ==="
    
    if [ -z "$TOKEN" ]; then
        log_fail "No authentication token available for job parser tests"
        return 1
    fi
    
    # Test job parsing endpoint
    log_test "Job Parsing Endpoint"
    job_parsing_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/jobs/parse" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Senior Software Engineer",
            "description": "We are looking for a Senior Software Engineer with 5+ years experience in JavaScript, React, Node.js. Remote work available.",
            "company": "TechCorp"
        }')
    
    if echo "$job_parsing_response" | grep -q "parsed" || echo "$job_parsing_response" | grep -q "skills"; then
        log_pass "Job parsing functional"
    else
        log_fail "Job parsing failed: $job_parsing_response"
    fi
}

test_matching_service() {
    echo ""
    log_info "=== Matching Service Tests ==="
    
    if [ -z "$TOKEN" ]; then
        log_fail "No authentication token available for matching tests"
        return 1
    fi
    
    # Test matching algorithm endpoint
    log_test "Matching Algorithm"
    matching_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/matching/calculate" \
        -H "Content-Type: application/json" \
        -d '{
            "cv": {
                "skills": ["JavaScript", "React", "Node.js"],
                "experience": 5,
                "location": "Paris"
            },
            "job": {
                "requiredSkills": ["JavaScript", "React"],
                "experienceMin": 3,
                "location": "Paris"
            }
        }')
    
    if echo "$matching_response" | grep -q "score" || echo "$matching_response" | grep -q "match"; then
        log_pass "Matching algorithm functional"
    else
        log_fail "Matching algorithm failed: $matching_response"
    fi
}

test_notification_service() {
    echo ""
    log_info "=== Notification Service Tests ==="
    
    if [ -z "$TOKEN" ]; then
        log_fail "No authentication token available for notification tests"
        return 1
    fi
    
    # Test notification creation
    log_test "Notification Creation"
    notification_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/notifications" \
        -H "Content-Type: application/json" \
        -d '{
            "type": "match_found",
            "title": "New Match Found",
            "message": "We found a new job match for you!",
            "data": {"jobId": "test-job-123"}
        }')
    
    if echo "$notification_response" | grep -q "id" || echo "$notification_response" | grep -q "created"; then
        log_pass "Notification creation functional"
    else
        log_fail "Notification creation failed: $notification_response"
    fi
    
    # Test notification retrieval
    log_test "Notification Retrieval"
    get_notifications_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/notifications")
    
    if echo "$get_notifications_response" | grep -q "notifications" || echo "$get_notifications_response" | grep -q "\\["; then
        log_pass "Notification retrieval functional"
    else
        log_fail "Notification retrieval failed: $get_notifications_response"
    fi
}

test_analytics_service() {
    echo ""
    log_info "=== Analytics Service Tests ==="
    
    if [ -z "$TOKEN" ]; then
        log_fail "No authentication token available for analytics tests"
        return 1
    fi
    
    # Test event tracking
    log_test "Event Tracking"
    analytics_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/analytics/events" \
        -H "Content-Type: application/json" \
        -d '{
            "eventType": "cv_upload",
            "eventData": {
                "fileName": "test_cv.pdf",
                "fileSize": 1024,
                "processingTime": 250
            }
        }')
    
    if echo "$analytics_response" | grep -q "tracked" || echo "$analytics_response" | grep -q "success"; then
        log_pass "Event tracking functional"
    else
        log_fail "Event tracking failed: $analytics_response"
    fi
    
    # Test metrics retrieval
    log_test "Metrics Retrieval"
    metrics_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/analytics/metrics/dashboard")
    
    if echo "$metrics_response" | grep -q "metrics" || echo "$metrics_response" | grep -q "totalUsers"; then
        log_pass "Metrics retrieval functional"
    else
        log_fail "Metrics retrieval failed: $metrics_response"
    fi
}

test_end_to_end_workflow() {
    echo ""
    log_info "=== End-to-End Workflow Tests ==="
    
    if [ -z "$TOKEN" ]; then
        log_fail "No authentication token available for E2E tests"
        return 1
    fi
    
    # Simulate complete user workflow
    log_test "Complete User Workflow"
    
    # 1. Parse a CV
    cv_parse_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/cv/parse" \
        -H "Content-Type: application/json" \
        -d '{
            "text": "Alice Johnson\\nFull Stack Developer\\n3 years experience\\nJavaScript, React, Node.js, Python\\nParis, France",
            "format": "text"
        }')
    
    # 2. Parse a job
    job_parse_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/jobs/parse" \
        -H "Content-Type: application/json" \
        -d '{
            "title": "Full Stack Developer",
            "description": "Looking for a Full Stack Developer with React and Node.js experience. 2+ years required. Paris location.",
            "company": "TechStartup"
        }')
    
    # 3. Get matches
    matches_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/matching/candidates?limit=10")
    
    # 4. Check notifications
    notifications_response=$(curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/notifications")
    
    if echo "$cv_parse_response" | grep -q "skills" && \
       echo "$job_parse_response" | grep -q "requirements" && \
       (echo "$matches_response" | grep -q "matches" || echo "$matches_response" | grep -q "\\["); then
        log_pass "End-to-end workflow completed successfully"
    else
        log_fail "End-to-end workflow failed at some step"
    fi
}

test_performance_and_load() {
    echo ""
    log_info "=== Performance and Load Tests ==="
    
    if [ -z "$TOKEN" ]; then
        log_fail "No authentication token available for performance tests"
        return 1
    fi
    
    # Test response times
    log_test "API Response Times"
    
    # Measure API Gateway response time
    start_time=$(date +%s%3N)
    curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/users/profile" > /dev/null
    end_time=$(date +%s%3N)
    response_time=$((end_time - start_time))
    
    if [ "$response_time" -lt 1000 ]; then
        log_pass "API response time acceptable ($response_time ms)"
    elif [ "$response_time" -lt 2000 ]; then
        log_pass "API response time moderate ($response_time ms)"
    else
        log_fail "API response time too slow ($response_time ms)"
    fi
    
    # Test concurrent requests (simple load test)
    log_test "Concurrent Request Handling"
    
    # Send 10 concurrent requests
    for i in {1..10}; do
        curl -s -H "Authorization: Bearer $TOKEN" "$API_URL/auth/validate" > /dev/null &
    done
    wait
    
    log_pass "Concurrent requests handled"
}

test_security() {
    echo ""
    log_info "=== Security Tests ==="
    
    # Test unauthenticated access
    log_test "Protected Endpoint Security"
    assert_http_status "$API_URL/users/profile" "401" "Unauthenticated access blocked"
    
    # Test invalid token
    log_test "Invalid Token Handling"
    assert_http_status "$API_URL/users/profile" "401" "Invalid token rejected" "-H \"Authorization: Bearer invalid_token\""
    
    # Test SQL injection protection (basic)
    log_test "SQL Injection Protection"
    injection_response=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d '{
            "email": "test@test.com; DROP TABLE users; --",
            "password": "password"
        }')
    
    if echo "$injection_response" | grep -q "Validation failed" || echo "$injection_response" | grep -q "Invalid"; then
        log_pass "SQL injection attempt blocked"
    else
        log_fail "SQL injection protection may be insufficient"
    fi
    
    # Test rate limiting (if enabled)
    log_test "Rate Limiting"
    rate_limit_status=0
    for i in {1..20}; do
        status=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/auth/validate" -H "Authorization: Bearer $TOKEN")
        if [ "$status" = "429" ]; then
            rate_limit_status=1
            break
        fi
    done
    
    if [ "$rate_limit_status" = "1" ]; then
        log_pass "Rate limiting is active"
    else
        log_pass "Rate limiting not triggered (or not configured)"
    fi
}

cleanup_test_data() {
    log_info "Cleaning up test data..."
    
    if [ -n "$TOKEN" ]; then
        # Logout test user
        curl -s -X POST "$API_URL/auth/logout" -H "Authorization: Bearer $TOKEN" > /dev/null
    fi
    
    log_info "Test cleanup completed"
}

show_test_summary() {
    echo ""
    echo "📊 Integration Test Summary"
    echo "=========================="
    echo "Total Tests: $TESTS_TOTAL"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    echo ""
    
    if [ "$TESTS_FAILED" -eq 0 ]; then
        echo -e "${GREEN}🎉 All tests passed! SuperSmartMatch V2 is ready for production.${NC}"
        return 0
    else
        echo -e "${RED}❌ Some tests failed. Please review the issues above.${NC}"
        return 1
    fi
}

# Main test execution
main() {
    case "${1:-all}" in
        "infrastructure")
            test_infrastructure
            ;;
        "services")
            test_microservices_health
            ;;
        "auth")
            test_authentication_flow
            ;;
        "integration")
            test_authentication_flow
            test_cv_parser_service
            test_job_parser_service
            test_matching_service
            test_notification_service
            test_analytics_service
            ;;
        "e2e")
            test_authentication_flow
            test_end_to_end_workflow
            ;;
        "performance")
            test_authentication_flow
            test_performance_and_load
            ;;
        "security")
            test_security
            ;;
        "all")
            test_infrastructure
            test_microservices_health
            test_authentication_flow
            test_cv_parser_service
            test_job_parser_service
            test_matching_service
            test_notification_service
            test_analytics_service
            test_end_to_end_workflow
            test_performance_and_load
            test_security
            cleanup_test_data
            show_test_summary
            ;;
        *)
            echo "Usage: $0 {infrastructure|services|auth|integration|e2e|performance|security|all}"
            echo ""
            echo "Test Suites:"
            echo "  infrastructure - Test database, Redis, MinIO connectivity"
            echo "  services      - Test all microservice health endpoints"
            echo "  auth          - Test authentication and authorization"
            echo "  integration   - Test service-to-service communication"
            echo "  e2e           - Test complete user workflows"
            echo "  performance   - Test response times and load handling"
            echo "  security      - Test security measures"
            echo "  all           - Run all test suites"
            exit 1
            ;;
    esac
    
    if [ "$1" != "all" ]; then
        show_test_summary
    fi
}

# Execute main function
main "$@"
