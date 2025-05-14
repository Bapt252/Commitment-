# Nexten SmartMatch - Système de Matching Bidirectionnel Intelligent

Ce document décrit le nouveau système de matching bidirectionnel implémenté pour Nexten, appelé **Nexten SmartMatch**, qui permet une correspondance intelligente et précise entre candidats et offres d'emploi.

## 1. Introduction

Nexten SmartMatch est un système avancé qui révolutionne la mise en relation entre candidats et employeurs en utilisant :

- Une approche bidirectionnelle
- Une analyse sémantique avancée
- Une intégration de la géolocalisation et du temps de trajet
- Un système de pondération dynamique
- Des insights détaillés et des recommandations

## 2. Caractéristiques principales

### 2.1. Matching bidirectionnel

Le système peut fonctionner dans les deux sens :
- Trouver les meilleures offres d'emploi pour un candidat
- Trouver les meilleurs candidats pour une offre d'emploi

Cette approche bidirectionnelle permet une utilisation flexible par les recruteurs comme par les candidats.

### 2.2. Sources de données intégrées

Le système utilise trois sources principales d'information :

1. **CV parsé via OpenAI** : 
   - Compétences techniques extraites
   - Expérience professionnelle
   - Formation
   - Résumé du profil

2. **Questionnaire candidat** :
   - Informations personnelles
   - Mobilité et préférences
   - Motivations et secteurs
   - Disponibilité et situation

3. **Questionnaire entreprise / Fiche de poste** :
   - Description du poste
   - Compétences requises et préférées
   - Mode de travail et localisation
   - Culture d'entreprise et valeurs

### 2.3. Analyse géographique et temps de trajet

Une fonctionnalité majeure du système est l'intégration de l'analyse géographique :

- Calcul du temps de trajet réel entre le candidat et l'entreprise via l'API Google Maps
- Prise en compte du mode de transport préféré (voiture, transports en commun, vélo, à pied)
- Évaluation de la compatibilité entre le temps de trajet calculé et le temps maximum accepté par le candidat

### 2.4. Analyse sémantique avancée

Le système utilise des techniques d'analyse sémantique pour :

- Détecter les compétences similaires ou synonymes
- Calculer la similarité sémantique entre descriptions de poste et résumés de CV
- Comparer les valeurs d'entreprise et les motivations des candidats

### 2.5. Insights et recommandations

Le système génère automatiquement :

- Points forts du matching
- Points d'amélioration
- Recommandations concrètes pour le recruteur

## 3. Architecture du système

Le système Nexten SmartMatch est composé de plusieurs composants :

```
matching-service/
├── app/
│   ├── algorithms/
│   │   ├── nexten_bidirectional_matcher.py   # Algorithme principal
│   │   ├── nlp_utils.py                      # Utilitaires NLP
│   ├── api/
│   │   ├── routes/
│   │   │   ├── bidirectional.py              # Routes API bidirectionnelles
│   ├── models/
│   │   ├── bidirectional.py                  # Modèles de données
│   ├── workers/
│   │   ├── bidirectional_tasks.py            # Tâches asynchrones
```

## 4. Fonctionnement de l'algorithme

### 4.1. Calcul du score global

Le système évalue plusieurs dimensions de compatibilité :

#### Basé sur le CV (55% du score total) :
- **Compétences** (25%) : Correspondance entre compétences du candidat et celles requises
- **Expérience** (15%) : Évaluation du niveau d'expérience par rapport aux besoins
- **Description** (10%) : Similarité sémantique entre résumé du CV et description du poste
- **Titre du poste** (5%) : Correspondance entre le titre actuel et celui proposé

#### Basé sur les questionnaires (45% du score total) :
- **Informations personnelles** (5%) : Adéquation du poste souhaité
- **Mobilité et préférences** (15%) : Mode de travail, localisation, type de contrat
- **Motivations et secteurs** (15%) : Secteurs d'activité, valeurs, technologies
- **Disponibilité et situation** (10%) : Disponibilité, attentes salariales

### 4.2. Évaluation des compétences

- Distinction entre compétences requises et préférées
- Détection des synonymes et termes similaires
- Bonus pour les compétences essentielles

### 4.3. Évaluation de l'expérience

- Courbe de valorisation pour l'expérience
- Traitement nuancé des candidats surqualifiés

### 4.4. Évaluation du temps de trajet

- Calcul du temps de trajet réel via l'API Google Maps
- Comparaison avec le temps maximum acceptable pour le candidat
- Score dégressif en fonction du pourcentage du temps maximal

### 4.5. Classification des résultats

Le système génère un score global entre 0 et 1, qui est ensuite classifié :
- **Excellent** (≥ 0.85)
- **Bon** (≥ 0.7)
- **Modéré** (≥ 0.5)
- **Faible** (≥ 0.3)
- **Insuffisant** (< 0.3)

## 5. Utilisation de l'API

### 5.1. Matching bidirectionnel simple

```
POST /api/v2/match?candidate_id=123&job_id=456&with_commute_time=true
```

### 5.2. Recherche d'offres pour un candidat

```
POST /api/v2/find-jobs
{
    "candidate_id": 123,
    "limit": 10,
    "min_score": 0.5,
    "with_commute_time": true,
    "webhook_url": "https://example.com/webhook"
}
```

### 5.3. Recherche de candidats pour une offre

```
POST /api/v2/find-candidates
{
    "job_id": 456,
    "limit": 10,
    "min_score": 0.5,
    "with_commute_time": true,
    "webhook_url": "https://example.com/webhook"
}
```

## 6. Exemples de résultats

### 6.1. Résultat de matching simple

```json
{
  "score": 0.82,
  "category": "good",
  "details": {
    "cv": {
      "total": 0.79,
      "skills": 0.85,
      "experience": 0.90,
      "description": 0.75,
      "title": 0.70
    },
    "questionnaire": {
      "total": 0.85,
      "informations_personnelles": 0.80,
      "mobilite_preferences": 0.95,
      "motivations_secteurs": 0.85,
      "disponibilite_situation": 0.80
    }
  },
  "insights": {
    "strengths": [
      "Excellente adéquation des compétences techniques",
      "Préférences de travail en parfaite adéquation (mode, localisation, contrat)"
    ],
    "areas_of_improvement": [
      "La localisation implique un temps de trajet de 35 minutes, ce qui est acceptable mais pourrait être optimisé"
    ],
    "recommendations": [
      "Bon profil, entretien recommandé",
      "Possibilité de discuter d'arrangements de télétravail partiel pour compenser le temps de trajet"
    ]
  }
}
```

### 6.2. Résultat de recherche multiple

```json
{
  "count": 3,
  "results": [
    {
      "job": {
        "id": 456,
        "title": "Développeur Full Stack Senior",
        "company": "TechInnovation",
        "location": "Paris"
      },
      "score": 0.82,
      "category": "good",
      "details": {...},
      "insights": {...}
    },
    {
      "job": {
        "id": 789,
        "title": "Lead Developer",
        "company": "DigitalSolutions",
        "location": "Paris"
      },
      "score": 0.75,
      "category": "good",
      "details": {...},
      "insights": {...}
    },
    ...
  ],
  "timestamp": "2025-05-14T07:42:12.123Z",
  "query_parameters": {
    "candidate_id": 123,
    "limit": 10,
    "min_score": 0.5,
    "with_commute_time": true
  }
}
```

## 7. Avantages du système

- **Précision accrue** : La prise en compte de multiples facteurs et l'analyse sémantique permettent une évaluation plus précise de la compatibilité.
- **Expérience utilisateur améliorée** : Le calcul du temps de trajet réel offre une expérience plus personnalisée.
- **Transparence** : Les insights et recommandations expliquent clairement les résultats du matching.
- **Flexibilité** : L'approche bidirectionnelle permet une utilisation par les recruteurs comme par les candidats.
- **Pertinence** : La pondération dynamique permet d'adapter l'importance des critères selon le contexte.

## 8. Évolutions futures

Le système a été conçu pour évoluer avec des améliorations futures :

1. **Intelligence artificielle avancée** :
   - Apprentissage automatique pour ajuster les pondérations en fonction des retours
   - Modèle prédictif de succès pour les recrutements

2. **Intégration de données externes** :
   - Données du marché de l'emploi
   - Tendances salariales par secteur et région

3. **Interface utilisateur enrichie** :
   - Visualisation des résultats de matching
   - Carte interactive des temps de trajet

4. **Analyse conversationnelle** :
   - Intégration d'un chatbot pour affiner les préférences
   - Recommandations personnalisées en langage naturel

## 9. Installation et configuration

Pour utiliser le système Nexten SmartMatch :

1. Assurez-vous que les dépendances sont installées :
   - scikit-learn
   - python-Levenshtein
   - aiohttp

2. Configurez la clé API Google Maps dans votre fichier `.env` :
   ```
   GOOGLE_MAPS_API_KEY=votre_clé_api_google_maps
   ```

3. Lancez le service :
   ```bash
   docker-compose up -d matching-service
   ```

## 10. Conclusion

Nexten SmartMatch représente une avancée significative dans le domaine du matching candidat-emploi. En intégrant des analyses sémantiques, géographiques et comportementales, le système offre une précision et une pertinence inégalées, facilitant ainsi la connexion entre les talents et les opportunités idéales.
