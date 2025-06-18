/**
 * Parser CV Optimisé - CORRECTION MULTI-PAGES PDF
 * Résout le problème de lecture des PDF multi-pages avec PDF.js
 * Version 2.1 - Fix complet pour CV comme celui de Sabine Rivière
 */

class EnhancedCVParserMultipage {
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
            'Excellente organisation du travail', 'Coordination', 'Assistance', 'Secrétariat',
            'Esprit d\'équipe', 'Gestion des agendas', 'Organisation des déplacements', 'Rédaction'
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

        // Charger PDF.js si pas déjà chargé
        this.initPDFJS();
    }

    /**
     * Initialise PDF.js pour la lecture des PDF multi-pages
     */
    async initPDFJS() {
        try {
            // Vérifier si PDF.js est déjà chargé
            if (typeof window.pdfjsLib !== 'undefined') {
                console.log('✅ PDF.js déjà chargé');
                return;
            }

            // Charger PDF.js dynamiquement
            console.log('🔧 Chargement PDF.js pour lecture multi-pages...');
            
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';
            script.onload = () => {
                console.log('✅ PDF.js chargé avec succès');
                if (window.pdfjsLib) {
                    window.pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
                }
            };
            script.onerror = () => {
                console.warn('⚠️ Échec du chargement PDF.js, fallback vers lecture basique');
            };
            
            document.head.appendChild(script);
            
            // Attendre le chargement
            await new Promise((resolve) => {
                script.onload = resolve;
                script.onerror = resolve; // Continue même en cas d'erreur
            });
            
        } catch (error) {
            console.warn('⚠️ Erreur lors de l\'initialisation PDF.js:', error);
        }
    }

    /**
     * Parse un CV avec lecture PDF multi-pages corrigée
     */
    async parseCV(file) {
        console.log('🔍 Démarrage du parsing multi-pages optimisé...');
        
        try {
            // Lire le contenu du fichier avec la méthode appropriée
            const content = await this.readFileContentAdvanced(file);
            console.log(`📄 Contenu total extrait: ${content.length} caractères`);
            
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
                source: 'enhanced_commitment_multipage_v2.1',
                timestamp: new Date().toISOString(),
                parsing_stats: this.getParsingStats(cleanContent, file)
            };
        } catch (error) {
            console.error('❌ Erreur lors du parsing multi-pages:', error);
            throw error;
        }
    }

    /**
     * MÉTHODE CORRIGÉE : Lecture avancée des fichiers avec support PDF multi-pages
     */
    async readFileContentAdvanced(file) {
        const fileType = file.type;
        const fileName = file.name.toLowerCase();
        
        console.log(`🔍 Analyse du fichier: ${file.name} (${fileType})`);
        
        // PDF : Utiliser PDF.js pour extraire le texte de toutes les pages
        if (fileType === 'application/pdf' || fileName.endsWith('.pdf')) {
            return await this.extractTextFromPDF(file);
        }
        
        // Images : Utiliser OCR ou afficher un message informatif
        if (fileType.startsWith('image/')) {
            console.log('📷 Fichier image détecté - extraction basique');
            return await this.handleImageFile(file);
        }
        
        // Documents Word : Extraction basique (pourrait être améliorée avec une lib spécialisée)
        if (fileType.includes('word') || fileName.endsWith('.doc') || fileName.endsWith('.docx')) {
            console.log('📝 Document Word détecté - extraction basique');
            return await this.readAsText(file);
        }
        
        // Fallback : lecture comme texte
        return await this.readAsText(file);
    }

    /**
     * NOUVELLE MÉTHODE : Extraction de texte PDF multi-pages avec PDF.js
     */
    async extractTextFromPDF(file) {
        try {
            console.log('📚 Extraction PDF multi-pages avec PDF.js...');
            
            // Vérifier que PDF.js est disponible
            if (typeof window.pdfjsLib === 'undefined') {
                console.warn('⚠️ PDF.js non disponible, fallback vers lecture basique');
                return await this.readAsText(file);
            }
            
            // Lire le fichier comme ArrayBuffer
            const arrayBuffer = await this.readAsArrayBuffer(file);
            
            // Charger le PDF
            const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
            console.log(`📖 PDF chargé: ${pdf.numPages} pages détectées`);
            
            let fullText = '';
            
            // Extraire le texte de toutes les pages
            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                console.log(`📄 Extraction page ${pageNum}/${pdf.numPages}...`);
                
                const page = await pdf.getPage(pageNum);
                const textContent = await page.getTextContent();
                
                // Combiner tous les éléments de texte de la page
                const pageText = textContent.items
                    .map(item => item.str || '')
                    .join(' ');
                
                console.log(`✅ Page ${pageNum} : ${pageText.length} caractères extraits`);
                
                // Ajouter le texte de la page au contenu total
                fullText += `\n\n--- PAGE ${pageNum} ---\n\n` + pageText;
            }
            
            console.log(`🎯 Extraction PDF terminée : ${fullText.length} caractères au total`);
            
            return fullText;
            
        } catch (error) {
            console.error('❌ Erreur lors de l\'extraction PDF:', error);
            console.log('🔄 Fallback vers lecture basique...');
            return await this.readAsText(file);
        }
    }

    /**
     * Lit un fichier comme ArrayBuffer (nécessaire pour PDF.js)
     */
    async readAsArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Erreur lecture ArrayBuffer'));
            reader.readAsArrayBuffer(file);
        });
    }

    /**
     * Gestion des fichiers images (placeholder pour OCR futur)
     */
    async handleImageFile(file) {
        console.log('📷 Fichier image détecté. Pour de meilleurs résultats, veuillez utiliser un fichier PDF ou Word.');
        
        // Placeholder : pour l'instant, retourner un message informatif
        // Dans une version future, on pourrait intégrer Tesseract.js pour l'OCR
        return `
        FICHIER IMAGE DÉTECTÉ
        
        Nom du fichier: ${file.name}
        Taille: ${(file.size / 1024 / 1024).toFixed(2)} MB
        
        Pour une extraction optimale des données de votre CV, 
        nous recommandons d'utiliser un fichier PDF ou Word.
        
        Vous pouvez continuer et compléter manuellement vos informations 
        à l'étape suivante.
        `;
    }

    /**
     * Lecture basique comme texte (fallback)
     */
    async readAsText(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('Erreur lecture fichier'));
            reader.readAsText(file, 'UTF-8');
        });
    }

    /**
     * Nettoie le texte d'entrée pour une meilleure extraction
     */
    cleanText(content) {
        let cleaned = content
            .replace(/[\\x00-\\x1F\\x7F]/g, ' ') // Caractères de contrôle
            .replace(/\\s+/g, ' ') // Espaces multiples
            .replace(/\\r\\n/g, '\\n') // Normaliser les retours à la ligne
            .replace(/--- PAGE \\d+ ---/g, '\\n') // Supprimer les marqueurs de pages
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
            /[\\w\\.-]+@[\\w\\.-]+\\.\\w+/g,
            /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}/g
        ];
        
        // Patterns pour téléphone français et internationaux
        const phonePatterns = [
            /(?:\\+33|0)[1-9](?:[\\s\\.-]?\\d{2}){4}/g, // France format standard
            /\\+33\\d{9}/g, // France international compact
            /(?:\\+\\d{1,3})?[\\s\\.-]?\\(?\\d{1,4}\\)?[\\s\\.-]?\\d{1,4}[\\s\\.-]?\\d{1,9}/g // International
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
                phone = match[0].replace(/[\\s\\.-]/g, ''); // Nettoyer
                break;
            }
        }
        
        // Extraction nom - logique améliorée pour détecter le nom en début de CV
        const lines = content.split('\\n').map(line => line.trim()).filter(line => line.length > 0);
        
        for (let i = 0; i < Math.min(5, lines.length); i++) {
            const line = lines[i];
            // Le nom doit être présent, pas trop long, sans email/téléphone/mots-clés CV
            if (line.length > 2 && line.length < 50 && 
                !line.includes('@') && 
                !line.match(/\\d{8,}/) && 
                !line.toLowerCase().includes('cv') &&
                !line.toLowerCase().includes('curriculum') &&
                !line.toLowerCase().includes('resume') &&
                !line.toLowerCase().includes('page')) {
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
        const lines = content.split('\\n').map(line => line.trim());
        
        // Chercher dans les premières lignes après le nom
        for (let i = 1; i < Math.min(8, lines.length); i++) {
            const line = lines[i];
            if (line.length > 5 && line.length < 100 && 
                !line.includes('@') && 
                !line.match(/\\+?\\d{8,}/) &&
                !line.toLowerCase().includes('email') &&
                !line.toLowerCase().includes('téléphone') &&
                !line.toLowerCase().includes('phone') &&
                !line.toLowerCase().includes('page')) {
                
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
            const bulletPoints = section.match(/[•\\-*]\\s*([^\\n\\r]{2,100})/g) || [];
            bulletPoints.forEach(point => {
                const cleanPoint = point.replace(/^[•\\-*]\\s*/, '').trim();
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
            const bulletPoints = section.match(/[•\\-*]\\s*([^\\n\\r]{2,50})/g) || [];
            bulletPoints.forEach(point => {
                const cleanPoint = point.replace(/^[•\\-*]\\s*/, '').trim();
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
            /(français|french)\\s*[-:\\s]*([a-z0-9\\s]+)/gi,
            /(anglais|english)\\s*[-:\\s]*([a-z0-9\\s]+)/gi,
            /(espagnol|spanish)\\s*[-:\\s]*([a-z0-9\\s]+)/gi,
            /(allemand|german)\\s*[-:\\s]*([a-z0-9\\s]+)/gi,
            /(italien|italian)\\s*[-:\\s]*([a-z0-9\\s]+)/gi,
            /(chinois|chinese)\\s*[-:\\s]*([a-z0-9\\s]+)/gi,
            /(japonais|japanese)\\s*[-:\\s]*([a-z0-9\\s]+)/gi
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
     * Extraction améliorée de l'expérience professionnelle - CORRECTION MAJEURE
     */
    extractWorkExperienceEnhanced(content) {
        const experiences = [];
        
        console.log('🔍 Recherche des expériences dans tout le contenu multi-pages...');
        
        // Méthode 1: Chercher les sections d'expérience formelles
        const expSections = this.extractSection(content, [
            'expérience', 'experience', 'parcours', 'emploi', 'travail'
        ]);
        
        expSections.forEach(section => {
            const sectionExperiences = this.parseExperienceSection(section);
            experiences.push(...sectionExperiences);
        });
        
        // Méthode 2: Recherche globale des patterns de dates dans tout le contenu
        const globalExperiences = this.extractExperiencesFromFullContent(content);
        globalExperiences.forEach(exp => {
            // Éviter les doublons
            if (!experiences.some(existing => 
                existing.title === exp.title && existing.company === exp.company)) {
                experiences.push(exp);
            }
        });
        
        // Trier par date (plus récent en premier)
        experiences.sort((a, b) => this.compareDates(b.start_date, a.start_date));
        
        console.log(`💼 ${experiences.length} expériences trouvées au total`);
        experiences.forEach((exp, index) => {
            console.log(`  ${index + 1}. ${exp.title} - ${exp.company} (${exp.start_date} - ${exp.end_date})`);
        });
        
        return experiences.length > 0 ? experiences : [{
            title: 'À compléter',
            company: 'À spécifier',
            start_date: 'À définir',
            end_date: 'À définir'
        }];
    }

    /**
     * NOUVELLE MÉTHODE : Extraction des expériences depuis tout le contenu multi-pages
     */
    extractExperiencesFromFullContent(content) {
        const experiences = [];
        
        // Pattern pour dates + titre/entreprise (plus flexible)
        const experiencePatterns = [
            // Pattern MM/YYYY - MM/YYYY
            /(\\d{2}\\/\\d{4})\\s*[-–]\\s*(\\d{2}\\/\\d{4}|présent|present|actuel|current)/gi,
            // Pattern YYYY - YYYY  
            /(\\d{4})\\s*[-–]\\s*(\\d{4}|présent|present|actuel|current)/gi
        ];
        
        const lines = content.split('\\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // Chercher les dates dans chaque ligne
            experiencePatterns.forEach(pattern => {
                const matches = line.matchAll(pattern);
                for (const match of matches) {
                    const startDate = match[1];
                    const endDate = match[2];
                    
                    // Chercher le titre et l'entreprise dans les lignes suivantes
                    const experience = this.extractExperienceDetailsAround(lines, i, startDate, endDate);
                    if (experience) {
                        experiences.push(experience);
                    }
                }
            });
        }
        
        return experiences;
    }

    /**
     * Extrait les détails d'une expérience autour d'une ligne de date
     */
    extractExperienceDetailsAround(lines, dateLineIndex, startDate, endDate) {
        let title = 'À compléter';
        let company = 'À spécifier';
        
        // Chercher dans les 5 lignes suivantes la ligne de date
        for (let i = dateLineIndex + 1; i < Math.min(dateLineIndex + 6, lines.length); i++) {
            const line = lines[i].trim();
            
            if (line.length > 5 && line.length < 150) {
                // Si on trouve une ligne qui ressemble à un titre de poste
                if (this.looksLikeJobTitle(line) && title === 'À compléter') {
                    title = line;
                } 
                // Si on trouve une ligne qui ressemble à une entreprise
                else if (this.looksLikeCompanyName(line) && company === 'À spécifier') {
                    company = line;
                }
                
                // Si on a trouvé les deux, on peut s'arrêter
                if (title !== 'À compléter' && company !== 'À spécifier') {
                    break;
                }
            }
        }
        
        // Si on n'a pas trouvé de titre, chercher dans la ligne de date elle-même
        if (title === 'À compléter') {
            const dateLine = lines[dateLineIndex].trim();
            const parts = dateLine.split(/\\d{2}\\/\\d{4}\\s*[-–]\\s*\\d{2}\\/\\d{4}/);
            if (parts.length > 1 && parts[1].trim().length > 5) {
                title = parts[1].trim();
            }
        }
        
        // Retourner seulement si on a au moins un titre valide
        if (title !== 'À compléter' || company !== 'À spécifier') {
            return {
                title: title,
                company: company,
                start_date: startDate,
                end_date: endDate.toLowerCase().includes('présent') || 
                          endDate.toLowerCase().includes('present') || 
                          endDate.toLowerCase().includes('actuel') ? 'Present' : endDate
            };
        }
        
        return null;
    }

    /**
     * Vérifie si une ligne ressemble à un nom d'entreprise
     */
    looksLikeCompanyName(text) {
        const companyIndicators = [
            'sarl', 'sas', 'sa', 'ltd', 'inc', 'corp', 'group', 'company', 'société',
            'entreprise', 'cabinet', 'agence', 'studio', 'consulting', 'solutions',
            'services', 'international', 'france', 'paris', 'london', 'new york'
        ];
        
        const lowerText = text.toLowerCase();
        
        // Une entreprise commence souvent par une majuscule et peut contenir des indicateurs
        return (text.charAt(0) === text.charAt(0).toUpperCase() && 
                text.length > 3 && text.length < 80) ||
               companyIndicators.some(indicator => lowerText.includes(indicator));
    }

    /**
     * Parse une section d'expérience
     */
    parseExperienceSection(section) {
        const experiences = [];
        
        // Pattern pour détecter les dates (MM/YYYY - MM/YYYY)
        const datePattern = /(\\d{2}\\/\\d{4})\\s*[-–]\\s*(\\d{2}\\/\\d{4}|présent|present|actuel|current)/gi;
        
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
        const lines = text.split('\\n').map(line => line.trim()).filter(line => line.length > 0);
        
        if (lines.length < 2) return null;
        
        let title = 'À compléter';
        let company = 'À spécifier';
        
        // Chercher le titre du poste
        for (let i = 1; i < Math.min(3, lines.length); i++) {
            const line = lines[i];
            if (line.length > 5 && line.length < 100 && 
                !line.match(/\\d{2}\\/\\d{4}/) && // Pas une date
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
                !line.match(/\\d{2}\\/\\d{4}/) && // Pas une date
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
     * Extraction de la formation - AMÉLIORATION MULTI-PAGES
     */
    extractEducationEnhanced(content) {
        const education = [];
        
        console.log('🎓 Recherche des formations dans tout le contenu multi-pages...');
        
        // Chercher les sections de formation
        const eduSections = this.extractSection(content, [
            'formation', 'education', 'études', 'diplôme', 'diploma', 'université', 'university', 'école'
        ]);
        
        eduSections.forEach(section => {
            const degrees = this.parseEducationSection(section);
            education.push(...degrees);
        });
        
        // Recherche globale des patterns de formation
        const globalEducation = this.extractEducationFromFullContent(content);
        globalEducation.forEach(edu => {
            // Éviter les doublons
            if (!education.some(existing => 
                existing.degree === edu.degree && existing.institution === edu.institution)) {
                education.push(edu);
            }
        });
        
        console.log(`🎓 ${education.length} formations trouvées`);
        
        return education.length > 0 ? education : [{
            degree: 'À compléter',
            institution: 'À spécifier',
            year: 'À définir'
        }];
    }

    /**
     * Extraction globale des formations depuis tout le contenu multi-pages
     */
    extractEducationFromFullContent(content) {
        const education = [];
        const lines = content.split('\\n');
        
        // Patterns pour détecter les formations
        const educationKeywords = [
            'diplôme', 'degree', 'bachelor', 'master', 'mba', 'phd', 'licence', 'university', 'université',
            'école', 'school', 'institut', 'institute', 'formation', 'études', 'bts', 'dut'
        ];
        
        const yearPattern = /\\b(19|20)\\d{2}\\b/g;
        
        lines.forEach(line => {
            const lowerLine = line.toLowerCase();
            const hasEducationKeyword = educationKeywords.some(keyword => 
                lowerLine.includes(keyword.toLowerCase())
            );
            
            if (hasEducationKeyword) {
                const yearMatch = line.match(yearPattern);
                if (yearMatch) {
                    const year = yearMatch[yearMatch.length - 1];
                    
                    // Extraire le diplôme et l'institution
                    let degree = line.trim();
                    let institution = 'À spécifier';
                    
                    // Si la ligne contient des virgules ou tirets, essayer de séparer
                    const parts = line.split(/[,\\-]/);
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
            }
        });
        
        return education;
    }

    /**
     * Parse une section de formation
     */
    parseEducationSection(section) {
        const education = [];
        const lines = section.split('\\n').map(line => line.trim()).filter(line => line.length > 0);
        
        // Chercher les patterns d'année
        const yearPattern = /\\b(19|20)\\d{2}\\b/g;
        
        lines.forEach(line => {
            const yearMatch = line.match(yearPattern);
            if (yearMatch) {
                const year = yearMatch[yearMatch.length - 1]; // Prendre la dernière année trouvée
                
                // Extraire le diplôme et l'institution
                const parts = line.split(/[,\\-]/);
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
        const lines = content.split('\\n');
        
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
                    
                    sectionContent += lines[j] + '\\n';
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
            'langues', 'languages', 'centres d\\'intérêt', 'hobbies', 'références', 'references',
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
     * Statistiques de parsing pour monitoring (améliorées)
     */
    getParsingStats(content, file) {
        return {
            content_length: content.length,
            lines_count: content.split('\\n').length,
            word_count: content.split(' ').length,
            file_size: file.size,
            file_type: file.type,
            file_name: file.name,
            parsing_time: new Date().toISOString(),
            parser_version: 'enhanced_multipage_v2.1_pdf_fix',
            pdf_support: typeof window.pdfjsLib !== 'undefined'
        };
    }
}

// Fonction d'intégration pour remplacer le parser existant
function createEnhancedMultipageParser() {
    const parser = new EnhancedCVParserMultipage();
    
    return {
        parseCV: async (file) => {
            try {
                return await parser.parseCV(file);
            } catch (error) {
                console.error('Erreur parsing enhanced multipage v2.1:', error);
                throw error;
            }
        }
    };
}

// Export pour utilisation globale
if (typeof window !== 'undefined') {
    window.EnhancedCVParserMultipage = EnhancedCVParserMultipage;
    window.createEnhancedMultipageParser = createEnhancedMultipageParser;
}

console.log('✅ Enhanced CV Parser Commitment v2.1 (Multi-page PDF Fix) chargé avec succès !');
