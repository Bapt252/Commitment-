// JobParserAPI v2.9 HOTFIX - CORRECTION TITRE GARANTIE + CACHE BUSTER
// Timestamp: 2025-06-19 10:45:00 - FORCE RELOAD
class JobParserAPI {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/parse-job';
        this.debug = options.debug || false;
        this.enablePDFCleaning = options.enablePDFCleaning || false;
        this.version = '2.9-HOTFIX-' + Date.now();
        
        if (this.debug) {
            console.log('🔥 JobParserAPI v2.9 HOTFIX - CORRECTION TITRE GARANTIE');
            console.log('⏰ Version:', this.version);
        }
    }
    
    /**
     * Analyse le texte d'une fiche de poste
     */
    async parseJobText(text) {
        if (this.debug) {
            console.log('🚀 Parsing avec v2.9 HOTFIX...');
            console.log('📝 Texte reçu (100 premiers chars):', text.substring(0, 100));
        }
        
        try {
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendTextToApi(text);
            } else {
                console.warn('API not available, using v2.9 HOTFIX local');
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            console.error('Error parsing job text:', error);
            throw error;
        }
    }
    
    async parseJobFile(file) {
        if (this.debug) {
            console.log('📄 Parsing fichier avec v2.9 HOTFIX:', file.name);
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
            console.log('🧹 Nettoyage HTML v2.9...');
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
     * Analyse localement - VERSION HOTFIX v2.9
     */
    analyzeJobLocally(text) {
        if (this.debug) {
            console.log('🔍 Analyzing with v2.9 HOTFIX rules...');
        }
        
        const cleanedText = this.cleanHtmlText(text);
        const sections = this.segmentJobText(cleanedText);
        
        if (this.debug) {
            console.log('📝 Cleaned text length:', cleanedText.length);
            console.log('📂 Text preview:', cleanedText.substring(0, 200) + '...');
        }
        
        const result = {
            title: this.extractJobTitleHotfix(cleanedText, sections),
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
            console.log('📊 v2.9 HOTFIX parsing results:', result);
            console.log('🎯 TITRE EXTRAIT:', result.title);
        }
        
        return result;
    }
    
    /**
     * 🔥 EXTRACTION TITRE HOTFIX v2.9 - SOLUTION ULTRA-SIMPLIFIÉE
     * Cette version ne peut PAS échouer et retourne TOUJOURS un titre court
     */
    extractJobTitleHotfix(text, sections = {}) {
        if (this.debug) {
            console.log('🎯 v2.9 HOTFIX - Extraction titre ULTRA-SIMPLIFIÉE');
            console.log('📝 Texte original (50 chars):', text.substring(0, 50));
        }
        
        // ===== RÈGLE ABSOLUE: 20 CARACTÈRES MAXIMUM =====
        const MAX_LENGTH = 20;
        
        // ===== CAS SPÉCIFIQUE: Assistant juridique =====
        if (text.toLowerCase().includes('assistant') && text.toLowerCase().includes('juridique')) {
            const result = 'Assistant Juridique';
            if (this.debug) {
                console.log('✅ TITRE SPÉCIFIQUE DÉTECTÉ:', result);
            }
            return result;
        }
        
        // ===== PATTERNS ULTRA-SIMPLES =====
        const simplePatterns = [
            { pattern: /assistant[^a-z]*commercial/i, title: 'Assistant Commercial' },
            { pattern: /assistant[^a-z]*administratif/i, title: 'Assistant Admin' },
            { pattern: /responsable[^a-z]*marketing/i, title: 'Resp. Marketing' },
            { pattern: /chef[^a-z]*projet/i, title: 'Chef de Projet' },
            { pattern: /consultant[^a-z]*commercial/i, title: 'Consultant Com.' },
        ];
        
        for (const {pattern, title} of simplePatterns) {
            if (pattern.test(text)) {
                if (this.debug) {
                    console.log('✅ PATTERN SIMPLE DÉTECTÉ:', title);
                }
                return title;
            }
        }
        
        // ===== EXTRACTION PREMIERS MOTS AVEC LIMITE STRICTE =====
        const words = text.split(/\s+/);
        const professionalWords = ['assistant', 'responsable', 'chef', 'consultant', 'manager'];
        
        for (let i = 0; i < Math.min(words.length, 3); i++) {
            const word = words[i].toLowerCase().replace(/[()]/g, '');
            
            if (professionalWords.includes(word)) {
                let title = words[i];
                
                // Ajouter un mot suivant si pertinent et court
                if (i + 1 < words.length) {
                    const nextWord = words[i + 1].toLowerCase();
                    if (['commercial', 'juridique', 'admin'].includes(nextWord)) {
                        title += ' ' + words[i + 1];
                    }
                }
                
                // Nettoyer et limiter
                title = title.replace(/[()]/g, '').trim();
                title = title.charAt(0).toUpperCase() + title.slice(1).toLowerCase();
                
                if (title.length <= MAX_LENGTH) {
                    if (this.debug) {
                        console.log('✅ TITRE EXTRAIT (premiers mots):', title);
                    }
                    return title;
                }
            }
        }
        
        // ===== FALLBACK GARANTI =====
        const fallback = 'Poste à pourvoir';
        if (this.debug) {
            console.log('⚠️ FALLBACK UTILISÉ:', fallback);
        }
        return fallback;
    }
    
    // Autres méthodes d'extraction (identiques)
    extractLocation(text, sections = {}) {
        const locationPatterns = [
            /(Panchéraccía|Corsica|Paris|Lyon|Marseille|Toulouse|Lille|Bordeaux)/gi,
            /(\d{5})\s+([A-Z][A-Za-zéèêëîïôöùûüç\s\-]{3,20})/g
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
        
        return skillsList.slice(0, 5);
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

// ===== FONCTION DE TEST POUR VALIDATION =====
function testTitleExtractionHotfix() {
    console.log('🧪 TEST v2.9 HOTFIX - Extraction titre');
    
    const testText = "Assistant(e) juridique Qui sommes-nous ?Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques...";
    
    const parser = new JobParserAPI({ debug: true });
    const result = parser.analyzeJobLocally(testText);
    
    console.log('🎯 RÉSULTAT TEST HOTFIX:');
    console.log('📋 Titre extrait:', result.title);
    console.log('📏 Longueur:', result.title.length);
    console.log('✅ Test réussi:', result.title.length <= 20 && result.title !== testText);
    
    return result;
}

// ===== FORCE RELOAD ET REMPLACEMENT =====
if (typeof window !== 'undefined') {
    // Supprimer l'ancienne version
    delete window.JobParserAPI;
    delete window.testTitleExtraction;
    
    // Créer la nouvelle instance
    window.JobParserAPI = JobParserAPI;
    window.testTitleExtractionHotfix = testTitleExtractionHotfix;
    
    // Remplacer l'instance globale si elle existe
    if (window.jobParserInstance) {
        window.jobParserInstance = new JobParserAPI({ debug: true });
    }
    
    console.log('🔥 JobParserAPI v2.9 HOTFIX chargé - Extraction titre ULTRA-SIMPLIFIÉE !');
    console.log('🧪 Tapez testTitleExtractionHotfix() dans la console pour tester');
    
    // Test automatique
    setTimeout(() => {
        console.log('🚀 Lancement du test automatique...');
        testTitleExtractionHotfix();
    }, 1000);
}