# 🚀 SuperSmartMatch - Configuration Complète avec Infrastructure Existante

Ce guide explique comment configurer SuperSmartMatch v2.1 avec votre infrastructure PostgreSQL + Redis existante.

## ✅ Configuration Terminée !

SuperSmartMatch est maintenant configuré pour utiliser votre infrastructure existante :

### 🗄️ **Base de Données**
- **PostgreSQL** : `postgresql://postgres:postgres@postgres:5432/nexten`
- **Redis** : `redis://redis:6379/0`
- **Partage des ressources** : Utilise les mêmes instances que vos autres services

### 🔧 **Port et Accès**
- **Port configuré** : `5062` (comme spécifié dans votre docker-compose.yml)
- **URL d'accès** : `http://localhost:5062`
- **Health Check** : `http://localhost:5062/api/v1/health`

### 📁 **Fichiers Créés/Modifiés**

#### **1. Configuration SuperSmartMatch**
```
super-smart-match/.env              # Variables d'environnement optimisées
super-smart-match/app.py            # Port configuré depuis ENV
```

#### **2. Infrastructure**
```
docker-compose.yml                  # Service SuperSmartMatch configuré
.env.example                        # Variables d'exemple mises à jour
start-supersmartmatch.sh           # Script de démarrage intelligent
```

## 🚀 **Démarrage Rapide**

### **Option 1 : Démarrage Automatique (Recommandé)**
```bash
# Rendre le script exécutable
chmod +x start-supersmartmatch.sh

# Lancer le script intelligent
./start-supersmartmatch.sh
```

Le script va :
- ✅ Vérifier les prérequis
- ✅ Configurer les variables d'environnement
- ✅ Choisir le mode de démarrage approprié
- ✅ Tester la connectivité
- ✅ Afficher les URLs d'accès

### **Option 2 : Démarrage Manuel**
```bash
# Démarrer uniquement SuperSmartMatch (si infrastructure existante)
docker-compose up -d supersmartmatch-service

# OU démarrer toute l'infrastructure
docker-compose up -d

# Vérifier le statut
curl http://localhost:5062/api/v1/health
```

## 🎯 **URLs et Endpoints**

### **SuperSmartMatch API**
- **Base URL** : `http://localhost:5062`
- **Health Check** : `GET /api/v1/health`
- **Algorithmes** : `GET /api/algorithms`
- **Matching candidat → jobs** : `POST /api/match`
- **Matching entreprise → candidats** : `POST /api/match-candidates`

### **Nouveaux Endpoints v2.1**
- **Questionnaire candidat** : `POST /api/candidate/<id>/questionnaire`
- **Analytics impact** : `POST /api/analytics/weighting-impact`
- **Profils démo** : `GET /api/demo/candidate-profiles`
- **Infos algorithme** : `GET /api/supersmartmatch/info`

### **Infrastructure Existante**
- **API Principale** : `http://localhost:5050`
- **Frontend** : `http://localhost:3000`
- **MinIO Console** : `http://localhost:9001`
- **Redis Commander** : `http://localhost:8081`

## ⚙️ **Variables d'Environnement Principales**

### **Obligatoires**
```bash
OPENAI=your_openai_api_key_here                    # Clé OpenAI pour IA
SECRET_KEY=your-super-secret-key-here              # Clé secrète unique
```

### **Infrastructure (Configuré Automatiquement)**
```bash
PORT=5062                                          # Port SuperSmartMatch
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/nexten
REDIS_URL=redis://redis:6379/0
```

### **Fonctionnalités v2.1 (Activées par Défaut)**
```bash
ENABLE_DYNAMIC_WEIGHTING=true                     # Pondération dynamique
ENABLE_INTELLIGENT_REASONING=true                 # Raisonnement IA
ENABLE_FLEXIBILITY_SCORING=true                   # Score flexibilité
ENABLE_TRAVEL_TIME_CALCULATION=true               # Calcul temps trajet
ENABLE_RISK_ANALYSIS=true                         # Analyse risques
```

## 🧪 **Test de Fonctionnement**

### **1. Health Check**
```bash
curl http://localhost:5062/api/v1/health
```

**Réponse attendue :**
```json
{
  "status": "healthy",
  "port": 5062,
  "version": "2.1",
  "supersmartmatch_available": true,
  "analytics_enabled": true
}
```

### **2. Test des Algorithmes**
```bash
curl http://localhost:5062/api/algorithms
```

### **3. Test Matching Simple**
```bash
curl -X POST http://localhost:5062/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python", "Django"],
      "annees_experience": 3
    },
    "questionnaire_data": {
      "priorites_candidat": {
        "evolution": 8,
        "remuneration": 6,
        "proximite": 4,
        "flexibilite": 9
      }
    },
    "job_data": [{
      "id": "job-001",
      "titre": "Développeur Python",
      "competences": ["Python", "Django"]
    }],
    "algorithm": "supersmartmatch"
  }'
```

## 📊 **Monitoring et Logs**

### **Logs SuperSmartMatch**
```bash
# Logs en temps réel
docker-compose logs -f supersmartmatch-service

# Logs récents
docker-compose logs --tail=50 supersmartmatch-service
```

### **État des Services**
```bash
# Vérifier tous les services
docker-compose ps

# Vérifier spécifiquement SuperSmartMatch
docker-compose ps supersmartmatch-service
```

### **Redémarrage**
```bash
# Redémarrer SuperSmartMatch seulement
docker-compose restart supersmartmatch-service

# Redémarrer toute l'infrastructure
docker-compose restart
```

## 🎛️ **Fonctionnalités v2.1 - Pondération Dynamique**

### **4 Leviers de Pondération**
1. **Évolution** (1-10) → Influence Expérience + Compétences
2. **Rémunération** (1-10) → Influence Rémunération
3. **Proximité** (1-10) → Influence Localisation
4. **Flexibilité** (1-10) → Nouveau critère (télétravail, horaires, RTT)

### **Exemple de Questionnaire Candidat**
```json
{
  "priorites_candidat": {
    "evolution": 8,        // Priorité élevée évolution
    "remuneration": 6,     // Moyenne
    "proximite": 4,        // Faible contrainte géo
    "flexibilite": 9       // Très important
  },
  "flexibilite_attendue": {
    "teletravail": "partiel",
    "horaires_flexibles": true,
    "rtt_important": true
  }
}
```

### **Raisonnement Intelligent**
- **Évolution rapide** : Candidat ambitieux × Poste évolutif
- **Stabilité** : Candidat stable × Poste long terme
- **Innovation** : Profil créatif × Environnement innovant
- **Leadership** : Potentiel management × Responsabilités
- **Spécialisation** : Expert technique × Poste technique
- **Adaptabilité** : Polyvalent × Environnement agile

## 🔧 **Résolution de Problèmes**

### **SuperSmartMatch ne démarre pas**
```bash
# Vérifier les logs
docker-compose logs supersmartmatch-service

# Vérifier les dépendances
docker-compose ps postgres redis

# Reconstruire si nécessaire
docker-compose build supersmartmatch-service
```

### **Erreur de connexion Base de Données**
```bash
# Vérifier PostgreSQL
docker exec nexten-postgres pg_isready -U postgres -d nexten

# Vérifier Redis
docker exec nexten-redis redis-cli ping
```

### **Port 5062 déjà utilisé**
```bash
# Voir qui utilise le port
lsof -i :5062

# Arrêter le processus si nécessaire
kill <PID>
```

## 🚀 **Performance et Optimisation**

### **Ressources Allouées**
- **CPU** : 1 cœur max, 0.5 cœur réservé
- **RAM** : 1 Go max, 512 Mo réservé
- **Réseau** : Réseau Docker nexten-network

### **Cache Redis**
- **TTL** : 1 heure par défaut
- **Clés** : Résultats de matching mis en cache
- **Analytics** : Métriques stockées 30 jours

### **Limites de Taux**
- **100 requêtes/minute** par IP
- **1000 requêtes/heure** par IP
- **Protection anti-abus** activée

## 📚 **Intégration avec vos Services**

### **Depuis votre API Principale**
```bash
# URL à utiliser depuis vos autres services
SUPERSMARTMATCH_SERVICE_URL=http://supersmartmatch-service:5062
```

### **Depuis le Frontend**
```javascript
// URL depuis le navigateur
const SUPERSMARTMATCH_URL = 'http://localhost:5062';

// Exemple d'appel
const response = await fetch(`${SUPERSMARTMATCH_URL}/api/match`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    cv_data: candidat,
    job_data: offres,
    algorithm: 'supersmartmatch'
  })
});
```

---

## 🎉 **SuperSmartMatch v2.1 est Prêt !**

Votre service de matching intelligent avec pondération dynamique est maintenant configuré et opérationnel avec votre infrastructure existante. 

**Profitez des nouvelles fonctionnalités v2.1 !** 🚀
