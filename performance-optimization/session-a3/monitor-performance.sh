#!/bin/bash

# Session A3 - Monitoring de performance continu post-optimisation
# Surveillance des métriques de performance en temps réel

set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
REFRESH_INTERVAL=10
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITORING_LOG="${SCRIPT_DIR}/monitoring-$(date +"%Y%m%d_%H%M%S").log"

# Fonction pour afficher l'aide
show_help() {
    echo -e "${CYAN}📊 SESSION A3 - MONITORING PERFORMANCE${NC}"
    echo -e "${CYAN}======================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage: $0 [options]${NC}"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  ${GREEN}-i, --interval SECONDS${NC}    Intervalle de rafraîchissement (défaut: 10s)"
    echo -e "  ${GREEN}-l, --log FILE${NC}           Fichier de log (défaut: auto-généré)"
    echo -e "  ${GREEN}-s, --static${NC}             Mode statique (une seule mesure)"
    echo -e "  ${GREEN}-h, --help${NC}               Afficher cette aide"
    echo ""
    echo -e "${CYAN}Contrôles:${NC}"
    echo -e "  ${YELLOW}Ctrl+C${NC}                   Arrêter le monitoring"
    echo -e "  ${YELLOW}q + Entrée${NC}               Quitter proprement"
    echo ""
    echo -e "${BLUE}Monitore:${NC}"
    echo -e "  • État des services HTTP"
    echo -e "  • Performance Redis (hit rate, mémoire)"
    echo -e "  • Métriques PostgreSQL (cache, connexions)"
    echo -e "  • Ressources containers Docker"
    echo -e "  • Métriques système"
}

# Parser les arguments
STATIC_MODE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--interval)
            REFRESH_INTERVAL="$2"
            shift 2
            ;;
        -l|--log)
            MONITORING_LOG="$2"
            shift 2
            ;;
        -s|--static)
            STATIC_MODE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Option inconnue: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Fonction pour logger les métriques
log_metrics() {
    echo "[$(date)] $1" >> "$MONITORING_LOG"
}

# Fonction pour nettoyer à la sortie
cleanup() {
    echo ""
    echo -e "${CYAN}📊 Monitoring arrêté${NC}"
    echo -e "${CYAN}📝 Log sauvegardé: $MONITORING_LOG${NC}"
    exit 0
}

# Capturer Ctrl+C
trap cleanup SIGINT

# Fonction pour vérifier les services HTTP
check_http_services() {
    local services_data=""
    local services_up=0
    local total_services=0
    
    services=(
        "http://localhost:5050/health:API-Principal"
        "http://localhost:5051/health:CV-Parser"
        "http://localhost:5055/health:Job-Parser"
        "http://localhost:5052/health:Matching-API"
        "http://localhost:5060/health:Personalization"
        "http://localhost:5057/health:User-Behavior"
    )
    
    for service in "${services[@]}"; do
        url=$(echo "$service" | cut -d: -f1-2)
        name=$(echo "$service" | cut -d: -f3)
        total_services=$((total_services + 1))
        
        # Mesurer le temps de réponse
        response_time=$(curl -w "%{time_total}" -s -o /dev/null "$url" --max-time 5 2>/dev/null || echo "timeout")
        
        if [[ "$response_time" != "timeout" ]] && [[ "$response_time" != "0.000000" ]]; then
            services_data="${services_data}  ✅ ${name} (${response_time}s)\n"
            services_up=$((services_up + 1))
        else
            services_data="${services_data}  ❌ ${name} (timeout/error)\n"
        fi
    done
    
    echo -e "${services_data}"
    echo -e "${BLUE}Services: ${services_up}/${total_services} actifs${NC}"
    
    log_metrics "HTTP_SERVICES: $services_up/$total_services active"
}

# Fonction pour vérifier Redis
check_redis() {
    if docker exec nexten-redis redis-cli ping >/dev/null 2>&1; then
        echo -e "  ✅ ${GREEN}Redis: Connecté${NC}"
        
        # Hit rate
        hits=$(docker exec nexten-redis redis-cli INFO stats 2>/dev/null | grep keyspace_hits | cut -d: -f2 | tr -d '\r' || echo "0")
        misses=$(docker exec nexten-redis redis-cli INFO stats 2>/dev/null | grep keyspace_misses | cut -d: -f2 | tr -d '\r' || echo "0")
        
        if [ -n "$hits" ] && [ -n "$misses" ] && [ "$hits" -gt 0 ]; then
            total=$((hits + misses))
            hit_rate=$(echo "scale=2; $hits * 100 / $total" | bc -l 2>/dev/null || echo "0")
            
            if (( $(echo "$hit_rate >= 80" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "     Hit Rate: ${GREEN}${hit_rate}%${NC} 🚀"
            elif (( $(echo "$hit_rate >= 60" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "     Hit Rate: ${YELLOW}${hit_rate}%${NC}"
            else
                echo -e "     Hit Rate: ${RED}${hit_rate}%${NC}"
            fi
            
            log_metrics "REDIS_HIT_RATE: $hit_rate%"
        else
            echo -e "     Hit Rate: ${YELLOW}Données insuffisantes${NC}"
        fi
        
        # Mémoire utilisée
        memory=$(docker exec nexten-redis redis-cli INFO memory 2>/dev/null | grep used_memory_human | cut -d: -f2 | tr -d '\r' || echo "N/A")
        echo -e "     Mémoire: ${memory}"
        
        # Nombre de clés
        keys_total=0
        for db in {0..15}; do
            keys_count=$(docker exec nexten-redis redis-cli -n $db DBSIZE 2>/dev/null || echo "0")
            keys_total=$((keys_total + keys_count))
        done
        echo -e "     Clés: ${keys_total}"
        
        log_metrics "REDIS_MEMORY: $memory, KEYS: $keys_total"
    else
        echo -e "  ❌ ${RED}Redis: Non accessible${NC}"
        log_metrics "REDIS: DISCONNECTED"
    fi
}

# Fonction pour vérifier PostgreSQL
check_postgresql() {
    if docker exec nexten-postgres psql -U postgres -d nexten -c "SELECT 1;" >/dev/null 2>&1; then
        echo -e "  ✅ ${GREEN}PostgreSQL: Connecté${NC}"
        
        # Cache hit ratio
        cache_hit=$(docker exec nexten-postgres psql -U postgres -d nexten -t -c "
        SELECT round((blks_hit::float/(blks_hit+blks_read+1))*100, 2) 
        FROM pg_stat_database 
        WHERE datname = 'nexten';
        " 2>/dev/null | tr -d ' ' || echo "0")
        
        if [ -n "$cache_hit" ] && [ "$cache_hit" != "0" ]; then
            if (( $(echo "$cache_hit >= 90" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "     Cache Hit: ${GREEN}${cache_hit}%${NC} 🚀"
            elif (( $(echo "$cache_hit >= 80" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "     Cache Hit: ${YELLOW}${cache_hit}%${NC}"
            else
                echo -e "     Cache Hit: ${RED}${cache_hit}%${NC}"
            fi
        else
            echo -e "     Cache Hit: ${YELLOW}N/A${NC}"
        fi
        
        # Connexions actives
        connections=$(docker exec nexten-postgres psql -U postgres -d nexten -t -c "
        SELECT count(*) FROM pg_stat_activity WHERE state = 'active';
        " 2>/dev/null | tr -d ' ' || echo "0")
        echo -e "     Connexions: ${connections}"
        
        log_metrics "POSTGRESQL_CACHE_HIT: $cache_hit%, CONNECTIONS: $connections"
    else
        echo -e "  ❌ ${RED}PostgreSQL: Non accessible${NC}"
        log_metrics "POSTGRESQL: DISCONNECTED"
    fi
}

# Fonction pour vérifier Docker
check_docker() {
    echo -e "${BLUE}🐳 Containers (Top 5):${NC}"
    
    # Stats des containers
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null | grep -E "(nexten|commitment)" | head -5 | while read line; do
        echo -e "  ${line}"
    done
    
    # Espace disque Docker
    docker_size=$(docker system df --format "{{.Size}}" 2>/dev/null | head -1 || echo "N/A")
    echo -e "  💾 Espace Docker: ${docker_size}"
    
    log_metrics "DOCKER_SIZE: $docker_size"
}

# Fonction pour vérifier le système
check_system() {
    echo -e "${BLUE}⚡ Système:${NC}"
    
    # Load average si disponible
    if [ -f /proc/loadavg ]; then
        load=$(cat /proc/loadavg | cut -d' ' -f1-3)
        echo -e "  📊 Load: ${load}"
    fi
    
    # Mémoire si disponible
    if command -v free >/dev/null 2>&1; then
        mem_usage=$(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')
        echo -e "  🧠 RAM: ${mem_usage}"
    fi
    
    # Espace disque
    disk_usage=$(df -h . | tail -1 | awk '{print $5}' 2>/dev/null || echo "N/A")
    echo -e "  💾 Disque: ${disk_usage}"
    
    log_metrics "SYSTEM: Load=$load, RAM=$mem_usage, Disk=$disk_usage"
}

# Fonction principale d'affichage
display_dashboard() {
    if [ "$STATIC_MODE" = false ]; then
        clear
    fi
    
    echo -e "${PURPLE}🎯 SESSION A3 - MONITORING PERFORMANCE${NC}"
    echo -e "${PURPLE}======================================${NC}"
    echo -e "${PURPLE}⏱️  Dernière mise à jour: $(date)${NC}"
    if [ "$STATIC_MODE" = false ]; then
        echo -e "${PURPLE}🔄 Rafraîchissement: ${REFRESH_INTERVAL}s (Ctrl+C pour arrêter)${NC}"
    fi
    echo ""
    
    # Services HTTP
    echo -e "${BLUE}🌐 Services HTTP:${NC}"
    check_http_services
    echo ""
    
    # Base de données
    echo -e "${BLUE}🗄️  Bases de données:${NC}"
    check_redis
    check_postgresql
    echo ""
    
    # Docker et système
    check_docker
    echo ""
    check_system
    
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ "$STATIC_MODE" = false ]; then
        echo -e "${YELLOW}💡 Tapez 'q' puis Entrée pour quitter, ou Ctrl+C${NC}"
    else
        echo -e "${GREEN}📊 Mesure statique terminée${NC}"
    fi
}

# Initialiser le log
{
    echo "# SESSION A3 - PERFORMANCE MONITORING LOG"
    echo "=========================================="
    echo "Started: $(date)"
    echo "Refresh interval: ${REFRESH_INTERVAL}s"
    echo "Static mode: $STATIC_MODE"
    echo ""
} > "$MONITORING_LOG"

echo -e "${CYAN}📊 SESSION A3 - MONITORING DÉMARRÉ${NC}"
echo -e "${CYAN}Log file: $MONITORING_LOG${NC}"
echo ""

if [ "$STATIC_MODE" = true ]; then
    # Mode statique - une seule mesure
    display_dashboard
    echo -e "${GREEN}✅ Mesure statique terminée${NC}"
    echo -e "${CYAN}📝 Résultats sauvegardés dans: $MONITORING_LOG${NC}"
else
    # Mode continu
    echo -e "${YELLOW}Démarrage du monitoring continu...${NC}"
    sleep 2
    
    # Boucle principale de monitoring
    while true; do
        display_dashboard
        
        # Attendre l'intervalle ou une entrée utilisateur
        read -t "$REFRESH_INTERVAL" user_input 2>/dev/null || true
        
        # Vérifier si l'utilisateur veut quitter
        if [[ "$user_input" = "q" ]] || [[ "$user_input" = "quit" ]]; then
            cleanup
        fi
    done
fi
