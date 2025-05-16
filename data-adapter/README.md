# SmartMatch Data Adapter

Ce service adapte les données entre les formats de sortie du CV Parser et du Job Parser vers le format attendu par l'algorithme de matching SmartMatch.

## Fonctionnalités

- Adaptation des données du CV Parser → format SmartMatch
- Adaptation des données du Job Parser → format SmartMatch
- Enrichissement des données avec des informations supplémentaires
- Support pour le traitement par lots
- API RESTful pour une intégration facile

## Installation rapide

```bash
# Rendre le script de démarrage exécutable
chmod +x start-smartmatch-adapter.sh

# Démarrer le service
./start-smartmatch-adapter.sh
```

## Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/adapter/health` | Vérifier la disponibilité du service |
| POST | `/api/adapter/adapt-cv` | Adapter un CV au format SmartMatch |
| POST | `/api/adapter/adapt-job` | Adapter une offre d'emploi au format SmartMatch |
| POST | `/api/adapter/batch-adapt-cv` | Adapter plusieurs CVs au format SmartMatch |
| POST | `/api/adapter/batch-adapt-job` | Adapter plusieurs offres d'emploi au format SmartMatch |
| POST | `/api/adapter/match` | Adapter les données puis lancer le matching |

## Exemples d'utilisation

### Adapter un CV

```bash
curl -X POST http://localhost:5053/api/adapter/adapt-cv \
  -H "Content-Type: application/json" \
  -d '{
    "nom": "Dupont",
    "prenom": "Jean",
    "poste": "Développeur Python Senior",
    "competences": ["Python", "Django", "Flask"],
    "logiciels": ["Git", "Docker"],
    "soft_skills": ["Communication", "Travail d'équipe"],
    "email": "jean.dupont@example.com",
    "telephone": "06 12 34 56 78",
    "adresse": "Paris"
  }'
```

### Adapter une offre d'emploi

```bash
curl -X POST http://localhost:5053/api/adapter/adapt-job \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Développeur Python Senior",
    "company": "Acme Inc.",
    "location": "Paris",
    "contract_type": "CDI",
    "skills": ["Python", "Django", "Flask", "SQL", "Git"],
    "experience": "5 ans",
    "education": "Master",
    "salary": "45K - 55K"
  }'
```

### Faire un matching

```bash
curl -X POST http://localhost:5053/api/adapter/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv": {
      "nom": "Dupont",
      "prenom": "Jean",
      "poste": "Développeur Python Senior",
      "competences": ["Python", "Django", "Flask"],
      "logiciels": ["Git", "Docker"],
      "soft_skills": ["Communication", "Travail d'équipe"],
      "email": "jean.dupont@example.com",
      "telephone": "06 12 34 56 78",
      "adresse": "Paris"
    },
    "job": {
      "title": "Développeur Python Senior",
      "company": "Acme Inc.",
      "location": "Paris",
      "contract_type": "CDI",
      "skills": ["Python", "Django", "Flask", "SQL", "Git"],
      "experience": "5 ans",
      "education": "Master",
      "salary": "45K - 55K"
    }
  }'
```

## Architecture

L'adaptateur est construit avec:
- **Flask**: pour l'API RESTful
- **NLTK**: pour l'analyse de texte et l'extraction d'informations
- **scikit-learn**: pour les algorithmes de vectorisation et de similarité

Le service s'intègre dans l'infrastructure Docker existante et communique avec:
- **CV Parser**: pour récupérer et adapter les données des CVs
- **Job Parser**: pour récupérer et adapter les données des offres d'emploi
- **Matching Service**: pour envoyer les données adaptées à l'algorithme de matching

## Personnalisation

Le comportement de l'adaptateur peut être ajusté en modifiant:
- Les mappings d'éducation et de contrat dans `smartmatch_data_adapter.py`
- Les extracteurs d'informations (salaire, expérience, etc.)
- La façon dont les compétences sont séparées entre requises et préférées

## Intégration dans votre code

Pour utiliser l'adaptateur dans votre propre code Python:

```python
from smartmatch_data_adapter import SmartMatchDataAdapter

# Initialiser l'adaptateur
adapter = SmartMatchDataAdapter()

# Adapter un CV
cv_data = {
    "nom": "Dupont",
    "prenom": "Jean",
    # ...
}
cv_smartmatch = adapter.cv_to_smartmatch_format(cv_data)

# Adapter une offre d'emploi
job_data = {
    "title": "Développeur Python Senior",
    # ...
}
job_smartmatch = adapter.job_to_smartmatch_format(job_data)

# Utiliser les données adaptées avec l'algorithme de matching
# ...
```
