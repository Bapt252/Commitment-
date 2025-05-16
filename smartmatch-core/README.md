# SmartMatch Core

Ce module contient l'implémentation de l'algorithme SmartMatch pour le matching entre candidats et offres d'emploi, avec une intégration complète des questionnaires candidat et client.

## Fonctionnalités

- **Analyse sémantique des compétences** avec expansion des synonymes pour une meilleure correspondance
- **Calcul du temps de trajet** via Google Maps API pour évaluer la distance entre le candidat et l'entreprise
- **Matching bidirectionnel** prenant en compte les préférences des candidats et les exigences des employeurs
- **Génération d'insights détaillés** pour comprendre les forces et faiblesses de chaque match
- **Intégration des questionnaires** pour une expérience utilisateur complète
- **Prise en compte des préférences de transport** et des temps de trajet maximaux acceptables
- **Analyse des priorités de motivation** des candidats
- **Vérification de la compatibilité des environnements de travail** (open space vs bureau)

## Structure du projet

- `smartmatch.py` - Implémentation de base de l'algorithme SmartMatch
- `smartmatch_extended.py` - Version étendue avec fonctionnalités supplémentaires pour les questionnaires
- `questionnaire_integration.py` - Fonctions de transformation des données des questionnaires
- `integration_example.py` - Exemple d'intégration complète
- `api.py` - API REST pour l'algorithme de base
- `api_extended.py` - API REST étendue avec support des questionnaires

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation des questionnaires

### Intégration du questionnaire candidat

```python
from questionnaire_integration import transform_candidate_questionnaire_to_smartmatch
from smartmatch_extended import create_extended_matcher

# Données du questionnaire candidat (depuis le formulaire HTML)
candidate_questionnaire_data = {
    "full-name": "Jean Dupont",
    "job-title": "Développeur Python",
    "transport-method": ["public-transport", "vehicle"],
    "commute-time-public-transport": "45",
    "office-preference": "openspace",
    "salary-range": "40K€ - 50K€",
    # ...
}

# Transformation en format SmartMatch
candidate = transform_candidate_questionnaire_to_smartmatch(candidate_questionnaire_data)

# Ajouter des données du CV
candidate["skills"] = ["Python", "Django", "JavaScript"]
candidate["years_of_experience"] = 5
candidate["education_level"] = "master"
```

### Intégration du questionnaire client et de la fiche de poste

```python
from questionnaire_integration import transform_client_questionnaire_to_smartmatch

# Données du questionnaire client
client_questionnaire_data = {
    "company-name": "TechSolutions",
    "work-environment": "openspace",
    "sector-list": "tech",
    # ...
}

# Données extraites de la fiche de poste
job_extracted_data = {
    "job-title-value": "Développeur Python Senior",
    "job-skills-value": "Python, Django, REST API",
    "job-salary-value": "45K€ - 55K€",
    # ...
}

# Transformation en format SmartMatch
job = transform_client_questionnaire_to_smartmatch(client_questionnaire_data, job_extracted_data)
```

### Calcul du matching avec intégration complète

```python
# Créer une instance de SmartMatcherExtended
matcher = create_extended_matcher(api_key="votre_clé_api_google_maps")

# Calculer le matching
result = matcher.calculate_match(candidate, job)

# Afficher le score et les insights
print(f"Score global: {result['overall_score']}")
for category, score in result["category_scores"].items():
    print(f"Score {category}: {score}")

for insight in result["insights"]:
    print(f"{insight['category'].upper()}: {insight['message']}")
```

## API REST

L'API étendue offre des endpoints pour l'intégration des questionnaires:

```bash
# Démarrer l'API
python api_extended.py
```

Endpoints disponibles:

- `POST /api/questionnaire/candidate/transform` - Transformer les données du questionnaire candidat
- `POST /api/questionnaire/client/transform` - Transformer les données du questionnaire client et de la fiche de poste
- `POST /api/questionnaire/match` - Calculer le matching directement à partir des questionnaires

Exemple d'utilisation avec cURL:

```bash
curl -X POST \
  http://localhost:5052/api/questionnaire/match \
  -H "Content-Type: application/json" \
  -d '{"candidate_questionnaire": {...}, "client_questionnaire": {...}, "job_data": {...}, "cv_data": {...}}'
```

## Exemples

Consultez le fichier `integration_example.py` pour des exemples complets d'utilisation.

## Personnalisation

Vous pouvez personnaliser les pondérations des différents facteurs dans `smartmatch_extended.py`:

```python
extended_weights = {
    "skills": 0.35,            
    "location": 0.20,          
    "experience": 0.15,        
    "education": 0.10,         
    "preferences": 0.10,       
    "environment": 0.05,       
    "commute_preference": 0.05 
}
```
