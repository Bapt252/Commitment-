/**
 * Analyseur de fiches de poste côté client
 * Ce script utilise des techniques de traitement de texte dans le navigateur
 * pour extraire des informations pertinentes des fichiers téléchargés.
 */

class JobPostingAnalyzer {
    constructor() {
        // Mots-clés pour détecter les différentes sections
        this.keywords = {
            title: [
                'poste', 'intitulé du poste', 'titre', 'position', 'job title',
                'recrutement', 'recherche', 'recrute', 'recrutement pour', 'à pourvoir'
            ],
            skills: [
                'compétences', 'skills', 'expertise', 'maîtrise', 'connaissances',
                'technologies', 'outils', 'savoir-faire', 'techniques', 'qualifications',
                'tech stack', 'stack', 'environnement technique'
            ],
            experience: [
                'expérience', 'années', 'ans', 'séniorité', 'niveau', 'profil',
                'experience', 'expérimenté', 'junior', 'senior', 'confirmé'
            ],
            contract: [
                'contrat', 'cdi', 'cdd', 'stage', 'alternance', 'freelance',
                'intérim', 'temps plein', 'temps partiel', 'contract', 'full-time',
                'part-time', 'permanent', 'temporary'
            ],
            responsibilities: [
                'missions', 'responsabilités', 'tâches', 'activités', 'attributions',
                'rôle', 'au quotidien', 'responsibilities', 'duties', 'mission'
            ],
            requirements: [
                'requis', 'prérequis', 'exigences', 'qualifications', 'diplôme',
                'formation', 'bac', 'master', 'licence', 'requirements', 
                'education', 'diploma'
            ],
            benefits: [
                'avantages', 'rémunération', 'salaire', 'package', 'prime',
                'bonus', 'télétravail', 'remote', 'benefits', 'salary', 'compensation',
                'rtt', 'mutuelle', 'tickets restaurant', 'comité d\'entreprise'
            ],
            company: [
                'entreprise', 'société', 'organisation', 'cabinet', 'établissement',
                'group', 'company', 'firm', 'business', 'agency'
            ],
            location: [
                'lieu', 'localisation', 'adresse', 'ville', 'région',
                'département', 'location', 'address', 'city', 'region',
                'siège', 'headquarters', 'locaux', 'bureaux', 'offices'
            ]
        };

        // Motifs pour détecter des formats spécifiques
        this.patterns = {
            experience: [
                /(\d+)[\s-]+(\d+)?\s*ans?/gi, // 2-5 ans, 3 ans, etc.
                /(\d+)\+\s*ans?/gi,  // 5+ ans
                /minimum\s*(\d+)\s*ans?/gi, // minimum 2 ans
                /au\s*moins\s*(\d+)\s*ans?/gi, // au moins 3 ans
                /expérience\s*de\s*(\d+)[\s-]+(\d+)?\s*ans?/gi, // expérience de 2-3 ans
                /expérience\s*(\d+)[\s-]+(\d+)?\s*ans?/gi, // expérience 2-3 ans
                /(junior|débutant|confirmé|senior|expert)/gi // niveaux d'expérience
            ],
            contract: [
                /(cdi|cdd|stage|alternance|apprentissage|freelance|intérim)/gi,
                /(temps plein|temps partiel|full-time|part-time)/gi,
                /(permanent|temporary)/gi
            ]
        };
    }

    /**
     * Analyse le texte d'une fiche de poste pour en extraire les informations pertinentes
     * @param {string} text - Le texte à analyser
     * @returns {object} Les informations extraites
     */
    analyze(text) {
        console.log("Analyzing text:", text.substring(0, 100) + "...");
        
        // Normaliser le texte (supprimer les caractères spéciaux, standardiser la casse)
        const normalizedText = this.normalizeText(text);
        
        // Séparer le texte en paragraphes
        const paragraphs = this.splitIntoParagraphs(normalizedText);
        
        // Extraire les différentes informations
        const result = {
            title: this.extractTitle(paragraphs),
            required_skills: this.extractSkills(paragraphs),
            preferred_skills: [],
            experience: this.extractExperience(paragraphs),
            contract_type: this.extractContractType(paragraphs),
            responsibilities: this.extractResponsibilities(paragraphs),
            requirements: this.extractRequirements(paragraphs),
            benefits: this.extractBenefits(paragraphs),
            company: this.extractCompany(paragraphs),
            location: this.extractLocation(paragraphs)
        };
        
        // Séparer les compétences requises et souhaitées (basé sur le contexte)
        this.separateSkills(result, normalizedText);
        
        console.log("Analysis result:", result);
        return result;
    }
    
    /**
     * Normalise le texte pour faciliter l'analyse
     */
    normalizeText(text) {
        return text
            .replace(/\r\n/g, '\n')  // Normaliser les sauts de ligne
            .replace(/\t/g, ' ')     // Remplacer les tabulations par des espaces
            .replace(/\s+/g, ' ')    // Remplacer les séquences d'espaces par un seul espace
            .replace(/•/g, '\n• ')   // Ajouter un saut de ligne avant les puces
            .replace(/\n-/g, '\n• ') // Convertir les tirets en début de ligne en puces
            .trim();                 // Supprimer les espaces au début et à la fin
    }
    
    /**
     * Découpe le texte en paragraphes
     */
    splitIntoParagraphs(text) {
        return text.split('\n').map(p => p.trim()).filter(p => p.length > 0);
    }
    
    /**
     * Extrait le titre du poste
     */
    extractTitle(paragraphs) {
        // Essayer de trouver un titre évident dans les premiers paragraphes
        for (let i = 0; i < Math.min(paragraphs.length, 10); i++) {
            const paragraph = paragraphs[i].toLowerCase();
            
            // Vérifier si le paragraphe contient des mots-clés de titre
            if (this.keywords.title.some(keyword => paragraph.includes(keyword.toLowerCase()))) {
                // Extraire le titre potentiel (texte après le mot-clé)
                for (const keyword of this.keywords.title) {
                    if (paragraph.includes(keyword.toLowerCase())) {
                        const parts = paragraph.split(keyword.toLowerCase());
                        if (parts.length > 1 && parts[1].trim().length > 0) {
                            // Nettoyer et capitaliser le titre
                            let title = parts[1].trim()
                                .replace(/^[:\s-]+/, '')  // Supprimer les caractères spéciaux au début
                                .replace(/[.!?].*$/, '')  // Supprimer tout après un point, point d'exclamation ou d'interrogation
                                .trim();
                            
                            // Capitaliser le titre
                            title = title.charAt(0).toUpperCase() + title.slice(1);
                            
                            if (title.length > 3 && title.length < 50) {
                                return title;
                            }
                        }
                    }
                }
            }
            
            // Si le paragraphe est court et en majuscules, c'est probablement un titre
            if (paragraph.length > 3 && paragraph.length < 50 && 
                paragraph === paragraph.toUpperCase() && 
                !paragraph.includes('•')) {
                return paragraph.charAt(0).toUpperCase() + paragraph.slice(1).toLowerCase();
            }
        }
        
        // Tenter une autre approche pour les 5 premiers paragraphes
        for (let i = 0; i < Math.min(paragraphs.length, 5); i++) {
            const paragraph = paragraphs[i];
            
            // Si c'est une phrase courte sans ponctuation, c'est probablement un titre
            if (paragraph.length > 3 && paragraph.length < 60 && 
                !paragraph.includes('.') && !paragraph.includes('•')) {
                // Capitaliser correctement
                return paragraph.charAt(0).toUpperCase() + paragraph.slice(1);
            }
        }
        
        // Revenir au premier paragraphe si aucun titre n'a été trouvé
        if (paragraphs.length > 0) {
            const firstPara = paragraphs[0];
            if (firstPara.length < 60) {
                return firstPara;
            } else {
                // Prendre les premiers mots significatifs
                return firstPara.split(' ').slice(0, 6).join(' ') + '...';
            }
        }
        
        return "Poste Non Spécifié";
    }
    
    /**
     * Extrait les compétences requises
     */
    extractSkills(paragraphs) {
        const skills = new Set();
        
        // Rechercher des paragraphes contenant des mots-clés sur les compétences
        for (const paragraph of paragraphs) {
            const lowerPara = paragraph.toLowerCase();
            
            // Vérifier si le paragraphe contient des mots-clés de compétences
            if (this.keywords.skills.some(keyword => lowerPara.includes(keyword.toLowerCase()))) {
                // Rechercher des puces qui indiquent souvent des compétences
                if (paragraph.includes('•')) {
                    const bulletPoints = paragraph.split('•').map(p => p.trim()).filter(p => p.length > 0);
                    bulletPoints.forEach(point => {
                        // Nettoyer et ajouter chaque compétence
                        const skill = point.split(',')[0].split('(')[0].trim();
                        if (skill.length > 1 && skill.length < 40) {
                            skills.add(skill);
                        }
                    });
                } else {
                    // Extraire des mots ou groupes de mots qui pourraient être des compétences
                    const potentialSkills = paragraph.split(/[,;:]/).map(s => s.trim());
                    potentialSkills.forEach(skill => {
                        if (skill.length > 1 && skill.length < 40 && 
                            !skill.toLowerCase().includes('année') && 
                            !skill.toLowerCase().includes('compétence')) {
                            skills.add(skill);
                        }
                    });
                }
            }
            
            // Rechercher des technologies spécifiques (mots commençant par majuscule ou avec des caractères spéciaux)
            const techWords = paragraph.split(/[,;\s]/).map(w => w.trim()).filter(w => w.length > 1);
            for (const word of techWords) {
                // Les technologies ont souvent une majuscule ou des caractères spéciaux
                if ((word.charAt(0) === word.charAt(0).toUpperCase() && 
                     word.charAt(0) !== word.charAt(0).toLowerCase()) || 
                    word.includes('.') || word.includes('#') || word.includes('+')) {
                    
                    // Vérifier si c'est une technologie connue
                    const techWords = [
                        "JavaScript", "Python", "Java", "C#", "C++", "Ruby", "Go", "PHP", "Swift",
                        "Kotlin", "TypeScript", "Rust", "SQL", "NoSQL", "React", "Angular", "Vue",
                        "Node.js", "Express", "Django", "Flask", "Spring", "ASP.NET", "Laravel",
                        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub",
                        "MongoDB", "MySQL", "PostgreSQL", "Oracle", "Redis", "Elasticsearch",
                        "HTML", "CSS", "SASS", "LESS", "Bootstrap", "Tailwind", "jQuery", "D3.js",
                        "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "R", "Tableau",
                        "Power BI", "Excel", "Word", "PowerPoint", "Photoshop", "Illustrator",
                        "Figma", "Sketch", "InDesign", "Jira", "Confluence", "Trello", "Asana", 
                        "Agile", "Scrum", "Kanban", "DevOps", "CI/CD", "REST", "GraphQL", "SOAP"
                    ];
                    
                    const lowerWord = word.toLowerCase();
                    if (techWords.some(tech => tech.toLowerCase() === lowerWord)) {
                        skills.add(word);
                    }
                }
            }
        }
        
        return Array.from(skills);
    }

    /**
     * Sépare les compétences requises et souhaitées
     */
    separateSkills(result, text) {
        // Si nous n'avons pas beaucoup de compétences, ne pas séparer
        if (result.required_skills.length <= 3) {
            return;
        }
        
        const preferredKeywords = [
            'souhaité', 'idéalement', 'apprécié', 'un plus', 'bonus',
            'preferred', 'plus', 'idéal', 'atout', 'avantage'
        ];
        
        // Rechercher des compétences préférées dans le texte
        const preferredSkills = new Set();
        
        for (const skill of result.required_skills) {
            // Rechercher le contexte autour de la compétence
            const index = text.indexOf(skill);
            if (index >= 0) {
                const contextBefore = text.substring(Math.max(0, index - 100), index);
                if (preferredKeywords.some(keyword => contextBefore.toLowerCase().includes(keyword))) {
                    preferredSkills.add(skill);
                }
            }
        }
        
        // Mettre à jour les compétences requises et préférées
        if (preferredSkills.size > 0) {
            result.required_skills = result.required_skills.filter(skill => !preferredSkills.has(skill));
            result.preferred_skills = Array.from(preferredSkills);
        }
    }

    /**
     * Extrait l'expérience requise
     */
    extractExperience(paragraphs) {
        // Rechercher des motifs d'expérience dans le texte
        for (const paragraph of paragraphs) {
            const lowerPara = paragraph.toLowerCase();
            
            // Vérifier si le paragraphe contient des mots-clés d'expérience
            if (this.keywords.experience.some(keyword => lowerPara.includes(keyword.toLowerCase()))) {
                // Rechercher des motifs spécifiques d'expérience
                for (const pattern of this.patterns.experience) {
                    const match = lowerPara.match(pattern);
                    if (match) {
                        return paragraph.substring(
                            Math.max(0, paragraph.toLowerCase().indexOf(match[0]) - 5),
                            Math.min(paragraph.length, paragraph.toLowerCase().indexOf(match[0]) + match[0].length + 20)
                        ).trim();
                    }
                }
                
                // Si on trouve un paragraphe court contenant le mot "expérience", le retourner
                if (lowerPara.includes('expérience') && paragraph.length < 100) {
                    return paragraph.trim();
                }
            }
        }
        
        return "Non spécifiée";
    }

    /**
     * Extrait le type de contrat
     */
    extractContractType(paragraphs) {
        // Rechercher des motifs de contrat dans le texte
        for (const paragraph of paragraphs) {
            const lowerPara = paragraph.toLowerCase();
            
            // Vérifier si le paragraphe contient des mots-clés de contrat
            if (this.keywords.contract.some(keyword => lowerPara.includes(keyword.toLowerCase()))) {
                // Rechercher des motifs spécifiques de contrat
                for (const pattern of this.patterns.contract) {
                    const match = lowerPara.match(pattern);
                    if (match) {
                        // Convertir en format standard
                        const contractType = match[0].toUpperCase();
                        if (contractType.includes("CDI")) return "CDI";
                        if (contractType.includes("CDD")) return "CDD";
                        if (contractType.includes("STAGE")) return "Stage";
                        if (contractType.includes("ALTERNANCE") || contractType.includes("APPRENTISSAGE")) return "Alternance";
                        if (contractType.includes("FREELANCE")) return "Freelance";
                        if (contractType.includes("INTÉRIM")) return "Intérim";
                        
                        // Par défaut, retourner la correspondance
                        return match[0].charAt(0).toUpperCase() + match[0].slice(1).toLowerCase();
                    }
                }
            }
        }
        
        return "Non spécifié";
    }

    /**
     * Extrait les responsabilités
     */
    extractResponsibilities(paragraphs) {
        const responsibilities = [];
        let inResponsibilitiesSection = false;
        
        for (const paragraph of paragraphs) {
            const lowerPara = paragraph.toLowerCase();
            
            // Détecter une section de responsabilités
            if (this.keywords.responsibilities.some(keyword => lowerPara.includes(keyword.toLowerCase()))) {
                inResponsibilitiesSection = true;
                continue;
            }
            
            // Si on est dans une section de responsabilités et qu'on trouve une puce, c'est probablement une responsabilité
            if (inResponsibilitiesSection && paragraph.includes('•')) {
                const bulletPoints = paragraph.split('•').map(p => p.trim()).filter(p => p.length > 0);
                bulletPoints.forEach(point => {
                    if (point.length > 5 && point.length < 200) {
                        responsibilities.push(point);
                    }
                });
            } 
            // Si on trouve un paragraphe court dans la section de responsabilités, c'est peut-être aussi une responsabilité
            else if (inResponsibilitiesSection && paragraph.length > 5 && paragraph.length < 200) {
                responsibilities.push(paragraph);
            }
            
            // Sortir de la section de responsabilités si on trouve une nouvelle section
            if (inResponsibilitiesSection && 
                (this.keywords.skills.some(keyword => lowerPara.includes(keyword.toLowerCase())) ||
                 this.keywords.requirements.some(keyword => lowerPara.includes(keyword.toLowerCase())) ||
                 this.keywords.benefits.some(keyword => lowerPara.includes(keyword.toLowerCase())))) {
                inResponsibilitiesSection = false;
            }
            
            // Limiter à 5 responsabilités
            if (responsibilities.length >= 5) {
                break;
            }
        }
        
        return responsibilities;
    }

    /**
     * Extrait les prérequis
     */
    extractRequirements(paragraphs) {
        const requirements = [];
        let inRequirementsSection = false;
        
        for (const paragraph of paragraphs) {
            const lowerPara = paragraph.toLowerCase();
            
            // Détecter une section de prérequis
            if (this.keywords.requirements.some(keyword => lowerPara.includes(keyword.toLowerCase()))) {
                inRequirementsSection = true;
                continue;
            }
            
            // Si on est dans une section de prérequis et qu'on trouve une puce, c'est probablement un prérequis
            if (inRequirementsSection && paragraph.includes('•')) {
                const bulletPoints = paragraph.split('•').map(p => p.trim()).filter(p => p.length > 0);
                bulletPoints.forEach(point => {
                    if (point.length > 5 && point.length < 200) {
                        requirements.push(point);
                    }
                });
            } 
            // Si on trouve un paragraphe court dans la section de prérequis, c'est peut-être aussi un prérequis
            else if (inRequirementsSection && paragraph.length > 5 && paragraph.length < 200) {
                requirements.push(paragraph);
            }
            
            // Sortir de la section de prérequis si on trouve une nouvelle section
            if (inRequirementsSection && 
                (this.keywords.skills.some(keyword => lowerPara.includes(keyword.toLowerCase())) ||
                 this.keywords.responsibilities.some(keyword => lowerPara.includes(keyword.toLowerCase())) ||
                 this.keywords.benefits.some(keyword => lowerPara.includes(keyword.toLowerCase())))) {
                inRequirementsSection = false;
            }
            
            // Limiter à 5 prérequis
            if (requirements.length >= 5) {
                break;
            }
        }
        
        return requirements;
    }

    /**
     * Extrait les avantages
     */
    extractBenefits(paragraphs) {
        const benefits = [];
        let inBenefitsSection = false;
        
        for (const paragraph of paragraphs) {
            const lowerPara = paragraph.toLowerCase();
            
            // Détecter une section d'avantages
            if (this.keywords.benefits.some(keyword => lowerPara.includes(keyword.toLowerCase()))) {
                inBenefitsSection = true;
                continue;
            }
            
            // Si on est dans une section d'avantages et qu'on trouve une puce, c'est probablement un avantage
            if (inBenefitsSection && paragraph.includes('•')) {
                const bulletPoints = paragraph.split('•').map(p => p.trim()).filter(p => p.length > 0);
                bulletPoints.forEach(point => {
                    if (point.length > 2 && point.length < 100) {
                        benefits.push(point);
                    }
                });
            } 
            // Si on trouve un paragraphe court dans la section d'avantages, c'est peut-être aussi un avantage
            else if (inBenefitsSection && paragraph.length > 2 && paragraph.length < 100) {
                benefits.push(paragraph);
            }
            
            // Sortir de la section d'avantages si on trouve une nouvelle section
            if (inBenefitsSection && 
                (this.keywords.skills.some(keyword => lowerPara.includes(keyword.toLowerCase())) ||
                 this.keywords.responsibilities.some(keyword => lowerPara.includes(keyword.toLowerCase())) ||
                 this.keywords.requirements.some(keyword => lowerPara.includes(keyword.toLowerCase())))) {
                inBenefitsSection = false;
            }
            
            // Limiter à 5 avantages
            if (benefits.length >= 5) {
                break;
            }
        }
        
        return benefits;
    }

    /**
     * Extrait le nom de l'entreprise
     */
    extractCompany(paragraphs) {
        // Rechercher un nom d'entreprise dans les premiers paragraphes
        for (let i = 0; i < Math.min(paragraphs.length, 10); i++) {
            const paragraph = paragraphs[i].toLowerCase();
            
            // Vérifier si le paragraphe contient des mots-clés d'entreprise
            if (this.keywords.company.some(keyword => paragraph.includes(keyword.toLowerCase()))) {
                // Extraire le nom de l'entreprise potentiel (texte après le mot-clé)
                for (const keyword of this.keywords.company) {
                    if (paragraph.includes(keyword.toLowerCase())) {
                        const parts = paragraph.split(keyword.toLowerCase());
                        if (parts.length > 1 && parts[1].trim().length > 0) {
                            // Nettoyer et capitaliser le nom
                            let company = parts[1].trim()
                                .replace(/^[:\s-]+/, '')  // Supprimer les caractères spéciaux au début
                                .replace(/[.!?].*$/, '')  // Supprimer tout après un point, point d'exclamation ou d'interrogation
                                .trim();
                            
                            // Capitaliser le nom
                            company = company.charAt(0).toUpperCase() + company.slice(1);
                            
                            if (company.length > 2 && company.length < 50) {
                                return company;
                            }
                        }
                    }
                }
            }
        }
        
        return "";
    }

    /**
     * Extrait la localisation
     */
    extractLocation(paragraphs) {
        // Rechercher une localisation dans les paragraphes
        for (const paragraph of paragraphs) {
            const lowerPara = paragraph.toLowerCase();
            
            // Vérifier si le paragraphe contient des mots-clés de localisation
            if (this.keywords.location.some(keyword => lowerPara.includes(keyword.toLowerCase()))) {
                // Extraire la localisation potentielle (texte après le mot-clé)
                for (const keyword of this.keywords.location) {
                    if (lowerPara.includes(keyword.toLowerCase())) {
                        const parts = paragraph.split(new RegExp(keyword, 'i'));
                        if (parts.length > 1 && parts[1].trim().length > 0) {
                            // Nettoyer la localisation
                            let location = parts[1].trim()
                                .replace(/^[:\s-]+/, '')  // Supprimer les caractères spéciaux au début
                                .replace(/[.!?].*$/, '')  // Supprimer tout après un point, point d'exclamation ou d'interrogation
                                .trim();
                            
                            if (location.length > 2 && location.length < 50) {
                                return location;
                            }
                        }
                    }
                }
            }
            
            // Rechercher des villes françaises connues
            const cities = [
                "Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", 
                "Strasbourg", "Montpellier", "Bordeaux", "Lille", "Rennes", 
                "Reims", "Le Havre", "Saint-Étienne", "Toulon", "Grenoble", 
                "Dijon", "Angers", "Nîmes", "Villeurbanne"
            ];
            
            for (const city of cities) {
                if (paragraph.includes(city)) {
                    // Extraire la phrase contenant la ville
                    const startIndex = Math.max(0, paragraph.indexOf(city) - 20);
                    const endIndex = Math.min(paragraph.length, paragraph.indexOf(city) + city.length + 20);
                    return paragraph.substring(startIndex, endIndex).trim();
                }
            }
        }
        
        return "";
    }
}

/**
 * Lit un fichier texte depuis un objet File
 */
async function readTextFromFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file);
    });
}

/**
 * Lit un fichier PDF depuis un objet File
 * Nécessite que PDF.js soit chargé sur la page
 */
async function readPdfFile(file) {
    // On va utiliser directement TextDecoder pour traiter le PDF comme du texte brut
    // Ce n'est pas parfait mais cela permet d'extraire du texte sans dépendance externe
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const content = e.target.result;
            
            // On va chercher des chaînes de texte lisibles dans le PDF
            // C'est une approche simpliste mais qui fonctionne pour des PDF simples
            let text = "";
            let inText = false;
            let buffer = "";
            
            // Convertir le buffer en chaîne
            const str = new TextDecoder().decode(new Uint8Array(content));
            
            // Rechercher des fragments de texte
            for (let i = 0; i < str.length; i++) {
                const c = str[i];
                
                // Les textes dans les PDF sont souvent entre parenthèses
                if (c === '(' && !inText) {
                    inText = true;
                    buffer = "";
                } else if (c === ')' && inText) {
                    inText = false;
                    
                    // Ajouter le buffer au texte si c'est probablement du texte
                    if (buffer.length > 2 && /[a-zA-Z0-9]/.test(buffer)) {
                        text += buffer + " ";
                    }
                } else if (inText) {
                    buffer += c;
                }
            }
            
            // Si nous n'avons pas trouvé de texte, essayer une autre approche
            if (text.length < 100) {
                // Rechercher des chaînes de caractères ASCII imprimables
                const regex = /[\x20-\x7E]{4,}/g;
                const matches = str.match(regex);
                
                if (matches && matches.length > 0) {
                    text = matches.join(" ");
                }
            }
            
            resolve(text);
        };
        reader.onerror = reject;
        reader.readAsArrayBuffer(file);
    });
}

/**
 * Détecte le type de fichier et lit son contenu
 */
async function extractTextFromFile(file) {
    console.log("Extracting text from file:", file.name, file.type);
    
    const fileType = file.type.toLowerCase();
    
    if (fileType === 'text/plain' || file.name.endsWith('.txt')) {
        // Fichier texte
        return await readTextFromFile(file);
    } else if (fileType === 'application/pdf' || file.name.endsWith('.pdf')) {
        // Fichier PDF
        return await readPdfFile(file);
    } else if (fileType.includes('word') || file.name.endsWith('.doc') || file.name.endsWith('.docx')) {
        // Document Word (simplifié, traité comme du texte)
        return await readTextFromFile(file);
    } else {
        // Type non supporté, tenter de lire comme du texte
        console.warn("File type not explicitly supported, attempting to read as text:", fileType);
        return await readTextFromFile(file);
    }
}

// Exposer les fonctions pour utilisation depuis d'autres scripts
window.JobParser = {
    analyzer: new JobPostingAnalyzer(),
    extractTextFromFile: extractTextFromFile,
    
    /**
     * Analyse un fichier et retourne les informations extraites
     */
    async analyzeFile(file) {
        try {
            const text = await extractTextFromFile(file);
            return {
                data: this.analyzer.analyze(text)
            };
        } catch (error) {
            console.error("Error analyzing file:", error);
            throw error;
        }
    },
    
    /**
     * Analyse un texte directement et retourne les informations extraites
     */
    analyzeText(text) {
        try {
            return {
                data: this.analyzer.analyze(text)
            };
        } catch (error) {
            console.error("Error analyzing text:", error);
            throw error;
        }
    }
};