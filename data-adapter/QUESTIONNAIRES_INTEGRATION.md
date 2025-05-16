# Intégration des Questionnaires dans SmartMatch

Ce document explique comment utiliser les nouvelles fonctionnalités d'intégration des questionnaires dans le SmartMatch Adapter.

## Vue d'ensemble

L'intégration des questionnaires permet d'enrichir le matching entre CV et offres d'emploi en prenant en compte des critères supplémentaires tels que :

- Mobilité et préférences de transport
- Environnement de travail préféré
- Type de structure
- Leviers de motivation
- Préférences sectorielles
- Disponibilité et préavis
- Et bien plus encore...

## Nouvelles fonctionnalités

### Nouveaux endpoints API

Trois nouveaux endpoints ont été ajoutés à l'API SmartMatch Adapter :

1. **`/api/adapter/enrich-cv-with-questionnaire`** : Enrichit les données CV avec les réponses au questionnaire candidat.
2. **`/api/adapter/enrich-job-with-questionnaire`** : Enrichit les données d'offre d'emploi avec les réponses au questionnaire client.
3. **`/api/adapter/smart-match`** : Effectue un matching avancé tenant compte des données enrichies.

### Nouvelles fonctions dans SmartMatchDataAdapter

Trois nouvelles fonctions principales ont été implémentées :

1. **`enrich_cv_data_with_questionnaire()`** : Enrichit les données CV avec les réponses du questionnaire candidat.
2. **`enrich_job_data_with_questionnaire()`** : Enrichit les données d'offre d'emploi avec les réponses du questionnaire client.
3. **`enhanced_match()`** : Réalise un matching avancé entre un CV et une offre d'emploi, en tenant compte des critères enrichis.

De plus, dix fonctions de calcul de compatibilité ont été ajoutées pour évaluer les différents aspects du matching :

1. **`_calculate_skills_compatibility()`** : Compatibilité des compétences techniques
2. **`_calculate_location_compatibility()`** : Compatibilité géographique avancée (avec temps de trajet)
3. **`_calculate_experience_compatibility()`** : Compatibilité de l'expérience professionnelle
4. **`_calculate_education_compatibility()`** : Compatibilité du niveau d'éducation
5. **`_calculate_work_environment_compatibility()`** : Compatibilité de l'environnement de travail
6. **`_calculate_structure_compatibility()`** : Compatibilité du type de structure
7. **`_calculate_sector_compatibility()`** : Compatibilité sectorielle
8. **`_calculate_salary_compatibility()`** : Compatibilité salariale
9. **`_calculate_availability_compatibility()`** : Compatibilité des disponibilités et préavis
10. **`_calculate_motivation_compatibility()`** : Compatibilité des leviers de motivation

## Comment utiliser les nouvelles fonctionnalités

### 1. Enrichir un CV avec un questionnaire

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
      "availability": "1month",
      "currently-employed": "yes",
      "notice-period": "1month"
    }
  }'
```

### 2. Enrichir une offre d'emploi avec un questionnaire

```bash
curl -X POST http://localhost:5053/api/adapter/enrich-job-with-questionnaire \
  -H "Content-Type: application/json" \
  -d '{
    "job_data": {
      "title": "Développeur Python Senior",
      "company": "Acme Inc.",
      "location": "Paris",
      "contract_type": "CDI",
      "skills": ["Python", "Django", "Flask", "SQL", "Git"]
    },
    "questionnaire_data": {
      "company-address": "123 Avenue des Champs-Élysées, 75008 Paris",
      "company-size": "pme",
      "recruitment-delay": ["1month"],
      "can-handle-notice": "yes",
      "notice-duration": "1month",
      "work-environment": "open-space",
      "team-composition": "Équipe de 8 développeurs",
      "evolution-perspectives": "Évolution vers lead developer",
      "salary": "45K - 55K",
      "benefits": "Télétravail 3j/semaine, RTT, tickets resto"
    }
  }'
```

### 3. Effectuer un matching avancé

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
      "motivations": ["remuneration", "evolution", "flexibility"],
      "preferred_structure_types": ["startup", "pme"]
    },
    "job": {
      "id": "job_456",
      "title": "Développeur Python Senior",
      "company": "Acme Inc.",
      "location": "48.8707,2.3053",
      "required_skills": ["Python", "Django", "SQL"],
      "preferred_skills": ["Flask", "Git", "Docker"],
      "company_size": "pme",
      "work_environment": "open-space",
      "salary_range": {
        "min": 45000,
        "max": 55000
      }
    }
  }'
```

### 4. Intégrer le questionnaire frontend

Vous pouvez modifier les fichiers de questionnaire HTML pour envoyer les données au SmartMatch Adapter en ajoutant le code JavaScript suivant :

#### Pour le questionnaire candidat (templates/candidate-questionnaire.html)

```javascript
// À la soumission du formulaire
document.getElementById('questionnaire-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Récupérer les données du formulaire
    const formData = new FormData(this);
    const questionnaireData = {};
    
    // Convertir FormData en objet simple
    for (let [key, value] of formData.entries()) {
        questionnaireData[key] = value;
    }
    
    // Récupérer les données du CV (par exemple depuis le sessionStorage)
    const cvData = JSON.parse(sessionStorage.getItem('parsedCvData') || '{}');
    
    // Envoyer les données pour enrichissement
    fetch('http://localhost:5053/api/adapter/enrich-cv-with-questionnaire', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cv_data: cvData,
            questionnaire_data: questionnaireData
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('CV enrichi:', data);
        // Stocker les données enrichies
        sessionStorage.setItem('enrichedCvData', JSON.stringify(data));
        // Redirection
        window.location.href = 'matching-results.html';
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
});
```

#### Pour le questionnaire client (templates/client-questionnaire.html)

```javascript
// À la soumission du formulaire
document.getElementById('client-questionnaire-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Récupérer les données du formulaire
    const formData = new FormData(this);
    const questionnaireData = {};
    
    // Convertir FormData en objet simple
    for (let [key, value] of formData.entries()) {
        questionnaireData[key] = value;
    }
    
    // Récupérer les données de l'offre d'emploi (depuis le sessionStorage)
    const jobData = JSON.parse(sessionStorage.getItem('parsedJobData') || '{}');
    
    // Envoyer les données pour enrichissement
    fetch('http://localhost:5053/api/adapter/enrich-job-with-questionnaire', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            job_data: jobData,
            questionnaire_data: questionnaireData
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Offre enrichie:', data);
        // Stocker les données enrichies
        sessionStorage.setItem('enrichedJobData', JSON.stringify(data));
        // Redirection
        window.location.href = 'candidates-recommendation.html';
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
});
```

## Structure des données

### Données CV enrichies

Les données CV enrichies contiennent les informations suivantes:

```json
{
  "id": "cv_123",
  "name": "Jean Dupont",
  "skills": ["Python", "Django", "Flask"],
  "soft_skills": ["Communication", "Travail d'équipe"],
  "location": "48.8566,2.3522",
  "address": "Paris",
  "contact": {
    "email": "jean.dupont@example.com",
    "phone": "06 12 34 56 78"
  },
  "years_of_experience": 3,
  "education_level": "bachelor",
  "remote_work": true,
  "salary_expectation": {
    "min": 45000,
    "max": 55000
  },
  "job_type": "full_time",
  "industry": "tech",
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
  "availability_days": 30,
  "currently_employed": true,
  "change_reason": "no-evolution",
  "notice_period_days": 30,
  "notice_negotiable": true,
  "recruitment_status": "in-progress"
}
```

### Données d'offre d'emploi enrichies

Les données d'offre d'emploi enrichies contiennent les informations suivantes:

```json
{
  "id": "job_456",
  "title": "Développeur Python Senior",
  "company": "Acme Inc.",
  "required_skills": ["Python", "Django", "SQL"],
  "preferred_skills": ["Flask", "Git", "Docker"],
  "location": "48.8707,2.3053",
  "location_text": "Paris",
  "min_years_of_experience": 5,
  "max_years_of_experience": 8,
  "required_education": "master",
  "offers_remote": true,
  "salary_range": {
    "min": 45000,
    "max": 55000
  },
  "job_type": "full_time",
  "industry": "tech",
  "responsibilities": ["Développer des applications web avec Django"],
  "benefits": ["Télétravail partiel", "Mutuelle d'entreprise", "Tickets restaurant"],
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

### Résultat de matching

Le résultat du matching avancé contient les informations suivantes:

```json
{
  "candidate_id": "cv_123",
  "job_id": "job_456",
  "candidate_name": "Jean Dupont",
  "job_title": "Développeur Python Senior",
  "company": "Acme Inc.",
  "overall_score": 0.82,
  "category_scores": {
    "skills": 0.85,
    "location": 0.70,
    "experience": 0.80,
    "education": 0.90,
    "work_environment": 0.95,
    "structure_type": 1.00,
    "sector": 0.80,
    "salary": 0.90,
    "availability": 0.70,
    "motivation": 0.75
  },
  "insights": [
    {
      "type": "required_skills_match",
      "message": "Excellente correspondance des compétences requises",
      "score": 0.85,
      "category": "strength",
      "matched_skills": ["Python", "Django"],
      "missing_skills": ["SQL"]
    },
    {
      "type": "location_match",
      "message": "Trajet de 12 min en vélo",
      "score": 0.70,
      "category": "strength",
      "distance_km": 2.5,
      "transport_details": [...]
    },
    // Autres insights...
  ]
}
```

## Prochaines améliorations

Voici quelques pistes d'amélioration pour les prochaines versions :

1. **Intégration de l'API Google Maps** pour des calculs précis de temps de trajet
2. **Apprentissage des préférences** pour affiner les scores de matching
3. **Interface de visualisation des résultats** pour une meilleure compréhension du matching
4. **Système de filtrage avancé** pour cibler les meilleurs candidats ou offres

## Support

Si vous avez des questions ou rencontrez des problèmes, n'hésitez pas à contacter l'équipe de développement.
