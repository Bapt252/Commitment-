# 🔄 Changement de Port SuperSmartMatch

## ⚠️ **Mise à Jour Importante**

**SuperSmartMatch utilise maintenant le port 5061 au lieu de 5060** pour éviter les conflits avec d'autres services.

## 🚀 **Comment tester maintenant**

### **1. Démarrer SuperSmartMatch**
```bash
# Le port a été changé automatiquement
./start-supersmartmatch.sh
```

Vous verrez maintenant :
```
🌐 Service disponible sur http://localhost:5061
📊 Endpoints:
   - Health: http://localhost:5061/api/health
   - Algorithmes: http://localhost:5061/api/algorithms
   - Matching: http://localhost:5061/api/match
```

### **2. Tester le service**
```bash
# Les tests utilisent automatiquement le nouveau port
./test-supersmartmatch.sh
```

### **3. Tests manuels**
Tous les appels API utilisent maintenant le port **5061** :

```bash
# Health check
curl http://localhost:5061/api/health

# Test de matching
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"competences": ["Python"]},
    "questionnaire_data": {"adresse": "Paris"},
    "job_data": [{"id": "job1", "competences": ["Python"]}]
  }'
```

## ✅ **Avantages du changement**

- ✅ **Pas de conflit** avec le port 5060 qui était déjà utilisé
- ✅ **Service démarre** sans problème
- ✅ **Tests fonctionnent** immédiatement
- ✅ **Documentation à jour** dans tous les fichiers

## 📋 **Fichiers mis à jour**

- `super-smart-match/app.py` - Port changé de 5060 → 5061
- `start-supersmartmatch.sh` - Messages mis à jour
- `test-supersmartmatch.sh` - Tests mis à jour  
- `README-SUPERSMARTMATCH-QUICKSTART.md` - Documentation mise à jour

## 🎯 **Prêt à tester !**

Maintenant vous pouvez directement exécuter :

```bash
# Démarrer le service
./start-supersmartmatch.sh

# Dans un autre terminal - tester
./test-supersmartmatch.sh
```

Plus aucun conflit de port ! 🎉
