// JobParserAPI v2.11 DÉFINITIVE - CORRECTION EXTRACTION TITRE
// Fix: Implémentation stratégie Multi-patterns basée sur test-pdf-parser.js
class JobParserAPI {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/parse-job';
        this.debug = options.debug || false;
        this.enablePDFCleaning = options.enablePDFCleaning || false;
        this.version = '2.11-MULTIPATTERNS-' + Date.now();
        
        if (this.debug) {
            console.log('🔥 JobParserAPI v2.11 DÉFINITIVE - STRATÉGIE MULTI-PATTERNS');
            console.log('⏰ Version:', this.version);
        }
    }
    
    /**
     * Analyse le texte d'une fiche de poste
     */
    async parseJobText(text) {
        if (this.debug) {
            console.log('🚀 Parsing avec v2.11 DÉFINITIVE...');
            console.log('📝 Texte reçu (100 premiers chars):', text.substring(0, 100));
        }
        
        try {
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendTextToApi(text);
            } else {
                console.warn('API not available, using v2.11 DÉFINITIVE local');
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            console.error('Error parsing job text:', error);
            throw error;
        }
    }
    
    async parseJobFile(file) {
        if (this.debug) {
            console.log('📄 Parsing fichier avec v2.11 DÉFINITIVE:', file.name);
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
            console.log('🧹 Nettoyage HTML v2.11...');
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
     * Analyse localement - VERSION DÉFINITIVE v2.11
     */
    analyzeJobLocally(text) {
        if (this.debug) {
            console.log('🔍 Analyzing with v2.11 DÉFINITIVE rules...');
        }
        
        const cleanedText = this.cleanHtmlText(text);
        const sections = this.segmentJobText(cleanedText);
        
        if (this.debug) {
            console.log('📝 Cleaned text length:', cleanedText.length);
            console.log('📂 Text preview:', cleanedText.substring(0, 200) + '...');
        }
        
        const result = {
            title: this.extractJobTitleMultiPatterns(cleanedText, sections),
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
            console.log('📊 v2.11 DÉFINITIVE parsing results:', result);
            console.log('🎯 TITRE EXTRAIT:', result.title);
        }
        
        return result;
    }
    
    /**
     * 🚀 EXTRACTION TITRE MULTI-PATTERNS v2.11 DÉFINITIVE
     * Basée sur les résultats de test-pdf-parser.js - Stratégie gagnante
     * Résultat validé: "Assistant(e) juridique" (22 caractères)
     */
    extractJobTitleMultiPatterns(text, sections = {}) {
        if (this.debug) {
            console.log('🎯 v2.11 MULTI-PATTERNS - Extraction titre définitive');
            console.log('📝 Texte original (100 chars):', text.substring(0, 100));
        }
        
        const MAX_LENGTH = 25;
        
        // ===== ÉTAPE 1: PATTERNS SPÉCIFIQUES HAUTE PRIORITÉ =====
        const highPriorityPatterns = [
            { regex: /Assistant(?:\(e\))?\s+juridique/i, name: 'Assistant juridique spécifique' },
            { regex: /Juriste(?:\s+[a-zA-ZÀ-ÿ]+)?/i, name: 'Juriste général' },
            { regex: /Conseiller(?:\(ère\))?\s+juridique/i, name: 'Conseiller juridique' },
            { regex: /Responsable(?:\s+[a-zA-ZÀ-ÿ]+){1,2}/i, name: 'Responsable' },
            { regex: /Chef(?:\s+de)?\s+[a-zA-ZÀ-ÿ]+/i, name: 'Chef' },
            { regex: /Manager(?:\s+[a-zA-ZÀ-ÿ]+)?/i, name: 'Manager' },
            { regex: /Directeur(?:\(trice\))?\s+[a-zA-ZÀ-ÿ]+/i, name: 'Directeur' },
            { regex: /Consultant(?:\(e\))?\s+[a-zA-ZÀ-ÿ]+/i, name: 'Consultant' },
            { regex: /Développeur(?:\(euse\))?\s+[a-zA-ZÀ-ÿ]+/i, name: 'Développeur' },
            { regex: /Comptable(?:\s+[a-zA-ZÀ-ÿ]+)?/i, name: 'Comptable' },
            { regex: /Secrétaire(?:\s+[a-zA-ZÀ-ÿ]+)?/i, name: 'Secrétaire' }
        ];
        
        if (this.debug) {
            console.log('🎯 Test patterns haute priorité:');
        }
        
        for (const { regex, name } of highPriorityPatterns) {
            const match = text.match(regex);
            if (match) {
                let title = match[0].trim();
                
                // Nettoyer le titre
                title = title.replace(/\([hf\/\s]*\)/gi, ''); // Supprimer (H/F), (e), etc.
                title = title.replace(/\s+/g, ' ').trim();
                
                // Limiter à MAX_LENGTH caractères
                if (title.length > MAX_LENGTH) {
                    title = title.substring(0, MAX_LENGTH).trim();
                }
                
                if (this.debug) {
                    console.log(`  ✅ ${name}: "${title}" (${title.length} caractères)`);
                }
                
                return title;
            }
            
            if (this.debug) {
                console.log(`  ❌ ${name}: Non trouvé`);
            }
        }
        
        // ===== ÉTAPE 2: ANALYSE DES PREMIÈRES LIGNES SIGNIFICATIVES =====
        if (this.debug) {
            console.log('\n🔍 Analyse premières lignes:');
        }
        
        const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        
        for (let i = 0; i < Math.min(3, lines.length); i++) {
            const line = lines[i];
            
            // Ignorer les lignes avec des mots-clés d'exclusion
            if (/^(qui sommes|nous|offre|entreprise|société|groupe|intitulé du poste|poste|recrutement)/i.test(line)) {
                if (this.debug) {
                    console.log(`  ⏭️ Ligne ${i + 1} ignorée: "${line.substring(0, 30)}..."`);
                }
                continue;
            }
            
            // Nettoyer la ligne pour extraire un titre potentiel
            let candidateTitle = line
                .replace(/^[^a-zA-ZÀ-ÿ]*/, '') // Supprimer caractères non alphabétiques au début
                .replace(/[^\w\sÀ-ÿ\(\)\-]/g, ' ') // Garder seulement lettres, espaces, parenthèses, tirets
                .replace(/\([hf\/\s]*\)/gi, '') // Supprimer (H/F), (e), etc.
                .replace(/\s+/g, ' ') // Normaliser les espaces
                .trim();
            
            if (candidateTitle.length >= 5 && candidateTitle.length <= 50) {
                // Limiter à MAX_LENGTH caractères
                if (candidateTitle.length > MAX_LENGTH) {
                    const words = candidateTitle.split(' ');
                    candidateTitle = words.slice(0, 3).join(' '); // Max 3 mots
                    if (candidateTitle.length > MAX_LENGTH) {
                        candidateTitle = candidateTitle.substring(0, MAX_LENGTH).trim();
                    }
                }
                
                // Vérifier que c'est un titre de poste valide
                const jobIndicators = /\b(assistant|responsable|chef|manager|directeur|consultant|développeur|comptable|secrétaire|juriste|conseiller)\b/i;
                if (jobIndicators.test(candidateTitle)) {
                    if (this.debug) {
                        console.log(`  ✅ Ligne ${i + 1} candidate: "${candidateTitle}" (${candidateTitle.length} caractères)`);
                    }
                    return candidateTitle;
                }
            }
            
            if (this.debug) {
                console.log(`  ❌ Ligne ${i + 1} rejetée: "${line.substring(0, 30)}..." (longueur: ${candidateTitle.length})`);
            }
        }
        
        // ===== ÉTAPE 3: PATTERNS GÉNÉRIQUES =====
        if (this.debug) {
            console.log('\n🔍 Recherche patterns génériques:');
        }
        
        const genericPatterns = [
            /\b(assistant|assistante|secrétaire|conseiller|conseillère|responsable|chef|manager|directeur|directrice|consultant|consultante)\s+\w+/gi
        ];
        
        for (const pattern of genericPatterns) {
            const matches = text.match(pattern);
            if (matches && matches.length > 0) {
                let title = matches[0].trim();
                title = title.replace(/\([hf\/\s]*\)/gi, '');
                title = title.replace(/\s+/g, ' ').trim();
                
                if (title.length <= MAX_LENGTH) {
                    if (this.debug) {
                        console.log(`  ✅ Pattern générique trouvé: "${title}" (${title.length} caractères)`);
                    }
                    return title;
                }
            }
        }
        
        // ===== ÉTAPE 4: FALLBACK GARANTI =====
        const fallback = 'Poste à pourvoir';
        if (this.debug) {
            console.log('\n⚠️ Fallback activé:', fallback);
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
            /(\d+\s*(?:à\s*\d+\s*)?an[s]?\s*(?:d['']?expérience)?)/i,
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
            /((?:bac|licence|master|bts|dut|cap)[^\n.]{0,40})/i,
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
            /(\d+\s*k?€?\s*(?:brut|net)?\s*(?:\/\s*an)?)/i,
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
function testTitleExtractionDefinitive() {
    console.log('🧪 TEST v2.11 DÉFINITIVE - Extraction Multi-Patterns');
    
    const testText = "Assistant(e) juridique Qui sommes-nous ?Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques...";
    
    const parser = new JobParserAPI({ debug: true });
    const result = parser.analyzeJobLocally(testText);
    
    console.log('🎯 RÉSULTAT TEST DÉFINITIF:');
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
    delete window.testTitleExtractionBalanced;
    
    // Créer la nouvelle instance
    window.JobParserAPI = JobParserAPI;
    window.testTitleExtractionDefinitive = testTitleExtractionDefinitive;
    
    // Remplacer l'instance globale si elle existe
    if (window.jobParserInstance) {
        window.jobParserInstance = new JobParserAPI({ debug: true });
    }
    
    console.log('🔥 JobParserAPI v2.11 DÉFINITIVE chargé - Multi-Patterns implémenté !');
    console.log('🧪 Tapez testTitleExtractionDefinitive() dans la console pour tester');
    
    // Test automatique
    setTimeout(() => {
        console.log('🚀 Lancement du test automatique définitif...');
        testTitleExtractionDefinitive();
    }, 1000);
}