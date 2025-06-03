#!/bin/bash

# 🚀 SuperSmartMatch V2 - Script de Déploiement Automatisé
# Déploiement complet et configuration du service unifié

set -euo pipefail  # Arrêt en cas d'erreur

# Configuration couleurs pour output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Emojis pour statut
SUCCESS="✅"
ERROR="❌"
WARNING="⚠️"
INFO="ℹ️"
ROCKET="🚀"
GEAR="⚙️"
CHART="📊"

# Variables de configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="supersmartmatch-v2"
VERSION="2.0.0"
DEFAULT_ENV="production"
DEPLOYMENT_TYPE=""
SKIP_TESTS=false
FORCE_REBUILD=false
MONITORING_ENABLED=true

# Fonctions utilitaires
print_banner() {
    echo -e "${PURPLE}"
    echo "════════════════════════════════════════════════════════════════"
    echo "🚀 SuperSmartMatch V2 - Déploiement Automatisé"
    echo "   Service Intelligent Unifié - Version ${VERSION}"
    echo "════════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}${INFO} [INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}${SUCCESS} [SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}${WARNING} [WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}${ERROR} [ERROR]${NC} $1"
}

log_step() {
    echo -e "${CYAN}${GEAR} [STEP]${NC} $1"
}

show_usage() {
    cat << EOF
${ROCKET} Usage: $0 [OPTIONS]

OPTIONS:
    -t, --type TYPE          Type de déploiement (docker|native|dev)
    -e, --env ENV           Environnement (production|staging|development)
    -s, --skip-tests        Ignorer les tests de validation
    -f, --force-rebuild     Forcer la reconstruction des images
    -m, --no-monitoring     Désactiver le monitoring
    -h, --help              Afficher cette aide

EXEMPLES:
    $0 --type docker --env production
    $0 --type native --env development --skip-tests
    $0 --type dev --force-rebuild

TYPES DE DÉPLOIEMENT:
    docker      Déploiement avec Docker Compose (recommandé)
    native      Installation Python native
    dev         Mode développement avec hot-reload
EOF
}

# Parsing des arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                DEPLOYMENT_TYPE="$2"
                shift 2
                ;;
            -e|--env)
                DEFAULT_ENV="$2"
                shift 2
                ;;
            -s|--skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            -f|--force-rebuild)
                FORCE_REBUILD=true
                shift
                ;;
            -m|--no-monitoring)
                MONITORING_ENABLED=false
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Option inconnue: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Vérification des prérequis
check_prerequisites() {
    log_step "Vérification des prérequis..."
    
    local missing_deps=()
    
    # Vérifications communes
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    # Vérifications spécifiques au type de déploiement
    case "$DEPLOYMENT_TYPE" in
        "docker")
            if ! command -v docker &> /dev/null; then
                missing_deps+=("docker")
            fi
            if ! command -v docker-compose &> /dev/null; then
                missing_deps+=("docker-compose")
            fi
            ;;
        "native"|"dev")
            if ! command -v pip3 &> /dev/null; then
                missing_deps+=("pip3")
            fi
            if ! command -v curl &> /dev/null; then
                missing_deps+=("curl")
            fi
            ;;
    esac
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Dépendances manquantes: ${missing_deps[*]}"
        echo -e "\n${INFO} Installez les dépendances manquantes:"
        
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "  brew install ${missing_deps[*]}"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            echo "  sudo apt-get install ${missing_deps[*]}"
        fi
        exit 1
    fi
    
    log_success "Tous les prérequis sont satisfaits"
}

# Configuration de l'environnement
setup_environment() {
    log_step "Configuration de l'environnement..."
    
    # Création du fichier .env si nécessaire
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            log_info "Fichier .env créé depuis .env.example"
        else
            log_warning "Fichier .env.example non trouvé, création manuelle nécessaire"
        fi
    fi
    
    # Variables d'environnement pour V2
    cat >> .env << EOF

# SuperSmartMatch V2 Configuration
SUPERSMARTMATCH_V2_ENABLED=true
SUPERSMARTMATCH_V2_PORT=5070
SUPERSMARTMATCH_V2_ENV=${DEFAULT_ENV}

# Intégrations services
NEXTEN_URL=http://localhost:5052
SUPERSMARTMATCH_V1_URL=http://localhost:5062
REDIS_URL=redis://localhost:6379

# Feature flags
ENABLE_V2=true
V2_TRAFFIC_PERCENTAGE=100
ENABLE_NEXTEN_ALGORITHM=true
ENABLE_SMART_SELECTION=true
EOF
    
    log_success "Environnement configuré pour ${DEFAULT_ENV}"
}

# Déploiement Docker
deploy_docker() {
    log_step "Déploiement Docker SuperSmartMatch V2..."
    
    # Vérification des fichiers Docker
    local required_files=("docker-compose.supersmartmatch-v2.yml" "Dockerfile.supersmartmatch-v2")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Fichier manquant: $file"
            exit 1
        fi
    done
    
    # Construction des images si nécessaire
    if [[ "$FORCE_REBUILD" == "true" ]] || ! docker images | grep -q supersmartmatch-v2; then
        log_step "Construction de l'image SuperSmartMatch V2..."
        docker build -f Dockerfile.supersmartmatch-v2 -t supersmartmatch-v2:${VERSION} .
        docker tag supersmartmatch-v2:${VERSION} supersmartmatch-v2:latest
        log_success "Image construite avec succès"
    fi
    
    # Arrêt des services existants
    log_step "Arrêt des services existants..."
    docker-compose -f docker-compose.supersmartmatch-v2.yml down --remove-orphans || true
    
    # Démarrage des services
    log_step "Démarrage des services SuperSmartMatch V2..."
    
    if [[ "$MONITORING_ENABLED" == "true" ]]; then
        docker-compose -f docker-compose.supersmartmatch-v2.yml up -d
        log_info "Services avec monitoring démarrés"
    else
        docker-compose -f docker-compose.supersmartmatch-v2.yml up -d \
            supersmartmatch-v2 redis-cache
        log_info "Services principaux démarrés (monitoring désactivé)"
    fi
    
    # Attendre que les services soient prêts
    log_step "Attente démarrage des services..."
    sleep 10
    
    # Vérification santé des services
    local max_retries=30
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s http://localhost:5070/health > /dev/null; then
            break
        fi
        
        retry_count=$((retry_count + 1))
        echo -n "."
        sleep 2
    done
    
    if [ $retry_count -eq $max_retries ]; then
        log_error "Service SuperSmartMatch V2 non accessible après ${max_retries} tentatives"
        docker-compose -f docker-compose.supersmartmatch-v2.yml logs supersmartmatch-v2
        exit 1
    fi
    
    log_success "Déploiement Docker complété"
}

# Déploiement natif Python
deploy_native() {
    log_step "Déploiement natif Python SuperSmartMatch V2..."
    
    # Création environnement virtuel
    if [[ ! -d "venv-supersmartmatch-v2" ]]; then
        log_step "Création de l'environnement virtuel..."
        python3 -m venv venv-supersmartmatch-v2
    fi
    
    # Activation environnement virtuel
    source venv-supersmartmatch-v2/bin/activate
    
    # Installation des dépendances
    log_step "Installation des dépendances Python..."
    pip install --upgrade pip
    pip install -r requirements-v2.txt
    
    # Démarrage Redis en Docker si pas déjà lancé
    if ! docker ps | grep -q redis-cache-v2; then
        log_step "Démarrage Redis cache..."
        docker run -d --name redis-cache-v2 -p 6379:6379 redis:7-alpine
    fi
    
    # Démarrage du service en arrière-plan
    log_step "Démarrage SuperSmartMatch V2..."
    nohup python supersmartmatch-v2-unified-service.py > supersmartmatch-v2.log 2>&1 &
    echo $! > supersmartmatch-v2.pid
    
    # Attendre démarrage
    sleep 5
    
    log_success "Déploiement natif complété"
}

# Déploiement développement
deploy_dev() {
    log_step "Configuration mode développement..."
    
    # Création environnement virtuel de dev
    if [[ ! -d "venv-dev" ]]; then
        python3 -m venv venv-dev
    fi
    
    source venv-dev/bin/activate
    
    # Installation dépendances dev
    pip install --upgrade pip
    pip install -r requirements-v2.txt
    
    # Installation outils de développement
    pip install black isort flake8 mypy pytest-cov pre-commit
    
    # Configuration pre-commit hooks
    if [[ -f ".pre-commit-config.yaml" ]]; then
        pre-commit install
        log_info "Pre-commit hooks installés"
    fi
    
    # Redis en Docker
    if ! docker ps | grep -q redis-dev; then
        docker run -d --name redis-dev -p 6379:6379 redis:7-alpine
    fi
    
    log_info "Mode développement configuré"
    log_info "Démarrage manuel: uvicorn supersmartmatch-v2-unified-service:app --reload --port 5070"
    
    log_success "Configuration développement complétée"
}

# Validation des services
validate_deployment() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        log_warning "Tests de validation ignorés"
        return
    fi
    
    log_step "Validation du déploiement..."
    
    # Test santé du service principal
    log_info "Test santé SuperSmartMatch V2..."
    if curl -s http://localhost:5070/health | grep -q "healthy"; then
        log_success "Service SuperSmartMatch V2 opérationnel"
    else
        log_error "Service SuperSmartMatch V2 non fonctionnel"
        exit 1
    fi
    
    # Tests d'intégration complets
    if [[ -f "validate-supersmartmatch-v2.py" ]]; then
        log_step "Exécution des tests d'intégration..."
        
        if python validate-supersmartmatch-v2.py; then
            log_success "Validation d'intégration réussie"
        else
            log_warning "Certains tests d'intégration ont échoué"
        fi
    fi
    
    # Test API V2
    log_info "Test API V2..."
    local test_payload='{
        "candidate": {"name": "Test User", "technical_skills": ["Python"]},
        "offers": [{"id": "test", "title": "Test Job"}],
        "algorithm": "auto"
    }'
    
    if curl -s -X POST http://localhost:5070/api/v2/match \
        -H "Content-Type: application/json" \
        -d "$test_payload" | grep -q "success"; then
        log_success "API V2 fonctionnelle"
    else
        log_warning "API V2 non accessible ou défaillante"
    fi
}

# Affichage des informations de déploiement
show_deployment_info() {
    echo -e "\n${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}${ROCKET} SuperSmartMatch V2 - Déploiement Terminé${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    
    echo -e "\n${CHART} ${CYAN}Services Disponibles:${NC}"
    echo -e "  ${GREEN}•${NC} SuperSmartMatch V2:  http://localhost:5070"
    echo -e "  ${GREEN}•${NC} API Documentation:   http://localhost:5070/api/docs"
    echo -e "  ${GREEN}•${NC} Health Check:        http://localhost:5070/health"
    echo -e "  ${GREEN}•${NC} Métriques:           http://localhost:5070/metrics"
    
    if [[ "$MONITORING_ENABLED" == "true" ]] && [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        echo -e "\n${CHART} ${CYAN}Monitoring:${NC}"
        echo -e "  ${GREEN}•${NC} Grafana Dashboard:   http://localhost:3000 (admin/supersmartmatch)"
        echo -e "  ${GREEN}•${NC} Prometheus:          http://localhost:9090"
    fi
    
    echo -e "\n${GEAR} ${CYAN}Commandes Utiles:${NC}"
    echo -e "  ${WHITE}# Test rapide API${NC}"
    echo -e "  curl http://localhost:5070/health"
    
    echo -e "\n  ${WHITE}# Test matching V2${NC}"
    echo -e "  curl -X POST http://localhost:5070/api/v2/match \\\\"
    echo -e "    -H 'Content-Type: application/json' \\\\"
    echo -e "    -d '{\"candidate\":{\"name\":\"Test\"},\"offers\":[{\"id\":\"1\"}]}'"
    
    if [[ "$DEPLOYMENT_TYPE" == "docker" ]]; then
        echo -e "\n  ${WHITE}# Logs services${NC}"
        echo -e "  docker-compose -f docker-compose.supersmartmatch-v2.yml logs -f"
        
        echo -e "\n  ${WHITE}# Arrêt services${NC}"
        echo -e "  docker-compose -f docker-compose.supersmartmatch-v2.yml down"
    fi
    
    echo -e "\n  ${WHITE}# Validation complète${NC}"
    echo -e "  python validate-supersmartmatch-v2.py"
    
    echo -e "\n${SUCCESS} ${GREEN}Déploiement SuperSmartMatch V2 réussi !${NC}"
    echo -e "${INFO} ${BLUE}Consultez README-SUPERSMARTMATCH-V2.md pour plus de détails${NC}"
}

# Fonction principale
main() {
    print_banner
    
    # Gestion des arguments
    if [[ $# -eq 0 ]]; then
        log_info "Mode interactif - Sélectionnez le type de déploiement:"
        echo "1) Docker (recommandé)"
        echo "2) Python natif"
        echo "3) Mode développement"
        read -p "Votre choix (1-3): " choice
        
        case $choice in
            1) DEPLOYMENT_TYPE="docker" ;;
            2) DEPLOYMENT_TYPE="native" ;;
            3) DEPLOYMENT_TYPE="dev" ;;
            *) log_error "Choix invalide"; exit 1 ;;
        esac
    else
        parse_arguments "$@"
    fi
    
    # Validation du type de déploiement
    if [[ ! "$DEPLOYMENT_TYPE" =~ ^(docker|native|dev)$ ]]; then
        log_error "Type de déploiement invalide: $DEPLOYMENT_TYPE"
        show_usage
        exit 1
    fi
    
    log_info "Type de déploiement: ${DEPLOYMENT_TYPE}"
    log_info "Environnement: ${DEFAULT_ENV}"
    
    # Exécution du déploiement
    check_prerequisites
    setup_environment
    
    case "$DEPLOYMENT_TYPE" in
        "docker")
            deploy_docker
            ;;
        "native")
            deploy_native
            ;;
        "dev")
            deploy_dev
            ;;
    esac
    
    validate_deployment
    show_deployment_info
}

# Gestion des signaux pour nettoyage
cleanup() {
    log_info "Nettoyage en cours..."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Exécution
main "$@"
