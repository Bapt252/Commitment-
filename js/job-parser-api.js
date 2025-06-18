// Créer un service de parsing amélioré de fiches de poste
class JobParserAPI {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/parse-job';
        this.debug = options.debug || false;
        this.enablePDFCleaning = options.enablePDFCleaning || false;
        
        if (this.debug) {
            console.log('JobParserAPI initialized with options:', options);
        }
    }
    
    /**
     * Analyse le texte d'une fiche de poste
     * @param {string} text - Le texte de la fiche de poste
     * @returns {Promise<Object>} - Les résultats de l'analyse
     */
    async parseJobText(text) {
        if (this.debug) {
            console.log('Parsing job text...');
        }
        
        try {
            // Vérifier d'abord si on peut utiliser l'API
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendTextToApi(text);
            } else {
                console.warn('API not available, using local fallback');
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            console.error('Error parsing job text:', error);
            throw error;
        }
    }
    
    /**
     * Analyse un fichier de fiche de poste
     * @param {File} file - Le fichier de la fiche de poste
     * @returns {Promise<Object>} - Les résultats de l'analyse
     */
    async parseJobFile(file) {
        if (this.debug) {
            console.log('Parsing job file:', file.name);
        }
        
        try {
            // Vérifier d'abord si on peut utiliser l'API
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendFileToApi(file);
            } else {
                console.warn('API not available, converting file to text...');
                
                // Lire le contenu du fichier comme texte
                const text = await this.readFileAsText(file);
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            console.error('Error parsing job file:', error);
            throw error;
        }
    }
    
    /**
     * Vérifie si l'API est disponible
     * @returns {Promise<boolean>} - true si l'API est disponible, false sinon
     */
    async checkApiAvailability() {
        try {
            const apiUrl = this.apiUrl.replace('/parse-job', '/health');
            const response = await fetch(apiUrl, {
                method: 'GET',
                signal: AbortSignal.timeout(1000) // Timeout court
            });
            
            return response.ok;
        } catch (error) {
            console.warn('API check failed:', error);
            return false;
        }
    }
    
    /**
     * Envoie du texte à l'API pour analyse
     * @param {string} text - Le texte à analyser
     * @returns {Promise<Object>} - Les résultats de l'analyse
     */
    async sendTextToApi(text) {
        const formData = new FormData();
        formData.append('text', text);
        
        const response = await fetch(this.apiUrl, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API Error (${response.status}): ${await response.text()}`);
        }
        
        return await response.json();
    }
    
    /**
     * Envoie un fichier à l'API pour analyse
     * @param {File} file - Le fichier à analyser
     * @returns {Promise<Object>} - Les résultats de l'analyse
     */
    async sendFileToApi(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(this.apiUrl, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API Error (${response.status}): ${await response.text()}`);
        }
        
        return await response.json();
    }
    
    /**
     * Lit un fichier comme texte
     * @param {File} file - Le fichier à lire
     * @returns {Promise<string>} - Le contenu du fichier
     */
    async readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                resolve(e.target.result);
            };
            
            reader.onerror = function(e) {
                reject(new Error('Error reading file: ' + e.target.error));
            };
            
            reader.readAsText(file);
        });
    }
    
    /**
     * Nettoie le texte HTML en supprimant les balises et en normalisant
     * @param {string} text - Le texte à nettoyer
     * @returns {string} - Le texte nettoyé
     */
    cleanHtmlText(text) {
        // Supprimer les balises HTML
        let cleaned = text.replace(/<[^>]*>/g, ' ');
        
        // Normaliser les espaces
        cleaned = cleaned.replace(/\s+/g, ' ');
        
        // Nettoyer les caractères spéciaux HTML
        cleaned = cleaned.replace(/&nbsp;/g, ' ')
                        .replace(/&amp;/g, '&')
                        .replace(/&lt;/g, '<')
                        .replace(/&gt;/g, '>')
                        .replace(/&quot;/g, '"');
        
        return cleaned.trim();
    }
    
    /**
     * Analyse localement un texte de fiche de poste (fallback amélioré)
     * @param {string} text - Le texte à analyser
     * @returns {Object} - Les résultats de l'analyse
     */
    analyzeJobLocally(text) {
        if (this.debug) {
            console.log('Analyzing job locally with enhanced rules...');
        }
        
        // Nettoyer le HTML d'abord
        const cleanedText = this.cleanHtmlText(text);
        
        if (this.debug) {
            console.log('Cleaned text length:', cleanedText.length);
        }
        
        const result = {
            title: this.extractJobTitle(cleanedText),
            company: this.extractCompany(cleanedText),
            location: this.extractLocation(cleanedText),
            contract_type: this.extractContractType(cleanedText),
            skills: this.extractSkills(cleanedText),
            experience: this.extractExperience(cleanedText),
            education: this.extractEducation(cleanedText),
            salary: this.extractSalary(cleanedText),
            responsibilities: this.extractResponsibilities(cleanedText),
            benefits: this.extractBenefits(cleanedText)
        };
        
        if (this.debug) {
            console.log('Parsing results:', result);
        }
        
        return result;
    }
    
    // Méthodes d'extraction améliorées
    
    extractJobTitle(text) {
        const titleRegexList = [
            // Pattern spécifique "Fiche de poste XYZ"
            /fiche\s+de\s+poste\s+(.+?)(?:\n|$)/i,
            // Pattern "Poste : XYZ"
            /poste\s*[:]\s*([^\n.]+)/i,
            // Pattern "Titre : XYZ"
            /titre\s*[:]\s*([^\n.]+)/i,
            // Pattern "Recrute XYZ"
            /recrute\s*(?:un|une)?\s*([^\n.]+)/i,
            // Pattern "Recherche XYZ"
            /recherch(?:e|ons)\s*(?:un|une)?\s*([^\n.]+)/i,
            // Pattern pour les titres en début de ligne (après nettoyage HTML)
            /^([A-Z][^.\n]{5,50})(?:\s+et\s+[A-Z][^.\n]{3,30})?$/im
        ];
        
        for (const regex of titleRegexList) {
            const match = text.match(regex);
            if (match && match[1] && match[1].trim()) {
                let title = match[1].trim();
                // Nettoyer les mots parasites
                title = title.replace(/^\s*(le|la|les|un|une|des)\s+/i, '');
                if (title.length > 3 && title.length < 100) {
                    return title;
                }
            }
        }
        
        // Fallback : chercher des mots-clés de métiers courants en début de texte
        const commonJobs = [
            'gestionnaire', 'développeur', 'chef', 'responsable', 'directeur', 
            'assistant', 'conseiller', 'technicien', 'ingénieur', 'commercial',
            'comptable', 'analyste', 'consultant', 'coordinateur', 'superviseur'
        ];
        
        const lines = text.split('\n').slice(0, 5); // Chercher dans les 5 premières lignes
        for (const line of lines) {
            const cleanLine = line.trim();
            if (cleanLine.length > 5 && cleanLine.length < 80) {
                for (const job of commonJobs) {
                    if (cleanLine.toLowerCase().includes(job)) {
                        return cleanLine;
                    }
                }
            }
        }
        
        return 'Titre non détecté';
    }
    
    extractCompany(text) {
        const companyRegexList = [
            // Patterns spécifiques
            /(?:le|la)\s+([A-Z][A-Z\s&]+)\s+est\s+(?:la\s+)?référence/i,
            /(?:société|entreprise|cabinet|groupe|association)\s*[:]\s*([^\n.]+)/i,
            /(?:chez|pour)\s+([A-Z][A-Za-z\s&.-]+?)(?:\s|,|\.|\n)/,
            // Pattern pour détecter des noms d'entreprise en majuscules
            /\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b/g
        ];
        
        for (const regex of companyRegexList) {
            const match = text.match(regex);
            if (match && match[1] && match[1].trim()) {
                const company = match[1].trim();
                if (company.length > 2 && company.length < 100) {
                    return company;
                }
            }
        }
        
        return '';
    }
    
    extractLocation(text) {
        const locationRegexList = [
            // Pattern spécifique "Lieu de travail : 75014 Paris"
            /lieu\s+de\s+travail\s*[:]\s*([^\n.]+)/i,
            // Patterns génériques
            /(?:lieu|localisation|adresse|situé[e]?\s+à)\s*[:]\s*([^\n.]+)/i,
            // Pattern pour codes postaux français
            /\b(\d{5})\s+([A-Z][a-zéèêëïîôöùûüç]+(?:\s+[A-Z][a-zéèêëïîôöùûüç]+)*)\b/,
            // Pattern pour les villes
            /(?:à|sur|dans)\s+((?:[A-Z][a-zéèêëïîôöùûüç]+)(?:[\s-][A-Z][a-zéèêëïîôöùûüç]+)*)/,
            /(?:poste\s*basé\s*à|poste\s*localisé\s*à)\s+([^\n.]+)/i
        ];
        
        for (const regex of locationRegexList) {
            const match = text.match(regex);
            if (match && match[1] && match[1].trim()) {
                return match[1].trim();
            }
        }
        
        return '';
    }
    
    extractContractType(text) {
        const contractTypes = ['CDI', 'CDD', 'INTERIM', 'STAGE', 'ALTERNANCE', 'APPRENTISSAGE', 'FREELANCE'];
        const contractRegexList = [
            new RegExp(`(?:type\\s+de\\s+contrat|contrat)\\s*[:]*\\s*(${contractTypes.join('|')})`, 'i'),
            new RegExp(`\\b(${contractTypes.join('|')})\\b`, 'i')
        ];
        
        for (const regex of contractRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                return match[1].toUpperCase();
            }
        }
        
        return '';
    }
    
    extractSkills(text) {
        const skillSectionRegexList = [
            // Patterns pour les sections de compétences
            /comp[ée]tences(?:\s+(?:requises|techniques|et\s+savoir-faire))?(?:\s*[:]\s*)([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i,
            /(?:maîtrise\s+des?\s+outils?|outils?\s+de\s+gestion)([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i,
            /savoir-faire(?:\s*[:]\s*)([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i
        ];
        
        let skillsSection = '';
        for (const regex of skillSectionRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                skillsSection = match[1].trim();
                break;
            }
        }
        
        const skillsList = [];
        
        // Chercher des technologies/outils spécifiques
        const techSkills = [
            'Excel', 'Cegid', 'SAP', 'Word', 'PowerPoint', 'Outlook', 'Teams',
            'JavaScript', 'Python', 'React', 'Vue', 'Angular', 'Node.js',
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Git', 'Docker',
            'Photoshop', 'Illustrator', 'Figma', 'Sketch'
        ];
        
        for (const skill of techSkills) {
            if (text.toLowerCase().includes(skill.toLowerCase())) {
                skillsList.push(skill);
            }
        }
        
        // Extraire des compétences de la section identifiée
        if (skillsSection) {
            // Chercher des puces ou des listes
            const bulletItems = skillsSection.match(/(?:^|[\n\r])\s*[-•*]\s*([^\n\r]+)/g);
            if (bulletItems) {
                for (const item of bulletItems) {
                    const skill = item.replace(/^[\s\n\r]*[-•*]\s*/, '').trim();
                    if (skill && skill.length > 2 && skill.length < 100) {
                        skillsList.push(skill);
                    }
                }
            }
            
            // Si pas de puces, chercher des phrases avec des compétences
            const skillKeywords = [
                'connaissance', 'maîtrise', 'expérience avec', 'utilisation de',
                'rigueur', 'organisation', 'autonomie', 'communication', 'gestion'
            ];
            
            for (const keyword of skillKeywords) {
                const regex = new RegExp(`${keyword}[^.]*`, 'gi');
                const matches = skillsSection.match(regex);
                if (matches) {
                    matches.forEach(match => {
                        if (match.length > 10 && match.length < 150) {
                            skillsList.push(match.trim());
                        }
                    });
                }
            }
        }
        
        return [...new Set(skillsList)]; // Supprimer les doublons
    }
    
    extractExperience(text) {
        const experienceRegexList = [
            // Patterns spécifiques améliorés
            /exp[ée]rience\s*[:]\s*minimum\s*([^.\n]+)/i,
            /minimum\s*([0-9]+(?:[,-]\s*[0-9]+)?)\s*an(?:s|nées?)\s*d['']?exp[ée]rience/i,
            /([0-9]+(?:[,-]\s*[0-9]+)?)\s*an(?:s|nées?)\s*d['']?exp[ée]rience/i,
            /exp[ée]rience(?:\s+requise)?(?:\s*[:]\s*)([^.\n]+)/i,
            /(?:justifier\s+d['']|avoir)\s*([0-9]+(?:[,-]\s*[0-9]+)?)\s*an(?:s|nées?)/i
        ];
        
        for (const regex of experienceRegexList) {
            const match = text.match(regex);
            if (match && match[1] && match[1].trim()) {
                return match[1].trim();
            }
        }
        
        return '';
    }
    
    extractEducation(text) {
        const educationRegexList = [
            // Patterns spécifiques améliorés
            /formation\s*[:]\s*([^.\n]+)/i,
            /(bac\s*\+\s*[0-9]+(?:\/[0-9]+)?[^.\n]*)/i,
            /(?:diplôme|qualification)(?:\s+requis)?(?:\s*[:]\s*)([^.\n]+)/i,
            /((?:bac|master|licence|doctorat|ingénieur|école)[^.\n]{0,50})/i,
            /(BTS|DUT|Master|Licence)[^.\n]*/i
        ];
        
        for (const regex of educationRegexList) {
            const match = text.match(regex);
            if (match && (match[1] || match[0])) {
                const education = (match[1] || match[0]).trim();
                if (education.length > 3 && education.length < 200) {
                    return education;
                }
            }
        }
        
        return '';
    }
    
    extractSalary(text) {
        const salaryRegexList = [
            // Patterns spécifiques améliorés
            /r[ée]mun[ée]ration\s*[:]\s*([^.\n]+)/i,
            /salaire(?:\s+proposé)?\s*[:]\s*([^.\n]+)/i,
            /(à\s+partir\s+de\s+[0-9]+\s*k?€?[^.\n]*)/i,
            /([0-9]+\s*k?€?\s*(?:brut|net)?\s*(?:\/|\s*par)?\s*(?:an|mois|année))/i,
            /([0-9]+(?:[,.-]\s*[0-9]+)*\s*(?:à|au?|et|-)\s*[0-9]+(?:[,.-]\s*[0-9]+)*\s*k?€?[^.\n]*)/i
        ];
        
        for (const regex of salaryRegexList) {
            const match = text.match(regex);
            if (match && (match[1] || match[0])) {
                const salary = (match[1] || match[0]).trim();
                if (salary.length > 2 && salary.length < 100) {
                    return salary;
                }
            }
        }
        
        return '';
    }
    
    extractResponsibilities(text) {
        const respSectionRegexList = [
            // Patterns spécifiques améliorés
            /missions?\s+principales?\s*[:]\s*([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i,
            /(?:responsabilit[ée]s|missions|tâches)(?:\s*[:]\s*)([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i,
            /(?:vous\s+serez\s+chargé|vos\s+missions)([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i,
            /(?:descriptif|description)(?:\s+du\s+poste)?(?:\s*[:]\s*)([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i
        ];
        
        let respSection = '';
        for (const regex of respSectionRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                respSection = match[1].trim();
                break;
            }
        }
        
        if (!respSection) {
            return [];
        }
        
        const respList = [];
        
        // Traiter les listes à puces
        const bulletItems = respSection.match(/(?:^|[\n\r])\s*[-•*]\s*([^\n\r]+)/g);
        if (bulletItems) {
            for (const item of bulletItems) {
                const resp = item.replace(/^[\s\n\r]*[-•*]\s*/, '').trim();
                if (resp && resp.length > 5 && resp.length < 500) {
                    respList.push(resp);
                }
            }
        }
        
        // Si pas de liste à puces, découper par phrases ou paragraphes
        if (respList.length === 0) {
            const sentences = respSection.split(/[.!?]\s+/);
            for (const sentence of sentences) {
                const cleanSentence = sentence.trim();
                if (cleanSentence.length > 10 && cleanSentence.length < 500) {
                    respList.push(cleanSentence);
                }
            }
        }
        
        return respList.length > 0 ? respList : [];
    }
    
    extractBenefits(text) {
        const benefitSectionRegexList = [
            // Patterns spécifiques améliorés
            /avantages\s*[:]\s*([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i,
            /(?:bénéfices|nous\s+(?:vous\s+)?offrons|nous\s+proposons)(?:\s*[:]\s*)([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i,
            /(?:package|rémunération\s+et\s+avantages)(?:\s*[:]\s*)([^]*?)(?:\n\s*\n|\n\s*[A-Z][^:]*[:]\s*|\Z)/i
        ];
        
        let benefitSection = '';
        for (const regex of benefitSectionRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                benefitSection = match[1].trim();
                break;
            }
        }
        
        const benefitList = [];
        
        // Chercher des avantages spécifiques même sans section dédiée
        const commonBenefits = [
            'télétravail', 'restaurant d\'entreprise', 'mutuelle', 'prévoyance',
            'congés', 'RTT', '13e mois', 'prime', 'augmentation', 'évolution',
            'formation', 'tickets restaurant', 'transport', 'parking'
        ];
        
        for (const benefit of commonBenefits) {
            const regex = new RegExp(`[^.]*${benefit}[^.]*`, 'gi');
            const matches = text.match(regex);
            if (matches) {
                matches.forEach(match => {
                    const cleanMatch = match.trim();
                    if (cleanMatch.length > 10 && cleanMatch.length < 200) {
                        benefitList.push(cleanMatch);
                    }
                });
            }
        }
        
        if (benefitSection) {
            // Traiter les listes à puces
            const bulletItems = benefitSection.match(/(?:^|[\n\r])\s*[-•*]\s*([^\n\r]+)/g);
            if (bulletItems) {
                for (const item of bulletItems) {
                    const benefit = item.replace(/^[\s\n\r]*[-•*]\s*/, '').trim();
                    if (benefit && benefit.length > 2 && benefit.length < 200) {
                        benefitList.push(benefit);
                    }
                }
            }
            
            // Si pas de puces, découper par lignes ou virgules
            if (bulletItems === null || bulletItems.length === 0) {
                const items = benefitSection.split(/[,\n]/);
                for (const item of items) {
                    const benefit = item.trim();
                    if (benefit && benefit.length > 5 && benefit.length < 200) {
                        benefitList.push(benefit);
                    }
                }
            }
        }
        
        return [...new Set(benefitList)]; // Supprimer les doublons
    }
}

// Créer une instance globale pour l'utiliser dans d'autres scripts
window.JobParserAPI = JobParserAPI;
