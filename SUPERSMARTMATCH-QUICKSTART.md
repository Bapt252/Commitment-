# 🚀 Guide Rapide - SuperSmartMatch Fixed

Ce guide vous aide à résoudre rapidement les problèmes de SuperSmartMatch et à démarrer le service.

## 🔧 Problèmes Résolus

### ✅ **Problème de Port 5060 Occupé**
- **Avant**: `Address already in use - Port 5060 is in use by another program`
- **Solution**: Détection automatique et libération du port ou utilisation d'un port alternatif (5061)

### ✅ **Warning SmartMatch**
- **Avant**: `WARNING - Impossible de charger SmartMatch: No module named 'app.compat'`
- **Solution**: Correction des imports et création d'adaptateurs robustes

### ✅ **Configuration Automatique**
- Installation des dépendances Flask manquantes
- Scripts de démarrage et test automatisés
- Gestion intelligente des algorithmes de fallback

## 🚀 Démarrage Rapide

### 1. Exécuter le Script de Correction

```bash
# Rendre le script exécutable
chmod +x fix-supersmartmatch.sh

# Exécuter la correction complète
./fix-supersmartmatch.sh
```

### 2. Démarrer SuperSmartMatch

```bash
# Le script crée automatiquement start-supersmartmatch.sh
./start-supersmartmatch.sh
```

### 3. Tester le Service

```bash
# Tester que tout fonctionne
./test-supersmartmatch.sh
```

## 📊 Vérification du Bon Fonctionnement

### Test de Santé (Health Check)
```bash
curl http://localhost:5061/api/health
```

**Réponse attendue:**
```json
{
  "status": "healthy",
  "service": "SuperSmartMatch",
  "algorithms_loaded": 4,
  "available_algorithms": ["enhanced", "custom", "smart_match", "hybrid"]
}
```

### Test des Algorithmes Disponibles
```bash
curl http://localhost:5061/api/algorithms
```

### Test de Matching Complet
```bash
curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python", "JavaScript", "React"],
      "annees_experience": 3
    },
    "questionnaire_data": {
      "adresse": "Paris",
      "salaire_souhaite": 45000,
      "mobilite": "hybrid"
    },
    "job_data": [
      {
        "id": "job1",
        "titre": "Développeur Full Stack",
        "competences": ["Python", "React", "Docker"],
        "localisation": "Paris",
        "salaire_min": 40000,
        "salaire_max": 50000
      }
    ],
    "algorithm": "auto",
    "limit": 5
  }'
```

## 🎯 Intégration avec votre Front-end

### Endpoints Disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health` | GET | Santé du service |
| `/api/algorithms` | GET | Liste des algorithmes |
| `/api/match` | POST | Matching principal |

### Exemple d'Intégration JavaScript

```javascript
// Configuration de base
const SUPERSMARTMATCH_URL = 'http://localhost:5061';

// Fonction de matching
async function matchCandidateWithJobs(cvData, questionnaireData, jobsData, algorithm = 'auto') {
    try {
        const response = await fetch(`${SUPERSMARTMATCH_URL}/api/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                cv_data: cvData,
                questionnaire_data: questionnaireData,
                job_data: jobsData,
                algorithm: algorithm,
                limit: 10
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('Erreur lors du matching:', error);
        throw error;
    }
}

// Utilisation
const cvData = {
    competences: ['Python', 'JavaScript', 'React'],
    annees_experience: 3
};

const questionnaireData = {
    adresse: 'Paris',
    salaire_souhaite: 45000,
    mobilite: 'hybrid'
};

const jobsData = [
    // Vos offres d'emploi...
];

matchCandidateWithJobs(cvData, questionnaireData, jobsData, 'hybrid')
    .then(result => {
        console.log('Résultats du matching:', result);
        // Traiter les résultats...
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
```

## 🔄 Algorithmes Disponibles

### 1. **Auto** (Recommandé)
- Sélection automatique du meilleur algorithme selon le contexte
- Analyse les données d'entrée pour optimiser la performance

### 2. **Enhanced**
- Algorithme amélioré avec pondération dynamique
- Nouveaux critères de matching avancés

### 3. **Smart Match**
- Matching bidirectionnel avec géolocalisation
- Analyse sémantique des compétences

### 4. **Custom**
- Votre algorithme personnalisé optimisé
- Spécifique aux besoins de Nexten

### 5. **Hybrid**
- Combine tous les algorithmes pour un résultat optimal
- Score de consensus et analyse comparative

### 6. **Comparison**
- Mode de test qui exécute tous les algorithmes
- Compare les performances et résultats

## 🛠️ Dépannage

### Problème de Port
```bash
# Vérifier quel processus utilise le port
lsof -i :5060

# Le script fix-supersmartmatch.sh gère automatiquement ce problème
```

### Problème de Dépendances
```bash
# Réinstaller les dépendances
cd super-smart-match
source venv/bin/activate
pip install --upgrade flask flask-cors pandas numpy scikit-learn
```

### Problème d'Import SmartMatch
Le script corrige automatiquement les imports avec:
- Gestion robuste des chemins d'import
- Adaptateurs de fallback
- Stubs pour les modules manquants

## 📈 Monitoring et Performance

### Logs du Service
```bash
# Les logs s'affichent dans le terminal lors du démarrage
tail -f super-smart-match/logs/supersmartmatch.log  # Si configuré
```

### Métriques Disponibles
- Temps d'exécution par algorithme
- Nombre de résultats par requête
- Scores de consensus (mode hybrid)
- Taux de succès par algorithme

## 🔗 Intégration avec Templates/

### Modification de vos Templates Existants

Dans vos templates HTML existants (dans le dossier `templates/`), vous pouvez maintenant utiliser SuperSmartMatch:

```html
<!-- Ajouter dans vos pages de matching -->
<script>
// Configuration SuperSmartMatch
window.SUPERSMARTMATCH_CONFIG = {
    url: 'http://localhost:5061',
    defaultAlgorithm: 'auto',
    timeout: 30000
};

// Fonction utilitaire pour le matching
window.nextenMatching = {
    async match(cvData, questionnaireData, jobsData, options = {}) {
        const config = window.SUPERSMARTMATCH_CONFIG;
        
        try {
            const response = await fetch(`${config.url}/api/match`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    cv_data: cvData,
                    questionnaire_data: questionnaireData,
                    job_data: jobsData,
                    algorithm: options.algorithm || config.defaultAlgorithm,
                    limit: options.limit || 10
                })
            });
            
            return await response.json();
        } catch (error) {
            console.error('SuperSmartMatch error:', error);
            throw error;
        }
    }
};
</script>
```

## 🎉 Résumé

Après exécution du script `fix-supersmartmatch.sh`, vous avez:

✅ **SuperSmartMatch fonctionnel** sur le port 5061 (ou 5060 si libre)  
✅ **4 algorithmes chargés** (enhanced, custom, smart_match, hybrid)  
✅ **API unifiée** prête pour l'intégration  
✅ **Scripts automatisés** pour démarrage et tests  
✅ **Gestion robuste des erreurs** et fallbacks  
✅ **Compatible** avec votre architecture existante  

Le service est maintenant prêt pour l'intégration avec votre front-end Nexten !
