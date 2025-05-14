/**
 * JobParserAPI - Classe pour l'intégration du parser de fiches de poste
 * Cette classe fournit des méthodes pour analyser des fiches de poste
 * à partir de fichiers PDF ou de texte brut.
 */
class JobParserAPI {
    /**
     * Initialise l'API du parser de fiches de poste
     * @param {Object} config - Configuration de l'API
     * @param {boolean} config.debug - Active le mode debug
     * @param {boolean} config.enablePDFCleaning - Active le nettoyage des PDF
     * @param {string} config.apiUrl - URL de l'API (par défaut: détection automatique ou localhost)
     * @param {boolean} config.forceLocalProcessing - Force l'analyse locale sans appeler l'API
     */
    constructor(config = {}) {
        // Récupérer l'URL de l'API depuis les paramètres de l'URL si disponible
        const urlParams = new URLSearchParams(window.location.search);
        const apiUrlFromParams = urlParams.get('apiUrl');
        
        this.config = {
            debug: config.debug || urlParams.has('debug'),
            enablePDFCleaning: config.enablePDFCleaning || false,
            apiUrl: config.apiUrl || apiUrlFromParams || this._detectApiUrl(),
            forceLocalProcessing: config.forceLocalProcessing || urlParams.has('localOnly')
        };
        
        if (this.config.debug) {
            console.log('JobParserAPI initialisée avec la configuration:', this.config);
        }
    }
    
    /**
     * Détecte automatiquement l'URL de l'API en fonction de l'environnement
     * @returns {string} URL de l'API
     * @private
     */
    _detectApiUrl() {
        // Essayer de détecter l'adresse du serveur en fonction de l'URL courante
        const currentUrl = new URL(window.location.href);
        const hostname = currentUrl.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return 'http://localhost:5055';
        } else if (hostname.includes('github.io')) {
            // En mode GitHub Pages, tenter plusieurs URLs connues
            return window.location.protocol + '//' + 
                  (window.location.hostname === 'localhost' ? 'localhost' : window.location.hostname) + 
                  ':5055';
        } else {
            // Fallback sur l'adresse IP locale ou le nom d'hôte actuel
            return window.location.protocol + '//' + hostname + ':5055';
        }
    }
    
    /**
     * Analyse un fichier PDF de fiche de poste
     * @param {File} file - Fichier PDF à analyser
     * @returns {Promise<Object>} - Résultat de l'analyse
     */
    async parseJobFile(file) {
        if (this.config.debug) {
            console.log('Analyse du fichier:', file.name);
        }
        
        // Si on force le traitement local, ne pas essayer l'API
        if (this.config.forceLocalProcessing) {
            if (this.config.debug) {
                console.log('Mode d\'analyse locale forcé, pas d\'appel API');
            }
            const text = await this._extractTextFromFile(file);
            return this.analyzeJobLocally(text);
        }
        
        try {
            const formData = new FormData();
            formData.append('job_post_file', file);
            
            if (this.config.debug) {
                console.log('Tentative d\'appel API à:', this.config.apiUrl);
            }
            
            try {
                // Vérifier si l'API est accessible
                const pingResponse = await fetch(`${this.config.apiUrl}/`, {
                    method: 'GET',
                    mode: 'cors',
                    cache: 'no-cache',
                    headers: {
                        'Accept': 'application/json'
                    },
                    timeout: 2000 // Timeout court pour le ping
                }).catch(e => {
                    if (this.config.debug) {
                        console.warn('Erreur lors du ping de l\'API:', e);
                    }
                    throw new Error('API indisponible');
                });
                
                if (!pingResponse || !pingResponse.ok) {
                    throw new Error('API indisponible');
                }
            } catch (pingError) {
                if (this.config.debug) {
                    console.warn('API indisponible, fallback sur l\'analyse locale', pingError);
                }
                const text = await this._extractTextFromFile(file);
                return this.analyzeJobLocally(text);
            }
            
            const response = await fetch(`${this.config.apiUrl}/api/parse-job-post`, {
                method: 'POST',
                mode: 'cors',
                cache: 'no-cache',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (this.config.debug) {
                console.log('Résultat de l\'analyse API:', result);
            }
            
            if (result.success) {
                return result.data;
            } else {
                throw new Error(result.error || 'Erreur lors de l\'analyse');
            }
        } catch (error) {
            if (this.config.debug) {
                console.error('Erreur lors de l\'analyse du fichier via API:', error);
            }
            
            // En cas d'erreur avec l'API, essayer l'analyse locale
            if (this.config.debug) {
                console.log('Fallback sur l\'analyse locale');
            }
            const text = await this._extractTextFromFile(file);
            return this.analyzeJobLocally(text);
        }
    }
    
    /**
     * Analyse un texte de fiche de poste
     * @param {string} text - Texte de la fiche de poste
     * @returns {Promise<Object>} - Résultat de l'analyse
     */
    async parseJobText(text) {
        if (this.config.debug) {
            console.log('Analyse du texte de la fiche de poste');
        }
        
        // Si on force le traitement local, ne pas essayer l'API
        if (this.config.forceLocalProcessing) {
            if (this.config.debug) {
                console.log('Mode d\'analyse locale forcé, pas d\'appel API');
            }
            return this.analyzeJobLocally(text);
        }
        
        try {
            try {
                // Vérifier si l'API est accessible
                const pingResponse = await fetch(`${this.config.apiUrl}/`, {
                    method: 'GET',
                    mode: 'cors',
                    cache: 'no-cache',
                    headers: {
                        'Accept': 'application/json'
                    },
                    timeout: 2000 // Timeout court pour le ping
                }).catch(e => {
                    if (this.config.debug) {
                        console.warn('Erreur lors du ping de l\'API:', e);
                    }
                    throw new Error('API indisponible');
                });
                
                if (!pingResponse || !pingResponse.ok) {
                    throw new Error('API indisponible');
                }
            } catch (pingError) {
                if (this.config.debug) {
                    console.warn('API indisponible, fallback sur l\'analyse locale', pingError);
                }
                return this.analyzeJobLocally(text);
            }
            
            const response = await fetch(`${this.config.apiUrl}/api/parse-job-post`, {
                method: 'POST',
                mode: 'cors',
                cache: 'no-cache',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ job_post_text: text })
            });
            
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (this.config.debug) {
                console.log('Résultat de l\'analyse API:', result);
            }
            
            if (result.success) {
                return result.data;
            } else {
                throw new Error(result.error || 'Erreur lors de l\'analyse');
            }
        } catch (error) {
            if (this.config.debug) {
                console.error('Erreur lors de l\'analyse du texte via API:', error);
            }
            
            // En cas d'erreur avec l'API, essayer l'analyse locale
            return this.analyzeJobLocally(text);
        }
    }
    
    /**
     * Analyse locale d'une fiche de poste (fallback si l'API n'est pas disponible)
     * @param {string} text - Texte de la fiche de poste
     * @returns {Object} - Résultat de l'analyse
     */
    analyzeJobLocally(text) {
        if (this.config.debug) {
            console.log('Analyse locale du texte de la fiche de poste');
        }
        
        // Extraction du titre du poste
        const titlePatterns = [
            /\b(?:poste|position|intitulé du poste|titre du poste|offre d'emploi)\s*[:-]\s*([^\.;\n\r]+)/i,
            /\brecherch(?:e|ons|ant)\s+(?:un(?:e)?)\s+([^\.;\n\r]+)/i,
            /\b(?:nous|entreprise)\s+recrut(?:e|ons)\s+(?:un(?:e)?)\s+([^\.;\n\r]+)/i,
            /\b((?:développeur|ingénieur|technicien|consultant|manager|responsable|directeur|analyste)[\s\w-]+)/i
        ];
        
        // Extraction de l'entreprise
        const companyPatterns = [
            /\b(?:entreprise|société|employeur|pour le compte de|au sein de)\s*[:-]\s*([^\.;\n\r]+)/i,
            /\b([\w\s-]+)\s+(?:est|recherche|recrute|souhaite)/i
        ];
        
        // Extraction de la localisation
        const locationPatterns = [
            /\b(?:lieu|localisation|localité|ville|site|basé à|poste basé|poste situé)\s*[:-]\s*([^\.;\n\r]+)/i,
            /\bà\s+([\w\s-]+)\s+\(\d{2,5}\)/i,
            /\b([\w\s-]+)\s+\(\d{2,5}\)/i
        ];
        
        // Extraction du type de contrat
        const contractPatterns = [
            /\b(?:type de contrat|contrat|type d'emploi)\s*[:-]\s*([^\.;\n\r]+)/i,
            /\b(CDI|CDD|Stage|Alternance|Intérim|Freelance|temps plein|temps partiel|permanent|temporaire)/i
        ];
        
        // Extraction de l'expérience requise
        const experiencePatterns = [
            /\b(?:expérience|années d'expérience|niveau d'expérience)\s*[:-]\s*([^\.;\n\r]+)/i,
            /\b(\d+[\s-]+ans?\s+d'expérience)/i,
            /\bexpérience\s+(?:de|d'au moins|minimum|min\.|requise|souhaitée)\s+(\d+[\s-]+ans?)/i,
            /\b(débutant|junior|confirmé|sénior|senior|expert)/i
        ];
        
        // Recherche de compétences techniques courantes dans le texte
        const commonSkills = [
            'JavaScript', 'React', 'Angular', 'Vue.js', 'Node.js', 'Python', 'Django', 'Flask',
            'Java', 'Spring', 'C#', '.NET', 'PHP', 'Laravel', 'Symfony', 'Ruby', 'Rails',
            'Go', 'Rust', 'TypeScript', 'HTML', 'CSS', 'SASS', 'LESS', 'SQL', 'MySQL',
            'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', 'CI/CD', 'Jenkins', 'Git', 'Agile', 'Scrum', 'Jira',
            'DevOps', 'TDD', 'Swift', 'Kotlin', 'Unity', 'Flutter', 'Dart', 'Firebase'
        ];
        
        // Recherche de formations/diplômes courants
        const educationPatterns = [
            /\b(?:formation|diplôme|niveau d'études|niveau de formation|profil académique)\s*[:-]\s*([^\.;\n\r]+)/i,
            /\b(Bac\s*\+\s*\d|Master|Licence|Bachelor|Ingénieur|Doctorat|MBA|BTS|DUT)/i
        ];
        
        // Recherche de salaire/rémunération
        const salaryPatterns = [
            /\b(?:salaire|rémunération|package|traitement|appointements)\s*[:-]\s*([^\.;\n\r]+)/i,
            /\b(\d+[\s-]*[kK€]|\d+[\s-]*000[\s-]*€|\d+[\s-]*000[\s-]*euros)/i
        ];
        
        // Extraction des informations à partir des patterns définis
        const extractInfo = (patterns, defaultValue = 'Not specified') => {
            for (const pattern of patterns) {
                const match = text.match(pattern);
                if (match && match[1] && match[1].trim()) {
                    return match[1].trim();
                }
            }
            return defaultValue;
        };
        
        // Extraction des compétences techniques
        const extractSkills = () => {
            const skills = [];
            for (const skill of commonSkills) {
                const pattern = new RegExp('\\b' + skill + '\\b', 'i');
                if (pattern.test(text)) {
                    skills.push(skill);
                }
            }
            return skills.length > 0 ? skills : ['Not specified'];
        };
        
        // Analyse des responsabilités/missions
        const extractResponsibilities = () => {
            const responsibilitiesPatterns = [
                /(?:missions|responsabilités|tâches|activités|missions principales)[\s\n]*:[\s\n]*((?:[\s\n]*[-•*][\s\n]*[^;:\.]*[;:\.]*[\s\n]*)+)/i,
                /(?:vous serez chargé de|vous serez responsable de|vous serez amené à)[\s\n]*:[\s\n]*((?:[\s\n]*[-•*][\s\n]*[^;:\.]*[;:\.]*[\s\n]*)+)/i
            ];
            
            for (const pattern of responsibilitiesPatterns) {
                const match = text.match(pattern);
                if (match && match[1]) {
                    // Extraction des items à puces
                    const itemsText = match[1];
                    const items = itemsText.split(/[\s\n]*[-•*][\s\n]*/).filter(item => item.trim().length > 0);
                    if (items.length > 0) {
                        return items.map(item => item.trim());
                    }
                }
            }
            return ['Not specified'];
        };
        
        // Extraction des avantages
        const extractBenefits = () => {
            const benefitsPatterns = [
                /(?:avantages|benefits|nous offrons|nous proposons|nous vous offrons|package|ce que nous offrons)[\s\n]*:[\s\n]*((?:[\s\n]*[-•*][\s\n]*[^;:\.]*[;:\.]*[\s\n]*)+)/i
            ];
            
            const commonBenefits = [
                'tickets restaurant', 'mutuelle', 'prévoyance', 'RTT', 'télétravail', 'remote',
                'flexible', 'formation', 'transport', 'treizième mois', '13ème mois',
                'bonus', 'intéressement', 'participation', 'CE', 'comité d\'entreprise'
            ];
            
            // Chercher par pattern
            for (const pattern of benefitsPatterns) {
                const match = text.match(pattern);
                if (match && match[1]) {
                    const itemsText = match[1];
                    const items = itemsText.split(/[\s\n]*[-•*][\s\n]*/).filter(item => item.trim().length > 0);
                    if (items.length > 0) {
                        return items.map(item => item.trim());
                    }
                }
            }
            
            // Si aucun pattern ne match, chercher les avantages courants dans le texte
            const benefits = [];
            for (const benefit of commonBenefits) {
                const pattern = new RegExp('\\b' + benefit + '\\b', 'i');
                if (pattern.test(text)) {
                    benefits.push(benefit);
                }
            }
            return benefits.length > 0 ? benefits : ['Not specified'];
        };
        
        // Résultat de l'analyse locale
        const result = {
            title: extractInfo(titlePatterns, 'Unknown Position'),
            company: extractInfo(companyPatterns, 'Unknown Company'),
            location: extractInfo(locationPatterns, 'Unknown Location'),
            contractType: extractInfo(contractPatterns),
            experience: extractInfo(experiencePatterns),
            education: extractInfo(educationPatterns),
            salary: extractInfo(salaryPatterns),
            skills: extractSkills(),
            responsibilities: extractResponsibilities(),
            benefits: extractBenefits()
        };
        
        if (this.config.debug) {
            console.log('Résultat de l\'analyse locale:', result);
        }
        
        return result;
    }
    
    /**
     * Extraire le texte d'un fichier (PDF, DOC, DOCX, TXT)
     * @param {File} file - Fichier à traiter
     * @returns {Promise<string>} - Texte extrait du fichier
     * @private
     */
    async _extractTextFromFile(file) {
        if (this.config.debug) {
            console.log('Extraction du texte du fichier:', file.name);
        }
        
        if (file.type === 'text/plain') {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = e => resolve(e.target.result);
                reader.onerror = e => reject(e);
                reader.readAsText(file);
            });
        }
        
        if (file.type === 'application/pdf') {
            // Si le module PDFCleaner est disponible, l'utiliser
            if (window.PDFCleaner && this.config.enablePDFCleaning) {
                try {
                    return await window.PDFCleaner.extractTextFromPDF(file);
                } catch (error) {
                    console.error('Erreur lors de l\'extraction avec PDFCleaner:', error);
                    // Fallback sur l'extraction simple
                    return this._basicExtractTextFromPDF(file);
                }
            } else {
                return this._basicExtractTextFromPDF(file);
            }
        }
        
        // Pour les autres types de fichiers, renvoyer une erreur
        throw new Error(`Type de fichier non supporté: ${file.type}`);
    }
    
    /**
     * Extraction basique de texte d'un PDF (à remplacer par une bibliothèque plus robuste)
     * @param {File} file - Fichier PDF
     * @returns {Promise<string>} - Texte extrait du PDF
     * @private
     */
    _basicExtractTextFromPDF(file) {
        // Cette fonction est un placeholder
        // Dans une implémentation réelle, utiliser pdf.js ou une autre bibliothèque
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve(
                    "Contenu basique extrait du PDF. Pour une extraction complète, " +
                    "veuillez utiliser le service d'API ou activer le nettoyage PDF."
                );
            }, 500);
        });
    }
}

// Exposer la classe globalement
window.JobParserAPI = JobParserAPI;
