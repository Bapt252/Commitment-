/**
 * cv-to-form-connector.js - Script pour connecter le service de parsing CV au formulaire candidat
 * Version améliorée avec support de GitHub Pages et données mockées
 */

/**
 * Classe principale pour gérer la connexion entre le parsing CV et le formulaire
 */
class CvToFormConnector {
  constructor() {
    this.apiBaseUrl = '/api/v1'; // URL de base de l'API
    this.parsedData = null;
    this.isDemo = window.location.hostname.includes('github.io') || 
                  window.location.hostname === 'localhost' || 
                  window.location.hostname === '127.0.0.1';
  }

  /**
   * Initialise le connecteur
   * @param {Object} options - Options de configuration
   */
  init(options = {}) {
    if (options.apiBaseUrl) {
      this.apiBaseUrl = options.apiBaseUrl;
    }

    console.log(`CV to Form Connector initialisé - Mode ${this.isDemo ? 'DÉMO' : 'PRODUCTION'}`);

    // Vérifier si on a un ID de CV dans les paramètres d'URL
    this.checkUrlForCvId();

    // Écouter les événements personnalisés pour le parsing CV
    document.addEventListener('cv:parsed', this.handleCvParsed.bind(this));

    // Précharger l'adaptateur API si nous sommes en mode démo
    if (this.isDemo && !window.ApiAdapter) {
      this.loadApiAdapter();
    }
  }

  /**
   * Charge l'adaptateur API dynamiquement si nécessaire
   */
  loadApiAdapter() {
    const script = document.createElement('script');
    script.src = "../static/scripts/api-adapter.js";
    script.onload = () => {
      console.log("CV to Form Connector: Adaptateur API chargé avec succès");
    };
    document.head.appendChild(script);
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
    // Utiliser l'adaptateur API si disponible
    if (window.ApiAdapter) {
      window.ApiAdapter.get(`/parsed_data/${cvId}`)
        .then(data => {
          console.log('Données du CV récupérées avec succès:', data);
          this.parsedData = data;
          
          // Marquer comme simulé si en mode démo
          if (this.isDemo && !this.parsedData.isSimulated) {
            this.parsedData.isSimulated = true;
          }
          
          this.storeDataAndRedirect();
        })
        .catch(error => {
          console.error('Erreur lors de la récupération des données du CV:', error);
          this.handleApiError();
        });
      return;
    }

    // Méthode traditionnelle si l'adaptateur n'est pas disponible
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
        
        // Marquer comme simulé si en mode démo
        if (this.isDemo && !this.parsedData.isSimulated) {
          this.parsedData.isSimulated = true;
        }
        
        this.storeDataAndRedirect();
      })
      .catch(error => {
        console.error('Erreur lors de la récupération des données du CV:', error);
        this.handleApiError();
      });
  }

  /**
   * Gère les erreurs d'API en mode démo
   */
  handleApiError() {
    if (this.isDemo) {
      console.log("Mode démo: Utilisation des données mockées pour le fallback");
      
      // Charger les données mockées
      const script = document.createElement('script');
      script.src = "../static/scripts/parsed-data-example.js";
      script.onload = () => {
        if (typeof mockParsedData !== 'undefined') {
          this.parsedData = mockParsedData;
          this.parsedData.isSimulated = true;
          this.storeDataAndRedirect();
        } else {
          this.showError('Impossible de récupérer les données du CV, même en mode démo.');
        }
      };
      document.head.appendChild(script);
    } else {
      this.showError('Impossible de récupérer les données du CV. Veuillez réessayer.');
    }
  }

  /**
   * Gère l'événement de parsing CV terminé
   * @param {CustomEvent} event - Événement personnalisé contenant les données parsées
   */
  handleCvParsed(event) {
    console.log('Événement de parsing CV reçu:', event);
    if (event.detail && event.detail.data) {
      this.parsedData = event.detail.data;
      
      // Marquer comme simulé si en mode démo
      if (this.isDemo && !this.parsedData.isSimulated) {
        this.parsedData.isSimulated = true;
      }
      
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

    // Utiliser l'adaptateur API si disponible
    if (window.ApiAdapter) {
      console.log("Utilisation de l'adaptateur API pour le parsing");
      return window.ApiAdapter.post('/parse', formData)
        .then(data => {
          console.log('CV parsé avec succès via adaptateur:', data);
          this.parsedData = data;
          
          // Marquer comme simulé si en mode démo
          if (this.isDemo && !this.parsedData.isSimulated) {
            this.parsedData.isSimulated = true;
          }
          
          // Déclencher un événement pour informer l'application
          const event = new CustomEvent('cv:parsed', {
            detail: { data: this.parsedData }
          });
          document.dispatchEvent(event);
          
          return this.parsedData;
        });
    }

    // Méthode traditionnelle si l'adaptateur n'est pas disponible
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
      
      // Marquer comme simulé si en mode démo
      if (this.isDemo && !this.parsedData.isSimulated) {
        this.parsedData.isSimulated = true;
      }
      
      // Déclencher un événement pour informer l'application
      const event = new CustomEvent('cv:parsed', {
        detail: { data: this.parsedData }
      });
      document.dispatchEvent(event);
      
      return this.parsedData;
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
    const formData = {
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
    
    // Si nous sommes en mode démo, ajouter un marqueur
    if (this.isDemo) {
      formData.isSimulated = true;
    }
    
    return formData;
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
    
    // Injection de l'adaptateur API si nécessaire (environnement de démo)
    if ((window.location.hostname.includes('github.io') || 
         window.location.hostname === 'localhost' || 
         window.location.hostname === '127.0.0.1') && 
        !document.querySelector('script[src*="api-adapter.js"]')) {
      
      console.log("Chargement dynamique de l'adaptateur API");
      const script = document.createElement('script');
      script.src = "./static/scripts/api-adapter.js";
      document.head.appendChild(script);
      
      // Attendre le chargement de l'adaptateur avant d'initialiser le connecteur
      script.onload = function() {
        window.cvToFormConnector.init();
        setupFormListeners();
      };
    } else {
      window.cvToFormConnector.init();
      setupFormListeners();
    }
    
    function setupFormListeners() {
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
              
              // En mode démo, essayer de charger des données factices
              if (window.cvToFormConnector.isDemo) {
                console.log("Mode démo: tentative de récupération avec des données mockées");
                // Charger les données factices
                const script = document.createElement('script');
                script.src = "./static/scripts/parsed-data-example.js";
                script.onload = function() {
                  if (typeof mockParsedData !== 'undefined') {
                    mockParsedData.isSimulated = true;
                    sessionStorage.setItem('parsedCandidateData', JSON.stringify(mockParsedData));
                    
                    // Montrer une notification
                    if (window.showNotification) {
                      window.showNotification("Utilisation de données d'exemple (mode démo)", "info");
                    }
                    
                    // Rediriger après un court délai
                    setTimeout(function() {
                      window.location.href = './templates/candidate-questionnaire.html';
                    }, 1500);
                  } else {
                    window.cvToFormConnector.showError('Erreur lors du traitement du CV, données de remplacement non disponibles.');
                  }
                };
                document.head.appendChild(script);
              } else {
                window.cvToFormConnector.showError('Erreur lors du traitement du CV. Veuillez réessayer.');
              }
              
              // Cacher l'indicateur de chargement
              if (window.hideLoadingOverlay) {
                window.hideLoadingOverlay();
              }
            });
        } else {
          window.cvToFormConnector.showError('Veuillez sélectionner un fichier CV à analyser.');
        }
      });
    }
  } else {
    console.log('Page de téléchargement de CV non détectée');
  }
});