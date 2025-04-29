/**
 * cv-to-form-connector.js - Script pour connecter le service de parsing CV au formulaire candidat
 */

/**
 * Classe principale pour gérer la connexion entre le parsing CV et le formulaire
 */
class CvToFormConnector {
  constructor() {
    this.apiBaseUrl = '/api/v1'; // URL de base de l'API
    this.parsedData = null;
  }

  /**
   * Initialise le connecteur
   * @param {Object} options - Options de configuration
   */
  init(options = {}) {
    if (options.apiBaseUrl) {
      this.apiBaseUrl = options.apiBaseUrl;
    }

    // Vérifier si on a un ID de CV dans les paramètres d'URL
    this.checkUrlForCvId();

    // Écouter les événements personnalisés pour le parsing CV
    document.addEventListener('cv:parsed', this.handleCvParsed.bind(this));

    console.log('CV to Form Connector initialisé');
  }

  /**
   * Vérifie si l'URL contient un ID de CV parsé
   */
  checkUrlForCvId() {
    const urlParams = new URLSearchParams(window.location.search);
    const cvId = urlParams.get('cv_id');
    
    if (cvId) {
      console.log(`ID de CV détecté dans l'URL: ${cvId}`);
      this.fetchCvData(cvId);
    }
  }

  /**
   * Récupère les données d'un CV parsé depuis l'API
   * @param {string} cvId - Identifiant du CV parsé
   */
  fetchCvData(cvId) {
    fetch(`${this.apiBaseUrl}/parse-results/${cvId}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Erreur lors de la récupération des données du CV (${response.status})`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Données du CV récupérées avec succès:', data);
        this.parsedData = data;
        this.storeDataAndRedirect();
      })
      .catch(error => {
        console.error('Erreur lors de la récupération des données du CV:', error);
        this.showError('Impossible de récupérer les données du CV. Veuillez réessayer.');
      });
  }

  /**
   * Gère l'événement de parsing CV terminé
   * @param {CustomEvent} event - Événement personnalisé contenant les données parsées
   */
  handleCvParsed(event) {
    console.log('Événement de parsing CV reçu:', event);
    if (event.detail && event.detail.data) {
      this.parsedData = event.detail.data;
      this.storeDataAndRedirect();
    } else {
      console.error('Événement de parsing CV reçu sans données');
    }
  }

  /**
   * Stocke les données parsées et redirige vers le formulaire
   */
  storeDataAndRedirect() {
    if (!this.parsedData) {
      console.error('Aucune donnée à stocker');
      return;
    }

    try {
      // Stocker les données dans sessionStorage pour les récupérer depuis le formulaire
      sessionStorage.setItem('parsedCandidateData', JSON.stringify(this.parsedData));
      
      // Rediriger vers le formulaire candidat
      window.location.href = './templates/candidate-questionnaire.html';
    } catch (error) {
      console.error('Erreur lors du stockage des données:', error);
      this.showError('Impossible de stocker les données. Veuillez réessayer.');
    }
  }

  /**
   * Soumet un CV pour parsing et attend le résultat
   * @param {File} cvFile - Fichier CV à parser
   * @returns {Promise} - Promesse résolue avec les données parsées
   */
  submitCvForParsing(cvFile) {
    if (!cvFile) {
      return Promise.reject(new Error('Aucun fichier CV fourni'));
    }

    // Créer un FormData pour l'envoi du fichier
    const formData = new FormData();
    formData.append('file', cvFile);

    return fetch(`${this.apiBaseUrl}/parse`, {
      method: 'POST',
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Erreur lors du parsing du CV (${response.status})`);
      }
      return response.json();
    })
    .then(data => {
      console.log('CV parsé avec succès:', data);
      this.parsedData = data;
      
      // Déclencher un événement pour informer l'application
      const event = new CustomEvent('cv:parsed', {
        detail: { data: data }
      });
      document.dispatchEvent(event);
      
      return data;
    });
  }

  /**
   * Affiche un message d'erreur à l'utilisateur
   * @param {string} message - Message d'erreur à afficher
   */
  showError(message) {
    // Chercher la fonction d'affichage de notification dans l'application
    if (window.showNotification) {
      window.showNotification(message, 'error');
    } else {
      // Fallback sur une alerte standard
      alert(message);
    }
  }

  /**
   * Convertit les données du format backend au format du formulaire
   * @param {Object} backendData - Données au format du backend
   * @returns {Object} - Données au format du formulaire
   */
  convertBackendDataToFormFormat(backendData) {
    // Cette fonction transforme les données du format API au format du formulaire
    // Elle est implémentée dans form-prefiller.js
    if (!backendData || !backendData.data) {
      console.error('Données invalides pour la conversion');
      return null;
    }

    // Créer une structure compatible avec le formulaire (version simplifée ici)
    // La version complète est dans form-prefiller.js (transformCvDataToFormData)
    return {
      personalInfo: {
        fullName: backendData.data.personal_info?.name || '',
        jobTitle: backendData.data.position || ''
      },
      mobility: {
        transportMethods: ['public-transport'],
        commuteTimes: { 'public-transport': '30' },
        address: backendData.data.personal_info?.address || '',
        officePreference: 'no-preference'
      },
      motivations: {
        order: ['remuneration', 'evolution', 'flexibility', 'location', 'other'],
        structureTypes: ['no-preference'],
        salaryRange: ''
      },
      availability: {
        timeframe: '1month',
        currentlyEmployed: false,
        recruitmentStatus: 'no-leads'
      }
    };
  }
}

// Créer et exporter l'instance du connecteur
window.cvToFormConnector = new CvToFormConnector();

// Initialiser automatiquement si le script est chargé dans la page de téléchargement de CV
document.addEventListener('DOMContentLoaded', function() {
  // Vérifier si nous sommes sur la page de téléchargement de CV
  const uploadForm = document.getElementById('cv-upload-form');
  
  if (uploadForm) {
    console.log('Page de téléchargement de CV détectée, initialisation du connecteur');
    window.cvToFormConnector.init();
    
    // Ajouter l'écouteur d'événement pour le téléchargement de CV
    uploadForm.addEventListener('submit', function(event) {
      event.preventDefault();
      
      const fileInput = document.getElementById('cv-file-input');
      if (fileInput && fileInput.files.length > 0) {
        // Montrer un indicateur de chargement
        if (window.showLoadingOverlay) {
          window.showLoadingOverlay('Analyse de votre CV en cours...');
        }
        
        // Soumettre le CV pour parsing
        window.cvToFormConnector.submitCvForParsing(fileInput.files[0])
          .then(() => {
            // Le connecteur gère la redirection
          })
          .catch(error => {
            console.error('Erreur lors du traitement du CV:', error);
            window.cvToFormConnector.showError('Erreur lors du traitement du CV. Veuillez réessayer.');
            
            // Cacher l'indicateur de chargement
            if (window.hideLoadingOverlay) {
              window.hideLoadingOverlay();
            }
          });
      } else {
        window.cvToFormConnector.showError('Veuillez sélectionner un fichier CV à analyser.');
      }
    });
  } else {
    console.log('Page de téléchargement de CV non détectée');
  }
});