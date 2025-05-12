/**
 * job-parser-api.js
 * Interface pour communiquer avec le service de parsing de fiches de poste 
 */

class JobParserAPI {
    constructor(options = {}) {
        // Configuration par défaut
        this.config = {
            apiUrl: options.apiUrl || 'http://localhost:5055/api/parse-job',
            timeout: options.timeout || 30000, // 30 secondes
            debug: options.debug || false,
            enablePDFCleaning: options.enablePDFCleaning || false,
            enableMockMode: options.enableMockMode || false
        };
        
        // Initialiser le nettoyeur PDF si activé
        if (this.config.enablePDFCleaning && typeof PDFCleaner === 'function') {
            this.pdfCleaner = new PDFCleaner();
        }
        
        // Log de débogage sur l'initialisation
        if (this.config.debug) {
            console.log('JobParserAPI initialisée avec la configuration:', this.config);
        }
    }
    
    /**
     * Parse une fiche de poste à partir d'un fichier
     * @param {File} file - Le fichier à analyser (PDF, DOCX, TXT)
     * @returns {Promise<Object>} Les informations extraites de la fiche de poste
     */
    async parseJobFile(file) {
        if (this.config.debug) {
            console.log(`Parsing du fichier: ${file.name} (${file.type}, ${file.size} bytes)`);
        }
        
        // Vérifier que le fichier est valide
        this._validateFile(file);
        
        // En mode mock, retourner des données simulées
        if (this.config.enableMockMode) {
            return this._getMockJobData(file.name);
        }
        
        // Créer un FormData avec le fichier
        const formData = new FormData();
        formData.append('file', file);
        
        // Nettoyer le PDF si nécessaire et possible
        if (this.config.enablePDFCleaning && file.type === 'application/pdf' && this.pdfCleaner) {
            try {
                const cleanedFile = await this.pdfCleaner.cleanFile(file);
                formData.set('file', cleanedFile);
                
                if (this.config.debug) {
                    console.log('Fichier PDF nettoyé avec succès');
                }
            } catch (error) {
                console.warn('Erreur lors du nettoyage du PDF, utilisation du fichier original:', error);
            }
        }
        
        // Envoyer la requête à l'API
        try {
            const response = await this._makeAPIRequest('POST', formData);
            
            // Traiter et retourner les données de parsing
            return this._processParsingResult(response);
        } catch (error) {
            // En cas d'erreur, essayer une analyse locale si possible
            console.error('Erreur lors de l\'appel à l\'API de parsing:', error);
            
            if (file.type === 'application/pdf' || file.type === 'text/plain') {
                // Pour les fichiers PDF et TXT, on peut essayer une extraction de texte locale
                try {
                    const text = await this._extractTextFromFile(file);
                    console.log('Fallback: Analyse locale du texte extrait');
                    return this.analyzeJobLocally(text);
                } catch (extractError) {
                    console.error('Erreur lors de l\'extraction locale du texte:', extractError);
                }
            }
            
            // Remonter l'erreur originale
            throw error;
        }
    }
    
    /**
     * Parse une fiche de poste à partir d'un texte
     * @param {string} text - Le texte de la fiche de poste
     * @returns {Promise<Object>} Les informations extraites de la fiche de poste
     */
    async parseJobText(text) {
        if (this.config.debug) {
            console.log(`Parsing du texte (${text.length} caractères)`);
        }
        
        // Vérifier que le texte est valide
        if (!text || typeof text !== 'string' || text.trim().length === 0) {
            throw new Error('Le texte de la fiche de poste est vide ou invalide');
        }
        
        // En mode mock, retourner des données simulées
        if (this.config.enableMockMode) {
            return this._getMockJobData();
        }
        
        // Créer un FormData avec le texte
        const formData = new FormData();
        formData.append('text', text);
        
        // Envoyer la requête à l'API
        try {
            const response = await this._makeAPIRequest('POST', formData);
            
            // Traiter et retourner les données de parsing
            return this._processParsingResult(response);
        } catch (error) {
            // En cas d'erreur, essayer une analyse locale
            console.error('Erreur lors de l\'appel à l\'API de parsing:', error);
            console.log('Fallback: Analyse locale du texte');
            return this.analyzeJobLocally(text);
        }
    }
    
    /**
     * Analyse une fiche de poste localement avec des expressions régulières
     * Utilisé comme fallback si l'API n'est pas disponible
     * @param {string} text - Le texte de la fiche de poste
     * @returns {Object} Les informations extraites de la fiche de poste
     */
    analyzeJobLocally(text) {
        if (this.config.debug) {
            console.log('Analyse locale du texte de la fiche de poste');
        }
        
        // Initialiser l'objet de résultat
        const result = {
            title: '',
            company: '',
            location: '',
            contract_type: '',
            skills: [],
            experience: '',
            education: '',
            salary: '',
            responsibilities: [],
            benefits: []
        };
        
        try {
            // Extraction du titre du poste
            const titlePatterns = [
                /(?:^|\n)[\s•]*Poste[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Intitulé du poste[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Offre d'emploi[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*([\w\s\-']+(?:développeur|ingénieur|technicien|consultant|manager|responsable|directeur|analyste)[\w\s\-']+)(?:\n|$)/i
            ];
            
            for (const pattern of titlePatterns) {
                const match = text.match(pattern);
                if (match) {
                    result.title = match[1].trim();
                    break;
                }
            }
            
            // Extraction de l'entreprise
            const companyPatterns = [
                /(?:^|\n)[\s•]*Entreprise[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Société[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Employeur[\s:]*(.+?)(?:\n|$)/i
            ];
            
            for (const pattern of companyPatterns) {
                const match = text.match(pattern);
                if (match) {
                    result.company = match[1].trim();
                    break;
                }
            }
            
            // Extraction de la localisation
            const locationPatterns = [
                /(?:^|\n)[\s•]*Lieu[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Localisation[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Localité[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Ville[\s:]*(.+?)(?:\n|$)/i
            ];
            
            for (const pattern of locationPatterns) {
                const match = text.match(pattern);
                if (match) {
                    result.location = match[1].trim();
                    break;
                }
            }
            
            // Extraction du type de contrat
            const contractPatterns = [
                /(?:^|\n)[\s•]*Type de contrat[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Contrat[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*(CDI|CDD|Stage|Alternance|Intérim|Freelance)(?:\n|$)/i
            ];
            
            for (const pattern of contractPatterns) {
                const match = text.match(pattern);
                if (match) {
                    result.contract_type = match[1].trim();
                    break;
                }
            }
            
            // Extraction des compétences
            const skillsPatterns = [
                /(?:^|\n)[\s•]*Compétences[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*Compétences requises[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*Compétences techniques[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*Qualifications[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*Prérequis[\s:]*(.+?)(?:\n\n|$)/i
            ];
            
            for (const pattern of skillsPatterns) {
                const match = text.match(pattern);
                if (match) {
                    const skillsText = match[1].trim();
                    // Extraire les compétences en les séparant par saut de ligne ou par des puces
                    const skills = skillsText.split(/[\n•,]/).map(s => s.trim()).filter(Boolean);
                    result.skills = skills;
                    break;
                }
            }
            
            // Extraction de l'expérience
            const expPatterns = [
                /(?:^|\n)[\s•]*Expérience[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Années d'expérience[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*([\d]+[\s]*ans d'expérience)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Expérience requise[\s:]*(.+?)(?:\n|$)/i
            ];
            
            for (const pattern of expPatterns) {
                const match = text.match(pattern);
                if (match) {
                    result.experience = match[1].trim();
                    break;
                }
            }
            
            // Extraction de la formation
            const eduPatterns = [
                /(?:^|\n)[\s•]*Formation[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Diplôme[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Niveau d'études[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Éducation[\s:]*(.+?)(?:\n|$)/i
            ];
            
            for (const pattern of eduPatterns) {
                const match = text.match(pattern);
                if (match) {
                    result.education = match[1].trim();
                    break;
                }
            }
            
            // Extraction du salaire
            const salaryPatterns = [
                /(?:^|\n)[\s•]*Salaire[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Rémunération[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*Package[\s:]*(.+?)(?:\n|$)/i,
                /(?:^|\n)[\s•]*\€[\s]*(.+?)(?:\n|$)/i
            ];
            
            for (const pattern of salaryPatterns) {
                const match = text.match(pattern);
                if (match) {
                    result.salary = match[1].trim();
                    break;
                }
            }
            
            // Extraction des responsabilités/missions
            const respPatterns = [
                /(?:^|\n)[\s•]*Description[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*Description du poste[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*Missions[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*Responsabilités[\s:]*(.+?)(?:\n\n|$)/i
            ];
            
            for (const pattern of respPatterns) {
                const match = text.match(pattern);
                if (match) {
                    result.responsibilities = [match[1].trim()];
                    break;
                }
            }
            
            // Extraction des avantages
            const benefitsPatterns = [
                /(?:^|\n)[\s•]*Avantages[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*Bénéfices[\s:]*(.+?)(?:\n\n|$)/i,
                /(?:^|\n)[\s•]*CE qu'on vous offre[\s:]*(.+?)(?:\n\n|$)/i
            ];
            
            for (const pattern of benefitsPatterns) {
                const match = text.match(pattern);
                if (match) {
                    const benefitsText = match[1].trim();
                    // Extraire les avantages en les séparant par saut de ligne ou par des puces
                    const benefits = benefitsText.split(/[\n•,]/).map(b => b.trim()).filter(Boolean);
                    result.benefits = benefits;
                    break;
                }
            }
            
            return result;
        } catch (error) {
            console.error('Erreur lors de l\'analyse locale:', error);
            return result; // Retourner le résultat même incomplet
        }
    }
    
    /**
     * Valide un fichier avant de l'envoyer à l'API
     * @param {File} file - Le fichier à valider
     * @throws {Error} Si le fichier est invalide
     * @private
     */
    _validateFile(file) {
        // Vérifier que le fichier est présent
        if (!file) {
            throw new Error('Aucun fichier fourni');
        }
        
        // Vérifier le type de fichier
        const allowedTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ];
        
        if (!allowedTypes.includes(file.type)) {
            throw new Error(`Type de fichier non supporté: ${file.type}. Types acceptés: PDF, DOC, DOCX et TXT.`);
        }
        
        // Vérifier la taille du fichier (max 5MB)
        const maxSize = 5 * 1024 * 1024; // 5MB
        if (file.size > maxSize) {
            throw new Error(`Fichier trop volumineux: ${Math.round(file.size / 1024 / 1024)}MB. Taille maximale: 5MB.`);
        }
    }
    
    /**
     * Fait une requête à l'API de parsing
     * @param {string} method - La méthode HTTP (GET, POST, etc.)
     * @param {FormData|Object} data - Les données à envoyer
     * @returns {Promise<Object>} La réponse de l'API
     * @private
     */
    async _makeAPIRequest(method, data) {
        // Déterminer l'URL de l'API
        const apiUrl = this._getApiUrl();
        
        // Options de la requête
        const options = {
            method: method,
            headers: {},
            body: data instanceof FormData ? data : JSON.stringify(data)
        };
        
        // Si les données ne sont pas un FormData, ajouter le header Content-Type
        if (!(data instanceof FormData)) {
            options.headers['Content-Type'] = 'application/json';
        }
        
        // Ajouter un timeout à la requête
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
        options.signal = controller.signal;
        
        try {
            // Log de debug pour la requête
            if (this.config.debug) {
                console.log(`Requête API: ${method} ${apiUrl}`);
                console.log('Données:', data instanceof FormData ? 'FormData' : data);
            }
            
            // Faire la requête
            const response = await fetch(apiUrl, options);
            
            // Annuler le timeout
            clearTimeout(timeoutId);
            
            // Vérifier le status de la réponse
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Erreur API (${response.status}): ${errorText}`);
            }
            
            // Parser la réponse JSON
            const result = await response.json();
            
            // Log de debug pour la réponse
            if (this.config.debug) {
                console.log('Réponse API:', result);
            }
            
            return result;
        } catch (error) {
            // Annuler le timeout si une erreur survient
            clearTimeout(timeoutId);
            
            // Si c'est une erreur de timeout
            if (error.name === 'AbortError') {
                throw new Error(`La requête a expiré après ${this.config.timeout / 1000} secondes`);
            }
            
            // Remonter l'erreur
            throw error;
        }
    }
    
    /**
     * Détermine l'URL de l'API à utiliser
     * @returns {string} L'URL de l'API
     * @private
     */
    _getApiUrl() {
        // Chercher d'abord dans les paramètres d'URL
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('apiUrl')) {
            return `${urlParams.get('apiUrl')}/api/parse-job`;
        }
        
        // Sinon, utiliser l'URL configurée
        return this.config.apiUrl;
    }
    
    /**
     * Extrait le texte d'un fichier localement
     * @param {File} file - Le fichier à traiter
     * @returns {Promise<string>} Le texte extrait
     * @private
     */
    async _extractTextFromFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (event) => {
                try {
                    const text = event.target.result;
                    resolve(text);
                } catch (error) {
                    reject(error);
                }
            };
            
            reader.onerror = (error) => {
                reject(error);
            };
            
            // Lire le fichier comme texte
            reader.readAsText(file);
        });
    }
    
    /**
     * Traite les résultats de parsing pour les normaliser
     * @param {Object} response - La réponse de l'API
     * @returns {Object} Les données normalisées
     * @private
     */
    _processParsingResult(response) {
        // Si la réponse a un format spécifique, la normaliser
        if (response.job_info) {
            // Format job_parser_gpt_cli.py
            const jobInfo = response.job_info;
            return {
                title: jobInfo.titre_poste || '',
                company: jobInfo.entreprise || '',
                location: jobInfo.localisation || '',
                contract_type: jobInfo.type_contrat || '',
                skills: Array.isArray(jobInfo.competences) ? 
                    jobInfo.competences : 
                    (jobInfo.competences ? [jobInfo.competences] : []),
                experience: jobInfo.experience || '',
                education: jobInfo.formation || '',
                salary: jobInfo.salaire || '',
                description: jobInfo.description || '',
                responsibilities: jobInfo.description ? [jobInfo.description] : [],
                benefits: []
            };
        }
        
        // Sinon, retourner la réponse telle quelle
        return response;
    }
    
    /**
     * Génère des données de mock pour les tests
     * @param {string} filename - Le nom du fichier (optionnel)
     * @returns {Object} Les données simulées
     * @private
     */
    _getMockJobData(filename = '') {
        // Données de mock basiques
        return {
            title: "Développeur Full Stack",
            company: "TechCorp Solutions",
            location: "Paris, France",
            contract_type: "CDI",
            skills: ["JavaScript", "React", "Node.js", "MongoDB", "Git"],
            experience: "3-5 ans",
            education: "Bac+5 en informatique ou équivalent",
            salary: "45-55K€ selon expérience",
            responsibilities: [
                "Développer des applications web responsive",
                "Collaborer avec l'équipe design pour implémenter les maquettes",
                "Maintenir et améliorer les applications existantes",
                "Participer aux revues de code et aux réunions d'équipe"
            ],
            benefits: [
                "Télétravail partiel",
                "Tickets restaurant",
                "Mutuelle d'entreprise",
                "Formation continue"
            ]
        };
    }
}

// Exposer la classe globalement
window.JobParserAPI = JobParserAPI;