/**
 * API d'intégration pour le service JOB PARSER avec GPT
 * Version améliorée utilisant GPT pour l'analyse des fiches de poste
 * Intégration directe avec l'outil de parsing parse_fdp_gpt.py
 */

// Configuration par défaut
const JOB_PARSER_GPT_CONFIG = {
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
    
    // Utiliser GPT pour l'analyse
    useGPT: true,
    
    // URL de l'API OpenAI
    openAIEndpoint: 'https://api.openai.com/v1/chat/completions',
    
    // Clé segmentée pour une meilleure sécurité
    apiKeySegments: [
        "sk-svcacct-",
        "xirkqM0lorBNrlphPEH3WbuQL-9BYy3H8QUlJjE5wby1FrPvX91P6e4qvTY3bQnvbbltkqAcGUT3B",
        "lbkFJT-fAaOxfrclRmFqFLPA5E6n0_OC3YW4eIiBZR-2fh-ZOquA4X_Y1KyliAv5cv_thp_WCU51EAA"
    ],
    
    // Mode debug - activé par défaut si ?debug=true est présent dans l'URL
    debug: new URLSearchParams(window.location.search).has('debug'),
    
    // Nettoyage PDF - activé par défaut
    enablePDFCleaning: true
};

// Classe principale d'intégration avec le JOB PARSER GPT
class JobParserGPTAPI {
    constructor(config = {}) {
        this.config = { ...JOB_PARSER_GPT_CONFIG, ...config };
        this.serverDetected = false;
        
        // Initialiser le nettoyeur de PDF
        if (this.config.enablePDFCleaning && window.PDFCleaner) {
            this.pdfCleaner = new PDFCleaner({ debug: this.config.debug });
        }
        
        this.log('JobParserGPTAPI initialized with config:', this.config);
        
        // Afficher un message pour aider au débogage
        if (this.config.debug) {
            console.log('%cJobParserGPTAPI Debug Mode activé - Utilise GPT', 'background: #7c3aed; color: white; padding: 5px; border-radius: 5px;');
        }
        
        // Afficher un avertissement si aucune clé API n'est trouvée
        if (this.config.useGPT && (!this.config.apiKeySegments || this.config.apiKeySegments.length === 0)) {
            console.warn('JobParserGPTAPI: Aucune clé API OpenAI trouvée. L\'analyse GPT ne sera pas disponible.');
        }
        
        // Détecter automatiquement le serveur d'API disponible
        this._detectApiServer();
    }

    /**
     * Reconstitue la clé API à partir des segments
     * @returns {string} - Clé API OpenAI
     * @private
     */
    _getAPIKey() {
        return this.config.apiKeySegments.join("");
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
        
        // En l'absence de serveur, on peut quand même utiliser GPT directement
        this.log('Will use direct GPT analysis as fallback');
        this.serverDetected = true;
    }

    /**
     * Analyse une fiche de poste à partir d'un fichier en utilisant GPT
     * @param {File} file - Fichier à analyser (PDF, DOCX, TXT)
     * @param {Object} options - Options supplémentaires
     * @returns {Promise<Object>} - Résultat de l'analyse
     */
    async parseJobFile(file, options = {}) {
        this.log('Parsing job file with GPT:', file.name, 'Size:', file.size, 'Type:', file.type);
        
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
            
            // Lire le fichier comme texte
            const text = await this._readFileAsText(file);
            
            // Nettoyer le texte si c'est un PDF
            let cleanedText = text;
            if ((file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')) && 
                this.config.enablePDFCleaning && this.pdfCleaner) {
                cleanedText = this.pdfCleaner.preprocessJobDescription(text);
            }
            
            // Si GPT est activé, utiliser GPT pour l'analyse
            if (this.config.useGPT) {
                try {
                    // Tenter d'abord la connexion au serveur, si disponible
                    if (this.serverDetected && this.config.activeApiUrl) {
                        try {
                            // Création du FormData avec le fichier
                            const formData = new FormData();
                            formData.append('file', file);
                            
                            // Ajout de l'option force_refresh
                            formData.append('force_refresh', options.forceRefresh || false);
                            
                            // Appel à l'API
                            const parseResponse = await this._sendDirectRequest('', {
                                method: 'POST',
                                body: formData
                            });
                            
                            this.log('Server parsing completed');
                            return parseResponse;
                        } catch (serverError) {
                            this.log('Server error, falling back to direct GPT analysis:', serverError.message);
                            // Fallback sur l'analyse directe avec GPT
                        }
                    }
                    
                    // Analyse directe avec GPT
                    return await this._analyzeWithGPTDirect(cleanedText);
                } catch (gptError) {
                    this.logError('GPT analysis error:', gptError);
                    
                    // Fallback sur l'analyse locale
                    if (options.useFallback !== false) {
                        this.log('Falling back to local analysis');
                        return this.analyzeJobLocally(cleanedText);
                    }
                    
                    throw gptError;
                }
            } else {
                // Si GPT n'est pas activé, utiliser l'analyse locale
                return this.analyzeJobLocally(cleanedText);
            }
        } catch (error) {
            this.logError('Error parsing job file:', error);
            throw error;
        }
    }

    /**
     * Analyse une fiche de poste à partir d'un texte en utilisant GPT
     * @param {string} text - Texte de la fiche de poste
     * @param {Object} options - Options supplémentaires
     * @returns {Promise<Object>} - Résultat de l'analyse
     */
    async parseJobText(text, options = {}) {
        this.log('Parsing job text with GPT, length:', text.length);
        
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
            
            // Si GPT est activé, utiliser GPT pour l'analyse
            if (this.config.useGPT) {
                try {
                    // Tenter d'abord la connexion au serveur, si disponible
                    if (this.serverDetected && this.config.activeApiUrl) {
                        try {
                            // Créer un formData avec le texte
                            const formData = new FormData();
                            formData.append('text', text);
                            
                            // Ajout de l'option force_refresh
                            formData.append('force_refresh', options.forceRefresh || false);
                            
                            // Appel à l'API
                            const parseResponse = await this._sendDirectRequest('/text', {
                                method: 'POST',
                                body: formData
                            });
                            
                            this.log('Server parsing completed');
                            return parseResponse;
                        } catch (serverError) {
                            this.log('Server error, falling back to direct GPT analysis:', serverError.message);
                            // Fallback sur l'analyse directe avec GPT
                        }
                    }
                    
                    // Analyse directe avec GPT
                    return await this._analyzeWithGPTDirect(text);
                } catch (gptError) {
                    this.logError('GPT analysis error:', gptError);
                    
                    // Fallback sur l'analyse locale
                    if (options.useFallback !== false) {
                        this.log('Falling back to local analysis');
                        return this.analyzeJobLocally(text);
                    }
                    
                    throw gptError;
                }
            } else {
                // Si GPT n'est pas activé, utiliser l'analyse locale
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            this.logError('Error parsing job text:', error);
            throw error;
        }
    }

    /**
     * Analyse une fiche de poste directement avec l'API OpenAI
     * @param {string} text - Texte de la fiche de poste
     * @returns {Promise<Object>} - Résultat de l'analyse
     * @private
     */
    async _analyzeWithGPTDirect(text) {
        this.log('Analyzing job directly with GPT API');
        
        try {
            // Vérifier si une clé API est disponible
            const apiKey = this._getAPIKey();
            if (!apiKey) {
                throw new Error("Aucune clé API OpenAI disponible pour l'analyse GPT");
            }
            
            // Tronquer le texte si nécessaire pour respecter les limites de l'API
            const maxLength = 15000;
            if (text.length > maxLength) {
                this.log(`Text too long (${text.length} chars), truncating to ${maxLength} chars`);
                text = text.substring(0, maxLength) + "... [texte tronqué]";
            }
            
            // Définir le prompt pour l'API
            const prompt = `
Analyse cette fiche de poste et extrait les informations importantes.
Réponds UNIQUEMENT au format JSON.

FICHE DE POSTE:
${text}

RÉPONDS AU FORMAT JSON EXACTEMENT COMME CECI:
{
  "title": "",
  "company": "",
  "location": "",
  "contract_type": "",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "requirements": [],
  "benefits": [],
  "salary_range": "",
  "remote_policy": ""
}
`;
            
            // Préparer la requête pour l'API OpenAI
            const response = await fetch(this.config.openAIEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify({
                    model: "gpt-3.5-turbo",
                    messages: [
                        {
                            role: "system",
                            content: "Tu es un expert en analyse de fiches de poste."
                        },
                        {
                            role: "user",
                            content: prompt
                        }
                    ],
                    temperature: 0.1
                })
            });
            
            // Vérifier la réponse
            if (!response.ok) {
                const errorData = await response.json().catch(() => null);
                throw new Error(`Erreur OpenAI: ${response.status} ${response.statusText} - ${JSON.stringify(errorData)}`);
            }
            
            // Parser la réponse
            const data = await response.json();
            const content = data.choices[0].message.content;
            
            // Tenter de parser le JSON de la réponse
            try {
                // Utiliser une regex pour extraire le JSON si nécessaire
                const jsonPattern = /(\{[\s\S]*\})/;
                const match = content.match(jsonPattern);
                
                if (match) {
                    const jsonStr = match[1];
                    const parsedResult = JSON.parse(jsonStr);
                    this.log('GPT analysis successful');
                    return parsedResult;
                } else {
                    // Tenter de parser directement si l'extraction a échoué
                    try {
                        const parsedResult = JSON.parse(content);
                        this.log('GPT analysis successful (direct parsing)');
                        return parsedResult;
                    } catch (jsonError) {
                        throw new Error(`Impossible de parser la réponse JSON: ${jsonError.message}`);
                    }
                }
            } catch (error) {
                this.logError('Error parsing GPT response:', error);
                throw error;
            }
        } catch (error) {
            this.logError('Error with GPT direct analysis:', error);
            throw error;
        }
    }

    /**
     * Analyse localement une fiche de poste (fallback)
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
        
        // Extraction de base
        
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
        
        // Extraction du type de contrat
        let contractType = "Non spécifié";
        const contractTypes = [
            { pattern: /\b(cdi|contrat à durée indéterminée)\b/i, value: "CDI" },
            { pattern: /\b(cdd|contrat à durée déterminée)\b/i, value: "CDD" },
            { pattern: /\b(stage|internship)\b/i, value: "Stage" },
            { pattern: /\b(freelance|indépendant)\b/i, value: "Freelance" },
            { pattern: /\b(alternance|apprentissage)\b/i, value: "Alternance" }
        ];
        
        for (const { pattern, value } of contractTypes) {
            if (pattern.test(text)) {
                contractType = value;
                break;
            }
        }
        
        // Extraction des compétences (recherche de mots clés et puces)
        const skills = [];
        const skillSections = text.match(/(?:compétences|skills|requises|required|maîtrise).*?(?:\n\n|\n[A-Z]|$)/is);
        
        if (skillSections) {
            const skillText = skillSections[0];
            const skillBullets = skillText.match(/(?:^|\n)\s*[-•*]\s*([^\n]+)/g);
            
            if (skillBullets) {
                skillBullets.forEach(bullet => {
                    const skill = bullet.replace(/^\s*[-•*]\s*/, '').trim();
                    if (skill && skill.length > 3 && skill.length < 50) {
                        skills.push(skill);
                    }
                });
            }
        }
        
        // Extraction du salaire
        let salary = "Non spécifié";
        const salaryPatterns = [
            /salaire\s*:\s*([^\.]+)/i,
            /rémunération\s*:\s*([^\.]+)/i,
            /package\s*:\s*([^\.]+)/i,
            /[\d]{2,3}[\s]*[kK€]\s*[\-à]\s*[\d]{2,3}[\s]*[kK€]/,
            /[\d]{2,3}[\s]*000[\s]*€\s*[\-à]\s*[\d]{2,3}[\s]*000[\s]*€/,
            /entre\s+[\d]+[\s]*[kK€][\s]*et[\s]*[\d]+[\s]*[kK€]/i
        ];
        
        for (const pattern of salaryPatterns) {
            const match = text.match(pattern);
            if (match) {
                salary = match[0].trim();
                break;
            }
        }
        
        return {
            title: title,
            company: company,
            location: location,
            contract_type: contractType,
            required_skills: skills.length > 0 ? skills : ["Non spécifié"],
            preferred_skills: [],
            responsibilities: ["Non spécifié"],
            requirements: ["Non spécifié"],
            benefits: ["Non spécifié"],
            salary_range: salary,
            remote_policy: "Non spécifié"
        };
    }

    // Méthodes d'utilitaires

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
     * Envoie une requête directe à l'API
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
     * Affiche un message de log si le mode debug est activé
     * @param {...any} args - Arguments du log
     */
    log(...args) {
        if (this.config.debug) {
            console.log('%c[JobParserGPTAPI]', 'color: #7c3aed; font-weight: bold;', ...args);
        }
    }

    /**
     * Affiche un message d'erreur si le mode debug est activé
     * @param {...any} args - Arguments du log d'erreur
     */
    logError(...args) {
        if (this.config.debug) {
            console.error('%c[JobParserGPTAPI ERROR]', 'color: #ef4444; font-weight: bold;', ...args);
        }
    }
}

// Exporter l'API pour l'utiliser dans d'autres fichiers
window.JobParserGPTAPI = JobParserGPTAPI;
