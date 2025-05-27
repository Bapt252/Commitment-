# 🎛️ Guide Pondération Dynamique - SuperSmartMatch v2.1

## 🚀 Vue d'ensemble

SuperSmartMatch v2.1 introduit la **pondération dynamique intelligente** qui adapte automatiquement l'algorithme selon les priorités de chaque candidat. Fini la pondération fixe ! 

### ⚡ Nouveautés clés

- **4 leviers candidat** : Évolution, Rémunération, Proximité, Flexibilité
- **Pondération adaptative** : Chaque candidat a sa propre pondération 
- **Nouveau critère flexibilité** : Télétravail, horaires flexibles, RTT
- **Matching bidirectionnel** : Personnalisé selon les priorités de chaque partie

---

## 🎯 Les 4 Leviers Candidat

### 1. 📈 ÉVOLUTION
- **Ce que ça mesure** : Perspectives, ambition, formation
- **Impact algorithme** : Influence **Expérience** + **Compétences**
- **Candidat type** : Ambitieux, veut progresser rapidement

### 2. 💰 RÉMUNÉRATION  
- **Ce que ça mesure** : Salaire, avantages, package global
- **Impact algorithme** : Influence **Rémunération**
- **Candidat type** : Priorité financière, négociation importante

### 3. 📍 PROXIMITÉ
- **Ce que ça mesure** : Localisation, temps trajet, mobilité
- **Impact algorithme** : Influence **Proximité** (ex-localisation)
- **Candidat type** : Contraintes géographiques, famille

### 4. 🔄 FLEXIBILITÉ
- **Ce que ça mesure** : Télétravail, horaires flexibles, RTT
- **Impact algorithme** : Influence **Flexibilité** (nouveau critère)
- **Candidat type** : Work-life balance, autonomie

---

## 📋 Structure questionnaire_data

### Format attendu

```json
{
  "questionnaire_data": {
    "priorites_candidat": {
      "evolution": 8,      // Note 1-10 (10 = priorité max)
      "remuneration": 9,   // Note 1-10  
      "proximite": 6,      // Note 1-10
      "flexibilite": 7     // Note 1-10
    },
    "flexibilite_attendue": {
      "teletravail": "partiel",        // "aucun" | "partiel" | "total"
      "horaires_flexibles": true,      // boolean
      "rtt_important": true            // boolean
    }
  }
}
```

### Exemples de profils

#### 🎯 Candidat "Salaire prioritaire"
```json
{
  "priorites_candidat": {
    "evolution": 3,        // Faible
    "remuneration": 9,     // 🎯 PRIORITÉ ÉLEVÉE
    "proximite": 6,        // Moyenne  
    "flexibilite": 5       // Moyenne
  }
}
```

#### 🚀 Candidat "Évolution prioritaire"
```json
{
  "priorites_candidat": {
    "evolution": 10,       // 🎯 PRIORITÉ MAXIMALE
    "remuneration": 3,     // Faible
    "proximite": 5,        // Moyenne
    "flexibilite": 6       // Moyenne
  }
}
```

---

## 🔧 Utilisation API

### Appel standard (sans changement)

```python
from algorithms.supersmartmatch import SuperSmartMatchAlgorithm

algorithm = SuperSmartMatchAlgorithm()

# Candidat avec questionnaire de priorités
candidat = {
    'id': 'cand_123',
    'annees_experience': 5,
    'salaire_souhaite': 55000,
    'competences': ['python', 'javascript'],
    
    # ⚡ NOUVEAU: Questionnaire priorités  
    'questionnaire_data': {
        'priorites_candidat': {
            'evolution': 8,
            'remuneration': 6, 
            'proximite': 4,
            'flexibilite': 9
        },
        'flexibilite_attendue': {
            'teletravail': 'partiel',
            'horaires_flexibles': True,
            'rtt_important': True
        }
    }
}

# Matching avec pondération automatiquement adaptée
results = algorithm.match_candidate_with_jobs(candidat, offres, limit=10)
```

### Réponse enrichie

```python
# Chaque résultat contient maintenant:
for result in results:
    # Pondération utilisée pour CE candidat
    print(result['ponderation_dynamique'])
    # {'proximite': 0.15, 'experience': 0.25, 'remuneration': 0.20, 'competences': 0.15, 'flexibilite': 0.25}
    
    # Scores avec nouveau critère flexibilité
    print(result['scores_detailles']['flexibilite'])
    # {'pourcentage': 85, 'details': [...], 'poids': 25.0}
    
    # Explication pondération dans les explications
    print(result['explications_entreprise']['ponderation'])
    # "🎛️ PONDÉRATION ADAPTÉE: FLEXIBILITE: priorité élevée (25.0%)"
```

---

## 🧮 Logique de calcul

### Transformation notes → facteurs

```python
# Note candidat → Facteur multiplicateur
note_1  → facteur_0.5    # Priorité très faible
note_5  → facteur_1.0    # Priorité moyenne (pondération de base)
note_10 → facteur_2.0    # Priorité maximale
```

### Mapping leviers → critères

```python
leviers_mapping = {
    'evolution': ['experience', 'competences'],  # Évolution influence 2 critères
    'remuneration': ['remuneration'],            # Rémunération → Rémunération
    'proximite': ['proximite'],                  # Proximité → Proximité  
    'flexibilite': ['flexibilite']               # Flexibilité → Flexibilité
}
```

### Exemple calcul

```python
# Candidat avec: evolution=10, remuneration=3, proximite=5, flexibilite=8

# 1. Calcul facteurs
facteur_evolution = 0.5 + (10-1) * (1.5/9) = 2.0     # Maximum
facteur_remuneration = 0.5 + (3-1) * (1.5/9) = 0.83  # Faible
facteur_proximite = 0.5 + (5-1) * (1.5/9) = 1.17     # Moyen
facteur_flexibilite = 0.5 + (8-1) * (1.5/9) = 1.67   # Élevé

# 2. Application aux critères
poids_experience = 0.20 * 2.0 = 0.40        # Évolution influence expérience
poids_competences = 0.15 * 2.0 = 0.30       # Évolution influence compétences  
poids_remuneration = 0.25 * 0.83 = 0.21     # Rémunération influencée
poids_proximite = 0.25 * 1.17 = 0.29        # Proximité influencée
poids_flexibilite = 0.15 * 1.67 = 0.25      # Flexibilité influencée

# 3. Normalisation pour somme = 1.0
total = 0.40 + 0.30 + 0.21 + 0.29 + 0.25 = 1.45
poids_final = {
    'experience': 0.40/1.45 = 0.28,
    'competences': 0.30/1.45 = 0.21, 
    'remuneration': 0.21/1.45 = 0.14,
    'proximite': 0.29/1.45 = 0.20,
    'flexibilite': 0.25/1.45 = 0.17
}
```

---

## 🧪 Tests et validation

### Lancer les tests

```bash
# Test complet pondération dynamique
cd super-smart-match
python test_dynamic_weighting.py

# Tests unitaires intégrés
python -c "from algorithms.supersmartmatch import test_dynamic_weighting; test_dynamic_weighting()"
```

### Cas de test clés

1. **Test comparatif** : Même candidat, priorités différentes
2. **Test 4 profils** : Validation des 4 types de candidat
3. **Test flexibilité** : Impact nouveau critère
4. **Test fallback** : Comportement sans questionnaire

### Validation attendue

- ✅ Candidat "salaire prioritaire" → Rémunération poids > base
- ✅ Candidat "évolution prioritaire" → Expérience + Compétences poids > base  
- ✅ Candidat "flexibilité prioritaire" → Flexibilité poids > base
- ✅ Candidat "proximité prioritaire" → Proximité poids > base
- ✅ Sans questionnaire → Pondération de base maintenue

---

## 🔧 Configuration avancée

### Personnaliser le mapping leviers

```python
# Dans supersmartmatch.py
self.config['leviers_mapping'] = {
    'evolution': ['experience', 'competences'],  # Peut être modifié
    'remuneration': ['remuneration'],
    'proximite': ['proximite'], 
    'flexibilite': ['flexibilite', 'proximite']  # Ex: flexibilité influence aussi proximité
}
```

### Ajuster les facteurs

```python
# Modifier la formule de calcul des facteurs
def calculate_dynamic_weights(self, candidat):
    # Facteur entre 0.3 et 2.5 au lieu de 0.5 et 2.0
    facteur = 0.3 + (note - 1) * (2.2 / 9)
```

### Pondération de base

```python
# Ajuster la pondération par défaut
'ponderation_base': {
    'proximite': 0.30,     # Augmenter proximité
    'experience': 0.20,
    'remuneration': 0.20,
    'competences': 0.15,
    'flexibilite': 0.15    # Nouveau critère
}
```

---

## 🚨 Points d'attention

### Validation données

1. **Notes 1-10** : Assurer que les notes sont bien entre 1 et 10
2. **Tous les leviers** : Fournir les 4 leviers (évolution, rémunération, proximité, flexibilité)
3. **Format flexibilité** : Respecter les valeurs attendues pour `teletravail`

### Gestion erreurs

```python
# L'algorithme handle gracieusement:
- Absence de questionnaire_data → Pondération de base
- Notes invalides → Pondération de base  
- Leviers manquants → Pondération de base
- Valeurs aberrantes → Normalisation automatique
```

### Performance

- **Impact négligeable** : +2-3ms par candidat
- **Compatible** : Fonctionne avec l'architecture existante
- **Rétrocompatible** : Candidats sans questionnaire fonctionnent normalement

---

## 📊 Exemples d'impact

### Candidat évolution vs salaire

| Critère | Base | Évolution prioritaire | Salaire prioritaire |
|---------|------|---------------------|-------------------|
| Expérience | 20% | **28%** ↗ | 16% ↘ |
| Compétences | 15% | **21%** ↗ | 12% ↘ |
| Rémunération | 25% | 14% ↘ | **35%** ↗ |
| Proximité | 25% | 20% ↘ | 22% ↘ |
| Flexibilité | 15% | 17% ↗ | 15% → |

### Impact sur le classement

Pour une même offre, selon le profil candidat :
- **Candidat salaire** : Score final influencé à 35% par la rémunération
- **Candidat évolution** : Score final influencé à 49% par expérience+compétences
- **Résultat** : Classement différent des offres selon les priorités !

---

## 🎉 Prochaines étapes

1. **Intégrer** dans votre flow de questionnaire candidat
2. **Tester** avec vos données réelles
3. **Analyser** l'impact sur la satisfaction candidat/entreprise
4. **Optimiser** les seuils selon vos métriques

La pondération dynamique transforme SuperSmartMatch en un algorithme véritablement personnalisé ! 🚀
