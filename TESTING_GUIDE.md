# 🧪 Guide de Test de l'Algorithme de Matching

Ce guide vous explique comment tester et modifier l'algorithme de matching sur le projet Commitment.

## 🚀 Démarrage Rapide

```bash
# 1. Récupérer les dernières modifications
git pull origin main

# 2. Rendre le script exécutable
chmod +x quick_test.sh

# 3. Lancer le test interactif
./quick_test.sh
```

## 📋 Options de Test Disponibles

### Option 1: Test Direct (Recommandé) ⭐
```bash
python test_algorithm_direct.py
```
**Avantages:**
- ✅ Aucun serveur requis
- ✅ Tests multiples automatiques
- ✅ Analyse détaillée des résultats
- ✅ Métriques de performance

### Option 2: API de Test
```bash
python test_algorithm.py
# Puis dans un autre terminal:
curl http://localhost:8001/test-simple
```
**Avantages:**
- ✅ Interface web interactive
- ✅ Tests via HTTP
- ✅ Documentation Swagger

### Option 3: Test Ultra-Rapide
```bash
python -c "from matching_engine import match_candidate_with_jobs; print('Test OK')"
```

## 🔍 Comprendre les Résultats

L'algorithme actuel utilise ces critères :

| Critère | Poids | Description |
|---------|-------|-------------|
| **Compétences** | 30% | Correspondance des skills techniques |
| **Localisation** | 20% | Distance et temps de trajet |
| **Type de contrat** | 15% | CDI/CDD/Freelance... |
| **Salaire** | 15% | Correspondance avec attentes |
| **Expérience** | 10% | Années d'expérience requises |
| **Disponibilité** | 10% | Date de début de poste |

## 🔧 Intégrer Votre Algorithme

### Étape 1: Analyser l'existant
```bash
# Comprendre le fonctionnement actuel
python test_algorithm_direct.py
```

### Étape 2: Créer votre version
```bash
# Copier le moteur existant
cp matching_engine.py my_matching_engine.py

# Modifier la fonction principale:
# match_candidate_with_jobs(cv_data, questionnaire_data, job_data, limit)
```

### Étape 3: Tester votre version
```bash
# Dans test_algorithm_direct.py, ligne 8:
# Remplacer: from matching_engine import match_candidate_with_jobs
# Par:       from my_matching_engine import match_candidate_with_jobs

python test_algorithm_direct.py
```

### Étape 4: Comparer les performances
```bash
# Créer un script de comparaison
python -c "
from matching_engine import match_candidate_with_jobs as algo_original
from my_matching_engine import match_candidate_with_jobs as algo_custom
import time

# Données de test
cv_data = {...}
questionnaire_data = {...}
job_data = [...]

# Test algorithme original
start = time.time()
results_original = algo_original(cv_data, questionnaire_data, job_data)
time_original = time.time() - start

# Test votre algorithme
start = time.time()
results_custom = algo_custom(cv_data, questionnaire_data, job_data)
time_custom = time.time() - start

print(f'Algorithme original: {time_original:.3f}s, Score moyen: {sum(r[\"matching_score\"] for r in results_original)/len(results_original):.1f}%')
print(f'Votre algorithme: {time_custom:.3f}s, Score moyen: {sum(r[\"matching_score\"] for r in results_custom)/len(results_custom):.1f}%')
"
```

## 📊 Exemples de Résultats Attendus

### Test Simple
```json
{
  "titre": "Développeur Full-Stack",
  "matching_score": 87,
  "matching_details": {
    "skills": 90,
    "contract": 100,
    "location": 85,
    "salary": 95,
    "experience": 80,
    "date": 85
  }
}
```

### Métriques de Performance
- ⏱️ **Temps d'exécution**: < 50ms pour 10 offres
- 🎯 **Précision**: Scores cohérents avec le profil
- 📈 **Scalabilité**: Capable de traiter 100+ offres

## 🐛 Résolution de Problèmes

### Erreur: Module not found
```bash
# Vérifier que vous êtes dans le bon répertoire
ls matching_engine.py

# Activer l'environnement virtuel si nécessaire
source venv/bin/activate
```

### Erreur: Port déjà utilisé
```bash
# Le script utilise automatiquement le port 8001
# Si problème, tuer le processus:
lsof -i :8001
kill -9 <PID>
```

### Erreur: Import
```bash
# Installer les dépendances manquantes
pip install fastapi uvicorn requests
```

## 🎯 Métriques d'Évaluation

Pour évaluer votre algorithme, considérez :

1. **Précision**: Les meilleurs matches sont-ils pertinents ?
2. **Rappel**: Trouve-t-il tous les matches intéressants ?
3. **Performance**: Temps d'exécution pour N offres
4. **Stabilité**: Résultats cohérents sur plusieurs runs
5. **Interprétabilité**: Peut-on expliquer pourquoi tel score ?

## 🚀 Intégration dans le Système

Une fois votre algorithme testé :

1. **Remplacer dans le service matching** :
   ```bash
   # Copier votre algorithme dans le service
   cp my_matching_engine.py matching-service/app/my_algorithm.py
   
   # Modifier matching-service/app/workers/tasks.py
   # pour utiliser votre algorithme
   ```

2. **Tester en intégration** :
   ```bash
   # Redémarrer le service de matching
   docker-compose restart nexten-matching-api
   
   # Tester via l'API complète
   curl http://localhost:5052/health
   ```

3. **Déployer** :
   ```bash
   # Rebuild et déployer
   ./rebuild-matching.sh
   ```

## 💡 Conseils pour l'Amélioration

- **Analyse sémantique** : Utilisez des embeddings pour les compétences
- **Apprentissage** : Intégrez les feedbacks utilisateurs
- **Pondération adaptative** : Ajustez les poids selon le profil
- **Cache intelligent** : Optimisez les calculs répétitifs

---

🎉 **Bon test et développement !** N'hésitez pas à expérimenter avec différentes approches d'algorithmes de matching.
