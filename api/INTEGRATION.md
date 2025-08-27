# Intégration de l'API avec le Frontend Commitment

Ce document explique comment intégrer l'API backend avec le frontend existant pour rendre la Phase 5 (API et intégration) pleinement fonctionnelle.

## Architecture

L'architecture d'intégration est simple :

```
Commitment Project
├── static/
│   └── scripts/
│       ├── document-parser.js  (Frontend - Points vers l'API)
│       └── job-description-parser.js (Frontend - Utilise les données analysées)
└── api/
    ├── app/  (Backend FastAPI)
    └── requirements.txt
```

Le frontend est déjà configuré pour utiliser l'API via le fichier `static/scripts/document-parser.js`, qui pointe vers `http://localhost:8000`.

## Installation et lancement

1. **Installer les dépendances backend** :
   ```bash
   cd api
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate sur Windows
   pip install -r requirements.txt
   ```

2. **Lancer l'API backend** :
   ```bash
   cd api
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Vérifier que l'API fonctionne** :
   Ouvrez http://localhost:8000 dans votre navigateur. Vous devriez voir un message de bienvenue.
   
   La documentation interactive est disponible sur http://localhost:8000/docs

## Tests d'intégration

Pour tester l'intégration frontend-backend :

1. Lancer l'API backend (instructions ci-dessus)
2. Ouvrir votre page frontend `templates/job-description-parser.html` dans un navigateur
3. Essayer d'analyser une fiche de poste (texte ou fichier)
4. Vérifier que le frontend affiche correctement les résultats d'analyse

## Modifications nécessaires pour un déploiement en production

Pour déployer en production :

1. Modifier l'URL de l'API dans `static/scripts/document-parser.js` :
   ```javascript
   // Remplacer cette ligne
   const API_BASE_URL = 'http://localhost:8000/api/v1';
   
   // Par l'URL de production
   const API_BASE_URL = 'https://votre-domaine.com/api/v1';
   ```

2. Configurer le backend API en production :
   ```bash
   cd api
   gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. Mettre en place un serveur Nginx comme proxy inverse pour servir à la fois le frontend et rediriger les requêtes API.

## Détails techniques

L'API expose deux endpoints principaux :

1. **POST /api/v1/jobs/parse** - Analyse le texte d'une fiche de poste
   - Corps de la requête : `{ "text": "Contenu de la fiche de poste..." }`
   - Réponse : Structure JSON avec les données extraites

2. **POST /api/v1/jobs/parse-file** - Analyse un fichier de fiche de poste
   - Corps de la requête : Formulaire multipart avec un champ `file`
   - Réponse : Même structure JSON que l'endpoint de texte

Ces endpoints retournent exactement le format attendu par le frontend existant.