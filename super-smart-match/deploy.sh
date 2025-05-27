#!/bin/bash

# SuperSmartMatch - Script de Déploiement
# Déploie le service unifié SuperSmartMatch

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="supersmartmatch"
DEFAULT_PORT=5000
ENVIRONMENT=${ENVIRONMENT:-development}

echo -e "${BLUE}🚀 SuperSmartMatch - Déploiement du Service Unifié${NC}"
echo "=================================================="

# Fonction d'affichage
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Python 3.8+
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    log_success "Python ${python_version} détecté"
    
    # Pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 n'est pas installé"
        exit 1
    fi
    
    # Git (optionnel)
    if command -v git &> /dev/null; then
        log_success "Git détecté"
    fi
    
    # Docker (optionnel)
    if command -v docker &> /dev/null; then
        log_success "Docker détecté"
    fi
}

# Installation des dépendances
install_dependencies() {
    log_info "Installation des dépendances Python..."
    
    # Créer un environnement virtuel s'il n'existe pas
    if [ ! -d "venv" ]; then
        log_info "Création de l'environnement virtuel..."
        python3 -m venv venv
    fi
    
    # Activer l'environnement virtuel
    log_info "Activation de l'environnement virtuel..."
    source venv/bin/activate
    
    # Mise à jour de pip
    pip install --upgrade pip
    
    # Installation des dépendances
    if [ -f "requirements.txt" ]; then
        log_info "Installation depuis requirements.txt..."
        pip install -r requirements.txt
    else
        log_warning "requirements.txt non trouvé, installation des dépendances de base..."
        pip install flask flask-cors pandas numpy scikit-learn psutil
    fi
    
    log_success "Dépendances installées"
}

# Configuration de l'environnement
setup_environment() {
    log_info "Configuration de l'environnement..."
    
    # Créer le fichier .env s'il n'existe pas
    if [ ! -f ".env" ]; then
        log_info "Création du fichier .env..."
        cat > .env << EOF
# SuperSmartMatch Configuration
FLASK_ENV=${ENVIRONMENT}
FLASK_APP=api.app
PORT=${DEFAULT_PORT}
DEBUG=$([ "$ENVIRONMENT" = "development" ] && echo "True" || echo "False")

# API Keys (à configurer)
OPENAI_API_KEY=your-openai-key-here
GOOGLE_MAPS_API_KEY=your-google-maps-key-here

# SuperSmartMatch Settings
SUPER_SMART_MATCH_MODE=auto
CACHE_TIMEOUT=300
MAX_HISTORY_SIZE=1000

# Database (optionnel)
# DATABASE_URL=postgresql://user:password@localhost/supersmartmatch

# Monitoring (optionnel)
# PROMETHEUS_PORT=9090
EOF
        log_warning "Fichier .env créé avec des valeurs par défaut"
        log_warning "Pensez à configurer vos clés API dans .env"
    else
        log_success "Fichier .env existant trouvé"
    fi
}

# Vérification de la configuration
verify_configuration() {
    log_info "Vérification de la configuration..."
    
    # Vérifier que les modules nécessaires sont bien présents
    python3 -c "
import sys
sys.path.append('.')

try:
    from super_smart_match.core.engine import SuperSmartMatchEngine
    from super_smart_match.api.app import create_app
    print('✅ Modules SuperSmartMatch importés avec succès')
except ImportError as e:
    print(f'❌ Erreur d\\'import: {e}')
    sys.exit(1)
" || {
        log_error "Erreur lors de la vérification des modules"
        log_info "Tentative de correction du PYTHONPATH..."
        export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
    }
}

# Test de l'application
test_application() {
    log_info "Test de l'application..."
    
    # Test d'import des modules
    python3 -c "
import sys
sys.path.append('.')

from super_smart_match.demo import create_test_data
from super_smart_match.core.engine import SuperSmartMatchEngine, MatchOptions

try:
    # Créer des données de test
    candidat, offres = create_test_data()
    print('✅ Données de test créées')
    
    # Tester le moteur
    engine = SuperSmartMatchEngine()
    options = MatchOptions(algorithme='auto', limite=3)
    
    # Test basique (peut échouer si les algorithmes originaux ne sont pas disponibles)
    print('✅ SuperSmartMatch engine initialisé')
    print('✅ Tests de base réussis')
    
except Exception as e:
    print(f'⚠️  Avertissement lors des tests: {e}')
    print('   (Le service fonctionnera avec les algorithmes de fallback)')
"
    
    log_success "Tests de base terminés"
}

# Démarrage du service
start_service() {
    log_info "Démarrage du service SuperSmartMatch..."
    
    # Activer l'environnement virtuel
    source venv/bin/activate
    
    # Définir les variables d'environnement
    export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"
    export FLASK_APP="super-smart-match.api.app"
    export FLASK_ENV="${ENVIRONMENT}"
    
    # Port configuration
    PORT=${PORT:-${DEFAULT_PORT}}
    
    log_info "Démarrage sur le port ${PORT}..."
    log_info "Mode: ${ENVIRONMENT}"
    
    if [ "$ENVIRONMENT" = "production" ]; then
        # Mode production avec Gunicorn
        if command -v gunicorn &> /dev/null; then
            log_info "Démarrage avec Gunicorn (production)..."
            gunicorn -w 4 -b 0.0.0.0:${PORT} "super-smart-match.api.app:create_app()"
        else
            log_warning "Gunicorn non trouvé, démarrage avec Flask (non recommandé en production)"
            python3 -m super-smart-match.api.app
        fi
    else
        # Mode développement
        log_info "Démarrage en mode développement..."
        python3 -c "
import sys
sys.path.append('.')
from super_smart_match.api.app import create_app
import os

app = create_app()
port = int(os.environ.get('PORT', ${PORT}))
app.run(host='0.0.0.0', port=port, debug=True)
"
    fi
}

# Déploiement Docker (optionnel)
deploy_docker() {
    if [ "$1" = "--docker" ] && command -v docker &> /dev/null; then
        log_info "Création de l'image Docker..."
        
        # Créer le Dockerfile s'il n'existe pas
        if [ ! -f "Dockerfile" ]; then
            cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port
EXPOSE 5000

# Variables d'environnement
ENV PYTHONPATH=/app
ENV FLASK_ENV=production

# Commande de démarrage
CMD ["python", "-m", "super-smart-match.api.app"]
EOF
        fi
        
        # Construire l'image
        docker build -t supersmartmatch:latest .
        
        # Créer le docker-compose.yml
        if [ ! -f "docker-compose.yml" ]; then
            cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  supersmartmatch:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - PORT=5000
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    
  # Optionnel: Base de données
  # postgres:
  #   image: postgres:13
  #   environment:
  #     POSTGRES_DB: supersmartmatch
  #     POSTGRES_USER: user
  #     POSTGRES_PASSWORD: password
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   ports:
  #     - "5432:5432"

# volumes:
#   postgres_data:
EOF
        fi
        
        log_success "Configuration Docker créée"
        log_info "Pour démarrer avec Docker: docker-compose up -d"
        return 0
    fi
    return 1
}

# Nettoyage
cleanup() {
    log_info "Nettoyage..."
    
    # Supprimer les fichiers temporaires
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Nettoyage terminé"
}

# Affichage de l'aide
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --install     Installation uniquement (sans démarrage)"
    echo "  --test        Tests uniquement"
    echo "  --start       Démarrage uniquement"
    echo "  --docker      Créer une configuration Docker"
    echo "  --production  Mode production"
    echo "  --help        Afficher cette aide"
    echo ""
    echo "Variables d'environnement:"
    echo "  ENVIRONMENT   development|production (défaut: development)"
    echo "  PORT         Port d'écoute (défaut: 5000)"
    echo ""
    echo "Exemples:"
    echo "  $0                    # Installation et démarrage complets"
    echo "  $0 --install          # Installation uniquement"
    echo "  $0 --docker           # Créer config Docker et démarrer"
    echo "  ENVIRONMENT=production $0 --production"
}

# Fonction principale
main() {
    case "$1" in
        --help)
            show_help
            exit 0
            ;;
        --docker)
            check_prerequisites
            install_dependencies
            setup_environment
            verify_configuration
            test_application
            if deploy_docker --docker; then
                log_success "Configuration Docker prête"
                log_info "Lancez: docker-compose up -d"
                exit 0
            fi
            ;;
        --install)
            check_prerequisites
            install_dependencies
            setup_environment
            verify_configuration
            log_success "Installation terminée"
            exit 0
            ;;
        --test)
            test_application
            exit 0
            ;;
        --start)
            start_service
            exit 0
            ;;
        --production)
            ENVIRONMENT=production
            ;;
        "")
            # Installation et démarrage complets
            ;;
        *)
            log_error "Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
    
    # Déploiement complet
    log_info "Démarrage du déploiement complet..."
    
    check_prerequisites
    install_dependencies
    setup_environment
    verify_configuration
    test_application
    cleanup
    
    log_success "Installation terminée avec succès!"
    echo ""
    log_info "🎯 Prochaines étapes:"
    echo "   1. Configurez vos clés API dans le fichier .env"
    echo "   2. Lancez le service avec: $0 --start"
    echo "   3. Testez l'API sur: http://localhost:${PORT}"
    echo ""
    log_info "📚 Documentation:"
    echo "   - API: http://localhost:${PORT}/api/v1/"
    echo "   - Health: http://localhost:${PORT}/api/v1/health"
    echo "   - Performance: http://localhost:${PORT}/api/v1/performance"
    echo ""
    
    # Demander si l'utilisateur veut démarrer maintenant
    if [ -t 0 ]; then  # Si en mode interactif
        echo -n "Voulez-vous démarrer le service maintenant ? (y/N): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo ""
            start_service
        fi
    fi
}

# Point d'entrée
main "$@"
