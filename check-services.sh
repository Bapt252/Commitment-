#!/bin/bash

# Script de vérification des services Commitment
# Usage: ./check-services.sh

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 VÉRIFICATION DES SERVICES COMMITMENT${NC}"
echo "==============================================="

# Function pour vérifier le statut d'un container
check_container() {
    local container_name=$1
    local status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null || echo "not_found")
    
    if [ "$status" = "running" ]; then
        echo -e "${GREEN}✅ $container_name: Running${NC}"
        return 0
    elif [ "$status" = "not_found" ]; then
        echo -e "${RED}❌ $container_name: Not found${NC}"
        return 1
    else
        echo -e "${RED}❌ $container_name: $status${NC}"
        return 1
    fi
}

# Function pour vérifier les endpoints de santé
check_health_endpoint() {
    local service_name=$1
    local url=$2
    local timeout=${3:-5}
    
    echo -n "   Testing health endpoint... "
    if curl -f -s --max-time $timeout "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health OK${NC}"
        return 0
    else
        echo -e "${RED}❌ Health FAIL${NC}"
        return 1
    fi
}

echo -e "\n${YELLOW}📦 1. VÉRIFICATION DES CONTAINERS${NC}"
echo "-----------------------------------"

# Infrastructure
echo -e "\n${BLUE}Infrastructure:${NC}"
check_container "nexten-postgres"
check_container "nexten-redis"  
check_container "nexten-minio"

# Services principaux
echo -e "\n${BLUE}Services principaux:${NC}"
check_container "nexten-api"
check_container "nexten-cv-parser"
check_container "nexten-job-parser"
check_container "nexten-matching-api"
check_container "nexten-personalization"
check_container "nexten-user-behavior"
check_container "nexten-feedback"
check_container "nexten-data-adapter"
check_container "nexten-frontend"

# Services de monitoring
echo -e "\n${BLUE}Monitoring:${NC}"
check_container "nexten-redis-commander"
check_container "nexten-rq-dashboard"

echo -e "\n${YELLOW}🌐 2. VÉRIFICATION DES ENDPOINTS${NC}"
echo "------------------------------------"

echo -e "\n${BLUE}Services avec endpoints /health:${NC}"
check_health_endpoint "API Backend" "http://localhost:5050/health"
check_health_endpoint "CV Parser" "http://localhost:5051/health"
check_health_endpoint "Job Parser" "http://localhost:5055/health"
check_health_endpoint "Matching API" "http://localhost:5052/health"
check_health_endpoint "Personalization" "http://localhost:5060/health"
check_health_endpoint "User Behavior" "http://localhost:5057/health"
check_health_endpoint "Feedback Service" "http://localhost:5058/health"

echo -e "\n${BLUE}Frontend et interfaces:${NC}"
check_health_endpoint "Frontend Next.js" "http://localhost:3000" 10
check_health_endpoint "MinIO Console" "http://localhost:9001" 5
check_health_endpoint "Redis Commander" "http://localhost:8081" 5
check_health_endpoint "RQ Dashboard" "http://localhost:9181" 5

echo -e "\n${YELLOW}📊 3. RÉSUMÉ DES PORTS${NC}"
echo "----------------------"
echo -e "${BLUE}Services fonctionnels:${NC}"
echo "  • Backend API:       http://localhost:5050"
echo "  • CV Parser:         http://localhost:5051"  
echo "  • Matching API:      http://localhost:5052"
echo "  • Data Adapter:      http://localhost:5053"
echo "  • Job Parser:        http://localhost:5055"
echo "  • User Behavior:     http://localhost:5057"
echo "  • Feedback Service:  http://localhost:5058"
echo "  • Personalization:   http://localhost:5060"

echo -e "\n${BLUE}Interfaces utilisateur:${NC}"
echo "  • Frontend:          http://localhost:3000"
echo "  • MinIO Console:     http://localhost:9001"
echo "  • Redis Commander:   http://localhost:8081"
echo "  • RQ Dashboard:      http://localhost:9181"

echo -e "\n${YELLOW}🔧 4. COMMANDES UTILES${NC}"
echo "----------------------"
echo "Voir les logs d'un service:"
echo "  docker logs nexten-<service-name> -f"
echo ""
echo "Redémarrer un service:"
echo "  docker-compose restart <service-name>"
echo ""
echo "Voir l'état détaillé:"
echo "  docker-compose ps"
echo ""
echo "Rebuilder et relancer:"
echo "  docker-compose up -d --build <service-name>"

echo -e "\n${GREEN}✨ Vérification terminée !${NC}"
