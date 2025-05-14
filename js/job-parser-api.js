// Créer un service de parsing basique de fiches de poste
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
     * Analyse localement un texte de fiche de poste (fallback)
     * @param {string} text - Le texte à analyser
     * @returns {Object} - Les résultats de l'analyse
     */
    analyzeJobLocally(text) {
        // Version simplifiée d'analyse locale
        if (this.debug) {
            console.log('Analyzing job locally...');
        }
        
        const result = {
            title: this.extractJobTitle(text),
            company: this.extractCompany(text),
            location: this.extractLocation(text),
            contract_type: this.extractContractType(text),
            skills: this.extractSkills(text),
            experience: this.extractExperience(text),
            education: this.extractEducation(text),
            salary: this.extractSalary(text),
            responsibilities: this.extractResponsibilities(text),
            benefits: this.extractBenefits(text)
        };
        
        return result;
    }
    
    // Méthodes d'extraction basées sur des règles simples
    
    extractJobTitle(text) {
        // Chercher les mots-clés indiquant un titre de poste
        const titleRegexList = [
            /poste\s*:\s*([^\n.]+)/i,
            /titre\s*:\s*([^\n.]+)/i,
            /recrute\s*(?:un|une)\s*([^\n.]+)/i,
            /recherch(?:e|ons)\s*(?:un|une)\s*([^\n.]+)/i,
            /^([^\n.]+?)(?:\n|$)/i  // Première ligne comme fallback
        ];
        
        for (const regex of titleRegexList) {
            const match = text.match(regex);
            if (match && match[1] && match[1].trim()) {
                return match[1].trim();
            }
        }
        
        return 'Titre non détecté';
    }
    
    extractCompany(text) {
        // Chercher des mentions d'entreprise
        const companyRegexList = [
            /(?:société|entreprise|cabinet|groupe)\s*:\s*([^\n.]+)/i,
            /(?:chez|pour)\s+([^\n.]+?)(?:\s|,|\.)/i
        ];
        
        for (const regex of companyRegexList) {
            const match = text.match(regex);
            if (match && match[1] && match[1].trim()) {
                return match[1].trim();
            }
        }
        
        return '';
    }
    
    extractLocation(text) {
        // Chercher des mentions de lieu
        const locationRegexList = [
            /(?:lieu|localisation|adresse|situé[e]? à)\s*:?\s*([^\n.]+)/i,
            /(?:à|sur|dans)\s+((?:(?:[A-Z][a-zéèêëïîôöùûüç]+)(?:[\s-][A-Z][a-zéèêëïîôöùûüç]+)*)|(?:\d{5}))/i,
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
        // Chercher des mentions de type de contrat
        const contractTypes = ['CDI', 'CDD', 'INTERIM', 'STAGE', 'ALTERNANCE', 'APPRENTISSAGE', 'FREELANCE'];
        const contractRegexList = [
            new RegExp(`(?:contrat|type de contrat)\\s*:?\\s*(${contractTypes.join('|')})`, 'i'),
            new RegExp(`(${contractTypes.join('|')})`, 'i')
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
        // Identificateur de sections liées aux compétences
        const skillSectionRegexList = [
            /comp[ée]tences(?:\s+requises|\s+techniques)?(?:\s*:|\s*\n)([\s\S]*?)(?:\n\s*\n|\n\s*[A-Z]|\Z)/i,
            /profil(?:\s+recherch[ée])?(?:\s*:|\s*\n)([\s\S]*?)(?:\n\s*\n|\n\s*[A-Z]|\Z)/i,
            /qualifications(?:\s*:|\s*\n)([\s\S]*?)(?:\n\s*\n|\n\s*[A-Z]|\Z)/i
        ];
        
        // Extraire la section compétences
        let skillsSection = '';
        for (const regex of skillSectionRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                skillsSection = match[1].trim();
                break;
            }
        }
        
        if (!skillsSection) {
            return [];
        }
        
        // Extraire les compétences individuelles (liste à puces ou séparées par virgules)
        const skillsList = [];
        
        // Traiter les listes à puces
        const bulletItems = skillsSection.match(/(?:^|\n)\s*[-•*]\s*([^\n]+)/g);
        if (bulletItems) {
            for (const item of bulletItems) {
                const skill = item.replace(/^\s*[-•*]\s*/, '').trim();
                if (skill && skill.length > 2) {
                    skillsList.push(skill);
                }
            }
        }
        
        // Si pas de liste à puces, découper par virgules/points/sauts de ligne
        if (skillsList.length === 0) {
            const items = skillsSection.split(/[,.;\n]/);
            for (const item of items) {
                const skill = item.trim();
                if (skill && skill.length > 2) {
                    skillsList.push(skill);
                }
            }
        }
        
        return skillsList.length > 0 ? skillsList : [];
    }
    
    extractExperience(text) {
        // Chercher des mentions d'expérience
        const experienceRegexList = [
            /exp[ée]rience(?:\s+requise)?(?:\s*:|\s+de|\s+d[''])\s*([^\n.]+)/i,
            /(\d+(?:[,\.]\d+)?(?:\s*[-àa]\s*\d+(?:[,\.]\d+)?)?)\s*an(?:s|nées?)(?:\s+d['']exp[ée]rience)?/i
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
        // Chercher des mentions de formation
        const educationRegexList = [
            /formation(?:\s+requise)?(?:\s*:|\s+de|\s+en|\s+type)\s*([^\n.]+)/i,
            /(?:dipl[ôo]me|qualification)(?:\s+requis)?(?:\s*:|\s+de|\s+en)\s*([^\n.]+)/i,
            /(?:bac|master|licence|doctorat|ingénieur|école)(?:\s*\+\s*\d+|\s+\d+)?(?:[^\n.]{0,30})/i
        ];
        
        for (const regex of educationRegexList) {
            const match = text.match(regex);
            if (match && (match[1] || match[0]) && (match[1] || match[0]).trim()) {
                return (match[1] || match[0]).trim();
            }
        }
        
        return '';
    }
    
    extractSalary(text) {
        // Chercher des mentions de salaire
        const salaryRegexList = [
            /salaire(?:\s+proposé)?(?:\s*:|\s+de|\s+entre|\s*\(?\s*(?:brut|net)\s*\)?)\s*([^\n.]+)/i,
            /((?:\d{2,3}(?:\s|\s*[ ,.]\s*)\d{3})|(?:\d{1,3}[kK])|(?:\d+(?:[,.]\d+)?[ ]*(?:à|au?|et|-)[ ]*\d+(?:[,.]\d+)?))[ ]*(?:€|k€|euros|EUR)?[ ]*(?:brut|net)?[ ]*(?:\/|par)?[ ]*(?:an|mois|jour)/i,
            /r[ée]mun[ée]ration(?:\s*:|\s+de|\s+entre|\s+à)\s*([^\n.]+)/i
        ];
        
        for (const regex of salaryRegexList) {
            const match = text.match(regex);
            if (match && (match[1] || match[0]) && (match[1] || match[0]).trim()) {
                return (match[1] || match[0]).trim();
            }
        }
        
        return '';
    }
    
    extractResponsibilities(text) {
        // Identificateur de sections liées aux responsabilités
        const respSectionRegexList = [
            /(?:missions|responsabilit[ée]s|t[âa]ches|poste)(?:\s*:|\s*\n)([\s\S]*?)(?:\n\s*\n|\n\s*[A-Z]|\Z)/i,
            /(?:descriptif|description)(?:\s+du poste)?(?:\s*:|\s*\n)([\s\S]*?)(?:\n\s*\n|\n\s*[A-Z]|\Z)/i
        ];
        
        // Extraire la section responsabilités
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
        
        // Extraire les responsabilités individuelles (liste à puces ou séparées par points)
        const respList = [];
        
        // Traiter les listes à puces
        const bulletItems = respSection.match(/(?:^|\n)\s*[-•*]\s*([^\n]+)/g);
        if (bulletItems) {
            for (const item of bulletItems) {
                const resp = item.replace(/^\s*[-•*]\s*/, '').trim();
                if (resp && resp.length > 5) {
                    respList.push(resp);
                }
            }
        }
        
        // Si pas de liste à puces, prendre tout comme une seule responsabilité
        if (respList.length === 0) {
            respList.push(respSection);
        }
        
        return respList;
    }
    
    extractBenefits(text) {
        // Identificateur de sections liées aux avantages
        const benefitSectionRegexList = [
            /(?:avantages|b[ée]n[ée]fices|nous\s+(?:vous\s+)?offrons|nous\s+proposons)(?:\s*:|\s*\n)([\s\S]*?)(?:\n\s*\n|\n\s*[A-Z]|\Z)/i,
            /(?:package|r[ée]mun[ée]ration et avantages)(?:\s*:|\s*\n)([\s\S]*?)(?:\n\s*\n|\n\s*[A-Z]|\Z)/i
        ];
        
        // Extraire la section avantages
        let benefitSection = '';
        for (const regex of benefitSectionRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                benefitSection = match[1].trim();
                break;
            }
        }
        
        if (!benefitSection) {
            return [];
        }
        
        // Extraire les avantages individuels (liste à puces ou séparées par points)
        const benefitList = [];
        
        // Traiter les listes à puces
        const bulletItems = benefitSection.match(/(?:^|\n)\s*[-•*]\s*([^\n]+)/g);
        if (bulletItems) {
            for (const item of bulletItems) {
                const benefit = item.replace(/^\s*[-•*]\s*/, '').trim();
                if (benefit && benefit.length > 2) {
                    benefitList.push(benefit);
                }
            }
        }
        
        // Si pas de liste à puces, découper par virgules/points/sauts de ligne
        if (benefitList.length === 0) {
            const items = benefitSection.split(/[,.;\n]/);
            for (const item of items) {
                const benefit = item.trim();
                if (benefit && benefit.length > 2) {
                    benefitList.push(benefit);
                }
            }
        }
        
        return benefitList.length > 0 ? benefitList : [];
    }
}

// Créer une instance globale pour l'utiliser dans d'autres scripts
window.JobParserAPI = JobParserAPI;
