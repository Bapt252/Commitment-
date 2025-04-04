/**
 * Module client pour le système de matching XGBoost
 * Permet d'interagir avec l'API de matching basée sur XGBoost
 */

// Configuration de l'API
const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Récupère les recommendations de candidats pour une entreprise en utilisant XGBoost
 * @param {string} companyId - Identifiant de l'entreprise
 * @param {Object} options - Options de filtrage
 * @param {number} options.limit - Nombre maximum de résultats (défaut: 10)
 * @param {number} options.minScore - Score minimal de matching en % (défaut: 50)
 * @returns {Promise<Object>} - Résultats du matching
 */
async function getXGBoostMatchingResults(companyId, options = {}) {
  try {
    const limit = options.limit || 10;
    const minScore = options.minScore || 50;
    
    const url = new URL(`${API_BASE_URL}/companies/match-xgboost/${companyId}/candidates`);
    url.searchParams.append('limit', limit);
    url.searchParams.append('min_score', minScore);
    
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors du matching XGBoost');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Erreur lors du matching XGBoost :', error);
    throw error;
  }
}

/**
 * Compare les résultats de matching entre l'algorithme traditionnel et XGBoost
 * @param {string} companyId - Identifiant de l'entreprise
 * @returns {Promise<Object>} - Comparaison des résultats
 */
async function compareMatchingAlgorithms(companyId) {
  try {
    // Récupérer les résultats des deux algorithmes
    const [traditionalResults, xgboostResults] = await Promise.all([
      fetch(`${API_BASE_URL}/companies/match/${companyId}/candidates`).then(r => r.json()),
      fetch(`${API_BASE_URL}/companies/match-xgboost/${companyId}/candidates`).then(r => r.json())
    ]);
    
    // Création d'un objet pour comparer les résultats
    const comparison = {
      traditional: {
        results: traditionalResults.results,
        count: traditionalResults.count,
        topCandidates: traditionalResults.results.slice(0, 3).map(r => ({
          id: r.candidate_id,
          name: r.candidate_name,
          score: r.match_score
        }))
      },
      xgboost: {
        results: xgboostResults.results,
        count: xgboostResults.count,
        topCandidates: xgboostResults.results.slice(0, 3).map(r => ({
          id: r.candidate_id,
          name: r.candidate_name,
          score: r.match_score
        }))
      },
      differences: {}
    };
    
    // Analyser les différences
    const traditionalMap = new Map(traditionalResults.results.map(r => [r.candidate_id, r]));
    const xgboostMap = new Map(xgboostResults.results.map(r => [r.candidate_id, r]));
    
    // Candidats présents dans les deux résultats
    const commonCandidates = [...traditionalMap.keys()].filter(id => xgboostMap.has(id));
    
    // Différences de scores pour les candidats communs
    const scoreDifferences = commonCandidates.map(id => {
      const traditionalScore = traditionalMap.get(id).match_score;
      const xgboostScore = xgboostMap.get(id).match_score;
      return {
        candidate_id: id,
        candidate_name: traditionalMap.get(id).candidate_name,
        traditional_score: traditionalScore,
        xgboost_score: xgboostScore,
        difference: xgboostScore - traditionalScore
      };
    });
    
    // Trier par différence absolue
    scoreDifferences.sort((a, b) => Math.abs(b.difference) - Math.abs(a.difference));
    
    comparison.differences = {
      commonCandidates: commonCandidates.length,
      significantChanges: scoreDifferences.filter(d => Math.abs(d.difference) > 10).length,
      largestChanges: scoreDifferences.slice(0, 3)
    };
    
    return comparison;
  } catch (error) {
    console.error('Erreur lors de la comparaison des algorithmes :', error);
    throw error;
  }
}

/**
 * Affiche les résultats de matching XGBoost dans l'interface
 * @param {Object} results - Résultats du matching
 * @param {HTMLElement} container - Élément DOM où afficher les résultats
 */
function displayXGBoostResults(results, container) {
  // Vider le conteneur
  container.innerHTML = '';
  
  // En-tête
  const header = document.createElement('div');
  header.className = 'matching-header';
  header.innerHTML = `
    <h3>Résultats de matching optimisé avec XGBoost</h3>
    <p class="matching-count">${results.count} candidats correspondants</p>
  `;
  container.appendChild(header);
  
  // Liste des candidats
  const candidatesList = document.createElement('div');
  candidatesList.className = 'candidates-list';
  
  results.results.forEach(candidate => {
    const candidateCard = document.createElement('div');
    candidateCard.className = 'candidate-card';
    
    // Définir la classe de score
    let scoreClass = 'score-medium';
    if (candidate.match_score >= 80) {
      scoreClass = 'score-high';
    } else if (candidate.match_score < 60) {
      scoreClass = 'score-low';
    }
    
    // Créer la structure HTML pour le candidat
    candidateCard.innerHTML = `
      <div class="candidate-header">
        <h4>${candidate.candidate_name}</h4>
        <span class="match-score ${scoreClass}">${Math.round(candidate.match_score)}%</span>
      </div>
      <div class="candidate-title">${candidate.title || 'Non spécifié'}</div>
      <div class="category-scores">
        ${Object.entries(candidate.category_scores).map(([category, score]) => `
          <div class="category-score">
            <div class="category-label">${formatCategoryName(category)}</div>
            <div class="score-bar">
              <div class="score-fill" style="width: ${score}%"></div>
            </div>
            <div class="score-value">${Math.round(score)}%</div>
          </div>
        `).join('')}
      </div>
      <div class="candidate-actions">
        <button class="btn-view-profile">Voir le profil</button>
        <button class="btn-contact">Contacter</button>
      </div>
    `;
    
    candidatesList.appendChild(candidateCard);
  });
  
  container.appendChild(candidatesList);
  
  // Ajouter des événements aux boutons (à implémenter selon les besoins)
  container.querySelectorAll('.btn-view-profile').forEach(button => {
    button.addEventListener('click', function() {
      // Implémentation à ajouter
      console.log('Voir le profil du candidat');
    });
  });
  
  container.querySelectorAll('.btn-contact').forEach(button => {
    button.addEventListener('click', function() {
      // Implémentation à ajouter
      console.log('Contacter le candidat');
    });
  });
}

/**
 * Formate le nom d'une catégorie pour l'affichage
 * @param {string} category - Nom de la catégorie
 * @returns {string} - Nom formaté
 */
function formatCategoryName(category) {
  const categoryNames = {
    'skills': 'Compétences',
    'experience': 'Expérience',
    'values': 'Valeurs',
    'work_environment': 'Environnement',
    'education': 'Formation'
  };
  
  return categoryNames[category] || category;
}

// Exporter les fonctions pour l'utilisation dans d'autres modules
window.xgboostMatching = {
  getXGBoostMatchingResults,
  compareMatchingAlgorithms,
  displayXGBoostResults
};