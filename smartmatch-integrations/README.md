# SmartMatch - Intégration avec les questionnaires

Ce module permet d'intégrer l'algorithme SmartMatch avec les questionnaires candidat et client utilisés dans la plateforme Commitment.

## Fonctionnalités

- Extraction des données des questionnaires HTML
- Transformation des réponses en format compatible avec SmartMatch
- Enrichissement des profils candidat et entreprise
- Matching amélioré prenant en compte les nouvelles dimensions
- Génération d'insights détaillés

## Architecture

Le système est composé de deux classes principales :

1. **`QuestionnaireConnector`** : Assure la liaison entre les formulaires HTML et l'algorithme SmartMatch
2. **`SmartMatchIntegration`** : Système complet d'intégration avec l'application

## Nouvelles dimensions de matching

L'intégration des questionnaires permet de prendre en compte de nouvelles dimensions :

### Pour les candidats

- **Mobilité** : Moyens de transport et temps de trajet maximum acceptables
- **Environnement de travail** : Préférences pour open space, bureau partagé, etc.
- **Motivations** : Priorités entre rémunération, évolution, flexibilité, etc.
- **Structure** : Préférences pour le type d'entreprise (startup, PME, grand groupe)
- **Secteur** : Préférences sectorielles et secteurs à éviter
- **Disponibilité** : Délai avant prise de poste
- **Préavis** : Durée et négociabilité du préavis

### Pour les entreprises

- **Délai de recrutement** : Urgence du besoin de recrutement
- **Gestion des préavis** : Capacité à accepter des préavis et durée maximum
- **Environnement** : Type d'espace de travail proposé
- **Flexibilité** : Télétravail et horaires aménagés
- **Perspectives** : Évolution possible au sein de l'entreprise
- **Équipe** : Composition et dynamique de l'équipe

## Utilisation

### Installation

```bash
# Copier le fichier dans votre projet
cp questionnaire_connector.py /chemin/vers/votre/projet/
```

### Exemple d'utilisation

```python
from questionnaire_connector import SmartMatchIntegration

# Initialiser le système d'intégration
integration = SmartMatchIntegration(api_key="VOTRE_CLE_API_GOOGLE_MAPS")

# Traiter une soumission candidat
cv_data = {...}  # Données du CV
questionnaire_data = {...}  # Données du questionnaire candidat
candidate = integration.process_candidate_submission(cv_data, questionnaire_data)

# Traiter une soumission offre d'emploi
job_data = {...}  # Données de l'offre
job_questionnaire_data = {...}  # Données du questionnaire client
job = integration.process_job_submission(job_data, job_questionnaire_data)

# Effectuer un matching
if hasattr(integration.data_adapter, 'enhanced_match'):
    result = integration.data_adapter.enhanced_match(candidate, job)
else:
    result = integration.matcher.calculate_match(candidate, job)

# Afficher le résultat
print(f"Score global: {result['overall_score']}")
for category, score in result['category_scores'].items():
    print(f"  - {category}: {score}")

# Afficher les insights
for insight in result['insights']:
    print(f"- {insight['message']} ({insight['category']})")
```

### Intégration avec Flask

Le module inclut un exemple d'intégration API pour Flask :

```python
from flask import Flask
from questionnaire_connector import SmartMatchIntegration, create_flask_routes

app = Flask(__name__)
integration = SmartMatchIntegration()

# Créer les routes API
create_flask_routes(app, integration)

if __name__ == "__main__":
    app.run(debug=True)
```

Cela crée plusieurs endpoints :

- `/api/process-candidate` : Traite une soumission candidat
- `/api/process-job` : Traite une soumission offre d'emploi  
- `/api/match` : Effectue un matching entre un candidat et une offre
- `/api/find-matches/candidate/<id>` : Trouve les meilleures offres pour un candidat
- `/api/find-matches/job/<id>` : Trouve les meilleurs candidats pour une offre

## Contribution

Pour contribuer à ce module :

1. Créez une branche (`git checkout -b feature/nouvelle-fonction`)
2. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonction'`)
3. Poussez vers la branche (`git push origin feature/nouvelle-fonction`)
4. Créez une Pull Request

## Licence

Ce projet est sous licence interne Nexten.
