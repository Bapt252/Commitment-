# 🚀 SuperSmartMatch V2 - Guide de Test Corrigé

## ❌ **Problème identifié**

L'endpoint `/match` n'existe **PAS** sur le port 5052. Vous testiez la mauvaise route sur le mauvais service !

## ✅ **Solution : Bonnes routes identifiées**

### **Port 5052 - Service de matching classique**
```bash
# ✅ Health check
curl http://localhost:5052/health

# ✅ Route principale V1 
curl -X POST http://localhost:5052/api/v1/queue-matching \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test-candidate-123",
    "job_id": "test-job-456",
    "webhook_url": "https://example.com/webhook"
  }'
```

### **Port 5062 - SuperSmartMatch V2** 
```bash
# ✅ Health check
curl http://localhost:5062/health

# ✅ Route V2 principale (format étendu)
curl -X POST http://localhost:5062/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Test User",
      "technical_skills": [
        {"name": "Python", "level": "Expert", "years": 5}
      ]
    },
    "offers": [
      {
        "id": "test-job",
        "title": "Développeur Python",
        "required_skills": ["Python", "Django"]
      }
    ],
    "algorithm": "auto"
  }'

# ✅ Route compatible V1 (format simplifié)
curl -X POST http://localhost:5062/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Test User",
      "technical_skills": ["Python", "Django"]
    },
    "offers": [
      {
        "id": "test-job",
        "title": "Développeur Python",
        "required_skills": ["Python", "Django"]
      }
    ]
  }'
```

## 🔧 **Tests rapides**

### **1. Test immédiat - Format corrigé**
```bash
# Test SuperSmartMatch V2 avec le bon format
curl -X POST http://localhost:5062/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Jean Dupont",
      "technical_skills": [
        {"name": "Python", "level": "Advanced", "years": 3},
        {"name": "Django", "level": "Intermediate", "years": 2}
      ]
    },
    "offers": [
      {
        "id": "dev-python-123",
        "title": "Développeur Python Senior",
        "required_skills": ["Python", "Django", "PostgreSQL"]
      }
    ]
  }'
```

### **2. Test service classique V1**
```bash
# Test service matching classique (port 5052)
curl -X POST http://localhost:5052/api/v1/queue-matching \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "jean-dupont-456",
    "job_id": "dev-python-123",
    "webhook_url": "https://webhook.example.com/callback"
  }'
```

## 📊 **Différences clés**

| Service | Port | Route principale | Format |
|---------|------|------------------|---------|
| **Matching classique** | 5052 | `/api/v1/queue-matching` | `candidate_id` + `job_id` |
| **SuperSmartMatch V2** | 5062 | `/api/v2/match` | Objets `candidate` + `offers` |

## 🧠 **Format de données correct**

### **V1 (Port 5052)**
```json
{
  "candidate_id": "string",
  "job_id": "string", 
  "webhook_url": "string"
}
```

### **V2 (Port 5062)**
```json
{
  "candidate": {
    "name": "string",
    "technical_skills": [
      {"name": "Python", "level": "Expert", "years": 5}
    ]
  },
  "offers": [
    {
      "id": "string",
      "title": "string", 
      "required_skills": ["Python", "Django"]
    }
  ]
}
```

## 🚀 **Scripts de test automatisés**

```bash
# Rendre les scripts exécutables
chmod +x test-supersmartmatch-v2-corrected.sh
chmod +x test-supersmartmatch-advanced.sh

# Test basique corrigé
./test-supersmartmatch-v2-corrected.sh

# Test avancé complet
./test-supersmartmatch-advanced.sh
```

## 🎯 **Commandes de debug**

```bash
# Vérifier quels services sont actifs
netstat -tlnp | grep :505

# Tester la connectivité
curl -I http://localhost:5052/health
curl -I http://localhost:5062/health

# Voir les logs en temps réel
docker logs -f matching-service
docker logs -f supersmartmatch-v2
```

## ⚡ **Solution EXPRESS**

Si vous voulez juste tester **maintenant** :

```bash
# Test rapide port 5062 (SuperSmartMatch V2)
curl -X POST http://localhost:5062/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {"name": "Test", "technical_skills": ["Python"]},
    "offers": [{"id": "1", "title": "Dev", "required_skills": ["Python"]}]
  }'
```

## 📋 **Résumé**

✅ **Problème résolu** : Utilisez `/api/v1/queue-matching` sur le port 5052 OU `/api/v2/match` sur le port 5062

✅ **Scripts corrigés** : Disponibles dans le repo avec les bonnes routes

✅ **Format correct** : `"candidate"` et `"offers"` au lieu de `"cv_data"` et `"job_data"`

🎯 **Utilisez ces routes pour vos tests SuperSmartMatch V2 !**
