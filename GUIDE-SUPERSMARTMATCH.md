# 🚀 SuperSmartMatch - Guide d'utilisation

**SuperSmartMatch** est un algorithme de matching intelligent qui calcule des **pourcentages de correspondance côté entreprise** avec un raisonnement avancé.

## 🎯 Fonctionnalités principales

### ✅ Matching côté entreprise avec pourcentages détaillés
- **Localisation** : Temps de trajet estimé et compatibilité géographique
- **Expérience** : Adéquation niveau/poste avec analyse surqualification
- **Rémunération** : Compatibilité avec le budget entreprise
- **Compétences** : Techniques, langues, logiciels avec scores détaillés

### 🧠 Raisonnement intelligent
- **Évolution rapide** : Candidat ambitieux × Poste avec perspectives
- **Stabilité** : Candidat stable × Poste long terme  
- **Innovation** : Profil créatif × Environnement innovant
- **Leadership** : Potentiel management × Responsabilités
- **Spécialisation** : Expert technique × Poste haute technicité
- **Adaptabilité** : Polyvalent × Environnement agile

### 📊 Analyse avancée pour recruteurs
- **Profil candidat** : Type, niveau, ambition, points forts
- **Risques/Opportunités** : Analyse des risques de recrutement
- **Explications détaillées** : Justifications intelligentes des scores

## 🚀 Démarrage rapide

### 1. Démarrer le serveur
```bash
cd super-smart-match
python app.py
```

Le serveur démarre sur http://localhost:5061

### 2. Tester avec le script
```bash
chmod +x test-supersmartmatch.sh
./test-supersmartmatch.sh
```

## 📡 API Endpoints

### Health Check
```bash
GET /api/health
```
Vérifie le statut et les algorithmes disponibles.

### Algorithmes disponibles
```bash
GET /api/algorithms
```
Liste tous les algorithmes avec leurs capacités.

### Matching candidat → jobs
```bash
POST /api/match
```

**Corps de la requête :**
```json
{
  "cv_data": {
    "competences": ["Python", "Django", "React"],
    "annees_experience": 5,
    "soft_skills": ["leadership", "innovation"],
    "langues": ["Français", "Anglais"],
    "logiciels": ["Git", "Docker"]
  },
  "questionnaire_data": {
    "adresse": "Paris 15ème",
    "salaire_souhaite": 60000,
    "contrats_recherches": ["CDI"],
    "criteres_importants": {
      "evolution_rapide": true
    },
    "objectifs_carriere": {
      "evolution_rapide": true
    }
  },
  "job_data": [
    {
      "id": "job-001",
      "titre": "Lead Developer",
      "competences": ["Python", "Django"],
      "localisation": "Paris 2ème",
      "salaire": "55-70K€",
      "perspectives_evolution": true
    }
  ],
  "algorithm": "supersmartmatch",
  "limit": 10
}
```

### 🏆 Matching entreprise → candidats (NOUVEAU)
```bash
POST /api/match-candidates
```

**Corps de la requête :**
```json
{
  "job_data": {
    "id": "startup-lead-001",
    "titre": "Lead Developer",
    "entreprise": "TechStartup",
    "competences": ["Python", "Django", "React"],
    "localisation": "Paris 2ème",
    "budget_max": 75000,
    "salaire": "60-75K€",
    "experience_requise": 4,
    "perspectives_evolution": true,
    "langues_requises": ["Français", "Anglais"],
    "logiciels_requis": ["Git", "Docker"]
  },
  "candidates_data": [
    {
      "candidate_id": "cand-001",
      "cv_data": {
        "nom": "Marie Dupont",
        "competences": ["Python", "Django", "React"],
        "annees_experience": 6,
        "langues": ["Français", "Anglais"],
        "logiciels": ["Git", "Docker"]
      },
      "questionnaire_data": {
        "adresse": "Paris 11ème",
        "salaire_souhaite": 68000,
        "objectifs_carriere": {
          "evolution_rapide": true
        }
      }
    }
  ],
  "algorithm": "supersmartmatch",
  "limit": 10
}
```

## 📊 Format des résultats côté entreprise

```json
{
  "success": true,
  "matching_mode": "company_to_candidates",
  "algorithm_used": "supersmartmatch",
  "results": [
    {
      "candidate_id": "cand-001",
      "matching_score_entreprise": 87,
      "scores_detailles": {
        "localisation": {
          "pourcentage": 90,
          "details": ["Même ville - Trajet court"]
        },
        "experience": {
          "pourcentage": 95,
          "details": ["Expérience parfaite: 6 ans pour 4 ans requis"]
        },
        "remuneration": {
          "pourcentage": 80,
          "details": ["Légèrement au-dessus du budget (+9%) - Négociable"]
        },
        "competences": {
          "pourcentage": 95,
          "details": ["Compétences techniques: 3/3 requises", "Langues: 2/2 requises"]
        }
      },
      "intelligence": {
        "bonus_applique": 10,
        "raisons": ["Candidat ambitieux × Poste avec perspectives d'évolution"],
        "recommandations": ["Candidat idéal pour une promotion rapide"]
      },
      "explications_entreprise": {
        "global": "🏆 CANDIDAT EXCELLENT - Correspondance exceptionnelle sur tous les critères",
        "localisation": "✅ Localisation excellente - Pas de problème de trajet",
        "experience": "✅ Expérience parfaitement adaptée au poste",
        "remuneration": "⚖️ Négociation salariale nécessaire",
        "competences": "✅ Compétences excellentes - Candidat opérationnel immédiatement"
      },
      "analyse_risques": {
        "risques": [],
        "opportunites": [
          "Disponibilité immédiate - Recrutement rapide possible",
          "Ambitions internationales - Atout pour développement global"
        ]
      },
      "profil_candidat": {
        "type_profil": "ambitieux",
        "niveau_experience": "senior",
        "ambition": "élevée",
        "points_forts": ["polyvalent", "international"]
      }
    }
  ]
}
```

## 🎯 Critères de scoring détaillés

### 📍 Localisation (25% du score)
- **90-100%** : Même ville/quartier ou télétravail compatible
- **70-89%** : Même région, trajet < 45min
- **50-69%** : Trajet acceptable < 1h
- **30-49%** : Trajet long > 1h
- **Bonus** : Candidat mobile (+10%)

### 💼 Expérience (25% du score)
- **95%** : Expérience parfaite (ratio 1.0-1.5)
- **90%** : Légèrement surqualifié (ratio 1.5-2.0) 
- **75%** : Surqualifié (ratio > 2.0) - Risque d'ennui
- **80%** : Légèrement sous-qualifié (ratio 0.8-1.0)
- **70%** : Sous-qualifié avec potentiel (ratio 0.5-0.8)
- **40%** : Expérience insuffisante (ratio < 0.5)

### 💰 Rémunération (20% du score)
- **98%** : Candidat sous budget minimum - Économie
- **95%** : Dans la fourchette budgétaire
- **80%** : Légèrement au-dessus (+10%) - Négociable
- **60%** : Au-dessus budget (+20%) - Difficile
- **30%** : Hors budget (>20%) - Très difficile

### 🔧 Compétences (30% du score)
- **Techniques (40%)** : Correspondance compétences requises + bonus
- **Langues (30%)** : Correspondance langues requises
- **Logiciels (30%)** : Correspondance outils requis

## 🧠 Bonus Intelligence (jusqu'à +15 points)

### Correspondances intelligentes détectées :
- **+10** : Évolution rapide (candidat ambitieux + poste évolutif)
- **+8** : Stabilité (candidat stable + poste long terme)
- **+12** : Innovation (candidat créatif + environnement innovant)
- **+15** : Leadership (potentiel management + responsabilités)
- **+10** : Spécialisation (expert technique + poste technique)
- **+8** : Adaptabilité (polyvalent + environnement agile)

## 📈 Exemples d'utilisation

### Test avec cURL

#### Matching côté entreprise
```bash
curl -X POST http://localhost:5061/api/match-candidates \
  -H "Content-Type: application/json" \
  -d '{
    "job_data": {
      "titre": "Lead Developer",
      "competences": ["Python", "React"],
      "budget_max": 70000,
      "perspectives_evolution": true
    },
    "candidates_data": [
      {
        "candidate_id": "test-001",
        "cv_data": {
          "competences": ["Python", "React", "AWS"],
          "annees_experience": 5
        },
        "questionnaire_data": {
          "salaire_souhaite": 65000,
          "objectifs_carriere": {"evolution_rapide": true}
        }
      }
    ],
    "algorithm": "supersmartmatch"
  }'
```

### JavaScript (Frontend)
```javascript
// Utilisation avec le client SuperSmartMatch
const response = await fetch('http://localhost:5061/api/match-candidates', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    job_data: job,
    candidates_data: candidates,
    algorithm: 'supersmartmatch',
    limit: 10
  })
});

const result = await response.json();

// Afficher les résultats côté entreprise
result.results.forEach(candidate => {
  console.log(`Candidat: ${candidate.cv_data.nom}`);
  console.log(`Score entreprise: ${candidate.matching_score_entreprise}%`);
  console.log(`Localisation: ${candidate.scores_detailles.localisation.pourcentage}%`);
  console.log(`Explications: ${candidate.explications_entreprise.global}`);
});
```

## 🔧 Configuration et personnalisation

### Seuils de scoring
Les seuils peuvent être ajustés dans `supersmartmatch.py` :

```python
'seuils': {
    'localisation': {
        'excellent': 85,
        'bon': 70,
        'acceptable': 50,
        'limite': 30
    },
    # etc.
}
```

### Pondération des critères
```python
'ponderation': {
    'localisation': 0.25,    # 25%
    'experience': 0.25,      # 25% 
    'remuneration': 0.20,    # 20%
    'competences': 0.30      # 30%
}
```

### Bonus intelligence
```python
'bonus_intelligence': {
    'evolution_rapide': 10,
    'stabilite': 8,
    'innovation': 12,
    'leadership': 15,
    'specialisation': 10,
    'adaptabilite': 8
}
```

## 🚨 Gestion d'erreurs

### Fallback automatique
Si SuperSmartMatch rencontre une erreur, le système bascule automatiquement vers un algorithme de fallback tout en conservant la fonctionnalité.

### Logs détaillés
```bash
# Vérifier les logs du serveur
tail -f super-smart-match/logs/app.log
```

### Tests de validation
```bash
# Lancer les tests complets
./test-supersmartmatch.sh

# Test de l'API uniquement
curl http://localhost:5061/api/health
```

## 📚 Ressources supplémentaires

- **Code source** : `super-smart-match/algorithms/supersmartmatch.py`
- **API principale** : `super-smart-match/app.py`
- **Tests** : `test-supersmartmatch.sh`
- **Documentation technique** : `super-smart-match/README.md`

## 🎯 Cas d'usage recommandés

### Pour les entreprises/recruteurs :
- **Tri automatique** des candidatures avec scores précis
- **Analyse des risques** de recrutement avant entretien
- **Négociation salariale** basée sur compatibilité budget
- **Priorisation** des candidats selon critères métier

### Pour les plateformes de recrutement :
- **Matching bidirectionnel** candidat ↔ entreprise
- **Personnalisation** des algorithmes selon secteur
- **Analytics avancées** sur la qualité des matches
- **Optimisation** des taux de conversion

---

**SuperSmartMatch** révolutionne le matching en apportant l'intelligence artificielle au service des recruteurs avec des pourcentages précis et un raisonnement explicable ! 🚀
