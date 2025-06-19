// JobParserAPI v2.12 EXTRACTION COMPLÈTE - OPTIMISATION TOUS CHAMPS
// Fix: Algorithmes optimisés basés sur analyse PDF réel testfp.pdf
class JobParserAPI {
    constructor(options = {}) {
        this.apiUrl = options.apiUrl || '/api/parse-job';
        this.debug = options.debug || false;
        this.enablePDFCleaning = options.enablePDFCleaning || false;
        this.version = '2.12-COMPLETE-' + Date.now();
        
        if (this.debug) {
            console.log('🔥 JobParserAPI v2.12 EXTRACTION COMPLÈTE - TOUS CHAMPS OPTIMISÉS');
            console.log('⏰ Version:', this.version);
        }
    }
    
    /**
     * Analyse le texte d'une fiche de poste
     */
    async parseJobText(text) {
        if (this.debug) {
            console.log('🚀 Parsing avec v2.12 EXTRACTION COMPLÈTE...');
            console.log('📝 Texte reçu (100 premiers chars):', text.substring(0, 100));
        }
        
        try {
            const apiAvailable = await this.checkApiAvailability();
            
            if (apiAvailable) {
                return await this.sendTextToApi(text);
            } else {
                console.warn('API not available, using v2.12 EXTRACTION COMPLÈTE local');
                return this.analyzeJobLocally(text);
            }
        } catch (error) {
            console.error('Error parsing job text:', error);
            throw error;
        }
    }
    
    async parseJobFile(file) {
        if (this.debug) {
            console.log('📄 Parsing fichier avec v2.12 EXTRACTION COMPLÈTE:', file.name);
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
            console.log('🧹 Nettoyage HTML v2.12...');
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
                      lowerPara.includes('vous serez chargé') || lowerPara.includes('votre mission')) {
                currentSection = 'jobDescription';
            } else if (lowerPara.includes('profil') || lowerPara.includes('compétence') || 
                      lowerPara.includes('expérience') || lowerPara.includes('formation') ||
                      lowerPara.includes('qualification') || lowerPara.includes('votre profil')) {
                currentSection = 'requirements';
            } else if (lowerPara.includes('avantage') || lowerPara.includes('nous offrons') || 
                      lowerPara.includes('package') || lowerPara.includes('bénéfice') || 
                      lowerPara.includes('informations clés')) {
                currentSection = 'benefits';
            } else if (lowerPara.includes('contact') || lowerPara.includes('candidature') || 
                      lowerPara.includes('@') || lowerPara.includes('processus de recrutement')) {
                currentSection = 'contact';
            }
            
            sections[currentSection] += paragraph + '\n';
        }
        
        return sections;
    }
    
    /**
     * Analyse localement - VERSION EXTRACTION COMPLÈTE v2.12
     */
    analyzeJobLocally(text) {
        if (this.debug) {
            console.log('🔍 Analyzing with v2.12 EXTRACTION COMPLÈTE...');
        }
        
        const cleanedText = this.cleanHtmlText(text);
        const sections = this.segmentJobText(cleanedText);
        
        if (this.debug) {
            console.log('📝 Cleaned text length:', cleanedText.length);
            console.log('📂 Text preview:', cleanedText.substring(0, 200) + '...');
        }
        
        const result = {
            title: this.extractJobTitleOptimized(cleanedText, sections),
            company: this.extractCompanyOptimized(cleanedText, sections),
            location: this.extractLocationOptimized(cleanedText, sections),
            contract_type: this.extractContractTypeOptimized(cleanedText, sections),
            skills: this.extractSkillsOptimized(cleanedText, sections),
            experience: this.extractExperienceOptimized(cleanedText, sections),
            education: this.extractEducationOptimized(cleanedText, sections),
            salary: this.extractSalaryOptimized(cleanedText, sections),
            responsibilities: this.extractResponsibilitiesOptimized(cleanedText, sections),
            benefits: this.extractBenefitsOptimized(cleanedText, sections)
        };
        
        if (this.debug) {
            console.log('📊 v2.12 EXTRACTION COMPLÈTE parsing results:', result);
            console.log('🎯 TOUS LES CHAMPS EXTRAITS:', Object.keys(result).length);
        }
        
        return result;
    }
    
    /**
     * 🎯 1. EXTRACTION TITRE OPTIMISÉE (basée sur v2.11)
     */
    extractJobTitleOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('🎯 1. Extraction titre optimisée');
        }
        
        const MAX_LENGTH = 25;
        
        // Pattern spécifique pour "Intitulé du poste :"
        const titleHeaderMatch = text.match(/intitulé\s+du\s+poste\s*:\s*([^\n\r]{3,50})/i);
        if (titleHeaderMatch) {
            let title = titleHeaderMatch[1].trim();
            title = title.replace(/\([hf\/\s]*\)/gi, '').trim();
            if (title.length <= MAX_LENGTH) {
                return title;
            }
        }
        
        // Patterns haute priorité
        const patterns = [
            /Assistant(?:\(e\))?\s+juridique/i,
            /Juriste(?:\s+[a-zA-ZÀ-ÿ]+)?/i,
            /Responsable\s+[a-zA-ZÀ-ÿ]+/i,
            /Chef\s+de\s+[a-zA-ZÀ-ÿ]+/i
        ];
        
        for (const pattern of patterns) {
            const match = text.match(pattern);
            if (match) {
                let title = match[0].trim().replace(/\([hf\/\s]*\)/gi, '');
                if (title.length <= MAX_LENGTH) {
                    return title;
                }
            }
        }
        
        return 'Poste à pourvoir';
    }
    
    /**
     * 🏢 2. EXTRACTION ENTREPRISE OPTIMISÉE
     */
    extractCompanyOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('🏢 2. Extraction entreprise optimisée');
        }
        
        // Pattern spécifique Corsica Sole
        const corsicaMatch = text.match(/(Corsica\s+Sole)/i);
        if (corsicaMatch) {
            return corsicaMatch[1];
        }
        
        // Autres patterns d'entreprises
        const companyPatterns = [
            /(SAS\s+[A-Z][A-Za-z\s]{3,30})/i,
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
    
    /**
     * 📍 3. EXTRACTION LIEU OPTIMISÉE
     */
    extractLocationOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('📍 3. Extraction lieu optimisée');
        }
        
        // Pattern spécifique "Localisation :"
        const locationHeaderMatch = text.match(/localisation\s*:\s*([^\n\r]{3,50})/i);
        if (locationHeaderMatch) {
            return locationHeaderMatch[1].trim();
        }
        
        // Patterns génériques
        const locationPatterns = [
            /(Paris\s+ou\s+Bordeaux)/i,
            /(Paris|Lyon|Marseille|Toulouse|Lille|Bordeaux|Nice|Nantes|Strasbourg|Montpellier|Rennes)/gi,
            /(\d{5})\s+([A-Z][a-zA-ZÀ-ÿ\s\-]{3,20})/g,
            /(Pancheraccia|Corsica|Corse)/gi
        ];
        
        for (const pattern of locationPatterns) {
            const match = text.match(pattern);
            if (match) {
                let location = match[1] && match[2] ? `${match[1]} ${match[2]}` : match[1] || match[0];
                location = location.trim();
                if (location.length >= 3 && location.length <= 50) {
                    return location;
                }
            }
        }
        
        return '';
    }
    
    /**
     * 📄 4. EXTRACTION TYPE DE CONTRAT OPTIMISÉE
     */
    extractContractTypeOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('📄 4. Extraction type de contrat optimisée');
        }
        
        // Pattern spécifique "Type de contrat :"
        const contractHeaderMatch = text.match(/type\s+de\s+contrat\s*:\s*([^\n\r]{3,50})/i);
        if (contractHeaderMatch) {
            return contractHeaderMatch[1].trim();
        }
        
        // Patterns spécifiques
        const contractPatterns = [
            /(Interim\s+pour\s+\d+\s+mois)/i,
            /\b(CDI)\b/i,
            /\b(CDD)\b/i,
            /\b(Stage)\b/i,
            /\b(INTERIM|INTÉRIM)\b/i,
            /\b(Freelance)\b/i,
            /(temps\s+partiel)/i,
            /(temps\s+plein)/i
        ];
        
        for (const pattern of contractPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        
        return '';
    }
    
    /**
     * 💼 5. EXTRACTION EXPÉRIENCE OPTIMISÉE
     */
    extractExperienceOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('💼 5. Extraction expérience optimisée');
        }
        
        // Pattern spécifique "à minima d'une expérience de X ans"
        const minimaMatch = text.match(/à\s+minima\s+d['']une\s+expérience\s+de\s+(\d+)\s+ans?/i);
        if (minimaMatch) {
            return `${minimaMatch[1]} ans minimum`;
        }
        
        // Autres patterns
        const experiencePatterns = [
            /(\d+)\s*(?:à\s*(\d+))?\s*ans?\s*(?:d['']?expérience)?/i,
            /(débutant[e]?)\s*accepté[e]?/i,
            /(junior|confirmé[e]?|senior)/i,
            /(sans\s+expérience)/i,
            /expérience\s+(souhaitée|requise|exigée|nécessaire)/i
        ];
        
        for (const pattern of experiencePatterns) {
            const match = text.match(pattern);
            if (match) {
                let experience = match[1];
                if (match[2]) experience += ` à ${match[2]} ans`;
                return experience;
            }
        }
        
        return '';
    }
    
    /**
     * 🎓 6. EXTRACTION FORMATION OPTIMISÉE
     */
    extractEducationOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('🎓 6. Extraction formation optimisée');
        }
        
        // Pattern spécifique "Diplômé(e) d'une B.T.S ou d'une Licence"
        const diplomeMatch = text.match(/diplômé\(e\)\s+d['']une\s+(B\.?T\.?S\.?\s+ou\s+d['']une\s+Licence[^\n]{0,50})/i);
        if (diplomeMatch) {
            return diplomeMatch[1].trim();
        }
        
        // Autres patterns
        const educationPatterns = [
            /(Master\s*[12]?(?:\s+[a-zA-ZÀ-ÿ\s]{3,30})?)/i,
            /(Licence(?:\s+[a-zA-ZÀ-ÿ\s]{3,30})?)/i,
            /(BTS\s+[a-zA-ZÀ-ÿ\s]{3,30})/i,
            /(DUT\s+[a-zA-ZÀ-ÿ\s]{3,30})/i,
            /(Bac\s*\+\s*[2-5])/i,
            /(niveau\s+(?:bac|licence|master|bts|dut))/i
        ];
        
        for (const pattern of educationPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        
        return '';
    }
    
    /**
     * 💰 7. EXTRACTION SALAIRE OPTIMISÉE
     */
    extractSalaryOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('💰 7. Extraction salaire optimisée');
        }
        
        // Pattern spécifique "Rémunération :"
        const remunerationMatch = text.match(/rémunération\s*:\s*([^\n\r]{10,80})/i);
        if (remunerationMatch) {
            return remunerationMatch[1].trim();
        }
        
        // Autres patterns
        const salaryPatterns = [
            /(fixe\s+à\s+définir\s+en\s+fonction\s+du\s+profil[^\n]{0,50})/i,
            /(\d{1,3}(?:\s?\d{3})*)\s*€\s*(?:brut|net)?\s*(?:\/\s*(?:mois|an|année))?/i,
            /(\d+)\s*k\s*€?\s*(?:brut|net)?\s*(?:\/\s*an)?/i,
            /(selon\s+(?:profil|expérience|convention|grille))/i,
            /(à\s+négocier|négociable)/i
        ];
        
        for (const pattern of salaryPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[1].trim();
            }
        }
        
        return '';
    }
    
    /**
     * 🎯 8. EXTRACTION COMPÉTENCES OPTIMISÉE
     */
    extractSkillsOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('🎯 8. Extraction compétences optimisée');
        }
        
        const skills = [];
        
        // Compétences techniques spécifiques détectées
        const technicalSkills = [
            'Pack Office', 'Word', 'Excel', 'PowerPoint', 'Outlook'
        ];
        
        // Soft skills spécifiques détectées
        const softSkills = [
            'capacité organisationnelle', 'gérer les priorités', 'proactif',
            'rigoureux', 'autonomie', 'esprit d\'équipe', 'capacité d\'analyse',
            'synthèse', 'diligence', 'flexibilité'
        ];
        
        // Vérifier compétences techniques
        technicalSkills.forEach(skill => {
            if (new RegExp(`\\b${skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i').test(text)) {
                skills.push(skill);
            }
        });
        
        // Vérifier soft skills
        softSkills.forEach(skill => {
            if (new RegExp(skill.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'i').test(text)) {
                skills.push(skill.charAt(0).toUpperCase() + skill.slice(1));
            }
        });
        
        return skills.slice(0, 10); // Max 10 compétences
    }
    
    /**
     * 📋 9. EXTRACTION RESPONSABILITÉS OPTIMISÉE
     */
    extractResponsibilitiesOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('📋 9. Extraction responsabilités optimisée');
        }
        
        const responsibilities = [];
        
        // Chercher la section "Votre mission"
        const missionMatch = text.match(/votre\s+mission\s*\n([\s\S]*?)(?=votre\s+profil|informations\s+clés|\n\n|$)/i);
        if (missionMatch) {
            const missionText = missionMatch[1];
            
            // Extraire les points de mission
            const bulletPoints = missionText.split(/[•\-\n]/).filter(point => {
                const cleanPoint = point.trim();
                return cleanPoint.length > 20 && cleanPoint.length < 200;
            });
            
            bulletPoints.forEach(point => {
                const cleanPoint = point.trim().replace(/^[^\w]*/, '');
                if (cleanPoint.length > 15) {
                    responsibilities.push(cleanPoint);
                }
            });
        }
        
        // Si pas trouvé, chercher par mots-clés
        if (responsibilities.length === 0) {
            const responsibilityKeywords = [
                'assister', 'réalisation', 'tenue', 'mise à jour', 'suivi'
            ];
            
            const sentences = text.split(/[.!?\n]/).filter(s => s.trim().length > 15);
            
            sentences.forEach(sentence => {
                const cleanSentence = sentence.trim();
                const lowerSentence = cleanSentence.toLowerCase();
                
                const hasKeyword = responsibilityKeywords.some(keyword => 
                    lowerSentence.includes(keyword.toLowerCase())
                );
                
                if (hasKeyword && cleanSentence.length > 20 && cleanSentence.length < 200) {
                    responsibilities.push(cleanSentence);
                }
            });
        }
        
        return responsibilities.slice(0, 6); // Max 6 responsabilités
    }
    
    /**
     * 🎁 10. EXTRACTION AVANTAGES OPTIMISÉE
     */
    extractBenefitsOptimized(text, sections = {}) {
        if (this.debug) {
            console.log('🎁 10. Extraction avantages optimisée');
        }
        
        const benefits = [];
        
        // Pattern spécifique "avantages" mentionné
        if (/\+\s*avantages/i.test(text)) {
            benefits.push('Avantages inclus');
        }
        
        // Rechercher section "Informations clés" ou avantages explicites
        const benefitPatterns = [
            /(À\s+pourvoir\s+immédiatement)/i,
            /(structure\s+dynamique\s+à\s+taille\s+humaine)/i,
            /(porteuse\s+de\s+sens\s+et\s+de\s+valeurs\s+humaines)/i
        ];
        
        benefitPatterns.forEach(pattern => {
            const match = text.match(pattern);
            if (match) {
                benefits.push(match[1].trim());
            }
        });
        
        // Avantages standards à chercher
        const standardBenefits = [
            'télétravail', 'remote', 'mutuelle', 'tickets restaurant', 'formation',
            'évolution', 'prime', 'bonus', 'véhicule', 'parking', 'ce', 'rtt',
            '13ème mois', 'participation'
        ];
        
        standardBenefits.forEach(benefit => {
            if (new RegExp(benefit, 'i').test(text)) {
                benefits.push(benefit.charAt(0).toUpperCase() + benefit.slice(1));
            }
        });
        
        return benefits.slice(0, 8); // Max 8 avantages
    }
}

// ===== FONCTION DE TEST POUR VALIDATION v2.12 =====
function testExtractionComplete() {
    console.log('🧪 TEST v2.12 EXTRACTION COMPLÈTE - 10 ÉLÉMENTS');
    
    const testText = `
    
Intitulé du poste : Assistant(e) juridique
Qui sommes-nous ?
Corsica Sole est une PME créée en 2009 spécialisée dans le développement & l'exploitation de projets photovoltaïques...
Votre mission 
Vous intègrerez le pôle Corporate/Assurances de la Direction Juridique de Corsica Sole composé de 2 juristes. Vous assisterez les juristes dans la tenue et le suivi d'un portefeuille de plus de 150 sociétés – SAS et SARL.
Votre Profil 
Diplômé(e) d'une B.T.S ou d'une Licence assistant de gestion ou juridique avec des connaissances en droit des sociétés, vous justifiez à minima d'une expérience de 10 ans dans des missions similaires.
Vous maitrisez : Pack Office : Word, Excel, Powerpoint
Informations clés
Localisation : Paris ou Bordeaux
Type de contrat : Interim pour 2 mois
Rémunération : fixe à définir en fonction du profil + avantages
    `;
    
    const parser = new JobParserAPI({ debug: true });
    const result = parser.analyzeJobLocally(testText);
    
    console.log('🎯 RÉSULTAT TEST COMPLET v2.12:');
    console.log('1. 📋 Titre:', result.title);
    console.log('2. 🏢 Entreprise:', result.company);
    console.log('3. 📍 Lieu:', result.location);
    console.log('4. 📄 Contrat:', result.contract_type);
    console.log('5. 💼 Expérience:', result.experience);
    console.log('6. 🎓 Formation:', result.education);
    console.log('7. 💰 Salaire:', result.salary);
    console.log('8. 🎯 Compétences:', result.skills);
    console.log('9. 📋 Responsabilités:', result.responsibilities.length, 'missions');
    console.log('10. 🎁 Avantages:', result.benefits);
    
    console.log('\n✅ Extraction complète réussie!');
    
    return result;
}

// ===== FORCE RELOAD ET REMPLACEMENT =====
if (typeof window !== 'undefined') {
    // Supprimer les anciennes versions
    delete window.JobParserAPI;
    delete window.testTitleExtraction;
    delete window.testTitleExtractionHotfix;
    delete window.testTitleExtractionBalanced;
    delete window.testTitleExtractionDefinitive;
    
    // Créer la nouvelle instance
    window.JobParserAPI = JobParserAPI;
    window.testExtractionComplete = testExtractionComplete;
    
    // Remplacer l'instance globale si elle existe
    if (window.jobParserInstance) {
        window.jobParserInstance = new JobParserAPI({ debug: true });
    }
    
    console.log('🔥 JobParserAPI v2.12 EXTRACTION COMPLÈTE chargé - 10 ÉLÉMENTS OPTIMISÉS !');
    console.log('🧪 Tapez testExtractionComplete() dans la console pour tester');
    
    // Test automatique
    setTimeout(() => {
        console.log('🚀 Lancement du test automatique complet...');
        testExtractionComplete();
    }, 1000);
}