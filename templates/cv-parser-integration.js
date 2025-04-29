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
    if (this.options.onParsingStart) {
      this.options.onParsingStart(file);
    }
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
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
      
      throw error;
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
}

// Exporter la classe d'intégration
window.CVParserIntegration = CVParserIntegration;
