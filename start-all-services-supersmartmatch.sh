#!/bin/bash

# Script de démarrage complet avec SuperSmartMatch intégré
# Auteur: Nexten Team
# Version: 2.0.0 avec SuperSmartMatch

echo "🚀 NEXTEN - Démarrage des services avec SuperSmartMatch"
echo "============================================================"
echo "📅 $(date)"
echo "👤 Utilisateur: $(whoami)"
echo "📁 Répertoire: $(pwd)"
echo ""

# Configuration
SUPER_SMART_MATCH_ENABLED=${SUPER_SMART_MATCH_ENABLED:-true}
START_MONITORING=${START_MONITORING:-false}
SKIP_LEGACY_SERVICES=${SKIP_LEGACY_SERVICES:-false}

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Fonction pour afficher les statuts
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_step() {
    echo -e "${PURPLE}🔧 $1${NC}"
}

# Vérification des prérequis
print_step "Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    print_status 1 "Docker non trouvé. Veuillez l'installer."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_status 1 "Docker Compose non trouvé. Veuillez l'installer."
    exit 1
fi

print_status 0 "Docker et Docker Compose disponibles"

# Vérification des fichiers nécessaires
print_step "Vérification des fichiers de configuration..."

if [ ! -f "docker-compose.yml" ]; then
    print_status 1 "docker-compose.yml non trouvé"
    exit 1
fi

if [ ! -f ".env.example" ]; then
    print_warning "Fichier .env.example non trouvé"
fi

if [ ! -f ".env" ]; then
    print_warning "Fichier .env non trouvé, création depuis .env.example"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status 0 "Fichier .env créé"
    fi
fi

print_status 0 "Configuration validée"

# Nettoyage des anciens conteneurs
print_step "Nettoyage des conteneurs existants..."
docker-compose down --remove-orphans > /dev/null 2>&1
print_status 0 "Conteneurs arrêtés"

# Construction des images
print_step "Construction des images Docker..."
echo "📦 Construction des images en cours..."
docker-compose build --parallel > /dev/null 2>&1
if [ $? -eq 0 ]; then
    print_status 0 "Images construites avec succès"
else
    print_status 1 "Erreur lors de la construction des images"
    print_warning "Tentative de construction sans cache..."
    docker-compose build --no-cache --parallel
fi

# Démarrage des services de base
print_step "Démarrage des services de base..."
echo "🗄️  Démarrage des services infrastructure..."

# Base de données et stockage
echo "   📊 PostgreSQL..."
docker-compose up -d postgres
sleep 5

echo "   🗃️  Redis..."
docker-compose up -d redis
sleep 3

echo "   📁 MinIO..."
docker-compose up -d minio
sleep 3

print_status 0 "Services de base démarrés"

# Services de parsing
if [ "$SKIP_LEGACY_SERVICES" != "true" ]; then
    print_step "Démarrage des services de parsing..."
    
    echo "   📄 CV Parser Service..."
    docker-compose up -d cv-parser-service
    sleep 5
    
    echo "   📋 Job Parser Service..."
    docker-compose up -d job-parser-service
    sleep 5
    
    print_status 0 "Services de parsing démarrés"
else
    print_info "Services legacy ignorés (SKIP_LEGACY_SERVICES=true)"
fi

# SuperSmartMatch - Service principal unifié
if [ "$SUPER_SMART_MATCH_ENABLED" = "true" ]; then
    print_step "🧠 Démarrage de SuperSmartMatch (Service unifié)..."
    
    # Vérification que le service est configuré
    if [ -d "super-smart-match-service" ]; then
        echo "   🔧 Construction de SuperSmartMatch..."
        docker-compose up -d supersmartmatch
        
        # Attente du démarrage
        echo "   ⏳ Attente du démarrage de SuperSmartMatch..."
        for i in {1..30}; do
            if curl -f http://localhost:5070/health >/dev/null 2>&1; then
                print_status 0 "SuperSmartMatch opérationnel sur http://localhost:5070"
                break
            fi
            echo -n "."
            sleep 2
        done
        
        if ! curl -f http://localhost:5070/health >/dev/null 2>&1; then
            print_status 1 "SuperSmartMatch n'a pas démarré correctement"
            echo "📋 Logs SuperSmartMatch:"
            docker-compose logs supersmartmatch | tail -20
        else
            # Test des algorithmes disponibles
            echo "   🧠 Vérification des algorithmes..."
            ALGOS=$(curl -s http://localhost:5070/algorithms | jq -r 'length' 2>/dev/null || echo "0")
            print_info "$ALGOS algorithmes disponibles dans SuperSmartMatch"
        fi
    else
        print_status 1 "Répertoire super-smart-match-service non trouvé"
        print_warning "SuperSmartMatch désactivé"
        SUPER_SMART_MATCH_ENABLED=false
    fi
else
    print_info "SuperSmartMatch désactivé (SUPER_SMART_MATCH_ENABLED=false)"
    
    # Démarrage des services legacy si SuperSmartMatch est désactivé
    print_step "Démarrage des services de matching legacy..."
    
    echo "   🎯 Matching Service..."
    docker-compose up -d matching-service
    sleep 5
    
    echo "   🎨 Personalization Service..."
    docker-compose up -d personalization-service
    sleep 3
fi

# Services complémentaires
if [ "$SKIP_LEGACY_SERVICES" != "true" ]; then
    print_step "Démarrage des services complémentaires..."
    
    echo "   📊 User Behavior Analysis..."
    docker-compose up -d user-behavior-service
    sleep 3
    
    echo "   📝 Feedback Service..."
    docker-compose up -d feedback-service
    sleep 3
    
    print_status 0 "Services complémentaires démarrés"
fi

# Frontend
print_step "Démarrage du frontend..."
echo "   🌐 Frontend Service..."
docker-compose up -d frontend
sleep 5
print_status 0 "Frontend démarré"

# Monitoring (optionnel)
if [ "$START_MONITORING" = "true" ]; then
    print_step "Démarrage du monitoring..."
    
    echo "   📊 Prometheus..."
    docker-compose --profile monitoring up -d prometheus
    sleep 3
    
    echo "   📈 Grafana..."
    docker-compose --profile monitoring up -d grafana
    sleep 5
    
    print_status 0 "Monitoring démarré"
fi

# Vérification finale des services
print_step "Vérification de l'état des services..."
echo ""
echo "🔍 État des services:"
echo "============================================================"

# Services principaux
services_to_check=()

if [ "$SUPER_SMART_MATCH_ENABLED" = "true" ]; then
    services_to_check+=("SuperSmartMatch:http://localhost:5070/health")
else
    services_to_check+=("Matching Service:http://localhost:5052/health")
    services_to_check+=("Personalization:http://localhost:5060/health")
fi

if [ "$SKIP_LEGACY_SERVICES" != "true" ]; then
    services_to_check+=(
        "CV Parser:http://localhost:5051/health"
        "Job Parser:http://localhost:5055/health"
        "User Behavior:http://localhost:5057/health"
        "Feedback:http://localhost:5058/health"
    )
fi

services_to_check+=(
    "Frontend:http://localhost:3000"
    "PostgreSQL:localhost:5432"
    "Redis:localhost:6379"
    "MinIO API:http://localhost:9000"
    "MinIO Console:http://localhost:9001"
)

if [ "$START_MONITORING" = "true" ]; then
    services_to_check+=(
        "Prometheus:http://localhost:9090"
        "Grafana:http://localhost:3000"
    )
fi

# Test de connectivité
all_ok=true
for service_info in "${services_to_check[@]}"; do
    service_name=$(echo $service_info | cut -d: -f1)
    service_url=$(echo $service_info | cut -d: -f2-)
    
    if [[ $service_url == http* ]]; then
        if curl -f -s --max-time 5 "$service_url" >/dev/null 2>&1; then
            print_status 0 "$service_name"
        else
            print_status 1 "$service_name (${service_url})"
            all_ok=false
        fi
    else
        # Test TCP pour les services non-HTTP
        host=$(echo $service_url | cut -d: -f1)
        port=$(echo $service_url | cut -d: -f2)
        if nc -z $host $port 2>/dev/null; then
            print_status 0 "$service_name"
        else
            print_status 1 "$service_name (${service_url})"
            all_ok=false
        fi
    fi
done

echo ""
echo "============================================================"

if [ "$all_ok" = true ]; then
    echo -e "${GREEN}🎉 TOUS LES SERVICES SONT OPÉRATIONNELS !${NC}"
else
    echo -e "${YELLOW}⚠️  Certains services ont des problèmes${NC}"
    echo -e "${BLUE}💡 Vérifiez les logs avec: docker-compose logs [service-name]${NC}"
fi

echo ""
echo "🌐 ACCÈS AUX SERVICES"
echo "============================================================"
echo -e "${BLUE}🏠 Page d'accueil:${NC}           http://localhost:3000"

if [ "$SUPER_SMART_MATCH_ENABLED" = "true" ]; then
    echo -e "${PURPLE}🧠 SuperSmartMatch API:${NC}       http://localhost:5070"
    echo -e "${PURPLE}📖 Documentation API:${NC}        http://localhost:5070/docs"
    echo -e "${PURPLE}🔍 Health Check:${NC}             http://localhost:5070/health"
    echo -e "${PURPLE}🎯 Algorithmes:${NC}              http://localhost:5070/algorithms"
else
    echo -e "${BLUE}🎯 Matching API:${NC}             http://localhost:5052"
    echo -e "${BLUE}📄 CV Parser:${NC}                http://localhost:5051"
    echo -e "${BLUE}📋 Job Parser:${NC}               http://localhost:5055"
    echo -e "${BLUE}🎨 Personalization:${NC}          http://localhost:5060"
fi

echo -e "${BLUE}🗄️  MinIO Console:${NC}            http://localhost:9001"
echo -e "${BLUE}💾 Redis Commander:${NC}           http://localhost:8081"

if [ "$START_MONITORING" = "true" ]; then
    echo -e "${BLUE}📊 Prometheus:${NC}               http://localhost:9090"
    echo -e "${BLUE}📈 Grafana:${NC}                  http://localhost:3000 (admin/nexten123)"
fi

echo ""
echo "⚙️  COMMANDES UTILES"
echo "============================================================"
echo "📋 Voir tous les logs:          docker-compose logs -f"
echo "📋 Logs d'un service:           docker-compose logs -f [service-name]"
echo "⏹️  Arrêter tous les services:   docker-compose down"
echo "🔄 Redémarrer un service:       docker-compose restart [service-name]"
echo "📊 État des conteneurs:        docker-compose ps"

if [ "$SUPER_SMART_MATCH_ENABLED" = "true" ]; then
    echo "🧪 Tester SuperSmartMatch:      cd super-smart-match-service && ./test-supersmartmatch.sh"
fi

echo ""
echo "🔧 VARIABLES D'ENVIRONNEMENT"
echo "============================================================"
echo "SUPER_SMART_MATCH_ENABLED=$SUPER_SMART_MATCH_ENABLED"
echo "START_MONITORING=$START_MONITORING"
echo "SKIP_LEGACY_SERVICES=$SKIP_LEGACY_SERVICES"
echo ""
echo "💡 Pour modifier: export VARIABLE=valeur avant de relancer le script"
echo ""

if [ "$SUPER_SMART_MATCH_ENABLED" = "true" ]; then
    echo -e "${GREEN}🚀 Nexten avec SuperSmartMatch est prêt !${NC}"
    echo -e "${GREEN}🧠 Utilisez l'API unifiée sur le port 5070${NC}"
else
    echo -e "${GREEN}🚀 Nexten est prêt (mode legacy) !${NC}"
fi

echo "============================================================"
echo "📅 Démarrage terminé: $(date)"
echo ""
