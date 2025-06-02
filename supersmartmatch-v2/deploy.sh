#!/bin/bash
# SuperSmartMatch V2 - Validation and Deployment Script
# Comprehensive validation and deployment automation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
V2_PORT=5070
V1_PORT=5062
NEXTEN_PORT=5052
REDIS_PORT=6379
DOCKER_COMPOSE_FILE="docker-compose.yml"
TEST_TIMEOUT=300

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    success "Docker Compose is installed"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
        exit 1
    fi
    success "Python 3 is installed"
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        error "curl is not installed"
        exit 1
    fi
    success "curl is installed"
}

# Build and validate Docker image
build_and_validate() {
    log "Building SuperSmartMatch V2 Docker image..."
    
    # Build the image
    docker build -t supersmartmatch-v2:latest .
    success "Docker image built successfully"
    
    # Test image
    log "Testing Docker image..."
    container_id=$(docker run -d -p ${V2_PORT}:${V2_PORT} supersmartmatch-v2:latest)
    
    # Wait for service to start
    sleep 10
    
    # Test health endpoint
    if curl -f http://localhost:${V2_PORT}/health &> /dev/null; then
        success "Docker image test passed"
    else
        error "Docker image test failed"
        docker logs $container_id
        docker stop $container_id
        exit 1
    fi
    
    # Cleanup test container
    docker stop $container_id
    docker rm $container_id
}

# Run unit tests
run_tests() {
    log "Running unit tests..."
    
    # Install test dependencies
    pip install -r requirements.txt
    
    # Run pytest
    if python -m pytest test_supersmartmatch_v2.py -v; then
        success "All tests passed"
    else
        error "Tests failed"
        exit 1
    fi
}

# Validate configuration
validate_config() {
    log "Validating configuration..."
    
    # Check config file exists
    if [[ ! -f "config.yml" ]]; then
        error "config.yml not found"
        exit 1
    fi
    success "Configuration file found"
    
    # Validate YAML syntax
    if python -c "import yaml; yaml.safe_load(open('config.yml'))" 2>/dev/null; then
        success "Configuration file is valid YAML"
    else
        error "Configuration file has invalid YAML syntax"
        exit 1
    fi
    
    # Check Docker Compose file
    if docker-compose -f $DOCKER_COMPOSE_FILE config &> /dev/null; then
        success "Docker Compose configuration is valid"
    else
        error "Docker Compose configuration is invalid"
        exit 1
    fi
}

# Deploy services
deploy_services() {
    log "Deploying SuperSmartMatch V2 services..."
    
    # Stop any existing services
    docker-compose -f $DOCKER_COMPOSE_FILE down --remove-orphans
    
    # Start services
    docker-compose -f $DOCKER_COMPOSE_FILE up -d
    
    success "Services deployment initiated"
}

# Wait for services to be healthy
wait_for_services() {
    log "Waiting for services to be healthy..."
    
    local max_attempts=60
    local attempt=0
    
    # Function to check service health
    check_service() {
        local port=$1
        local service_name=$2
        
        if curl -f http://localhost:${port}/health &> /dev/null; then
            return 0
        else
            return 1
        fi
    }
    
    # Wait for SuperSmartMatch V2
    log "Checking SuperSmartMatch V2 (port ${V2_PORT})..."
    while [ $attempt -lt $max_attempts ]; do
        if check_service $V2_PORT "SuperSmartMatch V2"; then
            success "SuperSmartMatch V2 is healthy"
            break
        fi
        
        sleep 5
        ((attempt++))
        
        if [ $attempt -eq $max_attempts ]; then
            error "SuperSmartMatch V2 failed to start"
            docker-compose logs supersmartmatch-v2
            exit 1
        fi
    done
    
    # Check Redis
    log "Checking Redis (port ${REDIS_PORT})..."
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker exec -it supersmartmatch-redis redis-cli ping | grep -q PONG; then
            success "Redis is healthy"
            break
        fi
        
        sleep 2
        ((attempt++))
        
        if [ $attempt -eq $max_attempts ]; then
            error "Redis failed to start"
            exit 1
        fi
    done
}

# Run integration tests
run_integration_tests() {
    log "Running integration tests..."
    
    # Test V2 API endpoint
    log "Testing V2 API endpoint..."
    
    sample_request='{
        "candidate": {
            "name": "Test User",
            "email": "test@example.com",
            "technical_skills": [
                {
                    "name": "Python",
                    "level": "Expert",
                    "years": 5
                }
            ]
        },
        "offers": [
            {
                "id": "test_job_1",
                "title": "Python Developer",
                "company": "Test Company",
                "required_skills": ["Python", "Django"]
            }
        ],
        "algorithm": "auto"
    }'
    
    response=$(curl -s -X POST http://localhost:${V2_PORT}/api/v2/match \
        -H "Content-Type: application/json" \
        -d "$sample_request")
    
    if echo "$response" | grep -q '"success":true'; then
        success "V2 API endpoint test passed"
    else
        error "V2 API endpoint test failed"
        echo "Response: $response"
        exit 1
    fi
    
    # Test V1 compatibility endpoint
    log "Testing V1 compatibility endpoint..."
    
    v1_request='{
        "candidate": {
            "name": "Test User",
            "email": "test@example.com",
            "technical_skills": ["Python", "Machine Learning"]
        },
        "offers": [
            {
                "id": "test_job_1",
                "title": "ML Engineer",
                "company": "Test Company",
                "required_skills": ["Python", "TensorFlow"]
            }
        ]
    }'
    
    response=$(curl -s -X POST http://localhost:${V2_PORT}/match \
        -H "Content-Type: application/json" \
        -d "$v1_request")
    
    if echo "$response" | grep -q '"matches"'; then
        success "V1 compatibility endpoint test passed"
    else
        error "V1 compatibility endpoint test failed"
        echo "Response: $response"
        exit 1
    fi
    
    # Test health checks
    log "Testing health checks..."
    
    health_response=$(curl -s http://localhost:${V2_PORT}/health)
    if echo "$health_response" | grep -q '"status":"healthy"'; then
        success "Health check test passed"
    else
        error "Health check test failed"
        exit 1
    fi
    
    # Test stats endpoint
    log "Testing stats endpoint..."
    
    stats_response=$(curl -s http://localhost:${V2_PORT}/stats)
    if echo "$stats_response" | grep -q '"status":"operational"'; then
        success "Stats endpoint test passed"
    else
        error "Stats endpoint test failed"
        exit 1
    fi
}

# Validate algorithm selection
validate_algorithm_selection() {
    log "Validating algorithm selection logic..."
    
    # Test complete data scenario (should select Nexten)
    complete_data_request='{
        "candidate": {
            "name": "Senior Developer",
            "email": "senior@example.com",
            "technical_skills": [
                {"name": "Python", "level": "Expert", "years": 8},
                {"name": "Machine Learning", "level": "Advanced", "years": 4}
            ],
            "experiences": [
                {
                    "title": "Senior Developer",
                    "company": "TechCorp",
                    "duration_months": 36,
                    "skills": ["Python", "Django"]
                }
            ]
        },
        "candidate_questionnaire": {
            "work_style": "collaborative",
            "culture_preferences": "innovation_focused",
            "remote_preference": "hybrid",
            "career_goals": "technical_leadership"
        },
        "offers": [
            {
                "id": "senior_job",
                "title": "Technical Lead",
                "company": "Innovation Co",
                "required_skills": ["Python", "Leadership"]
            }
        ],
        "company_questionnaires": [
            {
                "culture": "innovation_focused",
                "team_size": "small"
            }
        ],
        "algorithm": "auto"
    }'
    
    response=$(curl -s -X POST http://localhost:${V2_PORT}/api/v2/match \
        -H "Content-Type: application/json" \
        -d "$complete_data_request")
    
    if echo "$response" | grep -q '"selection_reason".*complete'; then
        success "Algorithm selection validation passed"
    else
        warning "Algorithm selection test inconclusive (may fall back due to service unavailability)"
    fi
}

# Performance validation
validate_performance() {
    log "Validating performance requirements..."
    
    request='{
        "candidate": {
            "name": "Performance Test",
            "email": "perf@example.com",
            "technical_skills": [{"name": "Python", "level": "Expert"}]
        },
        "offers": [
            {
                "id": "perf_job",
                "title": "Developer",
                "company": "Test Co",
                "required_skills": ["Python"]
            }
        ]
    }'
    
    # Measure response time
    start_time=$(date +%s%3N)
    response=$(curl -s -X POST http://localhost:${V2_PORT}/api/v2/match \
        -H "Content-Type: application/json" \
        -d "$request")
    end_time=$(date +%s%3N)
    
    response_time=$((end_time - start_time))
    
    if [ $response_time -lt 1000 ]; then  # Less than 1 second
        success "Performance validation passed (${response_time}ms)"
    else
        warning "Performance slower than expected (${response_time}ms)"
    fi
    
    # Check execution time in response
    execution_time=$(echo "$response" | grep -o '"execution_time_ms":[0-9]*' | cut -d':' -f2)
    if [ -n "$execution_time" ] && [ "$execution_time" -lt 500 ]; then
        success "Internal execution time acceptable (${execution_time}ms)"
    else
        warning "Internal execution time higher than expected"
    fi
}

# Show deployment summary
show_summary() {
    log "Deployment Summary:"
    echo
    echo "🚀 SuperSmartMatch V2 Services:"
    echo "   - V2 Main Service:    http://localhost:${V2_PORT}"
    echo "   - V2 API Docs:        http://localhost:${V2_PORT}/api/docs"
    echo "   - V1 Compatible API:  http://localhost:${V2_PORT}/match"
    echo "   - Health Check:       http://localhost:${V2_PORT}/health"
    echo "   - Stats:              http://localhost:${V2_PORT}/stats"
    echo
    echo "📊 Monitoring:"
    echo "   - Prometheus:         http://localhost:9090"
    echo "   - Grafana:            http://localhost:3000 (admin/supersmartmatch2024)"
    echo
    echo "🔧 Infrastructure:"
    echo "   - Redis:              localhost:${REDIS_PORT}"
    echo "   - Load Balancer:      http://localhost:80"
    echo
    echo "📋 Service Status:"
    docker-compose ps
    echo
    success "SuperSmartMatch V2 deployment completed successfully!"
}

# Cleanup function
cleanup() {
    if [ "$1" == "full" ]; then
        log "Performing full cleanup..."
        docker-compose down --volumes --remove-orphans
        docker system prune -f
        success "Full cleanup completed"
    else
        log "Stopping services..."
        docker-compose stop
        success "Services stopped"
    fi
}

# Main function
main() {
    case "$1" in
        "validate")
            log "🔍 Running validation only..."
            check_prerequisites
            validate_config
            run_tests
            success "Validation completed successfully"
            ;;
        "deploy")
            log "🚀 Running full deployment..."
            check_prerequisites
            validate_config
            build_and_validate
            run_tests
            deploy_services
            wait_for_services
            run_integration_tests
            validate_algorithm_selection
            validate_performance
            show_summary
            ;;
        "test")
            log "🧪 Running tests only..."
            run_integration_tests
            validate_algorithm_selection
            validate_performance
            ;;
        "cleanup")
            cleanup "$2"
            ;;
        "status")
            log "📊 Service status:"
            docker-compose ps
            ;;
        *)
            echo "Usage: $0 {validate|deploy|test|cleanup|status}"
            echo
            echo "Commands:"
            echo "  validate  - Run validation tests without deployment"
            echo "  deploy    - Full validation and deployment"
            echo "  test      - Run integration tests on running services"
            echo "  cleanup   - Stop services (add 'full' for complete cleanup)"
            echo "  status    - Show service status"
            echo
            echo "Examples:"
            echo "  $0 deploy              # Full deployment"
            echo "  $0 validate            # Validation only"
            echo "  $0 cleanup full        # Full cleanup with volumes"
            exit 1
            ;;
    esac
}

# Trap to cleanup on script exit
trap 'if [ $? -ne 0 ]; then error "Script failed. Check logs above."; fi' EXIT

# Run main function
main "$@"
