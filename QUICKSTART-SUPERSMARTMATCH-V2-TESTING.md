# 🎯 SuperSmartMatch V2 - Démarrage Rapide & Tests

## ⚡ **Test Instantané (30 secondes)**

```bash
# 1. Clone du projet
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-

# 2. Test avec le nouveau script enhanced v2.0
chmod +x test-supersmartmatch-v2-enhanced.sh
./test-supersmartmatch-v2-enhanced.sh

# 3. Résultats immédiats avec rapport détaillé !
```

## 🚀 **État du Projet**

✅ **IMPLÉMENTÉ ET OPÉRATIONNEL**
- ✅ **SuperSmartMatch V2** (port 5070) - Service unifié intelligent
- ✅ **Nexten Matcher** (port 5052) - 40K lignes ML avancé
- ✅ **SuperSmartMatch V1** (port 5062) - 4 algorithmes éprouvés
- ✅ **Sélection intelligente** d'algorithmes
- ✅ **APIs V2 + compatibilité V1**
- ✅ **Monitoring & métriques**

## 🧪 **Scripts de Test Disponibles**

### **🔥 NOUVEAU - Script Enhanced V2.0 (Recommandé)**
```bash
./test-supersmartmatch-v2-enhanced.sh
```
**Fonctionnalités :**
- ✅ 60+ tests complets avec validation JSON
- ✅ Interface colorée avec timestamps
- ✅ Tests de performance en temps réel
- ✅ Validation sélection intelligente d'algorithmes
- ✅ Tests d'erreurs et cas limites
- ✅ Rapport statistiques détaillé
- ✅ Codes de sortie informatifs

### **Scripts Existants**
```bash
# Test complet classique
./test-supersmartmatch-v2-complete.sh

# Tests corrigés
# Voir: GUIDE-TEST-SUPERSMARTMATCH-V2-CORRECTED.md

# Tests unitaires Python (si disponibles)
python test_supersmartmatch_v2.py
```

## 🎯 **Tests Essentiels**

### **1. Santé des Services**
```bash
curl http://localhost:5070/health  # SuperSmartMatch V2
curl http://localhost:5052/health  # Nexten Matcher
curl http://localhost:5062/health  # SuperSmartMatch V1
```

### **2. API V2 Native**
```bash
curl -X POST http://localhost:5070/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {"name": "Test User", "technical_skills": ["Python"]},
    "offers": [{"id": "job-001", "title": "Développeur"}],
    "algorithm": "auto"
  }'
```

### **3. Compatibilité V1**
```bash
curl -X POST http://localhost:5070/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {"name": "Test User"},
    "offers": [{"id": "job-001"}]
  }'
```

## 🧠 **Tests Sélection Intelligente**

### **Nexten Matcher (Priorité)**
- **Condition :** Questionnaire candidat complet
- **Test :** Profil ML Engineer + questionnaire détaillé
- **Résultat attendu :** `"algorithm_used": "nexten_matcher"`

### **Smart Match (Géolocalisation)**
- **Condition :** Contraintes géographiques
- **Test :** Candidat Lyon → Job Paris
- **Résultat attendu :** `"algorithm_used": "smart_match"`

### **Enhanced (Seniors)**
- **Condition :** 7+ années d'expérience
- **Test :** Tech Lead expérimenté
- **Résultat attendu :** `"algorithm_used": "enhanced"`

### **Semantic (NLP)**
- **Condition :** Compétences complexes
- **Test :** Profil avec descriptions détaillées
- **Résultat attendu :** `"algorithm_used": "semantic"`

## 🔧 **Déploiement pour Tests**

### **Option 1: Docker (Recommandé)**
```bash
./deploy-supersmartmatch-v2.sh --type docker
```

### **Option 2: Mode Développement**
```bash
./deploy-supersmartmatch-v2.sh --type dev
```

### **Option 3: Python Natif**
```bash
cd supersmartmatch-v2/
pip install -r requirements.txt
python main.py
```

## 📊 **Monitoring**

### **Métriques Prometheus**
```bash
curl http://localhost:5070/metrics
```

### **Statistiques Service**
```bash
curl http://localhost:5070/stats
```

### **Informations Service**
```bash
curl http://localhost:5070/info
```

## 🚨 **Dépannage Rapide**

### **Services Non Actifs**
```bash
# Vérifier ports
netstat -tlnp | grep ':505'

# Vérifier Docker
docker ps | grep supersmartmatch

# Redémarrer
docker-compose restart
```

### **Performance Dégradée**
```bash
# Test performance
time curl http://localhost:5070/health

# Métriques temps réel
curl http://localhost:5070/metrics | grep response_time
```

## 📚 **Documentation Complète**

- 📖 **Guide Enhanced :** [TESTING-GUIDE-SUPERSMARTMATCH-V2-ENHANCED.md](TESTING-GUIDE-SUPERSMARTMATCH-V2-ENHANCED.md)
- 📖 **Guide Tests :** [TESTING-GUIDE-SUPERSMARTMATCH-V2.md](TESTING-GUIDE-SUPERSMARTMATCH-V2.md)
- 📖 **README V2 :** [README-SUPERSMARTMATCH-V2.md](README-SUPERSMARTMATCH-V2.md)
- 🏗️ **Architecture :** [SUPERSMARTMATCH-V2-ARCHITECTURE-FINALE.md](SUPERSMARTMATCH-V2-ARCHITECTURE-FINALE.md)
- 🚀 **Déploiement :** [SUPERSMARTMATCH-V2-DEPLOYMENT-GUIDE.md](SUPERSMARTMATCH-V2-DEPLOYMENT-GUIDE.md)

## 🎉 **Résumé Express**

```bash
# 🚀 DÉMARRAGE IMMÉDIAT
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-
chmod +x test-supersmartmatch-v2-enhanced.sh
./test-supersmartmatch-v2-enhanced.sh

# ✅ En 30 secondes, vous avez :
# - Cloné le projet SuperSmartMatch V2
# - Exécuté 60+ tests complets
# - Obtenu un rapport détaillé de santé
# - Validé la sélection intelligente d'algorithmes
```

**🎯 Votre SuperSmartMatch V2 est prêt à être testé avec les outils les plus avancés !**

---

### **🔗 Liens Utiles**

- 🌐 **GitHub :** https://github.com/Bapt252/Commitment-
- 📊 **Monitoring :** http://localhost:5070/metrics
- 🏥 **Health Check :** http://localhost:5070/health
- 📚 **API Docs :** http://localhost:5070/docs (si activé)
