#!/bin/bash

# 🚀 SuperSmartMatch V2 - Script de Démarrage Automatique
# Orchestration complète du service unifié sur port 5070

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration par défaut
DEFAULT_MODE="docker"
DEFAULT_ENVIRONMENT="development"
DEFAULT_PORT=5070

# Affichage du header
print_header() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║              🚀 SuperSmartMatch V2 Launcher              ║"
    echo "║                 Service Unifié Port 5070                ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Affichage de l'aide
show_help() {
    echo -e "${CYAN}Usage: $0 [MODE] [OPTIONS]${NC}"
    echo ""
    echo -e "${YELLOW}MODES:${NC}"
    echo "  docker     - Démarrage avec Docker Compose (recommandé)"
    echo "  local      - Démarrage local avec Python"
    echo "  dev        - Mode développement avec hot reload"
    echo "  test       - Lancement des tests et validation"
    echo "  stop       - Arrêt de tous les services"
    echo "  status     - État des services"
    echo "  logs       - Affichage des logs"
    echo ""
    echo -e "${YELLOW}OPTIONS:${NC}"
    echo "  --port PORT        Port du service V2 (défaut: 5070)"
    echo "  --env ENV          Environnement (development/production)"
    echo "  --no-validation    Skip la validation post-démarrage"
    echo "  --verbose          Affichage détaillé"
    echo "  --help             Afficher cette aide"
    echo ""
    echo -e "${YELLOW}EXEMPLES:${NC}"
    echo "  $0 docker                    # Démarrage Docker standard"
    echo "  $0 local --port 5071         # Démarrage local port 5071"
    echo "  $0 dev --verbose             # Mode développement verbeux"
    echo "  $0 test                      # Tests complets"
}

# Vérification des prérequis
check_prerequisites() {
    echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"
    
    local missing_deps=0
    
    # Vérifier Docker si mode Docker
    if [[ "$MODE" == "docker" || "$MODE" == "dev" ]]; then
        if ! command -v docker &> /dev/null; then
            echo -e "${RED}❌ Docker non trouvé${NC}"
            missing_deps=1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            echo -e "${RED}❌ Docker Compose non trouvé${NC}"
            missing_deps=1
        fi
    fi
    
    # Vérifier Python si mode local
    if [[ "$MODE" == "local" || "$MODE" == "dev" || "$MODE" == "test" ]]; then
        if ! command -v python3 &> /dev/null; then
            echo -e "${RED}❌ Python 3 non trouvé${NC}"
            missing_deps=1
        fi
        
        if ! command -v pip &> /dev/null; then
            echo -e "${RED}❌ pip non trouvé${NC}"
            missing_deps=1
        fi
    fi
    
    # Vérifier les fichiers requis
    required_files=(
        "supersmartmatch-v2-unified-service.py"
        "requirements-v2.txt"
        "docker-compose.supersmartmatch-v2.yml"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo -e "${RED}❌ Fichier manquant: $file${NC}"
            missing_deps=1
        fi
    done
    
    if [[ $missing_deps -eq 1 ]]; then
        echo -e "${RED}💥 Prérequis manquants. Installation nécessaire.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prérequis satisfaits${NC}"
}

# Configuration de l'environnement
setup_environment() {
    echo -e "${BLUE}🔧 Configuration de l'environnement...${NC}"
    
    # Créer le fichier .env s'il n'existe pas
    if [[ ! -f ".env" ]]; then
        echo -e "${YELLOW}📝 Création du fichier .env...${NC}"
        cat > .env << EOF
# SuperSmartMatch V2 Configuration
SERVICE_PORT=${PORT}
ENVIRONMENT=${ENVIRONMENT}
SERVICE_NAME=supersmartmatch-v2

# Services externes
NEXTEN_URL=http://localhost:5052
SUPERSMARTMATCH_V1_URL=http://localhost:5062

# Redis
REDIS_URL=redis://localhost:6379
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
LOG_LEVEL=INFO
EOF
        echo -e "${GREEN}✅ Fichier .env créé${NC}"
    fi
    
    # Créer les répertoires nécessaires
    mkdir -p logs config data cache
    
    echo -e "${GREEN}✅ Environnement configuré${NC}"
}

# Démarrage mode Docker
start_docker() {
    echo -e "${BLUE}🐳 Démarrage avec Docker Compose...${NC}"
    
    # Arrêter les services existants
    docker-compose -f docker-compose.supersmartmatch-v2.yml down &>/dev/null || true
    
    # Build et démarrage
    if [[ "$VERBOSE" == "true" ]]; then
        docker-compose -f docker-compose.supersmartmatch-v2.yml up --build -d
    else
        docker-compose -f docker-compose.supersmartmatch-v2.yml up --build -d &>/dev/null
    fi
    
    # Attendre que les services soient prêts
    echo -e "${YELLOW}⏳ Attente des services (30s max)...${NC}"
    
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s http://localhost:${PORT}/health &>/dev/null; then
            echo -e "${GREEN}✅ SuperSmartMatch V2 opérationnel${NC}"
            break
        fi
        
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        echo -e "${RED}❌ Timeout - Service non démarré${NC}"
        show_logs
        exit 1
    fi
}

# Démarrage mode local
start_local() {
    echo -e "${BLUE}🐍 Démarrage local avec Python...${NC}"
    
    # Installation des dépendances
    if [[ ! -d "venv" ]]; then
        echo -e "${YELLOW}📦 Création de l'environnement virtuel...${NC}"
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    echo -e "${YELLOW}📦 Installation des dépendances...${NC}"
    pip install -r requirements-v2.txt &>/dev/null
    
    # Démarrage Redis si nécessaire
    if ! pgrep redis-server &>/dev/null; then
        echo -e "${YELLOW}🔴 Démarrage Redis...${NC}"
        redis-server &
        sleep 2
    fi
    
    # Démarrage du service
    echo -e "${BLUE}🚀 Démarrage SuperSmartMatch V2...${NC}"
    
    export SERVICE_PORT=${PORT}
    export ENVIRONMENT=${ENVIRONMENT}
    
    if [[ "$VERBOSE" == "true" ]]; then
        python supersmartmatch-v2-unified-service.py
    else
        python supersmartmatch-v2-unified-service.py &>/dev/null &
        local service_pid=$!
        
        # Attendre que le service soit prêt
        local max_attempts=20
        local attempt=0
        
        while [[ $attempt -lt $max_attempts ]]; do
            if curl -s http://localhost:${PORT}/health &>/dev/null; then
                echo -e "${GREEN}✅ SuperSmartMatch V2 opérationnel (PID: $service_pid)${NC}"
                break
            fi
            
            echo -n "."
            sleep 1
            ((attempt++))
        done
        
        if [[ $attempt -eq $max_attempts ]]; then
            echo -e "${RED}❌ Timeout - Service non démarré${NC}"
            kill $service_pid 2>/dev/null || true
            exit 1
        fi
    fi
}

# Mode développement
start_dev() {
    echo -e "${BLUE}🛠️ Mode développement avec hot reload...${NC}"
    
    # Installation des dépendances de développement
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install -r requirements-v2.txt
    pip install watchdog uvicorn[standard]
    
    # Démarrage avec hot reload
    export SERVICE_PORT=${PORT}
    export ENVIRONMENT=development
    
    uvicorn supersmartmatch_v2_unified_service:app \
        --host 0.0.0.0 \
        --port ${PORT} \
        --reload \
        --reload-dir . \
        --log-level info
}

# Tests et validation
run_tests() {
    echo -e "${BLUE}🧪 Exécution des tests et validation...${NC}"
    
    # Tests unitaires
    echo -e "${YELLOW}🔬 Tests unitaires...${NC}"
    if command -v python &>/dev/null; then
        python -m pytest test-supersmartmatch-v2.py -v
    else
        echo -e "${YELLOW}⏭️ Python non disponible, skip tests unitaires${NC}"
    fi
    
    # Validation d'intégration
    echo -e "${YELLOW}🔗 Validation d'intégration...${NC}"
    if curl -s http://localhost:${PORT}/health &>/dev/null; then
        python validate-supersmartmatch-v2.py http://localhost:${PORT}
    else
        echo -e "${RED}❌ Service non disponible pour validation${NC}"
        exit 1
    fi
}

# Arrêt des services
stop_services() {
    echo -e "${BLUE}🛑 Arrêt des services...${NC}"
    
    # Docker
    if command -v docker-compose &>/dev/null; then
        docker-compose -f docker-compose.supersmartmatch-v2.yml down &>/dev/null || true
        echo -e "${GREEN}✅ Services Docker arrêtés${NC}"
    fi
    
    # Processus locaux
    pkill -f "supersmartmatch-v2-unified-service.py" &>/dev/null || true
    pkill -f "uvicorn.*supersmartmatch" &>/dev/null || true
    
    echo -e "${GREEN}✅ Tous les services arrêtés${NC}"
}

# État des services
show_status() {
    echo -e "${BLUE}📊 État des services SuperSmartMatch V2${NC}"
    echo ""
    
    # Service principal V2
    if curl -s http://localhost:${PORT}/health &>/dev/null; then
        echo -e "${GREEN}✅ SuperSmartMatch V2 (port ${PORT})${NC}"
        
        # Informations détaillées
        local health_info=$(curl -s http://localhost:${PORT}/health 2>/dev/null)
        if [[ $? -eq 0 ]]; then
            echo "   $(echo $health_info | jq -r '.version // "Version inconnue"' 2>/dev/null || echo "Status: OK")"
        fi
    else
        echo -e "${RED}❌ SuperSmartMatch V2 (port ${PORT})${NC}"
    fi
    
    # Services externes
    if curl -s http://localhost:5052/health &>/dev/null; then
        echo -e "${GREEN}✅ Nexten Matcher (port 5052)${NC}"
    else
        echo -e "${YELLOW}⚠️  Nexten Matcher (port 5052) - Indisponible${NC}"
    fi
    
    if curl -s http://localhost:5062/health &>/dev/null; then
        echo -e "${GREEN}✅ SuperSmartMatch V1 (port 5062)${NC}"
    else
        echo -e "${YELLOW}⚠️  SuperSmartMatch V1 (port 5062) - Indisponible${NC}"
    fi
    
    # Redis
    if command -v redis-cli &>/dev/null && redis-cli ping &>/dev/null; then
        echo -e "${GREEN}✅ Redis Cache${NC}"
    else
        echo -e "${YELLOW}⚠️  Redis Cache - Indisponible${NC}"
    fi
    
    # Docker
    if command -v docker &>/dev/null; then
        local containers=$(docker ps --filter "name=supersmartmatch" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null)
        if [[ -n "$containers" && "$containers" != "NAMES	STATUS" ]]; then
            echo ""
            echo -e "${CYAN}🐳 Conteneurs Docker:${NC}"
            echo "$containers"
        fi
    fi
}

# Affichage des logs
show_logs() {
    echo -e "${BLUE}📋 Logs SuperSmartMatch V2${NC}"
    
    if command -v docker &>/dev/null; then
        # Logs Docker
        docker-compose -f docker-compose.supersmartmatch-v2.yml logs --tail=50 supersmartmatch-v2 2>/dev/null || {
            echo -e "${YELLOW}⚠️  Pas de logs Docker disponibles${NC}"
        }
    fi
    
    # Logs locaux
    if [[ -f "logs/supersmartmatch-v2.log" ]]; then
        echo -e "${CYAN}📄 Logs locaux:${NC}"
        tail -20 logs/supersmartmatch-v2.log
    fi
}

# Validation post-démarrage
post_start_validation() {
    if [[ "$NO_VALIDATION" == "true" ]]; then
        echo -e "${YELLOW}⏭️ Validation post-démarrage skip${NC}"
        return
    fi
    
    echo -e "${BLUE}✅ Validation post-démarrage...${NC}"
    
    # Test de base
    if curl -s http://localhost:${PORT}/health &>/dev/null; then
        echo -e "${GREEN}✅ Service accessible${NC}"
        
        # Test API simple
        local test_response=$(curl -s -X POST http://localhost:${PORT}/match \
            -H "Content-Type: application/json" \
            -d '{"cv_data":{"name":"Test"},"job_data":[{"id":"1","title":"Test"}]}' 2>/dev/null)
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}✅ API fonctionnelle${NC}"
        else
            echo -e "${YELLOW}⚠️  API non testée${NC}"
        fi
    else
        echo -e "${RED}❌ Service inaccessible${NC}"
        return 1
    fi
}

# Parsing des arguments
MODE="$1"
shift || true

VERBOSE="false"
NO_VALIDATION="false"
PORT=${DEFAULT_PORT}
ENVIRONMENT=${DEFAULT_ENVIRONMENT}

while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --no-validation)
            NO_VALIDATION="true"
            shift
            ;;
        --verbose)
            VERBOSE="true"
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Option inconnue: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Validation du mode
if [[ -z "$MODE" ]]; then
    MODE="$DEFAULT_MODE"
fi

case $MODE in
    docker|local|dev|test|stop|status|logs)
        ;;
    *)
        echo -e "${RED}❌ Mode invalide: $MODE${NC}"
        show_help
        exit 1
        ;;
esac

# Exécution principale
main() {
    print_header
    
    case $MODE in
        docker)
            check_prerequisites
            setup_environment
            start_docker
            post_start_validation
            echo -e "${GREEN}🎉 SuperSmartMatch V2 démarré avec succès!${NC}"
            echo -e "${CYAN}📍 Service disponible: http://localhost:${PORT}${NC}"
            echo -e "${CYAN}📚 Documentation: http://localhost:${PORT}/api/docs${NC}"
            ;;
        local)
            check_prerequisites
            setup_environment
            start_local
            post_start_validation
            echo -e "${GREEN}🎉 SuperSmartMatch V2 démarré localement!${NC}"
            echo -e "${CYAN}📍 Service disponible: http://localhost:${PORT}${NC}"
            ;;
        dev)
            check_prerequisites
            setup_environment
            start_dev
            ;;
        test)
            run_tests
            ;;
        stop)
            stop_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
    esac
}

# Gestion des signaux
trap 'echo -e "\n${YELLOW}⚠️  Arrêt demandé...${NC}"; stop_services; exit 0' INT TERM

# Exécution
main
