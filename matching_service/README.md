# Service de Matching Nexten SmartMatch

Ce service fournit une API REST pour le matching bidirectionnel entre candidats et entreprises, en utilisant les données issues des services de parsing de CV et de fiches de poste.

## Structure du service

- `app/adapters/parsing_adapter.py` : Adaptateur pour convertir les données parsées au format attendu par SmartMatch
- `app/adapters/matching_pipeline.py` : Pipeline d'intégration pour le processus de matching complet
- `app/adapters/matching_api.py` : API REST pour exposer les fonctionnalités de matching

## Démarrage du service

```bash
# Démarrer le service avec les paramètres par défaut
python run_matching_api.py

# Spécifier les URLs des services de parsing
python run_matching_api.py --cv-parser-url http://localhost:5051 --job-parser-url http://localhost:5055

# Spécifier le port d'écoute
python run_matching_api.py --port 5052

# Activer le mode debug
python run_matching_api.py --debug
```

## API REST

### Points de terminaison

- `GET /health` : Vérifier la santé du service
- `POST /match` : Lancer un matching complet entre tous les CVs et fiches de poste
- `GET /match/cv/{cv_id}/job/{job_id}` : Lancer un matching spécifique entre un CV et une fiche de poste
- `GET /match/cv/{cv_id}/all` : Lancer un matching entre un CV et toutes les fiches de poste
- `GET /match/job/{job_id}/all` : Lancer un matching entre une fiche de poste et tous les CVs
- `GET /match/results` : Récupérer tous les résultats de matching
- `GET /match/insights` : Récupérer tous les insights générés

### Exemples d'utilisation

```bash
# Vérifier la santé du service
curl http://localhost:5052/health

# Lancer un matching complet
curl -X POST http://localhost:5052/match

# Lancer un matching spécifique
curl http://localhost:5052/match/cv/cand_1/job/job_1

# Lancer un matching entre un CV et toutes les fiches de poste
curl http://localhost:5052/match/cv/cand_1/all

# Lancer un matching entre une fiche de poste et tous les CVs
curl http://localhost:5052/match/job/job_1/all

# Récupérer tous les résultats de matching
curl http://localhost:5052/match/results

# Récupérer tous les insights générés
curl http://localhost:5052/match/insights
```

## Intégration avec les services de parsing

Le service de matching s'intègre avec :

1. **Service de parsing de CV** (port 5051) :
   - Points de terminaison utilisés :
     - `GET /api/cvs` : Récupérer tous les CVs parsés
     - `GET /api/cv/{cv_id}` : Récupérer un CV spécifique

2. **Service de parsing de fiches de poste** (port 5055) :
   - Points de terminaison utilisés :
     - `GET /api/jobs` : Récupérer toutes les fiches de poste parsées
     - `GET /api/job/{job_id}` : Récupérer une fiche de poste spécifique

## Configuration

Les variables d'environnement suivantes peuvent être utilisées pour configurer le service :

- `CV_PARSER_URL` : URL du service de parsing de CV (défaut: http://localhost:5051)
- `JOB_PARSER_URL` : URL du service de parsing de fiches de poste (défaut: http://localhost:5055)
- `MATCHING_RESULTS_DIR` : Répertoire pour stocker les résultats (défaut: matching_results)
- `GOOGLE_MAPS_API_KEY` : Clé API Google Maps pour le calcul des temps de trajet
