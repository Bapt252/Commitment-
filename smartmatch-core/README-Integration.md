# Guide d'intégration des questionnaires avec SmartMatch

Ce guide décrit comment intégrer les questionnaires web (candidat et client) avec l'algorithme SmartMatch pour obtenir des résultats de matching plus précis et personnalisés.

## 1. Architecture d'intégration

L'intégration repose sur trois composants principaux :

- **Frontend** : Les questionnaires web HTML pour les candidats et les entreprises
- **Transformation** : Le module `questionnaire_integration.py` qui convertit les données des formulaires en format SmartMatch
- **Matching** : Les classes `SmartMatcher` et `SmartMatcherEnhanced` qui calculent les scores de matching

## 2. Flux de données

Le processus d'intégration suit ces étapes :

1. L'utilisateur remplit le questionnaire web (candidat ou client)
2. Les données du formulaire sont envoyées à l'API SmartMatch (via `api_enhanced.py`)
3. Le module de transformation (`questionnaire_integration.py`) convertit les données en format compatible
4. L'algorithme SmartMatch calcule les scores et génère des insights
5. Les résultats sont renvoyés à l'interface utilisateur

## 3. Intégration côté frontend

### Questionnaire candidat

Pour intégrer le questionnaire candidat, ajoutez ce code JavaScript :

```javascript
// Fonction pour soumettre le questionnaire candidat à l'API SmartMatch
async function submitCandidateQuestionnaire(formData) {
  try {
    // Récupérer les données du formulaire
    const candidateData = {};
    
    // Parcourir tous les champs du formulaire
    for (const [key, value] of formData.entries()) {
      candidateData[key] = value;
    }
    
    // Traitement spécial pour les checkboxes (structure-type, transport-method)
    const checkboxGroups = ['structure-type', 'transport-method'];
    for (const group of checkboxGroups) {
      const values = [];
      const checkboxes = document.querySelectorAll(`input[name="${group}"]:checked`);
      checkboxes.forEach(checkbox => values.push(checkbox.value));
      candidateData[group] = values;
    }
    
    // Si une analyse CV a été réalisée, inclure les compétences
    if (window.cvSkills) {
      candidateData.skills = window.cvSkills;
    }
    
    // Envoyer à l'API SmartMatch
    const response = await fetch('http://localhost:5052/api/process-questionnaires', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        candidate_data: candidateData,
        job_data: {},  // Sera rempli ultérieurement
        client_data: {}  // Sera rempli ultérieurement
      })
    });
    
    const result = await response.json();
    
    // Stocker les données transformées pour une utilisation ultérieure
    localStorage.setItem('smartmatch_candidate', JSON.stringify(result.candidate));
    
    return result;
  } catch (error) {
    console.error('Erreur lors de la soumission du questionnaire:', error);
    throw error;
  }
}
```

### Questionnaire client

Pour intégrer le questionnaire client, ajoutez ce code JavaScript :

```javascript
// Fonction pour soumettre le questionnaire client et les données du job à l'API SmartMatch
async function submitJobQuestionnaire(clientFormData, jobData) {
  try {
    // Récupérer les données du formulaire client
    const clientData = {};
    
    // Parcourir tous les champs du formulaire
    for (const [key, value] of clientFormData.entries()) {
      clientData[key] = value;
    }
    
    // Traitement spécial pour les checkboxes (recruitment-delay)
    const checkboxGroups = ['recruitment-delay'];
    for (const group of checkboxGroups) {
      const values = [];
      const checkboxes = document.querySelectorAll(`input[name="${group}"]:checked`);
      checkboxes.forEach(checkbox => values.push(checkbox.value));
      clientData[group] = values;
    }
    
    // Envoyer à l'API SmartMatch
    const response = await fetch('http://localhost:5052/api/process-questionnaires', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        candidate_data: {},  // Sera rempli ultérieurement
        job_data: jobData,  // Données extraites de la fiche de poste
        client_data: clientData
      })
    });
    
    const result = await response.json();
    
    // Stocker les données transformées pour une utilisation ultérieure
    localStorage.setItem('smartmatch_job', JSON.stringify(result.job));
    
    return result;
  } catch (error) {
    console.error('Erreur lors de la soumission du questionnaire:', error);
    throw error;
  }
}
```

### Calculer le matching

Pour calculer le matching entre un candidat et un job :

```javascript
// Fonction pour calculer le matching entre un candidat et un job
async function calculateQuestionnairesMatch(candidateData, jobData, clientData) {
  try {
    const response = await fetch('http://localhost:5052/api/questionnaire-match', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        candidate_data: candidateData,
        job_data: jobData,
        client_data: clientData
      })
    });
    
    return await response.json();
  } catch (error) {
    console.error('Erreur lors du calcul du matching:', error);
    throw error;
  }
}
```

## 4. Intégration côté backend

### Configuration de l'API

1. Installez les dépendances :

```bash
pip install -r requirements.txt
```

2. Lancez l'API améliorée :

```bash
python api_enhanced.py
```

### Utilisation directe dans d'autres applications

Vous pouvez également intégrer le code directement dans d'autres applications Python :

```python
from questionnaire_integration import process_questionnaires
from smartmatch_enhanced import SmartMatcherEnhanced

# Initialiser le matcher
matcher = SmartMatcherEnhanced()

# Transformer les données des questionnaires
candidate, job = process_questionnaires(candidate_data, job_data, client_data)

# Calculer le matching
result = matcher.calculate_match(candidate, job)

# Utiliser les résultats
print(f"Score global: {result['overall_score']}")
for insight in result['insights']:
    print(f"- {insight['message']}")
```

## 5. Exemple complet d'intégration

Dans le dossier `examples`, vous trouverez un exemple complet d'intégration incluant :

- Un fichier HTML pour les deux questionnaires
- Le code JavaScript pour l'envoi des données
- Un exemple d'affichage des résultats

Pour l'exécuter :

1. Lancez l'API
2. Ouvrez les exemples HTML dans un navigateur
3. Testez le processus complet d'intégration

## 6. Extension et personnalisation

Vous pouvez personnaliser l'intégration en :

- Modifiant les fonctions de transformation dans `questionnaire_integration.py`
- Ajoutant de nouveaux critères de matching dans `smartmatch_enhanced.py`
- Créant vos propres vues dans l'API pour des cas d'usage spécifiques

N'hésitez pas à adapter le code à vos besoins spécifiques.

## 7. Dépannage

### Problèmes courants et solutions

- **Les scores semblent incorrects** : Vérifiez la transformation des données avec l'endpoint `/api/process-questionnaires`
- **Erreurs lors de l'envoi des formulaires** : Vérifiez que tous les champs requis sont présents et bien formatés
- **Lenteur dans les calculs** : Activez le cache pour les calculs de distance et utilisez le mode batch pour plusieurs matchings

### Journalisation

Activez la journalisation détaillée pour le dépannage :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 8. Support et contact

Pour toute question ou suggestion, contactez l'équipe de développement.