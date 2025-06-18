/**
 * Parser CV Optimisé - Version Améliorée
 * Améliore la précision d'extraction des CVs en mode local
 * Compatible avec l'architecture Commitment existante
 */

class EnhancedCVParser {
    constructor() {
        // Listes étendues de mots-clés pour une détection précise
        this.techSkills = [
            'JavaScript', 'Python', 'Java', 'React', 'Angular', 'Vue.js', 'Node.js', 'PHP', 'C#', 'C++', 
            'HTML', 'CSS', 'SQL', 'TypeScript', 'Flutter', 'Swift', 'Kotlin', 'Ruby', 'Go', 'Rust',
            'MongoDB', 'MySQL', 'PostgreSQL', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
            'Git', 'Jenkins', 'Terraform', 'Ansible', 'Linux', 'Unix', 'Windows Server'
        ];
        
        this.businessSkills = [
            'Gestion projet', 'Gestion équipe', 'Communication', 'Leadership', 'Autonomie', 
            'Rigueur', 'Organisation', 'Analytique', 'Négociation', 'Présentation',
            'Budget', 'Planning', 'Reporting', 'Formation', 'Recrutement', 'Management',
            'Tenue d\'agendas', 'Suivi budgétaire', 'Préparation de rapports', 'Sens de la communication',
            'Excellente organisation du travail', 'Coordination', 'Assistance', 'Secrétariat'
        ];
        
        this.softwareTools = [
            'Microsoft Office', 'Excel', 'Word', 'PowerPoint', 'Outlook', 'Teams', 'Microsoft',
            'Google Workspace', 'Gmail', 'Google Drive', 'Google Sheets', 'Google', 
            'Photoshop', 'Illustrator', 'InDesign', 'Figma', 'Sketch', 'Adobe Creative',
            'AutoCAD', 'SolidWorks', 'SketchUp', 'Revit', 'Maya', '3ds Max',
            'SAP', 'Salesforce', 'CRM', 'ERP', 'JIRA', 'Confluence', 'Slack', 'Notion',
            'Tableau', 'Power BI', 'Excel avancé', 'VBA', 'Macros',
            'Concur', 'Coupa', 'Pennylane', 'QuickBooks', 'Sage', 'Cegid'
        ];
        
        this.languageLevels = {
            'natif': 'Natif',
            'native': 'Natif',
            'langue maternelle': 'Natif',
            'mother tongue': 'Natif',
            'c2': 'C2 - Maîtrise',
            'c1': 'C1 - Autonome',
            'b2': 'B2 - Avancé',
            'b1': 'B1 - Intermédiaire',
            'a2': 'A2 - Élémentaire',
            'a1': 'A1 - Débutant',
            'courant': 'Courant',
            'fluent': 'Courant',
            'avancé': 'Avancé',
            'advanced': 'Avancé',
            'intermédiaire': 'Intermédiaire',
            'intermediate': 'Intermédiaire',
            'débutant': 'Débutant',
            'beginner': 'Débutant',
            'notions': 'Notions',
            'basics': 'Notions'
        };
    }

    /**
     * Parse un CV avec une précision améliorée
     */
    parseCV(content) {
        console.log('🔍 Démarrage du parsing optimisé Commitment...');
        
        const cleanContent = this.cleanText(content);
        
        return {
            data: {
                personal_info: this.extractPersonalInfoEnhanced(cleanContent),
                current_position: this.extractCurrentPositionEnhanced(cleanContent),
                skills: this.extractSkillsEnhanced(cleanContent),
                software: this.extractSoftwareEnhanced(cleanContent),
                languages: this.extractLanguagesEnhanced(cleanContent),
                work_experience: this.extractWorkExperienceEnhanced(cleanContent),
                education: this.extractEducationEnhanced(cleanContent)
            },
            source: 'enhanced_commitment',
            timestamp: new Date().toISOString(),
            parsing_stats: this.getParsingStats(cleanContent)
        };
    }

    /**
     * Nettoie le texte d'entrée pour une meilleure extraction
     */
    cleanText(content) {
        let cleaned = content
            .replace(/[\x00-\x1F\x7F]/g, ' ') // Caractères de contrôle
            .replace(/\s+/g, ' ') // Espaces multiples
            .replace(/\r\n/g, '\n') // Normaliser les retours à la ligne
            .trim();
        
        console.log(`📝 Texte nettoyé: ${cleaned.length} caractères`);
        return cleaned;
    }

    /**
     * Extraction améliorée des informations personnelles
     */
    extractPersonalInfoEnhanced(content) {
        // Patterns sophistiqués pour l'email
        const emailPatterns = [
            /[\w\.-]+@[\w\.-]+\.\w+/g,
            /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g
        ];
        
        // Patterns pour téléphone français et internationaux
        const phonePatterns = [
            /(?:\+33|0)[1-9](?:[\s\.-]?\d{2}){4}/g, // France format standard
            /\+33\d{9}/g, // France international compact
            /(?:\+\d{1,3})?[\s\.-]?\(?\d{1,4}\)?[\s\.-]?\d{1,4}[\s\.-]?\d{1,9}/g // International
        ];
        
        let email = '';
        let phone = '';
        let name = '';
        
        // Extraction email - première occurrence valide
        for (const pattern of emailPatterns) {
            const match = content.match(pattern);
            if (match) {
                email = match[0];
                break;
            }
        }
        
        // Extraction téléphone - première occurrence valide
        for (const pattern of phonePatterns) {
            const match = content.match(pattern);
            if (match) {
                phone = match[0].replace(/[\s\.-]/g, ''); // Nettoyer
                break;
            }
        }
        
        // Extraction nom - logique améliorée pour détecter le nom en début de CV
        const lines = content.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        
        for (let i = 0; i < Math.min(3, lines.length); i++) {
            const line = lines[i];
            // Le nom doit être présent, pas trop long, sans email/téléphone/mots-clés CV
            if (line.length > 2 && line.length < 50 && 
                !line.includes('@') && 
                !line.match(/\d{8,}/) && 
                !line.toLowerCase().includes('cv') &&
                !line.toLowerCase().includes('curriculum') &&
                !line.toLowerCase().includes('resume')) {
                name = line;
                break;
            }
        }
        
        console.log(`👤 Info personnelles: nom="${name}", email="${email}", tel="${phone}"`);
        
        return {
            name: name || 'À compléter',
            email: email || 'À compléter',
            phone: phone || 'À compléter'
        };
    }

    /**
     * Extraction améliorée du poste actuel
     */
    extractCurrentPositionEnhanced(content) {
        const lines = content.split('\n').map(line => line.trim());
        
        // Chercher dans les premières lignes après le nom
        for (let i = 1; i < Math.min(5, lines.length); i++) {
            const line = lines[i];
            if (line.length > 5 && line.length < 100 && 
                !line.includes('@') && 
                !line.match(/\+?\d{8,}/) &&
                !line.toLowerCase().includes('email') &&
                !line.toLowerCase().includes('téléphone') &&
                !line.toLowerCase().includes('phone')) {
                
                // Vérifier si ça ressemble à un titre de poste
                if (this.looksLikeJobTitle(line)) {
                    console.log(`💼 Poste détecté: "${line}"`);
                    return line;
                }
            }
        }
        
        return 'Poste à compléter';
    }

    /**
     * Vérifie si une ligne ressemble à un titre de poste
     */
    looksLikeJobTitle(text) {
        const jobKeywords = [
            'assistant', 'développeur', 'ingénieur', 'chef', 'manager', 'directeur',
            'analyst', 'consultant', 'responsable', 'coordinateur', 'superviseur',
            'specialist', 'expert', 'lead', 'senior', 'junior', 'stagiaire',
            'executive', 'developer', 'engineer', 'officer', 'director'
        ];
        
        return jobKeywords.some(keyword => 
            text.toLowerCase().includes(keyword.toLowerCase())
        );
    }

    /**
     * Extraction améliorée des compétences
     */
    extractSkillsEnhanced(content) {
        const foundSkills = new Set();
        const lowerContent = content.toLowerCase();
        
        // Chercher compétences techniques
        this.techSkills.forEach(skill => {
            if (lowerContent.includes(skill.toLowerCase())) {
                foundSkills.add(skill);
            }
        });
        
        // Chercher compétences métier
        this.businessSkills.forEach(skill => {
            if (lowerContent.includes(skill.toLowerCase())) {
                foundSkills.add(skill);
            }
        });
        
        // Chercher dans les sections spécifiques
        const skillsSections = this.extractSection(content, [
            'compétences', 'skills', 'expertises', 'savoir-faire', 'compétences détectées'
        ]);
        
        skillsSections.forEach(section => {
            // Extraire des listes à puces
            const bulletPoints = section.match(/[•\-*]\s*([^\n\r]{2,100})/g) || [];
            bulletPoints.forEach(point => {
                const cleanPoint = point.replace(/^[•\-*]\s*/, '').trim();
                if (cleanPoint.length > 2 && cleanPoint.length < 50) {
                    foundSkills.add(cleanPoint);
                }
            });
        });
        
        const skillsArray = Array.from(foundSkills);
        console.log(`🛠️ Compétences trouvées: ${skillsArray.length} - ${skillsArray.slice(0, 5).join(', ')}...`);
        
        return skillsArray.length > 0 ? skillsArray : ['Compétences à spécifier'];
    }

    /**
     * Extraction améliorée des logiciels
     */
    extractSoftwareEnhanced(content) {
        const foundSoftware = new Set();
        const lowerContent = content.toLowerCase();
        
        this.softwareTools.forEach(software => {
            if (lowerContent.includes(software.toLowerCase())) {
                foundSoftware.add(software);
            }
        });
        
        // Chercher dans les sections logiciels/outils
        const softwareSections = this.extractSection(content, [
            'logiciels', 'software', 'outils', 'tools', 'applications', 'informatique'
        ]);
        
        softwareSections.forEach(section => {
            const bulletPoints = section.match(/[•\-*]\s*([^\n\r]{2,50})/g) || [];
            bulletPoints.forEach(point => {
                const cleanPoint = point.replace(/^[•\-*]\s*/, '').trim();
                if (cleanPoint.length > 2 && cleanPoint.length < 30) {
                    foundSoftware.add(cleanPoint);
                }
            });
        });
        
        const softwareArray = Array.from(foundSoftware);
        console.log(`💻 Logiciels trouvés: ${softwareArray.length} - ${softwareArray.slice(0, 5).join(', ')}...`);
        
        return softwareArray.length > 0 ? softwareArray : ['Logiciels à spécifier'];
    }

    /**
     * Extraction améliorée des langues avec niveaux
     */
    extractLanguagesEnhanced(content) {
        const languages = [];
        
        // Patterns pour détecter les langues avec niveaux
        const languagePatterns = [
            /(français|french)\s*[-:\s]*([a-z0-9\s]+)/gi,
            /(anglais|english)\s*[-:\s]*([a-z0-9\s]+)/gi,
            /(espagnol|spanish)\s*[-:\s]*([a-z0-9\s]+)/gi,
            /(allemand|german)\s*[-:\s]*([a-z0-9\s]+)/gi,
            /(italien|italian)\s*[-:\s]*([a-z0-9\s]+)/gi,
            /(chinois|chinese)\s*[-:\s]*([a-z0-9\s]+)/gi,
            /(japonais|japanese)\s*[-:\s]*([a-z0-9\s]+)/gi
        ];
        
        languagePatterns.forEach(pattern => {
            const matches = content.matchAll(pattern);
            for (const match of matches) {
                const language = this.normalizeLanguageName(match[1]);
                const levelText = match[2] ? match[2].toLowerCase().trim() : '';
                const level = this.extractLanguageLevel(levelText);
                
                // Éviter les doublons
                if (!languages.some(lang => lang.language.toLowerCase() === language.toLowerCase())) {
                    languages.push({
                        language: language,
                        level: level
                    });
                }
            }
        });
        
        // Si aucune langue détectée, ajouter des langues par défaut
        if (languages.length === 0) {
            languages.push(
                { language: 'Français', level: 'Natif' },
                { language: 'Anglais', level: 'À évaluer' }
            );
        }
        
        console.log(`🌍 Langues détectées: ${languages.map(l => `${l.language} (${l.level})`).join(', ')}`);
        
        return languages;
    }

    /**
     * Normalise le nom d'une langue
     */
    normalizeLanguageName(language) {
        const languageMap = {
            'français': 'Français',
            'french': 'Français',
            'anglais': 'Anglais',
            'english': 'Anglais',
            'espagnol': 'Espagnol',
            'spanish': 'Espagnol',
            'allemand': 'Allemand',
            'german': 'Allemand',
            'italien': 'Italien',
            'italian': 'Italien'
        };
        
        return languageMap[language.toLowerCase()] || language.charAt(0).toUpperCase() + language.slice(1).toLowerCase();
    }

    /**
     * Extrait le niveau d'une langue à partir du texte
     */
    extractLanguageLevel(text) {
        const normalizedText = text.toLowerCase().trim();
        
        // Chercher le niveau exact
        for (const [pattern, level] of Object.entries(this.languageLevels)) {
            if (normalizedText.includes(pattern)) {
                return level;
            }
        }
        
        return 'À évaluer';
    }

    /**
     * Extraction améliorée de l'expérience professionnelle
     */
    extractWorkExperienceEnhanced(content) {
        const experiences = [];
        
        // Chercher les sections d'expérience
        const expSections = this.extractSection(content, [
            'expérience', 'experience', 'parcours', 'emploi', 'travail'
        ]);
        
        if (expSections.length === 0) {
            console.log('❌ Aucune section d\'expérience trouvée');
            return [{
                title: 'À compléter',
                company: 'À spécifier',
                start_date: 'À définir',
                end_date: 'À définir'
            }];
        }
        
        expSections.forEach(section => {
            const sectionExperiences = this.parseExperienceSection(section);
            experiences.push(...sectionExperiences);
        });
        
        // Trier par date (plus récent en premier)
        experiences.sort((a, b) => this.compareDates(b.start_date, a.start_date));
        
        console.log(`💼 ${experiences.length} expériences trouvées`);
        
        return experiences.length > 0 ? experiences : [{
            title: 'À compléter',
            company: 'À spécifier',
            start_date: 'À définir',
            end_date: 'À définir'
        }];
    }

    /**
     * Parse une section d'expérience
     */
    parseExperienceSection(section) {
        const experiences = [];
        
        // Pattern pour détecter les dates (MM/YYYY - MM/YYYY)
        const datePattern = /(\d{2}\/\d{4})\s*[-–]\s*(\d{2}\/\d{4}|présent|present|actuel|current)/gi;
        
        let match;
        const dateMatches = [];
        
        // Trouver toutes les dates
        while ((match = datePattern.exec(section)) !== null) {
            dateMatches.push({
                start: match[1],
                end: match[2],
                index: match.index,
                fullMatch: match[0]
            });
        }
        
        // Pour chaque période trouvée, extraire l'expérience associée
        dateMatches.forEach((dateMatch, index) => {
            const startPos = dateMatch.index;
            const endPos = index < dateMatches.length - 1 ? 
                dateMatches[index + 1].index : section.length;
            
            const experienceText = section.substring(startPos, endPos);
            const experience = this.parseExperienceBlock(experienceText, dateMatch);
            
            if (experience) {
                experiences.push(experience);
            }
        });
        
        return experiences;
    }

    /**
     * Parse un bloc d'expérience individuel
     */
    parseExperienceBlock(text, dateMatch) {
        const lines = text.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        
        if (lines.length < 2) return null;
        
        let title = 'À compléter';
        let company = 'À spécifier';
        
        // Chercher le titre du poste
        for (let i = 1; i < Math.min(3, lines.length); i++) {
            const line = lines[i];
            if (line.length > 5 && line.length < 100 && 
                !line.match(/\d{2}\/\d{4}/) && // Pas une date
                this.looksLikeJobTitle(line)) {
                title = line;
                break;
            }
        }
        
        // Chercher le nom de l'entreprise
        for (let i = 1; i < Math.min(5, lines.length); i++) {
            const line = lines[i];
            if (line.length > 3 && line.length < 80 && 
                line !== title &&
                !line.match(/\d{2}\/\d{4}/) && // Pas une date
                !line.includes('•') && // Pas une liste
                !line.includes('-') && // Pas une liste
                line.charAt(0) === line.charAt(0).toUpperCase()) { // Commence par majuscule
                company = line;
                break;
            }
        }
        
        return {
            title: title,
            company: company,
            start_date: dateMatch.start,
            end_date: dateMatch.end.toLowerCase().includes('présent') || 
                      dateMatch.end.toLowerCase().includes('present') || 
                      dateMatch.end.toLowerCase().includes('actuel') ? 'Present' : dateMatch.end
        };
    }

    /**
     * Extraction de la formation
     */
    extractEducationEnhanced(content) {
        const education = [];
        
        // Chercher les sections de formation
        const eduSections = this.extractSection(content, [
            'formation', 'education', 'études', 'diplôme', 'diploma', 'université', 'university', 'école'
        ]);
        
        eduSections.forEach(section => {
            const degrees = this.parseEducationSection(section);
            education.push(...degrees);
        });
        
        console.log(`🎓 ${education.length} formations trouvées`);
        
        return education.length > 0 ? education : [{
            degree: 'À compléter',
            institution: 'À spécifier',
            year: 'À définir'
        }];
    }

    /**
     * Parse une section de formation
     */
    parseEducationSection(section) {
        const education = [];
        const lines = section.split('\n').map(line => line.trim()).filter(line => line.length > 0);
        
        // Chercher les patterns d'année
        const yearPattern = /\b(19|20)\d{2}\b/g;
        
        lines.forEach(line => {
            const yearMatch = line.match(yearPattern);
            if (yearMatch) {
                const year = yearMatch[yearMatch.length - 1]; // Prendre la dernière année trouvée
                
                // Extraire le diplôme et l'institution
                const parts = line.split(/[,\-]/);
                let degree = 'À compléter';
                let institution = 'À spécifier';
                
                if (parts.length >= 2) {
                    degree = parts[0].replace(yearPattern, '').trim();
                    institution = parts[1].trim();
                } else {
                    degree = line.replace(yearPattern, '').trim();
                }
                
                if (degree.length > 3) {
                    education.push({
                        degree: degree,
                        institution: institution,
                        year: year
                    });
                }
            }
        });
        
        return education;
    }

    /**
     * Extrait des sections spécifiques du contenu
     */
    extractSection(content, keywords) {
        const sections = [];
        const lines = content.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].toLowerCase();
            
            // Vérifier si la ligne contient un des mots-clés
            if (keywords.some(keyword => line.includes(keyword.toLowerCase()))) {
                // Extraire la section (jusqu'à la prochaine section ou fin)
                let sectionContent = '';
                let j = i + 1;
                
                while (j < lines.length) {
                    const nextLine = lines[j].toLowerCase();
                    
                    // Arrêter si on trouve une nouvelle section
                    if (this.isNewSection(nextLine) && j > i + 3) {
                        break;
                    }
                    
                    sectionContent += lines[j] + '\n';
                    j++;
                }
                
                if (sectionContent.trim().length > 10) {
                    sections.push(sectionContent);
                }
            }
        }
        
        return sections;
    }

    /**
     * Vérifie si une ligne marque le début d'une nouvelle section
     */
    isNewSection(line) {
        const sectionKeywords = [
            'expérience', 'experience', 'formation', 'education', 'compétences', 'skills',
            'langues', 'languages', 'centres d\'intérêt', 'hobbies', 'références', 'references',
            'coordonnées', 'contact', 'informatique', 'logiciels'
        ];
        
        return sectionKeywords.some(keyword => line.includes(keyword));
    }

    /**
     * Compare deux dates au format MM/YYYY
     */
    compareDates(date1, date2) {
        if (!date1 || !date2) return 0;
        
        const parseDate = (dateStr) => {
            if (dateStr.toLowerCase().includes('present') || 
                dateStr.toLowerCase().includes('actuel')) {
                return new Date();
            }
            
            const parts = dateStr.split('/');
            if (parts.length === 2) {
                return new Date(parseInt(parts[1]), parseInt(parts[0]) - 1);
            }
            return new Date(0);
        };
        
        return parseDate(date1) - parseDate(date2);
    }

    /**
     * Statistiques de parsing pour monitoring
     */
    getParsingStats(content) {
        return {
            content_length: content.length,
            lines_count: content.split('\n').length,
            word_count: content.split(' ').length,
            parsing_time: new Date().toISOString(),
            parser_version: 'enhanced_v1.0'
        };
    }
}

// Fonction d'intégration pour remplacer le parser existant
function createEnhancedParser() {
    const parser = new EnhancedCVParser();
    
    return {
        parseCV: async (file) => {
            try {
                const content = await readFileContent(file);
                return parser.parseCV(content);
            } catch (error) {
                console.error('Erreur parsing enhanced:', error);
                throw error;
            }
        }
    };
}

// Fonction utilitaire pour lire le contenu du fichier
async function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error('Erreur lecture fichier'));
        reader.readAsText(file);
    });
}

// Export pour utilisation globale
if (typeof window !== 'undefined') {
    window.EnhancedCVParser = EnhancedCVParser;
    window.createEnhancedParser = createEnhancedParser;
}

console.log('✅ Enhanced CV Parser Commitment chargé avec succès !');
