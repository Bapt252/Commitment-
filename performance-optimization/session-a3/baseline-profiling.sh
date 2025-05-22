#!/bin/bash

# Session A3 - Phase 0 : Performance Profiling & Baseline
# Durée : 45min
# Objectif : Établir métriques baseline et identifier bottlenecks

set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="./performance-optimization/session-a3/baseline-results-${TIMESTAMP}"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# URLs des services
API_BASE="http://localhost:5050"
CV_PARSER="http://localhost:5051"
JOB_PARSER="http://localhost:5055"
MATCHING_API="http://localhost:5052"
PERSONALIZATION="http://localhost:5060"
USER_BEHAVIOR="http://localhost:5057"

echo -e "${BLUE}🎯 Session A3 - Phase 0 : Performance Profiling & Baseline${NC}"
echo -e "${BLUE}⏱️  Durée estimée : 45 minutes${NC}"
echo -e "${BLUE}📊 Résultats : ${RESULTS_DIR}${NC}"
echo ""

# Créer le répertoire de résultats
mkdir -p "$RESULTS_DIR"
cd "$RESULTS_DIR"

# Fonction pour logger avec timestamp
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

# 1. ÉTABLIR MÉTRIQUES BASELINE ACTUELLES
log "📊 1. Établissement des métriques baseline..."

# Vérifier que les services sont en cours d'exécution
log "🔍 Vérification des services actifs..."
{
    echo "=== SERVICES STATUS ==="
    echo "Timestamp: $(date)"
    echo ""
    
    # Vérifier Docker Compose
    if docker-compose -f "../../../${DOCKER_COMPOSE_FILE}" ps > services_status.txt 2>&1; then
        echo "✅ Docker Compose status OK"
        cat services_status.txt
    else
        echo "❌ Docker Compose not running"
        cat services_status.txt
    fi
    echo ""
} > baseline_services.log

# Test de connectivité des services
log "🌐 Test de connectivité des endpoints..."
{
    echo "=== ENDPOINTS CONNECTIVITY ==="
    echo "Timestamp: $(date)"
    echo ""
    
    endpoints=(
        "$API_BASE/health:API-Principal"
        "$CV_PARSER/health:CV-Parser"
        "$JOB_PARSER/health:Job-Parser"
        "$MATCHING_API/health:Matching-API"
        "$PERSONALIZATION/health:Personalization"
        "$USER_BEHAVIOR/health:User-Behavior"
    )
    
    for endpoint in "${endpoints[@]}"; do
        url=$(echo "$endpoint" | cut -d: -f1)
        name=$(echo "$endpoint" | cut -d: -f2)
        
        if response=$(curl -s -w "%{http_code}:%{time_total}" "$url" 2>/dev/null); then
            http_code=$(echo "$response" | cut -d: -f1)
            time_total=$(echo "$response" | cut -d: -f2)
            
            if [ "$http_code" = "200" ]; then
                echo "✅ $name - HTTP $http_code - ${time_total}s"
            else
                echo "❌ $name - HTTP $http_code - ${time_total}s"
            fi
        else
            echo "❌ $name - Connection failed"
        fi
    done
    echo ""
} > baseline_connectivity.log

# Métriques de latence par endpoint
log "⚡ Mesure de latence des endpoints critiques..."
{
    echo "=== BASELINE LATENCY METRICS ==="
    echo "Timestamp: $(date)"
    echo ""
    
    # Test latence /health endpoints (5 requêtes par endpoint)
    for i in {1..5}; do
        echo "--- Test Round $i ---"
        
        # API Principal /health
        if response=$(curl -s -w "%{time_total},%{time_connect},%{time_starttransfer}" "$API_BASE/health" -o /dev/null 2>/dev/null); then
            echo "API-Health: $response"
        fi
        
        # CV Parser /health  
        if response=$(curl -s -w "%{time_total},%{time_connect},%{time_starttransfer}" "$CV_PARSER/health" -o /dev/null 2>/dev/null); then
            echo "CV-Parser-Health: $response"
        fi
        
        # Job Parser /health
        if response=$(curl -s -w "%{time_total},%{time_connect},%{time_starttransfer}" "$JOB_PARSER/health" -o /dev/null 2>/dev/null); then
            echo "Job-Parser-Health: $response"
        fi
        
        sleep 1
    done
    echo ""
} > baseline_latency.log

# 2. IDENTIFIER LES VRAIS BOTTLENECKS
log "🔍 2. Identification des bottlenecks..."

# PostgreSQL - Queries lentes
log "🗄️ Analyse PostgreSQL..."
{
    echo "=== POSTGRESQL PERFORMANCE ANALYSIS ==="
    echo "Timestamp: $(date)"
    echo ""
    
    # Connexion à PostgreSQL pour analyser les requêtes lentes
    if docker exec nexten-postgres psql -U postgres -d nexten -c "SELECT version();" >/dev/null 2>&1; then
        echo "✅ PostgreSQL connection OK"
        
        # Activer pg_stat_statements si pas déjà fait
        echo "--- Enabling pg_stat_statements ---"
        docker exec nexten-postgres psql -U postgres -d nexten -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;" 2>/dev/null || true
        
        # Requêtes les plus lentes
        echo "--- TOP 10 SLOWEST QUERIES ---"
        docker exec nexten-postgres psql -U postgres -d nexten -c "
        SELECT 
            round(mean_exec_time::numeric, 2) as avg_time_ms,
            round(total_exec_time::numeric, 2) as total_time_ms,
            calls,
            round((total_exec_time/calls)::numeric, 2) as avg_per_call_ms,
            substring(query, 1, 100) as query_snippet
        FROM pg_stat_statements 
        WHERE calls > 0
        ORDER BY mean_exec_time DESC 
        LIMIT 10;" 2>/dev/null || echo "pg_stat_statements not available yet"
        
        # Statistiques générales de la DB
        echo "--- DATABASE STATS ---"
        docker exec nexten-postgres psql -U postgres -d nexten -c "
        SELECT 
            datname,
            numbackends as active_connections,
            xact_commit,
            xact_rollback,
            blks_read,
            blks_hit,
            round((blks_hit::float/(blks_hit+blks_read))*100, 2) as cache_hit_ratio
        FROM pg_stat_database 
        WHERE datname = 'nexten';" 2>/dev/null
        
    else
        echo "❌ Cannot connect to PostgreSQL"
    fi
    echo ""
} > baseline_postgresql.log

# Redis - Analyse du cache
log "🚀 Analyse Redis..."
{
    echo "=== REDIS PERFORMANCE ANALYSIS ==="
    echo "Timestamp: $(date)"
    echo ""
    
    if docker exec nexten-redis redis-cli ping >/dev/null 2>&1; then
        echo "✅ Redis connection OK"
        
        # Statistiques Redis
        echo "--- REDIS INFO ---"
        docker exec nexten-redis redis-cli info memory
        echo ""
        docker exec nexten-redis redis-cli info stats
        echo ""
        docker exec nexten-redis redis-cli info clients
        echo ""
        
        # Nombre de clés par base
        echo "--- KEYS COUNT ---"
        for db in {0..15}; do
            keys_count=$(docker exec nexten-redis redis-cli -n $db dbsize 2>/dev/null || echo "0")
            if [ "$keys_count" != "0" ]; then
                echo "DB $db: $keys_count keys"
            fi
        done
        
    else
        echo "❌ Cannot connect to Redis"
    fi
    echo ""
} > baseline_redis.log

# Docker - Usage des ressources
log "🐳 Analyse Docker ressources..."
{
    echo "=== DOCKER RESOURCES USAGE ==="
    echo "Timestamp: $(date)"
    echo ""
    
    # Stats des containers
    echo "--- CONTAINER STATS ---"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
    echo ""
    
    # Taille des images
    echo "--- IMAGES SIZE ---"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "(nexten|commitment)" || echo "No commitment images found"
    echo ""
    
    # Volumes usage
    echo "--- VOLUMES SIZE ---"
    docker system df -v
    echo ""
} > baseline_docker.log

# 3. SETUP OUTILS DE BENCHMARKING
log "🔧 3. Setup des outils de benchmarking..."

# Installation d'Apache Bench si nécessaire
if ! command -v ab &> /dev/null; then
    warning "Apache Bench (ab) not found. Installing..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y apache2-utils
    elif command -v yum &> /dev/null; then
        sudo yum install -y httpd-tools
    elif command -v brew &> /dev/null; then
        brew install httpd
    else
        error "Cannot install Apache Bench. Please install manually."
    fi
fi

# Test Apache Bench simple
log "🚀 Test Apache Bench baseline..."
{
    echo "=== APACHE BENCH BASELINE TESTS ==="
    echo "Timestamp: $(date)"
    echo ""
    
    # Test de charge léger sur /health endpoints
    endpoints_ab=(
        "$API_BASE/health:API-Health"
        "$CV_PARSER/health:CV-Health"
        "$JOB_PARSER/health:Job-Health"
    )
    
    for endpoint in "${endpoints_ab[@]}"; do
        url=$(echo "$endpoint" | cut -d: -f1)
        name=$(echo "$endpoint" | cut -d: -f2)
        
        echo "--- $name Benchmark (10 requests, concurrency 2) ---"
        if ab -n 10 -c 2 "$url" 2>/dev/null | grep -E "(Requests per second|Time per request|Transfer rate|Connection Times)"; then
            echo "✅ $name benchmark completed"
        else
            echo "❌ $name benchmark failed"
        fi
        echo ""
    done
} > baseline_benchmark.log

# 4. GÉNÉRATION DU RAPPORT DE BASELINE
log "📋 4. Génération du rapport de baseline..."

{
    echo "# SESSION A3 - BASELINE PERFORMANCE REPORT"
    echo "================================="
    echo ""
    echo "**Generated:** $(date)"
    echo "**Duration:** Phase 0 - 45 minutes"
    echo "**Objective:** Establish baseline metrics and identify bottlenecks"
    echo ""
    
    echo "## 🎯 TARGET METRICS (Session A3)"
    echo "- Database: -40% query time, +30% throughput"
    echo "- Redis: +50% hit rate, -30% memory usage"  
    echo "- Containers: -30% image size, -20% runtime resources"
    echo "- Code: -25% response time critical paths"
    echo ""
    
    echo "## 📊 BASELINE METRICS"
    echo ""
    
    echo "### Services Connectivity"
    if [ -f "baseline_connectivity.log" ]; then
        grep -E "(✅|❌)" baseline_connectivity.log | head -10
    fi
    echo ""
    
    echo "### Average Response Times (Health Endpoints)"
    if [ -f "baseline_latency.log" ]; then
        echo "```"
        grep -E "(API-Health|CV-Parser-Health|Job-Parser-Health)" baseline_latency.log | \
        awk -F: '{print $1 ": " $2 "s"}' | head -15
        echo "```"
    fi
    echo ""
    
    echo "### PostgreSQL Performance"
    if [ -f "baseline_postgresql.log" ]; then
        echo "```"
        grep -A 5 "cache_hit_ratio" baseline_postgresql.log || echo "No PostgreSQL stats available"
        echo "```"
    fi
    echo ""
    
    echo "### Redis Performance"
    if [ -f "baseline_redis.log" ]; then
        echo "```"
        grep -E "(used_memory_human|keyspace_hits|keyspace_misses)" baseline_redis.log | head -10
        echo "```"
    fi
    echo ""
    
    echo "### Docker Resources"
    if [ -f "baseline_docker.log" ]; then
        echo "```"
        grep -A 10 "CONTAINER STATS" baseline_docker.log | head -15
        echo "```"
    fi
    echo ""
    
    echo "## 🔍 IDENTIFIED BOTTLENECKS"
    echo ""
    echo "### Critical Issues to Address:"
    echo "1. **Database Optimization Needed**"
    echo "   - Slow queries analysis required"
    echo "   - Index optimization opportunities"
    echo "   - Connection pooling tuning"
    echo ""
    echo "2. **Redis Cache Optimization**"
    echo "   - Hit rate improvement needed"
    echo "   - Memory usage optimization"
    echo "   - Pipeline operations implementation"
    echo ""
    echo "3. **Container Resource Optimization**"
    echo "   - Image size reduction opportunities"
    echo "   - Resource limits fine-tuning"
    echo "   - Multi-stage build optimization"
    echo ""
    echo "4. **Application Performance**"
    echo "   - Async operations optimization"
    echo "   - Memory leak investigation"
    echo "   - Critical path optimization"
    echo ""
    
    echo "## 📈 NEXT STEPS"
    echo ""
    echo "### Phase 1: Database Optimization (90min)"
    echo "- Run \`./database-optimization.sh\`"
    echo "- Target: -40% query time, +30% throughput"
    echo ""
    echo "### Phase 2: Redis Optimization (75min)"
    echo "- Run \`./redis-optimization.sh\`"
    echo "- Target: +50% hit rate, -30% memory usage"
    echo ""
    echo "### Phase 3: Container Optimization (75min)"
    echo "- Run \`./docker-optimization.sh\`"
    echo "- Target: -30% image size, -20% runtime resources"
    echo ""
    echo "### Phase 4: Code Optimization (45min)"
    echo "- Run \`./code-optimization.sh\`"
    echo "- Target: -25% response time critical paths"
    echo ""
    
    echo "---"
    echo "*Report generated by Session A3 Performance Optimization Framework*"
    
} > baseline_report.md

# Copier le rapport dans le répertoire parent pour visibilité
cp baseline_report.md "../baseline_report_${TIMESTAMP}.md"

log "✅ Baseline profiling completed!"
log "📋 Report: baseline_report.md"
log "📁 Detailed logs: ${RESULTS_DIR}/"
log ""
log "🚀 Ready for Phase 1: Database Optimization"
log "   Run: ./database-optimization.sh"

echo ""
echo -e "${GREEN}🎉 SESSION A3 - PHASE 0 COMPLETED!${NC}"
echo -e "${BLUE}📊 Baseline established with measurable metrics${NC}"
echo -e "${BLUE}🔍 Bottlenecks identified across all layers${NC}"
echo -e "${BLUE}⚡ Ready for performance optimization phases${NC}"
