# Système de Matching Avancé XGBoost

Ce module implémente un système de matching avancé basé sur XGBoost pour la plateforme Commitment. Il permet de trouver les candidats les plus pertinents pour une offre d'emploi et vice-versa, avec des explications détaillées sur les facteurs de matching.

## Fonctionnalités

### Moteur de Matching
- **Ranking bidirectionnel**: Classement des candidats pour une offre et des offres pour un candidat
- **Explications interprétables**: Utilisation de SHAP pour expliquer les prédictions du modèle
- **Scores par catégorie**: Décomposition du score global en catégories (compétences, culture, etc.)
- **Design modulaire**: Architecture extensible avec générateurs de features spécialisés

### Générateurs de Features
Le système utilise quatre générateurs de features spécialisés:

1. **SkillsFeatureGenerator**: Matching de compétences techniques
   - Matching exact et sémantique des compétences
   - Couverture des compétences requises
   - Matching taxonomique (hiérarchie de compétences)

2. **CulturalAlignmentGenerator**: Alignement culturel et de valeurs
   - Matching de valeurs explicites et implicites
   - Alignement par catégorie de valeurs
   - Compatibilité de style de management et de dynamique d'équipe

3. **TextualSimilarityGenerator**: Similarité textuelle
   - Similarité sémantique entre expérience et description de poste
   - Matching de titres de poste
   - Extraction et matching d'entités nommées

4. **PreferenceFeatureGenerator**: Préférences professionnelles
   - Matching de localisation et de mode de travail
   - Correspondance salariale
   - Matching de type de contrat et d'horaires

### API REST
Le système expose les fonctionnalités suivantes via l'API REST:

- `/matching/candidates/match`: Trouve les candidats les plus pertinents pour une offre
- `/matching/jobs/match`: Trouve les offres les plus pertinentes pour un candidat
- `/matching/explain`: Génère une explication détaillée pour une paire candidat-offre
- `/matching/train`: Entraîne les modèles de matching avec de nouvelles données

## Architecture

```
+------------------------+    +------------------------+    +------------------------+
|                        |    |                        |    |                        |
| Générateurs de         |    | Moteur de              |    | API                    |
| Features               |<-->| Matching               |<-->| REST                   |
| - Skills               |    | - XGBoost              |    | - Endpoints            |
| - Cultural             |    | - Normalisation        |    | - Schémas              |
| - Textual              |    | - Explications         |    | - Documentation        |
| - Preference           |    |                        |    |                        |
+------------------------+    +------------------------+    +------------------------+
```

## Utilisation

### Exemple de matching de candidats

```python
from backend.app.nlp.advanced_xgboost_matching import get_matching_engine

# Récupérer l'instance du moteur de matching
matching_engine = get_matching_engine()

# Exécuter le matching
results = matching_engine.rank_candidates_for_job(
    candidates=candidate_list,
    job_profile=job_data,
    limit=10
)

# Afficher les résultats
for candidate in results:
    print(f"{candidate['candidate_name']}: {candidate['relevance_score']}")
    print(f"Forces: {', '.join(candidate['explanation']['strengths'])}")
```

### Exemple d'explication détaillée

```python
# Générer une explication détaillée
explanation = matching_engine.explain_match(
    candidate_profile=candidate_data,
    job_profile=job_data
)

print(f"Score de matching: {explanation['match_score']}")
print(f"Résumé: {explanation['match_summary']}")

print("\nPoints forts:")
for factor in explanation['positive_factors']:
    print(f"- {factor['description']}")

print("\nAxes d'amélioration:")
for factor in explanation['negative_factors']:
    print(f"- {factor['description']}")
```

## Dépendances

- XGBoost: Pour les modèles de ranking
- SHAP: Pour l'interprétabilité des prédictions (optionnel)
- scikit-learn: Pour la préparation des données et l'évaluation
- spaCy: Pour le traitement linguistique
- sentence-transformers: Pour les embeddings sémantiques (optionnel)

## Installation

1. Installer les dépendances Python:
   ```
   pip install xgboost scikit-learn spacy shap sentence-transformers
   ```

2. Télécharger les modèles spaCy:
   ```
   python -m spacy download fr_core_news_md
   ```

3. Créer les répertoires de données:
   ```
   mkdir -p backend/data/models
   ```

## Améliorations futures

- Intégration d'un cache Redis pour les résultats de matching fréquents
- Ajout de pipelines d'entraînement automatique avec MLflow
- Support des embeddings multimodaux pour les CV avec images
- Extension pour le matching de compétences multilingue
