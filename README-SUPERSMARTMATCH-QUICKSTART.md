# 🚀 SuperSmartMatch - Guide d'Utilisation

SuperSmartMatch est un service unifié de matching candidat/emploi qui regroupe plusieurs algorithmes sous une seule API.

## ✅ **Installation et Démarrage Rapide**

```bash
# 1. Cloner le repository (si pas déjà fait)
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-

# 2. Rendre les scripts exécutables
chmod +x start-supersmartmatch.sh
chmod +x test-supersmartmatch.sh

# 3. Démarrer le service
./start-supersmartmatch.sh
```

## 🧪 **Tester le Service**

Dans un autre terminal :

```bash
# Tester que tout fonctionne
./test-supersmartmatch.sh
```

## 📊 **Algorithmes Disponibles**

| Algorithme | Description | Statut |
|------------|-------------|---------|
| `auto` | Sélection automatique du meilleur algorithme | ✅ Recommandé |
| `enhanced` | Algorithme amélioré avec pondération dynamique | ✅ Disponible |
| `original` | Algorithme de base du projet | ✅ Disponible |
| `fallback` | Algorithme simple de secours | ✅ Toujours disponible |

## 🌐 **Endpoints API**

### **Health Check**
```bash
curl http://localhost:5061/api/health
```

### **Liste des Algorithmes**
```bash
curl http://localhost:5061/api/algorithms
```

### **Matching Principal**
```bash
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python", "JavaScript"],
      "annees_experience": 3
    },
    "questionnaire_data": {
      "adresse": "Paris",
      "salaire_souhaite": 45000
    },
    "job_data": [
      {
        "id": "job1",
        "titre": "Développeur Full Stack",
        "competences": ["Python", "React"],
        "localisation": "Paris"
      }
    ],
    "algorithm": "auto",
    "limit": 10
  }'
```

## 📖 **Format de Réponse**

```json
{
  "success": true,
  "algorithm_used": "enhanced",
  "execution_time": 0.045,
  "total_results": 1,
  "results": [
    {
      "id": "job1",
      "titre": "Développeur Full Stack",
      "competences": ["Python", "React"],
      "localisation": "Paris",
      "matching_score": 85,
      "matching_details": {
        "skills": 90,
        "location": 100,
        "salary": 75
      }
    }
  ],
  "metadata": {
    "timestamp": 1672531200,
    "candidate_skills_count": 2,
    "jobs_analyzed": 1
  }
}
```

## 🔧 **Paramètres de l'API**

### **cv_data** (obligatoire)
```json
{
  "competences": ["Python", "JavaScript"],
  "annees_experience": 3,
  "niveau_etudes": "Master"
}
```

### **questionnaire_data** (obligatoire)
```json
{
  "adresse": "Paris",
  "salaire_souhaite": 45000,
  "mobilite": "hybrid",
  "types_contrat": ["CDI", "CDD"]
}
```

### **job_data** (obligatoire)
```json
[
  {
    "id": "job1",
    "titre": "Développeur",
    "competences": ["Python"],
    "localisation": "Paris",
    "salaire_min": 40000,
    "salaire_max": 50000,
    "type_contrat": "CDI"
  }
]
```

### **Paramètres optionnels**
- `algorithm`: "auto", "enhanced", "original", "fallback" (défaut: "auto")
- `limit`: Nombre max de résultats (défaut: 10)

## 🎯 **Exemples d'Utilisation**

### **JavaScript/Frontend**
```javascript
const response = await fetch('http://localhost:5061/api/match', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    cv_data: {competences: ['JavaScript', 'React']},
    questionnaire_data: {adresse: 'Paris'},
    job_data: [{id: 'job1', competences: ['React']}],
    algorithm: 'auto'
  })
});

const result = await response.json();
console.log(result.results);
```

### **Python**
```python
import requests

response = requests.post('http://localhost:5061/api/match', json={
    'cv_data': {'competences': ['Python', 'Django']},
    'questionnaire_data': {'adresse': 'Lyon'},
    'job_data': [{'id': 'job1', 'competences': ['Python']}],
    'algorithm': 'enhanced'
})

results = response.json()
print(results['results'])
```

## 🛠️ **Dépannage**

### **Service ne démarre pas**
```bash
# Vérifier Python
python3 --version

# Nettoyer et recommencer
rm -rf super-smart-match/venv
./start-supersmartmatch.sh
```

### **Port 5061 occupé**
```bash
# Trouver le processus
lsof -i :5061

# L'arrêter
kill -9 <PID>
```

### **Erreur d'algorithme**
Le service utilise automatiquement l'algorithme `fallback` en cas d'erreur, garantissant un fonctionnement continu.

## 📝 **Logs et Monitoring**

Les logs s'affichent dans le terminal où le service est lancé :
```
✅ Algorithme ENHANCED chargé
📊 3 algorithmes chargés
🚀 Démarrage sur le port 5061
🎯 Nouvelle demande: auto, 5 jobs, limit=10
```

## 🔄 **Intégration avec Autres Services**

SuperSmartMatch peut être intégré avec :
- **Job Parser Service** (port 5051)
- **CV Parser Service** (port 5053) 
- **Matching Service principal** (port 5052)

## 📈 **Performance**

- ⚡ **< 50ms** pour 10 jobs typiques
- 📊 **Support** jusqu'à 1000+ jobs
- 🔄 **Fallback automatique** en cas d'erreur
- 🎯 **Auto-sélection** de l'algorithme optimal

---

**🎉 SuperSmartMatch est prêt à l'emploi !**

Pour plus d'informations, consultez les autres fichiers README du projet.
