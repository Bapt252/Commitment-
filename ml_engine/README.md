# Module Machine Learning pour Commitment

Ce module ajoute des capacités d'apprentissage automatique à l'analyseur de fiches de poste.

## Fonctionnalités

- Infrastructure de collecte et stockage des données
- Modèle NER (Named Entity Recognition) pour l'extraction d'informations
- Modèle de classification des compétences
- API d'intégration avec le frontend existant

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### Configuration de la base de données

```bash
python ml_engine/setup_database.py
```

### Entraînement des modèles

```bash
python ml_engine/train_models.py
```

### Lancement de l'API

```bash
python ml_engine/api.py
```

## Intégration avec le frontend

L'API peut être utilisée directement depuis le frontend en modifiant la fonction `parseJobDescription` dans `static/scripts/job-description-parser.js` pour utiliser l'API ML au lieu de l'analyse basée sur des règles.