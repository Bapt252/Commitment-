# Backend NLP pour Commitment

Ce backend implémente un système de parsing intelligent pour traiter automatiquement les fiches de poste et les CV.

## Fonctionnalités

- Détection automatique du type de document (CV ou fiche de poste)
- Extraction des informations pertinentes:
  - Pour les fiches de poste: titre, expérience requise, compétences, formation, type de contrat, localisation, rémunération
  - Pour les CV: nom, contact, titre, compétences, formation, expérience, langues
- Calcul des scores de confiance pour chaque champ extrait
- API RESTful pour l'intégration avec le frontend

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Télécharger les modèles spaCy pour le français
python -m spacy download fr_core_news_lg
```

## Utilisation de l'API

### 1. Lancer le serveur

```bash
python run.py
```

Le serveur sera accessible sur http://localhost:8000 par défaut.

### 2. Endpoints disponibles

- `POST /api/v1/jobs/parse`: Analyse un texte (CV ou fiche de poste)
  ```json
  {
    "text": "Votre texte à analyser ici..."
  }
  ```

- `POST /api/v1/jobs/parse-file`: Analyse un fichier uploadé (CV ou fiche de poste)

### 3. Format de réponse

```json
{
  "doc_type": "cv" ou "job_posting",
  "extracted_data": {
    "titre": "...",
    "experience": "...",
    "competences": [...],
    ...
  },
  "confidence_scores": {
    "titre": 0.95,
    "experience": 0.85,
    ...,
    "global": 0.88
  }
}
```

## Architecture

- `document_classifier.py`: Détecte automatiquement le type de document
- `job_parser.py`: Extrait les informations des fiches de poste
- `cv_parser.py`: Extrait les informations des CV
- `document_parser.py`: Point d'entrée principal qui coordonne l'analyse

## Technologies utilisées

- spaCy pour l'analyse linguistique en français
- Transformers (CamemBERT) pour la compréhension contextuelle
- Expressions régulières pour les patterns standards
