# SmartMatch Data Adapter

Ce service adapte les données entre les formats de sortie du CV Parser et du Job Parser vers le format attendu par l'algorithme de matching SmartMatch.

## Fonctionnalités

- Adaptation des données du CV Parser → format SmartMatch
- Adaptation des données du Job Parser → format SmartMatch
- Enrichissement des données avec des informations supplémentaires
- Support pour le traitement par lots
- API RESTful pour une intégration facile
- **Nouveau:** Intégration des questionnaires candidat et entreprise

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
| POST | `/api/adapter/enrich-cv-with-questionnaire` | **Nouveau:** Enrichir un CV avec les données du questionnaire |
| POST | `/api/adapter/enrich-job-with-questionnaire` | **Nouveau:** Enrichir une offre d'emploi avec les données du questionnaire |
| POST | `/api/adapter/smart-match` | **Nouveau:** Matching avancé tenant compte des questionnaires |

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

### Nouveau: Enrichir un CV avec les données du questionnaire

```bash
curl -X POST http://localhost:5053/api/adapter/enrich-cv-with-questionnaire \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
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
    "questionnaire_data": {
      "transport-method": ["public-transport", "bike"],
      "commute-time-public-transport": "45",
      "commute-time-bike": "30",
      "address": "123 rue de Paris, 75001 Paris",
      "office-preference": "open-space",
      "motivation-order": "remuneration,evolution,flexibility,location,other",
      "structure-type": ["startup", "pme"],
      "salary-range": "45K - 55K"
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
- **Questionnaires**: pour enrichir les données avec les préférences personnalisées

## Personnalisation

Le comportement de l'adaptateur peut être ajusté en modifiant:
- Les mappings d'éducation et de contrat dans `smartmatch_data_adapter.py`
- Les extracteurs d'informations (salaire, expérience, etc.)
- La façon dont les compétences sont séparées entre requises et préférées
- Les poids des différents critères dans le calcul du score de matching

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

# Enrichir avec les données de questionnaire
questionnaire_data = {
    "transport-method": ["public-transport"],
    # ...
}
enriched_cv = adapter.enrich_cv_data_with_questionnaire(cv_smartmatch, questionnaire_data)

# Utiliser les données adaptées avec l'algorithme de matching avancé
match_result = adapter.enhanced_match(enriched_cv, job_smartmatch)
```

## Documentation détaillée

Pour plus d'informations sur l'intégration des questionnaires, consultez le document [QUESTIONNAIRE_INTEGRATION.md](./QUESTIONNAIRE_INTEGRATION.md).
