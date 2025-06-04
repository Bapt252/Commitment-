#!/bin/bash
set -euo pipefail

log() { echo -e "\033[0;34m[$(date +'%H:%M:%S')]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[$(date +'%H:%M:%S')] ✅ $1\033[0m"; }

log "🔧 Configuration Grafana dashboards..."

# Attendre que Grafana soit prêt
log "Attente Grafana..."
for i in {1..30}; do
    if curl -s http://localhost:3000/api/health | grep -q "ok"; then
        log_success "Grafana prêt"
        break
    fi
    echo -n "."
    sleep 2
done

# Vérifier datasource Prometheus
log "Vérification datasource Prometheus..."
curl -s -u admin:admin http://localhost:3000/api/datasources | jq .

# Créer un dashboard simple via API
log "Création dashboard SuperSmartMatch..."

DASHBOARD_JSON='{
  "dashboard": {
    "title": "SuperSmartMatch V2 - Monitoring",
    "tags": ["supersmartmatch", "v2"],
    "timezone": "browser",
    "panels": [
      {
        "title": "Services Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{job}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {"displayMode": "list"},
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "title": "V2 Precision Score",
        "type": "gauge",
        "targets": [
          {
            "expr": "v2_precision_score",
            "legendFormat": "V2 Precision %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "max": 100,
            "min": 0,
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "yellow", "value": 85},
                {"color": "green", "value": 95}
              ]
            },
            "unit": "percent"
          }
        }
      },
      {
        "title": "Request Rate V1 vs V2",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(v1_requests_total[5m])",
            "legendFormat": "V1 RPS"
          },
          {
            "expr": "rate(v2_requests_total[5m])",
            "legendFormat": "V2 RPS"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {
              "axisLabel": "",
              "axisPlacement": "auto",
              "barAlignment": 0,
              "drawStyle": "line",
              "fillOpacity": 10,
              "gradientMode": "none",
              "hideFrom": {"legend": false, "tooltip": false, "vis": false},
              "lineInterpolation": "linear",
              "lineWidth": 1,
              "pointSize": 5,
              "scaleDistribution": {"type": "linear"},
              "showPoints": "never",
              "spanNulls": false,
              "stacking": {"group": "A", "mode": "none"},
              "thresholdsStyle": {"mode": "off"}
            },
            "unit": "reqps"
          }
        }
      }
    ],
    "time": {"from": "now-5m", "to": "now"},
    "refresh": "5s"
  },
  "folderId": 0,
  "overwrite": true
}'

# Importer le dashboard
curl -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -u admin:admin \
  http://localhost:3000/api/dashboards/db \
  -d "$DASHBOARD_JSON"

log_success "Dashboard créé !"
log "🎯 Accédez à: http://localhost:3000/dashboards"
