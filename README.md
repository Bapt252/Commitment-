# 🎯 Commitment - Plateforme de Matching Emploi

## 📋 Vue d'ensemble

**Commitment** est une plateforme de matching emploi complète avec parsing de CV, questionnaires personnalisés, et intégration Google Maps pour calculer les temps de trajet.

### 🚀 Pages Frontend Déployées

- **📄 Upload CV** : https://bapt252.github.io/Commitment-/templates/candidate-upload.html
- **📝 Questionnaire Candidat** : https://bapt252.github.io/Commitment-/templates/candidate-questionnaire.html  
- **🎯 Interface Matching** : https://bapt252.github.io/Commitment-/templates/candidate-matching-improved.html
- **🏢 Questionnaire Entreprise** : https://bapt252.github.io/Commitment-/templates/client-questionnaire.html
- **💼 Recommandations** : https://bapt252.github.io/Commitment-/templates/candidate-recommendation.html

## 🏗️ Architecture Simplifiée

### Frontend (GitHub Pages)
```
📁 templates/
├── candidate-upload.html           # Upload CV + API OpenAI
├── candidate-questionnaire.html    # Questionnaire 4 sections
├── candidate-matching-improved.html # Interface matching + Maps
├── client-questionnaire.html       # Questionnaire entreprise
└── candidate-recommendation.html   # Recommandations candidats
```

### Backend Services
```
📁 backend/
├── api-matching-enhanced-v2.1-fixed.py        # API principale
├── unified_matching_service.py                # Service unifié
└── matching-service/
    ├── app/core/matching.py                   # Logique matching
    ├── app/services/personalized_matching.py # Personnalisation
    └── app/v2/smart_algorithm_selector.py    # Sélecteur algorithmes
```

### Frontend Assets
```
📁 static/
├── services/
│   ├── app.js                    # Application principale
│   ├── matching-algorithm.js    # Algorithme côté client
│   └── uiEffects.js             # Effets UI
└── js/
    ├── gpt-parser-client.js     # Parser CV principal
    ├── job-storage.js           # Stockage emplois
    └── tracking-sdk.js          # Analytics
```

## 📊 Données Collectées

### Parcours Candidat
1. **Upload CV** + Clé API OpenAI (optionnelle)
2. **Questionnaire** (4 sections) :
   - Informations personnelles
   - Mobilité et préférences  
   - Motivations et secteurs
   - Disponibilité et situation
3. **Matching** avec filtres et Google Maps

### Parcours Entreprise
1. **Questionnaire** (4 sections) :
   - Structure entreprise
   - Informations contact
   - Besoins recrutement + fiche entreprise
   - Confirmation
2. **Recommandations** candidats avec scores

## 🎯 Fonctionnalités Clés

### ✅ Matching Intelligent
- Algorithmes de correspondance avancés
- Scores de compatibilité en temps réel
- Filtres multi-critères

### ✅ Intégration Google Maps
- Calcul automatique des temps de trajet
- Localisation géographique précise
- Optimisation des correspondances par distance

### ✅ Parsing CV Automatique
- Support multiple formats (PDF, DOCX, TXT)
- Extraction automatique des compétences
- Intégration OpenAI pour analyse avancée

### ✅ Interface Utilisateur Moderne
- Design responsive et intuitif
- Progression étape par étape
- Visualisation des résultats de matching

## 🚀 Démarrage Rapide

### 1. Frontend (Déjà déployé)
Les pages sont accessibles directement via GitHub Pages aux URLs mentionnées ci-dessus.

### 2. Backend Local
```bash
# API principale de matching
python api-matching-enhanced-v2.1-fixed.py

# Service unifié
python backend/unified_matching_service.py

# Tests
python -m pytest tests/
```

### 3. Configuration
```bash
# Variables d'environnement
OPENAI_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
DATABASE_URL=your_database_url
```

## 📈 Performance

- **Temps de réponse** : < 2 secondes pour le matching
- **Précision** : Algorithmes optimisés pour la pertinence
- **Compatibilité** : Tous navigateurs modernes
- **Scalabilité** : Architecture microservices

## 🛠️ Technologies

- **Frontend** : HTML5, CSS3, JavaScript ES6+
- **Backend** : Python, FastAPI
- **Base de données** : PostgreSQL avec fonctions de matching
- **APIs** : OpenAI GPT, Google Maps
- **Déploiement** : GitHub Pages (frontend), services cloud (backend)

## 📞 Support

Pour toute question ou problème :
1. Vérifiez la documentation dans le code
2. Testez les pages frontend déployées
3. Consultez les logs des services backend

---

**🎯 Commitment - Matching emploi intelligent et efficace**

*Architecture simplifiée et optimisée pour une expérience utilisateur exceptionnelle.*