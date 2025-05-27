# SuperSmartMatch - Service Unifié de Matching pour Nexten

SuperSmartMatch est un service backend unifié qui regroupe **TOUS** vos algorithmes de matching sous une seule API moderne et performante. Il simplifie l'intégration avec votre front-end existant et vous permet de choisir le meilleur algorithme selon le contexte.

## 🎯 **Objectifs atteints**

✅ **Service unifié** : Tous les algorithmes accessibles via une seule API  
✅ **Sélection intelligente** : Choix automatique du meilleur algorithme  
✅ **Mode comparaison** : Test de tous les algorithmes simultanément  
✅ **Algorithme hybride** : Combine les résultats pour optimiser la précision  
✅ **Facilité d'intégration** : Compatible avec votre front-end existant  
✅ **Performance optimisée** : Exécution rapide et gestion intelligente des erreurs  

## 🧠 **Algorithmes intégrés**

| Algorithme | Description | Usage recommandé |
|------------|-------------|------------------|
| **`original`** | Algorithme de base avec calculs standards | Tests de référence |
| **`enhanced`** | Moteur amélioré avec pondération dynamique | Usage général recommandé |
| **`smart_match`** | Algorithme bidirectionnel avec géolocalisation | Matching géographique |
| **`custom`** | Votre algorithme personnalisé optimisé | Cas spécifiques |
| **`hybrid`** | Combine tous les algorithmes | Meilleure précision |
| **`auto`** | Sélection intelligente automatique | Mode par défaut |
| **`comparison`** | Exécute tous et compare les résultats | Analyse et debug |

## 🚀 **Installation et démarrage**

### 1. Démarrage rapide
```bash
# Rendre les scripts exécutables
chmod +x start-super-smart-match.sh
chmod +x test-super-smart-match.sh

# Démarrer le service
./start-super-smart-match.sh

# Dans un autre terminal, tester l'API
./test-super-smart-match.sh
```

### 2. Démarrage manuel
```bash
cd super-smart-match
pip install -r requirements.txt
python app.py
```

### 3. Avec Docker
```bash
cd super-smart-match
docker build -t super-smart-match .
docker run -p 5060:5060 super-smart-match
```

Le service sera disponible sur `http://localhost:5060`

## 📡 **API Endpoints**

### **Health Check**
```bash
GET /api/health
```
Vérifie le statut du service et les algorithmes chargés.

### **Liste des algorithmes**
```bash
GET /api/algorithms
```
Retourne la liste des algorithmes disponibles avec leurs descriptions.

### **Matching principal**
```bash
POST /api/match
```

**Body JSON :**
```json
{
  "cv_data": {
    "competences": ["Python", "React", "Django"],
    "annees_experience": 3,
    "formation": "Master Informatique"
  },
  "questionnaire_data": {
    "contrats_recherches": ["CDI"],
    "adresse": "Paris",
    "salaire_souhaite": 50000,
    "mobilite": "hybrid"
  },
  "job_data": [
    {
      "id": 1,
      "titre": "Développeur Full Stack",
      "competences": ["Python", "React", "Django"],
      "type_contrat": "CDI",
      "salaire": "45K-55K€",
      "localisation": "Paris"
    }
  ],
  "algorithm": "auto",
  "limit": 10
}
```

**Paramètres :**
- `algorithm` : `"auto"`, `"enhanced"`, `"hybrid"`, `"comparison"`, etc.
- `limit` : Nombre maximum de résultats (défaut: 10)

## 🔄 **Modes de fonctionnement**

### **Mode AUTO (recommandé)**
```json
{"algorithm": "auto"}
```
Sélectionne automatiquement le meilleur algorithme selon :
- Nombre de compétences du candidat
- Nombre d'offres à analyser
- Présence de données géographiques
- Présence d'informations salariales

### **Mode HYBRID (meilleure précision)**
```json
{"algorithm": "hybrid"}
```
- Exécute plusieurs algorithmes en parallèle
- Combine les résultats avec pondération intelligente
- Ajoute un bonus de consensus
- Optimal pour la précision

### **Mode COMPARISON (analyse)**
```json
{"algorithm": "comparison"}
```
- Exécute TOUS les algorithmes
- Compare les performances et résultats
- Idéal pour l'analyse et le debug
- Retourne des statistiques détaillées

## 🎨 **Intégration avec votre front-end**

### **JavaScript (compatible avec vos pages existantes)**
```javascript
// Exemple d'intégration simple
async function performMatching(cvData, questionnaireData, jobData) {
    const response = await fetch('http://localhost:5060/api/match', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cv_data: cvData,
            questionnaire_data: questionnaireData,
            job_data: jobData,
            algorithm: 'auto',  // Sélection intelligente
            limit: 10
        })
    });
    
    const result = await response.json();
    
    if (result.error) {
        console.error('Erreur de matching:', result.error);
        return [];
    }
    
    console.log(`Algorithme utilisé: ${result.algorithm_used}`);
    console.log(`Temps d'exécution: ${result.execution_time}s`);
    
    return result.results;
}

// Utilisation dans vos pages existantes
// Compatible avec candidate-matching-improved.html
const matchingResults = await performMatching(
    candidateData.cv,
    candidateData.questionnaire,
    availableJobs
);

// Afficher les résultats (votre code existant fonctionne)
displayMatchingResults(matchingResults);
```

### **Modification minimale de vos pages**
Pour intégrer SuperSmartMatch dans vos pages existantes, remplacez simplement l'URL de l'API :

```javascript
// Ancien code
const API_URL = 'http://localhost:5052/api/match';

// Nouveau code avec SuperSmartMatch
const API_URL = 'http://localhost:5060/api/match';
```

## 📊 **Réponses de l'API**

### **Réponse standard**
```json
{
  "algorithm_used": "enhanced",
  "execution_time": 0.142,
  "total_results": 3,
  "results": [
    {
      "id": 1,
      "titre": "Développeur Full Stack",
      "matching_score": 95,
      "matching_details": {
        "skills": 90,
        "contract": 100,
        "location": 85,
        "salary": 95
      }
    }
  ],
  "metadata": {
    "timestamp": 1645789234,
    "candidate_skills_count": 4,
    "jobs_analyzed": 3
  }
}
```

### **Réponse mode HYBRID**
```json
{
  "algorithm_used": "hybrid",
  "results": [
    {
      "matching_score": 87,
      "hybrid_details": {
        "individual_scores": {
          "enhanced": 85,
          "smart_match": 90,
          "original": 82
        },
        "algorithms_used": ["enhanced", "smart_match", "original"],
        "consensus_bonus": 5.2,
        "score_variance": 12.1
      }
    }
  ]
}
```

### **Réponse mode COMPARISON**
```json
{
  "mode": "comparison",
  "total_execution_time": 0.456,
  "best_scoring_algorithm": "enhanced",
  "fastest_algorithm": "original",
  "detailed_results": {
    "enhanced": {
      "average_score": 78.5,
      "execution_time": 0.156,
      "results_count": 3
    },
    "smart_match": {
      "average_score": 75.2,
      "execution_time": 0.234,
      "results_count": 3
    }
  }
}
```

## ⚡ **Performances**

### **Benchmarks typiques**
- **Enhanced** : ~150ms pour 10 offres
- **Smart Match** : ~200ms pour 10 offres  
- **Hybrid** : ~400ms pour 10 offres (précision maximale)
- **Comparison** : ~600ms pour 10 offres (mode debug)

### **Optimisations intégrées**
- Fallback automatique en cas d'erreur
- Gestion intelligente des timeouts
- Cache des calculs coûteux
- Parallélisation pour le mode hybrid

## 🔧 **Configuration avancée**

### **Variables d'environnement**
```bash
export PORT=5060                    # Port du service
export FLASK_ENV=production         # Mode Flask
export PYTHONPATH=/app             # Chemin Python
```

### **Personnalisation des poids (mode HYBRID)**
Les poids par défaut du mode hybrid :
```python
weights = {
    'enhanced': 0.4,      # Algorithme principal
    'custom': 0.3,        # Votre algorithme
    'smart_match': 0.2,   # Géolocalisation
    'original': 0.1       # Référence
}
```

## 🐛 **Dépannage**

### **Problèmes courants**

**1. "Algorithme non disponible"**
```bash
# Vérifier les algorithmes chargés
curl http://localhost:5060/api/algorithms
```

**2. "Erreur d'importation"**
```bash
# Vérifier que les fichiers d'algorithmes sont présents
ls -la matching_engine*.py
```

**3. "Port déjà utilisé"**
```bash
# Changer le port
export PORT=5061
python app.py
```

### **Logs de debug**
```bash
# Activer les logs détaillés
export FLASK_ENV=development
python app.py
```

## 🔄 **Intégration Docker Compose**

Ajoutez SuperSmartMatch à votre `docker-compose.yml` existant :

```yaml
services:
  super-smart-match:
    build: ./super-smart-match
    ports:
      - "5060:5060"
    environment:
      - FLASK_ENV=production
    depends_on:
      - redis
      - postgres
    restart: unless-stopped
    
  # Vos autres services existants...
  cv-parser-service:
    # ...
  job-parser-service:
    # ...
```

## 📈 **Monitoring et métriques**

### **Endpoints de monitoring**
```bash
# Statut de santé
GET /api/health

# Statistiques d'utilisation
GET /api/stats  # (à implémenter)

# Métriques de performance
GET /api/metrics  # (à implémenter)
```

## 🎯 **Roadmap**

### **Version 1.1 (prochaine)**
- [ ] Cache Redis pour améliorer les performances
- [ ] Métriques détaillées et monitoring
- [ ] Interface web d'administration
- [ ] Support des webhooks

### **Version 1.2**
- [ ] Machine Learning pour optimiser la sélection d'algorithmes
- [ ] API GraphQL en complément de REST
- [ ] Support multi-tenant

## 📞 **Support**

- **Documentation** : Ce README
- **Tests** : `./test-super-smart-match.sh`
- **Logs** : Consultez la sortie console du service
- **Issues** : Utilisez les issues GitHub du projet

---

**SuperSmartMatch** unifie enfin tous vos algorithmes de matching sous une API moderne et performante ! 🚀
