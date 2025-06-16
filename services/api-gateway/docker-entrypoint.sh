#!/bin/bash
# Script d'entrée pour l'API Gateway SuperSmartMatch V2
# Gestion intelligente du démarrage avec vérifications de santé

set -e

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
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

# Fonction pour attendre qu'un service soit disponible
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout=${4:-60}
    
    log_info "Attente de $service_name ($host:$port)..."
    
    for i in $(seq 1 $timeout); do
        if nc -z $host $port 2>/dev/null; then
            log_success "$service_name est disponible"
            return 0
        fi
        
        if [ $i -eq $timeout ]; then
            log_error "$service_name non disponible après $timeout secondes"
            return 1
        fi
        
        sleep 1
    done
}

# Fonction pour vérifier les variables d'environnement critiques
check_environment() {
    log_info "Vérification des variables d'environnement..."
    
    local required_vars=(
        "JWT_SECRET"
        "DATABASE_URL" 
        "REDIS_URL"
        "CV_PARSER_URL"
        "JOB_PARSER_URL"
        "MATCHING_SERVICE_URL"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=($var)
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Variables d'environnement manquantes: ${missing_vars[*]}"
        log_error "Impossible de démarrer l'API Gateway"
        exit 1
    fi
    
    log_success "Toutes les variables d'environnement sont définies"
}

# Fonction pour attendre les services dépendants
wait_for_dependencies() {
    log_info "Attente des services dépendants..."
    
    # Extraire host et port de DATABASE_URL
    if [[ $DATABASE_URL =~ postgresql://[^@]*@([^:]+):([^/]+) ]]; then
        db_host="${BASH_REMATCH[1]}"
        db_port="${BASH_REMATCH[2]}"
        wait_for_service $db_host $db_port "PostgreSQL" 60
    fi
    
    # Extraire host et port de REDIS_URL
    if [[ $REDIS_URL =~ redis://([^:]+):([^/]+) ]]; then
        redis_host="${BASH_REMATCH[1]}"
        redis_port="${BASH_REMATCH[2]}"
        wait_for_service $redis_host $redis_port "Redis" 30
    fi
    
    # Vérifier les microservices (optionnel en mode dégradé)
    local services=(
        "$CV_PARSER_URL cv-parser"
        "$JOB_PARSER_URL job-parser" 
        "$MATCHING_SERVICE_URL matching-service"
    )
    
    for service_info in "${services[@]}"; do
        local url=$(echo $service_info | cut -d' ' -f1)
        local name=$(echo $service_info | cut -d' ' -f2)
        
        if [[ $url =~ http://([^:]+):([^/]+) ]]; then
            local host="${BASH_REMATCH[1]}"
            local port="${BASH_REMATCH[2]}"
            
            if ! wait_for_service $host $port $name 10; then
                log_warning "$name non disponible - démarrage en mode dégradé"
            fi
        fi
    done
}

# Fonction pour initialiser la base de données
init_database() {
    log_info "Initialisation de la base de données..."
    
    python -c "
import asyncio
from utils.database import initialize_database

async def main():
    await initialize_database()

if __name__ == '__main__':
    asyncio.run(main())
" 2>/dev/null || {
        log_warning "Impossible d'initialiser la DB - elle sera créée au premier démarrage"
    }
}

# Fonction pour valider la configuration
validate_config() {
    log_info "Validation de la configuration..."
    
    python -c "
from config.settings import get_settings
try:
    settings = get_settings()
    print(f'Configuration valide pour environnement: {settings.ENVIRONMENT}')
except Exception as e:
    print(f'Erreur de configuration: {e}')
    exit(1)
"
    
    if [ $? -ne 0 ]; then
        log_error "Configuration invalide"
        exit 1
    fi
    
    log_success "Configuration validée"
}

# Fonction de health check interne
health_check() {
    log_info "Vérification de santé interne..."
    
    # Test d'import des modules principaux
    python -c "
import sys
try:
    from app import app
    from config.settings import get_settings
    from routes import auth, parsers, matching, health
    from middleware.auth_middleware import JWTMiddleware
    from utils.proxy import proxy_manager
    print('Tous les modules importés avec succès')
except ImportError as e:
    print(f'Erreur d\'import: {e}')
    sys.exit(1)
"
    
    if [ $? -ne 0 ]; then
        log_error "Erreur lors des vérifications internes"
        exit 1
    fi
    
    log_success "Vérifications internes OK"
}

# Fonction pour nettoyer les ressources au démarrage
cleanup_resources() {
    log_info "Nettoyage des ressources temporaires..."
    
    # Nettoyer les fichiers temporaires
    rm -rf /app/temp/* 2>/dev/null || true
    
    # Créer les répertoires nécessaires
    mkdir -p /app/logs /app/temp /app/uploads
    
    log_success "Ressources nettoyées"
}

# Fonction principale de démarrage
main() {
    log_info "🚀 Démarrage de SuperSmartMatch V2 API Gateway"
    log_info "Environment: ${ENVIRONMENT:-development}"
    log_info "Version: $(python -c 'from config.settings import get_settings; print(get_settings().VERSION)')"
    
    # Étapes de pré-démarrage
    check_environment
    cleanup_resources
    validate_config
    wait_for_dependencies
    health_check
    
    # Initialisation optionnelle de la DB
    if [ "${INIT_DB:-true}" = "true" ]; then
        init_database
    fi
    
    log_success "✅ Pré-démarrage terminé avec succès"
    log_info "🌟 Lancement de l'API Gateway sur le port ${PORT:-5050}"
    
    # Exécuter la commande passée en argument
    exec "$@"
}

# Gestion des signaux pour un arrêt propre
trap 'log_info "Signal reçu, arrêt en cours..."; exit 0' SIGTERM SIGINT

# Installer netcat si pas disponible (pour les checks de port)
if ! command -v nc >/dev/null 2>&1; then
    log_warning "netcat non disponible, installation..."
    apt-get update && apt-get install -y netcat-openbsd >/dev/null 2>&1 || true
fi

# Lancer la fonction principale
main "$@"
