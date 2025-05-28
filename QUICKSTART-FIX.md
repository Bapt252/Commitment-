# 🚀 Guide de Démarrage Rapide - Fix SuperSmartMatch

## ⚡ Solution en 2 étapes

### 1️⃣ Appliquer le fix automatique
```bash
chmod +x fix-numpy-compatibility.sh
./fix-numpy-compatibility.sh
```

### 2️⃣ Démarrer SuperSmartMatch
```bash
./start-supersmartmatch-fixed.sh
```

## ✅ C'est tout !

Votre SuperSmartMatch devrait maintenant fonctionner correctement sur http://localhost:5061

---

## 🔍 Vérification rapide

Si vous voulez vérifier que tout fonctionne :

```bash
# Test de l'API
curl http://localhost:5061/api/health

# Test de matching
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"competences": ["Python"], "annees_experience": 3},
    "questionnaire_data": {"adresse": "Paris"},
    "job_data": [{"id": "1", "titre": "Développeur", "competences": ["Python"]}],
    "algorithm": "auto"
  }'
```

## 🆘 En cas de problème

1. **Relancer le fix :** `./fix-numpy-compatibility.sh`
2. **Vérifier les logs** du script de fix
3. **Consulter** le fichier [NUMPY-COMPATIBILITY-FIX.md](./NUMPY-COMPATIBILITY-FIX.md) pour plus de détails

---

## 📋 Ce qui a été corrigé

- ✅ Conflit NumPy 2.x vs TensorFlow
- ✅ Erreurs `_ARRAY_API not found`
- ✅ Erreurs `numpy.dtype size changed`
- ✅ Imports TensorFlow sécurisés
- ✅ Warnings supprimés
- ✅ Environnement virtuel optimisé

**Votre SuperSmartMatch est maintenant prêt à l'emploi !** 🎉
