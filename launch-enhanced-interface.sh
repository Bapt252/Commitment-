#!/bin/bash

# 🚀 SuperSmartMatch V2 - Lancement Interface Enrichie
# Script de démarrage automatique avec vérifications complètes

echo "🚀 SuperSmartMatch V2 - Démarrage Interface Enrichie"
echo "=================================================="

# Couleurs pour les messages
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

# Vérification de Docker
check_docker() {
    log_info "Vérification de Docker..."
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé ou n'est pas dans le PATH"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker n'est pas démarré ou n'est pas accessible"
        exit 1
    fi
    
    log_success "Docker est opérationnel"
}

# Vérification de Docker Compose
check_docker_compose() {
    log_info "Vérification de Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    log_success "Docker Compose est disponible"
}

# Vérification des fichiers requis
check_files() {
    log_info "Vérification des fichiers requis..."
    
    if [ ! -f "docker-compose.v2.yml" ]; then
        log_error "Fichier docker-compose.v2.yml introuvable"
        exit 1
    fi
    
    if [ ! -f "web-interface/index-enhanced.html" ]; then
        log_error "Interface enrichie introuvable"
        exit 1
    fi
    
    log_success "Tous les fichiers requis sont présents"
}

# Démarrage des services
start_services() {
    log_info "Démarrage des services SuperSmartMatch V2..."
    
    # Arrêt des services existants
    docker-compose -f docker-compose.v2.yml down &> /dev/null
    
    # Démarrage des nouveaux services
    if docker-compose -f docker-compose.v2.yml up -d; then
        log_success "Services démarrés avec succès"
    else
        log_error "Erreur lors du démarrage des services"
        exit 1
    fi
}

# Attente que les services soient prêts
wait_for_services() {
    log_info "Attente de la disponibilité des services..."
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:5051/health &> /dev/null && \
           curl -s http://localhost:5053/health &> /dev/null; then
            log_success "Tous les services sont opérationnels"
            return 0
        fi
        
        echo -n "."
        sleep 2
        ((attempt++))
    done
    
    log_warning "Certains services pourraient ne pas être complètement prêts"
}

# Démarrage du serveur web
start_web_server() {
    log_info "Démarrage du serveur web..."
    
    # Vérifier si le port 8080 est libre
    if lsof -i :8080 &> /dev/null; then
        log_warning "Le port 8080 est déjà utilisé, arrêt du processus existant..."
        pkill -f "python.*8080" || true
        sleep 2
    fi
    
    # Démarrer le serveur web en arrière-plan
    cd web-interface
    nohup python3 -m http.server 8080 > ../web-server.log 2>&1 &
    WEB_PID=$!
    cd ..
    
    # Sauvegarder le PID du serveur web
    echo $WEB_PID > web-server.pid
    
    log_success "Serveur web démarré (PID: $WEB_PID)"
}

# Vérification de l'interface web
check_web_interface() {
    log_info "Vérification de l'interface web..."
    
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8080 &> /dev/null; then
            log_success "Interface web accessible"
            return 0
        fi
        
        echo -n "."
        sleep 1
        ((attempt++))
    done
    
    log_error "Interface web non accessible"
    return 1
}

# Affichage des informations de connexion
show_connection_info() {
    echo ""
    echo "🎯 SuperSmartMatch V2 - Interface Enrichie Démarrée!"
    echo "=================================================="
    echo ""
    echo "📱 Interface Standard    : http://localhost:8080"
    echo "🚀 Interface Enrichie    : http://localhost:8080/index-enhanced.html"
    echo ""
    echo "🔍 Services API :"
    echo "   CV Parser V2          : http://localhost:5051"
    echo "   Job Parser V2         : http://localhost:5053"
    echo "   Redis Cache           : localhost:6379"
    echo ""
    echo "📊 Fonctionnalités Enrichies :"
    echo "   ✅ Scoring détaillé visuel (40%+30%+15%+15%)"
    echo "   ✅ Analyse par onglets (Missions, Compétences, Expérience, Qualité)"
    echo "   ✅ Recommandations actionables"
    echo "   ✅ Export de rapports JSON"
    echo "   ✅ Démonstration automatisée"
    echo ""
    echo "🎮 Démarrage Rapide :"
    echo "   1. Ouvrir http://localhost:8080/index-enhanced.html"
    echo "   2. Cliquer sur '🎯 Démonstration Complète'"
    echo "   3. Observer l'analyse détaillée en temps réel"
    echo ""
    echo "📋 Pour les vrais documents :"
    echo "   1. Glisser un CV PDF dans la zone CV Parser"
    echo "   2. Glisser une fiche de poste PDF dans la zone Job Parser"
    echo "   3. Cliquer sur '🚀 Calcul Matching Détaillé'"
    echo ""
}

# Fonction d'arrêt propre
cleanup() {
    log_info "Arrêt des services..."
    
    # Arrêt du serveur web
    if [ -f "web-server.pid" ]; then
        WEB_PID=$(cat web-server.pid)
        if kill -0 $WEB_PID 2>/dev/null; then
            kill $WEB_PID
            log_success "Serveur web arrêté"
        fi
        rm -f web-server.pid
    fi
    
    # Arrêt des services Docker
    docker-compose -f docker-compose.v2.yml down
    log_success "Services Docker arrêtés"
}

# Gestion des signaux pour arrêt propre
trap cleanup EXIT INT TERM

# Vérification des arguments
if [ "$1" = "--stop" ]; then
    cleanup
    exit 0
fi

if [ "$1" = "--status" ]; then
    echo "🔍 Statut des Services SuperSmartMatch V2"
    echo "========================================"
    
    # Vérification Docker
    if docker-compose -f docker-compose.v2.yml ps | grep -q "Up"; then
        echo "✅ Services Docker : Actifs"
    else
        echo "❌ Services Docker : Inactifs"
    fi
    
    # Vérification serveur web
    if lsof -i :8080 &> /dev/null; then
        echo "✅ Serveur Web : Actif (port 8080)"
    else
        echo "❌ Serveur Web : Inactif"
    fi
    
    # Vérification APIs
    if curl -s http://localhost:5051/health &> /dev/null; then
        echo "✅ CV Parser V2 : Opérationnel"
    else
        echo "❌ CV Parser V2 : Non accessible"
    fi
    
    if curl -s http://localhost:5053/health &> /dev/null; then
        echo "✅ Job Parser V2 : Opérationnel"
    else
        echo "❌ Job Parser V2 : Non accessible"
    fi
    
    exit 0
fi

# Menu d'aide
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "🚀 SuperSmartMatch V2 - Script de Lancement Interface Enrichie"
    echo ""
    echo "Usage:"
    echo "  $0                 # Démarrer tous les services et l'interface"
    echo "  $0 --stop          # Arrêter tous les services"
    echo "  $0 --status        # Vérifier le statut des services"
    echo "  $0 --help          # Afficher cette aide"
    echo ""
    echo "L'interface enrichie sera accessible sur :"
    echo "  http://localhost:8080/index-enhanced.html"
    echo ""
    exit 0
fi

# Exécution principale
main() {
    check_docker
    check_docker_compose
    check_files
    start_services
    wait_for_services
    start_web_server
    check_web_interface
    show_connection_info
    
    # Attendre indéfiniment (Ctrl+C pour arrêter)
    log_info "Services en cours d'exécution. Appuyez sur Ctrl+C pour arrêter."
    while true; do
        sleep 10
        # Vérification périodique des services
        if ! curl -s http://localhost:5051/health &> /dev/null || \
           ! curl -s http://localhost:5053/health &> /dev/null; then
            log_warning "Un ou plusieurs services semblent indisponibles"
        fi
    done
}

# Démarrage du script
main