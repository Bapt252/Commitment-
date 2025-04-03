# Backend NLP pour Commitment

Ce backend implémente un système de parsing intelligent pour traiter automatiquement les fiches de poste et les CV.

## Fonctionnalités

- Détection automatique du type de document (CV ou fiche de poste)
- Extraction des informations pertinentes:
  - Pour les fiches de poste: titre, expérience requise, compétences, formation, type de contrat, localisation, rémunération
  - Pour les CV: nom, contact, titre, compétences, formation, expérience, langues
- Calcul des scores de confiance pour chaque champ extrait
- API RESTful pour l'intégration avec le frontend

### Nouvelles fonctionnalités (2025)

- **Classification avancée des documents** avec approche ML et règles heuristiques
- **Extraction intelligente des sections** avec détection multi-stratégies
- **Base de connaissances de compétences** avec taxonomie structurée
- **Support multi-format amélioré** pour PDF, DOCX, HTML
- **Pipeline robuste** avec gestion d'erreurs et journalisation

## Installation

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer automatiquement les modèles NLP et créer les répertoires nécessaires
python setup_nlp.py
```

## Utilisation de l'API

### 1. Lancer le serveur

```bash
python run.py
```

Le serveur sera accessible sur http://localhost:8000 par défaut.

### 2. Endpoints disponibles

- `POST /api/parse`: Analyse un texte (CV ou fiche de poste)
  ```json
  {
    "text": "Votre texte à analyser ici..."
  }
  ```

- `POST /api/parse-file`: Analyse un fichier uploadé (CV ou fiche de poste)

### 3. Format de réponse

```json
{
  "doc_type": "cv" ou "job_posting",
  "extracted_data": {
    "titre": "...",
    "experience": [...],
    "competences": [...],
    "competences_categories": {
      "langages_programmation": [...],
      "technologies_web": [...],
      "soft_skills": [...]
    },
    ...
  },
  "confidence_scores": {
    "titre": 0.95,
    "experience": 0.85,
    ...,
    "global": 0.88
  },
  "metadata": {
    "processing_time": 0.42,
    "char_count": 4832,
    "sections": ["header", "contact", ...],
    "language": "fr",
    "format_source": "PDF"
  }
}
```

## Architecture

- `document_classifier.py`: Détecte automatiquement le type de document avec ML
- `section_extractor.py`: Identifie et extrait les sections du document
- `skills_extractor.py`: Catégorise et extrait les compétences avec base de connaissances
- `document_converter.py`: Convertit différents formats de documents
- `job_parser.py`: Extrait les informations des fiches de poste
- `cv_parser.py`: Extrait les informations des CV
- `document_parser.py`: Pipeline principal de traitement

## Technologies utilisées

- spaCy pour l'analyse linguistique en français
- scikit-learn pour les approches ML
- pdfminer.six et docx2txt pour le traitement de documents
- joblib pour la sérialisation des modèles
- Expressions régulières pour les patterns standards

## Tests et débogage

Des logs détaillés sont disponibles dans le dossier `logs/`. Pour consulter les détails du traitement :

```bash
tail -f logs/document_parser.log
```

## Structure des données

Le répertoire `data/` contient des ressources comme la taxonomie des compétences (`skills_taxonomy.json`), que vous pouvez adapter à vos besoins spécifiques.
