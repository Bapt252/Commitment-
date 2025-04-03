// API de traitement des questionnaires candidats
const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Analyse les réponses du questionnaire candidat
 * @param {Object} answers - Réponses structurées du questionnaire
 * @returns {Promise<Object>} Résultat de l'analyse
 */
async function analyzeAnswers(answers) {
  try {
    const response = await fetch(`${API_BASE_URL}/candidates/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ answers }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors de l\'analyse du questionnaire');
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur:', error);
    throw error;
  }
}

/**
 * Affiche les résultats de l'analyse dans l'interface
 * @param {Object} results - Résultats de l'analyse
 * @param {HTMLElement} container - Élément HTML où afficher les résultats
 */
function displayAnalysisResults(results, container) {
  // Vider le conteneur
  container.innerHTML = '';
  
  // Domaines d'expertise
  const expertiseEl = document.createElement('div');
  expertiseEl.classList.add('result-section');
  expertiseEl.innerHTML = `
    <h3>Domaines d'expertise et d'intérêt</h3>
    <div class="tag-cloud">
      ${results.expertise.map(item => 
        `<div class="tag" style="font-size: ${10 + item.score * 10}px">
           ${item.domain} <span class="score">(${(item.score * 100).toFixed()}%)</span>
         </div>`
      ).join('')}
    </div>
  `;
  container.appendChild(expertiseEl);
  
  // Compétences techniques
  const skillsEl = document.createElement('div');
  skillsEl.classList.add('result-section');
  skillsEl.innerHTML = `
    <h3>Compétences techniques</h3>
    <div class="skills-grid">
      <div class="skills-column">
        <h4>Compétences explicites</h4>
        <ul>
          ${results.skills.explicit.map(skill => 
            `<li>${skill.name} <span class="confidence">(${(skill.confidence * 100).toFixed()}%)</span></li>`
          ).join('')}
        </ul>
      </div>
      <div class="skills-column">
        <h4>Compétences implicites</h4>
        <ul>
          ${results.skills.implicit.map(skill => 
            `<li>${skill.name} <span class="confidence">(${(skill.confidence * 100).toFixed()}%)</span></li>`
          ).join('')}
        </ul>
      </div>
    </div>
  `;
  container.appendChild(skillsEl);
  
  // Soft skills
  const softSkillsEl = document.createElement('div');
  softSkillsEl.classList.add('result-section');
  softSkillsEl.innerHTML = `
    <h3>Soft skills</h3>
    <div class="soft-skills-chart">
      ${results.soft_skills.map(skill => 
        `<div class="soft-skill-bar">
           <div class="soft-skill-name">${skill.name}</div>
           <div class="soft-skill-bar-outer">
             <div class="soft-skill-bar-inner" style="width: ${skill.score * 100}%"></div>
           </div>
           <div class="soft-skill-score">${(skill.score * 100).toFixed()}%</div>
         </div>`
      ).join('')}
    </div>
  `;
  container.appendChild(softSkillsEl);
  
  // Préférences professionnelles
  const preferencesEl = document.createElement('div');
  preferencesEl.classList.add('result-section');
  preferencesEl.innerHTML = `
    <h3>Préférences professionnelles</h3>
    <div class="preferences-grid">
      <div class="preference-item">
        <strong>Mode de travail :</strong> ${results.preferences.remote ? 'Remote' : 'Présentiel'}
        ${results.preferences.remote_percentage ? `(${results.preferences.remote_percentage}% remote)` : ''}
      </div>
      <div class="preference-item">
        <strong>Taille d'entreprise :</strong> ${results.preferences.company_size}
      </div>
      <div class="preference-item">
        <strong>Secteurs préférés :</strong> ${results.preferences.sectors.preferred.join(', ') || 'Non spécifié'}
      </div>
      <div class="preference-item">
        <strong>Secteurs à éviter :</strong> ${results.preferences.sectors.avoided.join(', ') || 'Non spécifié'}
      </div>
      <div class="preference-item">
        <strong>Salaire attendu :</strong> ${results.preferences.salary_range.formatted}
      </div>
      <div class="preference-item">
        <strong>Disponibilité :</strong> ${results.preferences.availability}
      </div>
    </div>
  `;
  container.appendChild(preferencesEl);
  
  // Niveau d'expérience et d'éducation
  const experienceEl = document.createElement('div');
  experienceEl.classList.add('result-section');
  experienceEl.innerHTML = `
    <h3>Expérience et éducation</h3>
    <div class="experience-container">
      <div class="experience-item">
        <strong>Niveau d'expérience :</strong> ${results.experience.level}
      </div>
      <div class="experience-item">
        <strong>Années d'expérience :</strong> ${results.experience.years} ans
      </div>
      <div class="experience-item">
        <strong>Niveau d'éducation :</strong> ${results.education.level}
      </div>
      <div class="experience-item">
        <strong>Domaine d'étude :</strong> ${results.education.field}
      </div>
    </div>
  `;
  container.appendChild(experienceEl);
}

/**
 * Générère des données de test pour simuler l'analyse
 * Utilisé seulement si l'API n'est pas disponible
 * @returns {Object} Données simulées pour les tests
 */
function generateMockAnalysisResults() {
  return {
    expertise: [
      { domain: "Développement Web", score: 0.85 },
      { domain: "Data Science", score: 0.65 },
      { domain: "Gestion De Projet", score: 0.45 },
      { domain: "Marketing Digital", score: 0.25 },
      { domain: "Finance", score: 0.15 }
    ],
    skills: {
      explicit: [
        { name: "JavaScript", confidence: 0.95 },
        { name: "React", confidence: 0.92 },
        { name: "Python", confidence: 0.88 },
        { name: "Node.js", confidence: 0.85 },
        { name: "SQL", confidence: 0.80 }
      ],
      implicit: [
        { name: "Méthodologie Agile", confidence: 0.75 },
        { name: "UX/UI Design", confidence: 0.68 },
        { name: "APIs REST", confidence: 0.65 },
        { name: "Git", confidence: 0.60 },
        { name: "Docker", confidence: 0.55 }
      ]
    },
    soft_skills: [
      { name: "Communication", score: 0.88 },
      { name: "Travail d'équipe", score: 0.85 },
      { name: "Adaptabilité", score: 0.82 },
      { name: "Résolution de problèmes", score: 0.78 },
      { name: "Leadership", score: 0.65 }
    ],
    preferences: {
      remote: true,
      remote_percentage: 80,
      company_size: "Startup, PME",
      sectors: {
        preferred: ["Technologie", "Santé", "Éducation"],
        avoided: ["Finance", "Industrie lourde"]
      },
      salary_range: {
        min: 45000,
        max: 55000,
        formatted: "45K€ - 55K€"
      },
      availability: "Dans 1 mois"
    },
    experience: {
      level: "Intermédiaire",
      years: 4
    },
    education: {
      level: "Master",
      field: "Informatique"
    }
  };
}

// Exporter les fonctions
window.candidateAnalyzer = {
  analyzeAnswers,
  displayAnalysisResults,
  generateMockAnalysisResults
};