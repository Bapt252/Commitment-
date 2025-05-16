# SmartMatch Questionnaire Integration Guide

Ce guide explique comment utiliser les nouvelles fonctionnalités d'intégration des questionnaires dans le SmartMatch Adapter.

## Nouvelles fonctionnalités

L'intégration des questionnaires dans SmartMatch permet désormais d'enrichir considérablement le système de matching entre les CV et les offres d'emploi en prenant en compte les préférences personnalisées des candidats et des entreprises. Voici les principales fonctionnalités ajoutées :

1. **Enrichissement des profils de candidats** avec les données des questionnaires
2. **Enrichissement des offres d'emploi** avec les données des questionnaires
3. **Matching avancé** tenant compte de tous ces critères supplémentaires

## Nouveaux endpoints API

### 1. Enrichir un CV avec les données du questionnaire

```
POST /api/adapter/enrich-cv-with-questionnaire
```

**Exemple de requête :**

```json
{
  "cv_data": {
    "nom": "Dupont",
    "prenom": "Jean",
    "poste": "Développeur Python Senior",
    "competences": ["Python", "Django", "Flask"],
    "logiciels": ["Git", "Docker"],
    "soft_skills": ["Communication", "Travail d'équipe"],
    "email": "jean.dupont@example.com",
    "telephone": "06 12 34 56 78",
    "adresse": "Paris"
  },
  "questionnaire_data": {
    "full-name": "Jean Dupont",
    "job-title": "Développeur Python Senior",
    "transport-method": ["public-transport", "bike"],
    "commute-time-public-transport": "45",
    "commute-time-bike": "30",
    "address": "123 rue de Paris, 75001 Paris",
    "address-lat": "48.8566",
    "address-lng": "2.3522",
    "office-preference": "open-space",
    "motivation-order": "remuneration,evolution,flexibility,location,other",
    "structure-type": ["startup", "pme"],
    "has-sector-preference": "yes",
    "sector-preference": ["tech", "finance"],
    "has-prohibited-sector": "yes",
    "prohibited-sector": ["hospitality"],
    "salary-range": "45K - 55K",
    "availability": "1month",
    "currently-employed": "yes",
    "listening-reason": "no-evolution",
    "notice-period": "1month",
    "notice-negotiable": "yes",
    "recruitment-status": "in-progress"
  }
}
```

### 2. Enrichir une offre d'emploi avec les données du questionnaire

```
POST /api/adapter/enrich-job-with-questionnaire
```

**Exemple de requête :**

```json
{
  "job_data": {
    "title": "Développeur Python Senior",
    "company": "Acme Inc.",
    "location": "Paris",
    "contract_type": "CDI",
    "skills": ["Python", "Django", "Flask", "SQL", "Git"],
    "experience": "5 ans",
    "education": "Master",
    "salary": "45K - 55K"
  },
  "questionnaire_data": {
    "company-name": "Acme Inc.",
    "company-address": "123 Avenue des Champs-Élysées, 75008 Paris",
    "company-website": "https://www.acme-inc.fr",
    "company-description": "Entreprise spécialisée dans le développement de solutions web innovantes",
    "company-size": "pme",
    "recruitment-delay": ["1month"],
    "can-handle-notice": "yes",
    "notice-duration": "1month",
    "recruitment-context": "growth",
    "experience-required": "5-10",
    "sector-knowledge": "no",
    "work-environment": "open-space",
    "team-composition": "Équipe de 8 développeurs, rattachée au CTO",
    "evolution-perspectives": "Possibilité d'évoluer vers un poste de lead developer dans les 2 ans",
    "salary": "45K - 55K",
    "benefits": "Télétravail 3 jours/semaine, RTT, tickets restaurant, mutuelle",
    "contract-type": "cadre"
  }
}
```

### 3. Effectuer un matching avancé

```
POST /api/adapter/smart-match
```

**Exemple de requête :**

```json
{
  "cv": {
    "id": "cv_123",
    "name": "Jean Dupont",
    "skills": ["Python", "Django", "Flask", "Git"],
    "location": "48.8566,2.3522",
    "mobility": {
      "transport_methods": ["public-transport", "bike"],
      "commute_times": {
        "public-transport": 45,
        "bike": 30
      }
    },
    "work_environment_preference": "open-space",
    "motivations": ["remuneration", "evolution", "flexibility", "location", "other"],
    "preferred_structure_types": ["startup", "pme"],
    "preferred_sectors": ["tech", "finance"],
    "prohibited_sectors": ["hospitality"],
    "salary_expectation": {
      "min": 45000,
      "max": 55000
    },
    "availability_days": 30,
    "currently_employed": true,
    "notice_period_days": 30,
    "notice_negotiable": true
  },
  "job": {
    "id": "job_456",
    "title": "Développeur Python Senior",
    "company": "Acme Inc.",
    "location": "48.8707,2.3053",
    "required_skills": ["Python", "Django", "SQL"],
    "preferred_skills": ["Flask", "Git", "Docker"],
    "company_size": "pme",
    "recruitment_delay_days": 30,
    "can_handle_notice": true,
    "max_notice_period_days": 30,
    "work_environment": "open-space",
    "team_composition": "Équipe de 8 développeurs, rattachée au CTO",
    "evolution_perspectives": "Possibilité d'évoluer vers un poste de lead developer dans les 2 ans",
    "salary_range": {
      "min": 45000,
      "max": 55000
    },
    "benefits": ["Télétravail 3 jours/semaine", "RTT", "Tickets restaurant", "Mutuelle"]
  }
}
```

## Formats de données enrichis

### CV enrichi

Le format enrichi d'un CV contient les champs supplémentaires suivants :

```json
{
  "mobility": {
    "transport_methods": ["public-transport", "bike"],
    "commute_times": {
      "public-transport": 45,
      "bike": 30
    }
  },
  "exact_address": "123 rue de Paris, 75001 Paris", 
  "work_environment_preference": "open-space",
  "motivations": ["remuneration", "evolution", "flexibility", "location", "other"],
  "preferred_structure_types": ["startup", "pme"],
  "has_sector_preference": true,
  "preferred_sectors": ["tech", "finance"],
  "prohibited_sectors": ["hospitality"],
  "salary_expectation": {
    "min": 45000,
    "max": 55000
  },
  "availability_days": 30,
  "currently_employed": true,
  "change_reason": "no-evolution",
  "notice_period_days": 30,
  "notice_negotiable": true,
  "recruitment_status": "in-progress"
}
```

### Offre d'emploi enrichie

Le format enrichi d'une offre d'emploi contient les champs supplémentaires suivants :

```json
{
  "exact_location": "123 Avenue des Champs-Élysées, 75008 Paris",
  "company_website": "https://www.acme-inc.fr",
  "company_description": "Entreprise spécialisée dans le développement de solutions web innovantes",
  "company_size": "pme",
  "recruitment_delay_days": 30,
  "can_handle_notice": true,
  "max_notice_period_days": 30,
  "recruitment_context": "growth",
  "requires_sector_knowledge": false,
  "work_environment": "open-space",
  "team_composition": "Équipe de 8 développeurs, rattachée au CTO",
  "evolution_perspectives": "Possibilité d'évoluer vers un poste de lead developer dans les 2 ans",
  "contract_details": "cadre"
}
```

## Critères de matching avancés

Le système de matching prend désormais en compte les critères suivants :

1. **Compatibilité des compétences** : Mise en correspondance des compétences du candidat avec les compétences requises et préférées du poste.

2. **Compatibilité géographique avancée** : Calcul des temps de trajet en fonction des modes de transport et des durées maximales acceptables.

3. **Expérience professionnelle** : Évaluation de l'adéquation entre l'expérience du candidat et les exigences du poste.

4. **Formation et diplômes** : Vérification de la correspondance entre le niveau d'éducation du candidat et les prérequis du poste.

5. **Environnement de travail** : Comparaison des préférences du candidat (open space, bureau) avec l'environnement proposé.

6. **Type de structure** : Évaluation de la correspondance entre les types de structure préférés par le candidat et l'entreprise.

7. **Secteur d'activité** : Vérification que le secteur d'activité de l'entreprise correspond aux préférences du candidat et n'est pas dans sa liste de secteurs à éviter.

8. **Rémunération** : Comparaison des attentes salariales du candidat avec la fourchette de rémunération du poste.

9. **Disponibilité et préavis** : Évaluation de la compatibilité entre la disponibilité du candidat et le délai de recrutement, ainsi que de la gestion des préavis.

10. **Leviers de motivation** : Analyse des leviers de motivation prioritaires du candidat par rapport aux caractéristiques du poste.

## Format du résultat de matching

Le résultat de matching contient maintenant un score global, des scores par catégorie et des insights détaillés pour chaque critère évalué :

```json
{
  "candidate_id": "cv_123",
  "job_id": "job_456",
  "candidate_name": "Jean Dupont",
  "job_title": "Développeur Python Senior",
  "company": "Acme Inc.",
  "overall_score": 0.85,
  "category_scores": {
    "skills": 0.9,
    "location": 0.7,
    "experience": 0.8,
    "education": 0.9,
    "work_environment": 1.0,
    "structure_type": 1.0,
    "sector": 1.0,
    "salary": 1.0,
    "availability": 0.8,
    "motivation": 0.9
  },
  "insights": [
    {
      "type": "required_skills_match",
      "message": "Excellente correspondance des compétences requises",
      "score": 0.9,
      "category": "strength",
      "matched_skills": ["Python", "Django"],
      "missing_skills": ["SQL"]
    },
    {
      "type": "location_match",
      "message": "Trajet de 35 min en transports en commun",
      "score": 0.7,
      "category": "strength",
      "distance_km": 5.2,
      "transport_details": [...]
    },
    // Autres insights...
  ]
}
```

## Intégration dans les formulaires frontend

Pour intégrer ces fonctionnalités dans les questionnaires frontend, vous devez ajouter des fonctions dans votre code JavaScript pour appeler les endpoints API appropriés.

### Exemple pour le questionnaire candidat :

```javascript
// Dans le fichier JavaScript du questionnaire candidat
function submitCandidateQuestionnaire(cvData, questionnaireData) {
    // Formatage des données pour l'API
    const requestData = {
        cv_data: cvData,
        questionnaire_data: questionnaireData
    };

    // Appel à l'API d'enrichissement
    fetch('http://localhost:5053/api/adapter/enrich-cv-with-questionnaire', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        console.log('CV enrichi:', data);
        // Stocker les données enrichies ou passer à l'étape suivante
        sessionStorage.setItem('enrichedCvData', JSON.stringify(data));
        // Redirection ou autre action
    })
    .catch(error => {
        console.error('Erreur lors de l\'enrichissement du CV:', error);
    });
}
```

## Tests CURL

Pour tester les nouveaux endpoints, vous pouvez utiliser les commandes curl suivantes :

### Enrichir un CV avec un questionnaire

```bash
curl -X POST http://localhost:5053/api/adapter/enrich-cv-with-questionnaire \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "nom": "Dupont",
      "prenom": "Jean",
      "poste": "Développeur Python Senior",
      "competences": ["Python", "Django", "Flask"],
      "logiciels": ["Git", "Docker"],
      "soft_skills": ["Communication", "Travail d'équipe"],
      "email": "jean.dupont@example.com",
      "telephone": "06 12 34 56 78",
      "adresse": "Paris"
    },
    "questionnaire_data": {
      "transport-method": ["public-transport", "bike"],
      "commute-time-public-transport": "45",
      "commute-time-bike": "30",
      "address": "123 rue de Paris, 75001 Paris",
      "office-preference": "open-space",
      "motivation-order": "remuneration,evolution,flexibility,location,other",
      "structure-type": ["startup", "pme"],
      "salary-range": "45K - 55K",
      "availability": "1month"
    }
  }'
```

### Enrichir une offre d'emploi avec un questionnaire

```bash
curl -X POST http://localhost:5053/api/adapter/enrich-job-with-questionnaire \
  -H "Content-Type: application/json" \
  -d '{
    "job_data": {
      "title": "Développeur Python Senior",
      "company": "Acme Inc.",
      "location": "Paris",
      "contract_type": "CDI",
      "skills": ["Python", "Django", "Flask", "SQL", "Git"],
      "experience": "5 ans",
      "education": "Master",
      "salary": "45K - 55K"
    },
    "questionnaire_data": {
      "company-address": "123 Avenue des Champs-Élysées, 75008 Paris",
      "company-size": "pme",
      "recruitment-delay": ["1month"],
      "can-handle-notice": "yes",
      "work-environment": "open-space",
      "team-composition": "Équipe de 8 développeurs, rattachée au CTO",
      "evolution-perspectives": "Possibilité d'évoluer vers un poste de lead developer dans les 2 ans"
    }
  }'
```

### Effectuer un matching avancé

```bash
curl -X POST http://localhost:5053/api/adapter/smart-match \
  -H "Content-Type: application/json" \
  -d '{
    "cv": {
      "id": "cv_123",
      "name": "Jean Dupont",
      "skills": ["Python", "Django", "Flask", "Git"],
      "location": "48.8566,2.3522",
      "mobility": {
        "transport_methods": ["public-transport", "bike"],
        "commute_times": {
          "public-transport": 45,
          "bike": 30
        }
      },
      "work_environment_preference": "open-space",
      "motivations": ["remuneration", "evolution", "flexibility", "location", "other"],
      "preferred_structure_types": ["startup", "pme"],
      "salary_expectation": {
        "min": 45000,
        "max": 55000
      },
      "availability_days": 30
    },
    "job": {
      "id": "job_456",
      "title": "Développeur Python Senior",
      "company": "Acme Inc.",
      "location": "48.8707,2.3053",
      "required_skills": ["Python", "Django", "SQL"],
      "preferred_skills": ["Flask", "Git", "Docker"],
      "company_size": "pme",
      "recruitment_delay_days": 30,
      "work_environment": "open-space",
      "evolution_perspectives": "Possibilité d'évoluer vers un poste de lead developer dans les 2 ans",
      "salary_range": {
        "min": 45000,
        "max": 55000
      }
    }
  }'
```
