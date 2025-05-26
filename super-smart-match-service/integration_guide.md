# Guide d'Intégration SuperSmartMatch

## 🔗 Intégration dans le projet Nexten existant

### 1. Ajout au docker-compose.yml principal

Ajoutez ces lignes à votre `docker-compose.yml` existant :

```yaml
# SuperSmartMatch - Service unifié
supersmartmatch:
  build:
    context: ./super-smart-match-service
    dockerfile: Dockerfile
  container_name: nexten-supersmartmatch
  ports:
    - "5070:5070"
  environment:
    - ENVIRONMENT=production
    - PORT=5070
    - HOST=0.0.0.0
    - REDIS_URL=redis://nexten-redis:6379/3
  volumes:
    - ./super-smart-match-service/logs:/app/logs
  networks:
    - nexten-network
  depends_on:
    - nexten-redis
    - matching-service
    - cv-parser-service
    - job-parser-service
  restart: unless-stopped
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:5070/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
  labels:
    - "com.nexten.service=supersmartmatch"
    - "com.nexten.version=1.0.0"
```

### 2. Mise à jour du script start-all-services.sh

Ajoutez cette ligne à votre script de démarrage :

```bash
# Ajout dans start-all-services.sh
echo "🚀 Démarrage de SuperSmartMatch (Service unifié)..."
docker-compose up -d supersmartmatch

# Vérification
echo "🔍 Vérification SuperSmartMatch..."
if curl -f http://localhost:5070/health >/dev/null 2>&1; then
    echo "✅ SuperSmartMatch opérationnel sur http://localhost:5070"
else
    echo "❌ Problème avec SuperSmartMatch"
fi
```

### 3. Modification de votre front-end

#### Ancien code (multiple services) :
```javascript
// candidate-matching-improved.html - AVANT
const matchingAPI = 'http://localhost:5052/api/match';
const jobAnalyzerAPI = 'http://localhost:5055/analyze';
const personalizationAPI = 'http://localhost:5060/api/v1/personalize';

// Multiples appels
fetch(matchingAPI, { /* ... */ })
  .then(response1 => {
    return fetch(jobAnalyzerAPI, { /* ... */ });
  })
  .then(response2 => {
    return fetch(personalizationAPI, { /* ... */ });
  });
```

#### Nouveau code (SuperSmartMatch) :
```javascript
// candidate-matching-improved.html - APRÈS
const superSmartMatchAPI = 'http://localhost:5070/api/v1/match';

// Un seul appel unifié
fetch(superSmartMatchAPI, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    candidate: {
      competences: candidateSkills,
      annees_experience: candidateExperience,
      adresse: candidateLocation,
      contrats_recherches: preferredContracts,
      salaire_souhaite: desiredSalary
    },
    jobs: jobsData,
    algorithm: 'auto',  // Sélection automatique intelligente
    options: {
      performance_priority: 'balanced',
      accuracy_priority: 'high'
    },
    limit: 20
  })
})
.then(response => response.json())
.then(data => {
  console.log('✅ Matching unifié terminé:', data);
  console.log('🧠 Algorithme utilisé:', data.algorithm_used);
  console.log('📊 Raisons du choix:', data.selection_reason);
  
  // Affichage des résultats
  displayMatchingResults(data.matches);
  
  // Affichage des métriques
  displayPerformanceMetrics(data.processing_metadata);
});
```

### 4. Configuration des paramètres avancés

```javascript
// Exemple d'utilisation avancée
const advancedMatching = {
  candidate: candidateData,
  jobs: jobsData,
  algorithm: 'auto',  // ou 'enhanced', 'semantic', 'smart-match', 'hybrid'
  options: {
    // Priorités de performance
    performance_priority: 'speed',     // 'speed', 'accuracy', 'balanced'
    accuracy_priority: 'high',         // 'high', 'medium', 'low'
    max_processing_time: 30,           // secondes
    
    // Options spécifiques
    enable_geolocation: true,
    semantic_analysis: true,
    personalization_enabled: true,
    
    // Cache
    use_cache: true,
    cache_ttl: 300  // 5 minutes
  },
  limit: 50
};
```

## 🎯 Scénarios d'utilisation

### Scénario 1: Candidat Junior
```javascript
// Le système sélectionnera automatiquement 'smart-match' ou 'enhanced'
const juniorCandidate = {
  competences: ["HTML", "CSS", "JavaScript"],
  annees_experience: 1,
  adresse: "Paris"
};
```

### Scénario 2: Candidat Senior Technique
```javascript
// Le système sélectionnera 'enhanced' ou 'semantic'
const seniorTechCandidate = {
  competences: ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
  annees_experience: 8,
  adresse: "Lyon"
};
```

### Scénario 3: Volume Important
```javascript
// Avec 1000+ offres, le système sélectionnera 'original' pour la vitesse
const largeDataset = {
  jobs: jobsArray,  // 1000+ offres
  algorithm: 'auto'
};
```

## 🔄 Migration graduelle

### Phase 1: Coexistence
```javascript
// Gardez vos anciens endpoints en fallback
const tryNewAPI = async () => {
  try {
    // Essayer SuperSmartMatch
    const response = await fetch('http://localhost:5070/api/v1/match', {
      method: 'POST',
      body: JSON.stringify(matchingRequest)
    });
    
    if (response.ok) {
      return await response.json();
    }
    throw new Error('SuperSmartMatch unavailable');
    
  } catch (error) {
    console.warn('🔄 Fallback vers ancien système:', error);
    // Fallback vers anciens services
    return await legacyMatching();
  }
};
```

### Phase 2: Migration complète
```javascript
// Remplacer tous les appels par SuperSmartMatch
const unifiedMatching = async (candidateData, jobsData, options = {}) => {
  const defaultOptions = {
    algorithm: 'auto',
    limit: 20,
    performance_priority: 'balanced'
  };
  
  const requestBody = {
    candidate: candidateData,
    jobs: jobsData,
    ...defaultOptions,
    ...options
  };
  
  const response = await fetch('http://localhost:5070/api/v1/match', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(requestBody)
  });
  
  return await response.json();
};
```

## 📊 Monitoring et debugging

### 1. Vérification de l'état
```javascript
// Vérifier si SuperSmartMatch est disponible
fetch('http://localhost:5070/health')
  .then(response => response.json())
  .then(health => {
    console.log('🏥 État SuperSmartMatch:', health.status);
    console.log('🧠 Algorithmes disponibles:', health.algorithms);
  });
```

### 2. Statistiques d'utilisation
```javascript
// Récupérer les statistiques
fetch('http://localhost:5070/api/v1/stats')
  .then(response => response.json())
  .then(stats => {
    console.log('📊 Statistiques globales:', stats);
    console.log('🏆 Algorithme le plus utilisé:', 
      Object.keys(stats.algorithms_stats)
        .sort((a, b) => stats.algorithms_stats[b].calls - stats.algorithms_stats[a].calls)[0]
    );
  });
```

### 3. Comparaison d'algorithmes
```javascript
// Comparer tous les algorithmes sur votre dataset
fetch('http://localhost:5070/api/v1/compare', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    candidate: candidateData,
    jobs: jobsData.slice(0, 10)  // Échantillon pour la comparaison
  })
})
.then(response => response.json())
.then(comparison => {
  console.log('🏁 Résultats de comparaison:', comparison);
  console.log('🥇 Algorithme recommandé:', comparison.recommendation.algorithm);
  
  // Affichage des performances
  Object.entries(comparison.performance_comparison).forEach(([algo, perf]) => {
    console.log(`${algo}: Précision ${perf.avg_score}%, Vitesse rang ${perf.speed_rank}`);
  });
});
```

## 🚀 Optimisations de performance

### 1. Préchargement intelligent
```javascript
// Précharger les algorithmes les plus probables
const preloadAlgorithms = async (candidateProfile) => {
  const recommendation = await fetch('http://localhost:5070/api/v1/recommend-algorithm', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      candidate: candidateProfile,
      jobs: [{id: 1, titre: 'Sample'}]  // Job minimal pour l'analyse
    })
  }).then(r => r.json());
  
  console.log(`🧠 Algorithme recommandé: ${recommendation.recommended_algorithm}`);
  return recommendation.recommended_algorithm;
};
```

### 2. Cache côté client
```javascript
class MatchingCache {
  constructor(ttl = 300000) { // 5 minutes
    this.cache = new Map();
    this.ttl = ttl;
  }
  
  generateKey(candidate, jobs, algorithm) {
    return btoa(JSON.stringify({
      skills: candidate.competences.sort(),
      experience: candidate.annees_experience,
      jobIds: jobs.map(j => j.id).sort(),
      algorithm
    }));
  }
  
  get(candidate, jobs, algorithm) {
    const key = this.generateKey(candidate, jobs, algorithm);
    const cached = this.cache.get(key);
    
    if (cached && Date.now() - cached.timestamp < this.ttl) {
      console.log('💨 Résultat depuis cache client');
      return cached.data;
    }
    
    return null;
  }
  
  set(candidate, jobs, algorithm, data) {
    const key = this.generateKey(candidate, jobs, algorithm);
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }
}

const matchingCache = new MatchingCache();
```

## 🔧 Configuration avancée

### Variables d'environnement pour le front-end
```javascript
// config.js
const API_CONFIG = {
  // URLs des services
  SUPER_SMART_MATCH_URL: process.env.SUPER_SMART_MATCH_URL || 'http://localhost:5070',
  
  // Fallback vers anciens services
  LEGACY_MATCHING_URL: 'http://localhost:5052',
  LEGACY_JOB_ANALYZER_URL: 'http://localhost:5055',
  
  // Options par défaut
  DEFAULT_ALGORITHM: 'auto',
  DEFAULT_LIMIT: 20,
  CACHE_TTL: 300000,
  REQUEST_TIMEOUT: 30000,
  
  // Feature flags
  USE_SUPER_SMART_MATCH: true,
  ENABLE_CLIENT_CACHE: true,
  ENABLE_PERFORMANCE_MONITORING: true
};
```

### Service wrapper complet
```javascript
class SuperSmartMatchService {
  constructor(config = API_CONFIG) {
    this.config = config;
    this.cache = new MatchingCache(config.CACHE_TTL);
  }
  
  async match(candidate, jobs, options = {}) {
    // Vérifier le cache
    const cacheKey = this.generateCacheKey(candidate, jobs, options.algorithm);
    const cached = this.cache.get(cacheKey);
    if (cached) return cached;
    
    // Préparer la requête
    const requestBody = {
      candidate,
      jobs,
      algorithm: options.algorithm || this.config.DEFAULT_ALGORITHM,
      limit: options.limit || this.config.DEFAULT_LIMIT,
      options: {
        performance_priority: options.performance_priority || 'balanced',
        accuracy_priority: options.accuracy_priority || 'high',
        max_processing_time: this.config.REQUEST_TIMEOUT / 1000
      }
    };
    
    try {
      // Appel à SuperSmartMatch
      const response = await fetch(`${this.config.SUPER_SMART_MATCH_URL}/api/v1/match`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(requestBody),
        signal: AbortSignal.timeout(this.config.REQUEST_TIMEOUT)
      });
      
      if (!response.ok) {
        throw new Error(`SuperSmartMatch error: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Mise en cache
      this.cache.set(cacheKey, result);
      
      return result;
      
    } catch (error) {
      console.warn('🔄 SuperSmartMatch failed, using fallback:', error);
      return await this.legacyFallback(candidate, jobs, options);
    }
  }
  
  async legacyFallback(candidate, jobs, options) {
    // Implémentation du fallback vers anciens services
    console.log('🔄 Utilisation des services legacy');
    // ... votre code existant ...
  }
  
  async getRecommendation(candidate, jobs) {
    const response = await fetch(`${this.config.SUPER_SMART_MATCH_URL}/api/v1/recommend-algorithm`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({candidate, jobs})
    });
    
    return await response.json();
  }
  
  async compareAlgorithms(candidate, jobs) {
    const response = await fetch(`${this.config.SUPER_SMART_MATCH_URL}/api/v1/compare`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({candidate, jobs})
    });
    
    return await response.json();
  }
}

// Utilisation
const matchingService = new SuperSmartMatchService();
```

## ✅ Checklist d'intégration

- [ ] SuperSmartMatch ajouté au docker-compose.yml
- [ ] Script start-all-services.sh mis à jour
- [ ] Front-end modifié pour utiliser l'API unifiée
- [ ] Tests d'intégration exécutés
- [ ] Monitoring configuré
- [ ] Documentation mise à jour
- [ ] Formation équipe sur la nouvelle API
- [ ] Plan de rollback préparé

## 🎉 Bénéfices attendus

✅ **Simplification architecture** : 1 service au lieu de 5  
✅ **Performance optimisée** : Sélection automatique du meilleur algorithme  
✅ **Maintenance réduite** : Interface unifiée  
✅ **Évolutivité** : Ajout facile de nouveaux algorithmes  
✅ **Observabilité** : Métriques centralisées  
✅ **Robustesse** : Fallback automatique en cas d'erreur  

---

**🚀 Votre système de matching devient intelligent et unifié !**
