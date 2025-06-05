# 🔧 Fix Grafana-Prometheus Connection - SuperSmartMatch V2

## 🚨 Problème Identifié

Grafana ne peut pas se connecter à Prometheus car les noms de containers ne correspondent pas :
- **Container actuel :** `supersmartmatch-prometheus`
- **Configuration Grafana :** `prometheus:9090`

## ⚡ Solution Immédiate (2 minutes)

### Option 1: Script Automatique ✅ RECOMMANDÉ
```bash
# Télécharger et exécuter la correction automatique
git pull origin main
chmod +x scripts/fix_grafana_prometheus_connection.sh
./scripts/fix_grafana_prometheus_connection.sh
```

### Option 2: Correction Manuelle
1. **Ouvrir Grafana :** http://localhost:3000 (admin/admin)
2. **Aller dans :** Configuration → Data Sources → Prometheus  
3. **Changer URL de :**
   ```
   http://prometheus:9090
   ```
   **vers :**
   ```
   http://supersmartmatch-prometheus:9090
   ```
4. **Cliquer :** "Save & Test"
5. **Résultat attendu :** ✅ "Data source is working"

## 🎯 Test de Validation

Une fois la correction appliquée, testez dans votre dashboard :
```promql
vector(95.09)
```
**Résultat attendu :** Affichage de 95.09% en vert

## 📊 Nouvelles Ressources Ajoutées

### Dashboard SuperSmartMatch V2
- **Precision Matching (%)** - Objectif : 95.09% ✅
- **Performance P95 (ms)** - Objectif : 50ms ✅  
- **ROI Annual (€)** - Objectif : €964,154 ✅
- **Services Health** - Monitoring temps réel

### Configuration Prometheus Optimisée
- Scraping configuré pour tous les services SuperSmartMatch
- Intervalles optimisés par service
- Support des métriques custom

### Script de Correction Intelligent
- Détection automatique des noms de containers
- Configuration automatique des datasources
- Tests de connectivité intégrés
- Instructions de debug détaillées

## 🔄 Commandes de Debug

```bash
# Vérifier l'état des containers
docker ps | grep -E "(prometheus|grafana)"

# Tester Prometheus directement
curl http://localhost:9090/-/healthy

# Voir les logs
docker logs supersmartmatch-prometheus
docker logs supersmartmatch-grafana

# Redémarrer si nécessaire  
docker restart supersmartmatch-grafana
```

## 🎉 Résultat Final

Après correction :
- ✅ Panel "Services Status" : Vert (1.0)
- ✅ Panel "Precision Matching (%)" : Vert (95.09%)
- ✅ Panel "Performance P95 (ms)" : Vert (50ms)
- ✅ Panel "ROI Annual (€)" : Vert (€964,154)

## 🚀 Prochaines Étapes

1. **Configurer les vraies métriques** depuis vos services
2. **Ajouter des alertes** pour monitoring proactif  
3. **Intégrer avec production_monitor.py**
4. **Configurer dashboards par service**

---

**Temps estimé de résolution :** 2 minutes avec le script automatique
