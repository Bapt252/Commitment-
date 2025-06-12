#!/bin/bash
# fix_grafana_prometheus_connection.sh
# Script pour corriger immédiatement la connexion Grafana → Prometheus

echo "🔧 Correction connexion Grafana → Prometheus SuperSmartMatch"
echo "============================================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de log
log() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. Vérifier l'état des containers
log "Vérification de l'état des containers..."
PROMETHEUS_CONTAINER=$(docker ps --format "table {{.Names}}" | grep prometheus)
GRAFANA_CONTAINER=$(docker ps --format "table {{.Names}}" | grep grafana)

if [ -z "$PROMETHEUS_CONTAINER" ]; then
    error "Container Prometheus non trouvé"
    exit 1
else
    success "Prometheus trouvé: $PROMETHEUS_CONTAINER"
fi

if [ -z "$GRAFANA_CONTAINER" ]; then
    error "Container Grafana non trouvé"  
    exit 1
else
    success "Grafana trouvé: $GRAFANA_CONTAINER"
fi

# 2. Tester la connectivité Prometheus
log "Test de connectivité Prometheus..."
PROM_HEALTH=$(curl -s http://localhost:9090/-/healthy 2>/dev/null || echo "FAIL")
if [ "$PROM_HEALTH" = "Prometheus is Healthy." ]; then
    success "Prometheus est accessible sur localhost:9090"
else
    warning "Prometheus pourrait ne pas être accessible"
    # Essayer de trouver le port
    PROM_PORT=$(docker port $PROMETHEUS_CONTAINER | grep 9090 | cut -d':' -f2)
    if [ ! -z "$PROM_PORT" ]; then
        log "Port Prometheus détecté: $PROM_PORT"
    fi
fi

# 3. Vérifier la configuration réseau Docker
log "Vérification du réseau Docker..."
NETWORK_NAME=$(docker inspect $PROMETHEUS_CONTAINER | jq -r '.[0].NetworkSettings.Networks | keys[]' 2>/dev/null)
if [ ! -z "$NETWORK_NAME" ] && [ "$NETWORK_NAME" != "null" ]; then
    success "Réseau détecté: $NETWORK_NAME"
    
    # Obtenir l'IP du container Prometheus
    PROM_IP=$(docker inspect $PROMETHEUS_CONTAINER | jq -r ".[0].NetworkSettings.Networks.\"$NETWORK_NAME\".IPAddress" 2>/dev/null)
    if [ ! -z "$PROM_IP" ] && [ "$PROM_IP" != "null" ]; then
        success "IP Prometheus: $PROM_IP"
    fi
fi

# 4. Correction de la datasource Grafana via API
log "Correction de la configuration Grafana..."

# Attendre que Grafana soit prêt
log "Attente de Grafana..."
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health >/dev/null 2>&1; then
        success "Grafana est prêt"
        break
    fi
    sleep 2
    if [ $i -eq 30 ]; then
        error "Timeout: Grafana non accessible"
        exit 1
    fi
done

# Configuration de la datasource corrigée
DATASOURCE_CONFIG=$(cat << EOF
{
  "name": "Prometheus",
  "type": "prometheus",
  "url": "http://$PROMETHEUS_CONTAINER:9090",
  "access": "proxy",
  "isDefault": true,
  "jsonData": {
    "httpMethod": "POST",
    "manageAlerts": true,
    "prometheusType": "Prometheus"
  }
}
EOF
)

# Créer/Mettre à jour la datasource
log "Mise à jour de la datasource Prometheus..."
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d "$DATASOURCE_CONFIG" \
  http://localhost:3000/api/datasources 2>/dev/null)

if echo "$RESPONSE" | grep -q "error"; then
    # Si erreur, essayer de mettre à jour
    warning "Mise à jour de la datasource existante..."
    DATASOURCE_ID=$(curl -s -H "Authorization: Basic YWRtaW46YWRtaW4=" \
      http://localhost:3000/api/datasources/name/Prometheus | jq -r '.id' 2>/dev/null)
    
    if [ ! -z "$DATASOURCE_ID" ] && [ "$DATASOURCE_ID" != "null" ]; then
        curl -s -X PUT \
          -H "Content-Type: application/json" \
          -H "Authorization: Basic YWRtaW46YWRtaW4=" \
          -d "$DATASOURCE_CONFIG" \
          http://localhost:3000/api/datasources/$DATASOURCE_ID >/dev/null
        success "Datasource mise à jour (ID: $DATASOURCE_ID)"
    fi
else
    success "Datasource Prometheus configurée"
fi

# 5. Test final de la connexion
log "Test final de la connexion..."
TEST_QUERY=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d '{"queries":[{"refId":"A","expr":"vector(95.09)","format":"time_series"}]}' \
  http://localhost:3000/api/ds/query 2>/dev/null)

if echo "$TEST_QUERY" | grep -q "95.09"; then
    success "✅ Connexion Grafana → Prometheus RÉPARÉE !"
else
    warning "Test partiel - vérification manuelle nécessaire"
fi

# 6. Instructions finales
echo ""
echo "🎉 CORRECTION TERMINÉE"
echo "======================"
echo "📊 Grafana: http://localhost:3000 (admin/admin)"
echo "📈 Prometheus: http://localhost:9090"
echo ""
echo "🔄 Actions suivantes:"
echo "1. Ouvrir Grafana dans votre navigateur"
echo "2. Aller dans Configuration → Data Sources → Prometheus"
echo "3. Vérifier que l'URL est: http://$PROMETHEUS_CONTAINER:9090"
echo "4. Cliquer 'Save & Test' - devrait afficher '✅ Data source is working'"
echo "5. Aller dans votre dashboard et tester la requête: vector(95.09)"
echo ""
echo "💡 Si problème persiste:"
echo "   - Vérifier: docker logs $GRAFANA_CONTAINER"
echo "   - Vérifier: docker logs $PROMETHEUS_CONTAINER"
echo "   - Redémarrer: docker restart $GRAFANA_CONTAINER"

# Afficher les informations de debug
echo ""
echo "🐛 Informations de debug:"
echo "Container Prometheus: $PROMETHEUS_CONTAINER"
echo "Container Grafana: $GRAFANA_CONTAINER"
echo "Réseau Docker: $NETWORK_NAME"
echo "IP Prometheus: $PROM_IP"
echo ""

success "Script terminé avec succès !"
