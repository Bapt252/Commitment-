
# Algorithme de Matching Intelligent Nexten

Ce document décrit l'algorithme de matching intelligent implémenté pour Nexten, qui permet de faire correspondre les profils des candidats aux offres d'emploi en utilisant une approche en trois phases :

1. **Parsing CV via OpenAI**
2. **Questionnaires candidat et entreprise**
3. **Matching intelligent combinant ces sources**

## 1. Aperçu du système

L'algorithme de matching de Nexten est conçu pour évaluer la compatibilité entre un candidat et une offre d'emploi en prenant en compte trois sources de données principales :

- **CV du candidat** : Analysé via OpenAI pour extraire les compétences, l'expérience et d'autres informations pertinentes
- **Questionnaire candidat** : Capte les préférences, les attentes et d'autres informations non présentes dans le CV
- **Questionnaire entreprise** : Définit précisément les besoins pour le poste au-delà de la description classique

## 2. Architecture et composants

Le système est composé de plusieurs modules :

- **`nexten_matcher.py`** : Contient l'algorithme principal de matching
- **`matching_service.py`** : Service intégrant le parsing CV et la gestion des questionnaires
- **`tasks.py`** : Tâches asynchrones pour le worker RQ

### Classe principale : `NextenMatchingAlgorithm`

Cette classe est le cœur du système, implémentant toute la logique de matching avec une architecture modulaire :

```python
matcher = NextenMatchingAlgorithm()
result = matcher.calculate_match(candidate_data, job_data)
```

## 3. Phase 1 : Parsing CV via OpenAI

Le système utilise OpenAI (GPT-4) pour extraire les informations structurées des CV :

```python
cv_data = await parse_cv_with_openai(cv_file_path, openai_client)
```

Les informations extraites comprennent :
- Nom complet
- Titre du poste
- Compétences techniques
- Expérience totale
- Formation
- Résumé du profil
- Postes précédents

## 4. Phase 2 : Questionnaires

### Questionnaire candidat

Le questionnaire candidat est structuré en quatre sections :

1. **Informations personnelles**
   - Nom et prénom
   - Intitulé de poste souhaité

2. **Mobilité et préférences**
   - Mode de travail (Sur site, Hybride, Remote)
   - Localisation
   - Type de contrat
   - Taille d'entreprise préférée

3. **Motivations et secteurs**
   - Secteurs d'activité d'intérêt
   - Valeurs importantes
   - Technologies préférées

4. **Disponibilité et situation**
   - Disponibilité pour commencer
   - Expérience totale
   - Attentes salariales

### Questionnaire entreprise

Le questionnaire entreprise capture des informations précises sur le poste :

- Poste proposé
- Mode de travail
- Localisation
- Type de contrat
- Taille d'entreprise
- Secteur d'activité
- Valeurs d'entreprise
- Technologies requises et préférées
- Date de début souhaitée
- Expérience requise
- Fourchette salariale

## 5. Phase 3 : Algorithme de matching intelligent

### Facteurs pris en compte par l'algorithme

L'algorithme évalue plusieurs dimensions de compatibilité :

#### Basé sur le CV :
- **Compétences** (25%) : Correspondance entre les compétences du candidat et celles requises pour le poste
- **Expérience** (15%) : Comparaison de l'expérience du candidat avec celle requise
- **Description** (10%) : Similarité entre le résumé du CV et la description du poste
- **Titre du poste** (5%) : Correspondance entre le titre du poste actuel et celui proposé

#### Basé sur les questionnaires :
- **Informations personnelles** (5%) : Adéquation du poste souhaité
- **Mobilité et préférences** (15%) : Mode de travail, localisation, type de contrat, etc.
- **Motivations et secteurs** (15%) : Secteurs d'activité, valeurs, technologies
- **Disponibilité et situation** (10%) : Disponibilité, attentes salariales

### Fonctionnement détaillé de l'algorithme

1. **Évaluation des compétences**
   - Distinction entre compétences requises et préférées
   - Bonus pour les compétences essentielles

2. **Courbe de valorisation pour l'expérience**
   - Pénalisation réduite pour les écarts mineurs
   - Traitement nuancé des candidats surqualifiés

3. **Évaluation des préférences de travail**
   - Correspondance du mode de travail (sur site, hybride, remote)
   - Correspondance de localisation
   - Adéquation du type de contrat

4. **Analyse de la compatibilité culturelle**
   - Correspondance des valeurs d'entreprise
   - Correspondance des secteurs d'activité

5. **Adéquation des attentes salariales**
   - Intersection des fourchettes salariales

### Système de scoring

Le système génère un score global entre 0 et 1, qui est ensuite classifié :
- **Excellent** (≥ 0.85)
- **Bon** (≥ 0.7)
- **Modéré** (≥ 0.5)
- **Faible** (≥ 0.3)
- **Insuffisant** (< 0.3)

Le système fournit également des insights pour expliquer le matching :
- **Forces** : Points forts de la correspondance
- **Points d'amélioration** : Écarts significatifs
- **Recommandations** : Suggestions d'action basées sur le score

## 6. Utilisation du service

### Matching simple entre un candidat et une offre

```python
result = await nexten_matching_process(candidate_id, job_id, db, openai_client)
```

### Matching d'un candidat avec plusieurs offres

```python
results = await bulk_matching_process(candidate_id, job_ids, db, openai_client)
```

### Recherche de candidats pour une offre

```python
results = await job_candidates_matching_process(job_id, candidate_ids, db, openai_client, limit=10)
```

### Traitement complet : parsing CV et matching

```python
result = await process_cv_and_match_task(candidate_id, cv_file_path, job_ids, db, openai_client)
```

## 7. Configuration de l'algorithme

L'algorithme est hautement configurable pour s'adapter aux besoins spécifiques :

```python
config = {
    'weights': {
        'cv_skills': 0.25,
        'cv_experience': 0.15,
        # Autres poids...
    },
    'thresholds': {
        'minimum_score': 0.3,
        'excellent_match': 0.85
    },
    'skills_config': {
        'essential_bonus': 1.5,
        'nice_to_have_factor': 0.7
    },
    # Autres configurations...
}

matcher = NextenMatchingAlgorithm(config)
```

## 8. Intégration avec les workers

Le système est conçu pour être utilisé dans un environnement asynchrone avec Redis Queue (RQ) :

```python
# Dans le code qui met en file d'attente les tâches
queue = Queue('matching_high', connection=redis_conn)
job = queue.enqueue(
    'app.workers.tasks.calculate_matching_score_task',
    args=(candidate_id, job_id),
    job_id=f"matching-{candidate_id}-{job_id}",
    meta={"webhook_url": webhook_url}
)
```

## 9. Évolutions futures

L'algorithme a été conçu avec une architecture modulaire pour faciliter les évolutions futures :

1. **Analyses sémantiques avancées** :
   - Utilisation d'embeddings pour les descriptions et résumés
   - Gestion avancée des synonymes entre compétences

2. **Apprentissage automatique** :
   - Calibrage automatique des poids basé sur le feedback
   - Modèle de prédiction de réussite des recrutements

3. **Facteurs contextuels** :
   - Prise en compte des tendances du marché
   - Adaptation à la rareté des compétences

4. **Optimisation des performances** :
   - Mise en cache des résultats intermédiaires
   - Calculs parallélisés pour les matchings en masse

## 10. Exemple de résultat

Voici un exemple de résultat retourné par l'algorithme :

```json
{
  "score": 0.78,
  "category": "good",
  "details": {
    "cv": {
      "total": 0.82,
      "skills": 0.85,
      "experience": 0.90,
      "description": 0.75,
      "title": 0.70
    },
    "questionnaire": {
      "total": 0.72,
      "informations_personnelles": 0.80,
      "mobilite_preferences": 0.65,
      "motivations_secteurs": 0.85,
      "disponibilite_situation": 0.60
    }
  },
  "insights": {
    "strengths": [
      "Excellente adéquation des compétences techniques",
      "Fort intérêt pour le secteur d'activité"
    ],
    "areas_of_improvement": [
      "Préférence pour Full remote vs Hybride requis"
    ],
    "recommendations": [
      "Bon profil, entretien recommandé"
    ]
  }
}
```

## Conclusion

L'algorithme de matching intelligent de Nexten offre une solution complète qui va au-delà de la simple correspondance de mots-clés. En intégrant les données du CV, les préférences du candidat et les exigences précises de l'entreprise, il permet d'identifier les candidats qui correspondent réellement aux besoins du poste, tout en assurant une expérience positive pour les deux parties.

Cette approche modulaire permet non seulement d'obtenir de bons résultats dès le MVP, mais aussi d'évoluer progressivement vers un système toujours plus précis et pertinent.
