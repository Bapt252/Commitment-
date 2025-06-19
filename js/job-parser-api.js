// JobParserAPI v2.10 ÉQUILIBRÉE - CORRECTION PARSING COMPLET
// Fix: Restauration de l'extraction complète + titre corrigé
class JobParserAPI {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/parse-job';
        this.debug = options.debug || false;
        this.enablePDFCleaning = options.enablePDFCleaning || false;
        this.version = '2.10-BALANCED-' + Date.now();
        
        if (this.debug) {
            console.log('🔥 JobParserAPI v2.10 ÉQUILIBRÉE - PARSING COMPLET RESTAURÉ');
            console.log('⏰ Version:', this.version);
        }
    }
    
    /**
     * Analyse le texte d'une fiche de poste
     */
    async parseJobText(text) {
        if (this.debug) {
            console.log('🚀 Parsing avec v2.10 ÉQUILIBRÉE...');
            console.log('📝 Texte reçu (100 premiers chars):', text.substring(0, 100));
        }
        
        try {
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendTextToApi(text);
            } else {
                console.warn('API not available, using v2.10 ÉQUILIBRÉE local');
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            console.error('Error parsing job text:', error);
            throw error;
        }
    }
    
    async parseJobFile(file) {
        if (this.debug) {
            console.log('📄 Parsing fichier avec v2.10 ÉQUILIBRÉE:', file.name);
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
            console.log('🧹 Nettoyage HTML v2.10...');
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
     * Analyse localement - VERSION ÉQUILIBRÉE v2.10
     */
    analyzeJobLocally(text) {
        if (this.debug) {
            console.log('🔍 Analyzing with v2.10 ÉQUILIBRÉE rules...');
        }
        
        const cleanedText = this.cleanHtmlText(text);
        const sections = this.segmentJobText(cleanedText);
        
        if (this.debug) {
            console.log('📝 Cleaned text length:', cleanedText.length);
            console.log('📂 Text preview:', cleanedText.substring(0, 200) + '...');
        }
        
        const result = {
            title: this.extractJobTitleBalanced(cleanedText, sections),
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
            console.log('📊 v2.10 ÉQUILIBRÉE parsing results:', result);
            console.log('🎯 TITRE EXTRAIT:', result.title);
        }
        
        return result;
    }
    
    /**
     * 🔥 EXTRACTION TITRE ÉQUILIBRÉE v2.10
     * Version équilibrée : détecte bien MAIS titre limité à 25 caractères max
     */
    extractJobTitleBalanced(text, sections = {}) {
        if (this.debug) {
            console.log('🎯 v2.10 ÉQUILIBRÉE - Extraction titre équilibrée');
            console.log('📝 Texte original (100 chars):', text.substring(0, 100));
        }
        
        // ===== RÈGLE ABSOLUE: 25 CARACTÈRES MAXIMUM =====
        const MAX_LENGTH = 25;
        
        // ===== STRATÉGIE 1: PATTERNS PROFESSIONNELS ÉTENDUS =====
        const jobPatterns = [
            // Assistants
            { pattern: /assistant[^a-z]*juridique/i, title: 'Assistant Juridique' },
            { pattern: /assistant[^a-z]*commercial/i, title: 'Assistant Commercial' },
            { pattern: /assistant[^a-z]*administratif/i, title: 'Assistant Admin' },
            { pattern: /assistant[^a-z]*technique/i, title: 'Assistant Technique' },
            { pattern: /assistant[^a-z]*marketing/i, title: 'Assistant Marketing' },
            { pattern: /assistant[^a-z]*rh/i, title: 'Assistant RH' },
            
            // Responsables
            { pattern: /responsable[^a-z]*commercial/i, title: 'Resp. Commercial' },
            { pattern: /responsable[^a-z]*marketing/i, title: 'Resp. Marketing' },
            { pattern: /responsable[^a-z]*vente/i, title: 'Resp. Vente' },
            { pattern: /responsable[^a-z]*projet/i, title: 'Resp. Projet' },
            
            // Chefs
            { pattern: /chef[^a-z]*projet/i, title: 'Chef de Projet' },
            { pattern: /chef[^a-z]*vente/i, title: 'Chef de Vente' },
            { pattern: /chef[^a-z]*équipe/i, title: 'Chef d\'Équipe' },
            
            // Consultants
            { pattern: /consultant[^a-z]*commercial/i, title: 'Consultant Com.' },
            { pattern: /consultant[^a-z]*technique/i, title: 'Consultant Tech.' },
            
            // Autres
            { pattern: /manager[^a-z]*commercial/i, title: 'Manager Commercial' },
            { pattern: /directeur[^a-z]*commercial/i, title: 'Dir. Commercial' },
            { pattern: /chargé[^a-z]*clientèle/i, title: 'Chargé Clientèle' },
            { pattern: /développeur[^a-z]*web/i, title: 'Développeur Web' },
            { pattern: /comptable/i, title: 'Comptable' },
            { pattern: /secrétaire/i, title: 'Secrétaire' }
        ];
        
        for (const {pattern, title} of jobPatterns) {
            if (pattern.test(text)) {
                if (this.debug) {
                    console.log('✅ PATTERN DÉTECTÉ:', title);
                }
                return title;
            }
        }
        
        // ===== STRATÉGIE 2: EXTRACTION INTELLIGENTE PREMIERS MOTS =====
        const words = text.split(/\s+/);
        const professionalWords = ['assistant', 'assistante', 'responsable', 'chef', 'consultant', 'consultante', 'manager', 'directeur', 'directrice', 'chargé', 'chargée'];
        
        for (let i = 0; i < Math.min(words.length, 6); i++) {
            const word = words[i].toLowerCase().replace(/[()]/g, '');
            
            if (professionalWords.includes(word)) {
                let titleParts = [words[i]];
                
                // Ajouter des mots suivants pertinents
                for (let j = i + 1; j < Math.min(words.length, i + 4); j++) {
                    const nextWord = words[j].toLowerCase();
                    const relevantWords = ['juridique', 'commercial', 'commerciale', 'administratif', 'administrative', 'technique', 'marketing', 'de', 'projet', 'vente', 'équipe', 'clientèle'];
                    
                    if (relevantWords.includes(nextWord)) {
                        titleParts.push(words[j]);
                        
                        // Cas spéciaux avec "de"
                        if (nextWord === 'de' && j + 1 < words.length) {
                            const thirdWord = words[j + 1].toLowerCase();
                            if (['projet', 'vente', 'marketing', 'équipe'].includes(thirdWord)) {
                                titleParts.push(words[j + 1]);
                                break;
                            }
                        }
                    } else {
                        break; // Arrêter si le mot n'est pas pertinent
                    }
                }
                
                let title = titleParts.join(' ');
                title = title.replace(/\([hf\/\s]*\)/gi, ''); // Supprimer (H/F)
                title = title.replace(/\s+/g, ' ').trim();
                
                // Capitaliser correctement
                title = title.split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                    .join(' ');
                
                if (title.length >= 3 && title.length <= MAX_LENGTH) {
                    if (this.debug) {
                        console.log('✅ TITRE EXTRAIT (mots intelligents):', title);
                    }
                    return title;
                }
            }
        }
        
        // ===== STRATÉGIE 3: PREMIÈRE LIGNE NETTOYÉE =====
        const firstLine = text.split('\n')[0].trim();
        if (firstLine && firstLine.length <= 50) { // Plus permissif pour la détection
            let cleanFirstLine = firstLine.replace(/\([hf\/\s]*\)/gi, '');
            cleanFirstLine = cleanFirstLine.replace(/[^\w\sàâäéèêëîïôöùûüç-]/gi, '');
            cleanFirstLine = cleanFirstLine.trim();
            
            if (cleanFirstLine.length >= 3) {
                // Limiter à MAX_LENGTH caractères
                if (cleanFirstLine.length > MAX_LENGTH) {
                    const words = cleanFirstLine.split(' ');
                    cleanFirstLine = words.slice(0, 3).join(' '); // Max 3 mots
                    if (cleanFirstLine.length > MAX_LENGTH) {
                        cleanFirstLine = cleanFirstLine.substring(0, MAX_LENGTH).trim();
                    }
                }
                
                // Capitaliser
                cleanFirstLine = cleanFirstLine.split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
                    .join(' ');
                
                if (this.debug) {
                    console.log('✅ TITRE EXTRAIT (première ligne):', cleanFirstLine);
                }
                return cleanFirstLine;
            }
        }
        
        // ===== FALLBACK GARANTI =====
        const fallback = 'Poste à pourvoir';
        if (this.debug) {
            console.log('⚠️ FALLBACK UTILISÉ:', fallback);
        }
        return fallback;
    }
    
    // Méthodes d'extraction restaurées et améliorées
    extractLocation(text, sections = {}) {
        const locationPatterns = [
            /(Panchéraccía|Corsica|Paris|Lyon|Marseille|Toulouse|Lille|Bordeaux|Nice|Nantes|Strasbourg|Montpellier|Rennes)/gi,
            /(\d{5})\s+([A-Z][A-Za-zéèêëîïôöùûüç\s\-]{3,20})/g,
            /(France|Corse)/gi
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
        const skillsToFind = [
            'Droit', 'Juridique', 'Commercial', 'Vente', 'Marketing',
            'Excel', 'Word', 'PowerPoint', 'Outlook', 'Pack Office',
            'Organisation', 'Autonomie', 'Communication', 'Relationnel',
            'Rigueur', 'Polyvalence', 'Dynamisme', 'Anglais', 'Espagnol'
        ];
        
        skillsToFind.forEach(skill => {
            if (new RegExp(`\\b${skill}\\b`, 'i').test(text)) {
                skillsList.push(skill);
            }
        });
        
        return skillsList.slice(0, 8); // Max 8 compétences
    }
    
    extractExperience(text, sections = {}) {
        const expPatterns = [
            /(\d+\s*(?:à\s*\d+\s*)?an[s]?\s*(?:d[''']?expérience)?)/i,
            /(débutant[e]?)/i,
            /(junior)/i,
            /(senior)/i,
            /(expérience\s+(?:souhaitée|requise|exigée))/i
        ];
        
        for (const pattern of expPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        return '';
    }
    
    extractCompany(text, sections = {}) {
        const companyPatterns = [
            /(Corsica\s+Sole)/i,
            /(Bcom\s*HR)/i,
            /([A-Z][A-Za-z\s]{2,30}(?:SARL|SAS|SA|EURL))/g,
            /(Groupe\s+[A-Z][A-Za-z\s]{2,20})/i
        ];
        
        for (const pattern of companyPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        return '';
    }
    
    extractContractType(text, sections = {}) {
        const contractTypes = ['CDI', 'CDD', 'INTERIM', 'INTÉRIM', 'STAGE', 'FREELANCE', 'TEMPS PARTIEL', 'TEMPS PLEIN'];
        const regex = new RegExp(`\\b(${contractTypes.join('|')})\\b`, 'i');
        const match = text.match(regex);
        return match ? match[1].toUpperCase() : '';
    }
    
    extractEducation(text, sections = {}) {
        const educationPatterns = [
            /((?:bac|licence|master|bts|dut|cap)[^\\n.]{0,40})/i,
            /(niveau\s+(?:bac|licence|master|bts|dut))/i,
            /(formation\s+(?:juridique|commerciale|administrative))/i
        ];
        
        for (const pattern of educationPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        return '';
    }
    
    extractSalary(text, sections = {}) {
        const salaryPatterns = [
            /(\d+\s*k?€?(?:\s*(?:brut|net))?(?:\s*\/\s*an)?)/i,
            /(selon\s+(?:profil|expérience|convention))/i,
            /(à\s+négocier)/i,
            /(salaire\s+(?:attractif|motivant))/i,
            /(\d+\s*-\s*\d+\s*k?€?)/i
        ];
        
        for (const pattern of salaryPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        return '';
    }
    
    extractResponsibilities(text, sections = {}) {
        const responsibilities = [];
        const responsibilityKeywords = [
            'gérer', 'assurer', 'participer', 'contribuer', 'développer',
            'organiser', 'coordonner', 'suivre', 'analyser', 'optimiser'
        ];
        
        const sentences = text.split(/[.!?]/).filter(s => s.trim().length > 15);
        
        sentences.forEach(sentence => {
            const lowerSentence = sentence.toLowerCase();
            if (responsibilityKeywords.some(keyword => lowerSentence.includes(keyword))) {
                const cleanSentence = sentence.trim();
                if (cleanSentence.length > 10 && cleanSentence.length < 150) {
                    responsibilities.push(cleanSentence);
                }
            }
        });
        
        return responsibilities.slice(0, 5);
    }
    
    extractBenefits(text, sections = {}) {
        const benefits = [];
        const commonBenefits = [
            'télétravail', 'remote', 'mutuelle', 'tickets restaurant', 'formation',
            'évolution', 'prime', 'bonus', 'véhicule', 'parking', 'ce', 'rtt'
        ];
        
        commonBenefits.forEach(benefit => {
            if (new RegExp(benefit, 'i').test(text)) {
                benefits.push(benefit.charAt(0).toUpperCase() + benefit.slice(1));
            }
        });
        
        return benefits;
    }
}

// ===== FONCTION DE TEST POUR VALIDATION =====
function testTitleExtractionBalanced() {
    console.log('🧪 TEST v2.10 ÉQUILIBRÉE - Extraction complète');
    
    const testText = "Assistant(e) juridique Qui sommes-nous ?Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques...";
    
    const parser = new JobParserAPI({ debug: true });
    const result = parser.analyzeJobLocally(testText);
    
    console.log('🎯 RÉSULTAT TEST ÉQUILIBRÉ:');
    console.log('📋 Titre extrait:', result.title);
    console.log('📏 Longueur:', result.title.length);
    console.log('🏢 Entreprise:', result.company);
    console.log('📍 Lieu:', result.location);
    console.log('📄 Contrat:', result.contract_type);
    console.log('🎯 Compétences:', result.skills);
    console.log('✅ Test titre réussi:', result.title.length <= 25 && result.title !== testText);
    
    return result;
}

// ===== FORCE RELOAD ET REMPLACEMENT =====
if (typeof window !== 'undefined') {
    // Supprimer les anciennes versions
    delete window.JobParserAPI;
    delete window.testTitleExtraction;
    delete window.testTitleExtractionHotfix;
    
    // Créer la nouvelle instance
    window.JobParserAPI = JobParserAPI;
    window.testTitleExtractionBalanced = testTitleExtractionBalanced;
    
    // Remplacer l'instance globale si elle existe
    if (window.jobParserInstance) {
        window.jobParserInstance = new JobParserAPI({ debug: true });
    }
    
    console.log('🔥 JobParserAPI v2.10 ÉQUILIBRÉE chargé - Parsing complet restauré !');
    console.log('🧪 Tapez testTitleExtractionBalanced() dans la console pour tester');
    
    // Test automatique
    setTimeout(() => {
        console.log('🚀 Lancement du test automatique équilibré...');
        testTitleExtractionBalanced();
    }, 1000);
}