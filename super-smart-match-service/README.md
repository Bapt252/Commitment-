# SuperSmartMatch - Service Unifié de Matching Nexten

![SuperSmartMatch Logo](https://img.shields.io/badge/SuperSmartMatch-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-red)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

**SuperSmartMatch** est le service unifié qui regroupe TOUS les algorithmes de matching de Nexten sous une seule API intelligente.

## 🎯 **Vue d'ensemble**

### **Problème résolu**
Au lieu d'avoir 5 services séparés pour chaque algorithme, SuperSmartMatch offre :
- 🧠 **Sélection automatique** du meilleur algorithme selon le contexte
- 🔧 **Interface unifiée** pour tous vos algorithmes
- ⚡ **Performances optimisées** avec cache intelligent
- 🔄 **Fallback automatique** en cas d'erreur
- 📊 **Comparaisons** entre algorithmes

### **Algorithmes intégrés**

| Algorithme | Version | Description | Cas d'usage |
|------------|---------|-------------|-------------|
| **Original** | 1.0.0 | Algorithme de base stable | Volume important, performance |
| **Enhanced** | 1.0.0 | Moteur avancé avec matching sémantique | Précision maximale, candidats expérimentés |
| **SmartMatch** | 1.2.0 | Bidirectionnel avec géolocalisation | Mobilité géographique, temps de trajet |
| **Sémantique** | 1.1.0 | Analyse sémantique des compétences | Compétences techniques, technologies liées |
| **Personnalisé** | 1.0.0 | Optimisé pour vos besoins spécifiques | Cas particuliers, optimisations locales |
| **Hybride** | 1.0.0 | Combine plusieurs algorithmes | Cas complexes, précision maximale |

## 🚀 **Démarrage rapide**

### **Option 1: Démarrage direct**
```bash
# Cloner et accéder au service
cd super-smart-match-service

# Rendre exécutable et démarrer
chmod +x start-supersmartmatch.sh
./start-supersmartmatch.sh
```

### **Option 2: Docker**
```bash
# Construction de l'image
docker build -t supersmartmatch .

# Démarrage du conteneur
docker run -p 5070:5070 supersmartmatch
```

### **Option 3: Docker Compose (recommandé)**
```bash
# Démarrage complet avec Redis et monitoring
docker-compose -f docker-compose.supersmartmatch.yml up -d

# Ou sans monitoring
docker-compose -f docker-compose.supersmartmatch.yml up -d supersmartmatch redis
```

## 🌐 **Accès aux services**

Après démarrage, les services sont disponibles :

- **📡 API principale** : http://localhost:5070
- **📄 Documentation Swagger** : http://localhost:5070/docs
- **📆 Documentation ReDoc** : http://localhost:5070/redoc
- **🔍 Health Check** : http://localhost:5070/health
- **🧠 Algorithmes disponibles** : http://localhost:5070/algorithms

## 📋 **API Usage**

### **1. Matching automatique (recommandé)**
```javascript
POST /api/v1/match
{
  "candidate": {
    "competences": ["Python", "Django", "React"],
    "annees_experience": 4,
    "adresse": "Paris",
    "contrats_recherches": ["CDI"],
    "salaire_souhaite": 50000
  },
  "jobs": [
    {
      "id": 1,
      "titre": "Développeur Full Stack",
      "competences": ["Python", "Django", "React"],
      "type_contrat": "CDI",
      "localisation": "Paris",
      "salaire": "45K-55K€"
    }
  ],
  "algorithm": "auto",  // Sélection automatique
  "limit": 10
}
```

### **2. Algorithme spécifique**
```javascript
POST /api/v1/match
{
  "candidate": { /* ... */ },
  "jobs": [ /* ... */ ],
  "algorithm": "enhanced",  // Algorithme spécifique
  "options": {
    "performance_priority": "accuracy",
    "max_processing_time": 30
  }
}
```

### **3. Recommandation d'algorithme**
```javascript
POST /api/v1/recommend-algorithm
{
  "candidate": { /* ... */ },
  "jobs": [ /* ... */ ]
}

// Réponse
{
  "recommended_algorithm": "enhanced",
  "confidence": 85,
  "reasoning": [
    "Optimal pour candidats expérimentés (4 ans d'exp.)",
    "Adapté aux compétences techniques"
  ],
  "alternatives": ["semantic", "hybrid"]
}
```

### **4. Comparaison d'algorithmes**
```javascript
POST /api/v1/compare
{
  "candidate": { /* ... */ },
  "jobs": [ /* ... */ ]
}

// Compare tous les algorithmes et retourne les performances
```

## 🧠 **Sélection intelligente**

SuperSmartMatch sélectionne automatiquement le meilleur algorithme basé sur :

### **Critères d'analyse**
- **📊 Volume de données** : 50 offres → `semantic`, 1000+ offres → `original`
- **🎓 Expérience candidat** : Junior → `smart-match`, Senior → `enhanced`
- **💻 Type de compétences** : Techniques → `semantic`, Management → `enhanced`
- **🌍 Mobilité** : Remote → `smart-match`, Local → `enhanced`
- **⚡ Performance** : Vitesse → `original`, Précision → `hybrid`

### **Exemple de sélection**
```
👨‍💻 Candidat: Développeur Python Senior (7 ans), 200 offres
➡️  Algorithme sélectionné: Enhanced
📝 Raisons:
   ✅ Optimal pour candidats senior (7 ans d'exp.)
   ✅ Adapté aux compétences techniques
   ✅ Volume moyen (200 offres) traité efficacement
```

## 📈 **Performances et optimisations**

### **Cache intelligent**
- ⏱️ Cache des résultats (TTL: 5 minutes)
- 📁 Clés de cache optimisées
- 🗑️ Nettoyage automatique

### **Fallback automatique**
```
🎯 Algorithme demandé: enhanced
❌ Échec: Erreur de calcul
🔄 Fallback: original
✅ Résultat retourné avec metadata de fallback
```

### **Métriques de performance**
```javascript
{
  "processing_time": 0.245,
  "algorithm_used": "enhanced",
  "from_cache": false,
  "performance_prediction": {
    "estimated_processing_time": 0.240,
    "expected_accuracy": 90,
    "memory_usage": "low",
    "scalability": "excellent"
  }
}
```

## 🛠️ **Tests et validation**

### **Tests automatiques**
```bash
# Exécuter tous les tests
chmod +x test-supersmartmatch.sh
./test-supersmartmatch.sh
```

### **Tests inclus**
- 🔍 Health check et disponibilité
- 🧠 Liste et info des algorithmes
- 🎯 Matching basique et avancé
- 🤖 Sélection automatique
- 📊 Statistiques et monitoring
- ⚠️ Gestion d'erreurs

## 🔌 **Intégration front-end**

### **Modification minimale de votre front-end existant**

Au lieu de :
```javascript
// Ancien: appels séparés
fetch('http://localhost:5052/api/match')      // Service matching
fetch('http://localhost:5055/api/analyze')   // Job analyzer
fetch('http://localhost:5060/api/personalize') // Personnalisation
```

Utilisez :
```javascript
// Nouveau: appel unifié
fetch('http://localhost:5070/api/v1/match', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    candidate: candidateData,
    jobs: jobsData,
    algorithm: 'auto'  // Ou spécifique: 'enhanced', 'semantic'...
  })
})
```

### **Avantages de l'intégration**
- ⚙️ **Configuration unique** : Un seul endpoint à configurer
- 🔧 **Maintenance simplifiée** : Plus besoin de gérer 5 services
- 🧠 **Intelligence automatique** : Le meilleur algorithme automatiquement
- 📊 **Métriques unifiées** : Performance et statistiques centralisées

## 📊 **Monitoring et observabilité**

### **Métriques disponibles**
```
GET /api/v1/stats
{
  "total_algorithms": 6,
  "total_calls": 1547,
  "total_errors": 12,
  "global_error_rate": 0.008,
  "algorithms_stats": {
    "enhanced": { "calls": 856, "avg_time": 0.245, "errors": 3 },
    "semantic": { "calls": 421, "avg_time": 0.389, "errors": 2 }
  }
}
```

### **Dashboards (avec monitoring activé)**
- **Prometheus** : http://localhost:9090
- **Grafana** : http://localhost:3000 (admin/nexten123)

## 🚀 **Déploiement production**

### **Variables d'environnement**
```bash
# Configuration de base
PORT=5070
HOST=0.0.0.0
ENVIRONMENT=production

# Cache Redis (optionnel)
REDIS_URL=redis://localhost:6379/0

# Logs
LOG_LEVEL=INFO
```

### **Docker production**
```bash
# Construction optimisée
docker build --target production -t supersmartmatch:prod .

# Déploiement avec scaling
docker-compose -f docker-compose.supersmartmatch.yml up -d --scale supersmartmatch=3
```

## 📚 **Documentation détaillée**

### **Structure du projet**
```
super-smart-match-service/
├── app.py                          # API FastAPI principale
├── algorithm_manager.py            # Gestionnaire d'algorithmes
├── algorithm_selector.py           # Sélecteur intelligent
├── unified_api.py                  # Interface unifiée
├── requirements.txt                # Dépendances Python
├── Dockerfile                      # Configuration Docker
├── docker-compose.supersmartmatch.yml
├── start-supersmartmatch.sh        # Script de démarrage
├── test-supersmartmatch.sh         # Script de tests
└── README.md                       # Cette documentation
```

### **Architecture**
```
🌐 Front-end
    │
    ▼
📡 SuperSmartMatch API (Port 5070)
    │
    ├── 🧠 Algorithm Selector
    │       │
    │       ├── 📊 Analyse contexte
    │       └── 🎯 Sélection optimale
    │
    ├── 🔧 Algorithm Manager
    │       │
    │       ├── 💻 Original Algorithm
    │       ├── ⚙️  Enhanced Algorithm
    │       ├── 🌍 SmartMatch Algorithm
    │       ├── 🧠 Semantic Algorithm
    │       ├── 🔧 Custom Algorithm
    │       └── 🔀 Hybrid Algorithm
    │
    └── 🔄 Unified API
            │
            ├── ⏱️ Cache intelligent
            ├── ⚠️ Gestion d'erreurs
            └── 📊 Métriques & monitoring
```

## 🔧 **Troubleshooting**

### **Problèmes courants**

**1. Port déjà utilisé**
```bash
# Vérifier les processus sur le port 5070
lsof -i :5070

# Arrêter le processus
kill -9 <PID>

# Ou changer le port
PORT=5071 ./start-supersmartmatch.sh
```

**2. Algorithmes non trouvés**
```bash
# Vérifier la présence des fichiers
ls -la ../matching_engine.py
ls -la ../enhanced_matching_engine.py

# Vérifier le PYTHONPATH
echo $PYTHONPATH
```

**3. Erreurs de dépendances**
```bash
# Réinstaller les dépendances
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🎆 **Roadmap et améliorations**

### **Version 1.1 (prochainement)**
- 🔄 Load balancing entre algorithmes
- 📊 Métriques détaillées Prometheus
- 🌐 API de configuration dynamique
- 🤖 Machine Learning pour l'optimisation des sélections

### **Version 1.2**
- 🔌 Webhooks pour notifications
- 🔒 Authentification et autorisation
- 📊 Dashboards avancés
- 🚀 Auto-scaling basé sur la charge

## 📞 **Support**

- **📜 Documentation** : Consultez `/docs` pour l'API complète
- **🔍 Health Check** : `/health` pour vérifier le statut
- **📊 Monitoring** : `/api/v1/stats` pour les statistiques
- **🧪 Tests** : `./test-supersmartmatch.sh` pour valider

---

**🎉 SuperSmartMatch - Simplifiez votre matching avec l'intelligence unifiée !**

*Auteur: Nexten Team | Version: 1.0.0*
