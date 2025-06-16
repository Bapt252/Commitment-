#!/bin/bash

# 🔧 Script de diagnostic et résolution SuperSmartMatch V2
# Résout les problèmes de connectivité réseau et services en restart

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose-integrated.yml"
API_GATEWAY_PORT=5055

echo -e "${BLUE}🚀 SuperSmartMatch V2 - Diagnostic et Résolution des Problèmes${NC}"
echo -e "${BLUE}================================================================${NC}"

# Fonction utilitaire
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# 1. Vérification de l'environnement Docker
echo -e "\n${PURPLE}🔍 1. DIAGNOSTIC DE L'ENVIRONNEMENT${NC}"
echo "=================================================="

# Vérifier Docker
if command -v docker &> /dev/null; then
    print_status 0 "Docker est installé"
    DOCKER_VERSION=$(docker --version)
    echo "   Version: $DOCKER_VERSION"
else
    print_status 1 "Docker n'est pas installé"
    exit 1
fi

# Vérifier Docker Compose
if command -v docker-compose &> /dev/null; then
    print_status 0 "Docker Compose est disponible"
    COMPOSE_VERSION=$(docker-compose --version)
    echo "   Version: $COMPOSE_VERSION"
else
    print_status 1 "Docker Compose n'est pas installé"
    exit 1
fi

# Vérifier le daemon Docker
if docker info &> /dev/null; then
    print_status 0 "Docker daemon est actif"
else
    print_status 1 "Docker daemon n'est pas actif"
    print_info "Tentative de démarrage du daemon Docker..."
    sudo systemctl start docker || true
fi

# 2. Diagnostic des containers existants
echo -e "\n${PURPLE}🔍 2. DIAGNOSTIC DES CONTAINERS EXISTANTS${NC}"
echo "=================================================="

print_info "Containers actuellement en cours d'exécution:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

print_info "Tous les containers (y compris arrêtés):"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"

# Vérifier les containers en restart
RESTARTING_CONTAINERS=$(docker ps --filter "status=restarting" --format "{{.Names}}")
if [ -n "$RESTARTING_CONTAINERS" ]; then
    print_warning "Containers en restart détectés:"
    echo "$RESTARTING_CONTAINERS"
    
    print_info "Logs des containers en restart:"
    for container in $RESTARTING_CONTAINERS; do
        echo -e "\n${YELLOW}📋 Logs de $container:${NC}"
        docker logs --tail 20 "$container" || true
    done
fi

# 3. Diagnostic réseau
echo -e "\n${PURPLE}🔍 3. DIAGNOSTIC RÉSEAU DOCKER${NC}"
echo "=================================================="

print_info "Réseaux Docker existants:"
docker network ls

# Vérifier si le réseau supersmartmatch existe
if docker network ls | grep -q "supersmartmatch"; then
    print_status 0 "Réseau supersmartmatch existe"
    
    print_info "Détails du réseau supersmartmatch:"
    docker network inspect supersmartmatch | jq '.[0].Containers' 2>/dev/null || \
    docker network inspect supersmartmatch | grep -A 20 "Containers"
else
    print_status 1 "Réseau supersmartmatch n'existe pas"
fi

# 4. Test de connectivité réseau
echo -e "\n${PURPLE}🔍 4. TEST DE CONNECTIVITÉ RÉSEAU${NC}"
echo "=================================================="

# Services à tester
SERVICES=(
    "nexten-api:5000"
    "nexten-data-adapter:5052"
    "cv-parser:5051"
    "job-parser:5053"
    "matching-service:5060"
    "redis:6379"
    "postgres:5432"
)

# Tester depuis l'API Gateway s'il existe
if docker ps | grep -q "api-gateway-simple"; then
    print_info "Test de résolution DNS depuis api-gateway-simple:"
    
    for service in "${SERVICES[@]}"; do
        service_name=${service%:*}
        service_port=${service#*:}
        
        echo -n "   $service_name: "
        if docker exec api-gateway-simple nslookup "$service_name" &>/dev/null; then
            echo -e "${GREEN}✅ DNS OK${NC}"
            
            # Test de connectivité TCP
            if docker exec api-gateway-simple nc -z "$service_name" "$service_port" &>/dev/null; then
                echo -e "      ${GREEN}✅ TCP connectivité OK${NC}"
            else
                echo -e "      ${RED}❌ TCP connectivité échouée${NC}"
            fi
        else
            echo -e "${RED}❌ DNS échoué${NC}"
        fi
    done
else
    print_warning "Container api-gateway-simple non trouvé, test de connectivité ignoré"
fi

# 5. Vérification des ports
echo -e "\n${PURPLE}🔍 5. VÉRIFICATION DES PORTS${NC}"
echo "=================================================="

PORTS=(3000 5000 5051 5052 5053 5055 5060 6379 5432)

for port in "${PORTS[@]}"; do
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        print_status 0 "Port $port est utilisé"
    else
        print_status 1 "Port $port est libre"
    fi
done

# 6. Solutions automatiques
echo -e "\n${PURPLE}🔧 6. RÉSOLUTION AUTOMATIQUE DES PROBLÈMES${NC}"
echo "=================================================="

# Arrêter tous les containers existants
print_info "Arrêt de tous les containers existants..."
docker-compose -f docker-compose.yml down 2>/dev/null || true
docker-compose -f docker-compose-integrated.yml down 2>/dev/null || true

# Nettoyer les containers orphelins
print_info "Nettoyage des containers orphelins..."
docker container prune -f

# Nettoyer les réseaux orphelins
print_info "Nettoyage des réseaux orphelins..."
docker network prune -f

# Nettoyer les volumes orphelins (optionnel)
read -p "Voulez-vous nettoyer les volumes orphelins ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Nettoyage des volumes orphelins..."
    docker volume prune -f
fi

# Construire les images si nécessaire
print_info "Reconstruction des images si nécessaire..."
if [ -f "$COMPOSE_FILE" ]; then
    docker-compose -f "$COMPOSE_FILE" build --parallel
else
    print_warning "Fichier $COMPOSE_FILE non trouvé, reconstruction ignorée"
fi

# 7. Démarrage de la nouvelle configuration
echo -e "\n${PURPLE}🚀 7. DÉMARRAGE DE LA CONFIGURATION INTÉGRÉE${NC}"
echo "=================================================="

if [ -f "$COMPOSE_FILE" ]; then
    print_info "Démarrage des services intégrés..."
    
    # Démarrage progressif pour éviter les problèmes de dépendances
    print_info "1. Démarrage infrastructure (Redis + PostgreSQL)..."
    docker-compose -f "$COMPOSE_FILE" up -d redis postgres
    
    sleep 10
    
    print_info "2. Démarrage API Gateway..."
    docker-compose -f "$COMPOSE_FILE" up -d api-gateway-simple
    
    sleep 10
    
    print_info "3. Démarrage frontend..."
    docker-compose -f "$COMPOSE_FILE" up -d nexten-frontend
    
    sleep 10
    
    print_info "4. Services optionnels disponibles avec profiles:"
    echo "   - docker-compose -f $COMPOSE_FILE --profile nexten up -d"
    echo "   - docker-compose -f $COMPOSE_FILE --profile parsing up -d"
    echo "   - docker-compose -f $COMPOSE_FILE --profile matching up -d"
    echo "   - docker-compose -f $COMPOSE_FILE --profile monitoring up -d"
    
else
    print_warning "Fichier $COMPOSE_FILE non trouvé. Veuillez le créer avant de continuer."
    exit 1
fi

# 8. Vérification finale
echo -e "\n${PURPLE}🔍 8. VÉRIFICATION FINALE${NC}"
echo "=================================================="

sleep 20  # Attendre que tous les services démarrent

print_info "Statut final des containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test des endpoints
print_info "Test des endpoints principaux:"

ENDPOINTS=(
    "http://localhost:$API_GATEWAY_PORT/api/gateway/status:API Gateway Status"
    "http://localhost:$API_GATEWAY_PORT/api/gateway/health:API Gateway Health"
    "http://localhost:3000:Frontend NexTen"
)

for endpoint_info in "${ENDPOINTS[@]}"; do
    endpoint=${endpoint_info%:*}
    name=${endpoint_info#*:}
    
    echo -n "   $name: "
    if curl -s --connect-timeout 5 "$endpoint" > /dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${RED}❌ Échec${NC}"
    fi
done

# 9. Résumé et prochaines étapes
echo -e "\n${PURPLE}📋 9. RÉSUMÉ ET PROCHAINES ÉTAPES${NC}"
echo "=================================================="

print_info "Configuration terminée ! Services disponibles:"
echo -e "${GREEN}🌟 API Gateway SuperSmartMatch V2: http://localhost:$API_GATEWAY_PORT/api/gateway/${NC}"
echo -e "${GREEN}🌐 Frontend NexTen: http://localhost:3000${NC}"
echo -e "${GREEN}📚 Documentation Swagger: http://localhost:$API_GATEWAY_PORT/api/gateway/docs${NC}"

echo -e "\n${BLUE}📋 Commandes utiles:${NC}"
echo "# Voir les logs de l'API Gateway:"
echo "docker-compose -f $COMPOSE_FILE logs -f api-gateway-simple"
echo ""
echo "# Démarrer les services de parsing:"
echo "docker-compose -f $COMPOSE_FILE --profile parsing up -d"
echo ""
echo "# Démarrer les services Nexten:"
echo "docker-compose -f $COMPOSE_FILE --profile nexten up -d"
echo ""
echo "# Démarrer le matching service:"
echo "docker-compose -f $COMPOSE_FILE --profile matching up -d"
echo ""
echo "# Monitoring en temps réel:"
echo "watch 'docker ps --format \"table {{.Names}}\\t{{.Status}}\\t{{.Ports}}\"'"

print_info "✅ Diagnostic et résolution terminés avec succès !"
