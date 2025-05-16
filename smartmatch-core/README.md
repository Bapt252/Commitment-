# SmartMatch Core

Ce module contient l'implémentation de base de l'algorithme SmartMatch pour le matching entre candidats et offres d'emploi.

## Fonctionnalités

- Analyse des compétences avec support des synonymes
- Calcul des temps de trajet (nécessite une clé API Google Maps)
- Matching des niveaux d'expérience et d'éducation
- Analyse des préférences de travail
- Génération d'insights détaillés

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation rapide

```python
from smartmatch import SmartMatcher

# Initialiser le matcher
matcher = SmartMatcher(api_key="votre_clé_api_google_maps")

# Charger vos données
candidate = {
    "id": "c1",
    "name": "Jean Dupont",
    "skills": ["Python", "Django", "JavaScript"],
    "location": "48.8566,2.3522",  # Paris
    "years_of_experience": 5,
    "education_level": "master",
    "remote_work": True,
    "salary_expectation": 65000
}

job = {
    "id": "j1",
    "title": "Développeur Python Senior",
    "required_skills": ["Python", "Django", "SQL"],
    "location": "48.8847,2.2967",  # Levallois-Perret
    "min_years_of_experience": 4,
    "required_education": "bachelor",
    "offers_remote": True,
    "salary_range": {"min": 55000, "max": 75000}
}

# Calculer le match
match_result = matcher.calculate_match(candidate, job)

# Afficher le score global
print(f"Score global: {match_result['overall_score']}")
```

## Intégration API

Pour intégrer SmartMatch dans une API existante:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from smartmatch import SmartMatcher

app = FastAPI()
matcher = SmartMatcher()

class Candidate(BaseModel):
    id: str
    skills: List[str]
    location: str
    years_of_experience: int
    education_level: str
    remote_work: bool = False
    salary_expectation: int = 0

class Job(BaseModel):
    id: str
    required_skills: List[str]
    location: str
    min_years_of_experience: int
    required_education: str
    offers_remote: bool = False
    salary_range: Dict[str, int] = {"min": 0, "max": 0}

@app.post("/api/match")
async def calculate_match(candidate: Candidate, job: Job):
    result = matcher.calculate_match(candidate.dict(), job.dict())
    return result
```

## Structure du projet

- `smartmatch.py` - Implementation de base
- `requirements.txt` - Dépendances
- `api.py` - Exemple d'intégration API
- `example.py` - Exemple d'utilisation
