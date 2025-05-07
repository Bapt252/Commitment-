// Configuration et constantes
const JOB_PARSER_API_URL = 'http://localhost:5054/api/parse-job';
const USE_REAL_API = true; // Toujours utiliser l'API réelle
const DEBUG_MODE = true; // Activer le mode débogage

// Fonction pour journaliser les messages de débogage
function logDebug(message, data = null) {
  if (DEBUG_MODE) {
    if (data) {
      console.log(`[DEBUG] ${message}`, data);
    } else {
      console.log(`[DEBUG] ${message}`);
    }
  }
}

/**
 * Fonction pour analyser une fiche de poste via l'API
 * @param {File} file - Le fichier PDF de la fiche de poste
 * @returns {Promise} - Une promesse qui se résout avec les données extraites
 */
function parseJobDescription(file) {
  // Afficher l'indicateur de chargement s'il existe
  const loadingIndicator = document.querySelector('.analysis-loading');
  if (loadingIndicator) {
    loadingIndicator.style.display = 'flex';
  }
  
  // Mode API réelle (toujours activé)
  logDebug(`Envoi du fichier "${file.name}" à l'API de parsing au ${JOB_PARSER_API_URL}`);
  
  // Préparer les données du formulaire
  const formData = new FormData();
  formData.append('file', file);
  
  // Appeler l'API
  return fetch(JOB_PARSER_API_URL, {
    method: 'POST',
    body: formData
  })
  .then(response => {
    logDebug(`Réponse reçue avec statut: ${response.status}`);
    
    // Masquer l'indicateur de chargement
    if (loadingIndicator) {
      loadingIndicator.style.display = 'none';
    }
    
    if (!response.ok) {
      throw new Error(`Erreur HTTP: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    logDebug('Données extraites reçues:', data);
    return data;
  })
  .catch(error => {
    logDebug(`Erreur lors de l'appel API: ${error.message}`);
    console.error('Erreur:', error);
    
    // Masquer l'indicateur de chargement
    if (loadingIndicator) {
      loadingIndicator.style.display = 'none';
    }
    
    // Afficher un message d'erreur
    const errorElement = document.querySelector('.analysis-error');
    if (errorElement) {
      errorElement.textContent = `Erreur lors de l'analyse du fichier: ${error.message}`;
      errorElement.style.display = 'block';
      
      // Masquer le message après 5 secondes
      setTimeout(() => {
        errorElement.style.display = 'none';
      }, 5000);
    }
    
    throw error;
  });
}

/**
 * Fonction pour mettre à jour l'interface utilisateur avec les données extraites
 * @param {Object} jobData - Les données extraites de la fiche de poste
 */
function updateUIWithJobData(jobData) {
  logDebug("Mise à jour de l'interface avec les données:", jobData);
  
  // Mise à jour du champ affiché "Poste"
  const jobTitleDisplay = document.querySelector('.job-title-display');
  if (jobTitleDisplay) {
    jobTitleDisplay.textContent = jobData.title || 'Titre non disponible';
  }
  
  // Mise à jour du champ affiché "Compétences requises"
  const jobSkillsDisplay = document.querySelector('.job-skills-display');
  if (jobSkillsDisplay) {
    if (jobData.skills && jobData.skills.length > 0) {
      jobSkillsDisplay.textContent = jobData.skills.join(', ');
    } else {
      jobSkillsDisplay.textContent = 'Aucune compétence spécifiée';
    }
  }
  
  // Mise à jour du champ affiché "Expérience"
  const jobExperienceDisplay = document.querySelector('.job-experience-display');
  if (jobExperienceDisplay) {
    jobExperienceDisplay.textContent = jobData.experience || 'Non spécifié';
  }
  
  // Mise à jour du champ affiché "Type de contrat"
  const jobContractDisplay = document.querySelector('.job-contract-display');
  if (jobContractDisplay) {
    jobContractDisplay.textContent = jobData.contract_type || 'Non spécifié';
  }
  
  // Stocker les données complètes dans un champ caché pour une utilisation ultérieure
  const jobDataField = document.getElementById('job-data-hidden');
  if (jobDataField) {
    jobDataField.value = JSON.stringify(jobData);
  }
  
  // Afficher la section des informations extraites
  const extractedInfoSection = document.querySelector('.extracted-info-section');
  if (extractedInfoSection) {
    extractedInfoSection.style.display = 'block';
  }
  
  // Activer l'indicateur de succès
  const successIndicator = document.querySelector('.analysis-success');
  if (successIndicator) {
    successIndicator.style.display = 'block';
    setTimeout(() => {
      successIndicator.style.display = 'none';
    }, 5000);
  }
}

/**
 * Initialisation du système d'analyse de fiches de poste
 */
function initJobFileAnalysis() {
  logDebug("Initialisation du système d'analyse de fiches de poste");
  
  // Créer une section d'analyse si elle n'existe pas déjà
  if (!document.querySelector('.job-file-analysis')) {
    createAnalysisUI();
  }
  
  // Ajouter les écouteurs d'événements pour le sélecteur de fichier et le bouton d'analyse
  setupEventListeners();
}

/**
 * Création de l'interface d'analyse
 */
function createAnalysisUI() {
  logDebug("Création de l'interface d'analyse");
  
  // Rechercher l'élément parent où insérer l'interface d'analyse
  const descriptionSection = document.querySelector('.description-section') || 
                            document.querySelector('form') ||
                            document.body;
  
  if (!descriptionSection) {
    logDebug("Impossible de trouver un élément parent pour l'interface d'analyse");
    return;
  }
  
  // Créer l'élément HTML pour l'interface d'analyse
  const analysisUI = document.createElement('div');
  analysisUI.className = 'job-file-analysis';
  analysisUI.style.marginBottom = '20px';
  analysisUI.style.padding = '15px';
  analysisUI.style.border = '1px solid #ddd';
  analysisUI.style.borderRadius = '8px';
  analysisUI.style.backgroundColor = '#f9f9f9';
  
  analysisUI.innerHTML = `
    <div class="file-upload-section">
      <label for="job-file-input" style="display: block; margin-bottom: 8px; font-weight: bold;">Téléchargez votre fiche de poste (PDF)</label>
      <div style="display: flex; align-items: center;">
        <input type="file" id="job-file-input" accept=".pdf" style="flex: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
        <button id="analyze-job-button" style="margin-left: 10px; padding: 8px 16px; background-color: #4a148c; color: white; border: none; border-radius: 4px; cursor: pointer;">
          Analyser
        </button>
      </div>
    </div>
    
    <div class="analysis-loading" style="display: none; margin-top: 15px; align-items: center; color: #666;">
      <div class="loading-spinner" style="width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #4a148c; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px;"></div>
      <span>Analyse en cours...</span>
    </div>
    
    <div class="analysis-error" style="display: none; margin-top: 15px; padding: 8px; background-color: #ffebee; color: #c62828; border-radius: 4px;"></div>
    
    <div class="analysis-success" style="display: none; margin-top: 15px; padding: 8px; background-color: #e8f5e9; color: #2e7d32; border-radius: 4px;">
      Analyse réussie ! Les informations ont été extraites.
    </div>
    
    <div class="extracted-info-section" style="display: none; margin-top: 20px; padding: 15px; border: 1px solid #e0e0e0; border-radius: 4px; background-color: white;">
      <h4 style="margin-top: 0; margin-bottom: 15px; color: #4a148c;">Informations extraites de votre fiche de poste</h4>
      
      <div style="margin-bottom: 10px;">
        <strong>Poste :</strong> <span class="job-title-display">-</span>
      </div>
      
      <div style="margin-bottom: 10px;">
        <strong>Compétences requises :</strong> <span class="job-skills-display">-</span>
      </div>
      
      <div style="margin-bottom: 10px;">
        <strong>Expérience :</strong> <span class="job-experience-display">-</span>
      </div>
      
      <div style="margin-bottom: 10px;">
        <strong>Type de contrat :</strong> <span class="job-contract-display">-</span>
      </div>
      
      <input type="hidden" id="job-data-hidden">
    </div>
  `;
  
  // Ajouter l'élément à la page
  descriptionSection.appendChild(analysisUI);
  
  // Ajouter les styles pour l'animation
  const styleElement = document.createElement('style');
  styleElement.textContent = `
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `;
  document.head.appendChild(styleElement);
}

/**
 * Configuration des écouteurs d'événements
 */
function setupEventListeners() {
  logDebug("Configuration des écouteurs d'événements");
  
  const fileInput = document.getElementById('job-file-input');
  const analyzeButton = document.getElementById('analyze-job-button');
  
  if (fileInput && analyzeButton) {
    analyzeButton.addEventListener('click', function() {
      const file = fileInput.files[0];
      if (file) {
        if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
          parseJobDescription(file)
            .then(jobData => {
              updateUIWithJobData(jobData);
            })
            .catch(error => {
              logDebug(`Erreur lors de l'analyse: ${error.message}`);
              // L'erreur est déjà gérée dans parseJobDescription
            });
        } else {
          const errorElement = document.querySelector('.analysis-error');
          if (errorElement) {
            errorElement.textContent = 'Veuillez sélectionner un fichier PDF.';
            errorElement.style.display = 'block';
            setTimeout(() => {
              errorElement.style.display = 'none';
            }, 5000);
          }
        }
      } else {
        const errorElement = document.querySelector('.analysis-error');
        if (errorElement) {
          errorElement.textContent = 'Veuillez sélectionner un fichier.';
          errorElement.style.display = 'block';
          setTimeout(() => {
            errorElement.style.display = 'none';
          }, 5000);
        }
      }
    });
    
    // Masquer le message d'erreur lorsqu'un fichier est sélectionné
    fileInput.addEventListener('change', function() {
      const errorElement = document.querySelector('.analysis-error');
      if (errorElement) {
        errorElement.style.display = 'none';
      }
    });
  } else {
    logDebug("Éléments du formulaire non trouvés");
  }
}

// Initialiser le système d'analyse lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
  initJobFileAnalysis();
});

// Si le DOM est déjà chargé, initialiser immédiatement
if (document.readyState === 'interactive' || document.readyState === 'complete') {
  initJobFileAnalysis();
}
