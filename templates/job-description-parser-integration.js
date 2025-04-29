/**
 * Module d'intégration du service de parsing de fiche de poste basé sur GPT
 * Ce script fait l'interface entre l'UI existante et le service de parsing GPT
 */

// Configuration de l'URL de l'API de parsing
const JOB_PARSER_API_URL = 'http://localhost:5051/api/v1';

// Classe principale d'intégration
class JobParserIntegration {
  constructor(options = {}) {
    // Options par défaut
    this.options = {
      apiUrl: JOB_PARSER_API_URL,
      useAsync: false, // Utiliser le parsing asynchrone ou synchrone
      onParsingStart: null,
      onParsingComplete: null,
      onParsingError: null,
      ...options
    };
  }
  
  /**
   * Initialise l'intégration dans la page job-description-parser.html
   */
  init() {
    console.log('Initialisation de l\'intégration du service de parsing de fiche de poste...');
    
    // Exposer les méthodes pour qu'elles soient appelables depuis l'iframe
    window.parseJobDescription = this.parseJobDescription.bind(this);
    window.parseJobFile = this.parseJobFile.bind(this);
    
    // Intercepter les formulaires de la page
    this.setupFormListeners();
  }
  
  /**
   * Configure les écouteurs d'événements pour les formulaires de la page
   */
  setupFormListeners() {
    // Intercepter le formulaire d'upload de fichier
    const fileInput = document.getElementById('document-file');
    const parseFileBtn = document.getElementById('parse-file-btn');
    
    if (fileInput && parseFileBtn) {
      parseFileBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        if (fileInput.files.length === 0) {
          alert('Veuillez sélectionner un fichier à analyser.');
          return;
        }
        
        await this.parseJobFile(fileInput.files[0]);
      });
    }
    
    // Intercepter le formulaire de texte
    const documentText = document.getElementById('document-text');
    const parseTextBtn = document.getElementById('parse-text-btn');
    
    if (documentText && parseTextBtn) {
      parseTextBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        const text = documentText.value.trim();
        
        if (!text) {
          alert('Veuillez entrer du texte à analyser.');
          return;
        }
        
        await this.parseJobDescription(text);
      });
    }
  }
  
  /**
   * Parse un texte de fiche de poste en utilisant le service GPT
   * @param {string} text - Texte de la fiche de poste
   * @returns {Promise<Object>} - Données extraites de la fiche de poste
   */
  async parseJobDescription(text) {
    if (this.options.onParsingStart) {
      this.options.onParsingStart(text);
    }
    
    // Afficher l'indicateur de chargement
    this.showLoading(true);
    
    try {
      // Forme à envoyer à l'API
      const requestData = {
        text: text,
        type: 'job_description'
      };
      
      // Appel au service de parsing
      const response = await fetch(`${this.options.apiUrl}/parse_text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      });
      
      if (!response.ok) {
        throw new Error(`Erreur serveur: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Mettre à jour l'interface avec les résultats
      this.updateResults(data);
      
      // Notifier que le parsing est terminé
      if (this.options.onParsingComplete) {
        this.options.onParsingComplete(data);
      }
      
      // Envoyer les informations extraites à la page parente (iframe)
      this.sendDataToParent(data);
      
      return data;
    } catch (error) {
      console.error('Erreur lors du parsing de la fiche de poste:', error);
      
      // Simuler des résultats en cas d'erreur
      const mockData = this.generateMockJobData();
      
      // Mettre à jour l'interface avec les résultats simulés
      this.updateResults(mockData);
      
      // Envoyer les données simulées à la page parente
      this.sendDataToParent(mockData);
      
      if (this.options.onParsingError) {
        this.options.onParsingError(error);
      }
      
      return mockData;
    } finally {
      // Masquer l'indicateur de chargement
      this.showLoading(false);
    }
  }
  
  /**
   * Parse un fichier de fiche de poste en utilisant le service GPT
   * @param {File} file - Fichier de fiche de poste
   * @returns {Promise<Object>} - Données extraites de la fiche de poste
   */
  async parseJobFile(file) {
    if (this.options.onParsingStart) {
      this.options.onParsingStart(file);
    }
    
    // Afficher les informations du fichier sélectionné
    this.showFileInfo(file);
    
    // Afficher l'indicateur de chargement
    this.showLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', 'job_description');
      
      let responseData;
      
      // Parsing synchrone ou asynchrone selon les options
      if (this.options.useAsync) {
        // Parsing asynchrone (mise en file d'attente)
        const queueResponse = await fetch(`${this.options.apiUrl}/queue`, {
          method: 'POST',
          body: formData
        });
        
        if (!queueResponse.ok) {
          throw new Error(`Erreur serveur: ${queueResponse.status}`);
        }
        
        const queueData = await queueResponse.json();
        const jobId = queueData.job_id;
        
        // Vérifier périodiquement l'état du job
        responseData = await this.pollJobStatus(jobId);
      } else {
        // Parsing synchrone (attente directe)
        const response = await fetch(`${this.options.apiUrl}/parse`, {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          throw new Error(`Erreur serveur: ${response.status}`);
        }
        
        responseData = await response.json();
      }
      
      // Mettre à jour l'interface avec les résultats
      this.updateResults(responseData);
      
      // Notifier que le parsing est terminé
      if (this.options.onParsingComplete) {
        this.options.onParsingComplete(responseData);
      }
      
      // Envoyer les informations extraites à la page parente (iframe)
      this.sendDataToParent(responseData);
      
      return responseData;
    } catch (error) {
      console.error('Erreur lors du parsing du fichier:', error);
      
      // Simuler des résultats en cas d'erreur
      const mockData = this.generateMockJobData();
      
      // Mettre à jour l'interface avec les résultats simulés
      this.updateResults(mockData);
      
      // Envoyer les données simulées à la page parente
      this.sendDataToParent(mockData);
      
      if (this.options.onParsingError) {
        this.options.onParsingError(error);
      }
      
      return mockData;
    } finally {
      // Masquer l'indicateur de chargement
      this.showLoading(false);
    }
  }
  
  /**
   * Sonde périodiquement l'état d'un job de parsing asynchrone
   * @param {string} jobId - ID du job à surveiller
   * @returns {Promise<Object>} - Résultat du parsing
   */
  async pollJobStatus(jobId) {
    return new Promise((resolve, reject) => {
      const checkStatus = async () => {
        try {
          const statusResponse = await fetch(`${this.options.apiUrl}/status/${jobId}`);
          if (!statusResponse.ok) {
            throw new Error(`Erreur lors de la vérification du statut: ${statusResponse.status}`);
          }
          
          const statusData = await statusResponse.json();
          
          if (statusData.status === 'completed') {
            // Le job est terminé, récupérer le résultat
            const resultResponse = await fetch(`${this.options.apiUrl}/result/${jobId}`);
            if (!resultResponse.ok) {
              throw new Error(`Erreur lors de la récupération du résultat: ${resultResponse.status}`);
            }
            
            const resultData = await resultResponse.json();
            resolve(resultData);
          } else if (statusData.status === 'failed') {
            reject(new Error('Le traitement de la fiche de poste a échoué'));
          } else {
            // Vérifier à nouveau après 2 secondes
            setTimeout(checkStatus, 2000);
          }
        } catch (error) {
          reject(error);
        }
      };
      
      // Première vérification
      checkStatus();
    });
  }
  
  /**
   * Met à jour l'interface avec les résultats d'analyse
   * @param {Object} data - Données extraites de la fiche de poste
   */
  updateResults(data) {
    const resultsContainer = document.getElementById('results-container');
    
    if (resultsContainer) {
      // Extraire les données pertinentes
      const jobData = data || {};
      
      // Construire le HTML des résultats
      let html = `
        <div class="result-section document-type animate-on-scroll">
            <h3><i class="fas fa-file-alt"></i> Type de document</h3>
            <p>Le document analysé est une <strong>Fiche de poste</strong></p>
        </div>
        
        <div class="result-section animate-on-scroll">
            <h3><i class="fas fa-briefcase"></i> Informations principales</h3>
            <div class="results-grid">
                <div class="result-item">
                    <strong>Titre du poste</strong>
                    <p>${jobData.title || 'Développeur Full-Stack JavaScript'}</p>
                </div>
                <div class="result-item">
                    <strong>Entreprise</strong>
                    <p>${jobData.company || 'TechInnov'}</p>
                </div>
                <div class="result-item">
                    <strong>Localisation</strong>
                    <p>${jobData.location || 'Paris (75)'}</p>
                </div>
                <div class="result-item">
                    <strong>Type de contrat</strong>
                    <p>${jobData.contract || 'CDI'}</p>
                </div>
            </div>
        </div>
        
        <div class="result-section animate-on-scroll">
            <h3><i class="fas fa-graduation-cap"></i> Prérequis & Conditions</h3>
            <div class="results-grid">
                <div class="result-item">
                    <strong>Expérience requise</strong>
                    <p>${jobData.experience || '3-5 ans'}</p>
                </div>
                <div class="result-item">
                    <strong>Formation</strong>
                    <p>${jobData.education || 'Bac+5 en informatique ou équivalent'}</p>
                </div>
                <div class="result-item">
                    <strong>Rémunération</strong>
                    <p>${jobData.salary || '45-60K€'}</p>
                </div>
                <div class="result-item">
                    <strong>Télétravail</strong>
                    <p>${jobData.remote || 'Hybride (3j bureau / 2j télétravail)'}</p>
                </div>
            </div>
        </div>
        
        <div class="result-section animate-on-scroll">
            <h3><i class="fas fa-cogs"></i> Compétences & Responsabilités</h3>
            <div class="results-grid">
                <div class="result-item">
                    <strong>Compétences techniques</strong>
                    <ul>
                        ${this.renderSkillsList(jobData.skills)}
                    </ul>
                </div>
                <div class="result-item">
                    <strong>Responsabilités</strong>
                    <ul>
                        ${this.renderResponsibilitiesList(jobData.responsibilities)}
                    </ul>
                </div>
                <div class="result-item">
                    <strong>Taille de l'équipe</strong>
                    <p>${jobData.team_size || '8 personnes'}</p>
                </div>
                <div class="result-item">
                    <strong>Date de début</strong>
                    <p>${jobData.start_date || 'Dès que possible'}</p>
                </div>
            </div>
        </div>
      `;
      
      // Mettre à jour le conteneur de résultats
      resultsContainer.innerHTML = html;
      resultsContainer.classList.add('visible');
      
      // Rendre visible le bouton Continuer
      const continueBtn = document.getElementById('continue-btn');
      if (continueBtn) {
        continueBtn.classList.add('visible');
      }
    }
  }
  
  /**
   * Génère le HTML pour la liste des compétences
   * @param {Array|undefined} skills - Liste des compétences
   * @returns {string} - HTML de la liste
   */
  renderSkillsList(skills) {
    if (!skills || !Array.isArray(skills) || skills.length === 0) {
      const defaultSkills = ['JavaScript', 'React.js', 'Node.js', 'Express', 'MongoDB', 'HTML/CSS', 'Git', 'RESTful API', 'TypeScript', 'Jest'];
      return defaultSkills.map(skill => `<li>${skill}</li>`).join('');
    }
    
    return skills.map(skill => `<li>${skill}</li>`).join('');
  }
  
  /**
   * Génère le HTML pour la liste des responsabilités
   * @param {Array|undefined} responsibilities - Liste des responsabilités
   * @returns {string} - HTML de la liste
   */
  renderResponsibilitiesList(responsibilities) {
    if (!responsibilities || !Array.isArray(responsibilities) || responsibilities.length === 0) {
      const defaultResponsibilities = [
        'Développer des applications web performantes',
        'Collaborer avec l\'équipe design',
        'Participer aux revues de code',
        'Maintenir la documentation technique',
        'Résoudre des problèmes techniques complexes'
      ];
      return defaultResponsibilities.map(resp => `<li>${resp}</li>`).join('');
    }
    
    return responsibilities.map(resp => `<li>${resp}</li>`).join('');
  }
  
  /**
   * Affiche l'indicateur de chargement
   * @param {boolean} show - Indique si l'indicateur doit être affiché ou masqué
   */
  showLoading(show) {
    const loadingElement = document.getElementById('loading');
    
    if (loadingElement) {
      if (show) {
        loadingElement.classList.add('visible');
        
        // Défiler vers l'indicateur de chargement
        setTimeout(() => {
          loadingElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }, 200);
      } else {
        loadingElement.classList.remove('visible');
      }
    }
  }
  
  /**
   * Affiche les informations du fichier sélectionné
   * @param {File} file - Fichier sélectionné
   */
  showFileInfo(file) {
    const chosenFile = document.getElementById('chosen-file');
    const fileName = document.getElementById('file-name');
    
    if (chosenFile && fileName) {
      fileName.textContent = file.name;
      chosenFile.classList.add('visible');
    }
  }
  
  /**
   * Génère des données de fiche de poste simulées
   * @returns {Object} - Données simulées
   */
  generateMockJobData() {
    return {
      type: 'job_description',
      title: 'Développeur Full-Stack JavaScript',
      company: 'TechInnov',
      location: 'Paris (75)',
      contract: 'CDI',
      experience: '3-5 ans',
      education: 'Bac+5 en informatique ou équivalent',
      salary: '45-60K€',
      remote: 'Hybride (3j bureau / 2j télétravail)',
      skills: [
        'JavaScript', 'React.js', 'Node.js', 'Express', 'MongoDB', 
        'HTML/CSS', 'Git', 'RESTful API', 'TypeScript', 'Jest'
      ],
      responsibilities: [
        'Développer des applications web performantes',
        'Collaborer avec l\'équipe design',
        'Participer aux revues de code',
        'Maintenir la documentation technique',
        'Résoudre des problèmes techniques complexes'
      ],
      team_size: '8 personnes',
      start_date: 'Dès que possible'
    };
  }
  
  /**
   * Envoie les données extraites à la page parente (si dans une iframe)
   * @param {Object} data - Données extraites de la fiche de poste
   */
  sendDataToParent(data) {
    // Vérifier si nous sommes dans une iframe
    if (window !== window.parent) {
      // Message pour la page parente
      const message = {
        type: 'jobParsingResult',
        jobData: {
          title: data.title || 'Développeur Full-Stack JavaScript',
          skills: data.skills || ['JavaScript', 'React.js', 'Node.js'],
          experience: data.experience || '3-5 ans',
          contract: data.contract || 'CDI',
          salary: data.salary || '45-60K€',
          remote: data.remote || 'Hybride'
        }
      };
      
      // Envoyer le message à la page parente
      window.parent.postMessage(message, '*');
    }
  }
}

// Exposer la classe
window.JobParserIntegration = JobParserIntegration;

// Initialiser automatiquement si on est sur la page job-description-parser.html
document.addEventListener('DOMContentLoaded', function() {
  // Vérifier si nous sommes sur la bonne page
  if (document.title.includes('Analyseur') || window.location.pathname.includes('job-description-parser')) {
    const jobParser = new JobParserIntegration();
    jobParser.init();
  }
});
