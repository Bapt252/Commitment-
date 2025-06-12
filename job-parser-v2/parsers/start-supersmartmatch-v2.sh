#!/bin/bash
#
# 🚀 SuperSmartMatch V2 - Script de Démarrage Rapide
# Configuration automatique et déploiement du service unifié
#
# Usage: ./start-supersmartmatch-v2.sh [option]
# Options:
#   dev      - Mode développement avec logs détaillés
#   prod     - Mode production avec monitoring complet
#   test     - Mode test avec validation automatique
#   clean    - Nettoyage et redémarrage complet

set -e

# Configuration
PROJECT_NAME="SuperSmartMatch V2"
SERVICE_PORT=5070
NEXTEN_PORT=5052
V1_PORT=5062
REDIS_PORT=6379

# Couleurs pour affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Fonctions utilitaires
print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "🚀 $PROJECT_NAME - Démarrage Rapide"
    echo "=================================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Vérification des prérequis
check_prerequisites() {
    print_step "Vérification des prérequis..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez installer Docker."
        exit 1
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose n'est pas installé."
        exit 1
    fi
    
    # Python (pour validation)
    if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
        print_warning "Python n'est pas installé. Validation automatique désactivée."
        PYTHON_AVAILABLE=false
    else
        PYTHON_AVAILABLE=true
    fi
    
    print_step "Prérequis validés ✓"
}

# Configuration de l'environnement
setup_environment() {
    print_step "Configuration de l'environnement..."
    
    # Création du fichier .env s'il n'existe pas
    if [ ! -f .env ]; then
        print_info "Création du fichier .env..."
        cat > .env << EOF
# SuperSmartMatch V2 Configuration
SERVICE_PORT=5070
ENVIRONMENT=${MODE:-production}
SERVICE_NAME=supersmartmatch-v2

# Services externes
NEXTEN_URL=http://nexten-matcher:5052
SUPERSMARTMATCH_V1_URL=http://supersmartmatch-v1:5062

# Redis
REDIS_URL=redis://redis-cache:6379
CACHE_TTL=300
CACHE_ENABLED=true

# Circuit breakers
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60
MAX_RESPONSE_TIME_MS=100

# Feature flags
ENABLE_V2=true
V2_TRAFFIC_PERCENTAGE=100
ENABLE_NEXTEN_ALGORITHM=true
ENABLE_SMART_SELECTION=true

# Monitoring
ENABLE_METRICS=true
LOG_LEVEL=${LOG_LEVEL:-INFO}
EOF
        print_step "Fichier .env créé"
    else
        print_info "Fichier .env existant utilisé"
    fi
    
    # Création des répertoires nécessaires
    mkdir -p logs config monitoring/grafana monitoring/prometheus
    print_step "Répertoires créés"
}

# Nettoyage des ressources existantes
cleanup() {
    print_step "Nettoyage des ressources existantes..."
    
    # Arrêt des conteneurs
    docker-compose -f docker-compose.supersmartmatch-v2.yml down --remove-orphans 2>/dev/null || true
    
    # Suppression des volumes si demandé
    if [ "$1" = "clean" ]; then
        print_warning "Suppression des volumes de données..."
        docker volume rm supersmartmatch-v2-redis-data 2>/dev/null || true
        docker volume rm supersmartmatch-v2-prometheus-data 2>/dev/null || true
        docker volume rm supersmartmatch-v2-grafana-data 2>/dev/null || true
    fi
    
    print_step "Nettoyage terminé"
}

# Construction des images
build_images() {
    print_step "Construction des images Docker..."
    
    # Construction de l'image SuperSmartMatch V2
    if [ -f "Dockerfile.supersmartmatch-v2" ]; then
        print_info "Construction SuperSmartMatch V2..."
        docker build -f Dockerfile.supersmartmatch-v2 -t supersmartmatch-v2:latest .
    else
        print_warning "Dockerfile.supersmartmatch-v2 non trouvé, utilisation de l'image par défaut"
    fi
    
    print_step "Images construites"
}

# Démarrage des services
start_services() {
    print_step "Démarrage des services SuperSmartMatch V2..."
    
    # Variables d'environnement selon le mode
    case $MODE in
        "dev")
            export LOG_LEVEL=DEBUG
            export ENVIRONMENT=development
            COMPOSE_OPTIONS="--scale supersmartmatch-v2=1"
            ;;
        "prod")
            export LOG_LEVEL=INFO
            export ENVIRONMENT=production
            COMPOSE_OPTIONS="--scale supersmartmatch-v2=2"
            ;;
        "test")
            export LOG_LEVEL=DEBUG
            export ENVIRONMENT=test
            COMPOSE_OPTIONS="--scale supersmartmatch-v2=1"
            ;;
        *)
            export LOG_LEVEL=INFO
            export ENVIRONMENT=production
            COMPOSE_OPTIONS=""
            ;;
    esac
    
    # Démarrage avec Docker Compose
    if [ -f "docker-compose.supersmartmatch-v2.yml" ]; then
        print_info "Utilisation de docker-compose.supersmartmatch-v2.yml..."
        docker-compose -f docker-compose.supersmartmatch-v2.yml up -d $COMPOSE_OPTIONS
    else
        print_error "Fichier docker-compose.supersmartmatch-v2.yml non trouvé!"
        exit 1
    fi
    
    print_step "Services démarrés"
}

# Vérification de la santé des services
health_check() {
    print_step "Vérification de la santé des services..."
    
    # Attendre que les services soient prêts
    print_info "Attente du démarrage des services (30s)..."
    sleep 30
    
    # Liste des services à vérifier
    declare -A services=(
        ["SuperSmartMatch V2"]="http://localhost:$SERVICE_PORT/health"
        ["Redis Cache"]="redis://localhost:$REDIS_PORT"
    )
    
    # Services optionnels (peuvent être en mode mock)
    declare -A optional_services=(
        ["Nexten Matcher"]="http://localhost:$NEXTEN_PORT/health"
        ["SuperSmartMatch V1"]="http://localhost:$V1_PORT/health"
    )
    
    # Vérification des services principaux
    for service in "${!services[@]}"; do
        url="${services[$service]}"
        if [[ $url == http* ]]; then
            if curl -sf "$url" >/dev/null 2>&1; then
                print_step "$service ✓"
            else
                print_error "$service ✗"
                HEALTH_ISSUES=true
            fi
        elif [[ $url == redis* ]]; then
            if docker exec redis-cache-v2 redis-cli ping >/dev/null 2>&1; then
                print_step "$service ✓"
            else
                print_error "$service ✗"
                HEALTH_ISSUES=true
            fi
        fi
    done
    
    # Vérification des services optionnels
    for service in "${!optional_services[@]}"; do
        url="${optional_services[$service]}"
        if curl -sf "$url" >/dev/null 2>&1; then
            print_step "$service ✓"
        else
            print_warning "$service ✗ (optionnel - fallback activé)"
        fi
    done
    
    if [ "$HEALTH_ISSUES" = true ]; then
        print_error "Problèmes de santé détectés!"
        return 1
    else
        print_step "Tous les services sont opérationnels ✓"
        return 0
    fi
}

# Test rapide de l'API
quick_api_test() {
    print_step "Test rapide de l'API..."
    
    # Données de test
    test_payload='{
        "candidate": {
            "name": "Test User",
            "technical_skills": ["Python", "Machine Learning"],
            "experiences": [{"duration_months": 24}]
        },
        "offers": [
            {
                "id": "test_job_1",
                "title": "Python Developer",
                "required_skills": ["Python", "Django"]
            }
        ],
        "algorithm": "auto"
    }'
    
    # Test API V2
    print_info "Test API V2..."
    if curl -sf -X POST "http://localhost:$SERVICE_PORT/api/v2/match" \
        -H "Content-Type: application/json" \
        -d "$test_payload" >/dev/null 2>&1; then
        print_step "API V2 fonctionnelle ✓"
    else
        print_error "API V2 non fonctionnelle ✗"
        return 1
    fi
    
    # Test API V1 (compatibilité)
    print_info "Test compatibilité API V1..."
    legacy_payload='{
        "cv_data": {
            "name": "Legacy User",
            "technical_skills": ["JavaScript", "React"]
        },
        "job_data": [
            {
                "id": "legacy_job_1",
                "title": "Frontend Developer",
                "required_skills": ["JavaScript", "React"]
            }
        ]
    }'
    
    if curl -sf -X POST "http://localhost:$SERVICE_PORT/match" \
        -H "Content-Type: application/json" \
        -d "$legacy_payload" >/dev/null 2>&1; then
        print_step "Compatibilité V1 préservée ✓"
    else
        print_warning "Compatibilité V1 problématique ⚠️"
    fi
    
    print_step "Tests API terminés"
}

# Validation complète (si Python disponible)
run_full_validation() {
    if [ "$PYTHON_AVAILABLE" = true ] && [ -f "validate-supersmartmatch-v2.py" ]; then
        print_step "Exécution de la validation complète..."
        
        # Installation des dépendances si nécessaire
        if [ -f "requirements-v2.txt" ]; then
            pip install -q aiohttp || true
        fi
        
        # Exécution du script de validation
        if python validate-supersmartmatch-v2.py "http://localhost:$SERVICE_PORT"; then
            print_step "Validation complète réussie ✓"
        else
            print_warning "Validation complète avec avertissements"
        fi
    else
        print_info "Validation complète ignorée (Python ou script non disponible)"
    fi
}

# Affichage des informations de connexion
show_connection_info() {
    print_step "Informations de connexion:"
    echo ""
    echo -e "${PURPLE}🚀 SuperSmartMatch V2 - Services Accessibles${NC}"
    echo "=================================================================="
    echo -e "${GREEN}📡 API V2 (native):${NC}        http://localhost:$SERVICE_PORT/api/v2/match"
    echo -e "${GREEN}🔄 API V1 (compatible):${NC}    http://localhost:$SERVICE_PORT/match"
    echo -e "${GREEN}💚 Health Check:${NC}           http://localhost:$SERVICE_PORT/health"
    echo -e "${GREEN}📊 Métriques:${NC}              http://localhost:$SERVICE_PORT/metrics"
    echo -e "${GREEN}📚 Documentation:${NC}          http://localhost:$SERVICE_PORT/api/docs"
    echo ""
    echo -e "${BLUE}🔧 Services de Support:${NC}"
    echo -e "${BLUE}📈 Prometheus:${NC}              http://localhost:9090"
    echo -e "${BLUE}📊 Grafana:${NC}                 http://localhost:3000 (admin/supersmartmatch)"
    echo -e "${BLUE}🗄️  Redis:${NC}                   localhost:$REDIS_PORT"
    echo ""
    echo -e "${YELLOW}🧪 Test Rapide:${NC}"
    echo "curl -X POST http://localhost:$SERVICE_PORT/api/v2/match \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"candidate\":{\"technical_skills\":[\"Python\"]},\"offers\":[{\"id\":\"1\",\"required_skills\":[\"Python\"]}]}'"
    echo ""
}

# Affichage de l'aide
show_help() {
    echo "Usage: $0 [MODE]"
    echo ""
    echo "Modes disponibles:"
    echo "  dev      - Mode développement (logs détaillés, 1 instance)"
    echo "  prod     - Mode production (2 instances, monitoring complet)"
    echo "  test     - Mode test (validation automatique)"
    echo "  clean    - Nettoyage complet et redémarrage"
    echo "  stop     - Arrêt des services"
    echo "  logs     - Affichage des logs"
    echo "  status   - Status des services"
    echo "  help     - Affichage de cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 dev     # Démarrage en mode développement"
    echo "  $0 prod    # Démarrage en mode production"
    echo "  $0 clean   # Nettoyage et redémarrage"
    exit 0
}

# Arrêt des services
stop_services() {
    print_step "Arrêt des services..."
    docker-compose -f docker-compose.supersmartmatch-v2.yml down
    print_step "Services arrêtés"
}

# Affichage des logs
show_logs() {
    print_info "Logs SuperSmartMatch V2 (Ctrl+C pour quitter):"
    docker-compose -f docker-compose.supersmartmatch-v2.yml logs -f supersmartmatch-v2
}

# Status des services
show_status() {
    print_step "Status des services:"
    docker-compose -f docker-compose.supersmartmatch-v2.yml ps
    echo ""
    health_check
}

# Fonction principale
main() {
    # Gestion des arguments
    MODE=${1:-prod}
    
    case $MODE in
        "help"|"-h"|"--help")
            show_help
            ;;
        "stop")
            stop_services
            exit 0
            ;;
        "logs")
            show_logs
            exit 0
            ;;
        "status")
            show_status
            exit 0
            ;;
        "clean")
            print_header
            cleanup clean
            MODE="prod"
            ;;
        "dev"|"prod"|"test")
            print_header
            ;;
        *)
            print_error "Mode '$MODE' non reconnu. Utilisez 'help' pour voir les options."
            exit 1
            ;;
    esac
    
    # Variables globales
    HEALTH_ISSUES=false
    
    # Séquence de démarrage
    check_prerequisites
    setup_environment
    cleanup
    build_images
    start_services
    
    # Vérifications et tests
    if health_check; then
        quick_api_test
        
        if [ "$MODE" = "test" ]; then
            run_full_validation
        fi
        
        show_connection_info
        
        print_step "🎉 SuperSmartMatch V2 démarré avec succès en mode $MODE!"
        print_info "Utilisez '$0 logs' pour voir les logs en temps réel"
        print_info "Utilisez '$0 stop' pour arrêter les services"
    else
        print_error "Échec du démarrage. Vérifiez les logs avec: docker-compose -f docker-compose.supersmartmatch-v2.yml logs"
        exit 1
    fi
}

# Gestion des signaux
trap 'print_warning "Interruption détectée. Utilisez \"$0 stop\" pour arrêter proprement les services."' INT

# Exécution
main "$@"
