# 🗺️ Configuration Google Maps pour SuperSmartMatch v2.2

## 📋 Prérequis

SuperSmartMatch v2.2 utilise Google Maps Directions API pour calculer les temps de trajet précis entre le domicile du candidat et le lieu de travail.

## 🔑 1. Obtenir une clé API Google Maps

### Étape 1: Accéder à Google Cloud Console
1. Rendez-vous sur [Google Cloud Console](https://console.cloud.google.com/)
2. Connectez-vous avec votre compte Google
3. Sélectionnez un projet existant ou créez-en un nouveau

### Étape 2: Activer les APIs nécessaires
1. Dans le menu, allez à **APIs et services > Bibliothèque**
2. Recherchez et activez les APIs suivantes :
   - **Directions API** (obligatoire)
   - **Geocoding API** (recommandé)

### Étape 3: Créer une clé API
1. Allez à **APIs et services > Identifiants**
2. Cliquez sur **+ CRÉER DES IDENTIFIANTS**
3. Sélectionnez **Clé API**
4. Copiez la clé générée

### Étape 4: Sécuriser la clé API (FORTEMENT RECOMMANDÉ)
1. Cliquez sur votre clé API nouvellement créée
2. Dans **Restrictions d'application**, sélectionnez :
   - **Adresses IP** pour limiter aux serveurs autorisés
   - **Sites web** pour limiter aux domaines autorisés
3. Dans **Restrictions d'API**, sélectionnez :
   - Directions API
   - Geocoding API (si activé)

## ⚙️ 2. Configuration de l'environnement

### Option A: Variable d'environnement système
```bash
# Linux/Mac
export GOOGLE_MAPS_API_KEY="AIzaSyC-dK6ubCZ8p_dWVnKANAMxgzMRmNrP48E"

# Windows CMD
set GOOGLE_MAPS_API_KEY=AIzaSyC-dK6ubCZ8p_dWVnKANAMxgzMRmNrP48E

# Windows PowerShell
$env:GOOGLE_MAPS_API_KEY="AIzaSyC-dK6ubCZ8p_dWVnKANAMxgzMRmNrP48E"
```

### Option B: Fichier .env (RECOMMANDÉ)
```bash
# Dans le répertoire super-smart-match/
echo "GOOGLE_MAPS_API_KEY=AIzaSyC-dK6ubCZ8p_dWVnKANAMxgzMRmNrP48E" >> .env
```

### Option C: Docker Compose
```yaml
# docker-compose.yml
services:
  supersmartmatch:
    environment:
      - GOOGLE_MAPS_API_KEY=AIzaSyC-dK6ubCZ8p_dWVnKANAMxgzMRmNrP48E
```

### Option D: Configuration Python directe
```python
import os
os.environ['GOOGLE_MAPS_API_KEY'] = 'AIzaSyC-dK6ubCZ8p_dWVnKANAMxgzMRmNrP48E'
```

## 🧪 3. Tester la configuration

### Test rapide via curl
```bash
curl "https://maps.googleapis.com/maps/api/directions/json?origin=Paris&destination=Lyon&key=VOTRE_CLE_API"
```

### Test avec SuperSmartMatch
```bash
# Démarrer SuperSmartMatch
cd super-smart-match
python app.py

# Dans un autre terminal
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"adresse": "Paris 15ème"},
    "job_data": [{"localisation": "Paris 2ème"}],
    "algorithm": "supersmartmatch"
  }'
```

### Vérification logs
```bash
# Observer les logs Google Maps
tail -f logs/app.log | grep "Google Maps"

# Logs attendus si tout fonctionne :
# ✅ Google Maps API configurée
# 🗺️ Google Maps: Paris 15ème → Paris 2ème = 25 min en transport en commun
```

## 🚨 4. Gestion d'erreurs courantes

### Erreur: API Key invalide
```
Google Maps API Error: REQUEST_DENIED
```
**Solution**: Vérifiez que la clé API est correcte et que les APIs sont activées

### Erreur: Quota dépassé
```
Google Maps API Error: OVER_QUERY_LIMIT
```
**Solution**: Vérifiez votre quota dans Google Cloud Console ou activez la facturation

### Erreur: Adresse non trouvée
```
Google Maps API Error: NOT_FOUND
```
**Solution**: SuperSmartMatch utilise automatiquement le mode fallback

### Erreur: Timeout
```
⏱️ Timeout Google Maps API
```
**Solution**: Vérifiez votre connexion internet ou augmentez le timeout

### Erreur: Service indisponible
```
Google Maps API Error: UNKNOWN_ERROR
```
**Solution**: SuperSmartMatch bascule automatiquement en mode estimation

## 💰 5. Gestion des coûts

### Tarification Google Maps Directions API
- **0.005€** par calcul de trajet (juin 2024)
- **40 000 requêtes gratuites** par mois
- Au-delà: facturation progressive

### Optimisations SuperSmartMatch v2.2
- **Cache intelligent**: évite 80%+ des appels répétés
- **Cache 1h** par route calculée
- **Fallback automatique** si quota dépassé
- **Limitation modes** selon préférences candidat

### Estimation coûts
```
100 candidats/jour × 5 offres = 500 calculs/jour
Avec cache 80% → 100 vrais appels Google Maps/jour
100 × 30 jours = 3000 appels/mois
3000 × 0.005€ = 15€/mois
```

## 📊 6. Monitoring et surveillance

### Métriques à surveiller
```bash
# Nombre d'appels Google Maps
grep "Google Maps:" logs/app.log | wc -l

# Taux de cache hit
grep "Cache hit" logs/app.log | wc -l

# Erreurs Google Maps
grep "Google Maps" logs/app.log | grep -E "(ERROR|WARNING)"

# Utilisation du fallback
grep "Fallback" logs/app.log | wc -l
```

### Alertes recommandées
- **Quota proche**: > 80% du quota mensuel utilisé
- **Taux d'erreur élevé**: > 5% d'erreurs Google Maps
- **Temps de réponse élevé**: > 2s pour les calculs
- **Cache inefficace**: < 70% de cache hit

## 🎯 7. Modes de transport supportés

| Mode | Code | Description | Use Case |
|------|------|-------------|----------|
| **Voiture** | `driving` | Trafic temps réel | Candidats avec véhicule |
| **Transport public** | `transit` | Horaires temps réel | Zones urbaines |
| **Marche** | `walking` | Temps piéton | Courtes distances |
| **Vélo** | `bicycling` | Pistes cyclables | Éco-mobilité |

### Configuration préférences candidat
```json
{
  "questionnaire_data": {
    "transport_preferences": {
      "transport_prefere": "transit",
      "heure_depart_travail": "08:30",
      "temps_trajet_max": 60
    }
  }
}
```

## 🔧 8. Configuration avancée

### Timeout et cache
```python
# Dans supersmartmatch.py
'google_maps': {
    'timeout': 5,  # Secondes
    'cache_duration': 3600,  # 1h en secondes
}
```

### Régions supportées
- **France** (par défaut)
- **Europe** (configurable)
- **Monde** (selon besoins)

### Modes de fallback
Si Google Maps indisponible :
1. **Calcul approximatif** basé sur les villes
2. **Score par défaut** selon la région
3. **Mode dégradé** avec avertissement utilisateur

## 🚀 9. Mise en production

### Checklist pré-déploiement
- [ ] Clé API Google Maps configurée
- [ ] APIs Directions et Geocoding activées
- [ ] Restrictions de sécurité configurées
- [ ] Monitoring des coûts activé
- [ ] Tests fonctionnels validés
- [ ] Fallback testé (désactiver temporairement l'API)

### Variables d'environnement production
```bash
# Obligatoire
GOOGLE_MAPS_API_KEY=your_production_api_key

# Optionnel
GOOGLE_MAPS_TIMEOUT=5
GOOGLE_MAPS_CACHE_DURATION=3600
GOOGLE_MAPS_DEFAULT_MODE=driving
```

---

**SuperSmartMatch v2.2 est maintenant prêt à calculer des temps de trajet précis ! 🎉**

Pour toute question, consultez le [guide de migration v2.2](../MIGRATION_GUIDE_v22.md) ou les [logs de l'application](../logs/app.log).
