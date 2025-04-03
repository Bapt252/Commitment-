// Interaction avec l'API de parsing de CV et fiches de poste

const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Parse un document à partir de texte 
 * @param {string} text - Texte à analyser
 * @returns {Promise<Object>} Résultat du parsing
 */
async function parseDocumentText(text) {
  try {
    const response = await fetch(`${API_BASE_URL}/jobs/parse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors du parsing du document');
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur:', error);
    throw error;
  }
}

/**
 * Parse un document à partir d'un fichier
 * @param {File} file - Fichier à analyser
 * @returns {Promise<Object>} Résultat du parsing
 */
async function parseDocumentFile(file) {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/jobs/parse-file`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Erreur lors du parsing du fichier');
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur:', error);
    throw error;
  }
}

/**
 * Affiche les résultats du parsing dans l'interface
 * @param {Object} results - Résultats du parsing
 * @param {HTMLElement} container - Élément HTML où afficher les résultats
 */
function displayParsingResults(results, container) {
  // Vider le conteneur
  container.innerHTML = '';
  
  // Informations sur le type de document
  const docTypeEl = document.createElement('div');
  docTypeEl.classList.add('result-section', 'document-type');
  docTypeEl.innerHTML = `
    <h3>Type de document: ${results.doc_type === 'cv' ? 'CV' : 'Fiche de poste'}</h3>
    <p>Score de confiance global: ${(results.confidence_scores.global * 100).toFixed(1)}%</p>
  `;
  container.appendChild(docTypeEl);
  
  // Afficher les données extraites selon le type de document
  const dataEl = document.createElement('div');
  dataEl.classList.add('result-section', 'extracted-data');
  
  let dataHTML = '<h3>Informations extraites</h3><div class="results-grid">';
  
  const data = results.extracted_data;
  
  if (results.doc_type === 'cv') {
    // Affichage pour un CV
    dataHTML += `
      <div class="result-item"><strong>Nom:</strong> ${formatValue(data.nom)}</div>
      <div class="result-item"><strong>Titre:</strong> ${formatValue(data.titre)}</div>
    `;
    
    // Contact
    if (data.contact && typeof data.contact === 'object') {
      dataHTML += '<div class="result-item"><strong>Contact:</strong><ul>';
      for (const [key, value] of Object.entries(data.contact)) {
        dataHTML += `<li>${key}: ${value}</li>`;
      }
      dataHTML += '</ul></div>';
    }
    
    // Compétences
    if (Array.isArray(data.competences)) {
      dataHTML += '<div class="result-item"><strong>Compétences:</strong><ul>';
      data.competences.forEach(skill => {
        if (skill !== 'Non spécifié') {
          dataHTML += `<li>${skill}</li>`;
        }
      });
      dataHTML += '</ul></div>';
    }
    
    // Formation
    if (Array.isArray(data.formation)) {
      dataHTML += '<div class="result-item"><strong>Formation:</strong><ul>';
      data.formation.forEach(edu => {
        if (edu.degree !== 'Non spécifié') {
          let eduStr = edu.degree;
          if (edu.institution) eduStr += ` - ${edu.institution}`;
          if (edu.period) eduStr += ` (${edu.period})`;
          dataHTML += `<li>${eduStr}</li>`;
        }
      });
      dataHTML += '</ul></div>';
    }
    
    // Expérience
    if (Array.isArray(data.experience)) {
      dataHTML += '<div class="result-item"><strong>Expérience:</strong><ul>';
      data.experience.forEach(exp => {
        if (exp.title !== 'Non spécifié') {
          let expStr = exp.title;
          if (exp.period) expStr += ` (${exp.period})`;
          dataHTML += `<li>${expStr}</li>`;
        }
      });
      dataHTML += '</ul></div>';
    }
    
    // Langues
    if (Array.isArray(data.langues)) {
      dataHTML += '<div class="result-item"><strong>Langues:</strong><ul>';
      data.langues.forEach(lang => {
        if (lang.language !== 'Non spécifié') {
          let langStr = lang.language;
          if (lang.level) langStr += ` - ${lang.level}`;
          dataHTML += `<li>${langStr}</li>`;
        }
      });
      dataHTML += '</ul></div>';
    }
    
  } else {
    // Affichage pour une fiche de poste
    dataHTML += `
      <div class="result-item"><strong>Titre du poste:</strong> ${formatValue(data.titre)}</div>
      <div class="result-item"><strong>Expérience requise:</strong> ${formatValue(data.experience)}</div>
      <div class="result-item"><strong>Type de contrat:</strong> ${formatValue(data.contrat)}</div>
      <div class="result-item"><strong>Localisation:</strong> ${formatValue(data.localisation)}</div>
      <div class="result-item"><strong>Rémunération:</strong> ${formatValue(data.remuneration)}</div>
    `;
    
    // Compétences
    if (Array.isArray(data.competences)) {
      dataHTML += '<div class="result-item"><strong>Compétences requises:</strong><ul>';
      data.competences.forEach(skill => {
        if (skill !== 'Non spécifié') {
          dataHTML += `<li>${skill}</li>`;
        }
      });
      dataHTML += '</ul></div>';
    }
    
    // Formation
    if (data.formation) {
      dataHTML += '<div class="result-item"><strong>Formation:</strong> ';
      if (Array.isArray(data.formation)) {
        dataHTML += '<ul>';
        data.formation.forEach(edu => {
          dataHTML += `<li>${edu}</li>`;
        });
        dataHTML += '</ul>';
      } else {
        dataHTML += formatValue(data.formation);
      }
      dataHTML += '</div>';
    }
  }
  
  dataHTML += '</div>';
  dataEl.innerHTML = dataHTML;
  container.appendChild(dataEl);
  
  // Afficher les scores de confiance si nécessaire
  const scoreEl = document.createElement('div');
  scoreEl.classList.add('result-section', 'confidence-scores');
  scoreEl.innerHTML = `
    <h3>Scores de confiance</h3>
    <details>
      <summary>Voir les scores détaillés</summary>
      <table>
        <tr><th>Champ</th><th>Score</th></tr>
        ${Object.entries(results.confidence_scores).map(([field, score]) => 
          `<tr><td>${field}</td><td>${(score * 100).toFixed(1)}%</td></tr>`
        ).join('')}
      </table>
    </details>
  `;
  container.appendChild(scoreEl);
}

/**
 * Formate une valeur pour l'affichage
 * @param {*} value - Valeur à formater
 * @returns {string} Valeur formatée
 */
function formatValue(value) {
  if (value === undefined || value === null) {
    return 'Non spécifié';
  }
  if (value === 'Non spécifié') {
    return value;
  }
  return value;
}

// Exporter les fonctions
window.documentParser = {
  parseDocumentText,
  parseDocumentFile,
  displayParsingResults
};