/**
 * Module d'intégration du système de parsing de CV basé sur GPT
 * Ce script fait l'interface entre l'UI existante et le service de parsing CV
 * Version améliorée avec support GitHub Pages
 */

// Configuration par défaut de l'URL de l'API de parsing
const CV_PARSER_API_URL = 'http://localhost:5051/api';

// Classe principale d'intégration
class CVParserIntegration {
  constructor(options = {}) {
    // Options par défaut
    this.options = {
      apiUrl: CV_PARSER_API_URL,
      useAsync: false, // Utiliser le parsing asynchrone ou synchrone
      onParsingStart: null,
      onParsingComplete: null,
      onParsingError: null,
      forceMock: this.isGitHubPages(), // Forcer le mode mock sur GitHub Pages
      ...options
    };
    
    console.log('CVParserIntegration initialisé avec API URL:', this.options.apiUrl);
    if (this.options.forceMock) {
      console.log('Mode mock activé (GitHub Pages ou configuration forcée)');
    }
  }
  
  /**
   * Vérifie si l'application s'exécute sur GitHub Pages
   * @returns {boolean} - true si l'app est sur GitHub Pages
   */
  isGitHubPages() {
    return window.location.hostname.includes('github.io');
  }
  
  /**
   * Initialise l'intégration dans une page existante
   * @param {Object} pageContext - Variables et fonctions de la page hôte
   */
  init(pageContext) {
    console.log('Initialisation de l\'intégration du service de parsing CV...');
    
    // Faire une référence globale pour faciliter l'usage
    window.parseCV = this.parseCV.bind(this);
  }
  
  /**
   * Parse un fichier CV en utilisant le service GPT
   * @param {File} file - Fichier CV à analyser
   * @returns {Promise<Object>} - Données extraites du CV
   */
  async parseCV(file) {
    console.log('Début du parsing de CV:', file.name);
    
    if (this.options.onParsingStart) {
      this.options.onParsingStart(file);
    }
    
    // Si on est en mode mock forcé (GitHub Pages), on renvoie directement une réponse simulée
    if (this.options.forceMock) {
      console.log('Utilisation du mode mock (GitHub Pages)');
      const mockResponse = this.generateMockResponse(file);
      
      // Ajouter un délai simulé pour une meilleure expérience utilisateur
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      if (this.options.onParsingComplete) {
        this.options.onParsingComplete(mockResponse);
      }
      
      return mockResponse;
    }
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('doc_type', 'cv');
      
      let responseData;
      
      // Parsing synchrone ou asynchrone selon les options
      if (this.options.useAsync) {
        // Parsing asynchrone (mise en file d'attente)
        console.log('Utilisation du parsing asynchrone (file d\'attente)');
        const queueResponse = await fetch(`${this.options.apiUrl}/queue`, {
          method: 'POST',
          body: formData,
          headers: {
            'Access-Control-Allow-Origin': '*'
          }
        });
        
        if (!queueResponse.ok) {
          throw new Error(`Erreur serveur: ${queueResponse.status}`);
        }
        
        const queueData = await queueResponse.json();
        const jobId = queueData.job_id;
        console.log('Job de parsing créé avec ID:', jobId);
        
        // Vérifier périodiquement l'état du job
        responseData = await this.pollJobStatus(jobId);
      } else {
        // Parsing synchrone (attente directe)
        console.log('Utilisation du parsing synchrone (direct)');
        const response = await fetch(`${this.options.apiUrl}/v1/parse`, {
          method: 'POST',
          body: formData,
          headers: {
            'Access-Control-Allow-Origin': '*'
          }
        });
        
        if (!response.ok) {
          throw new Error(`Erreur serveur: ${response.status}`);
        }
        
        responseData = await response.json();
      }
      
      console.log('Parsing terminé avec succès:', responseData);
      
      // Notifier la fin du parsing
      if (this.options.onParsingComplete) {
        this.options.onParsingComplete(responseData);
      }
      
      return responseData;
    } catch (error) {
      console.error('Erreur lors du parsing CV:', error);
      
      if (this.options.onParsingError) {
        this.options.onParsingError(error);
      }
      
      // Utiliser la réponse de secours après une erreur
      console.log('Utilisation du mode mock suite à une erreur');
      const mockResponse = this.generateMockResponse(file);
      
      // Ajouter un petit délai pour une meilleure expérience utilisateur
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (this.options.onParsingComplete) {
        this.options.onParsingComplete(mockResponse);
      }
      
      return mockResponse;
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
          const statusResponse = await fetch(`${this.options.apiUrl}/result/${jobId}`);
          if (!statusResponse.ok) {
            throw new Error(`Erreur lors de la vérification du statut: ${statusResponse.status}`);
          }
          
          const statusData = await statusResponse.json();
          
          if (statusData.status === 'done') {
            // Le job est terminé
            resolve(statusData.result);
          } else if (statusData.status === 'failed') {
            reject(new Error(statusData.error || 'Le traitement du CV a échoué'));
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
   * Génère une réponse de secours avec des données pertinentes basées sur le nom du fichier
   * @param {File} file - Fichier CV
   * @returns {Object} - Données simulées
   */
  generateMockResponse(file) {
    console.log('Génération d\'une réponse mock pour:', file.name);
    
    // Extraire le nom de base du fichier (sans extension)
    const baseName = file.name.split('.')[0].replace(/[_-]/g, ' ');
    
    // Extraire le nom et des informations de carrière possibles du nom de fichier
    let name = 'Thomas Martin';
    let jobTitle = 'Développeur Full Stack';
    let skills = ['JavaScript', 'HTML', 'CSS', 'React', 'Node.js', 'Python', 'SQL', 'Git', 'Docker', 'Agile'];
    
    // Essayer d'extraire des informations du nom de fichier
    if (baseName.includes('Comptable') || baseName.includes('comptable')) {
      jobTitle = 'Comptable';
      skills = ['Comptabilité générale', 'Fiscalité', 'SAP', 'Excel', 'Sage', 'Bilan', 'Gestion de trésorerie'];
    } else if (baseName.includes('Ingénieur') || baseName.includes('ingénieur')) {
      jobTitle = 'Ingénieur Logiciel';
    } else if (baseName.includes('Chef') || baseName.includes('manager')) {
      jobTitle = 'Chef de Projet';
      skills = ['Gestion de projet', 'Agile', 'Scrum', 'Budgétisation', 'Planification', 'JIRA', 'MS Project'];
    }
    
    // Essayer d'extraire un nom du fichier
    const nameMatch = baseName.match(/CV\s+([A-Za-z\s]+)/i);
    if (nameMatch && nameMatch[1]) {
      name = nameMatch[1].trim();
    }
    
    // Générer un email basé sur le nom
    const email = name.toLowerCase().replace(/\s+/g, '.') + '@exemple.com';
    
    // Données simulées plus complètes et adaptées
    return {
      processing_time: 1.25,
      parsed_at: Date.now() / 1000,
      file_format: file.name.split('.').pop().toLowerCase(),
      model: "mock",
      data: {
        personal_info: {
          name: name,
          email: email,
          phone: '+33 6 ' + Math.floor(10000000 + Math.random() * 90000000),
          address: '123 rue de Paris, 75001 Paris',
          linkedin: 'linkedin.com/in/' + name.toLowerCase().replace(/\s+/g, ''),
        },
        skills: skills,
        work_experience: [
          {
            title: jobTitle,
            company: 'TechCorp',
            start_date: '2022-01',
            end_date: 'present',
            description: 'Développement et maintenance des solutions techniques de l\'entreprise.'
          },
          {
            title: 'Assistant ' + jobTitle,
            company: 'WebAgency',
            start_date: '2020-03',
            end_date: '2021-12',
            description: 'Support aux équipes techniques et participation aux projets clients.'
          }
        ],
        education: [
          {
            degree: 'Master en ' + (jobTitle.includes('Comptable') ? 'Comptabilité' : 'Informatique'),
            institution: 'Université de Paris',
            start_date: '2018',
            end_date: '2020'
          },
          {
            degree: 'Licence en ' + (jobTitle.includes('Comptable') ? 'Économie' : 'Informatique'),
            institution: 'Université de Lyon',
            start_date: '2015',
            end_date: '2018'
          }
        ],
        languages: [
          {
            language: 'Français',
            level: 'Natif'
          },
          {
            language: 'Anglais',
            level: 'Courant'
          }
        ]
      }
    };
  }
}

// Exporter la classe d'intégration
window.CVParserIntegration = CVParserIntegration;
