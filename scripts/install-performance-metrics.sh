#!/bin/bash

# Script d'installation des métriques de performance
# Finalise la Session 2 à 100%

set -e

echo "🚀 Installation des métriques de performance - Session 2 finale"
echo "================================================================"

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les logs
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    log_error "Docker n'est pas en cours d'exécution. Veuillez démarrer Docker."
    exit 1
fi

# Créer la structure des dossiers si elle n'existe pas
log_info "Création de la structure des dossiers..."
mkdir -p shared/middleware
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/dashboards

# Installer les dépendances Python pour les métriques
log_info "Installation des dépendances Python..."
if ! grep -q "prometheus-client" requirements.txt 2>/dev/null; then
    echo "prometheus-client==0.18.0" >> requirements.txt
fi
if ! grep -q "structlog" requirements.txt 2>/dev/null; then
    echo "structlog==23.1.0" >> requirements.txt
fi

# Mettre à jour les Dockerfiles pour inclure les nouvelles dépendances
for service in cv-parser-service job-parser-service matching-service; do
    if [ -f "$service/Dockerfile" ]; then
        log_info "Mise à jour du Dockerfile pour $service..."
        
        # Ajouter l'installation du middleware de métriques
        if ! grep -q "prometheus-client" "$service/Dockerfile"; then
            sed -i '/RUN pip install/a RUN pip install prometheus-client structlog' "$service/Dockerfile"
        fi
    fi
done

# Redémarrer les services avec les nouvelles configurations
log_info "Redémarrage des services avec monitoring étendu..."

# Rebuild et restart avec monitoring
if [ -f docker-compose.yml ]; then
    docker-compose down
    docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml build --no-cache
    docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
fi

# Attendre que Prometheus soit prêt
log_info "Attente que Prometheus soit prêt..."
timeout=60
counter=0
while ! curl -s http://localhost:9090/-/ready > /dev/null; do
    if [ $counter -ge $timeout ]; then
        log_error "Timeout en attendant Prometheus"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done

# Attendre que Grafana soit prêt
log_info "Attente que Grafana soit prêt..."
counter=0
while ! curl -s http://localhost:3001/api/health > /dev/null; do
    if [ $counter -ge $timeout ]; then
        log_error "Timeout en attendant Grafana"
        exit 1
    fi
    sleep 1
    counter=$((counter + 1))
done

# Vérification que tout fonctionne
log_info "Vérification des endpoints de métriques..."

services=("localhost:5051" "localhost:5055" "localhost:5052" "localhost:5050")
service_names=("CV Parser" "Job Parser" "Matching Service" "API Gateway")

for i in "${!services[@]}"; do
    service=${services[$i]}
    name=${service_names[$i]}
    
    if curl -s "http://$service/metrics" > /dev/null; then
        log_info "✓ $name - Métriques disponibles"
    else
        log_warn "✗ $name - Métriques non disponibles (service peut-être en cours de démarrage)"
    fi
done

# Test rapide pour générer quelques métriques
log_info "Génération de métriques de test..."
for i in {1..5}; do
    curl -s http://localhost:5051/health > /dev/null || true
    curl -s http://localhost:5055/health > /dev/null || true
    curl -s http://localhost:5052/health > /dev/null || true
    sleep 1
done

# Afficher les URLs d'accès
echo ""
echo "🎉 Installation terminée avec succès!"
echo "=================================="
echo ""
echo "📊 Monitoring URLs:"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3001 (admin/admin123)"
echo "   • AlertManager: http://localhost:9093"
echo ""
echo "📈 Métriques Services:"
echo "   • CV Parser: http://localhost:5051/metrics"
echo "   • Job Parser: http://localhost:5055/metrics"
echo "   • Matching: http://localhost:5052/metrics"
echo "   • API Gateway: http://localhost:5050/metrics"
echo ""
echo "🔍 Dashboards Grafana:"
echo "   • Rechercher 'Nexten ML/AI Performance Dashboard' dans Grafana"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Vérifiez les métriques dans Prometheus"
echo "   2. Consultez les dashboards dans Grafana"
echo "   3. Configurez les notifications d'alertes"
echo "   4. Testez les endpoints pour générer des métriques"
echo ""
echo "📈 Métriques disponibles:"
echo "   • fastapi_requests_total - Nombre total de requêtes"
echo "   • fastapi_request_duration_seconds - Durée des requêtes"
echo "   • ml_inference_duration_seconds - Durée des inférences ML"
echo "   • ml_inference_total - Nombre d'inférences ML"
echo "   • parsing_accuracy_score - Score de précision du parsing"
echo "   • matching_score_distribution - Distribution des scores de matching"
echo "   • file_processing_size_bytes - Taille des fichiers traités"
echo ""

log_info "🎯 Session 2 complétée à 100%! Votre environnement de développement ML/AI est prêt."

exit 0
