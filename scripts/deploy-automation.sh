#!/bin/bash

# ===========================================
# SuperSmartMatch V2 - Deployment Automation Script
# Gestion des conflits locaux et déploiement complet
# Version macOS Compatible
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🚀 SuperSmartMatch V2 - Automated Deployment Manager${NC}"
echo -e "${PURPLE}===============================================${NC}"

# Functions
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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Check current git status
check_git_status() {
    log_step "Checking Git status and modified files..."
    
    if git status --porcelain | grep -q "^M"; then
        log_warning "Modified files detected:"
        git status --short | grep "^M"
        echo ""
        return 1
    else
        log_success "Working directory is clean"
        return 0
    fi
}

# Handle modified files
handle_modified_files() {
    log_step "Handling modified files..."
    
    echo -e "${YELLOW}Options to handle modified files:${NC}"
    echo "1. Stash changes and continue (Recommended)"
    echo "2. Commit changes and merge"
    echo "3. Reset hard to remote branch (WARNING: loses local changes)"
    echo "4. Show differences first"
    echo "5. Exit and handle manually"
    
    read -p "Choose option (1-5): " choice
    
    case $choice in
        1)
            log_info "Stashing local changes..."
            git stash push -m "Local changes backup - $(date)"
            git reset --hard origin/microservices-refactor
            log_success "Changes stashed and reset to remote branch"
            log_info "To recover stashed changes later: git stash pop"
            ;;
        2)
            log_info "Committing local changes..."
            git add .
            git commit -m "Local modifications before microservices deployment - $(date)"
            log_info "Merging with remote branch..."
            git merge origin/microservices-refactor
            log_success "Changes committed and merged"
            ;;
        3)
            log_warning "This will permanently delete your local changes!"
            read -p "Are you sure? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                git reset --hard origin/microservices-refactor
                log_success "Reset to remote branch completed"
            else
                log_info "Operation cancelled"
                exit 1
            fi
            ;;
        4)
            log_info "Showing differences for modified files..."
            git diff HEAD
            echo ""
            log_info "Re-run script to choose an action"
            exit 0
            ;;
        5)
            log_info "Exiting. Please handle the modified files manually"
            echo ""
            echo "Manual commands you can use:"
            echo "  git stash                    # Save changes temporarily"
            echo "  git reset --hard HEAD        # Discard changes"
            echo "  git add . && git commit      # Commit changes"
            exit 0
            ;;
        *)
            log_error "Invalid option"
            exit 1
            ;;
    esac
}

# Generate secure environment configuration (macOS compatible)
generate_env_config() {
    log_step "Setting up environment configuration..."
    
    if [ ! -f ".env.production" ]; then
        if [ -f ".env.production.template" ]; then
            log_info "Creating .env.production from template..."
            cp .env.production.template .env.production
            
            # Generate secure passwords (macOS compatible)
            log_info "Generating secure passwords..."
            
            # Generate passwords without special characters that cause sed issues
            JWT_SECRET=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 64)
            REDIS_PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32)
            POSTGRES_PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32)
            MINIO_SECRET_KEY=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32)
            GRAFANA_ADMIN_PASSWORD=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 16)
            GRAFANA_SECRET_KEY=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 32)
            
            # Use Python for safer text replacement (available on macOS)
            log_info "Updating configuration with secure values..."
            
            # Create a temporary Python script for text replacement
            cat > temp_replace.py << EOF
import sys
import re

# Read the file
with open('.env.production', 'r') as f:
    content = f.read()

# Define replacements
replacements = {
    'your_super_secure_jwt_secret_change_this_in_production_512bits_minimum': '$JWT_SECRET',
    'your_secure_redis_password_change_this': '$REDIS_PASSWORD',
    'your_secure_postgres_password_change_this': '$POSTGRES_PASSWORD',
    'your_secure_minio_secret_key_change_this': '$MINIO_SECRET_KEY',
    'your_secure_grafana_password_change_this': '$GRAFANA_ADMIN_PASSWORD',
    'your_secure_grafana_secret_key_change_this': '$GRAFANA_SECRET_KEY'
}

# Apply replacements
for old, new in replacements.items():
    content = content.replace(old, new)

# Write back to file
with open('.env.production', 'w') as f:
    f.write(content)

print("Configuration updated successfully")
EOF
            
            # Execute the Python script with environment variables
            JWT_SECRET="$JWT_SECRET" \
            REDIS_PASSWORD="$REDIS_PASSWORD" \
            POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
            MINIO_SECRET_KEY="$MINIO_SECRET_KEY" \
            GRAFANA_ADMIN_PASSWORD="$GRAFANA_ADMIN_PASSWORD" \
            GRAFANA_SECRET_KEY="$GRAFANA_SECRET_KEY" \
            python3 -c "
import os
replacements = {
    'your_super_secure_jwt_secret_change_this_in_production_512bits_minimum': os.environ['JWT_SECRET'],
    'your_secure_redis_password_change_this': os.environ['REDIS_PASSWORD'], 
    'your_secure_postgres_password_change_this': os.environ['POSTGRES_PASSWORD'],
    'your_secure_minio_secret_key_change_this': os.environ['MINIO_SECRET_KEY'],
    'your_secure_grafana_password_change_this': os.environ['GRAFANA_ADMIN_PASSWORD'],
    'your_secure_grafana_secret_key_change_this': os.environ['GRAFANA_SECRET_KEY']
}

with open('.env.production', 'r') as f:
    content = f.read()

for old, new in replacements.items():
    content = content.replace(old, new)

with open('.env.production', 'w') as f:
    f.write(content)
"
            
            # Clean up
            rm -f temp_replace.py
            
            log_success "Environment file created with secure passwords"
            log_warning "IMPORTANT: Save these credentials securely!"
            echo ""
            echo -e "${GREEN}Generated Passwords:${NC}"
            echo -e "${YELLOW}Grafana Admin: admin / $GRAFANA_ADMIN_PASSWORD${NC}"
            echo -e "${YELLOW}PostgreSQL: ssm_user / $POSTGRES_PASSWORD${NC}"
            echo -e "${YELLOW}Redis: $REDIS_PASSWORD${NC}"
            echo ""
        else
            log_error ".env.production.template not found"
            exit 1
        fi
    else
        log_success ".env.production already exists"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_step "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        echo "Please install Docker Desktop for Mac: https://docs.docker.com/desktop/mac/"
        exit 1
    fi
    log_success "Docker is installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        echo "Please install Docker Desktop for Mac which includes Docker Compose"
        exit 1
    fi
    log_success "Docker Compose is installed"
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        echo "Please start Docker Desktop"
        exit 1
    fi
    log_success "Docker is running"
    
    # Check Python3 availability
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is not available"
        echo "Python3 is required for configuration generation"
        exit 1
    fi
    log_success "Python3 is available"
    
    # Check available disk space (minimum 10GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ $available_space -lt 10485760 ]; then
        log_warning "Less than 10GB disk space available. Deployment may fail."
    else
        log_success "Sufficient disk space available"
    fi
}

# Make scripts executable
setup_scripts() {
    log_step "Setting up deployment scripts..."
    
    if [ -d "scripts" ]; then
        chmod +x scripts/*.sh
        log_success "Scripts made executable"
    else
        log_error "Scripts directory not found"
        exit 1
    fi
}

# Run deployment
run_deployment() {
    log_step "Starting microservices deployment..."
    
    # Check if deployment script exists
    if [ ! -f "scripts/deploy-production.sh" ]; then
        log_error "Deployment script not found"
        exit 1
    fi
    
    # Run deployment with detailed output
    log_info "Executing deployment script..."
    echo ""
    
    ./scripts/deploy-production.sh deploy
    
    echo ""
    log_success "Deployment script completed"
}

# Quick health check
quick_health_check() {
    log_step "Running quick health checks..."
    
    log_info "Waiting for services to stabilize..."
    sleep 15  # Wait for services to stabilize
    
    # Test main endpoints
    endpoints=(
        "http://localhost/health:Load Balancer"
        "http://localhost/api/health:API Gateway"
        "http://localhost:5051/health:CV Parser"
        "http://localhost:5052/health:Matching Service"
        "http://localhost:5053/health:Job Parser"
        "http://localhost:5054/health:User Service"
        "http://localhost:5055/health:Notification Service"
        "http://localhost:5056/health:Analytics Service"
    )
    
    failed_checks=0
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r url service <<< "$endpoint_info"
        if curl -f "$url" > /dev/null 2>&1; then
            log_success "✅ $service is healthy"
        else
            log_error "❌ $service health check failed"
            ((failed_checks++))
        fi
    done
    
    # Check monitoring endpoints
    if curl -f "http://localhost:3000/api/health" > /dev/null 2>&1; then
        log_success "✅ Grafana is accessible"
    else
        log_warning "⚠️ Grafana may not be fully ready yet"
    fi
    
    if curl -f "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
        log_success "✅ Prometheus is healthy"
    else
        log_warning "⚠️ Prometheus may not be fully ready yet"
    fi
    
    echo ""
    if [ $failed_checks -eq 0 ]; then
        log_success "🎉 All core services are healthy!"
    else
        log_warning "⚠️ $failed_checks service(s) failed health checks. They may need more time to start."
        log_info "You can check logs with: docker-compose -f docker-compose.production.yml logs -f"
    fi
}

# Show access information
show_access_info() {
    log_step "Deployment completed! Access information:"
    
    echo ""
    echo -e "${GREEN}🌐 Application Access Points:${NC}"
    echo "  • Main Application: http://localhost"
    echo "  • API Gateway: http://localhost/api"
    echo "  • API Health: http://localhost/api/health"
    echo ""
    echo -e "${GREEN}📊 Monitoring Dashboards:${NC}"
    echo "  • Grafana: http://localhost:3000"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • MinIO Console: http://localhost:9001"
    echo ""
    echo -e "${GREEN}🔧 Individual Services:${NC}"
    echo "  • CV Parser: http://localhost:5051"
    echo "  • Matching: http://localhost:5052"
    echo "  • Job Parser: http://localhost:5053"
    echo "  • User Service: http://localhost:5054"
    echo "  • Notifications: http://localhost:5055"
    echo "  • Analytics: http://localhost:5056"
    echo ""
    echo -e "${GREEN}📋 Useful Commands:${NC}"
    echo "  • View logs: docker-compose -f docker-compose.production.yml logs -f"
    echo "  • Stop services: ./scripts/deploy-production.sh stop"
    echo "  • Restart: ./scripts/deploy-production.sh restart"
    echo "  • Full tests: ./scripts/test-integration-complete.sh all"
    echo ""
    
    # Show credentials
    if [ -f ".env.production" ]; then
        grafana_password=$(grep "GRAFANA_ADMIN_PASSWORD" .env.production | cut -d'=' -f2)
        echo -e "${YELLOW}🔑 Important Credentials:${NC}"
        echo "  • Grafana Dashboard: admin / $grafana_password"
        echo ""
        echo -e "${BLUE}💡 Next Steps:${NC}"
        echo "  1. Test API: curl http://localhost/api/health"
        echo "  2. Open Grafana: http://localhost:3000"
        echo "  3. Run tests: ./scripts/test-integration-complete.sh all"
        echo ""
    fi
}

# Main execution flow
main() {
    echo ""
    
    # Step 1: Check git status
    if ! check_git_status; then
        handle_modified_files
    fi
    
    # Step 2: Check prerequisites
    check_prerequisites
    
    # Step 3: Setup environment
    generate_env_config
    
    # Step 4: Setup scripts
    setup_scripts
    
    # Step 5: Ask for confirmation
    echo ""
    log_warning "Ready to deploy SuperSmartMatch V2 microservices architecture"
    echo "This will:"
    echo "  • Build and deploy 7 microservices"
    echo "  • Setup complete infrastructure (PostgreSQL, Redis, MinIO, Nginx)"
    echo "  • Configure monitoring (Prometheus, Grafana)"
    echo "  • Run integration tests"
    echo ""
    read -p "Proceed with deployment? (y/N): " confirm
    
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled by user"
        exit 0
    fi
    
    # Step 6: Run deployment
    run_deployment
    
    # Step 7: Health checks
    quick_health_check
    
    # Step 8: Show access info
    show_access_info
    
    echo ""
    log_success "🎉 SuperSmartMatch V2 microservices deployment completed successfully!"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "check")
        check_git_status
        check_prerequisites
        ;;
    "env")
        generate_env_config
        ;;
    "health")
        quick_health_check
        ;;
    *)
        echo "Usage: $0 {deploy|check|env|health}"
        echo ""
        echo "Commands:"
        echo "  deploy  - Full automated deployment (default)"
        echo "  check   - Check prerequisites and git status"
        echo "  env     - Generate environment configuration only"
        echo "  health  - Run health checks on deployed services"
        exit 1
        ;;
esac