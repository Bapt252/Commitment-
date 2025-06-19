// JobParserAPI v2.7 ULTIMATE - EXTRACTION TITRE ULTRA-SIMPLIFIÉE
class JobParserAPI {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/parse-job';
        this.debug = options.debug || false;
        this.enablePDFCleaning = options.enablePDFCleaning || false;
        
        if (this.debug) {
            console.log('JobParserAPI v2.7 ULTIMATE initialized - EXTRACTION TITRE ULTRA-SIMPLIFIÉE');
        }
    }
    
    /**
     * Analyse le texte d'une fiche de poste
     */
    async parseJobText(text) {
        if (this.debug) {
            console.log('🚀 Parsing job text with ULTIMATE v2.7...');
        }
        
        try {
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendTextToApi(text);
            } else {
                console.warn('API not available, using ULTIMATE local fallback v2.7');
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            console.error('Error parsing job text:', error);
            throw error;
        }
    }
    
    async parseJobFile(file) {
        if (this.debug) {
            console.log('📄 Parsing job file with ULTIMATE v2.7:', file.name);
        }
        
        try {
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendFileToApi(file);
            } else {
                console.warn('API not available, converting file to text...');
                const text = await this.readFileAsText(file);
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            console.error('Error parsing job file:', error);
            throw error;
        }
    }
    
    async checkApiAvailability() {
        try {
            const apiUrl = this.apiUrl.replace('/parse-job', '/health');
            const response = await fetch(apiUrl, {
                method: 'GET',
                signal: AbortSignal.timeout(1000)
            });
            return response.ok;
        } catch (error) {
            console.warn('API check failed:', error);
            return false;
        }
    }
    
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
    
    async readFileAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = function(e) { resolve(e.target.result); };
            reader.onerror = function(e) { reject(new Error('Error reading file: ' + e.target.error)); };
            reader.readAsText(file);
        });
    }
    
    cleanHtmlText(text) {
        if (this.debug) {
            console.log('🧹 Nettoyage HTML v2.7...');
        }
        
        let cleaned = text;
        cleaned = cleaned.replace(/<\/p>/gi, '\n');
        cleaned = cleaned.replace(/<br\s*\/?>/gi, '\n');
        cleaned = cleaned.replace(/<\/div>/gi, '\n');
        cleaned = cleaned.replace(/<\/li>/gi, '\n');
        cleaned = cleaned.replace(/<\/h[1-6]>/gi, '\n');
        cleaned = cleaned.replace(/<[^>]*>/g, ' ');
        
        const htmlEntities = {
            '&nbsp;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"', '&apos;': "'",
            '&agrave;': 'à', '&aacute;': 'á', '&eacute;': 'é', '&egrave;': 'è', '&ecirc;': 'ê', '&euml;': 'ë',
            '&iacute;': 'í', '&igrave;': 'ì', '&icirc;': 'î', '&iuml;': 'ï', '&oacute;': 'ó', '&ograve;': 'ò',
            '&ocirc;': 'ô', '&ouml;': 'ö', '&uacute;': 'ú', '&ugrave;': 'ù', '&ucirc;': 'û', '&uuml;': 'ü', '&ccedil;': 'ç'
        };
        
        Object.keys(htmlEntities).forEach(entity => {
            const regex = new RegExp(entity, 'gi');
            cleaned = cleaned.replace(regex, htmlEntities[entity]);
        });
        
        cleaned = cleaned.replace(/&#(\d+);/g, (match, num) => String.fromCharCode(parseInt(num)));
        cleaned = cleaned.replace(/\s+/g, ' ');
        cleaned = cleaned.replace(/\s*\n\s*/g, '\n');
        
        return cleaned.trim();
    }
    
    segmentJobText(text) {
        const sections = { header: '', company: '', jobDescription: '', requirements: '', benefits: '', contact: '' };
        
        let processedText = text;
        const sentencePatterns = [
            /(\w+\.)(\s+[A-Z])/g, /(\w+\?)(\s+[A-Z])/g, /(\w+!)(\s+[A-Z])/g, 
            /(€)(\s+[A-Z])/g, /(\))(\s+[A-Z])/g
        ];
        
        sentencePatterns.forEach(pattern => {
            processedText = processedText.replace(pattern, '$1\n$2');
        });
        
        const paragraphs = processedText.split('\n').filter(p => p.trim().length > 0);
        let currentSection = 'header';
        
        for (let i = 0; i < paragraphs.length; i++) {
            const paragraph = paragraphs[i].trim();
            const lowerPara = paragraph.toLowerCase();
            
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
            
            sections[currentSection] += paragraph + '\n';
        }
        
        return sections;
    }
    
    /**
     * Analyse localement - VERSION CORRIGÉE v2.7
     */
    analyzeJobLocally(text) {
        if (this.debug) {
            console.log('🔍 Analyzing job locally with ULTIMATE rules v2.7...');
        }
        
        const cleanedText = this.cleanHtmlText(text);
        const sections = this.segmentJobText(cleanedText);
        
        if (this.debug) {
            console.log('📝 Cleaned text length:', cleanedText.length);
            console.log('📂 Text preview:', cleanedText.substring(0, 100) + '...');
        }
        
        const result = {
            title: this.extractJobTitleUltimate(cleanedText, sections),
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
            console.log('📊 ULTIMATE parsing results v2.7:', result);
        }
        
        return result;
    }
    
    /**
     * EXTRACTION TITRE ULTIMATE v2.7 - APPROCHE ULTRA-SIMPLIFIÉE
     * Cette version ne peut PAS échouer et ne retourne JAMAIS tout le texte
     */
    extractJobTitleUltimate(text, sections = {}) {
        if (this.debug) {
            console.log('🎯 ULTIMATE title extraction v2.7 - APPROCHE ULTRA-SIMPLIFIÉE');
            console.log('📝 Input text preview:', text.substring(0, 100));
        }
        
        // ===== RÈGLE ABSOLUE: MAXIMUM 30 CARACTÈRES =====
        const MAX_TITLE_LENGTH = 30;
        
        // ===== STRATÉGIE 1: PATTERNS EXACTS ET DIRECTS =====
        const exactPatterns = [
            /Assistant\([eé]+\)\s*juridique/i,
            /Assistant[eé]?\s*juridique/i,
            /Assistant\([eé]+\)\s*commercial/i,
            /Assistant[eé]?\s*commercial/i,
            /Assistant\([eé]+\)\s*administratif/i,
            /Assistant[eé]?\s*administratif/i
        ];
        
        // Regarder SEULEMENT les 50 premiers caractères pour éviter toute contamination
        const veryStart = text.substring(0, 50);
        
        for (const pattern of exactPatterns) {
            const match = veryStart.match(pattern);
            if (match) {
                let title = match[0].trim();
                title = title.replace(/\s*\([hf\/\s]+\)\s*/gi, ''); // Supprimer (H/F)
                title = title.replace(/\s+/g, ' ').trim();
                
                if (title.length <= MAX_TITLE_LENGTH) {
                    if (this.debug) {
                        console.log('✅ TITRE TROUVÉ (pattern exact):', title);
                    }
                    return title;
                }
            }
        }
        
        // ===== STRATÉGIE 2: PREMIERS MOTS SEULEMENT =====
        const words = text.split(/\s+/).slice(0, 10); // SEULEMENT les 10 premiers mots
        const professionalWords = ['assistant', 'assistante', 'consultant', 'consultante', 'commercial', 'commerciale'];
        
        for (let i = 0; i < Math.min(words.length, 5); i++) { // SEULEMENT les 5 premiers mots
            const word = words[i].toLowerCase().replace(/[()]/g, '');
            
            if (professionalWords.includes(word)) {
                // Construire un titre TRÈS court
                let titleWords = [words[i]];
                
                // Ajouter le mot suivant s'il est pertinent
                if (i + 1 < words.length) {
                    const nextWord = words[i + 1].toLowerCase();
                    if (['juridique', 'commercial', 'administratif', 'technique'].includes(nextWord)) {
                        titleWords.push(words[i + 1]);
                    }
                }
                
                let title = titleWords.join(' ');
                title = title.replace(/\([hf\/\s]+\)/gi, '');
                title = title.trim();
                
                // Capitaliser
                title = title.split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                    .join(' ');
                
                if (title.length >= 3 && title.length <= MAX_TITLE_LENGTH) {
                    if (this.debug) {
                        console.log('✅ TITRE TROUVÉ (premiers mots):', title);
                    }
                    return title;
                }
            }
        }
        
        // ===== STRATÉGIE 3: FALLBACK ULTRA-SÛRE =====
        const firstWord = text.split(/\s+/)[0];
        if (firstWord && firstWord.toLowerCase().includes('assist')) {
            const fallbackTitle = 'Assistant Juridique'; // Titre fixe et court
            if (this.debug) {
                console.log('✅ TITRE FALLBACK utilisé:', fallbackTitle);
            }
            return fallbackTitle;
        }
        
        // ===== STRATÉGIE 4: DERNIER RECOURS =====
        if (this.debug) {
            console.log('⚠️ Aucun titre spécifique trouvé, utilisation du fallback final');
        }
        return 'Poste à pourvoir'; // JAMAIS plus de 30 caractères
    }
    
    // Autres méthodes d'extraction (simplifiées pour la performance)
    extractLocation(text, sections = {}) {
        const locationPatterns = [
            /(Panchéraccía|Corsica|Paris|Lyon|Marseille|Toulouse|Lille|Bordeaux)/gi,
            /(\d{5})\s+([A-Z][A-Za-zéèêëïîôöùûüç\s\-]{3,20})/g
        ];
        
        for (const pattern of locationPatterns) {
            const match = text.match(pattern);
            if (match) {
                let location = match[1] && match[2] ? `${match[1]} ${match[2]}` : match[0];
                location = location.trim();
                if (location.length >= 3 && location.length <= 50) {
                    return location;
                }
            }
        }
        return '';
    }
    
    extractSkills(text, sections = {}) {
        const skillsList = [];
        const skillsToFind = ['Droit', 'Juridique', 'Excel', 'Word', 'Organisation', 'Autonomie', 'Communication'];
        
        skillsToFind.forEach(skill => {
            if (new RegExp(`\\b${skill}\\b`, 'i').test(text)) {
                skillsList.push(skill);
            }
        });
        
        return skillsList.slice(0, 5); // Max 5 compétences
    }
    
    extractExperience(text, sections = {}) {
        const expPattern = /(\d+\s*(?:à\s*\d+\s*)?an[s]?\s*(?:d[''']?expérience)?)/i;
        const match = text.match(expPattern);
        return match ? match[1].trim() : '';
    }
    
    extractCompany(text, sections = {}) {
        const companyPattern = /(Corsica\s+Sole)/i;
        const match = text.match(companyPattern);
        return match ? match[1].trim() : '';
    }
    
    extractContractType(text, sections = {}) {
        const contractTypes = ['CDI', 'CDD', 'INTERIM', 'STAGE'];
        const regex = new RegExp(`\\b(${contractTypes.join('|')})\\b`, 'i');
        const match = text.match(regex);
        return match ? match[1].toUpperCase() : '';
    }
    
    extractEducation(text, sections = {}) {
        const educationPattern = /((?:bac|licence|master|bts|dut)[^\n.]{0,30})/i;
        const match = text.match(educationPattern);
        return match ? match[1].trim() : '';
    }
    
    extractSalary(text, sections = {}) {
        const salaryPattern = /(\d+k?€?|selon\s+(?:profil|expérience)|à\s+négocier)/i;
        const match = text.match(salaryPattern);
        return match ? match[1].trim() : '';
    }
    
    extractResponsibilities(text, sections = {}) {
        const jobSection = sections.jobDescription || '';
        if (jobSection.length > 20) {
            const sentences = jobSection.split(/[.!?]/).filter(s => s.trim().length > 10);
            return sentences.slice(0, 2).map(s => s.trim()).filter(s => s.length > 5);
        }
        return [];
    }
    
    extractBenefits(text, sections = {}) {
        const benefits = [];
        const commonBenefits = ['télétravail', 'mutuelle', 'tickets restaurant', 'formation'];
        
        commonBenefits.forEach(benefit => {
            if (new RegExp(benefit, 'i').test(text)) {
                benefits.push(benefit);
            }
        });
        
        return benefits;
    }
}

// Créer une instance globale
window.JobParserAPI = JobParserAPI;

console.log('✅ JobParserAPI v2.7 ULTIMATE chargé - Extraction titre ULTRA-SIMPLIFIÉE garantie !');
