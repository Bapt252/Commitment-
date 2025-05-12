/**
 * API d'intégration pour le service JOB PARSER
 * Ce fichier permet de connecter l'interface utilisateur frontend au service JOB PARSER backend.
 */

// Configuration par défaut
const JOB_PARSER_CONFIG = {
    // URL de base de l'API (à modifier selon l'environnement)
    apiBaseUrl: '/api/job-parser',
    
    // Timeout des requêtes en millisecondes
    requestTimeout: 60000,
    
    // Intervalle de vérification du statut d'un job en millisecondes
    pollInterval: 2000,
    
    // Nombre maximum de tentatives de vérification
    maxPollAttempts: 30,
    
    // Mode debug
    debug: false
};

// Classe principale d'intégration avec le JOB PARSER
class JobParserAPI {
    constructor(config = {}) {
        this.config = { ...JOB_PARSER_CONFIG, ...config };
        this.log('JobParserAPI initialized with config:', this.config);
    }

    /**
     * Analyse une fiche de poste à partir d'un fichier
     * @param {File} file - Fichier à analyser (PDF, DOCX, TXT)
     * @param {Object} options - Options supplémentaires
     * @returns {Promise<Object>} - Résultat de l'analyse
     */
    async parseJobFile(file, options = {}) {
        this.log('Parsing job file:', file.name);
        
        try {
            // Création du FormData avec le fichier
            const formData = new FormData();
            formData.append('file', file);
            
            // Ajout des options supplémentaires si nécessaire
            if (options.priority) {
                formData.append('priority', options.priority);
            }
            
            // Appel à l'API pour mettre le job dans la file d'attente
            const queueResponse = await this._sendRequest('/queue', {
                method: 'POST',
                body: formData,
                headers: options.apiKey ? { 'X-API-Key': options.apiKey } : undefined
            });
            
            this.log('Job queued:', queueResponse);
            
            // Vérification périodique du statut du job
            return await this._pollJobStatus(queueResponse.job_id, options);
        } catch (error) {
            this.logError('Error parsing job file:', error);
            throw error;
        }
    }

    /**
     * Analyse une fiche de poste à partir d'un texte
     * @param {string} text - Texte de la fiche de poste
     * @param {Object} options - Options supplémentaires
     * @returns {Promise<Object>} - Résultat de l'analyse
     */
    async parseJobText(text, options = {}) {
        this.log('Parsing job text, length:', text.length);
        
        try {
            // Créer un fichier temporaire à partir du texte
            const file = new File([text], 'job_description.txt', { type: 'text/plain' });
            
            // Utiliser la méthode parseJobFile
            return await this.parseJobFile(file, options);
        } catch (error) {
            this.logError('Error parsing job text:', error);
            throw error;
        }
    }

    /**
     * Obtenir le résultat d'un job d'analyse déjà soumis
     * @param {string} jobId - Identifiant du job
     * @param {Object} options - Options supplémentaires
     * @returns {Promise<Object>} - Résultat de l'analyse
     */
    async getJobResult(jobId, options = {}) {
        this.log('Getting job result for ID:', jobId);
        
        try {
            // Appel à l'API pour récupérer le résultat
            const response = await this._sendRequest(`/result/${jobId}`, {
                method: 'GET',
                headers: options.apiKey ? { 'X-API-Key': options.apiKey } : undefined
            });
            
            this.log('Job result received:', response);
            return response;
        } catch (error) {
            this.logError('Error getting job result:', error);
            throw error;
        }
    }

    /**
     * Analyse le manuel d'une fiche de poste côté client (fallback)
     * @param {string} text - Texte de la fiche de poste
     * @returns {Object} - Résultat de l'analyse
     */
    analyzeJobLocally(text) {
        this.log('Analyzing job locally (fallback)');
        
        // Utiliser le parser JS côté client s'il est disponible
        if (window.JobParser && window.JobParser.parseJobDescription) {
            return window.JobParser.parseJobDescription(text);
        } else {
            throw new Error('Local JobParser not available');
        }
    }

    // Méthodes privées
    
    /**
     * Envoie une requête à l'API
     * @param {string} endpoint - Point d'entrée de l'API
     * @param {Object} options - Options de la requête
     * @returns {Promise<Object>} - Réponse de l'API
     * @private
     */
    async _sendRequest(endpoint, options = {}) {
        const url = this.config.apiBaseUrl + endpoint;
        
        // Création du contrôleur d'abandon pour le timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.requestTimeout);
        
        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP error ${response.status}: ${errorText}`);
            }
            
            return await response.json();
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${this.config.requestTimeout}ms`);
            }
            throw error;
        }
    }

    /**
     * Vérifie périodiquement le statut d'un job
     * @param {string} jobId - Identifiant du job
     * @param {Object} options - Options supplémentaires
     * @returns {Promise<Object>} - Résultat de l'analyse
     * @private
     */
    async _pollJobStatus(jobId, options = {}) {
        let attempts = 0;
        
        return new Promise((resolve, reject) => {
            const checkStatus = async () => {
                try {
                    attempts++;
                    
                    const result = await this.getJobResult(jobId, options);
                    
                    if (result.status === 'done') {
                        // Job terminé avec succès
                        this.log(`Job completed successfully after ${attempts} attempts`);
                        resolve(result.result);
                    } else if (result.status === 'failed') {
                        // Job en échec
                        this.logError(`Job failed: ${result.error}`);
                        reject(new Error(`Job parsing failed: ${result.error}`));
                    } else if (attempts >= this.config.maxPollAttempts) {
                        // Nombre maximum de tentatives atteint
                        this.logError(`Maximum polling attempts (${this.config.maxPollAttempts}) reached`);
                        reject(new Error(`Job parsing timed out after ${attempts} attempts`));
                    } else {
                        // Job en attente ou en cours, nouvelle vérification après l'intervalle
                        this.log(`Job status: ${result.status}, polling again in ${this.config.pollInterval}ms (attempt ${attempts}/${this.config.maxPollAttempts})`);
                        setTimeout(checkStatus, this.config.pollInterval);
                    }
                } catch (error) {
                    this.logError('Error polling job status:', error);
                    reject(error);
                }
            };
            
            // Première vérification
            checkStatus();
        });
    }

    /**
     * Affiche un message de log si le mode debug est activé
     * @param {...any} args - Arguments du log
     */
    log(...args) {
        if (this.config.debug) {
            console.log('[JobParserAPI]', ...args);
        }
    }

    /**
     * Affiche un message d'erreur si le mode debug est activé
     * @param {...any} args - Arguments du log d'erreur
     */
    logError(...args) {
        if (this.config.debug) {
            console.error('[JobParserAPI]', ...args);
        }
    }
}

// Exporter l'API pour l'utiliser dans d'autres fichiers
window.JobParserAPI = JobParserAPI;