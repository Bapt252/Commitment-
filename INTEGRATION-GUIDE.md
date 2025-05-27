# Guide d'intégration SuperSmartMatch avec votre Front-end

Ce guide détaille comment intégrer SuperSmartMatch dans vos pages front-end existantes avec un minimum de modifications.

## 📋 **Prérequis**

- SuperSmartMatch démarré sur `http://localhost:5060`
- Vos pages front-end existantes dans le dossier `templates/`
- Client JavaScript SuperSmartMatch (`client.js`)

## 🔧 **Étapes d'intégration**

### **1. Inclure le client SuperSmartMatch**

Ajoutez le client JavaScript dans vos pages existantes :

```html
<!-- Dans candidate-matching-improved.html, candidate-questionnaire.html, etc. -->
<script src="super-smart-match/client.js"></script>
```

### **2. Initialiser le client**

```javascript
// Initialisation du client SuperSmartMatch
const smartMatchClient = new SuperSmartMatchClient('http://localhost:5060');

// Test de disponibilité
smartMatchClient.health().then(health => {
    if (health.available) {
        console.log('✅ SuperSmartMatch disponible');
        console.log(`Algorithmes: ${Object.keys(health.data.available_algorithms).join(', ')}`);
    } else {
        console.log('⚠️ SuperSmartMatch non disponible - fallback activé');
    }
});
```

### **3. Adapter votre code de matching existant**

#### **Ancien code (exemple)**
```javascript
// Code existant dans candidate-matching-improved.html
async function performMatching() {
    const candidateData = {
        cv: extractedCVData,
        questionnaire: questionnaireData
    };
    
    const response = await fetch('http://localhost:5052/api/match', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            cv_data: candidateData.cv,
            questionnaire_data: candidateData.questionnaire,
            job_data: availableJobs
        })
    });
    
    const results = await response.json();
    displayResults(results);
}
```

#### **Nouveau code avec SuperSmartMatch**
```javascript
// Code intégré avec SuperSmartMatch
async function performMatching() {
    const frontendData = {
        candidate: {
            skills: extractedCVData.competences,
            experience: extractedCVData.annees_experience,
            education: extractedCVData.formation
        },
        questionnaire: {
            contract_types: questionnaireData.contrats_recherches,
            location: questionnaireData.adresse,
            salary_expectation: questionnaireData.salaire_souhaite,
            mobility: questionnaireData.mobilite
        },
        jobs: availableJobs
    };
    
    // Matching intelligent avec fallback automatique
    const results = await smartMatchClient.smartMatch(frontendData, {
        algorithm: 'auto',  // ou 'hybrid' pour plus de précision
        limit: 10
    });
    
    if (results.success) {
        console.log(`Algorithme utilisé: ${results.algorithm_used}`);
        console.log(`Temps d'exécution: ${results.execution_time}s`);
        displayResults(results.results);
    } else {
        console.error('Erreur de matching:', results.error);
        displayError(results.error);
    }
}
```

## 🎯 **Intégrations spécifiques par page**

### **candidate-matching-improved.html**

```javascript
// Ajout dans la fonction de matching existante
document.addEventListener('DOMContentLoaded', function() {
    const smartMatchClient = new SuperSmartMatchClient();
    
    // Fonction de matching améliorée
    window.enhancedMatching = async function(cvData, questionnaireData, jobsData) {
        // Préparer les données pour SuperSmartMatch
        const frontendData = {
            candidate: {
                skills: cvData.competences || [],
                experience: cvData.annees_experience || 0,
                education: cvData.formation || ''
            },
            questionnaire: {
                contract_types: questionnaireData.contrats_recherches || ['CDI'],
                location: questionnaireData.adresse || '',
                salary_expectation: questionnaireData.salaire_souhaite || 0,
                mobility: questionnaireData.mobilite || 'on_site'
            },
            jobs: jobsData
        };
        
        try {
            // Utiliser l'algorithme hybride pour plus de précision
            const result = await smartMatchClient.smartMatch(frontendData, {
                algorithm: 'hybrid',
                limit: 20
            });
            
            if (result.success) {
                // Affichage des métriques
                updateMatchingStats(result);
                
                // Affichage des résultats avec les scores détaillés
                displayMatchingResults(result.results);
                
                return result.results;
            } else {
                throw new Error(result.error);
            }
            
        } catch (error) {
            console.error('Erreur lors du matching:', error);
            showErrorMessage('Erreur lors du calcul des compatibilités. Veuillez réessayer.');
            return [];
        }
    };
    
    // Fonction pour afficher les métriques de matching
    function updateMatchingStats(result) {
        const statsContainer = document.getElementById('matching-stats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="stat-item">
                    <span class="stat-label">Algorithme:</span>
                    <span class="stat-value">${result.algorithm_used}</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Temps:</span>
                    <span class="stat-value">${result.execution_time}s</span>
                </div>
                <div class="stat-item">
                    <span class="stat-label">Résultats:</span>
                    <span class="stat-value">${result.total_results}</span>
                </div>
                ${result.fallback_used ? '<div class="stat-warning">Mode fallback utilisé</div>' : ''}
            `;
        }
    }
});
```

### **candidate-questionnaire.html**

```javascript
// Ajout pour la validation en temps réel
document.addEventListener('DOMContentLoaded', function() {
    const smartMatchClient = new SuperSmartMatchClient();
    
    // Validation et preview des résultats en temps réel
    async function previewMatching() {
        const currentData = getCurrentFormData();
        const mockJobs = getMockJobsForPreview();
        
        if (currentData.competences && currentData.competences.length > 0) {
            const previewData = {
                candidate: {
                    skills: currentData.competences,
                    experience: currentData.annees_experience || 0
                },
                questionnaire: {
                    contract_types: currentData.contrats_recherches || ['CDI'],
                    location: currentData.adresse || ''
                },
                jobs: mockJobs
            };
            
            try {
                const result = await smartMatchClient.smartMatch(previewData, {
                    algorithm: 'auto',
                    limit: 3
                });
                
                if (result.success && result.results.length > 0) {
                    showMatchingPreview(result.results);
                }
            } catch (error) {
                console.log('Preview non disponible:', error.message);
            }
        }
    }
    
    // Déclencher le preview à chaque changement significatif
    ['input', 'change'].forEach(eventType => {
        document.addEventListener(eventType, debounce(previewMatching, 1000));
    });
});
```

### **client-questionnaire.html**

```javascript
// Pour les entreprises : recommandation de candidats
document.addEventListener('DOMContentLoaded', function() {
    const smartMatchClient = new SuperSmartMatchClient();
    
    window.findCandidatesForJob = async function(jobData) {
        // Inverser le matching : chercher des candidats pour un poste
        const mockCandidates = await getMockCandidatesData();
        
        const results = [];
        
        // Tester chaque candidat contre le poste
        for (const candidate of mockCandidates) {
            const frontendData = {
                candidate: {
                    skills: candidate.competences,
                    experience: candidate.annees_experience,
                    education: candidate.formation
                },
                questionnaire: {
                    contract_types: candidate.contrats_recherches,
                    location: candidate.adresse,
                    salary_expectation: candidate.salaire_souhaite
                },
                jobs: [jobData]
            };
            
            try {
                const result = await smartMatchClient.smartMatch(frontendData, {
                    algorithm: 'enhanced',
                    limit: 1
                });
                
                if (result.success && result.results.length > 0) {
                    results.push({
                        candidate: candidate,
                        matching_score: result.results[0].matching_score,
                        matching_details: result.results[0].matching_details
                    });
                }
            } catch (error) {
                console.log(`Erreur pour le candidat ${candidate.id}:`, error.message);
            }
        }
        
        // Trier par score décroissant
        results.sort((a, b) => b.matching_score - a.matching_score);
        
        return results;
    };
});
```

## 🔄 **Comparaison des algorithmes en temps réel**

```javascript
// Fonction pour comparer tous les algorithmes
async function compareMatchingAlgorithms(cvData, questionnaireData, jobData) {
    const frontendData = {
        candidate: {
            skills: cvData.competences,
            experience: cvData.annees_experience,
            education: cvData.formation
        },
        questionnaire: {
            contract_types: questionnaireData.contrats_recherches,
            location: questionnaireData.adresse,
            salary_expectation: questionnaireData.salaire_souhaite
        },
        jobs: jobData
    };
    
    try {
        const comparison = await smartMatchClient.compareAlgorithms(
            frontendData.candidate,
            frontendData.questionnaire,
            frontendData.jobs,
            5
        );
        
        if (comparison.success && comparison.mode === 'comparison') {
            displayAlgorithmComparison(comparison);
            return comparison;
        }
    } catch (error) {
        console.error('Erreur lors de la comparaison:', error);
    }
}

function displayAlgorithmComparison(comparison) {
    const container = document.getElementById('algorithm-comparison');
    if (!container) return;
    
    const html = `
        <div class="comparison-results">
            <h3>Comparaison des algorithmes</h3>
            <div class="comparison-stats">
                <p><strong>Meilleur score:</strong> ${comparison.best_scoring_algorithm}</p>
                <p><strong>Plus rapide:</strong> ${comparison.fastest_algorithm}</p>
                <p><strong>Temps total:</strong> ${comparison.total_execution_time}s</p>
            </div>
            <div class="algorithm-details">
                ${Object.entries(comparison.detailed_results).map(([algo, data]) => `
                    <div class="algorithm-result">
                        <h4>${algo}</h4>
                        ${data.error ? 
                            `<p class="error">Erreur: ${data.error}</p>` :
                            `
                            <p>Score moyen: ${data.average_score}%</p>
                            <p>Temps: ${data.execution_time}s</p>
                            <p>Résultats: ${data.results_count}</p>
                            `
                        }
                    </div>
                `).join('')}
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}
```

## 🎨 **Améliorations visuelles**

### **CSS pour les métriques de matching**

```css
/* Ajout dans vos CSS existants */
.matching-stats {
    display: flex;
    gap: 20px;
    margin: 20px 0;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
}

.stat-item {
    display: flex;
    flex-direction: column;
    text-align: center;
}

.stat-label {
    font-size: 12px;
    color: #666;
    margin-bottom: 5px;
}

.stat-value {
    font-size: 18px;
    font-weight: bold;
    color: #2c3e50;
}

.stat-warning {
    color: #e67e22;
    font-size: 12px;
    font-style: italic;
}

.algorithm-comparison {
    margin: 20px 0;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.algorithm-result {
    padding: 10px;
    margin: 10px 0;
    background: #f5f5f5;
    border-radius: 4px;
}

.algorithm-result.best {
    background: #d4edda;
    border-left: 4px solid #28a745;
}
```

## 🚀 **Déploiement et test**

### **1. Test complet de l'intégration**

```bash
# Démarrer SuperSmartMatch
./start-super-smart-match.sh

# Tester l'API
./test-super-smart-match.sh

# Ouvrir vos pages front-end
open templates/candidate-matching-improved.html
```

### **2. Vérification de l'intégration**

```javascript
// Console du navigateur - test rapide
window.testIntegration = async function() {
    const client = new SuperSmartMatchClient();
    
    const testData = {
        candidate: { skills: ['Python', 'React'], experience: 3 },
        questionnaire: { contract_types: ['CDI'], location: 'Paris' },
        jobs: [{ title: 'Dev', skills: ['Python'], contract_type: 'CDI' }]
    };
    
    const result = await client.smartMatch(testData);
    console.log('Test d\'intégration:', result.success ? '✅ Succès' : '❌ Échec');
    return result;
};

// Exécuter le test
testIntegration();
```

## 🔧 **Dépannage**

### **Problèmes courants**

1. **CORS Error**
   ```javascript
   // Vérifier que SuperSmartMatch autorise les CORS
   // Le service inclut déjà Flask-CORS
   ```

2. **SuperSmartMatch non accessible**
   ```javascript
   // Le client bascule automatiquement en mode fallback
   // Vérifiez que le service est démarré sur le bon port
   ```

3. **Données incompatibles**
   ```javascript
   // Le client adapte automatiquement les formats
   // Utilisez adaptFrontendData() si nécessaire
   ```

### **Mode debug**

```javascript
// Activer les logs détaillés
const smartMatchClient = new SuperSmartMatchClient('http://localhost:5060');
smartMatchClient.debug = true;

// Tester étape par étape
const health = await smartMatchClient.health();
console.log('Health:', health);

const algorithms = await smartMatchClient.getAlgorithms();
console.log('Algorithms:', algorithms);
```

---

**Votre front-end existant est maintenant compatible avec SuperSmartMatch !** 🎉

L'intégration est **progressive** : vos pages continuent de fonctionner même si SuperSmartMatch n'est pas disponible grâce au système de fallback automatique.
