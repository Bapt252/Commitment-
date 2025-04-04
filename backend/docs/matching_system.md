# Système de Matching Candidats-Offres XGBoost

Ce document décrit le système de matching entre candidats et offres d'emploi basé sur XGBoost implémenté dans Commitment.

## 1. Vue d'ensemble

Le système permet de :
- Classer les candidats par pertinence pour une offre d'emploi donnée
- Classer les offres d'emploi par pertinence pour un candidat donné
- Fournir des explications détaillées sur les facteurs de matching

## 2. Architecture du système

Le système est composé des modules suivants :

1. **Moteur de matching XGBoost**
   - Génération de features sophistiquées
   - Algorithmes de ranking basés sur XGBoost
   - Système d'explications basé sur SHAP

2. **API RESTful pour l'accès**
   - Endpoints pour le classement de candidats
   - Endpoints pour le classement d'offres
   - Endpoints pour l'explication détaillée des matchings

3. **Système d'entraînement du modèle**
   - Génération de données d'entraînement
   - Fonction d'entraînement des modèles
   - Optimisation des hyperparamètres

## 3. Features utilisées pour le matching

### 3.1 Matching technique

- **Similarité des compétences (TF-IDF)** : Mesure la similarité entre les compétences du candidat et celles requises pour le poste
- **Couverture des compétences** : Pourcentage des compétences requises que possède le candidat
- **Concordance des niveaux d'expertise** : Compare les niveaux d'expertise pour chaque compétence

### 3.2 Expérience professionnelle

- **Matching des années d'expérience** : Compare les années d'expérience avec celles requises
- **Pertinence de l'expérience** : Analyse la pertinence de l'expérience passée pour le poste

### 3.3 Formation académique

- **Niveau de formation** : Compare le niveau de formation avec celui requis
- **Domaine d'études** : Évalue la correspondance du domaine d'études avec celui demandé

### 3.4 Alignement culturel et préférentiel

- **Alignement des valeurs** : Mesure la compatibilité entre les valeurs du candidat et la culture d'entreprise
- **Environnement de travail** : Compare les préférences d'environnement de travail
- **Localisation** : Évalue la correspondance géographique
- **Mode de travail** : Compare les préférences de mode de travail (remote, hybride, présentiel)
- **Correspondance salariale** : Évalue l'adéquation entre les attentes salariales et l'offre

### 3.5 Correspondance textuelle

- **Similarité des titres de poste** : Compare le titre de poste souhaité avec celui de l'offre
- **Similarité des descriptions** : Compare les descriptions d'expérience avec la description du poste

## 4. Utilisation de l'API

### 4.1 Classer les candidats pour une offre

```http
POST /api/v1/matching/rank-candidates
```

Corps de la requête :
```json
{
  "job_profile": {
    "job_title": "Développeur Python Senior",
    "required_skills": ["Python", "Django", "SQL"],
    "required_experience_years": 5,
    "required_education_level": "Master",
    "company_values": ["Innovation", "Excellence", "Collaboration"]
  },
  "candidate_ids": ["candidate_1", "candidate_2"],
  "limit": 10
}
```

### 4.2 Classer les offres pour un candidat

```http
POST /api/v1/matching/rank-jobs
```

Corps de la requête :
```json
{
  "candidate_profile": {
    "name": "John Doe",
    "competences": ["Python", "JavaScript", "React"],
    "experience_years": 3,
    "education_level": "Bachelor"
  },
  "job_ids": ["job_1", "job_2"],
  "limit": 10
}
```

### 4.3 Obtenir une explication détaillée

```http
POST /api/v1/matching/explain-match
```

Corps de la requête :
```json
{
  "candidate_profile": {
    "name": "John Doe",
    "competences": ["Python", "JavaScript", "React"],
    "experience_years": 3,
    "education_level": "Bachelor"
  },
  "job_profile": {
    "job_title": "Développeur Python Senior",
    "required_skills": ["Python", "Django", "SQL"],
    "required_experience_years": 5,
    "required_education_level": "Master"
  }
}
```

## 5. Entraînement du modèle

Pour entraîner ou mettre à jour le modèle avec les données actuelles de la base de données :

```http
POST /api/v1/matching/train-model
```

Pour optimiser les hyperparamètres du modèle :

```http
POST /api/v1/matching/tune-hyperparameters
```

## 6. Format des données pour le matching

### 6.1 Format du profil candidat

```json
{
  "id": "candidate_123",
  "name": "John Doe",
  "competences": ["Python", "JavaScript", "React", "Node.js"],
  "skills_with_level": {
    "Python": "expert",
    "JavaScript": "advanced",
    "React": "intermediate"
  },
  "experience": [
    {
      "title": "Développeur Full Stack",
      "company": "Tech Solutions Inc.",
      "period": "2020-2023",
      "description": "Développement d'applications web avec React et Node.js"
    }
  ],
  "experience_years": 3,
  "education_level": "Master",
  "education_field": "Informatique",
  "values": {
    "explicit_values": ["Innovation", "Apprentissage continu", "Travail d'équipe"]
  },
  "work_preferences": {
    "team_size": "medium",
    "management_style": "collaborative",
    "company_culture": "innovative",
    "pace": "fast-paced"
  },
  "preferred_location": "Paris",
  "preferred_work_mode": "hybrid",
  "expected_salary": {
    "min": 50000,
    "max": 70000
  },
  "preferred_company_size": "medium",
  "preferred_industries": ["Tech", "Finance", "Healthcare"]
}
```

### 6.2 Format du profil offre d'emploi

```json
{
  "id": "job_456",
  "job_title": "Développeur Full Stack",
  "company_name": "Innovative Solutions",
  "required_skills": ["JavaScript", "React", "Node.js", "MongoDB"],
  "required_skills_with_level": {
    "JavaScript": "advanced",
    "React": "intermediate",
    "Node.js": "intermediate"
  },
  "required_experience_years": 2,
  "job_description": "Nous recherchons un développeur full stack pour rejoindre notre équipe...",
  "required_education_level": "Bachelor",
  "preferred_education_field": "Informatique ou domaine connexe",
  "company_values": {
    "explicit_values": ["Innovation", "Excellence", "Collaboration"]
  },
  "work_environment": {
    "team_size": "small",
    "management_style": "autonomous",
    "company_culture": "innovative",
    "pace": "balanced"
  },
  "location": "Lyon",
  "work_mode": ["hybrid", "remote"],
  "salary_range": {
    "min": 45000,
    "max": 65000
  },
  "company_size": "small",
  "industry": "Technology"
}
```

## 7. Dépendances

Le système de matching nécessite les dépendances suivantes :

- XGBoost (`xgboost`)
- SHAP (`shap`)
- scikit-learn (`scikit-learn`)
- NumPy (`numpy`)
- Pandas (`pandas`)
- spaCy avec le modèle français (`fr_core_news_md`)
