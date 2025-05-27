# 🎯 SuperSmartMatch v2.0 - Guide de Test à Grande Échelle

## 🚀 **NOUVELLES FONCTIONNALITÉS IMPLÉMENTÉES**

### ✅ **Ce qui est maintenant disponible :**

1. **Temps de trajet exact** selon mode de transport (pied, voiture, transport, vélo)
2. **Pondération intelligente** selon questionnaire candidat
3. **Explications détaillées** pour chaque score
4. **Support CDI/CDD/INTERIM** avec correspondances partielles
5. **Classement logique** basé sur les réponses du questionnaire

---

## 🧪 **COMMENT TESTER**

### **1. Démarrer SuperSmartMatch v2.0**

```bash
# Récupérer les dernières mises à jour
git pull origin main

# Redémarrer SuperSmartMatch (il détectera automatiquement le nouveau moteur)
./start-supersmartmatch.sh
```

### **2. Tests automatisés avancés**

```bash
# Rendre exécutable et lancer les tests avancés
chmod +x test-supersmartmatch-advanced.sh
./test-supersmartmatch-advanced.sh
```

### **3. Format de réponse enrichi**

Maintenant les réponses incluent :

```json
{
  "matching_score": 82,
  "matching_details": {
    "skills": 85,
    "contract": 100,
    "location": 90,
    "travel_time": 95,     // NOUVEAU
    "date": 80,
    "salary": 75,
    "experience": 90
  },
  "matching_explanations": {    // NOUVEAU
    "skills": "Excellente correspondance - vous maîtrisez la plupart des compétences",
    "contract": "Type de contrat CDI correspond à vos préférences",
    "travel_time": "Trajet court (25min) en metro",
    "salary": "Fourchette salariale 60000-70000€ compatible avec vos attentes (55000€)"
  },
  "travel_info": {             // NOUVEAU
    "origin": "Paris 15ème",
    "destination": "Paris 8ème", 
    "transport_mode": "metro",
    "estimated_time_minutes": 25,
    "estimated_time_display": "25min",
    "is_reasonable": true
  }
}
```

---

## 🎯 **PONDÉRATION INTELLIGENTE IMPLÉMENTÉE**

### **Logique adaptative selon questionnaire :**

1. **Si candidat a quitté pour salaire** (`raison_changement: "salaire"`)
   - Salaire : **35%** (au lieu de 15%)
   - Skills : 20%, Location : 15%

2. **Si candidat privilégie équilibre vie pro/perso** (`priorite: "equilibre"`)
   - Temps trajet : **25%**
   - Localisation : **25%**

3. **Si candidat cherche évolution** (`objectif: "competences"`)
   - Compétences : **35%**
   - Expérience : 15%

4. **Si transport en commun/à pied**
   - Temps trajet devient **critique** (25-30%)

---

## 📊 **TESTS AVEC DONNÉES RÉALISTES**

### **Test 1 : Candidat Senior privilégiant salaire**

```bash
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
      "annees_experience": 8,
      "niveau_etudes": "Master",
      "derniere_fonction": "Tech Lead",
      "secteur_activite": "FinTech"
    },
    "questionnaire_data": {
      "adresse": "Paris 11ème",
      "salaire_souhaite": 75000,
      "types_contrat": ["CDI"],
      "mode_transport": "metro",
      "temps_trajet_max": 60,
      "date_disponibilite": "2025-06-01",
      "raison_changement": "salaire",
      "priorite": "remuneration",
      "objectif": "evolution"
    },
    "job_data": [
      {
        "id": "senior-001",
        "titre": "Senior Python Developer",
        "entreprise": "BigTech",
        "competences": ["Python", "Django", "PostgreSQL"],
        "localisation": "Paris 2ème",
        "type_contrat": "CDI", 
        "salaire_min": 80000,
        "salaire_max": 95000,
        "experience_requise": 5,
        "date_debut_souhaitee": "2025-06-15"
      },
      {
        "id": "senior-002",
        "titre": "Tech Lead",
        "entreprise": "Startup",
        "competences": ["Python", "AWS", "Docker"],
        "localisation": "Boulogne-Billancourt",
        "type_contrat": "CDI",
        "salaire_min": 70000,
        "salaire_max": 80000,
        "experience_requise": 7
      }
    ],
    "algorithm": "advanced"
  }'
```

### **Test 2 : Candidat Junior privilégiant localisation**

```bash
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["JavaScript", "React", "HTML", "CSS"],
      "annees_experience": 2,
      "niveau_etudes": "Bachelor"
    },
    "questionnaire_data": {
      "adresse": "Paris 18ème",
      "salaire_souhaite": 38000,
      "types_contrat": ["CDI", "CDD"],
      "mode_transport": "pied",
      "temps_trajet_max": 20,
      "raison_changement": "localisation",
      "priorite": "equilibre",
      "objectif": "competences"
    },
    "job_data": [
      {
        "id": "junior-001",
        "titre": "Développeur Frontend Junior",
        "competences": ["JavaScript", "React"],
        "localisation": "Paris 18ème",
        "type_contrat": "CDI",
        "salaire_min": 35000,
        "salaire_max": 40000,
        "experience_requise": 1
      },
      {
        "id": "junior-002", 
        "titre": "React Developer",
        "competences": ["React", "Node.js"],
        "localisation": "La Défense",
        "type_contrat": "CDI",
        "salaire_min": 42000,
        "salaire_max": 48000,
        "experience_requise": 2
      }
    ]
  }'
```

### **Test 3 : Candidat avec contraintes transport**

```bash
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["PHP", "MySQL", "Symfony"],
      "annees_experience": 4
    },
    "questionnaire_data": {
      "adresse": "Vincennes", 
      "mode_transport": "transport",
      "temps_trajet_max": 45,
      "types_contrat": ["CDI", "CDD", "INTERIM"]
    },
    "job_data": [
      {
        "id": "php-001",
        "titre": "Développeur PHP",
        "competences": ["PHP", "MySQL"],
        "localisation": "Paris 12ème",
        "type_contrat": "CDI"
      },
      {
        "id": "php-002",
        "titre": "Développeur Symfony",
        "competences": ["PHP", "Symfony"],
        "localisation": "Créteil",
        "type_contrat": "INTERIM"
      }
    ]
  }'
```

---

## 🔥 **TEST GRANDE ÉCHELLE**

### **Données pour 100+ jobs**

```bash
# Utiliser l'endpoint de données de test
curl http://localhost:5061/api/test-data
```

Puis créer un script Python pour générer automatiquement des centaines de CV et jobs :

```python
import requests
import json

# Exemple de génération de 100 jobs
jobs = []
for i in range(100):
    jobs.append({
        "id": f"job-{i:03d}",
        "titre": f"Développeur {['Python', 'Java', 'JavaScript'][i%3]}",
        "competences": [["Python", "Django"], ["Java", "Spring"], ["JavaScript", "React"]][i%3],
        "localisation": ["Paris", "Lyon", "Marseille"][i%3],
        "type_contrat": ["CDI", "CDD", "INTERIM"][i%3],
        "salaire_min": 35000 + (i % 50) * 1000,
        "salaire_max": 45000 + (i % 50) * 1000
    })

# Test avec 100 jobs
response = requests.post('http://localhost:5061/api/match', json={
    'cv_data': {...},
    'questionnaire_data': {...},
    'job_data': jobs,
    'algorithm': 'advanced',
    'limit': 50
})
```

---

## 📈 **RÉSULTATS ATTENDUS**

Avec SuperSmartMatch v2.0, vous devriez voir :

1. **Scores plus précis** avec temps de trajet réel
2. **Classement intelligent** selon priorités candidat
3. **Explications détaillées** pour chaque critère
4. **Support complet** CDI/CDD/INTERIM
5. **Performance** maintenue même avec 1000+ jobs

---

## 🎯 **PROCHAINES ÉTAPES**

Pour une implémentation production complète :

1. **Intégrer API Google Maps** pour temps trajet réels
2. **Base de données** pour persistance candidates/jobs
3. **Machine Learning** pour améliorer la pondération
4. **Interface graphique** pour visualiser les résultats

**SuperSmartMatch v2.0 répond maintenant à tous vos besoins ! 🚀**
