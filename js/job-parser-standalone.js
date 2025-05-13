/**
 * job-parser-standalone.js
 * Implémentation autonome pour l'analyse de fiches de poste sur GitHub Pages
 * Ne nécessite pas de backend - fonctionne entièrement côté client
 */

document.addEventListener('DOMContentLoaded', function() {
    initStandaloneParser();
});

/**
 * Initialisation du parser autonome
 */
function initStandaloneParser() {
    // Configuration
    const DEBUG = new URLSearchParams(window.location.search).has('debug');
    
    // Debug logging
    function log(message) {
        if (DEBUG) {
            console.log('[JOB PARSER]', message);
        }
    }
    
    log('Initialisation du parser autonome...');
    
    // Nettoyer l'interface des éléments dupliqués
    cleanupDuplicateElements();
    
    // Connecter les événements aux éléments d'interface
    connectUiEvents();
    
    // Activer le bouton d'analyse GPT
    const analyzeButton = document.getElementById('analyze-with-gpt');
    if (analyzeButton) {
        analyzeButton.disabled = false;
        
        // Mettre à jour le statut
        const statusElement = document.getElementById('gpt-analyze-status');
        if (statusElement) {
            statusElement.textContent = 'Prêt (mode local)';
            statusElement.style.color = 'green';
        }
    }
    
    // Charger et afficher les données précédemment parsées (si disponibles)
    loadStoredParsingResults();
}

/**
 * Nettoyer les éléments d'interface dupliqués
 */
function cleanupDuplicateElements() {
    // Supprimer les boutons d'analyse GPT dupliqués
    const gptButtons = document.querySelectorAll('#analyze-with-gpt');
    if (gptButtons.length > 1) {
        for (let i = 1; i < gptButtons.length; i++) {
            if (gptButtons[i].parentNode) {
                gptButtons[i].parentNode.removeChild(gptButtons[i]);
            }
        }
    }
    
    // Éviter les conflits avec d'autres scripts
    window.jobParserInitialized = true;
}

/**
 * Connecter les événements aux éléments d'interface
 */
function connectUiEvents() {
    // Connecter le bouton d'analyse GPT
    const analyzeButton = document.getElementById('analyze-with-gpt');
    if (analyzeButton) {
        analyzeButton.addEventListener('click', handleAnalyzeButtonClick);
    }
    
    // Connecter le bouton d'analyse texte
    const analyzeTextButton = document.getElementById('analyze-job-text');
    if (analyzeTextButton) {
        analyzeTextButton.addEventListener('click', handleAnalyzeTextClick);
    }
    
    // Connecter l'événement du fichier
    const fileInput = document.getElementById('job-file-input');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileInputChange);
    }
}

/**
 * Gestion du clic sur le bouton "Analyser avec GPT"
 */
async function handleAnalyzeButtonClick() {
    // Récupérer le texte ou le fichier
    const textarea = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    let jobText = '';
    
    if (textarea && textarea.value.trim()) {
        jobText = textarea.value.trim();
    } else if (fileInput && fileInput.files.length > 0) {
        const file = fileInput.files[0];
        try {
            jobText = await readFileAsText(file);
        } catch (error) {
            console.error('Erreur lors de la lecture du fichier:', error);
            showNotification('Erreur lors de la lecture du fichier.', 'error');
            return;
        }
    }
    
    if (!jobText) {
        showNotification('Veuillez entrer du texte ou sélectionner un fichier.', 'error');
        return;
    }
    
    // Afficher le chargement
    const loader = document.getElementById('analysis-loader');
    if (loader) loader.style.display = 'flex';
    
    // Mettre à jour le statut
    const statusElement = document.getElementById('gpt-analyze-status');
    if (statusElement) statusElement.textContent = 'Analyse en cours...';
    
    // Désactiver le bouton pendant l'analyse
    analyzeButton.disabled = true;
    
    try {
        // Simuler un délai d'analyse
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Analyser le texte avec notre analyseur local amélioré
        const result = analyzeJobPostingEnhanced(jobText);
        
        // Sauvegarder et afficher les résultats
        saveParsingResults(result);
        showJobResults(result);
        
        showNotification('Analyse terminée avec succès !', 'success');
        
        // Mettre à jour le statut
        if (statusElement) statusElement.textContent = 'Analyse réussie !';
    } catch (error) {
        console.error('Erreur lors de l\'analyse:', error);
        showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
        
        // Mettre à jour le statut
        if (statusElement) statusElement.textContent = 'Erreur: ' + error.message;
    } finally {
        // Réactiver le bouton
        analyzeButton.disabled = false;
        
        // Masquer le chargement
        if (loader) loader.style.display = 'none';
    }
}

/**
 * Gestion du clic sur le bouton d'analyse de texte
 */
async function handleAnalyzeTextClick() {
    const textarea = document.getElementById('job-description-text');
    if (!textarea || !textarea.value.trim()) {
        showNotification('Veuillez entrer du texte à analyser.', 'error');
        return;
    }
    
    // Afficher le chargement
    const loader = document.getElementById('analysis-loader');
    if (loader) loader.style.display = 'flex';
    
    try {
        // Simuler un délai d'analyse
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Analyser le texte avec notre analyseur local simple
        const result = analyzeJobPosting(textarea.value.trim());
        
        // Sauvegarder et afficher les résultats
        saveParsingResults(result);
        showJobResults(result);
        
        showNotification('Analyse terminée avec succès !', 'success');
    } catch (error) {
        console.error('Erreur lors de l\'analyse:', error);
        showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
    } finally {
        // Masquer le chargement
        if (loader) loader.style.display = 'none';
    }
}

/**
 * Gestion du changement de fichier
 */
async function handleFileInputChange(event) {
    if (!event.target.files.length) return;
    
    const file = event.target.files[0];
    
    // Vérifier la taille du fichier (max 5MB)
    const maxSizeInBytes = 5 * 1024 * 1024;
    if (file.size > maxSizeInBytes) {
        showNotification('Le fichier est trop volumineux. La taille maximale est de 5MB.', 'error');
        return;
    }
    
    // Vérifier le type de fichier
    const acceptedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    ];
    
    if (!acceptedTypes.includes(file.type)) {
        showNotification('Format de fichier non supporté. Veuillez utiliser PDF, DOC, DOCX ou TXT.', 'error');
        return;
    }
    
    // Afficher le badge de fichier
    const fileName = document.getElementById('file-name');
    const fileBadge = document.getElementById('file-badge');
    if (fileName && fileBadge) {
        fileName.textContent = file.name;
        fileBadge.style.display = 'inline-flex';
    }
    
    showNotification('Fichier sélectionné avec succès', 'success');
    
    // Analyser automatiquement le fichier
    const loader = document.getElementById('analysis-loader');
    if (loader) loader.style.display = 'flex';
    
    try {
        // Lire le fichier comme texte
        const text = await readFileAsText(file);
        
        // Simuler un délai d'analyse
        await new Promise(resolve => setTimeout(resolve, 1200));
        
        // Analyser le texte
        const result = analyzeJobPostingEnhanced(text);
        
        // Sauvegarder et afficher les résultats
        saveParsingResults(result);
        showJobResults(result);
        
        showNotification('Fichier analysé avec succès !', 'success');
    } catch (error) {
        console.error('Erreur lors de l\'analyse du fichier:', error);
        showNotification('Erreur lors de l\'analyse du fichier: ' + error.message, 'error');
    } finally {
        // Masquer le chargement
        if (loader) loader.style.display = 'none';
    }
}

/**
 * Lire un fichier comme texte
 */
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => resolve(e.target.result);
        reader.onerror = e => reject(new Error('Erreur lors de la lecture du fichier'));
        reader.readAsText(file);
    });
}

/**
 * Analyse simplifiée d'une fiche de poste
 */
function analyzeJobPosting(text) {
    // Structure de résultat
    const result = {
        title: '',
        company: '',
        location: '',
        contract_type: '',
        skills: [],
        experience: '',
        education: '',
        salary: '',
        responsibilities: [],
        benefits: []
    };
    
    try {
        // Titre du poste
        const titlePatterns = [
            /(?:^|\n)[\s•]*Poste[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Intitulé du poste[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Offre d'emploi[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*([\w\s\-']+(?:développeur|ingénieur|technicien|consultant|manager|responsable|directeur|analyste)[\w\s\-']+)(?:\n|$)/i
        ];
        
        for (const pattern of titlePatterns) {
            const match = text.match(pattern);
            if (match) {
                result.title = match[1].trim();
                break;
            }
        }
        
        // Entreprise
        const companyPatterns = [
            /(?:^|\n)[\s•]*Entreprise[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Société[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Employeur[\s:]*(.+?)(?:\n|$)/i
        ];
        
        for (const pattern of companyPatterns) {
            const match = text.match(pattern);
            if (match) {
                result.company = match[1].trim();
                break;
            }
        }
        
        // Localisation
        const locationPatterns = [
            /(?:^|\n)[\s•]*Lieu[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Localisation[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Localité[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Ville[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*(?:à|a) ((?:Paris|Lyon|Marseille|Lille|Toulouse|Bordeaux|Nantes|Nice|Strasbourg|Rennes|Grenoble|Montpellier)(?:\s*(?:\(.*?\))?)?)(?:\n|$)/i
        ];
        
        for (const pattern of locationPatterns) {
            const match = text.match(pattern);
            if (match) {
                result.location = match[1].trim();
                break;
            }
        }
        
        // Type de contrat
        const contractPatterns = [
            /(?:^|\n)[\s•]*Type de contrat[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Contrat[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*(CDI|CDD|Stage|Alternance|Intérim|Freelance)(?:\n|$)/i
        ];
        
        for (const pattern of contractPatterns) {
            const match = text.match(pattern);
            if (match) {
                result.contract_type = match[1].trim();
                break;
            }
        }
        
        // Compétences
        const commonTechSkills = [
            'JavaScript', 'Python', 'Java', 'C#', 'C++', 'Ruby', 'PHP', 'Swift', 'Kotlin',
            'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring', 'ASP.NET',
            'HTML', 'CSS', 'SQL', 'NoSQL', 'MongoDB', 'MySQL', 'PostgreSQL', 'Oracle',
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'DevOps', 'CI/CD',
            'Git', 'Jenkins', 'Jira', 'Agile', 'Scrum', 'TDD', 'DDD'
        ];
        
        // Rechercher les compétences dans le texte
        commonTechSkills.forEach(skill => {
            const regex = new RegExp(`\\b${skill}\\b`, 'i');
            if (regex.test(text)) {
                result.skills.push(skill);
            }
        });
        
        // Expérience requise
        const expPatterns = [
            /(?:^|\n)[\s•]*Expérience[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Années d'expérience[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*([\d]+[\s]*ans d'expérience)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Expérience requise[\s:]*(.+?)(?:\n|$)/i,
            /expérience (?:de|d'au moins|minimum|>|supérieure à) (\d+)[\s-]*ans/i
        ];
        
        for (const pattern of expPatterns) {
            const match = text.match(pattern);
            if (match) {
                result.experience = match[1].trim();
                break;
            }
        }
        
        // Formation
        const eduPatterns = [
            /(?:^|\n)[\s•]*Formation[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Diplôme[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Niveau d'études[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Éducation[\s:]*(.+?)(?:\n|$)/i,
            /(?:Bac|Master|Licence)[\s+](\+\d|1|2|3|4|5)/i
        ];
        
        for (const pattern of eduPatterns) {
            const match = text.match(pattern);
            if (match) {
                result.education = match[1].trim();
                break;
            }
        }
        
        // Salaire
        const salaryPatterns = [
            /(?:^|\n)[\s•]*Salaire[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Rémunération[\s:]*(.+?)(?:\n|$)/i,
            /(?:^|\n)[\s•]*Package[\s:]*(.+?)(?:\n|$)/i,
            /(\d{2,3}[ -]?(?:à|a|-)[ -]?\d{2,3}[ -]?K€)/i,
            /(\d{2,3}[ -]?(?:à|a|-)[ -]?\d{2,3}[ -]?K)/i,
            /salaire[\s:]*de[\s:]*([\d\s.,]+)[\s]*(?:€|k€|euros)/i
        ];
        
        for (const pattern of salaryPatterns) {
            const match = text.match(pattern);
            if (match) {
                result.salary = match[1].trim();
                break;
            }
        }
        
        // Extraire les paragraphes pour les responsabilités
        const paragraphs = text.split(/\n\s*\n/);
        const responsibilityKeywords = ['mission', 'responsabilité', 'tâche', 'rôle', 'projet'];
        
        for (const paragraph of paragraphs) {
            if (responsibilityKeywords.some(keyword => paragraph.toLowerCase().includes(keyword))) {
                // Extraire les lignes qui commencent par des tirets ou des puces
                const lines = paragraph.split('\n')
                    .map(line => line.trim())
                    .filter(line => line.startsWith('-') || line.startsWith('•'));
                
                if (lines.length > 0) {
                    result.responsibilities = lines.map(line => line.replace(/^[-•]\s*/, ''));
                } else if (paragraph.length > 30 && paragraph.length < 500) {
                    // Si pas de liste à puces mais paragraphe de taille raisonnable
                    result.responsibilities.push(paragraph);
                }
                break;
            }
        }
        
        // Extraire les avantages
        const benefitKeywords = ['avantage', 'bénéfice', 'offrons', 'proposons', 'ticket restaurant', 'mutuelle', 'télétravail'];
        
        for (const paragraph of paragraphs) {
            if (benefitKeywords.some(keyword => paragraph.toLowerCase().includes(keyword))) {
                // Extraire les lignes qui commencent par des tirets ou des puces
                const lines = paragraph.split('\n')
                    .map(line => line.trim())
                    .filter(line => line.startsWith('-') || line.startsWith('•'));
                
                if (lines.length > 0) {
                    result.benefits = lines.map(line => line.replace(/^[-•]\s*/, ''));
                }
                break;
            }
        }
        
        // Si certains champs sont vides, ajouter des valeurs par défaut
        if (!result.title) result.title = "Poste à pourvoir";
        if (!result.company) result.company = "Entreprise";
        if (!result.location) result.location = "France";
        if (result.skills.length === 0) result.skills = ["Compétence technique"];
        
        return result;
    } catch (error) {
        console.error('Erreur lors de l\'analyse:', error);
        return result;
    }
}

/**
 * Analyse améliorée d'une fiche de poste (simulation GPT)
 */
function analyzeJobPostingEnhanced(text) {
    // Obtenir les résultats de base
    const basicResult = analyzeJobPosting(text);
    
    // Améliorer les résultats
    const enhancedResult = { ...basicResult };
    
    // Essayer d'extraire plus d'informations
    try {
        // Amélioration du titre
        if (!enhancedResult.title || enhancedResult.title === "Poste à pourvoir") {
            // Chercher des titres de poste communs
            const commonTitles = [
                "Développeur", "Ingénieur", "Chef de projet", "Product Owner", "Scrum Master",
                "DevOps", "Data Scientist", "Analyste", "Consultant", "Architecte"
            ];
            
            const specializations = [
                "Frontend", "Backend", "Fullstack", "Web", "Mobile", "IoT", "Cloud",
                "Java", "JavaScript", "Python", "PHP", "C#", ".NET", "Ruby", "Go"
            ];
            
            // Chercher le premier titre qui apparaît dans le texte
            for (const title of commonTitles) {
                const regex = new RegExp(`\\b${title}\\b`, 'i');
                if (regex.test(text)) {
                    // Chercher une spécialisation pour compléter le titre
                    for (const spec of specializations) {
                        const specRegex = new RegExp(`\\b${spec}\\b`, 'i');
                        if (specRegex.test(text)) {
                            enhancedResult.title = `${title} ${spec}`;
                            break;
                        }
                    }
                    
                    if (enhancedResult.title === "Poste à pourvoir") {
                        enhancedResult.title = title;
                    }
                    break;
                }
            }
            
            // En dernier recours, utiliser le début du texte
            if (enhancedResult.title === "Poste à pourvoir") {
                const firstLine = text.split('\n')[0].trim();
                if (firstLine.length > 5 && firstLine.length < 100) {
                    enhancedResult.title = firstLine;
                }
            }
        }
        
        // Amélioration de la détection des compétences
        const softSkills = [
            "Communication", "Travail en équipe", "Autonomie", "Rigueur", "Organisation",
            "Adaptabilité", "Créativité", "Résolution de problèmes", "Leadership", "Gestion du temps"
        ];
        
        // Ajouter des soft skills si détectés
        softSkills.forEach(skill => {
            const regex = new RegExp(`\\b${skill}\\b`, 'i');
            if (regex.test(text) && !enhancedResult.skills.includes(skill)) {
                enhancedResult.skills.push(skill);
            }
        });
        
        // Amélioration des responsabilités
        if (enhancedResult.responsibilities.length === 0) {
            // Analyser le texte pour trouver les responsabilités
            const sections = text.split(/(?:^|\n)#+\s*(?:Mission|Responsabilit|Tâche|Rôle|Description du poste)/i);
            
            if (sections.length > 1) {
                // Extraire les lignes qui ressemblent à des responsabilités
                const responsibilitySection = sections[1].split(/(?:^|\n)#+\s*(?:Profil|Compétence|Requis|Avantage)/i)[0];
                const lines = responsibilitySection.split('\n')
                    .map(line => line.trim())
                    .filter(line => (line.startsWith('-') || line.startsWith('•') || line.startsWith('*')) && line.length > 10);
                
                if (lines.length > 0) {
                    enhancedResult.responsibilities = lines.map(line => line.replace(/^[-•*]\s*/, ''));
                } else {
                    // Si pas de liste à puces, extraire des phrases
                    const sentences = responsibilitySection.match(/[^.!?]+[.!?]+/g);
                    if (sentences && sentences.length > 0) {
                        enhancedResult.responsibilities = sentences
                            .map(s => s.trim())
                            .filter(s => s.length > 20 && s.length < 200)
                            .slice(0, 5);
                    }
                }
            }
        }
        
        // Amélioration des avantages
        if (enhancedResult.benefits.length === 0) {
            // Vérifier pour des avantages communs
            const commonBenefits = [
                "Télétravail", "Tickets restaurant", "Mutuelle", "Prévoyance", "RTT",
                "Locaux modernes", "Événements d'équipe", "Formation continue", "Plan d'épargne",
                "Horaires flexibles", "Prime"
            ];
            
            commonBenefits.forEach(benefit => {
                const regex = new RegExp(`\\b${benefit}\\b`, 'i');
                if (regex.test(text)) {
                    enhancedResult.benefits.push(benefit);
                }
            });
        }
        
        // Amélioration du type de contrat
        if (!enhancedResult.contract_type) {
            const contractTypes = {
                "CDI": /\bCDI\b|contrat à durée indéterminée/i,
                "CDD": /\bCDD\b|contrat à durée déterminée/i,
                "Stage": /\bstage\b/i,
                "Alternance": /\balternance\b|contrat d'apprentissage|contrat de professionnalisation/i,
                "Freelance": /\bfreelance\b|indépendant/i
            };
            
            for (const [type, regex] of Object.entries(contractTypes)) {
                if (regex.test(text)) {
                    enhancedResult.contract_type = type;
                    break;
                }
            }
        }
    } catch (error) {
        console.error('Erreur lors de l\'amélioration de l\'analyse:', error);
    }
    
    return enhancedResult;
}

/**
 * Sauvegarder les résultats d'analyse
 */
function saveParsingResults(result) {
    try {
        // Sauvegarder dans sessionStorage et localStorage pour persistance
        sessionStorage.setItem('parsedJobData', JSON.stringify(result));
        localStorage.setItem('parsedJobData', JSON.stringify(result));
    } catch (error) {
        console.error('Erreur lors de la sauvegarde des résultats:', error);
    }
}

/**
 * Charger les résultats d'analyse précédemment stockés
 */
function loadStoredParsingResults() {
    try {
        // Essayer d'abord sessionStorage, puis localStorage
        let storedData = sessionStorage.getItem('parsedJobData') || localStorage.getItem('parsedJobData');
        
        if (storedData) {
            const parsedData = JSON.parse(storedData);
            showJobResults(parsedData);
        }
    } catch (error) {
        console.error('Erreur lors du chargement des résultats stockés:', error);
    }
}
