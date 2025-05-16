# Guide de Tests pour SmartMatch

Ce document explique comment tester l'algorithme SmartMatch dans le projet Commitment.

## Prérequis

- Python 3.11+
- Environnement virtuel activé
- Packages requis installés:
  ```
  pip install flask-pydantic
  ```

## Tests disponibles

Deux types de tests sont disponibles:

1. **Tests Fonctionnels** - Démontrent le fonctionnement de base de SmartMatch avec des exemples concrets
2. **Tests Unitaires** - Vérifient le bon fonctionnement de toutes les fonctionnalités de SmartMatch

## Exécution des tests

Nous avons créé un script shell pour simplifier l'exécution des tests:

```bash
# Rendre le script exécutable
chmod +x run_smartmatch_tests.sh

# Exécuter les tests fonctionnels (par défaut)
./run_smartmatch_tests.sh

# Exécuter les tests unitaires
./run_smartmatch_tests.sh unit
```

## Exécution manuelle des tests

Vous pouvez également exécuter les tests directement avec Python:

```bash
# Tests fonctionnels
python test_functional.py

# Tests unitaires
python test_smartmatch_unit_fixed.py
```

## Utilisation de SmartMatch dans votre code

Voici comment utiliser SmartMatch dans votre propre code:

```python
from app.smartmatch import SmartMatcher

# Initialisation
matcher = SmartMatcher(api_key="votre_clé_api_google_maps")  # La clé API est optionnelle

# Charger des données
test_data = matcher.load_test_data()  # Données de test incluses
candidates = test_data["candidates"]
jobs = test_data["jobs"]

# OU utiliser vos propres données
mon_candidat = {
    "id": "c123",
    "name": "Nom Prénom",
    "skills": ["Python", "Flask", "SQL"],
    "location": "48.8566,2.3522",  # Paris (format latitude,longitude)
    "years_of_experience": 4,
    "education_level": "master",
    "remote_work": True,
    "salary_expectation": 60000,
    "job_type": "full_time"
}

mon_job = {
    "id": "j456",
    "title": "Développeur Backend",
    "required_skills": ["Python", "SQL"],
    "preferred_skills": ["Flask", "Docker"],
    "location": "48.8847,2.2967",  # Levallois-Perret
    "min_years_of_experience": 3,
    "required_education": "bachelor",
    "offers_remote": True,
    "salary_range": {"min": 50000, "max": 70000},
    "job_type": "full_time"
}

# Calcul du matching
match_result = matcher.calculate_match(mon_candidat, mon_job)

# Accès aux résultats
score_global = match_result["overall_score"]
score_compétences = match_result["category_scores"]["skills"]
score_localisation = match_result["category_scores"]["location"]
insights = match_result["insights"]

# Matching par lots
batch_results = matcher.batch_match([candidat1, candidat2], [job1, job2, job3])
```

## Configuration de l'API Google Maps

Si vous souhaitez utiliser le calcul de temps de trajet, vous devez configurer une clé API Google Maps:

```bash
# Via variable d'environnement
export GOOGLE_MAPS_API_KEY="votre_clé_api_google_maps"

# OU directement lors de l'initialisation
matcher = SmartMatcher(api_key="votre_clé_api_google_maps")
```

Sans clé API, les calculs de distance seront désactivés et un score neutre (0.5) sera attribué pour la correspondance de localisation.

## Dépannage

1. **ImportError**: Assurez-vous d'exécuter les tests depuis le répertoire `matching-service`.

2. **Erreurs API Google Maps**: Si vous voyez "REQUEST_DENIED", c'est normal sans clé API valide.

3. **Échecs de tests**: Si les tests unitaires échouent, vérifiez que vos dépendances sont à jour:
   ```
   pip install -r requirements.txt
   ```