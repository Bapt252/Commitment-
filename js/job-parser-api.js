// JobParserAPI v2.4 - Version corrigée avec algorithme d'extraction amélioré
class JobParserAPI {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/parse-job';
        this.debug = options.debug || false;
        this.enablePDFCleaning = options.enablePDFCleaning || false;
        
        if (this.debug) {
            console.log('JobParserAPI v2.4 Enhanced initialized with options:', options);
        }
    }
    
    /**
     * Analyse le texte d'une fiche de poste
     * @param {string} text - Le texte de la fiche de poste
     * @returns {Promise<Object>} - Les résultats de l'analyse
     */
    async parseJobText(text) {
        if (this.debug) {
            console.log('🚀 Parsing job text with enhanced v2.4...');
        }
        
        try {
            // Vérifier d'abord si on peut utiliser l'API
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendTextToApi(text);
            } else {
                console.warn('API not available, using enhanced local fallback v2.4');
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
            console.log('📄 Parsing job file with enhanced v2.4:', file.name);
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
     * Version améliorée v2.4 avec meilleur traitement des entités HTML françaises
     */
    cleanHtmlText(text) {
        if (this.debug) {
            console.log('🧹 Nettoyage HTML avancé v2.4...');
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
     * Segmente le texte en sections logiques pour améliorer l'extraction
     */
    segmentJobText(text) {
        const sections = {
            header: '',
            company: '',
            jobDescription: '',
            requirements: '',
            benefits: '',
            contact: ''
        };
        
        // Diviser le texte en paragraphes
        const paragraphs = text.split('\n').filter(p => p.trim().length > 0);
        
        let currentSection = 'header';
        
        for (let i = 0; i < paragraphs.length; i++) {
            const paragraph = paragraphs[i].trim();
            const lowerPara = paragraph.toLowerCase();
            
            // Identifier la section actuelle basée sur des mots-clés
            if (lowerPara.includes('qui sommes-nous') || lowerPara.includes('présentation') || 
                lowerPara.includes('notre entreprise') || lowerPara.includes('société')) {
                currentSection = 'company';
            } else if (lowerPara.includes('mission') || lowerPara.includes('responsabilité') || 
                      lowerPara.includes('vous serez chargé') || lowerPara.includes('poste')) {
                currentSection = 'jobDescription';
            } else if (lowerPara.includes('profil') || lowerPara.includes('compétence') || 
                      lowerPara.includes('expérience') || lowerPara.includes('formation') ||
                      lowerPara.includes('qualification')) {
                currentSection = 'requirements';
            } else if (lowerPara.includes('avantage') || lowerPara.includes('nous offrons') || 
                      lowerPara.includes('package') || lowerPara.includes('bénéfice')) {
                currentSection = 'benefits';
            } else if (lowerPara.includes('contact') || lowerPara.includes('candidature') || 
                      lowerPara.includes('@') || lowerPara.includes('tel') || lowerPara.includes('fax')) {
                currentSection = 'contact';
            }
            
            // Ajouter le paragraphe à la section appropriée
            sections[currentSection] += paragraph + '\n';
        }
        
        return sections;
    }
    
    /**
     * Analyse localement un texte de fiche de poste (fallback amélioré v2.4)
     * @param {string} text - Le texte à analyser
     * @returns {Object} - Les résultats de l'analyse
     */
    analyzeJobLocally(text) {
        if (this.debug) {
            console.log('🔍 Analyzing job locally with enhanced rules v2.4...');
        }
        
        // Nettoyer le HTML d'abord
        const cleanedText = this.cleanHtmlText(text);
        
        // Segmenter le texte en sections
        const sections = this.segmentJobText(cleanedText);
        
        if (this.debug) {
            console.log('📝 Cleaned text length:', cleanedText.length);
            console.log('📂 Sections identified:', Object.keys(sections).filter(key => sections[key].length > 0));
        }
        
        const result = {
            title: this.extractJobTitle(cleanedText, sections),
            company: this.extractCompany(cleanedText, sections),
            location: this.extractLocation(cleanedText, sections),
            contract_type: this.extractContractType(cleanedText, sections),
            skills: this.extractSkills(cleanedText, sections),
            experience: this.extractExperience(cleanedText, sections),
            education: this.extractEducation(cleanedText, sections),
            salary: this.extractSalary(cleanedText, sections),
            responsibilities: this.extractResponsibilities(cleanedText, sections),
            benefits: this.extractBenefits(cleanedText, sections)
        };
        
        if (this.debug) {
            console.log('📊 Enhanced parsing results v2.4:', result);
        }
        
        return result;
    }
    
    // Méthodes d'extraction améliorées v2.4
    
    /**
     * Extraction du titre de poste améliorée - VERSION CORRIGÉE
     */
    extractJobTitle(text, sections = {}) {
        if (this.debug) {
            console.log('🎯 Enhanced title extraction v2.4...');
        }
        
        // Chercher d'abord dans les 3 premières lignes
        const firstLines = text.split('\n').slice(0, 3);
        
        for (const line of firstLines) {
            const cleanLine = line.trim();
            
            // Ignorer les lignes trop longues (probablement pas des titres)
            if (cleanLine.length > 80) continue;
            
            // Ignorer les lignes qui ressemblent à des descriptions d'entreprise
            if (cleanLine.toLowerCase().includes('qui sommes-nous') || 
                cleanLine.toLowerCase().includes('société') ||
                cleanLine.toLowerCase().includes('entreprise') ||
                cleanLine.toLowerCase().includes('pme') ||
                cleanLine.length < 5) continue;
            
            // Patterns pour identifier un titre de poste
            const jobTitlePatterns = [
                /assistant[e]?\s*\([hf\/]+\)?\s*(juridique|commercial|administratif|rh)/i,
                /assistant[e]?\s*(juridique|commercial|administratif|rh)/i,
                /développeur|développeuse/i,
                /commercial[e]?/i,
                /consultant[e]?/i,
                /manager|responsable|chef|directeur/i,
                /technicien[ne]?|ingénieur[e]?/i,
                /gestionnaire|coordinateur[trice]?/i
            ];
            
            for (const pattern of jobTitlePatterns) {
                if (pattern.test(cleanLine)) {
                    // Nettoyer le titre trouvé
                    let title = cleanLine;
                    title = title.replace(/\s*\([hf\/\s]+\)\s*/gi, ''); // Supprimer (H/F)
                    title = title.replace(/\s*-.*$/i, ''); // Supprimer ce qui vient après un tiret
                    title = title.trim();
                    
                    if (title.length >= 5 && title.length <= 60) {
                        if (this.debug) {
                            console.log('✅ Title found:', title);
                        }
                        return title;
                    }
                }
            }
        }
        
        // Fallback : chercher des patterns spécifiques
        const titleRegexList = [
            /(?:poste|offre|intitulé)\s*[:\-]?\s*([^\n]{5,60})/i,
            /(?:recherche|recrute)\s*(?:un[e]?)?\s*([^\n]{5,60})/i,
        ];
        
        for (const regex of titleRegexList) {
            const match = text.match(regex);
            if (match && match[1]) {
                let title = match[1].trim();
                if (title.length >= 5 && title.length <= 60) {
                    if (this.debug) {
                        console.log('✅ Title found via pattern:', title);
                    }
                    return title;
                }
            }
        }
        
        if (this.debug) {
            console.log('❌ No clear title detected');
        }
        return 'Poste à pourvoir';
    }
    
    /**
     * Extraction du lieu améliorée pour les adresses françaises
     */
    extractLocation(text, sections = {}) {
        if (this.debug) {
            console.log('📍 Enhanced location extraction v2.4...');
        }
        
        const locationRegexList = [
            // Codes postaux français avec ville
            /(\d{5})\s+([A-Z][A-Za-zéèêëïîôöùûüç\s\-]+)/g,
            
            // Patterns spécifiques
            /(?:lieu|localisation|adresse|situé|basé|implanté)\s*[:\-]?\s*([^\n.,]{3,50})/i,
            
            // Villes françaises connues
            /(Paris|Lyon|Marseille|Toulouse|Lille|Bordeaux|Nantes|Strasbourg|Rennes|Montpellier|Nice|Grenoble|Bastia)(?:\s+\d+)?/gi,
            
            // Pattern dans les coordonnées de contact
            /(?:\d{5}\s+)?([A-Z][A-Za-zéèêëïîôöùûüç\s\-]+)(?:\s*,\s*FRANCE)?/g
        ];
        
        // Chercher dans la section contact en priorité
        const contactSection = sections.contact || '';
        
        for (const regex of locationRegexList) {
            const matches = (contactSection + '\n' + text).matchAll(regex);
            
            for (const match of matches) {
                let location = '';
                
                if (match[1] && match[2]) {
                    // Code postal + ville
                    location = `${match[1]} ${match[2]}`.trim();
                } else if (match[1]) {
                    location = match[1].trim();
                } else {
                    location = match[0].trim();
                }
                
                // Valider et nettoyer
                if (location.length >= 3 && location.length <= 50 && 
                    !location.includes('www') && !location.includes('@')) {
                    
                    // Nettoyer la localisation
                    location = location.replace(/^\w+:\s*/, ''); // Supprimer "Lieu: "
                    location = location.replace(/\s*,\s*FRANCE\s*$/i, ''); // Supprimer ", FRANCE"
                    
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
     * Extraction des compétences améliorée
     */
    extractSkills(text, sections = {}) {
        if (this.debug) {
            console.log('💻 Enhanced skills extraction v2.4...');
        }
        
        const skillsList = [];
        
        // Utiliser principalement la section requirements
        const searchText = sections.requirements || text;
        
        // Technologies et outils spécifiques
        const techSkills = [
            // Juridique
            'Droit', 'Juridique', 'Contrats', 'Contentieux', 'Droit commercial', 'Droit social',
            
            // Logiciels courants
            'Excel', 'Word', 'PowerPoint', 'Outlook', 'SAP', 'Sage', 'Cegid',
            
            // Technologies web
            'JavaScript', 'HTML', 'CSS', 'React', 'Vue.js', 'Angular', 'Node.js', 'Python', 'Java', 'PHP',
            
            // Compétences transversales
            'Autonomie', 'Rigueur', 'Organisation', 'Communication', 'Travail en équipe', 'Adaptabilité',
            'Gestion du stress', 'Proactivité', 'Diplomatie', 'Polyvalence', 'Synthèse', 'Analyse'
        ];
        
        // Chercher chaque compétence dans le texte
        techSkills.forEach(skill => {
            const regex = new RegExp(`\\b${skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i');
            if (regex.test(searchText)) {
                skillsList.push(skill);
            }
        });
        
        // Chercher des listes à puces de compétences
        const bulletPointMatches = searchText.match(/(?:^|\n)\s*[-•*]\s*([^\n]{3,50})/g);
        if (bulletPointMatches) {
            bulletPointMatches.forEach(item => {
                const skill = item.replace(/^[\s\n]*[-•*]\s*/, '').trim();
                if (skill.length > 2 && skill.length < 50 && !skillsList.includes(skill)) {
                    skillsList.push(skill);
                }
            });
        }
        
        if (this.debug && skillsList.length > 0) {
            console.log('✅ Skills found:', skillsList);
        }
        
        return skillsList.slice(0, 10); // Limiter à 10 compétences max
    }
    
    /**
     * Extraction de l'expérience améliorée
     */
    extractExperience(text, sections = {}) {
        if (this.debug) {
            console.log('💼 Enhanced experience extraction v2.4...');
        }
        
        const searchText = sections.requirements || text;
        
        const experienceRegexList = [
            // Patterns français spécifiques
            /((?:minimum|au moins|plus de|entre)?\s*\d+\s*(?:à\s*\d+\s*)?an[s]?\s*(?:d[''']?expérience|minimum)?[^\n]*)/i,
            /(expérience\s+(?:de|d[''']?)\s*\d+\s*(?:à\s*\d+\s*)?\s*an[s]?[^\n]*)/i,
            /(profil\s+(?:junior|senior|confirmé|débutant)[^\n]*)/i,
            /(première\s+expérience|débutant\s+accepté|sans\s+expérience)/i
        ];
        
        for (const regex of experienceRegexList) {
            const match = searchText.match(regex);
            if (match && match[1]) {
                let experience = match[1].trim();
                
                if (experience.length >= 5 && experience.length <= 100) {
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
    
    // Conserver les autres méthodes d'extraction existantes mais simplifiées
    extractCompany(text, sections = {}) {
        const companySection = sections.company || text;
        
        const companyRegexList = [
            /(?:société|entreprise|groupe)\s*[:]?\s*([^\n.]{3,50})/i,
            /([A-Z][A-Za-z\s&.-]{3,30})(?:\s+est\s+)/i
        ];
        
        for (const regex of companyRegexList) {
            const match = companySection.match(regex);
            if (match && match[1] && match[1].trim().length > 2) {
                return match[1].trim();
            }
        }
        
        return '';
    }
    
    extractContractType(text, sections = {}) {
        const contractTypes = ['CDI', 'CDD', 'INTERIM', 'STAGE', 'ALTERNANCE', 'APPRENTISSAGE', 'FREELANCE'];
        const regex = new RegExp(`\\b(${contractTypes.join('|')})\\b`, 'i');
        const match = text.match(regex);
        return match ? match[1].toUpperCase() : '';
    }
    
    extractEducation(text, sections = {}) {
        const searchText = sections.requirements || text;
        const educationRegex = /((?:bac|licence|master|ingénieur|bts|dut)[^\n.]{0,50})/i;
        const match = searchText.match(educationRegex);
        return match ? match[1].trim() : '';
    }
    
    extractSalary(text, sections = {}) {
        const salaryRegex = /((?:\d+k?€?|selon\s+(?:profil|expérience)|à\s+négocier)[^\n.]{0,50})/i;
        const match = text.match(salaryRegex);
        return match ? match[1].trim() : '';
    }
    
    extractResponsibilities(text, sections = {}) {
        const jobSection = sections.jobDescription || '';
        if (jobSection.length > 20) {
            // Prendre les premières phrases significatives
            const sentences = jobSection.split(/[.!?]/).filter(s => s.trim().length > 10);
            return sentences.slice(0, 3).map(s => s.trim()).filter(s => s.length > 5);
        }
        return [];
    }
    
    extractBenefits(text, sections = {}) {
        const benefitsSection = sections.benefits || '';
        if (benefitsSection.length > 20) {
            const benefits = [];
            const commonBenefits = ['télétravail', 'mutuelle', 'tickets restaurant', 'formation', 'rtt'];
            
            commonBenefits.forEach(benefit => {
                if (new RegExp(benefit, 'i').test(benefitsSection)) {
                    benefits.push(benefit);
                }
            });
            
            return benefits;
        }
        return [];
    }
}

// Créer une instance globale pour l'utiliser dans d'autres scripts
window.JobParserAPI = JobParserAPI;

console.log('✅ JobParserAPI v2.4 Enhanced chargé avec succès - Algorithme d\'extraction amélioré !');
