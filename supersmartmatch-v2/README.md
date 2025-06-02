# SuperSmartMatch V2 - Service de Matching Intelligent Unifié

## 🎯 **Vue d'ensemble**

SuperSmartMatch V2 est un service intelligent qui unifie et optimise les capacités de matching en sélectionnant automatiquement l'algorithme optimal selon le contexte.

### **Services unifiés**
- **Nexten Matcher** (port 5052) : 40K lignes de ML avancé
- **SuperSmartMatch V1** (port 5062) : 4 algorithmes de matching (smart-match, enhanced, semantic, hybrid)
- **Service unifié V2** (port 5070) : Sélection intelligente automatique

### **Objectif de performance**
🎯 **+13% de précision** grâce à la sélection intelligente d'algorithme

## 🧠 **Logique de sélection intelligente**

### **Règles métier**
1. **Nexten Matcher** : Priorité si questionnaires complets (données riches)
2. **Smart-Match** : Pour matching géographique et calculs de déplacement
3. **Enhanced** : Optimisé pour les profils seniors et expérimentés
4. **Semantic** : Pour l'analyse NLP complexe et matching de compétences
5. **Basic** : Fallback pour cas simples

### **Hiérarchie de fallback**
```
Nexten Matcher → Enhanced → Smart-Match → Semantic → Basic
```

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                SuperSmartMatch V2 (Port 5070)              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │ Sélecteur       │  │ Circuit         │  │ Monitoring  │ │
│  │ Intelligent     │  │ Breakers        │  │ Temps Réel  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
                       │                 │
        ┌──────────────┘                 └──────────────┐
        │                                               │
┌───────▼────────┐                            ┌────────▼────────┐
│ Nexten Matcher │                            │ SuperSmartMatch │
│   (Port 5052)  │                            │    V1 (5062)    │
│   40K lignes   │                            │  4 algorithmes  │
│   ML avancé    │                            │                 │
└────────────────┘                            └─────────────────┘
```

## 🚀 **Installation & Démarrage**

### **1. Configuration**
```bash
# Copier la configuration
cp .env.example .env

# Éditer vos variables d'environnement
vim .env
```

### **2. Démarrage Docker**
```bash
# Construire l'image
docker build -t supersmartmatch-v2 .

# Démarrer le service
docker-compose up supersmartmatch-v2
```

### **3. Démarrage local**
```bash
# Installer les dépendances
pip install -r requirements.txt

# Démarrer le service
python main.py
```

## 📡 **Endpoints API**

### **Endpoint principal V2**
```http
POST /api/v2/match
Content-Type: application/json

{
  "cv_data": {
    "competences": ["Python", "FastAPI"],
    "experience": 5,
    "localisation": "Paris",
    "questionnaire_complete": true
  },
  "jobs": [
    {
      "id": "job-123",
      "competences": ["Python", "Django"],
      "localisation": "Lyon",
      "type_contrat": "CDI"
    }
  ],
  "options": {
    "force_algorithm": null,
    "max_results": 10,
    "enable_fallback": true
  }
}
```

### **Endpoint de compatibilité V1**
```http
POST /api/v1/match
Content-Type: application/json

{
  "cv_data": {...},
  "job_data": [...],
  "algorithm": "auto"
}
```

### **Endpoints de monitoring**
```http
GET /api/v2/health
GET /api/v2/metrics
GET /api/v2/algorithms/status
```

## 🔧 **Configuration**

### **Variables d'environnement**
```env
# Service principal
PORT=5070
DEBUG=false
LOG_LEVEL=INFO

# Services externes
NEXTEN_MATCHER_URL=http://matching-api:5052
SUPERSMARTMATCH_V1_URL=http://supersmartmatch-service:5062

# Redis pour cache et monitoring
REDIS_URL=redis://redis:6379/0
CACHE_TTL=3600

# Circuit breakers
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
CIRCUIT_BREAKER_EXPECTED_EXCEPTION=RequestException

# Monitoring
MONITORING_ENABLED=true
METRICS_RETENTION_HOURS=24
```

## 🧪 **Tests et validation**

### **Tests unitaires**
```bash
# Exécuter tous les tests
pytest tests/

# Tests spécifiques
pytest tests/test_algorithm_selector.py
pytest tests/test_adapters.py
pytest tests/test_circuit_breakers.py
```

### **Tests d'intégration**
```bash
# Validation des services externes
python scripts/validate_integration.py

# Test de performance
python scripts/performance_test.py
```

### **Scripts de validation**
```bash
# Validation complète du système
./scripts/validate_system.sh

# Test des algorithmes individuels
./scripts/test_algorithms.sh
```

## 📊 **Monitoring et métriques**

### **Métriques collectées**
- Latence par algorithme
- Taux de succès/échec
- Utilisation des circuit breakers
- Distribution des sélections d'algorithmes
- Performance comparative

### **Dashboard**
Accès : `http://localhost:5070/dashboard`

## 🔄 **Logique de sélection détaillée**

### **1. Évaluation des données d'entrée**
```python
def evaluate_input_data(cv_data, jobs):
    score = 0
    
    # Richesse du questionnaire
    if cv_data.get('questionnaire_complete'):
        score += 40
    
    # Qualité des données géographiques
    if has_location_data(cv_data, jobs):
        score += 20
    
    # Complexité des compétences
    if has_complex_skills(cv_data, jobs):
        score += 20
    
    # Profil senior
    if is_senior_profile(cv_data):
        score += 20
    
    return score
```

### **2. Sélection d'algorithme**
```python
def select_algorithm(input_score, cv_data, jobs):
    if input_score >= 80:
        return "nexten"
    elif has_location_requirements(jobs):
        return "smart-match"
    elif is_senior_profile(cv_data):
        return "enhanced"
    elif has_complex_nlp_requirements(cv_data, jobs):
        return "semantic"
    else:
        return "basic"
```

## 🛠️ **Développement**

### **Structure du projet**
```
supersmartmatch-v2/
├── app/
│   ├── __init__.py
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Configuration centralisée
│   ├── models/              # Modèles Pydantic
│   ├── services/            # Logique métier
│   ├── adapters/            # Adaptateurs services externes
│   ├── utils/               # Utilitaires
│   └── monitoring/          # Monitoring et métriques
├── tests/
├── scripts/
├── docker/
├── requirements.txt
├── Dockerfile
└── README.md
```

### **Contribution**
1. Fork le projet
2. Créer une branche feature
3. Faire vos modifications
4. Ajouter des tests
5. Créer une Pull Request

## 📈 **Roadmap**

### **Version 2.1**
- [ ] ML automatique pour sélection d'algorithme
- [ ] Cache intelligent prédictif
- [ ] Optimisations de performance

### **Version 2.2**
- [ ] Support multi-langue
- [ ] Intégration IA générative
- [ ] Analytics avancés

## 🆘 **Support et dépannage**

### **Problèmes fréquents**

**Service non accessible**
```bash
# Vérifier le status
curl http://localhost:5070/api/v2/health

# Vérifier les logs
docker logs nexten-supersmartmatch-v2
```

**Services externes indisponibles**
```bash
# Vérifier Nexten Matcher
curl http://localhost:5052/health

# Vérifier SuperSmartMatch V1
curl http://localhost:5062/api/v1/health
```

### **Logs et debug**
```bash
# Logs détaillés
export LOG_LEVEL=DEBUG
python main.py

# Monitoring circuit breakers
curl http://localhost:5070/api/v2/metrics
```

---

**SuperSmartMatch V2** - Développé avec ❤️ pour unifier et optimiser l'intelligence de matching
