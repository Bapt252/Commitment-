# Intégration Frontend des Questionnaires avec SmartMatch

Ce guide détaille l'intégration côté frontend des questionnaires web avec l'algorithme SmartMatch. Il inclut le code JavaScript nécessaire et des exemples d'utilisation.

## 1. Prérequis

- API SmartMatch étendue en cours d'exécution (voir `api_enhanced.py`)
- Questionnaires HTML candidat et client tels que dans le dépôt

## 2. Configuration JavaScript

Ajoutez le script suivant à vos pages de questionnaire pour faciliter l'intégration :

```html
<script src="smartmatch-integration.js"></script>
```

Voici le contenu du fichier `smartmatch-integration.js` :

```javascript
/**
 * SmartMatch Integration for Questionnaires
 * -----------------------------------------
 * This script provides functions to integrate web questionnaires
 * with the SmartMatch algorithm API.
 */

// Configuration
const SMARTMATCH_API_URL = 'http://localhost:5052';

// Utility functions
function getFormData(formElement) {
  const formData = new FormData(formElement);
  const data = {};
  
  // Process regular form fields
  for (const [key, value] of formData.entries()) {
    data[key] = value;
  }
  
  // Special handling for checkboxes (multiple values)
  const checkboxGroups = document.querySelectorAll('input[type="checkbox"][name]');
  const groupNames = new Set();
  
  checkboxGroups.forEach(checkbox => {
    groupNames.add(checkbox.name);
  });
  
  groupNames.forEach(name => {
    const checkboxes = document.querySelectorAll(`input[type="checkbox"][name="${name}"]:checked`);
    if (checkboxes.length > 0) {
      data[name] = Array.from(checkboxes).map(cb => cb.value);
    }
  });
  
  return data;
}

// Candidate questionnaire integration
const SmartMatchCandidate = {
  /**
   * Process and submit candidate questionnaire data
   * @param {HTMLFormElement} formElement - The candidate questionnaire form
   * @returns {Promise} - Resolves with the processed candidate data
   */
  submitQuestionnaire: async function(formElement) {
    try {
      const data = getFormData(formElement);
      
      // Add CV skills if available (from CV parser)
      if (window.cvSkills && Array.isArray(window.cvSkills)) {
        data.skills = window.cvSkills;
      }
      
      // Process motivation priorities (comma-separated string to array)
      if (data['motivation-order'] && typeof data['motivation-order'] === 'string') {
        data['motivation-order'] = data['motivation-order'].split(',');
      }
      
      // Send to API for processing
      const response = await fetch(`${SMARTMATCH_API_URL}/api/process-questionnaires`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_data: data,
          job_data: {},
          client_data: {}
        })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Store for later use
      localStorage.setItem('smartmatch_candidate', JSON.stringify(result.candidate));
      
      return result.candidate;
    } catch (error) {
      console.error('Error submitting candidate questionnaire:', error);
      throw error;
    }
  },
  
  /**
   * Get the stored candidate data
   * @returns {Object|null} - The stored candidate data or null if not available
   */
  getStoredData: function() {
    const stored = localStorage.getItem('smartmatch_candidate');
    return stored ? JSON.parse(stored) : null;
  }
};

// Job questionnaire integration
const SmartMatchJob = {
  /**
   * Process and submit job questionnaire data
   * @param {HTMLFormElement} clientFormElement - The client questionnaire form
   * @param {Object} jobData - The job posting data (from job parser)
   * @returns {Promise} - Resolves with the processed job data
   */
  submitQuestionnaire: async function(clientFormElement, jobData = {}) {
    try {
      const clientData = getFormData(clientFormElement);
      
      // Send to API for processing
      const response = await fetch(`${SMARTMATCH_API_URL}/api/process-questionnaires`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          candidate_data: {},
          job_data: jobData,
          client_data: clientData
        })
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const result = await response.json();
      
      // Store for later use
      localStorage.setItem('smartmatch_job', JSON.stringify(result.job));
      
      return result.job;
    } catch (error) {
      console.error('Error submitting job questionnaire:', error);
      throw error;
    }
  },
  
  /**
   * Get the stored job data
   * @returns {Object|null} - The stored job data or null if not available
   */
  getStoredData: function() {
    const stored = localStorage.getItem('smartmatch_job');
    return stored ? JSON.parse(stored) : null;
  }
};

// Matching integration
const SmartMatch = {
  /**
   * Calculate matching between candidate and job
   * @param {Object} candidateData - Candidate data from questionnaire
   * @param {Object} jobData - Job data from parser
   * @param {Object} clientData - Client data from questionnaire
   * @returns {Promise} - Resolves with the matching result
   */
  calculateMatch: async function(candidateData, jobData, clientData) {
    try {
      const response = await fetch(`${SMARTMATCH_API_URL}/api/questionnaire-match`, {
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
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error calculating match:', error);
      throw error;
    }
  },
  
  /**
   * Calculate matching using stored data
   * @returns {Promise} - Resolves with the matching result
   */
  calculateStoredMatch: async function() {
    const candidateData = SmartMatchCandidate.getStoredData();
    const jobData = SmartMatchJob.getStoredData();
    
    if (!candidateData || !jobData) {
      throw new Error('Missing stored data for candidate or job');
    }
    
    return await this.calculateMatch(candidateData, jobData, {});
  },
  
  /**
   * Find best matching jobs for a candidate
   * @param {Object} candidateData - Candidate data
   * @param {Array} jobsArray - Array of job data
   * @param {Number} limit - Maximum number of results
   * @returns {Promise} - Resolves with sorted matching results
   */
  findBestJobs: async function(candidateData, jobsArray, limit = 5) {
    try {
      const results = [];
      
      for (const job of jobsArray) {
        const result = await this.calculateMatch(candidateData, job, {});
        results.push(result);
      }
      
      // Sort by overall score
      results.sort((a, b) => b.overall_score - a.overall_score);
      
      // Return top results
      return results.slice(0, limit);
    } catch (error) {
      console.error('Error finding best jobs:', error);
      throw error;
    }
  },
  
  /**
   * Create a visual representation of the matching result
   * @param {Object} matchResult - The matching result from calculateMatch
   * @param {HTMLElement} containerElement - Container to render the visualization
   */
  visualizeMatch: function(matchResult, containerElement) {
    if (!matchResult || !containerElement) return;
    
    // Clear container
    containerElement.innerHTML = '';
    
    // Create score display
    const scoreContainer = document.createElement('div');
    scoreContainer.className = 'smartmatch-score';
    
    // Overall score
    const score = Math.round(matchResult.overall_score * 100);
    const scoreElement = document.createElement('div');
    scoreElement.className = 'overall-score';
    scoreElement.innerHTML = `
      <div class="score-circle">
        <div class="score-value">${score}%</div>
      </div>
      <div class="score-label">Compatibilité globale</div>
    `;
    scoreContainer.appendChild(scoreElement);
    
    // Category scores
    const categoryContainer = document.createElement('div');
    categoryContainer.className = 'category-scores';
    
    const categoryNames = {
      skills: 'Compétences',
      location: 'Localisation',
      experience: 'Expérience',
      education: 'Formation',
      preferences: 'Préférences',
      environment: 'Environnement',
      motivation: 'Motivation'
    };
    
    for (const [category, value] of Object.entries(matchResult.category_scores)) {
      const categoryElement = document.createElement('div');
      categoryElement.className = 'category-score';
      categoryElement.innerHTML = `
        <div class="category-name">${categoryNames[category] || category}</div>
        <div class="category-bar">
          <div class="category-fill" style="width: ${Math.round(value * 100)}%;"></div>
        </div>
        <div class="category-value">${Math.round(value * 100)}%</div>
      `;
      categoryContainer.appendChild(categoryElement);
    }
    
    scoreContainer.appendChild(categoryContainer);
    containerElement.appendChild(scoreContainer);
    
    // Insights
    const insightsContainer = document.createElement('div');
    insightsContainer.className = 'smartmatch-insights';
    insightsContainer.innerHTML = '<h3>Analyse détaillée</h3>';
    
    // Group insights by category
    const insightCategories = {
      strength: { title: 'Points forts', class: 'insight-strength', icon: '✓' },
      weakness: { title: 'Points d\'amélioration', class: 'insight-weakness', icon: '⚠' },
      mismatch: { title: 'Non-correspondances', class: 'insight-mismatch', icon: '✗' },
      dealbreaker: { title: 'Éléments rédhibitoires', class: 'insight-dealbreaker', icon: '⛔' }
    };
    
    const groupedInsights = {};
    
    matchResult.insights.forEach(insight => {
      const category = insight.category || 'info';
      if (!groupedInsights[category]) {
        groupedInsights[category] = [];
      }
      groupedInsights[category].push(insight);
    });
    
    // Create insight sections
    for (const [category, insights] of Object.entries(groupedInsights)) {
      const categoryInfo = insightCategories[category] || { 
        title: category.charAt(0).toUpperCase() + category.slice(1), 
        class: 'insight-info',
        icon: 'ℹ'
      };
      
      const sectionElement = document.createElement('div');
      sectionElement.className = `insight-section ${categoryInfo.class}`;
      sectionElement.innerHTML = `<h4>${categoryInfo.title}</h4>`;
      
      const insightsList = document.createElement('ul');
      insights.forEach(insight => {
        const insightElement = document.createElement('li');
        insightElement.innerHTML = `<span class="insight-icon">${categoryInfo.icon}</span> ${insight.message}`;
        insightsList.appendChild(insightElement);
      });
      
      sectionElement.appendChild(insightsList);
      insightsContainer.appendChild(sectionElement);
    }
    
    containerElement.appendChild(insightsContainer);
  }
};
```

## 3. Intégration dans le Questionnaire Candidat

Ajoutez ce code au questionnaire candidat pour envoyer les données à l'API SmartMatch :

```javascript
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('questionnaire-form');
  const submitBtn = document.getElementById('submit-btn');
  
  if (form && submitBtn) {
    submitBtn.addEventListener('click', async function(e) {
      e.preventDefault();
      
      if (validateStep(4)) {  // Validation du formulaire
        try {
          // Afficher un indicateur de chargement
          document.getElementById('loading-overlay').classList.add('active');
          
          // Soumettre le questionnaire à SmartMatch
          const candidateData = await SmartMatchCandidate.submitQuestionnaire(form);
          
          // Stocker l'ID pour la page de matching
          sessionStorage.setItem('candidate_id', candidateData.id);
          
          // Redirection vers la page de matching
          window.location.href = 'candidate-matching-improved.html';
        } catch (error) {
          console.error('Erreur lors du traitement du questionnaire:', error);
          showNotification('Une erreur est survenue lors du traitement de votre candidature', 'error');
          
          // Masquer l'indicateur de chargement
          document.getElementById('loading-overlay').classList.remove('active');
        }
      }
    });
  }
});
```

## 4. Intégration dans le Questionnaire Client

Ajoutez ce code au questionnaire client pour envoyer les données à l'API SmartMatch :

```javascript
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('client-questionnaire-form');
  const submitButton = document.getElementById('submit-form');
  
  if (form && submitButton) {
    submitButton.addEventListener('click', async function(e) {
      e.preventDefault();
      
      try {
        // Récupérer les données de la fiche de poste (depuis l'analyseur)
        const jobData = {};
        // Remplir avec les données extraites par l'analyseur de fiche de poste
        const fields = ['job-title-value', 'job-contract-value', 'job-location-value', 
                       'job-experience-value', 'job-education-value', 'job-salary-value',
                       'job-skills-value', 'job-responsibilities-value', 'job-benefits-value'];
        
        fields.forEach(field => {
          const element = document.getElementById(field);
          if (element) {
            jobData[field] = element.textContent || element.value || '';
          }
        });
        
        // Soumettre le questionnaire à SmartMatch
        const processedJob = await SmartMatchJob.submitQuestionnaire(form, jobData);
        
        // Afficher un message de succès
        showNotification('Votre demande a été envoyée avec succès!', 'success');
        
        // Stocker l'ID pour la page de recommandation
        sessionStorage.setItem('job_id', processedJob.id);
        
        // Rediriger vers la page appropriée
        setTimeout(() => {
          const recruitmentNeeded = form.querySelector('input[name="recruitment-need"]:checked')?.value || 'no';
          if (recruitmentNeeded === 'yes') {
            window.location.href = 'candidate-recommendation.html';
          } else {
            window.location.href = 'company-dashboard.html';
          }
        }, 2000);
      } catch (error) {
        console.error('Erreur lors du traitement du questionnaire:', error);
        showNotification('Une erreur est survenue lors du traitement de votre demande', 'error');
      }
    });
  }
});
```

## 5. Visualisation des Résultats de Matching

Pour afficher les résultats du matching, ajoutez ce code à votre page de résultats :

```javascript
document.addEventListener('DOMContentLoaded', function() {
  const resultContainer = document.getElementById('matching-results');
  
  if (resultContainer) {
    // Essayer de calculer le matching avec les données stockées
    SmartMatch.calculateStoredMatch()
      .then(result => {
        // Visualiser le résultat
        SmartMatch.visualizeMatch(result, resultContainer);
      })
      .catch(error => {
        console.error('Erreur lors du calcul du matching:', error);
        resultContainer.innerHTML = `
          <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            <p>Impossible de calculer le matching. Veuillez réessayer ultérieurement.</p>
          </div>
        `;
      });
  }
});
```

## 6. Styles CSS pour la Visualisation

Ajoutez ces styles CSS pour la visualisation des résultats :

```css
/* SmartMatch Visualization Styles */
.smartmatch-score {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-bottom: 2rem;
}

.overall-score {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.score-circle {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #a78bfa);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.2);
}

.score-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
}

.score-label {
  font-size: 1.2rem;
  font-weight: 500;
  color: #4b5563;
}

.category-scores {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
  width: 100%;
}

.category-score {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.category-name {
  font-weight: 500;
  color: #4b5563;
}

.category-bar {
  height: 10px;
  background-color: #e5e7eb;
  border-radius: 5px;
  overflow: hidden;
}

.category-fill {
  height: 100%;
  background: linear-gradient(90deg, #7c3aed, #a78bfa);
  border-radius: 5px;
  transition: width 0.5s ease;
}

.category-value {
  font-size: 0.9rem;
  color: #6b7280;
  text-align: right;
}

.smartmatch-insights {
  background-color: #f9fafb;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 2rem;
}

.smartmatch-insights h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  color: #374151;
}

.insight-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
}

.insight-section h4 {
  margin-top: 0;
  margin-bottom: 0.75rem;
  font-size: 1.1rem;
}

.insight-section ul {
  margin: 0;
  padding-left: 0;
  list-style: none;
}

.insight-section li {
  margin-bottom: 0.5rem;
  display: flex;
  align-items: flex-start;
}

.insight-icon {
  margin-right: 0.75rem;
  font-size: 1.2rem;
}

.insight-strength {
  background-color: rgba(16, 185, 129, 0.1);
}

.insight-strength h4 {
  color: #059669;
}

.insight-weakness {
  background-color: rgba(245, 158, 11, 0.1);
}

.insight-weakness h4 {
  color: #d97706;
}

.insight-mismatch {
  background-color: rgba(239, 68, 68, 0.1);
}

.insight-mismatch h4 {
  color: #dc2626;
}

.insight-dealbreaker {
  background-color: rgba(220, 38, 38, 0.1);
  border-left: 4px solid #ef4444;
}

.insight-dealbreaker h4 {
  color: #b91c1c;
}

.insight-info {
  background-color: rgba(59, 130, 246, 0.1);
}

.insight-info h4 {
  color: #2563eb;
}

@media (max-width: 768px) {
  .smartmatch-score {
    gap: 1.5rem;
  }
  
  .score-circle {
    width: 120px;
    height: 120px;
  }
  
  .score-value {
    font-size: 2rem;
  }
  
  .category-scores {
    grid-template-columns: 1fr;
  }
}
```

## 7. Exemple d'Utilisation Complète

Voici un exemple complet de page de résultats de matching :

```html
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Résultats de Matching</title>
  
  <!-- CSS -->
  <link rel="stylesheet" href="../static/styles/nexten-modern-interactive.css">
  <link rel="stylesheet" href="../static/styles/matching-results.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
  
  <!-- SmartMatch Integration -->
  <script src="../static/scripts/smartmatch-integration.js"></script>
</head>
<body>
  <div class="container">
    <header class="header">
      <h1>Résultats de Matching</h1>
      <p class="subtitle">Voici la compatibilité entre votre profil et l'offre sélectionnée</p>
    </header>
    
    <main>
      <div id="matching-results" class="matching-results-container">
        <!-- Le contenu sera généré dynamiquement par SmartMatch.visualizeMatch() -->
        <div class="loading">
          <div class="spinner"></div>
          <p>Calcul du matching en cours...</p>
        </div>
      </div>
      
      <div class="actions">
        <a href="dashboard.html" class="btn btn-outline">
          <i class="fas fa-arrow-left"></i> Retour au tableau de bord
        </a>
        <a href="contact.html" class="btn btn-primary">
          Contacter un conseiller <i class="fas fa-arrow-right"></i>
        </a>
      </div>
    </main>
  </div>
  
  <script>
    document.addEventListener('DOMContentLoaded', function() {
      const resultContainer = document.getElementById('matching-results');
      
      if (resultContainer) {
        // Essayer de calculer le matching avec les données stockées
        SmartMatch.calculateStoredMatch()
          .then(result => {
            // Visualiser le résultat
            SmartMatch.visualizeMatch(result, resultContainer);
          })
          .catch(error => {
            console.error('Erreur lors du calcul du matching:', error);
            resultContainer.innerHTML = `
              <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Impossible de calculer le matching. Veuillez réessayer ultérieurement.</p>
              </div>
            `;
          });
      }
    });
  </script>
</body>
</html>
```

## 8. Conseils d'Intégration

- **Tests progressifs** : Intégrez une fonctionnalité à la fois, en commençant par la soumission des questionnaires.
- **Gestion des erreurs** : Ajoutez des messages d'erreur clairs et des alternatives pour les utilisateurs.
- **Caching** : Stockez les résultats calculés pour éviter des appels API inutiles.
- **Rétrocompatibilité** : Assurez-vous que votre site fonctionne même si l'API SmartMatch n'est pas disponible.