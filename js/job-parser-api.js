// JobParserAPI v2.3 - Version améliorée avec règles d'extraction optimisées pour les fiches de poste françaises
class JobParserAPI {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/parse-job';
        this.debug = options.debug || false;
        this.enablePDFCleaning = options.enablePDFCleaning || false;
        
        if (this.debug) {
            console.log('JobParserAPI v2.3 Enhanced initialized with options:', options);
        }
    }
    
    /**
     * Analyse le texte d'une fiche de poste
     * @param {string} text - Le texte de la fiche de poste
     * @returns {Promise<Object>} - Les résultats de l'analyse
     */
    async parseJobText(text) {
        if (this.debug) {
            console.log('🚀 Parsing job text with enhanced v2.3...');
        }
        
        try {
            // Vérifier d'abord si on peut utiliser l'API
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendTextToApi(text);
            } else {
                console.warn('API not available, using enhanced local fallback v2.3');
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
            console.log('📄 Parsing job file with enhanced v2.3:', file.name);
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
     * Version améliorée v2.3 avec meilleur traitement des entités HTML françaises
     */
    cleanHtmlText(text) {
        if (this.debug) {
            console.log('🧹 Nettoyage HTML avancé v2.3...');
        }
        
        let cleaned = text;
        
        // Remplacer les balises de paragraphe par des sauts de ligne
        cleaned = cleaned.replace(/<\/p>/gi, '\n');
        cleaned = cleaned.replace(/<br\s*\/?>/gi, '\n');
        cleaned = cleaned.replace(/<\/div>/gi, '\n');
        cleaned = cleaned.replace(/<\/li>/gi, '\n');
        cleaned = cleaned.replace(/<\/h[1-6]>/gi, '\n');
        
        // Supprimer toutes les autres balises HTML
        cleaned = cleaned.replace(/<[^>]*>/g, ' ');
        
        // Nettoyer les entités HTML étendues (spécialement pour le français)
        const htmlEntities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&agrave;': 'à',
            '&aacute;': 'á',
            '&eacute;': 'é',
            '&egrave;': 'è',
            '&ecirc;': 'ê',
            '&euml;': 'ë',
            '&iacute;': 'í',
            '&igrave;': 'ì',
            '&icirc;': 'î',
            '&iuml;': 'ï',
            '&oacute;': 'ó',
            '&ograve;': 'ò',
            '&ocirc;': 'ô',
            '&ouml;': 'ö',
            '&uacute;': 'ú',
            '&ugrave;': 'ù',
            '&ucirc;': 'û',
            '&uuml;': 'ü',
            '&ccedil;': 'ç'
        };
        
        Object.keys(htmlEntities).forEach(entity => {
            const regex = new RegExp(entity, 'gi');
            cleaned = cleaned.replace(regex, htmlEntities[entity]);
        });
        
        // Nettoyer les entités numériques
        cleaned = cleaned.replace(/&#(\d+);/g, (match, num) => {
            return String.fromCharCode(parseInt(num));
        });
        
        // Normaliser les espaces multiples
        cleaned = cleaned.replace(/\s+/g, ' ');
        
        // Nettoyer les espaces autour des sauts de ligne
        cleaned = cleaned.replace(/\s*\n\s*/g, '\n');
        
        return cleaned.trim();
    }
    
    /**
     * Analyse localement un texte de fiche de poste (fallback amélioré v2.3)
     * @param {string} text - Le texte à analyser
     * @returns {Object} - Les résultats de l'analyse
     */
    analyzeJobLocally(text) {
        if (this.debug) {
            console.log('🔍 Analyzing job locally with enhanced rules v2.3...');
        }
        
        // Nettoyer le HTML d'abord
        const cleanedText = this.cleanHtmlText(text);
        
        if (this.debug) {
            console.log('📝 Cleaned text length:', cleanedText.length);
            console.log('📝 Cleaned text sample (300 chars):', cleanedText.substring(0, 300));
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
            console.log('📊 Enhanced parsing results v2.3:', result);
        }
        
        return result;
    }
    
    // Méthodes d'extraction améliorées v2.3
    
    /**
     * Extraction du titre de poste améliorée spécialement pour les fiches françaises
     */
    extractJobTitle(text) {
        if (this.debug) {
            console.log('🎯 Enhanced title extraction for French job posts...');
        }
        
        const titleRegexList = [
            // Patterns spécifiques français
            /fiche\s+de\s+poste\s*[:\-]?\s*(.+?)(?:\n|$)/i,
            /offre\s+d?[''']?emploi\s*[:\-]?\s*(.+?)(?:\n|$)/i,
            /poste\s*[:\-]\s*([^\n.]+)/i,
            /titre\s*[:\-]\s*([^\n.]+)/i,
            /intitulé\s*[:\-]?\s*([^\n.]+)/i,
            
            // Patterns pour actions de recrutement
            /recrute\s*(?:un[e]?)?\s*([^\n.]+?)(?:\s+\(|$|\n)/i,
            /recherche\s*(?:un[e]?)?\s*([^\n.]+?)(?:\s+\(|$|\n)/i,
            /cherche\s*(?:un[e]?)?\s*([^\n.]+?)(?:\s+\(|$|\n)/i,
            
            // Patterns pour métiers spécifiques français
            /(gestionnaire\s+(?:paie|rh|administration|comptabilité|stock|clientèle)[^\n]*)/i,
            /(responsable\s+(?:commercial|marketing|rh|paie|comptabilité|administration|communication)[^\n]*)/i,
            /(chef\s+(?:de\s+(?:projet|service|vente|rayon|produit)|comptable|d'équipe)[^\n]*)/i,
            /(directeur\s+(?:commercial|marketing|administratif|général|financier)[^\n]*)/i,
            /(assistant[e]?\s+(?:commercial|administratif|rh|comptable|direction|marketing)[^\n]*)/i,
            /(conseiller[ère]?\s+(?:commercial|clientèle|vente|immobilier|financier)[^\n]*)/i,
            /(technicien[ne]?\s+(?:maintenance|informatique|qualité|support)[^\n]*)/i,
            /(ingénieur\s+(?:commercial|système|qualité|développement|informatique)[^\n]*)/i,
            /(développeur\s+(?:web|mobile|frontend|backend|fullstack|javascript)[^\n]*)/i,
            /(analyste\s+(?:financier|système|données|programmeur)[^\n]*)/i,
            /(consultant[e]?\s+(?:rh|marketing|système|commercial)[^\n]*)/i,
            /(coordinateur[trice]?\s+(?:projet|qualité|logistique|marketing)[^\n]*)/i,
            /(manager\s+(?:commercial|équipe|projet|retail)[^\n]*)/i,
            /(chargé[e]?\s+(?:de\s+(?:communication|marketing|clientèle|projet)|d'affaires)[^\n]*)/i,
            
            // Pattern générique pour titres en début de ligne (plus permissif)
            /^([A-Z][A-Za-z\s&.-]{5,60})(?:\s*[-–—]\s*[A-Z]|$)/m,
            
            // Pattern pour lignes courtes en majuscules
            /^([A-Z\s&]{8,40})$/m
        ];
        
        for (const regex of titleRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                let title = match[1].trim();
                
                // Nettoyer le titre extrait
                title = title.replace(/^(le|la|les|un|une|des)\s+/i, '');
                title = title.replace(/\s*[(.]\s*h\/f\s*[).]?\s*$/i, '');
                title = title.replace(/\s*[(.]\s*f\/h\s*[).]?\s*$/i, '');
                title = title.replace(/\s*[(.]\s*cdi\s*[).]?\s*$/i, '');
                title = title.replace(/\s*[(.]\s*cdd\s*[).]?\s*$/i, '');
                title = title.replace(/\s*[(.]\s*temps\s+(?:plein|partiel)\s*[).]?\s*$/i, '');
                
                if (title.length >= 5 && title.length <= 80 && !title.includes('©') && !title.includes('@')) {
                    if (this.debug) {
                        console.log('✅ Title found:', title);
                    }
                    return title;
                }
            }
        }
        
        // Fallback : chercher des mots-clés métier dans les premières lignes
        const lines = text.split('\n').slice(0, 8);
        for (const line of lines) {
            const cleanLine = line.trim();
            if (cleanLine.length > 5 && cleanLine.length < 80) {
                const jobKeywords = [
                    'gestionnaire', 'responsable', 'chef', 'directeur', 'assistant',
                    'conseiller', 'technicien', 'ingénieur', 'développeur', 'commercial',
                    'comptable', 'analyste', 'consultant', 'coordinateur', 'superviseur',
                    'manager', 'chargé', 'adjoint', 'secrétaire', 'vendeur', 'employé'
                ];
                
                for (const keyword of jobKeywords) {
                    if (cleanLine.toLowerCase().includes(keyword)) {
                        if (this.debug) {
                            console.log('✅ Title found (fallback):', cleanLine);
                        }
                        return cleanLine;
                    }
                }
            }
        }
        
        if (this.debug) {
            console.log('❌ No title detected');
        }
        return 'Titre non détecté';
    }
    
    /**
     * Extraction du lieu améliorée pour les adresses françaises
     */
    extractLocation(text) {
        if (this.debug) {
            console.log('📍 Enhanced location extraction for French addresses...');
        }
        
        const locationRegexList = [
            // Patterns spécifiques français
            /lieu\s+de\s+travail\s*[:\-]?\s*([^\n.]+)/i,
            /localisation\s*[:\-]?\s*([^\n.]+)/i,
            /adresse\s*[:\-]?\s*([^\n.]+)/i,
            /situé[e]?\s+(?:à|au|en)\s+([^\n.]+)/i,
            /poste\s+basé\s+(?:à|au|en)\s+([^\n.]+)/i,
            /poste\s+localisé\s+(?:à|au|en)\s+([^\n.]+)/i,
            /travail\s+(?:à|au|en)\s+([^\n.]+)/i,
            /secteur\s*[:\-]?\s*([^\n.]+)/i,
            
            // Patterns pour codes postaux français (5 chiffres + ville)
            /(\d{5})\s+([A-Z][a-zéèêëïîôöùûüç]+(?:[\s-][A-Z][a-zéèêëïîôöùûüç]+)*)/,
            
            // Patterns pour grandes villes françaises
            /(paris\s*(?:\d{1,2}[èe]?)?(?:\s*arrondissement)?)/i,
            /(lyon\s*\d?)/i,
            /(marseille\s*\d?)/i,
            /(toulouse\s*\d?)/i,
            /(lille\s*\d?)/i,
            /(bordeaux\s*\d?)/i,
            /(nantes\s*\d?)/i,
            /(strasbourg\s*\d?)/i,
            /(rennes\s*\d?)/i,
            /(montpellier\s*\d?)/i,
            /(nice\s*\d?)/i,
            /(grenoble\s*\d?)/i,
            
            // Pattern pour "à Paris", "sur Lyon", etc.
            /(?:à|sur|dans|en)\s+((?:[A-Z][a-zéèêëïîôöùûüç]+)(?:[\s-][A-Z][a-zéèêëïîôöùûüç]+)*)/,
            
            // Pattern pour département (2 chiffres)
            /(\d{2})\s*[-–]?\s*([A-Z][a-zéèêëïîôöùûüç]+(?:[\s-][A-Z][a-zéèêëïîôöùûüç]+)*)/,
            
            // Pattern générique pour lieu avec ponctuation
            /(?:lieu|zone|région)\s*[:\-]?\s*([A-Z][a-zA-Zéèêëïîôöùûüç\s-]+)/i
        ];
        
        for (const regex of locationRegexList) {
            const match = text.match(regex);
            if (match) {
                let location = '';
                
                if (match[1] && match[2]) {
                    // Code postal + ville ou département + région
                    location = `${match[1]} ${match[2]}`;
                } else if (match[1]) {
                    location = match[1];
                } else {
                    location = match[0];
                }
                
                location = location.trim();
                
                // Valider la longueur et exclure les résultats aberrants
                if (location.length >= 2 && location.length <= 100 && !location.includes('©') && !location.includes('@')) {
                    if (this.debug) {
                        console.log('✅ Location found:', location);
                    }
                    return location;
                }
            }
        }
        
        if (this.debug) {
            console.log('❌ No location detected');
        }
        return '';
    }
    
    /**
     * Extraction de l'expérience améliorée pour les formulations françaises
     */
    extractExperience(text) {
        if (this.debug) {
            console.log('💼 Enhanced experience extraction for French job requirements...');
        }
        
        const experienceRegexList = [
            // Patterns spécifiques français améliorés
            /exp[ée]rience\s*[:\-]?\s*((?:minimum|requis[e]?)?\s*\d+\s*(?:à\s*\d+\s*)?an[s]?[^\n]*)/i,
            /exp[ée]rience\s*[:\-]?\s*(minimum\s*[^\n]+)/i,
            /minimum\s*(\d+\s*(?:à\s*\d+\s*)?\s*an[s]?\s*(?:d[''']?exp[ée]rience)?[^\n]*)/i,
            /(\d+\s*(?:à\s*\d+\s*)?\s*an[s]?\s*d[''']?exp[ée]rience[^\n]*)/i,
            /(?:justifier|avoir|posséder)\s*(?:d[''']?)?\s*(?:au\s*)?minimum\s*(\d+\s*an[s]?[^\n]*)/i,
            /(?:justifier|avoir|posséder)\s*(?:d[''']?)?\s*(\d+\s*(?:à\s*\d+\s*)?\s*an[s]?\s*d[''']?exp[ée]rience[^\n]*)/i,
            
            // Patterns pour niveaux d'expérience
            /profil\s+(junior|débutant[e]?|confirm[ée]|senior|expert)[^\n]*/i,
            /niveau\s+(junior|débutant[e]?|confirm[ée]|senior|expert)[^\n]*/i,
            /candidat\s+(junior|débutant[e]?|confirm[ée]|senior|expert)[^\n]*/i,
            
            // Patterns pour expérience secteur spécifique
            /exp[ée]rience\s+(?:dans|en|sur)\s+([^\n]+)/i,
            /connaissance\s+(?:du|des|de)\s+([^\n]+)/i,
            
            // Pattern générique pour "X ans" avec contexte
            /(\d+\s*(?:à\s*\d+\s*)?\s*an[s]?)\s*(?:minimum|requis|souhaité|d[''']?exp[ée]rience|dans\s+le\s+domaine)?/i,
            
            // Patterns pour première expérience
            /(première\s+exp[ée]rience|d[ée]butant[e]?\s+accept[ée]|sans\s+exp[ée]rience)/i
        ];
        
        for (const regex of experienceRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                let experience = match[1].trim();
                
                // Valider et nettoyer l'expérience
                if (experience.length >= 3 && experience.length <= 200 && !experience.includes('©') && !experience.includes('@')) {
                    if (this.debug) {
                        console.log('✅ Experience found:', experience);
                    }
                    return experience;
                }
            }
        }
        
        if (this.debug) {
            console.log('❌ No experience detected');
        }
        return '';
    }
    
    extractCompany(text) {
        const companyRegexList = [
            /(?:société|entreprise|cabinet|groupe|association)\s*[:]?\s*([^\n.]+)/i,
            /(?:chez|pour)\s+([A-Z][A-Za-z\s&.-]+?)(?:\s|,|\.|\n)/,
            /\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)(?:\s+(?:recrute|recherche))/i
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
        const skillsList = [];
        
        // Chercher une section dédiée aux compétences
        const skillSectionRegexList = [
            /comp[ée]tences(?:\s+(?:requises|techniques|et\s+savoir-faire))?(?:\s*[:]?\s*)([^]*?)(?:\n\s*\n|$)/i,
            /savoir-faire(?:\s*[:]?\s*)([^]*?)(?:\n\s*\n|$)/i,
            /qualifications(?:\s*[:]?\s*)([^]*?)(?:\n\s*\n|$)/i,
            /outils?\s+(?:maitrisés?|utilisés?)(?:\s*[:]?\s*)([^]*?)(?:\n\s*\n|$)/i,
            /logiciels?\s+(?:maitrisés?|utilisés?)(?:\s*[:]?\s*)([^]*?)(?:\n\s*\n|$)/i
        ];
        
        let skillsSection = '';
        for (const regex of skillSectionRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                skillsSection = match[1].trim();
                break;
            }
        }
        
        // Technologies et outils spécifiques français
        const techSkills = [
            // Logiciels de gestion/paie français
            'ADP', 'Sage', 'Cegid', 'Silae', 'Paie Plus', 'Meta4', 'SAP HCM', 'SIRH',
            // Suite Office
            'Excel', 'Word', 'PowerPoint', 'Outlook', 'Access', 'SharePoint', 'Teams',
            // Technologies web
            'JavaScript', 'HTML', 'CSS', 'React', 'Vue.js', 'Angular', 'Node.js',
            'Python', 'Java', 'C#', 'PHP', 'Ruby', 'TypeScript',
            // Bases de données
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle',
            // Design
            'Photoshop', 'Illustrator', 'InDesign', 'Figma', 'Sketch', 'Canva',
            // CRM/ERP français
            'Salesforce', 'Zoho', 'HubSpot', 'Pipedrive',
            // Autres
            'Git', 'Docker', 'AWS', 'Azure', 'Google Analytics'
        ];
        
        // Ajouter les technologies trouvées
        techSkills.forEach(skill => {
            const regex = new RegExp(`\\b${skill}\\b`, 'i');
            if (text.match(regex)) {
                skillsList.push(skill);
            }
        });
        
        // Extraire des compétences de la section dédiée
        if (skillsSection) {
            // Chercher des listes à puces
            const bulletItems = skillsSection.match(/(?:^|[\n\r])\s*[-•*]\s*([^\n\r]+)/g);
            if (bulletItems) {
                bulletItems.forEach(item => {
                    const skill = item.replace(/^[\s\n\r]*[-•*]\s*/, '').trim();
                    if (skill && skill.length > 2 && skill.length < 100) {
                        skillsList.push(skill);
                    }
                });
            }
        }
        
        // Compétences transversales françaises
        const softSkills = [
            'autonomie', 'rigueur', 'organisation', 'communication',
            'travail en équipe', 'adaptabilité', 'sens du service',
            'gestion du stress', 'proactivité', 'diplomatie', 'polyvalence'
        ];
        
        softSkills.forEach(skill => {
            const regex = new RegExp(`\\b${skill}\\b`, 'i');
            if (text.match(regex)) {
                skillsList.push(skill);
            }
        });
        
        return [...new Set(skillsList)]; // Supprimer les doublons
    }
    
    extractEducation(text) {
        const educationRegexList = [
            // Patterns spécifiques français
            /formation\s*[:\-]?\s*([^\n.]+)/i,
            /diplôme\s*[:\-]?\s*([^\n.]+)/i,
            /qualification\s*[:\-]?\s*([^\n.]+)/i,
            /niveau\s*(?:d[''']?études?)?\s*[:\-]?\s*([^\n.]+)/i,
            
            // Patterns pour niveaux BAC
            /(bac\s*\+\s*\d+(?:\/\d+)?[^\n]*)/i,
            /(niveau\s+bac\s*\+?\s*\d*[^\n]*)/i,
            
            // Diplômes spécifiques
            /((?:BTS|DUT|Licence|Master|Doctorat|Ingénieur)[^\n]*)/i,
            /((?:CAP|BEP|Bac\s+Pro)[^\n]*)/i
        ];
        
        for (const regex of educationRegexList) {
            const match = text.match(regex);
            if (match) {
                const education = (match[1] || match[0]).trim();
                if (education.length > 3 && education.length < 200 && !education.includes('©')) {
                    return education;
                }
            }
        }
        
        return '';
    }
    
    extractSalary(text) {
        const salaryRegexList = [
            // Patterns spécifiques français
            /r[ée]mun[ée]ration\s*[:\-]?\s*([^\n.]+)/i,
            /salaire\s*(?:proposé|offert)?\s*[:\-]?\s*([^\n.]+)/i,
            /package\s*(?:salarial)?\s*[:\-]?\s*([^\n.]+)/i,
            
            // Patterns pour montants en K€
            /(\d+\s*k?€?\s*(?:brut|net)?\s*(?:\/|par)?\s*(?:an|année|mois))/i,
            /(?:à\s+partir\s+de|entre|de)\s*(\d+\s*k?€?[^\n]*)/i,
            
            // Patterns pour fourchettes
            /(\d+\s*(?:k?€?)?\s*(?:à|au?|et|-)?\s*\d+\s*k?€?\s*(?:brut|net)?[^\n]*)/i,
            
            // Pattern pour "selon profil"
            /(selon\s+(?:profil|expérience)[^\n]*)/i,
            /(à\s+négocier[^\n]*)/i
        ];
        
        for (const regex of salaryRegexList) {
            const match = text.match(regex);
            if (match) {
                const salary = (match[1] || match[0]).trim();
                if (salary.length > 2 && salary.length < 100 && !salary.includes('©')) {
                    return salary;
                }
            }
        }
        
        return '';
    }
    
    extractResponsibilities(text) {
        const respSectionRegexList = [
            /missions?\s+principales?\s*[:]?\s*([^]*?)(?:\n\s*\n|$)/i,
            /(?:responsabilit[ée]s|missions|tâches)(?:\s*[:]?\s*)([^]*?)(?:\n\s*\n|$)/i,
            /(?:vous\s+serez\s+chargé|vos\s+missions)([^]*?)(?:\n\s*\n|$)/i,
            /(?:descriptif|description)(?:\s+du\s+poste)?(?:\s*[:]?\s*)([^]*?)(?:\n\s*\n|$)/i
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
        
        // Si pas de liste à puces, découper par phrases
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
            /avantages\s*[:]?\s*([^]*?)(?:\n\s*\n|$)/i,
            /(?:bénéfices|nous\s+(?:vous\s+)?offrons|nous\s+proposons)(?:\s*[:]?\s*)([^]*?)(?:\n\s*\n|$)/i
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
        
        // Chercher des avantages spécifiques français
        const commonBenefits = [
            'télétravail', 'restaurant d\'entreprise', 'mutuelle', 'prévoyance',
            'congés', 'RTT', '13e mois', 'prime', 'tickets restaurant', 
            'transport', 'parking', 'formation', 'véhicule de fonction'
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
        
        return [...new Set(benefitList)]; // Supprimer les doublons
    }
}

// Créer une instance globale pour l'utiliser dans d'autres scripts
window.JobParserAPI = JobParserAPI;

console.log('✅ JobParserAPI v2.3 Enhanced chargé avec succès - Optimisé pour fiches françaises !');
