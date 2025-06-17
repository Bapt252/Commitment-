#!/bin/bash

# SuperSmartMatch V3.0 Enhanced - Script de démarrage corrigé
# Auteur: Claude
# Version: 3.0.0

set -e

echo "🎯 SuperSmartMatch V3.0 Enhanced - Démarrage des services"
echo "============================================================"

# Configuration des ports (évite conflits AirPlay macOS)
CV_PARSER_PORT=5051
JOB_PARSER_PORT=5053
SUPERSMARTMATCH_PORT=5067
API_GATEWAY_PORT=5065
DASHBOARD_PORT=5070
DATA_ADAPTER_PORT=8000

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages colorés
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

# Fonction pour vérifier si un port est libre
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        log_warning "Port $port déjà occupé"
        return 1
    fi
    return 0
}

# Fonction pour démarrer un service
start_service() {
    local service_name=$1
    local command=$2
    local port=$3
    local log_file="logs/${service_name}.log"
    
    log_info "Démarrage $service_name sur port $port..."
    
    # Créer le dossier logs s'il n'existe pas
    mkdir -p logs
    
    # Démarrer le service en arrière-plan
    nohup $command > "$log_file" 2>&1 &
    local pid=$!
    
    # Sauvegarder le PID
    echo $pid > "logs/${service_name}.pid"
    
    # Attendre un peu que le service démarre
    sleep 3
    
    # Vérifier si le service répond
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        log_success "$service_name démarré avec succès (PID: $pid)"
        return 0
    else
        log_warning "$service_name démarré mais ne répond pas encore (PID: $pid)"
        return 0
    fi
}

# Fonction pour installer les dépendances si nécessaire
install_dependencies() {
    log_info "Vérification des dépendances..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    # Installer les packages Python requis
    if ! python3 -c "import fastapi, uvicorn, streamlit" &> /dev/null; then
        log_info "Installation des dépendances Python..."
        pip install fastapi uvicorn streamlit requests aiohttp httpx
    fi
    
    log_success "Dépendances OK"
}

# Fonction pour créer la structure de test
setup_test_environment() {
    log_info "Configuration de l'environnement de test..."
    
    if [ -f "test_data_automation.py" ]; then
        python3 test_data_automation.py
        log_success "Structure de test créée"
    else
        log_warning "Script de test non trouvé, structure manuelle requise"
    fi
}

# Fonction pour arrêter tous les services
stop_all_services() {
    log_info "Arrêt de tous les services..."
    
    for pid_file in logs/*.pid; do
        if [ -f "$pid_file" ]; then
            local pid=$(cat "$pid_file")
            local service_name=$(basename "$pid_file" .pid)
            
            if kill -0 "$pid" 2>/dev/null; then
                log_info "Arrêt $service_name (PID: $pid)"
                kill "$pid"
                rm "$pid_file"
            fi
        fi
    done
    
    log_success "Tous les services arrêtés"
}

# Fonction pour vérifier la santé des services
check_services_health() {
    log_info "Vérification de la santé des services..."
    
    local services=(
        "CV Parser:$CV_PARSER_PORT"
        "Job Parser:$JOB_PARSER_PORT"
        "SuperSmartMatch:$SUPERSMARTMATCH_PORT"
        "API Gateway:$API_GATEWAY_PORT"
        "Dashboard:$DASHBOARD_PORT"
    )
    
    local healthy_count=0
    
    for service in "${services[@]}"; do
        local name=$(echo $service | cut -d: -f1)
        local port=$(echo $service | cut -d: -f2)
        
        if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "$name: OK"
            ((healthy_count++))
        else
            log_warning "$name: Not responding"
        fi
    done
    
    log_info "Services actifs: $healthy_count/${#services[@]}"
}

# Fonction principale
main() {
    # Gérer les signaux d'interruption
    trap 'log_info "Interruption détectée, arrêt des services..."; stop_all_services; exit 0' INT TERM
    
    case "${1:-start}" in
        "start")
            log_info "🏗️  Démarrage des services..."
            
            # Vérifications préliminaires
            install_dependencies
            setup_test_environment
            
            # Démarrer les services un par un
            start_service "cv_parser" "python3 cv_parser_service.py" $CV_PARSER_PORT
            start_service "job_parser" "python3 job_parser_service.py" $JOB_PARSER_PORT
            start_service "api_gateway" "python3 api_gateway.py" $API_GATEWAY_PORT
            
            # Services optionnels (peuvent déjà être démarrés)
            if check_port $SUPERSMARTMATCH_PORT; then
                log_info "Port $SUPERSMARTMATCH_PORT libre, démarrage SuperSmartMatch..."
                # start_service "supersmartmatch" "uvicorn app:app --host 0.0.0.0 --port $SUPERSMARTMATCH_PORT" $SUPERSMARTMATCH_PORT
            else
                log_success "SuperSmartMatch déjà en cours d'exécution sur port $SUPERSMARTMATCH_PORT"
            fi
            
            if check_port $DASHBOARD_PORT; then
                log_info "Port $DASHBOARD_PORT libre, démarrage Dashboard..."
                # start_service "dashboard" "streamlit run dashboard_v3.py --server.port $DASHBOARD_PORT --server.headless true" $DASHBOARD_PORT
            else
                log_success "Dashboard déjà en cours d'exécution sur port $DASHBOARD_PORT"
            fi
            
            # Attendre que les services soient prêts
            log_info "⏳ Attente de la disponibilité des services..."
            sleep 5
            
            # Vérifier la santé
            check_services_health
            
            # Afficher le résumé
            echo ""
            echo "🎯 SuperSmartMatch V3.0 Enhanced - Prêt !"
            echo "========================================"
            echo "📊 Dashboard: http://localhost:$DASHBOARD_PORT"
            echo "🌐 API Gateway: http://localhost:$API_GATEWAY_PORT"
            echo "📄 CV Parser: http://localhost:$CV_PARSER_PORT"
            echo "💼 Job Parser: http://localhost:$JOB_PARSER_PORT"
            echo "🤖 SuperSmartMatch: http://localhost:$SUPERSMARTMATCH_PORT"
            echo ""
            echo "🧪 Pour lancer les tests:"
            echo "python -m unittest test_supersmartmatch_v3_enhanced.py -v"
            echo ""
            echo "🔧 Pour arrêter les services:"
            echo "./start_services_fixed.sh stop"
            echo ""
            ;;
            
        "stop")
            stop_all_services
            ;;
            
        "restart")
            log_info "Redémarrage des services..."
            stop_all_services
            sleep 2
            $0 start
            ;;
            
        "status")
            check_services_health
            ;;
            
        "logs")
            log_info "Logs des services:"
            for log_file in logs/*.log; do
                if [ -f "$log_file" ]; then
                    echo "\n=== $(basename "$log_file") ==="
                    tail -10 "$log_file"
                fi
            done
            ;;
            
        *)
            echo "Usage: $0 {start|stop|restart|status|logs}"
            echo ""
            echo "  start   - Démarre tous les services SuperSmartMatch V3.0"
            echo "  stop    - Arrête tous les services"
            echo "  restart - Redémarre tous les services"
            echo "  status  - Vérifie l'état des services"
            echo "  logs    - Affiche les logs des services"
            exit 1
            ;;
    esac
}

# Lancer la fonction principale avec tous les arguments
main "$@"