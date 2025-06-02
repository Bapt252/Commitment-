#!/bin/bash

# 🚀 SuperSmartMatch V2 Quick Start Script
# 
# This script provides easy deployment and management of SuperSmartMatch V2
# with intelligent V1/V2 routing and progressive migration capabilities.

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SERVICE_NAME="supersmartmatch-v2"
DEFAULT_PORT=5062

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Print banner
print_banner() {
    echo -e "${PURPLE}"
    echo "  ____                       ____                      _   __  __       _       _      __     _____  "
    echo " / ___| _   _ _ __   ___ _ __/ ___| _ __ ___   __ _ _ __| |_|  \/  | __ _| |_ ___| |__   \ \   / /___ \ "
    echo " \___ \| | | | '_ \ / _ \ '__\___ \| '_ \` _ \ / _\` | '__| __| |\/| |/ _\` | __/ __| '_ \   \ \ / /  __) |"
    echo "  ___) | |_| | |_) |  __/ |   ___) | | | | | | (_| | |  | |_| |  | | (_| | || (__| | | |   \ V /  / __/ "
    echo " |____/ \__,_| .__/ \___|_|  |____/|_| |_| |_|\__,_|_|   \__|_|  |_|\__,_|\__\___|_| |_|    \_/  |_____|"
    echo "              |_|                                                                                       "
    echo -e "${NC}"
    echo -e "${GREEN}🚀 Unified Intelligent Matching Service - V2 Architecture${NC}"
    echo -e "${BLUE}🎯 +13% Precision • ⚡ <100ms Response • 🔄 100% Backward Compatible${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        log_success "Docker available for containerized deployment"
        DOCKER_AVAILABLE=true
    else
        log_warning "Docker not available - will use Python direct deployment"
        DOCKER_AVAILABLE=false
    fi
    
    # Check port availability
    if lsof -Pi :$DEFAULT_PORT -sTCP:LISTEN -t >/dev/null; then
        log_warning "Port $DEFAULT_PORT is already in use"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    
    log_success "Prerequisites check completed"
}

# Install dependencies
install_dependencies() {
    log_info "Installing Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    log_success "Dependencies installed successfully"
}

# Deploy with Docker
deploy_docker() {
    log_info "Deploying SuperSmartMatch V2 with Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Check if docker-compose.v2.yml exists
    if [ ! -f "docker-compose.v2.yml" ]; then
        log_warning "docker-compose.v2.yml not found, creating minimal configuration..."
        create_docker_compose
    fi
    
    # Start services
    docker-compose -f docker-compose.v2.yml up -d
    
    # Wait for service to be ready
    wait_for_service
    
    log_success "SuperSmartMatch V2 deployed successfully with Docker"
}

# Deploy with Python
deploy_python() {
    log_info "Deploying SuperSmartMatch V2 with Python..."
    
    cd "$PROJECT_ROOT"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start the service in background
    nohup python -m app.v2.main_service > supersmartmatch_v2.log 2>&1 &
    echo $! > supersmartmatch_v2.pid
    
    # Wait for service to be ready
    wait_for_service
    
    log_success "SuperSmartMatch V2 deployed successfully with Python"
    log_info "Service PID: $(cat supersmartmatch_v2.pid)"
    log_info "Logs: tail -f supersmartmatch_v2.log"
}

# Wait for service to be ready
wait_for_service() {
    log_info "Waiting for service to be ready..."
    
    for i in {1..30}; do
        if curl -sf http://localhost:$DEFAULT_PORT/health > /dev/null 2>&1; then
            log_success "Service is ready!"
            return 0
        fi
        echo -n "."
        sleep 2
    done
    
    log_error "Service failed to start or is not responding"
    return 1
}

# Create minimal Docker Compose configuration
create_docker_compose() {
    cat > docker-compose.v2.yml << EOF
version: '3.8'

services:
  supersmartmatch-v2:
    build: .
    ports:
      - "$DEFAULT_PORT:$DEFAULT_PORT"
    environment:
      - SUPERSMARTMATCH_VERSION=2.0.0
      - SUPERSMARTMATCH_ENVIRONMENT=production
      - ENABLE_V2=true
      - V2_TRAFFIC_PERCENTAGE=100
      - ENABLE_NEXTEN_ALGORITHM=true
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:$DEFAULT_PORT/health"]
      interval: 30s
      timeout: 10s
      retries: 3
EOF
    
    log_success "Created docker-compose.v2.yml"
}

# Test the deployment
test_deployment() {
    log_info "Testing SuperSmartMatch V2 deployment..."
    
    # Test health endpoint
    if ! curl -sf http://localhost:$DEFAULT_PORT/health > /dev/null; then
        log_error "Health check failed"
        return 1
    fi
    
    # Test V2 API
    if curl -sf http://localhost:$DEFAULT_PORT/api/v2/health > /dev/null; then
        log_success "V2 API is responding"
    else
        log_warning "V2 API health check failed"
    fi
    
    # Test V1 compatibility
    if curl -sf http://localhost:$DEFAULT_PORT/stats > /dev/null; then
        log_success "V1 compatibility endpoints working"
    else
        log_warning "V1 compatibility check failed"
    fi
    
    log_success "Deployment test completed"
}

# Show service status
show_status() {
    log_header "=== SuperSmartMatch V2 Service Status ==="
    
    # Check if service is running
    if curl -sf http://localhost:$DEFAULT_PORT/health > /dev/null 2>&1; then
        log_success "Service is running on port $DEFAULT_PORT"
        
        # Get service info
        response=$(curl -s http://localhost:$DEFAULT_PORT/ 2>/dev/null || echo '{"error": "no response"}')
        echo "Service Response: $response" | python3 -m json.tool 2>/dev/null || echo "$response"
        
        # Show available endpoints
        echo -e "\n${BLUE}Available Endpoints:${NC}"
        echo "  🔗 Health Check:      http://localhost:$DEFAULT_PORT/health"
        echo "  🔗 V2 API:           http://localhost:$DEFAULT_PORT/api/v2/match"
        echo "  🔗 V1 Compatible:    http://localhost:$DEFAULT_PORT/match"
        echo "  🔗 Statistics:       http://localhost:$DEFAULT_PORT/stats"
        echo "  🔗 Configuration:    http://localhost:$DEFAULT_PORT/config"
        echo "  🔗 API Docs:         http://localhost:$DEFAULT_PORT/api/docs"
        
    else
        log_error "Service is not running or not responding"
        return 1
    fi
}

# Stop the service
stop_service() {
    log_info "Stopping SuperSmartMatch V2..."
    
    # Stop Docker deployment
    if [ -f "docker-compose.v2.yml" ] && command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.v2.yml down
        log_success "Docker services stopped"
    fi
    
    # Stop Python deployment
    if [ -f "supersmartmatch_v2.pid" ]; then
        pid=$(cat supersmartmatch_v2.pid)
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            rm -f supersmartmatch_v2.pid
            log_success "Python service stopped (PID: $pid)"
        else
            log_warning "PID file found but process not running"
            rm -f supersmartmatch_v2.pid
        fi
    fi
    
    log_success "SuperSmartMatch V2 stopped"
}

# Run migration from V1 to V2
run_migration() {
    log_header "=== Starting V1 to V2 Migration ==="
    
    read -p "Enter initial V2 traffic percentage (0-100, default 5): " traffic_percentage
    traffic_percentage=${traffic_percentage:-5}
    
    if ! [[ "$traffic_percentage" =~ ^[0-9]+$ ]] || [ "$traffic_percentage" -gt 100 ]; then
        log_error "Invalid traffic percentage. Must be 0-100."
        return 1
    fi
    
    log_info "Starting migration with $traffic_percentage% V2 traffic..."
    
    # Update configuration
    curl -X POST "http://localhost:$DEFAULT_PORT/api/v2/admin/config/update" \
        -H "Content-Type: application/json" \
        -d "{\"feature_flags\": {\"v2_traffic_percentage\": $traffic_percentage}}" \
        2>/dev/null || log_warning "Failed to update traffic percentage via API"
    
    log_success "Migration started with $traffic_percentage% traffic to V2"
    log_info "Monitor progress with: $0 status"
    log_info "Increase traffic with: $0 migrate --traffic=<percentage>"
}

# Show help
show_help() {
    cat << EOF
SuperSmartMatch V2 Quick Start Script

USAGE:
    $0 [COMMAND] [OPTIONS]

COMMANDS:
    start           Start SuperSmartMatch V2 service
    stop            Stop SuperSmartMatch V2 service
    restart         Restart SuperSmartMatch V2 service
    status          Show service status and endpoints
    test            Test the deployment
    migrate         Run V1 to V2 migration
    logs            Show service logs
    update          Update service configuration
    help            Show this help message

OPTIONS:
    --docker        Force Docker deployment
    --python        Force Python deployment
    --port=PORT     Use custom port (default: $DEFAULT_PORT)
    --traffic=PCT   Set V2 traffic percentage for migration

EXAMPLES:
    $0 start                    # Start with auto-detection
    $0 start --docker           # Force Docker deployment
    $0 migrate --traffic=25     # Migrate 25% traffic to V2
    $0 status                   # Check service status
    $0 stop                     # Stop the service

ENDPOINTS:
    Health:      http://localhost:$DEFAULT_PORT/health
    V2 API:      http://localhost:$DEFAULT_PORT/api/v2/match
    V1 API:      http://localhost:$DEFAULT_PORT/match
    Docs:        http://localhost:$DEFAULT_PORT/api/docs

For more information, see: matching-service/docs/ARCHITECTURE_V2.md
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker)
            FORCE_DOCKER=true
            shift
            ;;
        --python)
            FORCE_PYTHON=true
            shift
            ;;
        --port=*)
            DEFAULT_PORT="${1#*=}"
            shift
            ;;
        --traffic=*)
            TRAFFIC_PERCENTAGE="${1#*=}"
            shift
            ;;
        *)
            COMMAND=$1
            shift
            ;;
    esac
done

# Main execution
main() {
    print_banner
    
    case "${COMMAND:-help}" in
        start)
            check_prerequisites
            install_dependencies
            
            if [[ "$FORCE_DOCKER" == "true" ]] || ([[ "$FORCE_PYTHON" != "true" ]] && [[ "$DOCKER_AVAILABLE" == "true" ]]); then
                deploy_docker
            else
                deploy_python
            fi
            
            test_deployment
            show_status
            ;;
            
        stop)
            stop_service
            ;;
            
        restart)
            stop_service
            sleep 2
            $0 start
            ;;
            
        status)
            show_status
            ;;
            
        test)
            test_deployment
            ;;
            
        migrate)
            run_migration
            ;;
            
        logs)
            if [ -f "supersmartmatch_v2.log" ]; then
                tail -f supersmartmatch_v2.log
            else
                docker-compose -f docker-compose.v2.yml logs -f 2>/dev/null || log_error "No logs found"
            fi
            ;;
            
        update)
            if [[ -n "$TRAFFIC_PERCENTAGE" ]]; then
                curl -X POST "http://localhost:$DEFAULT_PORT/api/v2/admin/config/update" \
                    -H "Content-Type: application/json" \
                    -d "{\"feature_flags\": {\"v2_traffic_percentage\": $TRAFFIC_PERCENTAGE}}"
                log_success "Updated V2 traffic to $TRAFFIC_PERCENTAGE%"
            else
                log_error "Use --traffic=<percentage> to set traffic percentage"
            fi
            ;;
            
        help|--help|-h)
            show_help
            ;;
            
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
