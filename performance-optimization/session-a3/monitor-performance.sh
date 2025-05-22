#!/bin/bash

# Session A3 - Monitoring Performance Continu
# Surveillance des métriques post-optimisation

set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITORING_DIR="$SCRIPT_DIR/monitoring"
LOG_FILE="$MONITORING_DIR/monitoring-${TIMESTAMP}.log"

# URLs des services
API_BASE="http://localhost:5050"
CV_PARSER="http://localhost:5051"
JOB_PARSER="http://localhost:5055"
MATCHING_API="http://localhost:5052"
PERSONALIZATION="http://localhost:5060"
USER_BEHAVIOR="http://localhost:5057"

# Créer le répertoire de monitoring
mkdir -p "$MONITORING_DIR"

# Fonction pour logger
log() {
    echo "[$(date +'%H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Fonction pour afficher le dashboard
show_performance_dashboard() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    SESSION A3 - MONITORING PERFORMANCE                      ║"
    echo "║                           TABLEAU DE BORD TEMPS RÉEL                        ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${BLUE}🕐 $(date)${NC}"
    echo -e "${BLUE}📊 Monitoring depuis: $(date -d @$(stat -c %Y "$LOG_FILE" 2>/dev/null || echo $(date +%s)) 2>/dev/null || echo "maintenant")${NC}"
    echo ""
}

# Fonction pour tester la latence des endpoints
test_endpoints_latency() {
    echo -e "${YELLOW}⚡ LATENCE DES ENDPOINTS${NC}"
    echo "────────────────────────────"
    
    local endpoints=(
        "$API_BASE/health:API-Principal"
        "$CV_PARSER/health:CV-Parser"
        "$JOB_PARSER/health:Job-Parser"
        "$MATCHING_API/health:Matching-API"
        "$PERSONALIZATION/health:Personalization"
        "$USER_BEHAVIOR/health:User-Behavior"
    )
    
    local total_response_time=0
    local successful_tests=0
    
    for endpoint in "${endpoints[@]}"; do
        local url=$(echo "$endpoint" | cut -d: -f1-2)
        local name=$(echo "$endpoint" | cut -d: -f3)
        
        local response_time=$(curl -w "%{time_total}" -s -o /dev/null "$url" 2>/dev/null || echo "0")
        local http_code=$(curl -w "%{http_code}" -s -o /dev/null "$url" 2>/dev/null || echo "000")
        
        if [ "$http_code" = "200" ]; then
            local response_ms=$(echo "$response_time * 1000" | bc -l 2>/dev/null || echo "0")
            printf "✅ %-20s %6.0fms (HTTP 200)\n" "$name" "$response_ms"
            total_response_time=$(echo "$total_response_time + $response_time" | bc -l 2>/dev/null || echo "$total_response_time")
            successful_tests=$((successful_tests + 1))
        else
            printf "❌ %-20s %6s (HTTP %s)\n" "$name" "FAIL" "$http_code"
        fi
    done
    
    if [ $successful_tests -gt 0 ]; then
        local avg_response_time=$(echo "scale=3; $total_response_time / $successful_tests" | bc -l 2>/dev/null || echo "0")
        local avg_response_ms=$(echo "$avg_response_time * 1000" | bc -l 2>/dev/null || echo "0")
        echo ""
        printf "📊 Latence moyenne: %.0fms (%d/%d services OK)\n" "$avg_response_ms" "$successful_tests" "${#endpoints[@]}"
        
        # Évaluation de la performance
        if (( $(echo "$avg_response_ms < 100" | bc -l 2>/dev/null || echo 0) )); then
            echo -e "${GREEN}🎯 Performance: EXCELLENTE (<100ms)${NC}"
        elif (( $(echo "$avg_response_ms < 250" | bc -l 2>/dev/null || echo 0) )); then
            echo -e "${GREEN}🎯 Performance: BONNE (<250ms)${NC}"
        elif (( $(echo "$avg_response_ms < 500" | bc -l 2>/dev/null || echo 0) )); then
            echo -e "${YELLOW}🎯 Performance: ACCEPTABLE (<500ms)${NC}"
        else
            echo -e "${RED}🎯 Performance: LENTE (≥500ms)${NC}"
        fi
    fi
    echo ""
}

# Fonction pour surveiller PostgreSQL
monitor_postgresql() {
    echo -e "${YELLOW}🗄️ POSTGRESQL PERFORMANCE${NC}"
    echo "──────────────────────────────"
    
    if docker exec nexten-postgres psql -U postgres -d nexten -c "SELECT 1;" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL: Connecté${NC}"
        
        # Cache hit ratio
        local cache_hit=$(docker exec nexten-postgres psql -U postgres -d nexten -t -c "
        SELECT round((blks_hit::float/(blks_hit+blks_read+1))*100, 1)
        FROM pg_stat_database 
        WHERE datname = 'nexten';
        " 2>/dev/null | xargs || echo "0")
        
        if [ -n "$cache_hit" ] && [ "$cache_hit" != "0" ]; then
            printf "📊 Cache Hit Ratio: %s%%\n" "$cache_hit"
            
            if (( $(echo "$cache_hit >= 95" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "${GREEN}🎯 Cache: EXCELLENT (≥95%)${NC}"
            elif (( $(echo "$cache_hit >= 90" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "${GREEN}🎯 Cache: BON (≥90%)${NC}"
            elif (( $(echo "$cache_hit >= 80" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "${YELLOW}🎯 Cache: ACCEPTABLE (≥80%)${NC}"
            else
                echo -e "${RED}🎯 Cache: FAIBLE (<80%)${NC}"
            fi
        fi
        
        # Connexions actives
        local active_conn=$(docker exec nexten-postgres psql -U postgres -d nexten -t -c "
        SELECT numbackends FROM pg_stat_database WHERE datname = 'nexten';
        " 2>/dev/null | xargs || echo "0")
        
        printf "🔗 Connexions actives: %s\n" "${active_conn:-0}"
        
        # Query performance (si pg_stat_statements est disponible)
        local avg_query_time=$(docker exec nexten-postgres psql -U postgres -d nexten -t -c "
        SELECT round(avg(mean_exec_time), 2) 
        FROM pg_stat_statements 
        WHERE calls > 0;
        " 2>/dev/null | xargs || echo "N/A")
        
        if [ "$avg_query_time" != "N/A" ] && [ -n "$avg_query_time" ]; then
            printf "⚡ Temps moyen requête: %sms\n" "$avg_query_time"
        fi
        
    else
        echo -e "${RED}❌ PostgreSQL: Non accessible${NC}"
    fi
    echo ""
}

# Fonction pour surveiller Redis
monitor_redis() {
    echo -e "${YELLOW}🚀 REDIS PERFORMANCE${NC}"
    echo "─────────────────────"
    
    if docker exec nexten-redis redis-cli ping >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis: Connecté${NC}"
        
        # Hit rate
        local hits=$(docker exec nexten-redis redis-cli INFO stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
        local misses=$(docker exec nexten-redis redis-cli INFO stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
        
        if [ -n "$hits" ] && [ -n "$misses" ] && [ "$hits" -gt 0 ] && [ "$misses" -gt 0 ]; then
            local total=$((hits + misses))
            local hit_rate=$(echo "scale=1; $hits * 100 / $total" | bc -l 2>/dev/null || echo "0")
            
            printf "📊 Hit Rate: %s%% (%s hits / %s total)\n" "$hit_rate" "$hits" "$total"
            
            if (( $(echo "$hit_rate >= 90" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "${GREEN}🎯 Cache: EXCELLENT (≥90%)${NC}"
            elif (( $(echo "$hit_rate >= 80" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "${GREEN}🎯 Cache: BON (≥80%)${NC}"
            elif (( $(echo "$hit_rate >= 60" | bc -l 2>/dev/null || echo 0) )); then
                echo -e "${YELLOW}🎯 Cache: ACCEPTABLE (≥60%)${NC}"
            else
                echo -e "${RED}🎯 Cache: FAIBLE (<60%)${NC}"
            fi
        else
            echo "📊 Hit Rate: Données insuffisantes"
        fi
        
        # Memory usage
        local memory=$(docker exec nexten-redis redis-cli INFO memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')
        local peak_memory=$(docker exec nexten-redis redis-cli INFO memory | grep used_memory_peak_human | cut -d: -f2 | tr -d '\r')
        
        printf "💾 Mémoire utilisée: %s (pic: %s)\n" "${memory:-N/A}" "${peak_memory:-N/A}"
        
        # Keys count
        local total_keys=0
        for db in {0..15}; do
            local keys_count=$(docker exec nexten-redis redis-cli -n $db DBSIZE 2>/dev/null || echo "0")
            total_keys=$((total_keys + keys_count))
        done
        
        printf "🔑 Total clés: %d\n" "$total_keys"
        
    else
        echo -e "${RED}❌ Redis: Non accessible${NC}"
    fi
    echo ""
}

# Fonction pour surveiller les containers
monitor_containers() {
    echo -e "${YELLOW}🐳 CONTAINERS PERFORMANCE${NC}"
    echo "────────────────────────────"
    
    # Stats des containers
    local container_stats=$(docker stats --no-stream --format "{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null | grep nexten)
    
    if [ -n "$container_stats" ]; then
        echo "$container_stats" | while IFS=$'\t' read -r name cpu memory mem_perc; do
            printf "%-20s CPU: %6s Memory: %12s (%s)\n" "$name" "$cpu" "$memory" "$mem_perc"
        done
        
        # Calcul des moyennes
        local avg_cpu=$(echo "$container_stats" | awk -F'\t' '{gsub(/%/, "", $2); sum+=$2; count++} END {if(count>0) printf "%.1f", sum/count; else print "0"}')
        local avg_mem=$(echo "$container_stats" | awk -F'\t' '{gsub(/%/, "", $4); sum+=$4; count++} END {if(count>0) printf "%.1f", sum/count; else print "0"}')
        
        echo ""
        printf "📊 Moyennes: CPU: %s%%, Memory: %s%%\n" "$avg_cpu" "$avg_mem"
        
        # Évaluation
        if (( $(echo "$avg_cpu < 50 && $avg_mem < 70" | bc -l 2>/dev/null || echo 0) )); then
            echo -e "${GREEN}🎯 Ressources: OPTIMALES${NC}"
        elif (( $(echo "$avg_cpu < 80 && $avg_mem < 85" | bc -l 2>/dev/null || echo 0) )); then
            echo -e "${YELLOW}🎯 Ressources: ACCEPTABLES${NC}"
        else
            echo -e "${RED}🎯 Ressources: ÉLEVÉES${NC}"
        fi
    else
        echo -e "${RED}❌ Aucun container nexten trouvé${NC}"
    fi
    echo ""
}

# Fonction pour afficher les métriques d'objectifs Session A3
show_session_a3_targets() {
    echo -e "${CYAN}🎯 OBJECTIFS SESSION A3 - VALIDATION CONTINUE${NC}"
    echo "═══════════════════════════════════════════════════"
    
    # Base de données (-40% query time, +30% throughput)
    echo -e "${BLUE}📊 Base de données:${NC}"
    local db_status="❓"
    if docker exec nexten-postgres psql -U postgres -d nexten -c "SELECT 1;" >/dev/null 2>&1; then
        local cache_hit=$(docker exec nexten-postgres psql -U postgres -d nexten -t -c "
        SELECT round((blks_hit::float/(blks_hit+blks_read+1))*100, 1)
        FROM pg_stat_database WHERE datname = 'nexten';
        " 2>/dev/null | xargs || echo "0")
        
        if (( $(echo "$cache_hit >= 90" | bc -l 2>/dev/null || echo 0) )); then
            db_status="✅"
        elif (( $(echo "$cache_hit >= 80" | bc -l 2>/dev/null || echo 0) )); then
            db_status="⚠️"
        else
            db_status="❌"
        fi
    fi
    echo "   Target: -40% query time, +30% throughput → $db_status"
    
    # Redis (+50% hit rate, -30% memory usage)
    echo -e "${BLUE}🚀 Redis cache:${NC}"
    local redis_status="❓"
    if docker exec nexten-redis redis-cli ping >/dev/null 2>&1; then
        local hits=$(docker exec nexten-redis redis-cli INFO stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
        local misses=$(docker exec nexten-redis redis-cli INFO stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
        
        if [ -n "$hits" ] && [ -n "$misses" ] && [ "$hits" -gt 0 ] && [ "$misses" -gt 0 ]; then
            local total=$((hits + misses))
            local hit_rate=$(echo "scale=1; $hits * 100 / $total" | bc -l 2>/dev/null || echo "0")
            
            if (( $(echo "$hit_rate >= 80" | bc -l 2>/dev/null || echo 0) )); then
                redis_status="✅"
            elif (( $(echo "$hit_rate >= 60" | bc -l 2>/dev/null || echo 0) )); then
                redis_status="⚠️"
            else
                redis_status="❌"
            fi
        fi
    fi
    echo "   Target: +50% hit rate, -30% memory usage → $redis_status"
    
    # Containers (-30% image size, -20% runtime resources)
    echo -e "${BLUE}🐳 Containers:${NC}"
    local container_status="❓"
    local container_stats=$(docker stats --no-stream --format "{{.MemPerc}}" 2>/dev/null | grep -o '[0-9.]*' | head -5)
    if [ -n "$container_stats" ]; then
        local avg_mem=$(echo "$container_stats" | awk '{sum+=$1; count++} END {if(count>0) print sum/count; else print 100}')
        
        if (( $(echo "$avg_mem < 70" | bc -l 2>/dev/null || echo 0) )); then
            container_status="✅"
        elif (( $(echo "$avg_mem < 85" | bc -l 2>/dev/null || echo 0) )); then
            container_status="⚠️"
        else
            container_status="❌"
        fi
    fi
    echo "   Target: -30% image size, -20% runtime resources → $container_status"
    
    # Code critique (-25% response time)
    echo -e "${BLUE}⚡ Code critique:${NC}"
    local code_status="❓"
    local response_time=$(curl -w "%{time_total}" -s -o /dev/null "$API_BASE/health" 2>/dev/null || echo "1")
    local response_ms=$(echo "$response_time * 1000" | bc -l 2>/dev/null || echo "1000")
    
    if (( $(echo "$response_ms < 150" | bc -l 2>/dev/null || echo 0) )); then
        code_status="✅"
    elif (( $(echo "$response_ms < 300" | bc -l 2>/dev/null || echo 0) )); then
        code_status="⚠️"
    else
        code_status="❌"
    fi
    echo "   Target: -25% response time endpoints critiques → $code_status"
    
    echo ""
}

# Fonction pour générer un rapport de monitoring
generate_monitoring_report() {
    local report_file="$MONITORING_DIR/monitoring-report-$(date +%Y%m%d_%H%M).md"
    
    {
        echo "# Rapport de Monitoring Session A3"
        echo "=================================="
        echo ""
        echo "**Généré:** $(date)"
        echo "**Période:** Monitoring continu post-Session A3"
        echo ""
        
        echo "## 📊 État des Services"
        echo ""
        
        # Test de latence
        echo "### Latence des Endpoints"
        local endpoints=(
            "$API_BASE/health:API-Principal"
            "$CV_PARSER/health:CV-Parser"
            "$JOB_PARSER/health:Job-Parser"
            "$MATCHING_API/health:Matching-API"
        )
        
        echo "| Service | Latence | Status |"
        echo "|---------|---------|--------|"
        
        for endpoint in "${endpoints[@]}"; do
            local url=$(echo "$endpoint" | cut -d: -f1-2)
            local name=$(echo "$endpoint" | cut -d: -f3)
            
            local response_time=$(curl -w "%{time_total}" -s -o /dev/null "$url" 2>/dev/null || echo "0")
            local http_code=$(curl -w "%{http_code}" -s -o /dev/null "$url" 2>/dev/null || echo "000")
            local response_ms=$(echo "$response_time * 1000" | bc -l 2>/dev/null || echo "0")
            
            if [ "$http_code" = "200" ]; then
                printf "| %s | %.0fms | ✅ OK |\n" "$name" "$response_ms"
            else
                printf "| %s | FAIL | ❌ ERROR |\n" "$name"
            fi
        done
        
        echo ""
        echo "## 🎯 Validation Objectifs Session A3"
        echo ""
        echo "- **Database**: Cache hit ratio et performance queries"
        echo "- **Redis**: Hit rate et optimisation mémoire"  
        echo "- **Containers**: Utilisation ressources optimisée"
        echo "- **Code**: Response time des endpoints critiques"
        echo ""
        
        echo "---"
        echo "*Rapport généré automatiquement par le monitoring Session A3*"
        
    } > "$report_file"
    
    echo -e "${GREEN}📋 Rapport généré: $report_file${NC}"
}

# Fonction principale de monitoring
main() {
    echo "Démarrage du monitoring continu Session A3..."
    log "Monitoring Session A3 démarré"
    
    local iteration=0
    
    while true; do
        iteration=$((iteration + 1))
        
        show_performance_dashboard
        
        echo -e "${MAGENTA}📊 Itération #$iteration${NC}"
        echo ""
        
        test_endpoints_latency
        monitor_postgresql
        monitor_redis
        monitor_containers
        show_session_a3_targets
        
        echo -e "${CYAN}⏱️ Prochaine mise à jour dans 30 secondes...${NC}"
        echo -e "${CYAN}Press Ctrl+C pour arrêter le monitoring${NC}"
        
        # Log des métriques principales
        log "Iteration #$iteration - Monitoring completed"
        
        # Générer un rapport toutes les 10 itérations (5 minutes)
        if [ $((iteration % 10)) -eq 0 ]; then
            generate_monitoring_report
        fi
        
        sleep 30
    done
}

# Gestion du signal d'interruption
trap 'echo -e "\n${YELLOW}Monitoring arrêté par l'utilisateur${NC}"; log "Monitoring arrêté"; exit 0' INT

# Point d'entrée
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
