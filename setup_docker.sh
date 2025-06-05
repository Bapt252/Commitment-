#!/bin/bash

# =============================================================================
# Script de Setup Docker pour SuperSmartMatch V2
# Construit toutes les images nécessaires localement
# =============================================================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher un message coloré
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${BLUE}🚀 Setup SuperSmartMatch V2 - Construction des images Docker${NC}"
echo "=================================================================="

# Vérification des prérequis
log_info "Vérification des prérequis..."
if ! command -v docker &> /dev/null; then
    log_error "Docker n'est pas installé. Installez Docker Desktop pour continuer."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose n'est pas installé."
    exit 1
fi

log_success "Docker et Docker Compose sont installés"

# Création du docker-compose pour les tests
log_info "Création du docker-compose de test..."

cat > docker-compose.test.yml << 'EOF'
version: '3.8'

services:
  # Infrastructure Services
  redis:
    image: redis:7-alpine
    container_name: nexten_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    networks:
      - nexten_network

  postgres:
    image: postgres:15
    container_name: nexten_postgres
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=nexten
      - POSTGRES_USER=postgres  
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-multiple-postgres-databases.sh:/docker-entrypoint-initdb.d/init-multiple-postgres-databases.sh
    networks:
      - nexten_network

  minio:
    image: minio/minio:latest
    container_name: nexten_minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin123
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"
    networks:
      - nexten_network

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    container_name: nexten_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    networks:
      - nexten_network

  grafana:
    image: grafana/grafana:latest
    container_name: nexten_grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning:ro
    networks:
      - nexten_network

  alertmanager:
    image: prom/alertmanager:latest
    container_name: nexten_alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager:ro
    networks:
      - nexten_network

  # Exporters
  node-exporter:
    image: prom/node-exporter:latest
    container_name: nexten_node_exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - nexten_network

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: nexten_redis_exporter
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis://redis:6379
    depends_on:
      - redis
    networks:
      - nexten_network

  postgres-exporter:
    image: prometheuscommunity/postgres-exporter:latest
    container_name: nexten_postgres_exporter
    ports:
      - "9187:9187"
    environment:
      - DATA_SOURCE_NAME=postgresql://postgres:password@postgres:5432/nexten?sslmode=disable
    depends_on:
      - postgres
    networks:
      - nexten_network

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: nexten_cadvisor
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:rw
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    privileged: true
    networks:
      - nexten_network

  # Application Services
  cv-parser:
    build:
      context: ./cv-parser-service
      dockerfile: Dockerfile
    container_name: nexten_cv_parser
    ports:
      - "5051:5051"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/nexten
      - LOG_LEVEL=INFO
    depends_on:
      - redis
      - postgres
    volumes:
      - ./logs:/app/logs
    networks:
      - nexten_network

  job-parser:
    build:
      context: ./job-parser-service
      dockerfile: Dockerfile
    container_name: nexten_job_parser
    ports:
      - "5053:5053"
    environment:
      - REDIS_URL=redis://redis:6379/1
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/nexten
      - LOG_LEVEL=INFO
    depends_on:
      - redis
      - postgres
    volumes:
      - ./logs:/app/logs
    networks:
      - nexten_network

  matching-service:
    build:
      context: ./matching-service
      dockerfile: Dockerfile
    container_name: nexten_matching
    ports:
      - "5052:5052"
    environment:
      - REDIS_URL=redis://redis:6379/2
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/nexten
      - LOG_LEVEL=INFO
    depends_on:
      - redis
      - postgres
    volumes:
      - ./logs:/app/logs
    networks:
      - nexten_network

  gateway:
    build:
      context: ./gateway
      dockerfile: Dockerfile
    container_name: nexten_gateway
    ports:
      - "5050:5050"
    environment:
      - CV_PARSER_URL=http://cv-parser:5051
      - JOB_PARSER_URL=http://job-parser:5053
      - MATCHING_URL=http://matching-service:5052
      - REDIS_URL=redis://redis:6379/3
    depends_on:
      - cv-parser
      - job-parser
      - matching-service
    networks:
      - nexten_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: nexten_frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5050
    depends_on:
      - gateway
    networks:
      - nexten_network

  # Development Tools
  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: nexten_redis_commander
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOSTS=local:redis:6379
    depends_on:
      - redis
    networks:
      - nexten_network

  rq-dashboard:
    image: eoranged/rq-dashboard:latest
    container_name: nexten_rq_dashboard
    ports:
      - "9181:9181"
    environment:
      - RQ_DASHBOARD_REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    networks:
      - nexten_network

volumes:
  redis_data:
  postgres_data:
  minio_data:
  grafana_data:

networks:
  nexten_network:
    driver: bridge
EOF

log_success "docker-compose.test.yml créé"

# Construction des images une par une
log_info "Construction des images Docker..."

# Services principaux
services=(
    "cv-parser-service:nexten-cv-parser"
    "job-parser-service:nexten-job-parser" 
    "matching-service:nexten-matching"
    "gateway:nexten-gateway"
    "frontend:nexten-frontend"
)

for service in "${services[@]}"; do
    IFS=':' read -r directory image_name <<< "$service"
    
    if [ -d "$directory" ]; then
        log_info "Construction de l'image $image_name depuis $directory..."
        
        if docker build -t "$image_name:latest" "$directory/"; then
            log_success "Image $image_name construite avec succès"
        else
            log_warning "Échec de construction de $image_name, on continue..."
        fi
    else
        log_warning "Répertoire $directory non trouvé, on passe..."
    fi
done

# Création des dossiers nécessaires
log_info "Création des dossiers de configuration..."

mkdir -p monitoring/{prometheus,grafana,alertmanager}
mkdir -p logs

# Configuration Prometheus basique
cat > monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'cv-parser'
    static_configs:
      - targets: ['cv-parser:5051']
    metrics_path: '/metrics'

  - job_name: 'job-parser'
    static_configs:
      - targets: ['job-parser:5053']
    metrics_path: '/metrics'

  - job_name: 'matching-service'
    static_configs:
      - targets: ['matching-service:5052']
    metrics_path: '/metrics'

  - job_name: 'gateway'
    static_configs:
      - targets: ['gateway:5050']
    metrics_path: '/metrics'
EOF

# Configuration AlertManager basique
cat > monitoring/alertmanager/alertmanager.yml << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alertmanager@nexten.local'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://127.0.0.1:5001/'
EOF

log_success "Configuration de monitoring créée"

# Script de démarrage
cat > start_nexten.sh << 'EOF'
#!/bin/bash

echo "🚀 Démarrage de SuperSmartMatch V2..."

# Arrêter les conteneurs existants si ils existent
docker-compose -f docker-compose.test.yml down

# Nettoyer les volumes orphelins
docker volume prune -f

# Démarrer les services infrastructure d'abord
echo "📊 Démarrage de l'infrastructure..."
docker-compose -f docker-compose.test.yml up -d redis postgres minio

# Attendre que les services soient prêts
echo "⏳ Attente de l'infrastructure (30s)..."
sleep 30

# Démarrer les services de monitoring
echo "📈 Démarrage du monitoring..."
docker-compose -f docker-compose.test.yml up -d prometheus grafana alertmanager node-exporter redis-exporter postgres-exporter cadvisor

# Attendre que le monitoring soit prêt
echo "⏳ Attente du monitoring (15s)..."
sleep 15

# Démarrer les services applicatifs
echo "🔧 Démarrage des services métier..."
docker-compose -f docker-compose.test.yml up -d cv-parser job-parser matching-service gateway

# Attendre que les services métier soient prêts
echo "⏳ Attente des services métier (20s)..."
sleep 20

# Démarrer le frontend et les outils de dev
echo "🌐 Démarrage du frontend et outils de développement..."
docker-compose -f docker-compose.test.yml up -d frontend redis-commander rq-dashboard

echo "✅ SuperSmartMatch V2 démarré!"
echo ""
echo "🔗 Services disponibles:"
echo "  - Frontend:          http://localhost:3000"
echo "  - API Gateway:       http://localhost:5050"
echo "  - CV Parser:         http://localhost:5051" 
echo "  - Job Parser:        http://localhost:5053"
echo "  - Matching Service:  http://localhost:5052"
echo "  - Grafana:           http://localhost:3001 (admin/admin123)"
echo "  - Prometheus:        http://localhost:9090"
echo "  - Redis Commander:   http://localhost:8081"
echo "  - RQ Dashboard:      http://localhost:9181"
echo "  - MinIO:             http://localhost:9001 (minioadmin/minioadmin123)"
echo ""
echo "🧪 Pour tester le système:"
echo "  ./scripts/test-full-integration.sh"
EOF

chmod +x start_nexten.sh

# Script d'arrêt
cat > stop_nexten.sh << 'EOF'
#!/bin/bash

echo "🛑 Arrêt de SuperSmartMatch V2..."
docker-compose -f docker-compose.test.yml down

echo "🧹 Nettoyage des ressources..."
docker system prune -f

echo "✅ SuperSmartMatch V2 arrêté"
EOF

chmod +x stop_nexten.sh

# Script de test rapide
cat > quick_test.sh << 'EOF'
#!/bin/bash

echo "🧪 Tests rapides SuperSmartMatch V2..."

# Test des services de base
echo "🔍 Vérification des services..."

services=(
    "http://localhost:5050/health:API Gateway"
    "http://localhost:5051/health:CV Parser"
    "http://localhost:5053/health:Job Parser" 
    "http://localhost:5052/health:Matching Service"
    "http://localhost:3000:Frontend"
    "http://localhost:9090:Prometheus"
    "http://localhost:3001:Grafana"
)

for service in "${services[@]}"; do
    IFS=':' read -r url name <<< "$service"
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        echo "✅ $name - OK"
    else
        echo "❌ $name - FAILED"
    fi
done

echo ""
echo "🎯 Test de parsing CV (mock)..."
CV_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"mock": true}' \
    http://localhost:5051/api/parse-cv-mock/ 2>/dev/null)

if echo "$CV_RESPONSE" | grep -q -i "success\|result\|parsed"; then
    echo "✅ CV Parser - Test réussi"
else
    echo "❌ CV Parser - Test échoué"
fi

echo ""
echo "💼 Test de parsing Job (mock)..."
JOB_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"mock": true}' \
    http://localhost:5053/api/parse-job-mock/ 2>/dev/null)

if echo "$JOB_RESPONSE" | grep -q -i "success\|result\|parsed"; then
    echo "✅ Job Parser - Test réussi"
else
    echo "❌ Job Parser - Test échoué"
fi

echo ""
echo "🎯 Test de matching..."
MATCH_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "cv_data": {"skills": ["python", "django"]},
        "job_data": {"required_skills": ["python", "api"]}
    }' \
    http://localhost:5052/api/match/ 2>/dev/null)

if echo "$MATCH_RESPONSE" | grep -q -i "score\|match"; then
    echo "✅ Matching Service - Test réussi"
else
    echo "❌ Matching Service - Test échoué"
fi

echo ""
echo "📊 Tests terminés!"
EOF

chmod +x quick_test.sh

log_success "Scripts de gestion créés:"
log_info "  - start_nexten.sh     : Démarre tous les services"
log_info "  - stop_nexten.sh      : Arrête tous les services" 
log_info "  - quick_test.sh       : Tests rapides des APIs"

echo ""
echo -e "${GREEN}🎉 Setup terminé avec succès ! 🎉${NC}"
echo ""
echo -e "${YELLOW}📋 Prochaines étapes :${NC}"
echo "  1. Démarrer le système :  ${BLUE}./start_nexten.sh${NC}"
echo "  2. Tester les APIs :      ${BLUE}./quick_test.sh${NC}"
echo "  3. Tests complets :       ${BLUE}./scripts/test-full-integration.sh${NC}"
echo ""
echo -e "${BLUE}📊 Services qui seront disponibles :${NC}"
echo "  🌐 Frontend:          http://localhost:3000"
echo "  🔧 API Gateway:       http://localhost:5050"
echo "  📄 CV Parser:         http://localhost:5051"
echo "  💼 Job Parser:        http://localhost:5053"
echo "  🎯 Matching Service:  http://localhost:5052"
echo "  📈 Grafana:           http://localhost:3001"
echo "  📊 Prometheus:        http://localhost:9090"
echo ""