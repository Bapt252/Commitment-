# 🧪 Guide de Test SuperSmartMatch V2 - README TESTS

## 🎯 **Démarrage Rapide - Test en 30 secondes**

```bash
# 1. Déployer SuperSmartMatch V2
./deploy-supersmartmatch-v2.sh --type docker

# 2. Exécuter les tests complets
chmod +x test-supersmartmatch-v2-complete.sh
./test-supersmartmatch-v2-complete.sh

# 3. Vérification rapide
curl http://localhost:5070/health
```

## 📊 **État de l'Implémentation**

✅ **IMPLÉMENTÉ ET OPÉRATIONNEL**
- ✅ SuperSmartMatch V1 (port 5062) - 4 algorithmes éprouvés
- ✅ Nexten Matcher (port 5052) - 40K lignes de ML avancé  
- ✅ SuperSmartMatch V2 (port 5070) - Service unifié intelligent
- ✅ Sélection automatique d'algorithmes
- ✅ APIs V2 + compatibilité V1
- ✅ Monitoring et métriques

## 🚀 **Méthodes de Test Disponibles**

### **1. Test Automatisé Complet (Recommandé)**
```bash
# Script de test complet avec 20+ tests
./test-supersmartmatch-v2-complete.sh
```
**Inclut :**
- Tests de santé des services
- Validation API V2 native
- Tests compatibilité V1
- Sélection intelligente d'algorithmes
- Tests de performance
- Cas d'usage réels

### **2. Tests Manuels Rapides**
```bash
# Test santé
curl http://localhost:5070/health

# Test API V2 simple
curl -X POST http://localhost:5070/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{"candidate":{"name":"Test"},"offers":[{"id":"1"}],"algorithm":"auto"}'

# Test compatibilité V1
curl -X POST http://localhost:5070/match \
  -H "Content-Type: application/json" \
  -d '{"candidate":{"name":"Test"},"offers":[{"id":"1"}]}'
```

### **3. Tests Spécialisés Existants**
```bash
# Tests corrigés existants
chmod +x GUIDE-TEST-SUPERSMARTMATCH-V2-CORRECTED.md

# Validation Python (si disponible)
python validate-supersmartmatch-v2.py

# Tests unitaires (si disponibles) 
python -m pytest test-supersmartmatch-v2.py -v
```

## 🎯 **Tests de Sélection Intelligente**

### **Test 1: Nexten Matcher (Prioritaire)**
```bash
# Avec questionnaire complet → sélectionne Nexten
curl -X POST http://localhost:5070/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {"name": "Expert ML", "technical_skills": [{"name": "Python", "level": "Expert", "years": 7}]},
    "candidate_questionnaire": {"work_style": "analytical", "culture_preferences": "data_driven"},
    "offers": [{"id": "ml_job", "title": "ML Engineer"}],
    "algorithm": "auto"
  }'
# ✅ Vérifier: "algorithm_used": "nexten_matcher"
```

### **Test 2: Smart Match (Géolocalisation)**
```bash
# Contraintes géographiques → sélectionne Smart
curl -X POST http://localhost:5070/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {"name": "Dev Mobile", "localisation": "Lyon"},
    "offers": [{"id": "job_paris", "localisation": "Paris"}],
    "algorithm": "auto"
  }'
# ✅ Vérifier: "algorithm_used": "smart_match"
```

### **Test 3: Enhanced (Profil Sénior)**
```bash
# 7+ années d'expérience → sélectionne Enhanced
curl -X POST http://localhost:5070/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Tech Lead",
      "experiences": [
        {"duration_months": 48, "title": "Tech Lead"},
        {"duration_months": 36, "title": "Senior Dev"}
      ]
    },
    "offers": [{"id": "lead_job", "title": "Engineering Manager"}],
    "algorithm": "auto"
  }'
# ✅ Vérifier: "algorithm_used": "enhanced"
```

## 📋 **Checklist de Validation**

### **Services Opérationnels**
```bash
# Vérifier tous les ports
curl http://localhost:5070/health  # V2 Unifié
curl http://localhost:5052/health  # Nexten Matcher
curl http://localhost:5062/health  # SuperSmartMatch V1
netstat -tlnp | grep ':505'        # Ports actifs
```

### **APIs Fonctionnelles**
- [ ] `/health` → `{"status": "healthy"}`
- [ ] `/api/v2/match` → Format API V2 complet
- [ ] `/match` → Compatibilité V1 maintenue
- [ ] `/metrics` → Métriques Prometheus
- [ ] `/api/v2/algorithms` → Liste algorithmes

### **Sélection Intelligente**
- [ ] `algorithm: "auto"` + questionnaire → Nexten
- [ ] Contraintes géo → Smart Match
- [ ] Profils séniors (7+ ans) → Enhanced
- [ ] Compétences NLP complexes → Semantic
- [ ] Fallback hiérarchique fonctionnel

### **Performance**
- [ ] Response time < 100ms (production)
- [ ] Response time < 1s (acceptable)
- [ ] Cache Redis opérationnel
- [ ] Pas d'erreurs dans les logs

## 🔧 **Déploiement pour Tests**

### **Option 1: Docker (Recommandé)**
```bash
# Déploiement automatique
./deploy-supersmartmatch-v2.sh --type docker --env production

# OU Docker Compose direct
docker-compose -f docker-compose.supersmartmatch-v2.yml up -d

# Vérification
docker ps | grep supersmartmatch
```

### **Option 2: Mode Développement**
```bash
# Setup dev
./deploy-supersmartmatch-v2.sh --type dev

# Démarrage manuel
cd venv-dev && source bin/activate
uvicorn supersmartmatch-v2-unified-service:app --reload --port 5070
```

### **Option 3: Python Natif**
```bash
# Installation native
./deploy-supersmartmatch-v2.sh --type native --env development

# Service en arrière-plan
python supersmartmatch-v2-unified-service.py
```

## 🎯 **Cas d'Usage de Test Réels**

### **Cas 1: ML Engineer avec Questionnaire Complet**
```json
{
  "candidate": {
    "name": "Alice Chen",
    "technical_skills": [
      {"name": "Python", "level": "Expert", "years": 6},
      {"name": "TensorFlow", "level": "Advanced", "years": 4}
    ]
  },
  "candidate_questionnaire": {
    "work_style": "analytical",
    "culture_preferences": "data_driven",
    "remote_preference": "hybrid"
  },
  "offers": [{
    "id": "ml_engineer_001",
    "title": "Senior ML Engineer",
    "required_skills": ["Python", "TensorFlow", "AWS"]
  }],
  "algorithm": "auto"
}
```
**Résultat attendu:** Sélection Nexten Matcher

### **Cas 2: Contraintes Géographiques**
```json
{
  "candidate": {
    "name": "Pierre Durand",
    "technical_skills": ["JavaScript", "React"],
    "localisation": "Lyon",
    "mobility": true
  },
  "offers": [
    {"id": "js_paris", "localisation": "Paris"},
    {"id": "js_marseille", "localisation": "Marseille"}
  ],
  "algorithm": "auto"
}
```
**Résultat attendu:** Sélection Smart Match avec calcul distances

### **Cas 3: Profil Sénior Leadership**
```json
{
  "candidate": {
    "name": "Philippe Roussel",
    "technical_skills": ["Java", "Architecture", "Management"],
    "experiences": [
      {"duration_months": 48, "title": "Tech Lead"},
      {"duration_months": 36, "title": "Architect"}
    ]
  },
  "offers": [{"id": "architect_job", "title": "Solution Architect"}],
  "algorithm": "auto"
}
```
**Résultat attendu:** Sélection Enhanced avec pondération expérience

## 🚨 **Résolution de Problèmes**

### **Services Non Accessibles**
```bash
# Diagnostic complet
./test-supersmartmatch-v2-complete.sh

# Vérification processus
docker ps | grep supersmartmatch
netstat -tlnp | grep 5070

# Logs de debug
docker logs supersmartmatch-v2
tail -f supersmartmatch-v2.log
```

### **Erreurs de Connectivité**
```bash
# Test connectivité services
curl http://localhost:5052/health  # Nexten
curl http://localhost:5062/health  # V1
ping localhost

# Redémarrage
docker-compose -f docker-compose.supersmartmatch-v2.yml restart
```

### **Performance Dégradée**
```bash
# Métriques temps réel
curl http://localhost:5070/metrics | grep response_time

# Cache Redis
redis-cli ping
redis-cli info stats

# Ressources système
docker stats supersmartmatch-v2
```

## 📊 **Monitoring des Tests**

### **Métriques Clés à Surveiller**
```bash
# Response time
curl http://localhost:5070/metrics | grep "response_time"

# Success rate  
curl http://localhost:5070/metrics | grep "success_rate"

# Algorithm usage
curl http://localhost:5070/metrics | grep "algorithm_selected"

# Cache performance
curl http://localhost:5070/metrics | grep "cache_hit"
```

### **Dashboard de Monitoring**
- **Grafana**: http://localhost:3000 (si monitoring activé)
- **Prometheus**: http://localhost:9090
- **Service Status**: http://localhost:5070/dashboard

## 🎉 **Commandes Express**

### **Test Complet en 1 Commande**
```bash
# Déploiement + Test complet
./deploy-supersmartmatch-v2.sh --type docker && ./test-supersmartmatch-v2-complete.sh
```

### **Test de Validation Rapide**
```bash
# Test API V2 avec résultat formaté
curl -X POST http://localhost:5070/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{"candidate":{"name":"Quick Test"},"offers":[{"id":"test"}],"algorithm":"auto"}' \
  | jq '.'
```

### **Test Performance Simple**
```bash
# 5 requêtes chronométrées
for i in {1..5}; do
  time curl -s -X POST http://localhost:5070/api/v2/match \
    -H "Content-Type: application/json" \
    -d '{"candidate":{"name":"Perf Test"},"offers":[{"id":"'$i'"}]}'
done
```

## 📚 **Documentation de Référence**

- **📖 Guide complet**: [README-SUPERSMARTMATCH-V2.md](README-SUPERSMARTMATCH-V2.md)
- **🔧 Script déploiement**: [deploy-supersmartmatch-v2.sh](deploy-supersmartmatch-v2.sh)  
- **🧪 Tests automatisés**: [test-supersmartmatch-v2-complete.sh](test-supersmartmatch-v2-complete.sh)
- **📋 Tests corrigés**: [GUIDE-TEST-SUPERSMARTMATCH-V2-CORRECTED.md](GUIDE-TEST-SUPERSMARTMATCH-V2-CORRECTED.md)
- **🏗️ Architecture**: [SUPERSMARTMATCH-V2-ARCHITECTURE-FINALE.md](SUPERSMARTMATCH-V2-ARCHITECTURE-FINALE.md)

---

## 🎯 **Résumé pour Démarrage Immédiat**

```bash
# 1. Cloner et déployer
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-
./deploy-supersmartmatch-v2.sh --type docker

# 2. Tester complet
./test-supersmartmatch-v2-complete.sh

# 3. Test manuel rapide
curl http://localhost:5070/health
curl -X POST http://localhost:5070/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{"candidate":{"name":"Test"},"offers":[{"id":"1"}],"algorithm":"auto"}'

# ✅ SuperSmartMatch V2 testé et validé !
```

**🚀 Votre SuperSmartMatch V2 est prêt et entièrement testable !**
