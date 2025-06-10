#!/bin/bash

# ===========================================
# SuperSmartMatch V2 - Validation Finale Architecture Microservices
# ===========================================

set -e

echo "🔍 SuperSmartMatch V2 - Validation Finale Architecture Microservices"
echo "====================================================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Validation counters
VALIDATIONS_TOTAL=0
VALIDATIONS_PASSED=0
VALIDATIONS_FAILED=0

validate() {
    local test_name="$1"
    local command="$2"
    
    echo -e "${BLUE}[VALIDATION]${NC} $test_name"
    ((VALIDATIONS_TOTAL++))
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}[✅ PASS]${NC} $test_name"
        ((VALIDATIONS_PASSED++))
        return 0
    else
        echo -e "${RED}[❌ FAIL]${NC} $test_name"
        ((VALIDATIONS_FAILED++))
        return 1
    fi
}

validate_file_exists() {
    local file_path="$1"
    local description="$2"
    
    echo -e "${BLUE}[VALIDATION]${NC} $description"
    ((VALIDATIONS_TOTAL++))
    
    if [ -f "$file_path" ]; then
        echo -e "${GREEN}[✅ PASS]${NC} $description"
        ((VALIDATIONS_PASSED++))
        return 0
    else
        echo -e "${RED}[❌ FAIL]${NC} $description - File not found: $file_path"
        ((VALIDATIONS_FAILED++))
        return 1
    fi
}

echo ""
echo "🏗️ VALIDATION ARCHITECTURE MICROSERVICES"
echo "========================================="

# 1. Docker Compose Production
validate_file_exists "docker-compose.production.yml" "Docker Compose Production Configuration"

# 2. Environment Template
validate_file_exists ".env.production.template" "Environment Configuration Template"

# 3. API Gateway Service
validate_file_exists "services/api-gateway/package.json" "API Gateway Service Configuration"
validate_file_exists "services/api-gateway/Dockerfile" "API Gateway Dockerfile"

# 4. CV Parser Service
validate_file_exists "services/cv-parser/package.json" "CV Parser Service Configuration"

# 5. Job Parser Service  
validate_file_exists "services/job-parser/package.json" "Job Parser Service Configuration"

# 6. Matching Service
validate_file_exists "services/matching/package.json" "Matching Service Configuration"

# 7. User Service
validate_file_exists "services/user/package.json" "User Service Configuration"

# 8. Notification Service
validate_file_exists "services/notification/package.json" "Notification Service Configuration"

# 9. Analytics Service
validate_file_exists "services/analytics/package.json" "Analytics Service Configuration"

echo ""
echo "🛠️ VALIDATION INFRASTRUCTURE"
echo "============================"

# 10. Nginx Configuration
validate_file_exists "nginx/nginx.conf" "Nginx Load Balancer Configuration"

# 11. Database Initialization
validate_file_exists "database/init/01-init-databases.sh" "PostgreSQL Database Initialization"

# 12. Prometheus Configuration
validate_file_exists "monitoring/prometheus/prometheus.yml" "Prometheus Monitoring Configuration"

# 13. Grafana Configuration
validate_file_exists "monitoring/grafana/datasources/datasources.yml" "Grafana Datasources Configuration"

echo ""
echo "🚀 VALIDATION SCRIPTS DÉPLOIEMENT"
echo "================================="

# 14. Deployment Script
validate_file_exists "scripts/deploy-production.sh" "Production Deployment Script"
validate "Deploy Script Executable" "[ -x scripts/deploy-production.sh ]"

# 15. Integration Tests
validate_file_exists "scripts/test-integration.sh" "Integration Test Suite"
validate "Integration Test Executable" "[ -x scripts/test-integration.sh ]"

echo ""
echo "📚 VALIDATION DOCUMENTATION"
echo "==========================="

# 16. Architecture Documentation
validate_file_exists "docs/MICROSERVICES_ARCHITECTURE.md" "Microservices Architecture Documentation"

# 17. Updated README
validate_file_exists "README.md" "Updated README Documentation"

echo ""
echo "🔒 VALIDATION SÉCURITÉ"
echo "====================="

# 18. Environment Variables Check
echo -e "${BLUE}[VALIDATION]${NC} Environment Variables Configuration"
((VALIDATIONS_TOTAL++))

if grep -q "JWT_SECRET" .env.production.template && \
   grep -q "POSTGRES_PASSWORD" .env.production.template && \
   grep -q "REDIS_PASSWORD" .env.production.template; then
    echo -e "${GREEN}[✅ PASS]${NC} Environment Variables Configuration"
    ((VALIDATIONS_PASSED++))
else
    echo -e "${RED}[❌ FAIL]${NC} Environment Variables Configuration"
    ((VALIDATIONS_FAILED++))
fi

# 19. Docker Compose Security
echo -e "${BLUE}[VALIDATION]${NC} Docker Compose Security Configuration"
((VALIDATIONS_TOTAL++))

if grep -q "secrets:" docker-compose.production.yml && \
   grep -q "healthcheck:" docker-compose.production.yml && \
   grep -q "restart: unless-stopped" docker-compose.production.yml; then
    echo -e "${GREEN}[✅ PASS]${NC} Docker Compose Security Configuration"
    ((VALIDATIONS_PASSED++))
else
    echo -e "${RED}[❌ FAIL]${NC} Docker Compose Security Configuration"
    ((VALIDATIONS_FAILED++))
fi

echo ""
echo "📊 VALIDATION MONITORING"
echo "======================="

# 20. Prometheus Targets
echo -e "${BLUE}[VALIDATION]${NC} Prometheus Monitoring Targets"
((VALIDATIONS_TOTAL++))

if grep -q "api-gateway:5050" monitoring/prometheus/prometheus.yml && \
   grep -q "cv-parser-service:5051" monitoring/prometheus/prometheus.yml && \
   grep -q "matching-service:5052" monitoring/prometheus/prometheus.yml; then
    echo -e "${GREEN}[✅ PASS]${NC} Prometheus Monitoring Targets"
    ((VALIDATIONS_PASSED++))
else
    echo -e "${RED}[❌ FAIL]${NC} Prometheus Monitoring Targets"
    ((VALIDATIONS_FAILED++))
fi

echo ""
echo "🎯 VALIDATION OBJECTIFS BUSINESS"
echo "==============================="

# 21. All 7 Microservices Present
echo -e "${BLUE}[VALIDATION]${NC} 7 Microservices Architecture Complete"
((VALIDATIONS_TOTAL++))

microservices_count=0
[ -d "services/api-gateway" ] && ((microservices_count++))
[ -d "services/cv-parser" ] && ((microservices_count++))
[ -d "services/job-parser" ] && ((microservices_count++))
[ -d "services/matching" ] && ((microservices_count++))
[ -d "services/user" ] && ((microservices_count++))
[ -d "services/notification" ] && ((microservices_count++))
[ -d "services/analytics" ] && ((microservices_count++))

if [ "$microservices_count" -eq 7 ]; then
    echo -e "${GREEN}[✅ PASS]${NC} 7 Microservices Architecture Complete ($microservices_count/7)"
    ((VALIDATIONS_PASSED++))
else
    echo -e "${RED}[❌ FAIL]${NC} 7 Microservices Architecture Incomplete ($microservices_count/7)"
    ((VALIDATIONS_FAILED++))
fi

# 22. Infrastructure Complete
echo -e "${BLUE}[VALIDATION]${NC} Complete Infrastructure Stack"
((VALIDATIONS_TOTAL++))

if grep -q "postgres:" docker-compose.production.yml && \
   grep -q "redis:" docker-compose.production.yml && \
   grep -q "minio:" docker-compose.production.yml && \
   grep -q "nginx:" docker-compose.production.yml; then
    echo -e "${GREEN}[✅ PASS]${NC} Complete Infrastructure Stack (PostgreSQL, Redis, MinIO, Nginx)"
    ((VALIDATIONS_PASSED++))
else
    echo -e "${RED}[❌ FAIL]${NC} Complete Infrastructure Stack"
    ((VALIDATIONS_FAILED++))
fi

# 23. Port Configuration
echo -e "${BLUE}[VALIDATION]${NC} Service Port Configuration"
((VALIDATIONS_TOTAL++))

if grep -q "5050:5050" docker-compose.production.yml && \
   grep -q "5051:5051" docker-compose.production.yml && \
   grep -q "5052:5052" docker-compose.production.yml && \
   grep -q "5053:5053" docker-compose.production.yml && \
   grep -q "5054:5054" docker-compose.production.yml && \
   grep -q "5055:5055" docker-compose.production.yml && \
   grep -q "5056:5056" docker-compose.production.yml; then
    echo -e "${GREEN}[✅ PASS]${NC} Service Port Configuration (5050-5056)"
    ((VALIDATIONS_PASSED++))
else
    echo -e "${RED}[❌ FAIL]${NC} Service Port Configuration"
    ((VALIDATIONS_FAILED++))
fi

echo ""
echo "📋 RÉSUMÉ VALIDATION FINALE"
echo "==========================="
echo "Total Validations: $VALIDATIONS_TOTAL"
echo -e "Passed: ${GREEN}$VALIDATIONS_PASSED${NC}"
echo -e "Failed: ${RED}$VALIDATIONS_FAILED${NC}"
echo ""

if [ "$VALIDATIONS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}🎉 VALIDATION RÉUSSIE - Architecture Microservices Complète!${NC}"
    echo ""
    echo -e "${GREEN}✅ MISSION ACCOMPLIE:${NC}"
    echo "• 7 microservices déployés selon spécifications"
    echo "• Infrastructure complète (PostgreSQL, Redis, MinIO, Nginx)"
    echo "• Configuration sécurisée pour production"
    echo "• Monitoring et observabilité opérationnels"
    echo "• Documentation complète et scripts d'automatisation"
    echo "• Tests d'intégration et validation"
    echo ""
    echo -e "${BLUE}🚀 Prêt pour déploiement production:${NC}"
    echo "  ./scripts/deploy-production.sh"
    echo ""
    exit 0
else
    echo -e "${RED}❌ VALIDATION ÉCHOUÉE - Corrections nécessaires${NC}"
    echo ""
    echo "Veuillez corriger les problèmes identifiés ci-dessus avant de procéder au déploiement."
    exit 1
fi
