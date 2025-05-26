# 🚀 SuperSmartMatch - Service Unifié de Matching

SuperSmartMatch est le service backend unifié qui regroupe TOUS les algorithmes de matching de Nexten sous une seule API puissante et flexible.

## 🌟 Caractéristiques

- **🔄 Multi-algorithmes** : Regroupe SmartMatch, Enhanced, Semantic, Job Analyzer et Compare
- **🎯 Auto-sélection** : Choisit automatiquement le meilleur algorithme selon les données
- **⚡ Performance** : Optimisé pour des résultats rapides et précis
- **🔌 Plug & Play** : Intégration directe avec votre front-end existant
- **📊 Analytics** : Suivi des performances et comparaisons en temps réel

## 🏗️ Architecture

```
SuperSmartMatch/
├── core/
│   ├── __init__.py
│   ├── engine.py           # Moteur principal
│   ├── selector.py         # Sélecteur d'algorithme
│   └── unified_api.py      # API unifiée
├── algorithms/
│   ├── __init__.py
│   ├── smart_match.py      # Algorithme SmartMatch
│   ├── enhanced.py         # Enhanced Matching Engine
│   ├── semantic.py         # Analyseur sémantique
│   ├── job_analyzer.py     # Job Analyzer
│   └── comparator.py       # Comparateur d'algorithmes
├── utils/
│   ├── __init__.py
│   ├── data_adapter.py     # Adaptateur de données
│   ├── performance.py      # Monitoring performances
│   └── fallback.py         # Gestion des fallbacks
├── api/
│   ├── __init__.py
│   ├── app.py             # Application Flask
│   ├── routes.py          # Routes API
│   └── middleware.py      # Middleware
├── tests/
├── docs/
└── requirements.txt
```

## 🚀 Démarrage Rapide

### Installation

```bash
cd super-smart-match
pip install -r requirements.txt
```

### Configuration

```bash
# Variables d'environnement
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_MAPS_API_KEY="your-google-maps-key"
export SUPER_SMART_MATCH_MODE="auto"  # auto, smart-match, enhanced, hybrid, comparison
```

### Lancement

```bash
python -m api.app
```

## 🎮 Utilisation

### API Endpoints

#### 1. Match Unifié
```http
POST /api/v1/match
Content-Type: application/json

{
  "candidat": {
    "competences": ["Python", "React"],
    "adresse": "Paris",
    "mobilite": "hybrid",
    "annees_experience": 3,
    "salaire_souhaite": 50000,
    "contrats_recherches": ["CDI"],
    "disponibilite": "immediate"
  },
  "offres": [
    {
      "titre": "Développeur Full Stack",
      "competences": ["Python", "React"],
      "localisation": "Paris",
      "type_contrat": "CDI",
      "salaire": "45K-55K€",
      "politique_remote": "hybrid"
    }
  ],
  "options": {
    "algorithme": "auto",  // auto, smart-match, enhanced, hybrid, comparison
    "limite": 10,
    "seuil_minimum": 60,
    "details": true
  }
}
```

#### 2. Comparaison d'Algorithmes
```http
POST /api/v1/compare
```

#### 3. Analyse de Performance
```http
GET /api/v1/performance
```

### Format de Réponse

```json
{
  "status": "success",
  "algorithme_utilise": "enhanced",
  "temps_execution": 0.234,
  "resultats": [
    {
      "id": "job_1",
      "titre": "Développeur Full Stack",
      "score_global": 87,
      "scores_details": {
        "competences": 92,
        "localisation": 85,
        "salaire": 80,
        "contrat": 95,
        "experience": 88
      },
      "explications": {
        "competences": "Excellente correspondance des compétences techniques",
        "localisation": "Proche de votre domicile (15 min)",
        "recommandation": "Candidature fortement recommandée"
      },
      "confiance": 0.89
    }
  ],
  "meta": {
    "total_offres": 1,
    "algorithmes_testes": ["enhanced", "smart-match"],
    "performance": {
      "precision": 0.87,
      "rappel": 0.82
    }
  }
}
```

## 🧠 Algorithmes Intégrés

### 1. **Auto** (Recommandé)
- Sélection intelligente du meilleur algorithme
- Analyse des données d'entrée
- Optimization automatique des performances

### 2. **SmartMatch**
- Matching bidirectionnel avec géolocalisation
- Intégration Google Maps
- Gestion des préférences de télétravail

### 3. **Enhanced**
- Pondération dynamique basée sur les préférences
- Support des soft skills et culture d'entreprise
- Explications détaillées

### 4. **Semantic**
- Analyse sémantique des compétences
- Correspondance intelligente au-delà des mots-clés
- Support WordNet

### 5. **Hybrid**
- Combine plusieurs algorithmes
- Agrégation pondérée des scores
- Meilleure précision

### 6. **Comparison**
- Teste tous les algorithmes
- Analyse comparative des performances
- Recommandations d'optimisation

## 🔧 Configuration Avancée

### Poids des Algorithmes (Mode Hybrid)

```python
HYBRID_WEIGHTS = {
    "smart_match": 0.3,
    "enhanced": 0.4,
    "semantic": 0.3
}
```

### Seuils de Sélection Auto

```python
AUTO_SELECTION_RULES = {
    "smart_match": {
        "condition": "has_geolocation and has_remote_preferences",
        "weight": 0.8
    },
    "enhanced": {
        "condition": "has_soft_skills or has_culture_preferences",
        "weight": 0.9
    },
    "semantic": {
        "condition": "complex_skills_matching_needed",
        "weight": 0.7
    }
}
```

## 📊 Monitoring et Analytics

### Métriques Suivies

- **Performance** : Temps d'exécution, mémoire utilisée
- **Qualité** : Scores de précision, rappel, F1-score
- **Usage** : Algorithmes les plus utilisés, taux de succès
- **Erreurs** : Taux d'échec, types d'erreurs

### Dashboard

Accédez au dashboard de monitoring : `http://localhost:5000/dashboard`

## 🔌 Intégration Front-end

### JavaScript Client

```javascript
// Client SuperSmartMatch
class SuperSmartMatchClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
    }
    
    async match(candidat, offres, options = {}) {
        const response = await fetch(`${this.baseUrl}/api/v1/match`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidat, offres, options })
        });
        return response.json();
    }
    
    async compareAlgorithms(candidat, offres) {
        const response = await fetch(`${this.baseUrl}/api/v1/compare`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ candidat, offres })
        });
        return response.json();
    }
}

// Usage
const client = new SuperSmartMatchClient();
const results = await client.match(candidateData, jobsData, {
    algorithme: 'auto',
    details: true
});
```

### Intégration avec votre Front-end Existant

Remplacez simplement votre endpoint actuel :

```javascript
// Avant
const response = await fetch('/api/match', { ... });

// Après
const response = await fetch('/api/v1/match', { ... });
```

## 🧪 Tests

```bash
# Tests unitaires
python -m pytest tests/

# Tests d'intégration
python -m pytest tests/integration/

# Tests de performance
python -m pytest tests/performance/

# Tests avec données réelles
python scripts/test_with_real_data.py
```

## 🔧 Développement

### Ajouter un Nouvel Algorithme

1. Créez `algorithms/mon_algorithme.py`
2. Implémentez l'interface `BaseAlgorithm`
3. Ajoutez-le au sélecteur dans `core/selector.py`
4. Ajoutez les tests correspondants

### Structure d'un Algorithme

```python
from core.base import BaseAlgorithm

class MonAlgorithme(BaseAlgorithm):
    def __init__(self):
        super().__init__()
        self.name = "mon_algorithme"
        
    def calculate_match(self, candidat, offre):
        # Votre logique ici
        return {
            "score": 85,
            "details": {...},
            "explications": {...}
        }
        
    def supports(self, candidat, offre):
        # Vérifier si l'algorithme peut traiter ces données
        return True
```

## 📈 Roadmap

- [x] **v1.0** : Service unifié de base
- [x] **v1.1** : Sélection automatique d'algorithme
- [ ] **v1.2** : Machine Learning pour l'optimisation
- [ ] **v1.3** : Support multi-langues
- [ ] **v1.4** : API GraphQL
- [ ] **v2.0** : Algorithmes d'apprentissage adaptatif

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

**SuperSmartMatch** - Le futur du matching intelligent pour Nexten 🚀
