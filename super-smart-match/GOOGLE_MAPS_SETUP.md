# 🗺️ Configuration Google Maps pour SuperSmartMatch v2.2

## 📋 Prérequis

### 1. Créer une clé API Google Maps

1. **Accéder à Google Cloud Console** : https://console.cloud.google.com/
2. **Créer un projet** (ou utiliser un existant)
3. **Activer les APIs nécessaires** :
   - **Directions API** (obligatoire)
   - **Geocoding API** (recommandé)
   - **Maps JavaScript API** (optionnel pour interface web)

4. **Créer une clé API** :
   - Aller dans "Identifiants" → "Créer des identifiants" → "Clé API"
   - Noter la clé générée

5. **Configurer les restrictions** (recommandé) :
   - Restriction par IP pour la sécurité
   - Restriction aux APIs Directions et Geocoding

### 2. Configuration dans l'environnement

#### Option A: Variable d'environnement
```bash
export GOOGLE_MAPS_API_KEY="votre_cle_api_ici"
```

#### Option B: Fichier .env
```bash
# Dans le fichier .env du projet
GOOGLE_MAPS_API_KEY=votre_cle_api_ici
```

#### Option C: Configuration Docker
```yaml
# Dans docker-compose.yml
services:
  super-smart-match:
    environment:
      - GOOGLE_MAPS_API_KEY=votre_cle_api_ici
```

## 🚀 Utilisation

### Structure du questionnaire mise à jour

```json
{
  "questionnaire_data": {
    "priorites_candidat": {
      "evolution": 7,
      "remuneration": 8,
      "proximite": 9,
      "flexibilite": 6
    },
    "transport_preferences": {
      "transport_prefere": "transit",
      "heure_depart_travail": "08:30",
      "temps_trajet_max": 60
    },
    "flexibilite_attendue": {
      "teletravail": "partiel",
      "horaires_flexibles": true,
      "rtt_important": true
    }
  }
}
```

### Modes de transport supportés

- **`driving`** : Voiture (avec trafic temps réel)
- **`transit`** : Transport en commun (horaires temps réel)
- **`walking`** : À pied
- **`bicycling`** : Vélo

### Exemple d'appel API

```bash
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python", "React"],
      "adresse": "Paris 15ème"
    },
    "questionnaire_data": {
      "priorites_candidat": {
        "proximite": 9,
        "evolution": 7,
        "remuneration": 6,
        "flexibilite": 5
      },
      "transport_preferences": {
        "transport_prefere": "transit",
        "heure_depart_travail": "08:30"
      }
    },
    "job_data": [{
      "id": "job-001",
      "titre": "Développeur Full Stack",
      "localisation": "Paris 2ème",
      "salaire": "50-60K€"
    }],
    "algorithm": "supersmartmatch"
  }'
```

### Réponse avec informations de trajet

```json
{
  "results": [
    {
      "matching_score_entreprise": 85,
      "scores_detailles": {
        "proximite": {
          "pourcentage": 90,
          "details": [
            "🗺️ 25min en transport en commun",
            "📍 Distance: 8.2 km",
            "🚇 Lignes: 8 (Métro), RER A (RER)"
          ],
          "travel_info": {
            "duration_minutes": 25,
            "duration_text": "25 min",
            "distance_km": 8.2,
            "distance_text": "8.2 km",
            "mode": "transit",
            "mode_text": "en transport en commun",
            "transit_details": [
              {"line": "8", "type": "SUBWAY"},
              {"line": "RER A", "type": "HEAVY_RAIL"}
            ]
          }
        }
      }
    }
  ]
}
```

## ⚙️ Configuration avancée

### Personnaliser les seuils de temps

```python
# Dans supersmartmatch.py
'seuils_temps': {  # En minutes
    'excellent': 15,    # < 15min = Excellent
    'tres_bon': 25,     # 15-25min = Très bon
    'bon': 40,          # 25-40min = Bon
    'acceptable': 60,   # 40-60min = Acceptable
    'limite': 90,       # 60-90min = Limite
    'difficile': 120    # > 90min = Difficile
}
```

### Cache et performance

- **Cache automatique** : 1h par défaut
- **Timeout API** : 5 secondes
- **Gestion d'erreurs** : Fallback automatique sur l'ancien système

### Monitoring des appels API

```python
# Log des appels Google Maps
logger.info(f"🗺️ Google Maps: {origin} → {destination} = {duration_text} {mode_text}")
```

## 🔧 Dépannage

### Erreurs courantes

1. **"ZERO_RESULTS"** : Adresses non trouvées
   - Vérifier le format des adresses
   - Utiliser des adresses plus précises

2. **"OVER_QUERY_LIMIT"** : Quota API dépassé
   - Vérifier la facturation Google Cloud
   - Optimiser le cache

3. **"REQUEST_DENIED"** : Clé API invalide
   - Vérifier la clé API
   - Vérifier les restrictions

### Mode dégradé

Si Google Maps n'est pas disponible :
- Fallback automatique sur l'ancien système
- Message dans les logs : `"⚠️ Calcul approximatif - Google Maps non disponible"`
- Fonctionnalité préservée avec scores estimés

## 💰 Coûts Google Maps

### Tarification (indicatif)

- **Directions API** : ~0.005€ par requête
- **1000 calculs/jour** : ~5€/mois
- **Première tranche gratuite** : 40,000 requêtes/mois

### Optimisation des coûts

1. **Cache intelligent** : Évite les appels répétés
2. **Limitation des modes** : Tester seulement les modes pertinents
3. **Batch processing** : Grouper les calculs si possible

## 🧪 Test de l'intégration

```bash
# Test direct de l'algorithme
cd super-smart-match
python algorithms/supersmartmatch.py

# Test complet via API
curl http://localhost:5061/api/health
```

## 📊 Métriques et analytics

Le système fournit maintenant :
- **Temps de trajet précis** par mode de transport
- **Distance réelle** en km
- **Détails des lignes** de transport en commun
- **Comparaison des modes** de transport
- **Scores adaptatifs** selon les préférences

---

**SuperSmartMatch v2.2 avec Google Maps** offre une précision inégalée dans l'évaluation des temps de trajet pour un matching candidat-poste optimal ! 🚀
