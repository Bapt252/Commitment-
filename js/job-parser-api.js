/**
 * API d'intégration pour le service JOB PARSER
 * Ce fichier permet de connecter l'interface utilisateur frontend au service JOB PARSER backend.
 * Version améliorée avec détection automatique du serveur et meilleure résilience.
 */

// Configuration par défaut
const JOB_PARSER_CONFIG = {
    // URLs de base de l'API - Avec détection automatique du serveur
    apiBaseUrls: [
        // Priorité 1: URL relative (production)
        '/api/job-parser',
        // Priorité 2: Port standard (5053)
        'http://localhost:5053/api/parse-job',
        // Priorité 3: Port alternatif (7000)
        'http://localhost:7000/api/job-parser'
    ],
    
    // URL active (sera déterminée automatiquement)
    activeApiUrl: null,
    
    // Timeout des requêtes en millisecondes
    requestTimeout: 120000,
    
    // Intervalle de vérification du statut d'un job en millisecondes
    pollInterval: 2000,
    
    // Nombre maximum de tentatives de vérification
    maxPollAttempts: 30,
    
    // Mode debug - activé par défaut si ?debug=true est présent dans l'URL
    debug: new URLSearchParams(window.location.search).has('debug'),
    
    // Nettoyage PDF - activé par défaut
    enablePDFCleaning: true
};

// Classe principale d'intégration avec le JOB PARSER
class JobParserAPI {
    constructor(config = {}) {
        this.config = { ...JOB_PARSER_CONFIG, ...config };
        this.serverDetected = false;
        
        // Initialiser le nettoyeur de PDF
        if (this.config.enablePDFCleaning && window.PDFCleaner) {
            this.pdfCleaner = new PDFCleaner({ debug: this.config.debug });
        }
        
        this.log('JobParserAPI initialized with config:', this.config);
        
        // Afficher un message pour aider au débogage
        if (this.config.debug) {
            console.log('%cJobParserAPI Debug Mode activé', 'background: #7c3aed; color: white; padding: 5px; border-radius: 5px;');
        }
        
        // Détecter automatiquement le serveur d'API disponible
        this._detectApiServer();
    }

    /**
     * Détecte automatiquement le serveur d'API disponible
     * @private
     */
    async _detectApiServer() {
        if (this.config.apiBaseUrl) {
            // Si une URL a été spécifiée explicitement dans la config, l'utiliser
            this.config.activeApiUrl = this.config.apiBaseUrl;
            this.log('Using explicitly configured API URL:', this.config.activeApiUrl);
            this.serverDetected = true;
            return;
        }
        
        // Sinon, tester les URLs par ordre de priorité
        this.log('Detecting available API server...');
        
        for (const url of this.config.apiBaseUrls) {
            try {
                const healthEndpoint = url.endsWith('/') ? url + 'health' : url + '/health';
                
                const response = await fetch(healthEndpoint, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/json'
                    },
                    // Timeout court pour la détection
                    signal: AbortSignal.timeout(3000)
                });
                
                if (response.ok) {
                    this.config.activeApiUrl = url;
                    this.log('API server detected at:', url);
                    this.serverDetected = true;
                    
                    // Déclencher un événement personnalisé pour informer l'application
                    const event = new CustomEvent('jobParserApiReady', { detail: { url } });
                    window.dispatchEvent(event);
                    
                    return;
                }
            } catch (error) {
                // Continuer avec l'URL suivante
                console.warn(`API server not available at ${url}:`, error.message);
            }
        }
        
        // Si aucun serveur n'a été détecté, utiliser l'URL par défaut
        this.config.activeApiUrl = this.config.apiBaseUrls[0];
        this.log('No API server detected, using default URL:', this.config.activeApiUrl);
        
        // Déclencher un événement d'erreur
        const event = new CustomEvent('jobParserApiError', { 
            detail: { error: 'No API server detected' } 
        });
        window.dispatchEvent(event);
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
            
            // Attendre que la détection du serveur soit terminée
            if (!this.serverDetected) {
                await this._waitForServerDetection();
            }
            
            // Si c'est un PDF, et que le nettoyage PDF est activé, pré-traiter le fichier
            if ((file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) && 
                this.config.enablePDFCleaning && this.pdfCleaner) {
                
                this.log('File is a PDF, pre-processing for better extraction');
                
                // Pour les fichiers PDF, nous pouvons soit:
                // 1. Les envoyer directement au serveur (qui a maintenant un meilleur extracteur PDF)
                // 2. Les lire localement, nettoyer le texte, puis envoyer le texte nettoyé
                
                // Option 1: Envoyer directement au serveur (plus rapide)
                // Création du FormData avec le fichier
                const formData = new FormData();
                formData.append('file', file);
                
                // Ajout de l'option force_refresh
                formData.append('force_refresh', options.forceRefresh || false);
                
                // Ajout des options supplémentaires si nécessaire
                if (options.priority) {
                    formData.append('priority', options.priority);
                }
                
                // Déterminer si l'API utilise un système de file d'attente ou une API directe
                try {
                    if (this.config.activeApiUrl.includes('/job-parser')) {
                        // Système de file d'attente
                        const queueResponse = await this._sendRequest('/queue', {
                            method: 'POST',
                            body: formData
                        });
                        
                        this.log('Job queued:', queueResponse);
                        
                        // Vérification périodique du statut du job
                        return await this._pollJobStatus(queueResponse.job_id, options);
                    } else {
                        // API directe
                        const parseResponse = await this._sendDirectRequest('', {
                            method: 'POST',
                            body: formData
                        });
                        
                        this.log('Direct parsing completed');
                        return parseResponse;
                    }
                } catch (apiError) {
                    // En cas d'erreur avec l'API, essayer l'option 2 (lecture et nettoyage local)
                    this.log('API error, falling back to local processing:', apiError.message);
                    
                    // Lire le fichier comme texte
                    const text = await this._readFileAsText(file);
                    
                    // Nettoyer le texte
                    const cleanedText = this.pdfCleaner.preprocessJobDescription(text);
                    
                    // Analyser le texte nettoyé
                    return await this.parseJobText(cleanedText, { ...options, isPDFText: true });
                }
            } else {
                // Pour les autres formats, procéder normalement
                
                // Création du FormData avec le fichier
                const formData = new FormData();
                formData.append('file', file);
                
                // Ajout de l'option force_refresh
                formData.append('force_refresh', options.forceRefresh || false);
                
                // Ajout des options supplémentaires si nécessaire
                if (options.priority) {
                    formData.append('priority', options.priority);
                }
                
                // Déterminer si l'API utilise un système de file d'attente ou une API directe
                if (this.config.activeApiUrl.includes('/job-parser')) {
                    // Système de file d'attente
                    const queueResponse = await this._sendRequest('/queue', {
                        method: 'POST',
                        body: formData
                    });
                    
                    this.log('Job queued:', queueResponse);
                    
                    // Vérification périodique du statut du job
                    return await this._pollJobStatus(queueResponse.job_id, options);
                } else {
                    // API directe
                    const parseResponse = await this._sendDirectRequest('', {
                        method: 'POST',
                        body: formData
                    });
                    
                    this.log('Direct parsing completed');
                    return parseResponse;
                }
            }
        } catch (error) {
            this.logError('Error parsing job file:', error);
            
            // En cas d'erreur, utiliser l'analyse locale comme fallback
            if (options.useFallback !== false) {
                this.log('Using local fallback analysis');
                const text = await this._readFileAsText(file);
                
                // Nettoyer le texte si c'est un PDF
                let cleanedText = text;
                if ((file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) && 
                    this.config.enablePDFCleaning && this.pdfCleaner) {
                    cleanedText = this.pdfCleaner.preprocessJobDescription(text);
                }
                
                return this.analyzeJobLocally(cleanedText);
            }
            
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
            
            // Nettoyer le texte s'il semble contenir des artefacts PDF
            if (this.config.enablePDFCleaning && this.pdfCleaner && 
                (options.isPDFText || this.pdfCleaner.hasPDFArtifacts(text))) {
                this.log('PDF artifacts detected in text, cleaning...');
                text = this.pdfCleaner.preprocessJobDescription(text);
            }
            
            // Attendre que la détection du serveur soit terminée
            if (!this.serverDetected) {
                await this._waitForServerDetection();
            }
            
            // Créer un formData avec le texte
            const formData = new FormData();
            formData.append('text', text);
            
            // Ajout de l'option force_refresh
            formData.append('force_refresh', options.forceRefresh || false);
            
            // Déterminer si l'API utilise un système de file d'attente ou une API directe
            if (this.config.activeApiUrl.includes('/job-parser')) {
                // Système de file d'attente
                const queueResponse = await this._sendRequest('/queue', {
                    method: 'POST',
                    body: formData
                });
                
                this.log('Job queued:', queueResponse);
                
                // Vérification périodique du statut du job
                return await this._pollJobStatus(queueResponse.job_id, options);
            } else {
                // API directe
                const parseResponse = await this._sendDirectRequest('/text', {
                    method: 'POST',
                    body: formData
                });
                
                this.log('Direct parsing completed');
                return parseResponse;
            }
        } catch (error) {
            this.logError('Error parsing job text:', error);
            
            // En cas d'erreur, utiliser l'analyse locale comme fallback
            if (options.useFallback !== false) {
                this.log('Using local fallback analysis');
                return this.analyzeJobLocally(text);
            }
            
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
        if (this.config.enablePDFCleaning && this.pdfCleaner && this.pdfCleaner.hasPDFArtifacts(text)) {
            this.log('PDF artifacts detected, cleaning before local analysis');
            text = this.pdfCleaner.preprocessJobDescription(text);
        }
        
        // Utiliser le parser JS côté client s'il est disponible
        if (window.JobParser && window.JobParser.parseJobDescription) {
            this.log('Using local JobParser');
            return window.JobParser.parseJobDescription(text);
        } else {
            // Analyse simplifiée si le parser n'est pas disponible
            this.log('Local JobParser not available, using enhanced extraction');
            
            // Extraire le titre du poste (première ligne non vide)
            const lines = text.split('\n').filter(line => line.trim());
            const title = lines.length > 0 ? lines[0].trim() : "Non spécifié";
            
            // Extraire l'entreprise (recherche de mots clés)
            let company = "Non spécifié";
            const companyKeywords = ["entreprise:", "société:", "company:", "chez ", "at "];
            for (const line of lines) {
                for (const keyword of companyKeywords) {
                    if (line.toLowerCase().includes(keyword)) {
                        company = line.split(keyword)[1]?.trim() || company;
                        break;
                    }
                }
            }
            
            // Extraire le lieu (recherche de mots clés)
            let location = "Non spécifié";
            const locationKeywords = ["lieu:", "location:", "à ", "in ", "ville:", "site:"];
            for (const line of lines) {
                for (const keyword of locationKeywords) {
                    if (line.toLowerCase().includes(keyword)) {
                        location = line.split(keyword)[1]?.trim() || location;
                        break;
                    }
                }
            }
            
            // Extraire les compétences (recherche de mots clés)
            const skills = [];
            const skillsKeywords = ["compétences", "skills", "requises", "required", "maîtrise", "connaissance"];
            let skillsFound = false;
            
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i].toLowerCase();
                
                if (!skillsFound && skillsKeywords.some(keyword => line.includes(keyword))) {
                    skillsFound = true;
                    continue;
                }
                
                if (skillsFound) {
                    if (line.match(/^\s*[-•*]\s+/) || line.trim().length < 50) {
                        const skill = line.replace(/^\s*[-•*]\s+/, '').trim();
                        if (skill && !skill.includes(":") && skill.length > 3 && skill.length < 50) {
                            skills.push(skill);
                        }
                    }
                    
                    // Arrêter après un certain nombre de compétences ou une ligne vide
                    if (skills.length >= 5 || line.trim() === "") {
                        break;
                    }
                }
            }
            
            return {
                title: title,
                company: company,
                location: location,
                contract_type: this._extractContractType(text),
                required_skills: skills.length > 0 ? skills : ["Non spécifié"],
                preferred_skills: [],
                responsibilities: this._extractResponsibilities(text),
                requirements: [],
                benefits: this._extractBenefits(text),
                salary_range: this._extractSalary(text),
                remote_policy: this._extractRemotePolicy(text)
            };
        }
    }

    // Méthodes d'extraction améliorées
    
    /**
     * Extrait le type de contrat du texte
     * @param {string} text - Texte à analyser
     * @returns {string} - Type de contrat
     * @private
     */
    _extractContractType(text) {
        const contractTypes = {
            "cdi": "CDI",
            "contrat à durée indéterminée": "CDI",
            "cdd": "CDD",
            "contrat à durée déterminée": "CDD",
            "stage": "Stage",
            "internship": "Stage",
            "freelance": "Freelance",
            "indépendant": "Freelance",
            "alternance": "Alternance",
            "apprentissage": "Alternance",
            "temps partiel": "Temps partiel",
            "part-time": "Temps partiel",
            "temps plein": "Temps plein",
            "full-time": "Temps plein"
        };
        
        const textLower = text.toLowerCase();
        
        for (const [keyword, contractType] of Object.entries(contractTypes)) {
            if (textLower.includes(keyword)) {
                return contractType;
            }
        }
        
        return "Non spécifié";
    }
    
    /**
     * Extrait les responsabilités du texte
     * @param {string} text - Texte à analyser
     * @returns {Array<string>} - Liste des responsabilités
     * @private
     */
    _extractResponsibilities(text) {
        const lines = text.split('\n');
        const responsibilities = [];
        
        // Chercher les sections de responsabilités/missions
        const keywords = ["responsabilités", "missions", "tâches", "rôle", "vous serez chargé"];
        let inResponsibilitiesSection = false;
        let sectionEndCounter = 0;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].toLowerCase();
            
            // Détecter le début d'une section de responsabilités
            if (!inResponsibilitiesSection) {
                if (keywords.some(keyword => line.includes(keyword))) {
                    inResponsibilitiesSection = true;
                    continue;
                }
            } else {
                // Dans une section de responsabilités
                const trimmedLine = lines[i].trim();
                
                // Détecter les points de liste
                if (trimmedLine.match(/^\s*[-•*]\s+/) || trimmedLine.match(/^\s*\d+\.\s+/)) {
                    const responsibility = trimmedLine.replace(/^\s*[-•*\d\.]\s+/, '').trim();
                    
                    if (responsibility && responsibility.length > 10) {
                        responsibilities.push(responsibility);
                        sectionEndCounter = 0;
                    }
                } else if (trimmedLine === "") {
                    // Compter les lignes vides pour détecter la fin de la section
                    sectionEndCounter++;
                    
                    if (sectionEndCounter >= 2) {
                        inResponsibilitiesSection = false;
                    }
                } else if (trimmedLine.length > 10 && !trimmedLine.includes(":")) {
                    // Ligne de texte qui pourrait être une responsabilité
                    responsibilities.push(trimmedLine);
                    sectionEndCounter = 0;
                }
                
                // Détecter une nouvelle section
                if (line.match(/^[a-z\s]{2,25}:\s*$/) || line.match(/^[A-Z\s]{2,25}$/) || line.match(/^[A-Z][a-z\s]{2,25}:/)) {
                    inResponsibilitiesSection = false;
                }
                
                // Limiter le nombre de responsabilités
                if (responsibilities.length >= 5) {
                    break;
                }
            }
        }
        
        return responsibilities.length > 0 ? responsibilities : ["Non spécifié"];
    }
    
    /**
     * Extrait les avantages du texte
     * @param {string} text - Texte à analyser
     * @returns {Array<string>} - Liste des avantages
     * @private
     */
    _extractBenefits(text) {
        const lines = text.split('\n');
        const benefits = [];
        
        // Chercher les sections d'avantages
        const keywords = ["avantages", "benefits", "nous offrons", "we offer", "package"];
        let inBenefitsSection = false;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].toLowerCase();
            
            // Détecter le début d'une section d'avantages
            if (!inBenefitsSection) {
                if (keywords.some(keyword => line.includes(keyword))) {
                    inBenefitsSection = true;
                    continue;
                }
            } else {
                // Dans une section d'avantages
                const trimmedLine = lines[i].trim();
                
                // Détecter les points de liste
                if (trimmedLine.match(/^\s*[-•*]\s+/) || trimmedLine.match(/^\s*\d+\.\s+/)) {
                    const benefit = trimmedLine.replace(/^\s*[-•*\d\.]\s+/, '').trim();
                    
                    if (benefit && benefit.length > 5 && benefit.length < 100) {
                        benefits.push(benefit);
                    }
                } else if (trimmedLine === "") {
                    // Une ligne vide peut indiquer la fin de la section
                    inBenefitsSection = false;
                }
                
                // Détecter une nouvelle section
                if (line.match(/^[a-z\s]{2,25}:\s*$/) || line.match(/^[A-Z\s]{2,25}$/)) {
                    inBenefitsSection = false;
                }
                
                // Limiter le nombre d'avantages
                if (benefits.length >= 5) {
                    break;
                }
            }
        }
        
        return benefits.length > 0 ? benefits : ["Non spécifié"];
    }
    
    /**
     * Extrait le salaire du texte
     * @param {string} text - Texte à analyser
     * @returns {string} - Salaire
     * @private
     */
    _extractSalary(text) {
        const textLower = text.toLowerCase();
        
        // Chercher des motifs de salaire courants
        const salaryRegexes = [
            /salaire\s*:\s*([^\.]+)/i,
            /rémunération\s*:\s*([^\.]+)/i,
            /package\s*:\s*([^\.]+)/i,
            /[\d]{2,3}[\s]*[kK€]\s*[\-à]\s*[\d]{2,3}[\s]*[kK€]/,
            /[\d]{2,3}[\s]*000[\s]*€\s*[\-à]\s*[\d]{2,3}[\s]*000[\s]*€/,
            /entre\s+[\d]+[\s]*[kK€][\s]*et[\s]*[\d]+[\s]*[kK€]/i
        ];
        
        for (const regex of salaryRegexes) {
            const match = textLower.match(regex);
            if (match) {
                return match[0].trim();
            }
        }
        
        return "Non spécifié";
    }
    
    /**
     * Extrait la politique de télétravail du texte
     * @param {string} text - Texte à analyser
     * @returns {string} - Politique de télétravail
     * @private
     */
    _extractRemotePolicy(text) {
        const textLower = text.toLowerCase();
        
        if (textLower.includes("100% télétravail") || textLower.includes("full remote")) {
            return "100% télétravail";
        } else if (textLower.includes("télétravail partiel") || textLower.includes("partial remote")) {
            return "Télétravail partiel";
        } else if (textLower.match(/télétravail[\s:]+(\d+)[\s]*jour/)) {
            const match = textLower.match(/télétravail[\s:]+(\d+)[\s]*jour/);
            return `Télétravail ${match[1]} jours par semaine`;
        } else if (textLower.includes("télétravail") || textLower.includes("remote")) {
            return "Télétravail possible";
        } else if (textLower.includes("sur site") || textLower.includes("présentiel")) {
            return "Travail sur site";
        }
        
        return "Non spécifié";
    }

    // Méthodes privées
    
    /**
     * Attend que la détection du serveur soit terminée
     * @returns {Promise<void>}
     * @private
     */
    _waitForServerDetection() {
        return new Promise((resolve) => {
            if (this.serverDetected) {
                resolve();
                return;
            }
            
            const checkInterval = setInterval(() => {
                if (this.serverDetected) {
                    clearInterval(checkInterval);
                    resolve();
                }
            }, 100);
            
            // Timeout après 5 secondes
            setTimeout(() => {
                clearInterval(checkInterval);
                this.log('Server detection timed out, using default URL');
                this.config.activeApiUrl = this.config.apiBaseUrls[0];
                this.serverDetected = true;
                resolve();
            }, 5000);
        });
    }

    /**
     * Lit un fichier sous forme de texte
     * @param {File} file - Fichier à lire
     * @returns {Promise<string>} - Contenu du fichier
     * @private
     */
    _readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = () => reject(new Error('Erreur lors de la lecture du fichier'));
            reader.readAsText(file);
        });
    }

    /**
     * Envoie une requête à l'API (avec gestion de file d'attente)
     * @param {string} endpoint - Point d'entrée de l'API
     * @param {Object} options - Options de la requête
     * @returns {Promise<Object>} - Réponse de l'API
     * @private
     */
    async _sendRequest(endpoint, options = {}) {
        const url = this.config.activeApiUrl + endpoint;
        
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
     * Envoie une requête directe à l'API (sans file d'attente)
     * @param {string} endpoint - Point d'entrée de l'API
     * @param {Object} options - Options de la requête
     * @returns {Promise<Object>} - Réponse de l'API
     * @private
     */
    async _sendDirectRequest(endpoint, options = {}) {
        const url = this.config.activeApiUrl + endpoint;
        
        // Création du contrôleur d'abandon pour le timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.requestTimeout);
        
        try {
            this.log(`Sending direct request to ${url}`, options);
            
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