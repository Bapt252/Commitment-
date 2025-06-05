# 🚀 Guide d'Intégration Frontend - SuperSmartMatch V2

## ✅ APIs Fonctionnelles Prêtes

### 📊 **Status des Services (Mis à jour)**
- ✅ **Job Parser** - Port 5053 - Documentation FastAPI disponible
- ✅ **Matching Service** - Port 5052 - API REST opérationnelle  
- ✅ **Grafana** - Port 3001 - Monitoring complet
- ✅ **Prometheus** - Port 9090 - Métriques temps réel
- ⚠️ **CV Parser** - Port 5051 - Endpoints à corriger
- ❌ **Gateway** - Port 5050 - Service non démarré

---

## 🔗 **Configuration Frontend**

### **Configuration JavaScript/TypeScript**
```javascript
const API_CONFIG = {
  // Services fonctionnels
  JOB_PARSER: 'http://localhost:5053',
  MATCHING_SERVICE: 'http://localhost:5052',
  GRAFANA: 'http://localhost:3001',
  PROMETHEUS: 'http://localhost:9090',
  
  // Endpoints de santé
  HEALTH_CHECKS: {
    jobParser: '/health',
    matching: '/health',
    grafana: '/api/health'
  },
  
  // Documentation auto-générée
  JOB_PARSER_DOCS: '/docs',
  JOB_PARSER_SCHEMA: '/openapi.json'
};
```

---

## 💼 **Job Parser API**

### **Endpoints Disponibles**
- 📖 **Documentation FastAPI :** `http://localhost:5053/docs`
- 🔍 **Schema JSON :** `http://localhost:5053/openapi.json`
- ❤️ **Health Check :** `http://localhost:5053/health`

### **Exemples d'Utilisation**

#### **1. Vérifier la santé du service**
```javascript
const checkJobParserHealth = async () => {
  try {
    const response = await fetch('http://localhost:5053/health');
    const health = await response.json();
    console.log('Job Parser Status:', health);
    return response.ok;
  } catch (error) {
    console.error('Job Parser unreachable:', error);
    return false;
  }
};
```

#### **2. Explorer les endpoints disponibles**
```javascript
const getJobParserSchema = async () => {
  try {
    const response = await fetch('http://localhost:5053/openapi.json');
    const schema = await response.json();
    
    // Voir tous les endpoints disponibles
    const endpoints = Object.keys(schema.paths);
    console.log('Available endpoints:', endpoints);
    
    return schema;
  } catch (error) {
    console.error('Cannot fetch schema:', error);
  }
};
```

#### **3. Parser une offre d'emploi (une fois les endpoints identifiés)**
```javascript
const parseJobDescription = async (jobData) => {
  try {
    // Endpoint à confirmer via la documentation FastAPI
    const response = await fetch('http://localhost:5053/api/parse-job', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        job_description: jobData.description,
        company_info: jobData.company,
        requirements: jobData.requirements
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Job parsing error:', error);
    throw error;
  }
};
```

---

## 🎯 **Matching Service API**

### **Endpoints Identifiés**
- ❤️ **Health Check :** `http://localhost:5052/health` ✅
- 🎯 **Matching :** `http://localhost:5052/api/match` (HTTP 405 - méthode à corriger)

### **Tests et Utilisation**

#### **1. Vérifier la santé**
```javascript
const checkMatchingHealth = async () => {
  const response = await fetch('http://localhost:5052/health');
  return response.json();
};
```

#### **2. Explorer le service**
```javascript
const exploreMatchingService = async () => {
  // Test du root endpoint
  const rootResponse = await fetch('http://localhost:5052/');
  const rootData = await rootResponse.json();
  console.log('Matching service info:', rootData);
  
  // Test différentes méthodes sur /api/match
  const methods = ['GET', 'POST', 'PUT'];
  for (const method of methods) {
    try {
      const response = await fetch('http://localhost:5052/api/match', {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: method !== 'GET' ? JSON.stringify({test: 'data'}) : undefined
      });
      console.log(`${method} /api/match:`, response.status, response.statusText);
    } catch (error) {
      console.error(`${method} failed:`, error);
    }
  }
};
```

#### **3. Effectuer un matching (une fois la méthode HTTP correcte identifiée)**
```javascript
const performMatching = async (cvData, jobData) => {
  try {
    const response = await fetch('http://localhost:5052/api/match', {
      method: 'POST', // ou GET selon ce qui fonctionne
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        cv_data: cvData,
        job_data: jobData
      })
    });
    
    const matchResult = await response.json();
    return matchResult;
  } catch (error) {
    console.error('Matching error:', error);
    throw error;
  }
};
```

---

## 📊 **Grafana Integration**

### **Configuration**
- 🌐 **URL :** `http://localhost:3001`
- 👤 **Credentials :** `admin` / `admin123`
- 🔌 **API :** `http://localhost:3001/api/`

### **Utilisation**

#### **1. Authentification**
```javascript
const grafanaAuth = {
  username: 'admin',
  password: 'admin123'
};

const checkGrafanaHealth = async () => {
  const response = await fetch('http://localhost:3001/api/health', {
    headers: {
      'Authorization': 'Basic ' + btoa(`${grafanaAuth.username}:${grafanaAuth.password}`)
    }
  });
  return response.json();
};
```

#### **2. Récupérer les métriques**
```javascript
const getGrafanaDashboards = async () => {
  const response = await fetch('http://localhost:3001/api/search', {
    headers: {
      'Authorization': 'Basic ' + btoa(`${grafanaAuth.username}:${grafanaAuth.password}`)
    }
  });
  return response.json();
};
```

---

## 📈 **Prometheus Integration**

### **Métriques Disponibles**
```javascript
const getPrometheusMetrics = async () => {
  // Lister toutes les métriques
  const metricsResponse = await fetch('http://localhost:9090/api/v1/label/__name__/values');
  const metrics = await metricsResponse.json();
  
  // Voir les targets monitorées
  const targetsResponse = await fetch('http://localhost:9090/api/v1/targets');
  const targets = await targetsResponse.json();
  
  return { metrics: metrics.data, targets: targets.data };
};

const queryPrometheus = async (query) => {
  const response = await fetch(`http://localhost:9090/api/v1/query?query=${encodeURIComponent(query)}`);
  return response.json();
};
```

---

## 🧪 **Script de Test Complet**

### **Télécharger et Exécuter**
```bash
# Récupérer le script de test
git pull
chmod +x test_working_apis.sh
./test_working_apis.sh
```

### **Tests Frontend**
```javascript
// Test complet de connectivité
const testAllServices = async () => {
  const results = {
    jobParser: await checkJobParserHealth(),
    matching: await checkMatchingHealth(), 
    grafana: await checkGrafanaHealth(),
    prometheus: await fetch('http://localhost:9090').then(r => r.ok)
  };
  
  console.log('Services Status:', results);
  return results;
};

// Workflow de test du parcours complet
const testJobMatchingWorkflow = async () => {
  // 1. Explorer la documentation Job Parser
  const schema = await getJobParserSchema();
  
  // 2. Identifier les endpoints de parsing
  const parseEndpoints = Object.keys(schema.paths).filter(path => 
    path.includes('parse') || path.includes('job')
  );
  
  // 3. Tester le matching service
  await exploreMatchingService();
  
  // 4. Vérifier les métriques
  const metrics = await getPrometheusMetrics();
  
  return { schema, parseEndpoints, metrics };
};
```

---

## 🚀 **Prochaines Étapes**

### **Immédiatement Disponible**
1. ✅ **Ouvrir la doc Job Parser :** http://localhost:5053/docs
2. ✅ **Tester les APIs :** `./test_working_apis.sh`
3. ✅ **Configurer le monitoring :** Grafana + Prometheus
4. ✅ **Commencer l'intégration** avec les services fonctionnels

### **À Résoudre**
1. 🔧 **CV Parser :** Identifier les endpoints corrects
2. 🔧 **Gateway :** Démarrer le service API Gateway  
3. 🔧 **Matching :** Corriger la méthode HTTP

### **Workflow Recommandé**
1. **Phase 1 :** Intégrer Job Parser + Matching (fonctionnels)
2. **Phase 2 :** Ajouter CV Parser une fois corrigé
3. **Phase 3 :** Utiliser Gateway pour unifier les APIs
4. **Phase 4 :** Optimiser avec monitoring avancé

---

## 📞 **Support**

- 📖 **Documentation Job Parser :** http://localhost:5053/docs
- 📊 **Monitoring :** http://localhost:3001 (admin/admin123)
- 🔧 **Tests :** `./test_working_apis.sh`

**🎯 Vous pouvez commencer l'intégration frontend dès maintenant avec les services fonctionnels !**