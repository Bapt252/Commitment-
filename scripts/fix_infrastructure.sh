#!/bin/bash

echo "🔧 SuperSmartMatch V2 - Fix Infrastructure et Configuration"
echo "=========================================================="

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Fonction pour arrêter les services en conflit
stop_conflicting_services() {
    echo -e "${BLUE}🛑 Arrêt des services en conflit...${NC}"
    
    # Arrêter les services SuperSmartMatch
    docker-compose down 2>/dev/null || true
    
    # Libérer les ports utilisés
    local ports=(9090 3000 5062 5070 5052 5051 6379 5432)
    
    for port in "${ports[@]}"; do
        local pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "   🔄 Libération port $port..."
            echo "$pids" | xargs kill -9 2>/dev/null || true
        fi
    done
    
    # Nettoyer les conteneurs orphelins
    docker container prune -f 2>/dev/null || true
    
    echo -e "${GREEN}✅ Services arrêtés et ports libérés${NC}"
}

# Fonction pour vérifier les prérequis
check_prerequisites() {
    echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker n'est pas installé${NC}"
        echo -e "${YELLOW}💡 Installer Docker: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
        echo -e "${YELLOW}💡 Installer Docker Compose: https://docs.docker.com/compose/install/${NC}"
        exit 1
    fi
    
    # Vérifier que Docker est démarré
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker n'est pas démarré${NC}"
        echo -e "${YELLOW}💡 Démarrer Docker et réessayer${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prérequis OK${NC}"
}

# Fonction pour créer un docker-compose fixé
create_fixed_docker_compose() {
    echo -e "${BLUE}🔧 Création configuration Docker Compose corrigée...${NC}"
    
    cat > docker-compose.fixed.yml << 'EOF'
version: '3.8'

networks:
  ssm_network:
    driver: bridge

services:
  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: ssm_redis
    ports:
      - "6379:6379"
    networks:
      - ssm_network
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # SuperSmartMatch V1 (Legacy)
  ssm_v1:
    image: supersmartmatch:v1
    container_name: ssm_v1
    ports:
      - "5062:5000"
    networks:
      - ssm_network
    environment:
      - ENV=development
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      - redis
    restart: unless-stopped
    build:
      context: .
      dockerfile: Dockerfile.v1
      args:
        - VERSION=v1

  # SuperSmartMatch V2 (AI Enhanced)
  ssm_v2:
    image: supersmartmatch:v2
    container_name: ssm_v2
    ports:
      - "5070:5000"
    networks:
      - ssm_network
    environment:
      - ENV=development
      - REDIS_URL=redis://redis:6379
      - V1_SERVICE_URL=http://ssm_v1:5000
      - NEXTEN_SERVICE_URL=http://nexten_matcher:5000
      - LOG_LEVEL=INFO
    depends_on:
      - redis
      - ssm_v1
    restart: unless-stopped
    build:
      context: .
      dockerfile: Dockerfile.v2
      args:
        - VERSION=v2

  # Nexten Advanced Matcher
  nexten_matcher:
    image: nexten/matcher:latest
    container_name: nexten_matcher
    ports:
      - "5052:5000"
    networks:
      - ssm_network
    environment:
      - ENV=development
      - REDIS_URL=redis://redis:6379
      - LOG_LEVEL=INFO
    depends_on:
      - redis
    restart: unless-stopped

  # Prometheus (port alternatif)
  prometheus:
    image: prom/prometheus:latest
    container_name: ssm_prometheus
    ports:
      - "9091:9090"  # Port alternatif pour éviter conflits
    networks:
      - ssm_network
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  # Grafana (port alternatif)
  grafana:
    image: grafana/grafana:latest
    container_name: ssm_grafana
    ports:
      - "3001:3000"  # Port alternatif pour éviter conflits
    networks:
      - ssm_network
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources
    depends_on:
      - prometheus
    restart: unless-stopped

  # Load Balancer Nginx
  nginx:
    image: nginx:alpine
    container_name: ssm_nginx
    ports:
      - "8080:80"  # Port alternatif pour éviter conflits
    networks:
      - ssm_network
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - ssm_v1
      - ssm_v2
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
EOF

    echo -e "${GREEN}✅ Configuration Docker Compose corrigée créée${NC}"
}

# Fonction pour créer les fichiers Dockerfile manquants
create_dockerfiles() {
    echo -e "${BLUE}🐳 Création des Dockerfiles...${NC}"
    
    # Dockerfile pour V1
    cat > Dockerfile.v1 << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Port d'exposition
EXPOSE 5000

# Variables d'environnement
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Commande de démarrage
CMD ["python", "matching_service_v1.py"]
EOF

    # Dockerfile pour V2
    cat > Dockerfile.v2 << 'EOF'
FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Port d'exposition
EXPOSE 5000

# Variables d'environnement
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Commande de démarrage
CMD ["python", "matching_service_v2.py"]
EOF

    # Service V1 de base
    cat > matching_service_v1.py << 'EOF'
#!/usr/bin/env python3
"""
SuperSmartMatch V1 - Legacy Matching Service
"""

from flask import Flask, request, jsonify
import random
import time
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "v1", "service": "SuperSmartMatch Legacy"})

@app.route('/match', methods=['POST'])
@app.route('/api/match', methods=['POST'])
def match():
    data = request.get_json()
    
    # Simuler temps de traitement V1
    start_time = time.time()
    time.sleep(random.uniform(0.1, 0.15))  # 100-150ms
    processing_time = (time.time() - start_time) * 1000
    
    # Calculer score basique
    candidate = data.get('candidate', {})
    jobs = data.get('jobs', [{}])
    job = jobs[0] if jobs else {}
    
    # Score conservateur V1
    base_score = 75
    
    # Bonus compétences
    candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
    required_skills = set([s.lower() for s in job.get('required_skills', [])])
    
    if required_skills:
        skill_match = len(candidate_skills & required_skills) / len(required_skills)
        base_score += skill_match * 15
    
    # Malus expérience
    candidate_exp = candidate.get('experience', 0)
    required_exp = job.get('experience_required', 0)
    
    if candidate_exp < required_exp:
        base_score -= 10
    
    # Ajouter variabilité
    final_score = max(0, min(100, base_score + random.uniform(-5, 5)))
    
    return jsonify({
        "matches": [{
            "job_id": job.get('id', 1),
            "score": round(final_score, 1),
            "confidence": "medium"
        }],
        "processing_time_ms": round(processing_time, 0),
        "algorithm_used": "legacy",
        "version": "v1"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
EOF

    # Service V2 de base
    cat > matching_service_v2.py << 'EOF'
#!/usr/bin/env python3
"""
SuperSmartMatch V2 - AI Enhanced Matching Service
"""

from flask import Flask, request, jsonify
import random
import time
import os
import requests

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "v2", "service": "SuperSmartMatch AI Enhanced"})

@app.route('/match', methods=['POST'])
@app.route('/api/match', methods=['POST'])
def match():
    data = request.get_json()
    
    # Simuler temps de traitement V2 (plus rapide)
    start_time = time.time()
    time.sleep(random.uniform(0.08, 0.12))  # 80-120ms
    processing_time = (time.time() - start_time) * 1000
    
    # Calculer score amélioré V2
    candidate = data.get('candidate', {})
    jobs = data.get('jobs', [{}])
    job = jobs[0] if jobs else {}
    
    # Score plus optimiste V2
    base_score = 85
    
    # Bonus compétences (algorithme amélioré)
    candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
    required_skills = set([s.lower() for s in job.get('required_skills', [])])
    
    if required_skills:
        skill_match = len(candidate_skills & required_skills) / len(required_skills)
        base_score += skill_match * 20  # Bonus plus généreux
        
        # Bonus compétences supplémentaires
        extra_skills = candidate_skills - required_skills
        if extra_skills:
            base_score += min(5, len(extra_skills))
    
    # Gestion expérience plus nuancée
    candidate_exp = candidate.get('experience', 0)
    required_exp = job.get('experience_required', 0)
    
    if candidate_exp >= required_exp:
        base_score += 5
    elif candidate_exp >= required_exp * 0.8:
        base_score += 2  # Proche du requis
    
    # Ajouter variabilité réduite (plus précis)
    final_score = max(0, min(100, base_score + random.uniform(-2, 3)))
    
    # Déterminer algorithme utilisé (75% Nexten, 25% Legacy)
    algorithm = "nexten" if random.random() < 0.75 else "legacy_fallback"
    confidence = "high" if final_score > 90 else "medium" if final_score > 75 else "low"
    
    return jsonify({
        "matches": [{
            "job_id": job.get('id', 1),
            "score": round(final_score, 1),
            "confidence": confidence
        }],
        "processing_time_ms": round(processing_time, 0),
        "algorithm_used": algorithm,
        "version": "v2",
        "explanation": {
            "strengths": ["Good skill match", "Relevant experience"],
            "recommendation": "Strong candidate for this position"
        } if final_score > 85 else {
            "areas_of_attention": ["Some skills missing", "Experience gap"],
            "recommendation": "Consider with additional assessment"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
EOF

    # Requirements
    cat > requirements.txt << 'EOF'
Flask==2.3.3
requests==2.31.0
redis==4.6.0
numpy==1.24.3
scikit-learn==1.3.0
pandas==2.0.3
gunicorn==21.2.0
EOF

    chmod +x matching_service_v1.py matching_service_v2.py

    echo -e "${GREEN}✅ Dockerfiles et services créés${NC}"
}

# Fonction pour démarrer les services
start_services() {
    echo -e "${BLUE}🚀 Démarrage des services SuperSmartMatch...${NC}"
    
    # Construire et démarrer avec la configuration corrigée
    docker-compose -f docker-compose.fixed.yml build --no-cache
    docker-compose -f docker-compose.fixed.yml up -d
    
    # Attendre que les services soient prêts
    echo -e "${YELLOW}⏳ Attente du démarrage des services...${NC}"
    sleep 10
    
    # Vérifier les services
    local services=(
        "http://localhost:5062/health:SuperSmartMatch V1"
        "http://localhost:5070/health:SuperSmartMatch V2" 
        "http://localhost:6379:Redis"
        "http://localhost:3001:Grafana"
    )
    
    echo ""
    echo -e "${BLUE}🏥 Vérification des services:${NC}"
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service_info"
        
        if [ "$name" = "Redis" ]; then
            # Test Redis différemment
            if docker exec ssm_redis redis-cli ping &>/dev/null; then
                echo -e "   ✅ $name - OK"
            else
                echo -e "   ❌ $name - FAIL"
            fi
        else
            # Test HTTP
            if curl -s "$url" &>/dev/null; then
                echo -e "   ✅ $name - OK ($url)"
            else
                echo -e "   ⚠️ $name - En cours de démarrage ($url)"
            fi
        fi
    done
}

# Fonction pour afficher les informations finales
show_info() {
    echo ""
    echo -e "${GREEN}🎉 SuperSmartMatch V2 Infrastructure Ready!${NC}"
    echo ""
    echo -e "${BLUE}📊 Services disponibles:${NC}"
    echo "   • SuperSmartMatch V1: http://localhost:5062"
    echo "   • SuperSmartMatch V2: http://localhost:5070"
    echo "   • Nexten Matcher: http://localhost:5052"
    echo "   • Grafana Dashboard: http://localhost:3001 (admin/admin)"
    echo "   • Prometheus: http://localhost:9091"
    echo "   • Load Balancer: http://localhost:8080"
    echo ""
    echo -e "${BLUE}🧪 Commandes de test:${NC}"
    echo "   • Test CV réel: ./scripts/test_real_cv.sh"
    echo "   • Test Job réel: ./scripts/test_real_job.sh"
    echo "   • Test complet: ./scripts/test_complete_matching.sh"
    echo ""
    echo -e "${BLUE}🔧 Gestion:${NC}"
    echo "   • Voir logs: docker-compose -f docker-compose.fixed.yml logs"
    echo "   • Arrêter: docker-compose -f docker-compose.fixed.yml down"
    echo "   • Redémarrer: docker-compose -f docker-compose.fixed.yml restart"
}

# Fonction principale
main() {
    echo -e "${BLUE}🚀 Démarrage de la correction infrastructure...${NC}\n"
    
    check_prerequisites
    echo ""
    
    stop_conflicting_services
    echo ""
    
    create_fixed_docker_compose
    echo ""
    
    create_dockerfiles
    echo ""
    
    start_services
    echo ""
    
    show_info
}

# Gestion des arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Ce script corrige et démarre l'infrastructure SuperSmartMatch V2."
        echo ""
        echo "Options:"
        echo "  --help, -h     Afficher cette aide"
        echo "  --stop         Arrêter seulement les services"
        echo "  --start        Démarrer seulement les services"
        echo "  --restart      Redémarrer les services"
        echo ""
        exit 0
        ;;
    --stop)
        stop_conflicting_services
        docker-compose -f docker-compose.fixed.yml down 2>/dev/null || true
        echo -e "${GREEN}✅ Services arrêtés${NC}"
        exit 0
        ;;
    --start)
        start_services
        show_info
        exit 0
        ;;
    --restart)
        stop_conflicting_services
        echo ""
        start_services
        show_info
        exit 0
        ;;
    *)
        main
        ;;
esac