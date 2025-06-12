#!/bin/bash

# Script de déploiement du monitoring Prometheus/Grafana
# Session 2 : Setup environnement et outils de développement

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
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

# Vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérifier que Docker fonctionne
    if ! docker info &> /dev/null; then
        log_error "Docker n'est pas démarré"
        exit 1
    fi
    
    log_success "Prérequis vérifiés"
}

# Créer la structure des dossiers
create_directories() {
    log_info "Création de la structure des dossiers..."
    
    # Dossiers de configuration monitoring
    mkdir -p monitoring/{prometheus/{rules},grafana/{provisioning/{datasources,dashboards},dashboards/{system,services,databases,business}},alertmanager}
    
    # Permissions pour Grafana
    sudo chown -R 472:472 monitoring/grafana/ 2>/dev/null || log_warning "Impossible de définir les permissions Grafana (necessaire pour les volumes)"
    
    log_success "Structure des dossiers créée"
}

# Créer les fichiers de configuration
create_config_files() {
    log_info "Création des fichiers de configuration..."
    
    # Note: Les fichiers ont été créés via les artifacts précédents
    # Ce script assume qu'ils sont déjà en place
    
    # Vérifier la présence des fichiers essentiels
    local required_files=(
        "monitoring/prometheus/prometheus.yml"
        "monitoring/prometheus/rules/alert-rules.yml"
        "monitoring/alertmanager/alertmanager.yml"
        "monitoring/grafana/provisioning/datasources/prometheus.yml"
        "monitoring/grafana/provisioning/dashboards/dashboards.yml"
        "docker-compose.monitoring.yml"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Fichier manquant: $file"
            log_info "Veuillez vous assurer que tous les fichiers de configuration sont en place"
            exit 1
        fi
    done
    
    log_success "Fichiers de configuration vérifiés"
}

# Démarrer les services de monitoring
start_monitoring() {
    log_info "Démarrage des services de monitoring..."
    
    # Arrêter les services existants si ils tournent
    log_info "Arrêt des services existants..."
    docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml down 2>/dev/null || true
    
    # Démarrer tous les services
    log_info "Démarrage de tous les services..."
    docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
    
    log_success "Services de monitoring démarrés"
}

# Vérifier que les services sont opérationnels
check_services() {
    log_info "Vérification de l'état des services..."
    
    local services=(
        "prometheus:9090:Prometheus"
        "grafana:3000:Grafana"
        "node-exporter:9100:Node Exporter"
        "cadvisor:8080:cAdvisor"
        "alertmanager:9093:AlertManager"
        "redis-exporter:9121:Redis Exporter"
        "postgres-exporter:9187:Postgres Exporter"
    )
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service port name <<< "$service_info"
        
        log_info "Vérification de $name sur le port $port..."
        
        # Attendre que le service soit disponible (timeout 60s)
        local timeout=60
        local count=0
        
        while ! curl -s "http://localhost:$port" >/dev/null 2>&1; do
            sleep 2
            count=$((count + 2))
            
            if [[ $count -ge $timeout ]]; then
                log_warning "$name n'est pas accessible sur le port $port (timeout)"
                break
            fi
        done
        
        if curl -s "http://localhost:$port" >/dev/null 2>&1; then
            log_success "$name est opérationnel sur http://localhost:$port"
        fi
    done
}

# Afficher les informations d'accès
show_access_info() {
    log_info "=== INFORMATIONS D'ACCÈS ==="
    echo
    log_success "Monitoring déployé avec succès!"
    echo
    echo "🔍 Services de monitoring accessibles:"
    echo "  • Prometheus:     http://localhost:9090"
    echo "  • Grafana:        http://localhost:3001 (admin/admin123)"
    echo "  • AlertManager:   http://localhost:9093"
    echo "  • Node Exporter:  http://localhost:9100"
    echo "  • cAdvisor:       http://localhost:8080"
    echo
    echo "📊 Services métier existants:"
    echo "  • API principale: http://localhost:5050"
    echo "  • CV Parser:      http://localhost:5051"
    echo "  • Job Parser:     http://localhost:5055"
    echo "  • Matching API:   http://localhost:5052"
    echo "  • Frontend:       http://localhost:3000"
    echo
    echo "🗄️ Services de stockage:"
    echo "  • Redis Commander: http://localhost:8081"
    echo "  • RQ Dashboard:    http://localhost:9181"
    echo "  • MinIO Console:   http://localhost:9001 (minioadmin/minioadmin)"
    echo
    log_info "Configuration terminée! 🎉"
}

# Fonction d'assistance pour les métriques
setup_app_metrics() {
    log_info "=== CONFIGURATION DES MÉTRIQUES APPLICATIVES ==="
    echo
    log_info "Pour activer les métriques dans vos services Python:"
    echo
    echo "1. Ajoutez prometheus_client à vos requirements.txt:"
    echo "   prometheus-client>=0.17.0"
    echo
    echo "2. Intégrez le middleware de métriques (voir cv-parser-service/metrics.py)"
    echo
    echo "3. Redémarrez vos services pour appliquer les changements:"
    echo "   docker-compose restart cv-parser job-parser matching-api"
    echo
    log_warning "N'oubliez pas d'ajouter l'endpoint /metrics à vos services!"
}

# Fonction principale
main() {
    echo
    log_info "🚀 Déploiement du monitoring Prometheus/Grafana"
    log_info "Session 2 : Setup environnement et outils de développement"
    echo
    
    check_prerequisites
    create_directories
    create_config_files
    start_monitoring
    
    # Attendre un moment pour que les services démarrent
    log_info "Attente du démarrage des services..."
    sleep 10
    
    check_services
    show_access_info
    setup_app_metrics
    
    echo
    log_success "✅ Session 2 terminée avec succès!"
    log_info "Le monitoring Prometheus/Grafana est maintenant opérationnel."
}

# Gestion des arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "restart")
        log_info "Redémarrage des services de monitoring..."
        docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml restart
        ;;
    "stop")
        log_info "Arrêt des services de monitoring..."
        docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml down
        ;;
    "logs")
        log_info "Logs des services de monitoring..."
        docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml logs -f
        ;;
    "status")
        log_info "État des services..."
        docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml ps
        ;;
    *)
        log_info "Usage: $0 [deploy|restart|stop|logs|status]"
        log_info "  deploy  : Déploie le monitoring (défaut)"
        log_info "  restart : Redémarre les services"
        log_info "  stop    : Arrête les services"
        log_info "  logs    : Affiche les logs"
        log_info "  status  : Affiche l'état des services"
        ;;
esac