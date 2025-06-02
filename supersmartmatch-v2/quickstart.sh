#!/bin/bash
# SuperSmartMatch V2 - Quick Start Script
# Simple script for rapid development and testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Default configuration
DEFAULT_PORT=5070
DEFAULT_HOST="0.0.0.0"
DEFAULT_ENV="development"

# Display banner
show_banner() {
    echo -e "${BLUE}"
    echo "🚀 SuperSmartMatch V2 - Quick Start"
    echo "=================================="
    echo "Unified Intelligent Matching Service"
    echo "Port: ${DEFAULT_PORT} | Version: 2.0.0"
    echo -e "${NC}"
}

# Usage information
show_usage() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  start     - Start SuperSmartMatch V2 service"
    echo "  dev       - Start in development mode with hot reload"
    echo "  test      - Run quick API test"
    echo "  demo      - Run demonstration with sample data"
    echo "  install   - Install dependencies"
    echo "  clean     - Clean up temporary files"
    echo "  help      - Show this help message"
    echo
    echo "Options:"
    echo "  --port PORT     - Service port (default: ${DEFAULT_PORT})"
    echo "  --host HOST     - Service host (default: ${DEFAULT_HOST})"
    echo "  --env ENV       - Environment (development/production)"
    echo
    echo "Examples:"
    echo "  $0 start                    # Start service on default port"
    echo "  $0 dev --port 5071         # Development mode on port 5071"
    echo "  $0 test                     # Quick API test"
    echo "  $0 demo                     # Run demonstration"
}

# Log function
log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check if Python is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is not installed"
    fi
    
    local python_version=$(python3 --version | cut -d' ' -f2)
    log "Python version: $python_version"
}

# Install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    if [[ ! -f "requirements.txt" ]]; then
        error "requirements.txt not found"
    fi
    
    pip install -r requirements.txt
    success "Dependencies installed"
}

# Create .env file if it doesn't exist
setup_env() {
    if [[ ! -f ".env" ]]; then
        log "Creating .env file from .env.example..."
        cp .env.example .env
        success ".env file created"
    fi
}

# Start the service
start_service() {
    local port=${1:-$DEFAULT_PORT}
    local host=${2:-$DEFAULT_HOST}
    local env=${3:-$DEFAULT_ENV}
    
    log "Starting SuperSmartMatch V2 service..."
    log "Host: $host | Port: $port | Environment: $env"
    
    # Set environment variables
    export ENVIRONMENT=$env
    export HOST=$host
    export PORT=$port
    
    # Start the service
    python main.py
}

# Start in development mode
start_dev() {
    local port=${1:-$DEFAULT_PORT}
    local host=${2:-$DEFAULT_HOST}
    
    log "Starting SuperSmartMatch V2 in development mode..."
    log "Host: $host | Port: $port | Hot reload: enabled"
    
    # Set development environment
    export ENVIRONMENT=development
    export LOG_LEVEL=DEBUG
    export ENABLE_DEBUG_LOGS=true
    
    # Start with uvicorn and hot reload
    uvicorn main:app --host $host --port $port --reload --log-level debug
}

# Wait for service to be ready
wait_for_service() {
    local port=${1:-$DEFAULT_PORT}
    local max_attempts=30
    local attempt=0
    
    log "Waiting for service to be ready on port $port..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$port/health > /dev/null 2>&1; then
            success "Service is ready!"
            return 0
        fi
        
        sleep 2
        ((attempt++))
        echo -n "."
    done
    
    error "Service failed to start after $max_attempts attempts"
}

# Run quick API test
run_test() {
    local port=${1:-$DEFAULT_PORT}
    
    log "Running quick API test on port $port..."
    
    # Check if service is running
    if ! curl -s http://localhost:$port/health > /dev/null; then
        error "Service is not running on port $port"
    fi
    
    # Test health endpoint
    log "Testing health endpoint..."
    health_response=$(curl -s http://localhost:$port/health)
    if echo "$health_response" | grep -q '"status":"healthy"'; then
        success "Health check passed"
    else
        error "Health check failed"
    fi
    
    # Test V2 API with sample data
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
                "required_skills": ["Python"]
            }
        ],
        "algorithm": "auto"
    }'
    
    api_response=$(curl -s -X POST http://localhost:$port/api/v2/match \
        -H "Content-Type: application/json" \
        -d "$sample_request")
    
    if echo "$api_response" | grep -q '"success":true'; then
        success "V2 API test passed"
        echo "Algorithm used: $(echo "$api_response" | grep -o '"algorithm_used":"[^"]*"' | cut -d'"' -f4)"
    else
        warning "V2 API test failed - check service logs"
        echo "Response: $api_response"
    fi
    
    # Test V1 compatibility
    log "Testing V1 compatibility endpoint..."
    v1_request='{
        "candidate": {
            "name": "V1 Test User",
            "technical_skills": ["Python"],
            "experiences": [
                {
                    "title": "Developer",
                    "company": "TestCorp",
                    "duration": 24
                }
            ]
        },
        "offers": [
            {
                "id": "v1_job_1",
                "title": "Python Developer",
                "required_skills": ["Python"]
            }
        ]
    }'
    
    v1_response=$(curl -s -X POST http://localhost:$port/match \
        -H "Content-Type: application/json" \
        -d "$v1_request")
    
    if echo "$v1_response" | grep -q '"matches"'; then
        success "V1 compatibility test passed"
    else
        warning "V1 compatibility test failed"
    fi
    
    success "All tests completed!"
}

# Run demonstration
run_demo() {
    local port=${1:-$DEFAULT_PORT}
    
    log "Running SuperSmartMatch V2 demonstration..."
    
    # Check if service is running
    if ! curl -s http://localhost:$port/health > /dev/null; then
        error "Service is not running on port $port. Start it first with: $0 start"
    fi
    
    echo -e "${PURPLE}"
    echo "🎯 SuperSmartMatch V2 Demonstration"
    echo "=================================="
    echo -e "${NC}"
    
    # Demo 1: Complete data scenario (should select Nexten)
    echo -e "${YELLOW}Demo 1: Complete Data Scenario (Nexten Algorithm)${NC}"
    
    complete_data_request='{
        "candidate": {
            "name": "Marie Expert",
            "email": "marie@example.com",
            "technical_skills": [
                {"name": "Python", "level": "Expert", "years": 6},
                {"name": "Machine Learning", "level": "Advanced", "years": 4}
            ],
            "experiences": [
                {
                    "title": "Senior ML Engineer",
                    "company": "TechCorp",
                    "duration_months": 36,
                    "skills": ["Python", "TensorFlow"]
                }
            ]
        },
        "candidate_questionnaire": {
            "work_style": "collaborative",
            "culture_preferences": "innovation_focused",
            "remote_preference": "hybrid"
        },
        "offers": [
            {
                "id": "ml_job_001",
                "title": "ML Engineering Lead",
                "company": "AI Labs",
                "required_skills": ["Python", "Machine Learning", "Leadership"]
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
    
    echo "📤 Sending complete data request..."
    demo1_response=$(curl -s -X POST http://localhost:$port/api/v2/match \
        -H "Content-Type: application/json" \
        -d "$complete_data_request")
    
    if echo "$demo1_response" | grep -q '"success":true'; then
        algorithm=$(echo "$demo1_response" | grep -o '"algorithm_used":"[^"]*"' | cut -d'"' -f4)
        score=$(echo "$demo1_response" | grep -o '"overall_score":[0-9.]*' | cut -d':' -f2)
        reason=$(echo "$demo1_response" | grep -o '"selection_reason":"[^"]*"' | cut -d'"' -f4)
        
        echo "✅ Algorithm selected: $algorithm"
        echo "📊 Match score: $score"
        echo "💡 Selection reason: $reason"
    else
        echo "❌ Demo 1 failed"
    fi
    
    echo
    sleep 2
    
    # Demo 2: Minimal data scenario
    echo -e "${YELLOW}Demo 2: Minimal Data Scenario${NC}"
    
    minimal_request='{
        "candidate": {
            "name": "Junior Dev",
            "email": "junior@example.com",
            "technical_skills": [
                {"name": "Python", "level": "Beginner", "years": 1}
            ]
        },
        "offers": [
            {
                "id": "junior_job_001",
                "title": "Junior Developer",
                "company": "StartupCorp",
                "required_skills": ["Python"]
            }
        ],
        "algorithm": "auto"
    }'
    
    echo "📤 Sending minimal data request..."
    demo2_response=$(curl -s -X POST http://localhost:$port/api/v2/match \
        -H "Content-Type: application/json" \
        -d "$minimal_request")
    
    if echo "$demo2_response" | grep -q '"success":true'; then
        algorithm=$(echo "$demo2_response" | grep -o '"algorithm_used":"[^"]*"' | cut -d'"' -f4)
        score=$(echo "$demo2_response" | grep -o '"overall_score":[0-9.]*' | cut -d':' -f2)
        
        echo "✅ Algorithm selected: $algorithm"
        echo "📊 Match score: $score"
    else
        echo "❌ Demo 2 failed"
    fi
    
    echo
    echo -e "${GREEN}🎉 Demonstration completed!${NC}"
    echo
    echo "📋 Service Information:"
    echo "   - V2 API: http://localhost:$port/api/v2/match"
    echo "   - V1 Compatible: http://localhost:$port/match"
    echo "   - Documentation: http://localhost:$port/api/docs"
    echo "   - Health: http://localhost:$port/health"
    echo "   - Stats: http://localhost:$port/stats"
}

# Clean up temporary files
clean_up() {
    log "Cleaning up temporary files..."
    
    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # Remove test artifacts
    rm -rf .pytest_cache 2>/dev/null || true
    rm -rf htmlcov 2>/dev/null || true
    rm -f .coverage 2>/dev/null || true
    
    success "Cleanup completed"
}

# Parse command line arguments
parse_args() {
    local port=$DEFAULT_PORT
    local host=$DEFAULT_HOST
    local env=$DEFAULT_ENV
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --port)
                port="$2"
                shift 2
                ;;
            --host)
                host="$2"
                shift 2
                ;;
            --env)
                env="$2"
                shift 2
                ;;
            *)
                break
                ;;
        esac
    done
    
    echo "$port $host $env"
}

# Main function
main() {
    show_banner
    
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 0
    fi
    
    local command=$1
    shift
    
    # Parse remaining arguments
    local args=($(parse_args "$@"))
    local port=${args[0]}
    local host=${args[1]}
    local env=${args[2]}
    
    case $command in
        "start")
            check_python
            setup_env
            start_service "$port" "$host" "$env"
            ;;
        "dev")
            check_python
            setup_env
            start_dev "$port" "$host"
            ;;
        "test")
            run_test "$port"
            ;;
        "demo")
            run_demo "$port"
            ;;
        "install")
            check_python
            install_dependencies
            ;;
        "clean")
            clean_up
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
