# SuperSmartMatch v2.1 - Service Unifié de Matching avec Pondération Dynamique

SuperSmartMatch est un service backend unifié qui regroupe **TOUS** vos algorithmes de matching sous une seule API moderne et performante. Il simplifie l'intégration avec votre front-end existant et vous permet de choisir le meilleur algorithme selon le contexte.

## 🚀 **NOUVEAUTÉS v2.1 - Pondération Dynamique**

### ⚡ **Révolution du Matching Personnalisé**

✨ **Pondération dynamique** : Chaque candidat a sa propre pondération automatiquement adaptée  
✨ **4 leviers candidat** : Évolution, Rémunération, Proximité, Flexibilité  
✨ **Nouveau critère flexibilité** : Télétravail, horaires flexibles, RTT  
✨ **Matching bidirectionnel** : Personnalisé selon les priorités de chaque partie  
✨ **Questionnaire intelligent** : Notes 1-10 qui adaptent l'algorithme  

### 🎛️ **Les 4 Leviers Candidat**

| Levier | Impact Algorithme | Candidat Type |
|--------|------------------|---------------|
| 📈 **ÉVOLUTION** | Influence **Expérience** + **Compétences** | Ambitieux, veut progresser |
| 💰 **RÉMUNÉRATION** | Influence **Rémunération** | Priorité financière |
| 📍 **PROXIMITÉ** | Influence **Proximité** | Contraintes géographiques |
| 🔄 **FLEXIBILITÉ** | Influence **Flexibilité** (nouveau) | Work-life balance |

---

## 🎯 **Objectifs atteints**

✅ **Service unifié** : Tous les algorithmes accessibles via une seule API  
✅ **Sélection intelligente** : Choix automatique du meilleur algorithme  
✅ **Pondération dynamique** : Adaptation automatique aux priorités candidat ⭐ **NOUVEAU**  
✅ **Mode comparaison** : Test de tous les algorithmes simultanément  
✅ **Algorithme hybride** : Combine les résultats pour optimiser la précision  
✅ **Facilité d'intégration** : Compatible avec votre front-end existant  
✅ **Performance optimisée** : Exécution rapide et gestion intelligente des erreurs  

## 🧠 **Algorithmes intégrés**

| Algorithme | Description | Usage recommandé |
|------------|-------------|------------------|
| **`supersmartmatch`** ⭐ | Algorithme v2.1 avec pondération dynamique | **Usage recommandé v2.1** |
| **`enhanced`** | Moteur amélioré avec pondération dynamique | Usage général |
| **`smart_match`** | Algorithme bidirectionnel avec géolocalisation | Matching géographique |
| **`original`** | Algorithme de base avec calculs standards | Tests de référence |
| **`custom`** | Votre algorithme personnalisé optimisé | Cas spécifiques |
| **`hybrid`** | Combine tous les algorithmes | Meilleure précision |
| **`auto`** | Sélection intelligente automatique | Mode par défaut |
| **`comparison`** | Exécute tous et compare les résultats | Analyse et debug |

## 🚀 **Installation et démarrage**

### 1. Démarrage rapide
```bash
# Rendre les scripts exécutables
chmod +x start-super-smart-match.sh
chmod +x test-super-smart-match.sh

# Démarrer le service
./start-super-smart-match.sh

# Dans un autre terminal, tester l'API
./test-super-smart-match.sh
```

### 2. Test de la pondération dynamique v2.1
```bash
cd super-smart-match
python test_dynamic_weighting.py
```

### 3. Démarrage manuel
```bash
cd super-smart-match
pip install -r requirements.txt
python app.py
```

### 4. Avec Docker
```bash
cd super-smart-match
docker build -t super-smart-match .\ndocker run -p 5060:5060 super-smart-match
```

Le service sera disponible sur `http://localhost:5060`

## 📡 **API Endpoints**

### **Health Check**
```bash
GET /api/health
```
Vérifie le statut du service et les algorithmes chargés.

### **Liste des algorithmes**
```bash
GET /api/algorithms
```
Retourne la liste des algorithmes disponibles avec leurs descriptions.

### ⚡ **Matching principal v2.1 avec pondération dynamique**
```bash
POST /api/match
```

**Body JSON avec questionnaire candidat :**
```json
{
  "cv_data": {
    "competences": ["Python", "React", "Django"],
    "annees_experience": 3,
    "formation": "Master Informatique"
  },
  "questionnaire_data": {
    "contrats_recherches": ["CDI"],
    "adresse": "Paris",
    "salaire_souhaite": 50000,
    "mobilite": "hybrid",
    
    // ⚡ NOUVEAU v2.1: Priorités candidat
    "priorites_candidat": {
      "evolution": 8,        // Note 1-10 (10 = priorité max)
      "remuneration": 6,     // Note 1-10  
      "proximite": 4,        // Note 1-10
      "flexibilite": 9       // Note 1-10
    },
    
    // ⚡ NOUVEAU v2.1: Attentes flexibilité
    "flexibilite_attendue": {
      "teletravail": "partiel",        // "aucun" | "partiel" | "total"
      "horaires_flexibles": true,      // boolean
      "rtt_important": true            // boolean
    }
  },
  "job_data": [
    {
      "id": 1,
      "titre": "Développeur Full Stack",
      "competences": ["Python", "React", "Django"],
      "type_contrat": "CDI",
      "salaire": "45K-55K€",
      "localisation": "Paris",
      
      // ⚡ NOUVEAU v2.1: Critères flexibilité offre
      "politique_remote": "télétravail partiel possible",
      "horaires_flexibles": true,
      "jours_rtt": 15
    }
  ],
  "algorithm": "supersmartmatch",  // ⚡ Utiliser v2.1
  "limit": 10
}
```

### ⚡ **Nouveaux endpoints v2.1**

#### **Questionnaire candidat**
```bash
POST /api/candidate/<candidate_id>/questionnaire
```

#### **Analytics pondération dynamique**
```bash
POST /api/analytics/weighting-impact
```

#### **Profils démo**
```bash
GET /api/demo/candidate-profiles
```

**Paramètres :**
- `algorithm` : `"supersmartmatch"`, `"auto"`, `"enhanced"`, `"hybrid"`, `"comparison"`, etc.
- `limit` : Nombre maximum de résultats (défaut: 10)

## 🔄 **Modes de fonctionnement**

### ⚡ **Mode SUPERSMARTMATCH v2.1 (recommandé)**
```json
{"algorithm": "supersmartmatch"}
```
- **Pondération dynamique** basée sur les priorités candidat
- **Nouveau critère flexibilité** (télétravail, horaires, RTT)
- **Matching bidirectionnel** personnalisé
- **4 leviers candidat** pour adaptation automatique

### **Mode AUTO (intelligent)**
```json
{"algorithm": "auto"}
```
Sélectionne automatiquement le meilleur algorithme selon :
- Présence de questionnaire candidat → SuperSmartMatch v2.1
- Nombre de compétences du candidat
- Nombre d'offres à analyser
- Présence de données géographiques
- Présence d'informations salariales

### **Mode HYBRID (meilleure précision)**
```json
{"algorithm": "hybrid"}
```
- Exécute plusieurs algorithmes en parallèle
- Combine les résultats avec pondération intelligente
- Ajoute un bonus de consensus
- Optimal pour la précision

### **Mode COMPARISON (analyse)**
```json
{"algorithm": "comparison"}
```
- Exécute TOUS les algorithmes
- Compare les performances et résultats
- Idéal pour l'analyse et le debug
- Retourne des statistiques détaillées

## 🎨 **Intégration avec votre front-end**

### **JavaScript v2.1 (avec pondération dynamique)**
```javascript
// Exemple d'intégration v2.1 avec questionnaire candidat
async function performMatchingV21(cvData, questionnaireData, jobData) {
    const response = await fetch('http://localhost:5060/api/match', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            cv_data: cvData,
            questionnaire_data: {
                ...questionnaireData,
                
                // ⚡ NOUVEAU: Ajouter les priorités candidat
                priorites_candidat: {
                    evolution: 8,        // Récupéré du formulaire candidat
                    remuneration: 6,     // Récupéré du formulaire candidat
                    proximite: 4,        // Récupéré du formulaire candidat
                    flexibilite: 9       // Récupéré du formulaire candidat
                },
                
                flexibilite_attendue: {
                    teletravail: 'partiel',
                    horaires_flexibles: true,
                    rtt_important: true
                }
            },
            job_data: jobData,
            algorithm: 'supersmartmatch',  // ⚡ Utiliser v2.1
            limit: 10
        })
    });
    
    const result = await response.json();
    
    if (result.error) {
        console.error('Erreur de matching:', result.error);
        return [];
    }
    
    console.log(`Algorithme utilisé: ${result.algorithm_used}`);
    console.log(`Pondération dynamique: ${JSON.stringify(result.results[0]?.ponderation_dynamique)}`);
    console.log(`Temps d'exécution: ${result.execution_time}s`);
    
    return result.results;
}

// Fonction pour créer le questionnaire candidat
function createCandidateQuestionnaire() {
    return {
        // Questions priorités (échelle 1-10)
        "Quelle importance accordez-vous à l'évolution de carrière?": 8,
        "Quelle importance accordez-vous à la rémunération?": 6,
        "Quelle importance accordez-vous à la proximité du travail?": 4,
        "Quelle importance accordez-vous à la flexibilité?": 9,
        
        // Questions flexibilité
        "Souhaitez-vous du télétravail?": "partiel",
        "Souhaitez-vous des horaires flexibles?": true,
        "Les RTT sont-ils importants pour vous?": true
    };
}

// Utilisation complète v2.1
const candidateQuestionnaire = createCandidateQuestionnaire();
const matchingResults = await performMatchingV21(
    candidateData.cv,
    candidateQuestionnaire,
    availableJobs
);

// Afficher les nouveaux résultats v2.1
displayMatchingResultsV21(matchingResults);
```

### **Affichage des résultats v2.1**
```javascript
function displayMatchingResultsV21(results) {
    results.forEach(result => {
        // Score traditionnel
        console.log(`Score: ${result.matching_score_entreprise}%`);
        
        // ⚡ NOUVEAU: Pondération utilisée
        console.log('Pondération adaptée:', result.ponderation_dynamique);
        
        // ⚡ NOUVEAU: Score flexibilité
        console.log(`Flexibilité: ${result.scores_detailles.flexibilite.pourcentage}%`);
        
        // ⚡ NOUVEAU: Explication personnalisée
        if (result.explications_entreprise.ponderation) {
            console.log(result.explications_entreprise.ponderation);
        }
    });
}
```

### **Modification minimale de vos pages**
Pour intégrer SuperSmartMatch v2.1 dans vos pages existantes, remplacez simplement l'algorithme :

```javascript
// Ancien code
const body = {
    // ...vos données
    algorithm: 'enhanced'
};

// Nouveau code avec SuperSmartMatch v2.1
const body = {
    // ...vos données + questionnaire candidat
    algorithm: 'supersmartmatch'
};
```

## 📊 **Réponses de l'API v2.1**

### **Réponse standard v2.1**
```json
{
  "algorithm_used": "supersmartmatch",
  "version": "2.1",
  "execution_time": 0.142,
  "total_results": 3,
  "results": [
    {
      "id": 1,
      "titre": "Développeur Full Stack",
      "matching_score_entreprise": 95,  // Score côté entreprise
      
      // ⚡ NOUVEAU: Pondération utilisée pour CE candidat
      "ponderation_dynamique": {
        "proximite": 0.15,
        "experience": 0.28,
        "remuneration": 0.14,
        "competences": 0.21,
        "flexibilite": 0.22
      },
      
      // ⚡ NOUVEAU: Scores détaillés avec flexibilité
      "scores_detailles": {
        "proximite": {
          "pourcentage": 85,
          "details": ["Même ville - Trajet court"],
          "poids": 15.0
        },
        "experience": {
          "pourcentage": 95,
          "details": ["Expérience parfaite: 5 ans pour 5 ans requis"],
          "poids": 28.0
        },
        "remuneration": {
          "pourcentage": 90,
          "details": ["Dans la fourchette budgétaire"],
          "poids": 14.0
        },
        "competences": {
          "pourcentage": 92,
          "details": ["Compétences techniques: 3/3 requises"],
          "poids": 21.0
        },
        "flexibilite": {  // ⚡ NOUVEAU CRITÈRE
          "pourcentage": 88,
          "details": ["Télétravail partiel compatible", "Horaires flexibles disponibles"],
          "poids": 22.0
        }
      },
      
      // ⚡ NOUVEAU: Explications avec pondération
      "explications_entreprise": {
        "global": "🏆 CANDIDAT EXCELLENT - Correspondance exceptionnelle",
        "ponderation": "🎛️ PONDÉRATION ADAPTÉE: FLEXIBILITE: priorité élevée (22.0%)"
      }
    }
  ]
}
```

### **Réponse analytics pondération dynamique**
```json
{
  "has_questionnaire": true,
  "dynamic_weights": {
    "proximite": 0.15,
    "experience": 0.28,
    "remuneration": 0.14,
    "competences": 0.21,
    "flexibilite": 0.22
  },
  "fixed_weights": {
    "proximite": 0.25,
    "experience": 0.20,
    "remuneration": 0.25,
    "competences": 0.15,
    "flexibilite": 0.15
  },
  "impact_statistics": {
    "avg_score_difference": 8.5,
    "jobs_improved_ranking": 2,
    "jobs_degraded_ranking": 1
  },
  "recommendations": [
    "La pondération dynamique améliore significativement les scores (+8.5% en moyenne)",
    "Le levier 'flexibilite' domine la personnalisation du matching"
  ]
}
```

## ⚡ **Performances v2.1**

### **Benchmarks typiques**
- **SuperSmartMatch v2.1** : ~180ms pour 10 offres (avec pondération dynamique)
- **Enhanced** : ~150ms pour 10 offres
- **Smart Match** : ~200ms pour 10 offres  
- **Hybrid** : ~400ms pour 10 offres (précision maximale)
- **Comparison** : ~600ms pour 10 offres (mode debug)

### **Optimisations v2.1**
- Calcul pondération dynamique en cache
- Scoring flexibilité optimisé
- Fallback intelligent sans questionnaire
- Parallélisation critères v2.1

## 🧪 **Tests et validation v2.1**

### **Lancer les tests de pondération dynamique**
```bash
cd super-smart-match

# Tests complets v2.1
python test_dynamic_weighting.py

# Tests unitaires intégrés
python -c "from algorithms.supersmartmatch import test_dynamic_weighting; test_dynamic_weighting()"

# Test comparatif fixe vs dynamique
python example_integration_v21.py
```

### **Validation des 4 leviers candidat**
- ✅ Candidat "salaire prioritaire" → Rémunération poids > base
- ✅ Candidat "évolution prioritaire" → Expérience + Compétences poids > base  
- ✅ Candidat "flexibilité prioritaire" → Flexibilité poids > base
- ✅ Candidat "proximité prioritaire" → Proximité poids > base
- ✅ Sans questionnaire → Pondération de base maintenue

## 🔧 **Configuration avancée v2.1**

### **Personnaliser le mapping leviers candidat**
```python
# Dans supersmartmatch.py
self.config['leviers_mapping'] = {
    'evolution': ['experience', 'competences'],  # Évolution influence 2 critères
    'remuneration': ['remuneration'],            # Direct
    'proximite': ['proximite'],                  # Direct
    'flexibilite': ['flexibilite', 'proximite'] # Flexibilité peut aussi influencer proximité
}
```

### **Ajuster la pondération de base v2.1**
```python
'ponderation_base': {
    'proximite': 0.25,      # Proximité (ex-localisation)
    'experience': 0.20,     # Expérience
    'remuneration': 0.25,   # Rémunération  
    'competences': 0.15,    # Compétences
    'flexibilite': 0.15     # ⚡ NOUVEAU: Flexibilité
}
```

### **Variables d'environnement**
```bash
export PORT=5060                    # Port du service
export FLASK_ENV=production         # Mode Flask
export PYTHONPATH=/app             # Chemin Python
export SUPERSMARTMATCH_VERSION=2.1  # Version explicite
```

## 🐛 **Dépannage v2.1**

### **Problèmes spécifiques v2.1**

**1. "Questionnaire invalide"**
```bash
# Vérifier la structure questionnaire_data
curl -X POST http://localhost:5060/api/candidate/test/questionnaire \
  -H "Content-Type: application/json" \
  -d '{"priorites_candidat": {"evolution": 8, "remuneration": 6, "proximite": 4, "flexibilite": 9}}'
```

**2. "Pondération non calculée"**
```bash
# Vérifier les logs de calculate_dynamic_weights
python -c "
from algorithms.supersmartmatch import SuperSmartMatchAlgorithm
algo = SuperSmartMatchAlgorithm()
candidat = {'questionnaire_data': {'priorites_candidat': {'evolution': 8, 'remuneration': 6, 'proximite': 4, 'flexibilite': 9}}}
print(algo.calculate_dynamic_weights(candidat))
"
```

**3. "Critère flexibilité manquant"**
```bash
# Vérifier que les offres contiennent les champs flexibilité
# politique_remote, horaires_flexibles, jours_rtt
```

### **Logs de debug v2.1**
```bash
# Activer les logs détaillés pour v2.1
export FLASK_ENV=development
export SUPERSMARTMATCH_DEBUG=true
python app.py
```

## 📈 **Exemples d'impact v2.1**

### **Candidat évolution vs salaire**

| Critère | Base | Évolution prioritaire | Salaire prioritaire |
|---------|------|---------------------|-------------------|
| Expérience | 20% | **28%** ↗ | 16% ↘ |
| Compétences | 15% | **21%** ↗ | 12% ↘ |
| Rémunération | 25% | 14% ↘ | **35%** ↗ |
| Proximité | 25% | 20% ↘ | 22% ↘ |
| Flexibilité | 15% | 17% ↗ | 15% → |

### **Impact sur le classement**

Pour une même offre, selon le profil candidat :
- **Candidat salaire** : Score final influencé à 35% par la rémunération
- **Candidat évolution** : Score final influencé à 49% par expérience+compétences
- **Candidat flexibilité** : Score final influencé à 25% par la flexibilité
- **Résultat** : Classement complètement différent selon les priorités ! 🎯

## 📚 **Documentation complète v2.1**

- **[Guide Pondération Dynamique](PONDERATION_DYNAMIQUE_GUIDE.md)** - Documentation complète v2.1
- **[Exemple d'intégration](example_integration_v21.py)** - Code Flask d'exemple
- **[Tests de validation](test_dynamic_weighting.py)** - Tests complets v2.1

## 🎯 **Roadmap v2.2**

### **Version 2.2 (prochaine)**
- [ ] Machine Learning pour optimiser les facteurs de pondération
- [ ] Interface web d'administration des priorités candidat  
- [ ] Analytics avancés impact pondération dynamique
- [ ] Support A/B testing pondération fixe vs dynamique

### **Version 2.3**
- [ ] Pondération côté entreprise (critères recruteur)
- [ ] Matching multidirectionnel (candidat ↔ entreprise ↔ poste)
- [ ] Apprentissage automatique des préférences
- [ ] API GraphQL pour flexibilité avancée

## 📞 **Support v2.1**

- **Documentation** : [Guide Pondération Dynamique](PONDERATION_DYNAMIQUE_GUIDE.md)
- **Tests** : `python test_dynamic_weighting.py`
- **Exemples** : `python example_integration_v21.py`
- **Logs** : Consultez la sortie console du service
- **Issues** : Utilisez les issues GitHub du projet

---

**SuperSmartMatch v2.1** révolutionne le matching avec la pondération dynamique ! Chaque candidat a maintenant son algorithme personnalisé selon ses priorités réelles. 🚀✨

### 🎉 **Résumé des bénéfices v2.1**

✨ **Pour les candidats** : Matching personnalisé selon LEURS priorités réelles  
✨ **Pour les entreprises** : Candidats mieux qualifiés et plus motivés  
✨ **Pour les recruteurs** : Compréhension fine des motivations candidat  
✨ **Pour la plateforme** : Différenciation concurrentielle majeure  

La révolution du matching intelligent commence maintenant ! 🎯
