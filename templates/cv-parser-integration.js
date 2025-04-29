/**
 * Module d'intégration du système de parsing de CV basé sur GPT
 * Ce script fait l'interface entre l'UI existante et le service de parsing CV
 */

// Configuration de l'URL de l'API de parsing
const CV_PARSER_API_URL = 'http://localhost:5051/api/v1';

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
      ...options
    };
    
    // Garder une référence aux fonctions originales
    this.originalHandleFile = null;
  }
  
  /**
   * Initialise l'intégration dans une page existante
   * @param {Object} pageContext - Variables et fonctions de la page hôte
   */
  init(pageContext) {
    console.log('Initialisation de l\'intégration du service de parsing CV...');
    
    // Sauvegarder la référence à handleFile pour pouvoir l'utiliser plus tard
    if (pageContext && pageContext.handleFile) {
      this.originalHandleFile = pageContext.handleFile;
      // Remplacer la fonction handleFile
      pageContext.handleFile = this.handleFile.bind(this, pageContext);
      console.log('Fonction handleFile remplacée avec succès');
    } else {
      console.warn('Fonction handleFile non trouvée dans le contexte de page, impossible de l\'intercepter');
    }
    
    // Exposer les méthodes utiles dans le contexte global
    window.CVParserIntegration = this;
  }
  
  /**
   * Gère l'envoi d'un fichier CV au service de parsing
   * @param {Object} pageContext - Contexte de la page hôte
   * @param {File} file - Fichier CV téléchargé
   */
  async handleFile(pageContext, file) {
    // Vérifications initiales et affichage des informations du fichier
    // (ce code est copié de la fonction originale pour maintenir le comportement)
    if (!this.checkFileType(file)) {
      if (pageContext.errorText && pageContext.errorMessage) {
        pageContext.errorText.textContent = 'Type de fichier non pris en charge. Veuillez charger un fichier PDF, DOC, DOCX, JPG ou PNG.';
        pageContext.errorMessage.style.display = 'block';
        setTimeout(() => {
          pageContext.errorMessage.style.display = 'none';
        }, 5000);
      }
      return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
      if (pageContext.errorText && pageContext.errorMessage) {
        pageContext.errorText.textContent = 'La taille du fichier dépasse la limite de 10MB.';
        pageContext.errorMessage.style.display = 'block';
        setTimeout(() => {
          pageContext.errorMessage.style.display = 'none';
        }, 5000);
      }
      return;
    }
    
    // Masquer message d'erreur s'il était affiché
    if (pageContext.errorMessage) {
      pageContext.errorMessage.style.display = 'none';
    }
    
    // Affichage des informations sur le fichier
    if (pageContext.fileName && pageContext.fileSize && pageContext.fileInfo) {
      pageContext.fileName.textContent = file.name;
      pageContext.fileSize.textContent = pageContext.formatFileSize ? 
        pageContext.formatFileSize(file.size) : `${(file.size / 1024).toFixed(2)} KB`;
      pageContext.fileInfo.style.display = 'flex';
    }
    
    // Afficher l'indicateur de chargement
    if (pageContext.loadingIndicator) {
      pageContext.loadingIndicator.style.display = 'flex';
    }
    
    // Mise à jour de la barre de progression
    if (pageContext.stepperProgress) {
      pageContext.stepperProgress.style.width = '33.33%';
    }
    
    // Notifier le début du parsing
    if (this.options.onParsingStart) {
      this.options.onParsingStart(file);
    }
    
    try {
      // Utiliser notre service de parsing basé sur GPT
      const formData = new FormData();
      formData.append('file', file);
      
      let responseData;
      
      try {
        // Appel différent selon que l'on utilise le mode synchrone ou asynchrone
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
          
          // Vérifier l'état du job toutes les 2 secondes
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
        
        // Traiter les données reçues pour les adapter au format attendu par la page
        const extractedData = this.processExtractedData(responseData);
        
        // Mettre à jour l'interface
        this.updateUI(pageContext, extractedData);
        
        // Notifier que le parsing est terminé
        if (this.options.onParsingComplete) {
          this.options.onParsingComplete(extractedData);
        }
      } catch (apiError) {
        console.error('Erreur lors de l\'appel au service de parsing:', apiError);
        
        // En cas d'erreur, on utilise la fonction originale comme solution de secours
        if (this.originalHandleFile) {
          console.log('Utilisation de la fonction de parsing originale comme solution de secours');
          return this.originalHandleFile(file);
        }
        
        // Notifier l'erreur
        if (this.options.onParsingError) {
          this.options.onParsingError(apiError);
        }
        
        // Afficher l'erreur
        if (pageContext.errorText && pageContext.errorMessage) {
          pageContext.errorText.textContent = `Erreur lors de l'analyse: ${apiError.message}`;
          pageContext.errorMessage.style.display = 'block';
        }
      } finally {
        // Cacher l'indicateur de chargement
        if (pageContext.loadingIndicator) {
          pageContext.loadingIndicator.style.display = 'none';
        }
      }
    } catch (error) {
      console.error('Erreur globale lors du parsing:', error);
      
      // Cacher l'indicateur de chargement
      if (pageContext.loadingIndicator) {
        pageContext.loadingIndicator.style.display = 'none';
      }
      
      // Afficher l'erreur
      if (pageContext.errorText && pageContext.errorMessage) {
        pageContext.errorText.textContent = `Erreur lors de l'analyse: ${error.message}`;
        pageContext.errorMessage.style.display = 'block';
      }
      
      // Notifier l'erreur
      if (this.options.onParsingError) {
        this.options.onParsingError(error);
      }
    }
  }
  
  /**
   * Vérifie si le type de fichier est supporté
   * @param {File} file - Fichier à vérifier
   * @returns {boolean} - true si le fichier est supporté
   */
  checkFileType(file) {
    const allowedTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'image/jpeg',
      'image/png',
      'text/plain'
    ];
    
    const fileExtension = file.name.split('.').pop().toLowerCase();
    const allowedExtensions = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'];
    
    return allowedTypes.includes(file.type) || allowedExtensions.includes(fileExtension);
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
            reject(new Error('Le traitement du CV a échoué'));
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
   * Traite les données extraites du CV pour les adapter au format attendu par l'UI
   * @param {Object} data - Données brutes du service de parsing
   * @returns {Object} - Données formatées
   */
  processExtractedData(data) {
    // Le service renvoie déjà un objet, extraire les données importantes
    const extracted = data.personal_info || {};
    const skills = data.skills || [];
    const workExperience = data.work_experience || [];
    const education = data.education || [];
    
    // Calculer l'expérience totale en années
    let totalExperience = '0';
    if (workExperience.length > 0) {
      // Méthode simple: prendre la somme des durées
      let months = 0;
      workExperience.forEach(exp => {
        const startDate = exp.start_date ? new Date(exp.start_date) : null;
        const endDate = exp.end_date ? new Date(exp.end_date) : new Date();
        
        if (startDate) {
          const diffYears = (endDate.getFullYear() - startDate.getFullYear());
          const diffMonths = endDate.getMonth() - startDate.getMonth();
          months += diffYears * 12 + diffMonths;
        }
      });
      
      totalExperience = `${Math.floor(months / 12)} ans`;
    }
    
    // Extraire le job title du dernier emploi
    const latestJob = workExperience.length > 0 ? workExperience[0] : null;
    const jobTitle = latestJob ? latestJob.title : '';
    
    // Formater pour l'UI
    return {
      name: extracted.name || 'Non détecté',
      job_title: jobTitle || 'Non détecté',
      email: extracted.email || 'Non détecté',
      phone: extracted.phone || 'Non détecté',
      skills: Array.isArray(skills) ? skills.join(', ') : skills || 'Non détecté',
      experience: totalExperience || 'Non détecté'
    };
  }
  
  /**
   * Met à jour l'interface utilisateur avec les données extraites
   * @param {Object} pageContext - Contexte de la page
   * @param {Object} data - Données extraites du CV
   */
  updateUI(pageContext, data) {
    // Mettre à jour les champs d'affichage
    if (pageContext.parsedName) {
      pageContext.parsedName.textContent = data.name;
    }
    
    if (pageContext.parsedJobTitle) {
      pageContext.parsedJobTitle.textContent = data.job_title;
    }
    
    if (pageContext.parsedEmail) {
      pageContext.parsedEmail.textContent = data.email;
    }
    
    if (pageContext.parsedPhone) {
      pageContext.parsedPhone.textContent = data.phone;
    }
    
    if (pageContext.parsedSkills) {
      pageContext.parsedSkills.textContent = data.skills;
    }
    
    if (pageContext.parsedExperience) {
      pageContext.parsedExperience.textContent = data.experience;
    }
    
    // Afficher les résultats
    if (pageContext.parsedData) {
      pageContext.parsedData.style.display = 'block';
    }
    
    if (pageContext.successMessage) {
      pageContext.successMessage.style.display = 'block';
      
      // Masquer le message de succès après 3 secondes
      setTimeout(() => {
        pageContext.successMessage.style.display = 'none';
      }, 3000);
    }
    
    // Sauvegarder les données pour le chat
    if (pageContext.documentData !== undefined) {
      pageContext.documentData = data;
    }
  }
}

// Exporter la classe d'intégration
window.CVParserIntegration = CVParserIntegration;
