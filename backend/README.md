# Backend NLP pour Commitment

Ce backend implémente un système de parsing intelligent pour traiter automatiquement les fiches de poste, les CV et les questionnaires entreprises.

## Fonctionnalités

- Détection automatique du type de document (CV ou fiche de poste)
- Extraction des informations pertinentes:
  - Pour les fiches de poste: titre, expérience requise, compétences, formation, type de contrat, localisation, rémunération
  - Pour les CV: nom, contact, titre, compétences, formation, expérience, langues
  - Pour les questionnaires entreprises: valeurs, culture d'entreprise, environnement de travail, technologies, secteur d'activité
- Système de matching entre candidats et entreprises
- Calcul des scores de confiance pour chaque champ extrait
- API RESTful pour l'intégration avec le frontend

### Nouvelles fonctionnalités (2025)

- **Classification avancée des documents** avec approche ML et règles heuristiques
- **Extraction intelligente des sections** avec détection multi-stratégies
- **Base de connaissances de compétences** avec taxonomie structurée
- **Support multi-format amélioré** pour PDF, DOCX, HTML
- **Pipeline robuste** avec gestion d'erreurs et journalisation
- **Matching intelligent** entre candidats et entreprises basé sur des critères multiples
- **Analyse des questionnaires entreprises** pour compréhension de la culture et des valeurs

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

#### Parsing de documents
- `POST /api/jobs/parse`: Analyse un texte (CV ou fiche de poste)
  ```json
  {
    "text": "Votre texte à analyser ici..."
  }
  ```

- `POST /api/jobs/parse-file`: Analyse un fichier uploadé (CV ou fiche de poste)

#### Analyse des questionnaires entreprises
- `POST /api/companies/questionnaire`: Analyse un questionnaire d'entreprise
  ```json
  {
    "company_info": {
      "name": "Entreprise XYZ",
      "website": "https://xyz.com"
    },
    "company_values": "Nous valorisons l'innovation et la collaboration...",
    "work_environment": {
      "remote_policy": "hybrid",
      "office_locations": ["Paris", "Lyon"]
    },
    "technologies": ["Python", "React", "AWS"]
  }
  ```

#### Matching candidats-entreprises
- `GET /api/companies/match/{company_id}/candidates`: Trouve les candidats correspondant à une entreprise
- `GET /api/users/match/{user_id}/companies`: Trouve les entreprises correspondant à un candidat

### 3. Format de réponse

```json
{
  "doc_type": "cv" ou "job_posting" ou "company_questionnaire",
  "extracted_data": {
    "titre": "...",
    "experience": [...],
    "competences": [...],
    "competences_categories": {
      "langages_programmation": [...],
      "technologies_web": [...],
      "soft_skills": [...]
    },
    "values": {
      "detected_values": {
        "innovation": 0.8,
        "collaboration": 0.7
      }
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

### Résultats de matching

```json
{
  "results": [
    {
      "candidate_id": "c1",
      "candidate_name": "Jean Dupont",
      "match_score": 85.7,
      "category_scores": {
        "skills": 90.0,
        "experience": 80.0,
        "values": 85.0,
        "work_environment": 75.0,
        "education": 70.0
      },
      "title": "Développeur Full Stack"
    },
    ...
  ],
  "count": 10,
  "company_id": "company123"
}
```

## Architecture

- `document_classifier.py`: Détecte automatiquement le type de document avec ML
- `section_extractor.py`: Identifie et extrait les sections du document
- `skills_extractor.py`: Catégorise et extrait les compétences avec base de connaissances
- `document_converter.py`: Convertit différents formats de documents
- `job_parser.py`: Extrait les informations des fiches de poste
- `cv_parser.py`: Extrait les informations des CV
- `company_questionnaire_parser.py`: Analyse les questionnaires d'entreprise
- `matching_engine.py`: Système de matching intelligent
- `document_parser.py`: Pipeline principal de traitement

## Technologies utilisées

- spaCy pour l'analyse linguistique en français
- scikit-learn pour les approches ML et le calcul de similarité
- pdfminer.six et docx2txt pour le traitement de documents
- joblib pour la sérialisation des modèles
- Expressions régulières pour les patterns standards
- FastAPI pour l'API RESTful

## Tests et débogage

Des logs détaillés sont disponibles dans le dossier `logs/`. Pour consulter les détails du traitement :

```bash
tail -f logs/document_parser.log
```

## Structure des données

Le répertoire `data/` contient des ressources comme:
- `skills_taxonomy.json`: Taxonomie des compétences
- `company_values_taxonomy.json`: Taxonomie des valeurs d'entreprise
- `industry_sectors.json`: Classification des secteurs d'activité
- `matching_config.json`: Configuration des poids pour le matching
