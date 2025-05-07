// Configuration et constantes
const JOB_PARSER_API_URL = 'http://localhost:5054/api/parse-job';
const USE_REAL_API = true; // Définir à true pour utiliser l'API réelle, false pour la simulation

/**
 * Fonction pour analyser une fiche de poste via l'API
 * @param {File} file - Le fichier PDF de la fiche de poste
 * @returns {Promise} - Une promesse qui se résout avec les données extraites
 */
function parseJobDescription(file) {
  // Afficher un indicateur de chargement si disponible
  const loadingIndicator = document.getElementById('loading-indicator');
  if (loadingIndicator) {
    loadingIndicator.style.display = 'block';
  }
  
  if (!USE_REAL_API) {
    // Mode simulation - retourne des données fictives après un délai
    console.log('Mode simulation activé - génération de données simulées');
    return new Promise((resolve) => {
      setTimeout(() => {
        // Masquer l'indicateur de chargement
        if (loadingIndicator) {
          loadingIndicator.style.display = 'none';
        }
        
        // Retourner des données simulées
        resolve({
          title: "Développeur Full Stack",
          skills: ["JavaScript", "React", "Node.js", "Python", "MongoDB"],
          contract_type: "CDI",
          location: "Paris",
          experience: "3-5 ans d'expérience",
          education: "Bac+5",
          salary: "",
          company: ""
        });
      }, 1500); // Délai simulé de 1.5 secondes
    });
  }
  
  // Mode API réelle
  console.log(`Envoi du fichier "${file.name}" à l'API de parsing`);
  
  // Préparer les données du formulaire
  const formData = new FormData();
  formData.append('file', file);
  
  // Appeler l'API
  return fetch(JOB_PARSER_API_URL, {
    method: 'POST',
    body: formData
  })
  .then(response => {
    console.log(`Réponse reçue avec statut: ${response.status}`);
    
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
    console.log('Données extraites reçues:', data);
    return data;
  })
  .catch(error => {
    console.error('Erreur lors de l\'analyse de la fiche de poste:', error);
    
    // Masquer l'indicateur de chargement
    if (loadingIndicator) {
      loadingIndicator.style.display = 'none';
    }
    
    // Afficher un message d'erreur
    const errorElement = document.getElementById('error-message');
    if (errorElement) {
      errorElement.textContent = `Erreur lors de l'analyse du fichier: ${error.message}`;
      errorElement.style.display = 'block';
    }
    
    throw error;
  });
}

/**
 * Fonction pour mettre à jour l'interface utilisateur avec les données extraites
 * @param {Object} jobData - Les données extraites de la fiche de poste
 */
function updateUIWithJobData(jobData) {
  // Mise à jour du titre du poste
  const titleField = document.getElementById('job-title');
  if (titleField) {
    titleField.value = jobData.title || '';
  }
  
  // Mise à jour des compétences requises
  const skillsField = document.getElementById('job-skills');
  if (skillsField) {
    skillsField.value = jobData.skills ? jobData.skills.join(', ') : '';
  }
  
  // Mise à jour du type de contrat
  const contractField = document.getElementById('job-contract');
  if (contractField) {
    contractField.value = jobData.contract_type || '';
  }
  
  // Mise à jour de la localisation
  const locationField = document.getElementById('job-location');
  if (locationField) {
    locationField.value = jobData.location || '';
  }
  
  // Mise à jour de l'expérience requise
  const experienceField = document.getElementById('job-experience');
  if (experienceField) {
    experienceField.value = jobData.experience || '';
  }
  
  // Mise à jour du niveau d'éducation
  const educationField = document.getElementById('job-education');
  if (educationField) {
    educationField.value = jobData.education || '';
  }
  
  // Ajoutez d'autres champs selon votre interface
}

/**
 * Gestionnaire d'événement pour le téléchargement de la fiche de poste
 * À ajouter à votre code existant
 */
function setupJobFileUpload() {
  const fileInput = document.getElementById('job-file-input');
  const uploadButton = document.getElementById('analyze-job-button');
  
  if (fileInput && uploadButton) {
    uploadButton.addEventListener('click', function() {
      const file = fileInput.files[0];
      if (file) {
        if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
          // Analyser le fichier PDF
          parseJobDescription(file)
            .then(jobData => {
              // Mettre à jour l'interface utilisateur avec les données extraites
              updateUIWithJobData(jobData);
              
              // Afficher un message de succès
              const successMessage = document.getElementById('success-message');
              if (successMessage) {
                successMessage.textContent = 'Analyse réussie ! Les champs ont été pré-remplis.';
                successMessage.style.display = 'block';
                
                // Masquer le message après 5 secondes
                setTimeout(() => {
                  successMessage.style.display = 'none';
                }, 5000);
              }
            })
            .catch(error => {
              console.error('Erreur:', error);
            });
        } else {
          // Afficher un message d'erreur pour les fichiers non-PDF
          const errorElement = document.getElementById('error-message');
          if (errorElement) {
            errorElement.textContent = 'Veuillez sélectionner un fichier PDF.';
            errorElement.style.display = 'block';
          }
        }
      } else {
        // Afficher un message d'erreur si aucun fichier n'est sélectionné
        const errorElement = document.getElementById('error-message');
        if (errorElement) {
          errorElement.textContent = 'Veuillez sélectionner un fichier.';
          errorElement.style.display = 'block';
        }
      }
    });
    
    // Masquer le message d'erreur lorsqu'un fichier est sélectionné
    fileInput.addEventListener('change', function() {
      const errorElement = document.getElementById('error-message');
      if (errorElement) {
        errorElement.style.display = 'none';
      }
    });
  }
}

// Initialiser la fonctionnalité de téléchargement de fichier lorsque le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
  setupJobFileUpload();
  console.log('Fonctionnalité d\'analyse de fiches de poste initialisée');
});
