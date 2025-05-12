/**
 * API d'intégration pour le service JOB PARSER
 * Ce fichier permet de connecter l'interface utilisateur frontend au service JOB PARSER backend.
 */

// Configuration par défaut
const JOB_PARSER_CONFIG = {
    // URL de base de l'API - Choisir l'URL appropriée selon l'environnement
    // Utiliser l'URL relative pour la production, et l'URL complète pour le développement local
    apiBaseUrl: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:5000/api/job-parser'  // Développement local
        : '/api/job-parser',  // Production (URL relative)
    
    // Timeout des requêtes en millisecondes
    requestTimeout: 120000,
    
    // Intervalle de vérification du statut d'un job en millisecondes
    pollInterval: 2000,
    
    // Nombre maximum de tentatives de vérification
    maxPollAttempts: 30,
    
    // Mode debug - activé par défaut si ?debug=true est présent dans l'URL
    debug: new URLSearchParams(window.location.search).has('debug')
};

// Classe principale d'intégration avec le JOB PARSER
class JobParserAPI {
    constructor(config = {}) {
        this.config = { ...JOB_PARSER_CONFIG, ...config };
        this.log('JobParserAPI initialized with config:', this.config);
        
        // Afficher un message pour aider au débogage
        if (this.config.debug) {
            console.log('%cJobParserAPI Debug Mode activé', 'background: #7c3aed; color: white; padding: 5px; border-radius: 5px;');
            console.log(`API URL: ${this.config.apiBaseUrl}`);
        }
    }

    /**
     * Analyse une fiche de poste à partir d'un fichier
     * @param {File} file - Fichier à analyser (PDF, DOCX, TXT)
     * @param {Object} options - Options supplémentaires
     * @returns {Promise<Object>} - Résultat de l'analyse
     */
    async parseJobFile(file, options = {}) {
        this.log('Parsing job file:', file.name, 'Size:', file.size, 'Type:', file.type);
        
        try {
            // Vérification préalable du fichier
            if (!file) {
                throw new Error("Aucun fichier fourni");
            }
            
            if (file.size === 0) {
                throw new Error("Le fichier est vide");
            }
            
            // Vérification du type de fichier
            const allowedTypes = ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
            if (!allowedTypes.includes(file.type) && !file.name.match(/\.(pdf|docx?|txt)$/i)) {
                throw new Error("Format de fichier non pris en charge. Utilisez PDF, DOC, DOCX ou TXT.");
            }
            
            // Création du FormData avec le fichier
            const formData = new FormData();
            formData.append('file', file);
            
            // Ajout des options supplémentaires si nécessaire
            if (options.priority) {
                formData.append('priority', options.priority);
            }
            
            // Vérification spécifique pour les fichiers PDF
            if (file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) {
                this.log('File is a PDF, ensuring proper handling');
            }
            
            // Appel à l'API pour mettre le job dans la file d'attente
            const queueResponse = await this._sendRequest('/queue', {
                method: 'POST',
                body: formData
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
            // Vérification préalable du texte
            if (!text || text.trim().length === 0) {
                throw new Error("Le texte est vide");
            }
            
            // Créer un formData avec le texte
            const formData = new FormData();
            formData.append('text', text);
            
            // Appel à l'API pour mettre le job dans la file d'attente
            const queueResponse = await this._sendRequest('/queue', {
                method: 'POST',
                body: formData
            });
            
            this.log('Job queued:', queueResponse);
            
            // Vérification périodique du statut du job
            return await this._pollJobStatus(queueResponse.job_id, options);
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
                method: 'GET'
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
        
        // Nettoyage préalable du texte
        if (text.startsWith("%PDF")) {
            this.log('Detected PDF header in text, cleaning up');
            
            // Supprimer les lignes d'entête PDF
            const lines = text.split('\n');
            const cleanedLines = [];
            let started = false;
            
            for (const line of lines) {
                if (!started && (line.startsWith("%") || /^[^\w\s]/.test(line))) {
                    continue;
                } else {
                    started = true;
                    cleanedLines.push(line);
                }
            }
            
            text = cleanedLines.join('\n');
            this.log('Cleaned text:', text.substring(0, 100) + '...');
        }
        
        // Utiliser le parser JS côté client s'il est disponible
        if (window.JobParser && window.JobParser.parseJobDescription) {
            this.log('Using local JobParser');
            return window.JobParser.parseJobDescription(text);
        } else {
            // Analyse simplifiée si le parser n'est pas disponible
            this.log('Local JobParser not available, using simplified extraction');
            
            // Extraire le titre du poste (première ligne non vide)
            const title = text.split('\n').find(line => line.trim())?.trim() || "Non spécifié";
            
            return {
                title: title !== "Non spécifié" ? title : "%PDF-1.7", // Valeur par défaut reconnue
                company: "Non spécifié",
                location: "Non spécifié",
                skills: ["Non spécifié"],
                experience: "Non spécifié",
                responsibilities: ["Non spécifié"],
                requirements: ["Non spécifié"],
                salary: "Non spécifié",
                benefits: ["Non spécifié"]
            };
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
            this.log(`Sending request to ${url}`, options);
            
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
                    
                    // En cas d'erreur de communication, essayer encore 
                    // jusqu'à atteindre le nombre maximum de tentatives
                    if (attempts >= this.config.maxPollAttempts) {
                        reject(error);
                    } else {
                        this.log(`Communication error, retrying in ${this.config.pollInterval}ms`);
                        setTimeout(checkStatus, this.config.pollInterval);
                    }
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
            console.log('%c[JobParserAPI]', 'color: #7c3aed; font-weight: bold;', ...args);
        }
    }

    /**
     * Affiche un message d'erreur si le mode debug est activé
     * @param {...any} args - Arguments du log d'erreur
     */
    logError(...args) {
        if (this.config.debug) {
            console.error('%c[JobParserAPI ERROR]', 'color: #ef4444; font-weight: bold;', ...args);
        }
    }
}

// Exporter l'API pour l'utiliser dans d'autres fichiers
window.JobParserAPI = JobParserAPI;