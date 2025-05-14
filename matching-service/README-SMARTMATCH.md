# Nexten SmartMatch: Matching bidirectionnel avancé

Ce module implémente un système avancé de matching bidirectionnel pour mettre en relation les candidats et les offres d'emploi.

## Caractéristiques

- **Analyse sémantique des compétences** avec expansion des synonymes pour une meilleure correspondance
- **Calcul du temps de trajet** via l'API Google Maps pour évaluer la distance entre le candidat et l'entreprise
- **Matching bidirectionnel** prenant en compte les préférences des candidats et les exigences des employeurs
- **Génération d'insights détaillés** pour comprendre les forces et faiblesses de chaque match
- **Visualisations** des résultats avec graphiques radar, comparaisons et heatmaps

## Installation

Toutes les dépendances nécessaires sont incluses dans le fichier `requirements.txt` du service de matching.

```bash
pip install -r requirements.txt
```

## Configuration

Pour utiliser les fonctionnalités complètes de SmartMatch, vous devez configurer une clé API Google Maps pour les calculs de distance:

1. Récupérez une clé API Google Maps avec accès à l'API Distance Matrix
2. Définissez-la comme variable d'environnement:
   ```bash
   export GOOGLE_MAPS_API_KEY="votre_clé_api"
   ```
   
   Ou passez-la directement au constructeur:
   ```python
   matcher = SmartMatcher(api_key="votre_clé_api")
   ```

## Utilisation

### Import et initialisation

```python
from app.smartmatch import SmartMatcher

# Initialiser le SmartMatcher
matcher = SmartMatcher(api_key="votre_clé_api")
```

### Exemple de matching simple

```python
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

# Afficher les scores par catégorie
for category, score in match_result["category_scores"].items():
    print(f"Score {category}: {score}")

# Afficher les insights
for insight in match_result["insights"]:
    print(f"{insight['category']}: {insight['message']} ({insight['score']})")
```

### Matching par lots

```python
# Charger plusieurs candidats et offres
candidates = [...]  # Liste de profils candidats
jobs = [...]        # Liste d'offres d'emploi

# Effectuer le matching par lots
results = matcher.batch_match(candidates, jobs)

# Traiter les résultats
for match in results:
    print(f"Match {match['candidate_id']} - {match['job_id']}: {match['overall_score']}")
```

## Tests

Deux scripts de test sont fournis pour valider le fonctionnement du système:

1. **Tests unitaires**: Vérifie chaque composant du système
   ```bash
   python test_smartmatch_unit.py
   ```

2. **Test complet**: Exécute un test de bout en bout avec visualisations
   ```bash
   python test_smartmatch.py
   ```

## Données de test intégrées

Le SmartMatcher inclut des données de test qui peuvent être utilisées pour évaluer rapidement le système:

```python
# Charger les données de test
test_data = matcher.load_test_data()
candidates = test_data["candidates"]
jobs = test_data["jobs"]

# Utiliser ces données pour vos tests
```

## Facteurs de pondération

Par défaut, le système utilise les pondérations suivantes pour calculer le score global:

- Compétences: 40%
- Localisation: 25%
- Expérience: 15%
- Éducation: 10%
- Préférences: 10%

Ces pondérations peuvent être ajustées en modifiant le dictionnaire `weights` dans l'initialisation du SmartMatcher:

```python
matcher = SmartMatcher(api_key="votre_clé_api")
matcher.weights = {
    "skills": 0.35,
    "location": 0.30,
    "experience": 0.15,
    "education": 0.10,
    "preferences": 0.10
}
```

## Extensibilité

Le système SmartMatch est conçu pour être facilement extensible:

1. **Ajout de nouveaux critères de matching**: Ajoutez une nouvelle méthode `calculate_X_match` et intégrez-la dans `calculate_match`
2. **Modification des règles de scoring**: Ajustez les seuils et formules dans chaque méthode de calcul
3. **Expansion des insights**: Ajoutez des règles supplémentaires dans la méthode `generate_insights`

## Intégration avec d'autres systèmes

Le SmartMatch peut être intégré à d'autres systèmes via son API simple:

1. **API RESTful**: Exposez les fonctionnalités via des endpoints HTTP
2. **Traitement par lots**: Traitez de grandes quantités de données en arrière-plan
3. **Tableau de bord**: Visualisez les résultats dans une interface utilisateur

## Prochaines améliorations

- **Support des compétences soft**: Ajouter l'analyse des compétences non techniques
- **Personnalisation des pondérations par utilisateur**: Permettre aux utilisateurs d'ajuster l'importance de chaque facteur
- **Apprentissage continu**: Améliorer le matching en fonction des retours des utilisateurs
