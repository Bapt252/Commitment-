#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 NexTen Services Health Check${NC}"
echo -e "${BLUE}==============================${NC}\n"

# Vérifier que Docker est en cours d'exécution
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas en cours d'exécution ou vous n'avez pas les permissions${NC}"
    exit 1
fi

# Vérifier chaque service
services=("api" "cv-parser" "matching-api" "cv-parser-worker" "matching-worker-high" "matching-worker-standard" "matching-worker-bulk")

echo -e "${YELLOW}💻 Services Status:${NC}"
echo "------------------"

all_healthy=true

for service in "${services[@]}"; do
    container_name="nexten-${service}"
    
    # Vérifier si le conteneur existe
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        # Vérifier l'état du conteneur
        status=$(docker inspect -f '{{.State.Status}}' $container_name 2>/dev/null)
        health=$(docker inspect -f '{{.State.Health.Status}}' $container_name 2>/dev/null)
        
        if [ "$status" = "running" ]; then
            if [ "$health" = "healthy" ]; then
                echo -e "${GREEN}✓ $service: healthy${NC}"
            elif [ "$health" = "unhealthy" ]; then
                echo -e "${RED}✗ $service: unhealthy${NC}"
                all_healthy=false
            elif [ -z "$health" ]; then
                echo -e "${YELLOW}⚠️  $service: running (no healthcheck)${NC}"
            else
                echo -e "${YELLOW}⚠️  $service: $health${NC}"
            fi
        else
            echo -e "${RED}✗ $service: $status${NC}"
            all_healthy=false
        fi
    else
        echo -e "${RED}✗ $service: not found${NC}"
        all_healthy=false
    fi
done

# Vérifier l'utilisation des ressources
echo -e "\n${YELLOW}📊 Resource Usage:${NC}"
echo "----------------"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.PIDs}}" | grep "nexten-" || echo "No containers found"

# Vérifier les logs d'erreur récents
echo -e "\n${YELLOW}🚨 Recent Errors (last 5):${NC}"
echo "-------------------------"
error_count=0
for service in "${services[@]}"; do
    container_name="nexten-${service}"
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        errors=$(docker logs --tail=50 $container_name 2>&1 | grep -i "error\|exception\|failed" | tail -5)
        if [ ! -z "$errors" ]; then
            echo -e "${RED}$service:${NC}"
            echo "$errors"
            echo ""
            ((error_count++))
        fi
    fi
done

if [ $error_count -eq 0 ]; then
    echo -e "${GREEN}No recent errors found${NC}"
fi

# Vérifier les queues Redis
echo -e "\n${YELLOW}📦 Redis Queue Status:${NC}"
echo "--------------------"

# Vérifier si Redis Commander est accessible
if curl -s "http://localhost:8081" > /dev/null; then
    echo -e "${GREEN}✓ Redis Commander accessible at http://localhost:8081${NC}"
else
    echo -e "${YELLOW}⚠️  Redis Commander not accessible${NC}"
fi

# Vérifier si RQ Dashboard est accessible
if curl -s "http://localhost:9181" > /dev/null; then
    echo -e "${GREEN}✓ RQ Dashboard accessible at http://localhost:9181${NC}"
else
    echo -e "${YELLOW}⚠️  RQ Dashboard not accessible${NC}"
fi

# Résumé final
echo -e "\n${BLUE}=== Summary ===${NC}"
if [ "$all_healthy" = true ]; then
    echo -e "${GREEN}✅ All services are healthy${NC}"
else
    echo -e "${RED}⚠️  Some services need attention${NC}"
    echo -e "${YELLOW}Run 'docker-compose logs [service]' for more details${NC}"
fi

# Mode interactif pour plus de détails
echo -e "\n${YELLOW}📊 Want to see detailed logs for a specific service? (y/n)${NC}"
read -r answer

if [ "$answer" = "y" ]; then
    echo -e "${YELLOW}Available services:${NC}"
    for i in "${!services[@]}"; do
        echo "$((i+1)). ${services[$i]}"
    done
    
    echo -e "\n${YELLOW}Enter service number (1-${#services[@]}):${NC}"
    read -r choice
    
    if [[ "$choice" -ge 1 && "$choice" -le "${#services[@]}" ]]; then
        service_index=$((choice-1))
        service_name="nexten-${services[$service_index]}"
        echo -e "\n${BLUE}Logs for ${services[$service_index]}:${NC}"
        docker logs --tail=50 $service_name
    else
        echo -e "${RED}Invalid choice${NC}"
    fi
fi