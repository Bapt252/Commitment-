#!/bin/bash

# Session A3 - Phase 0: Baseline Profiling
# Mesures initiales de performance avant optimisation

set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASELINE_DIR="${SCRIPT_DIR}/baseline-${TIMESTAMP}"

echo -e "${CYAN}🎯 SESSION A3 - PHASE 0 : BASELINE PROFILING${NC}"
echo -e "${CYAN}⏱️  Durée : 15 minutes${NC}"
echo -e "${CYAN}🎯 Objectif : Mesures initiales avant optimisation${NC}"
echo -e "${CYAN}📊 Résultats : ${BASELINE_DIR}${NC}"
echo ""

# Créer le répertoire de baseline
mkdir -p "$BASELINE_DIR"

# Fonction pour logger avec timestamp
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
}

success() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] SUCCESS: $1${NC}"
}

# 1. PROFILING DES SERVICES
log "🔍 1. Profiling des services HTTP..."

{
    echo "=== SERVICES BASELINE PROFILING ==="
    echo "Timestamp: $(date)"
    echo ""
    
    # Services à tester
    services=(
        "http://localhost:5050/health:API-Principal"
        "http://localhost:5051/health:CV-Parser"
        "http://localhost:5055/health:Job-Parser"
        "http://localhost:5052/health:Matching-API"
        "http://localhost:5060/health:Personalization"
        "http://localhost:5057/health:User-Behavior"
    )
    
    echo "--- SERVICES AVAILABILITY ---"
    available_services=0
    total_services=${#services[@]}
    
    for service in "${services[@]}"; do
        url=$(echo "$service" | cut -d: -f1-2)
        name=$(echo "$service" | cut -d: -f3)
        
        if curl -s -f "$url" --max-time 5 >/dev/null 2>&1; then
            echo "✅ $name - Available"
            available_services=$((available_services + 1))
        else
            echo "❌ $name - Not available"
        fi
    done
    
    echo ""
    echo "Services ready: $available_services/$total_services"
    
    echo ""
    echo "--- RESPONSE TIME BASELINE ---"
    
    for service in "${services[@]}"; do
        url=$(echo "$service" | cut -d: -f1-2)
        name=$(echo "$service" | cut -d: -f3)
        
        echo "Testing $name response times:"
        
        total_time=0
        successful_requests=0
        
        for i in {1..10}; do
            response_time=$(curl -w "%{time_total}" -s -o /dev/null "$url" --max-time 10 2>/dev/null || echo "0")
            if [ "$response_time" != "0" ]; then
                echo "  Request $i: ${response_time}s"
                total_time=$(echo "$total_time + $response_time" | bc -l 2>/dev/null || echo "$total_time")
                successful_requests=$((successful_requests + 1))
            else
                echo "  Request $i: FAILED"
            fi
        done
        
        if [ "$successful_requests" -gt 0 ]; then
            avg_time=$(echo "scale=4; $total_time / $successful_requests" | bc -l 2>/dev/null || echo "N/A")
            echo "  Average: ${avg_time}s ($successful_requests/10 successful)"
        else
            echo "  Average: N/A (all requests failed)"
        fi
        echo ""
    done
    
} > "$BASELINE_DIR/services_baseline.log"

# 2. PROFILING DATABASE
log "🗄️ 2. Profiling PostgreSQL..."

{
    echo "=== DATABASE BASELINE PROFILING ==="
    echo "Timestamp: $(date)"
    echo ""
    
    if docker exec nexten-postgres psql -U postgres -d nexten -c "SELECT 1;" >/dev/null 2>&1; then
        echo "✅ PostgreSQL connection successful"
        echo ""
        
        echo "--- DATABASE SIZE ---"
        docker exec nexten-postgres psql -U postgres -d nexten -c "
        SELECT 
            pg_size_pretty(pg_database_size('nexten')) as database_size;
        " 2>/dev/null || echo "Size query failed"
        
        echo ""
        echo "--- CACHE STATISTICS ---"
        docker exec nexten-postgres psql -U postgres -d nexten -c "
        SELECT 
            datname,
            blks_read,
            blks_hit,
            round((blks_hit::float/(blks_hit+blks_read+1))*100, 2) as cache_hit_ratio_pct
        FROM pg_stat_database 
        WHERE datname = 'nexten';
        " 2>/dev/null || echo "Cache stats not available"
        
        echo ""
        echo "--- CONNECTION STATISTICS ---"
        docker exec nexten-postgres psql -U postgres -d nexten -c "
        SELECT 
            numbackends as active_connections,
            xact_commit,
            xact_rollback,
            conflicts,
            temp_files,
            temp_bytes
        FROM pg_stat_database 
        WHERE datname = 'nexten';
        " 2>/dev/null || echo "Connection stats not available"
        
        echo ""
        echo "--- TABLE STATISTICS ---"
        docker exec nexten-postgres psql -U postgres -d nexten -c "
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples
        FROM pg_stat_user_tables 
        ORDER BY n_live_tup DESC 
        LIMIT 10;
        " 2>/dev/null || echo "Table stats not available"
        
    else
        echo "❌ Cannot connect to PostgreSQL"
    fi
    
} > "$BASELINE_DIR/database_baseline.log"

# 3. PROFILING REDIS
log "🚀 3. Profiling Redis..."

{
    echo "=== REDIS BASELINE PROFILING ==="
    echo "Timestamp: $(date)"
    echo ""
    
    if docker exec nexten-redis redis-cli ping >/dev/null 2>&1; then
        echo "✅ Redis connection successful"
        echo ""
        
        echo "--- REDIS INFO ---"
        docker exec nexten-redis redis-cli INFO server | head -10
        
        echo ""
        echo "--- MEMORY USAGE ---"
        docker exec nexten-redis redis-cli INFO memory | grep -E "(used_memory_human|used_memory_peak_human|maxmemory_human)"
        
        echo ""
        echo "--- KEYSPACE STATISTICS ---"
        docker exec nexten-redis redis-cli INFO keyspace
        
        echo ""
        echo "--- HIT/MISS STATISTICS ---"
        docker exec nexten-redis redis-cli INFO stats | grep -E "(keyspace_hits|keyspace_misses)"
        
        # Calculer le hit rate actuel
        hits=$(docker exec nexten-redis redis-cli INFO stats | grep keyspace_hits | cut -d: -f2 | tr -d '\r')
        misses=$(docker exec nexten-redis redis-cli INFO stats | grep keyspace_misses | cut -d: -f2 | tr -d '\r')
        
        if [ -n "$hits" ] && [ -n "$misses" ] && [ "$hits" -gt 0 ] && [ "$misses" -gt 0 ]; then
            total=$((hits + misses))
            hit_rate=$(echo "scale=2; $hits * 100 / $total" | bc -l 2>/dev/null || echo "0")
            echo ""
            echo "--- CALCULATED HIT RATE ---"
            echo "Current Hit Rate: ${hit_rate}%"
            echo "Hits: $hits"
            echo "Misses: $misses"
            echo "Total: $total"
        else
            echo ""
            echo "--- HIT RATE ---"
            echo "Insufficient data for hit rate calculation"
            echo "Hits: ${hits:-0}"
            echo "Misses: ${misses:-0}"
        fi
        
        echo ""
        echo "--- CLIENT CONNECTIONS ---"
        docker exec nexten-redis redis-cli INFO clients
        
    else
        echo "❌ Cannot connect to Redis"
    fi
    
} > "$BASELINE_DIR/redis_baseline.log"

# 4. PROFILING CONTAINERS
log "🐳 4. Profiling Docker containers..."

{
    echo "=== DOCKER CONTAINERS BASELINE ==="
    echo "Timestamp: $(date)"
    echo ""
    
    echo "--- RUNNING CONTAINERS ---"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(nexten|commitment)" || echo "No relevant containers found"
    
    echo ""
    echo "--- CONTAINER RESOURCE USAGE ---"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" | head -10
    
    echo ""
    echo "--- DOCKER IMAGES SIZE ---"
    echo "All images:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | head -15
    
    echo ""
    echo "Commitment-related images:"
    docker images | grep -E "(nexten|commitment)" || echo "No commitment-specific images found"
    
    echo ""
    echo "--- DOCKER SYSTEM INFO ---"
    docker system df
    
} > "$BASELINE_DIR/docker_baseline.log"

# 5. SYSTÈME & RESSOURCES
log "⚡ 5. Profiling système et ressources..."

{
    echo "=== SYSTEM RESOURCES BASELINE ==="
    echo "Timestamp: $(date)"
    echo ""
    
    echo "--- SYSTEM INFO ---"
    echo "OS: $(uname -s)"
    echo "Kernel: $(uname -r)"
    echo "Architecture: $(uname -m)"
    
    echo ""
    echo "--- CPU INFO ---"
    if command -v nproc >/dev/null 2>&1; then
        echo "CPU Cores: $(nproc)"
    fi
    
    if [ -f /proc/loadavg ]; then
        echo "Load Average: $(cat /proc/loadavg)"
    fi
    
    echo ""
    echo "--- MEMORY INFO ---"
    if command -v free >/dev/null 2>&1; then
        free -h
    elif [ -f /proc/meminfo ]; then
        grep -E "(MemTotal|MemAvailable|MemFree)" /proc/meminfo
    fi
    
    echo ""
    echo "--- DISK USAGE ---"
    df -h | head -10
    
    echo ""
    echo "--- NETWORK INTERFACES ---"
    if command -v ip >/dev/null 2>&1; then
        ip addr show | grep -E "(inet|UP)"
    elif command -v ifconfig >/dev/null 2>&1; then
        ifconfig | grep -E "(inet|UP)"
    fi
    
} > "$BASELINE_DIR/system_baseline.log"

# 6. RAPPORT DE BASELINE
log "📊 6. Génération du rapport de baseline..."

{
    echo "# SESSION A3 - BASELINE PROFILING REPORT"
    echo "======================================="
    echo ""
    echo "**Generated:** $(date)"
    echo "**Purpose:** Initial performance measurements before Session A3 optimizations"
    echo "**Philosophy:** \"Measure first, optimize second, validate always\""
    echo ""
    
    echo "## 📊 BASELINE MEASUREMENTS SUMMARY"
    echo ""
    
    # Services summary
    if [ -f "$BASELINE_DIR/services_baseline.log" ]; then
        available=$(grep "Services ready:" "$BASELINE_DIR/services_baseline.log" | cut -d: -f2 | tr -d ' ')
        echo "### Services Availability: $available"
        echo ""
    fi
    
    # Database summary
    if [ -f "$BASELINE_DIR/database_baseline.log" ]; then
        echo "### Database Status"
        if grep -q "✅ PostgreSQL connection successful" "$BASELINE_DIR/database_baseline.log"; then
            echo "- ✅ PostgreSQL: Connected and accessible"
            
            # Cache hit ratio
            cache_hit=$(grep "cache_hit_ratio_pct" "$BASELINE_DIR/database_baseline.log" | grep -o '[0-9.]*' | head -1)
            if [ -n "$cache_hit" ]; then
                echo "- Cache Hit Ratio: ${cache_hit}%"
            fi
        else
            echo "- ❌ PostgreSQL: Not accessible"
        fi
        echo ""
    fi
    
    # Redis summary
    if [ -f "$BASELINE_DIR/redis_baseline.log" ]; then
        echo "### Redis Status"
        if grep -q "✅ Redis connection successful" "$BASELINE_DIR/redis_baseline.log"; then
            echo "- ✅ Redis: Connected and accessible"
            
            # Hit rate
            hit_rate=$(grep "Current Hit Rate:" "$BASELINE_DIR/redis_baseline.log" | grep -o '[0-9.]*' | head -1)
            if [ -n "$hit_rate" ]; then
                echo "- Hit Rate: ${hit_rate}%"
            fi
        else
            echo "- ❌ Redis: Not accessible"
        fi
        echo ""
    fi
    
    echo "## 🎯 SESSION A3 OPTIMIZATION TARGETS"
    echo ""
    echo "Based on baseline measurements, Session A3 will target:"
    echo "- **Database:** -40% query time, +30% throughput, >90% cache hit ratio"
    echo "- **Redis:** +50% hit rate, -30% memory usage"
    echo "- **Containers:** -30% image size, -20% runtime resources"
    echo "- **Services:** -25% response time, improved async patterns"
    echo ""
    
    echo "## 📁 BASELINE DATA LOCATION"
    echo ""
    echo "All baseline measurements are stored in:"
    echo "- \`services_baseline.log\` - HTTP services performance"
    echo "- \`database_baseline.log\` - PostgreSQL metrics"
    echo "- \`redis_baseline.log\` - Redis cache performance"
    echo "- \`docker_baseline.log\` - Container resource usage"
    echo "- \`system_baseline.log\` - System resources"
    echo ""
    echo "---"
    echo "**Baseline profiling completed at $(date)**"
    echo "*Ready to proceed with Session A3 optimization phases*"
    
} > "$BASELINE_DIR/baseline_report.md"

success "✅ Baseline profiling completed!"
success "📋 Baseline report: $BASELINE_DIR/baseline_report.md"
success "📊 All baseline measurements captured"
success "🎯 Ready for Session A3 optimization phases"
success "📁 Data location: ${BASELINE_DIR}/"

echo ""
echo -e "${CYAN}🎉 SESSION A3 PHASE 0 COMPLETED!${NC}"
echo -e "${CYAN}⏱️  Baseline profiling finished${NC}"
echo -e "${CYAN}📊 Performance measurements captured${NC}"
echo -e "${CYAN}🚀 Ready to proceed with optimizations${NC}"
echo ""
echo -e "${GREEN}Next step: Run database optimization${NC}"
echo -e "${GREEN}Command: ./database-optimization.sh${NC}"
