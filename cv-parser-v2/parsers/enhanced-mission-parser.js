/**
 * Enhanced Mission Parser - Analyseur enrichi de missions CV
 * Compatible avec SuperSmartMatch V2.1
 */

const fs = require('fs');

class EnhancedMissionParser {
    constructor() {
        this.name_patterns = [
            /^([A-Z][a-z]+ [A-Z][a-z]+)/m,
            /Nom\s*:?\s*([A-Z][a-z]+ [A-Z][a-z]+)/i,
            /([A-Z][A-Z\s]+[A-Z])/m
        ];
        
        this.mission_keywords = [
            'responsable', 'gestion', 'développement', 'management', 'coordination',
            'analyse', 'suivi', 'contrôle', 'pilotage', 'supervision', 'encadrement',
            'facturation', 'comptabilité', 'commercial', 'vente', 'client'
        ];
        
        this.skill_patterns = [
            /(?:Compétences|Skills|Technologies|Outils)\s*:?\s*([^\n\r]+)/gi,
            /(?:Maîtrise|Connaissance)\s+(?:de\s+)?([A-Za-z0-9\s,]+)/gi
        ];
    }

    /**
     * Parse un CV avec extraction enrichie des missions
     */
    parseEnhancedCVWithMissions(text) {
        const result = {
            personal_info: this.extractPersonalInfo(text),
            professional_experience: this.extractProfessionalExperience(text),
            skills: this.extractSkills(text),
            technical_skills: [],
            soft_skills: [],
            education: [],
            languages: this.extractLanguages(text),
            certifications: []
        };

        // Séparer les compétences techniques et soft skills
        const allSkills = result.skills;
        result.technical_skills = this.filterTechnicalSkills(allSkills);
        result.soft_skills = this.filterSoftSkills(allSkills);

        return result;
    }

    /**
     * Extrait les informations personnelles
     */
    extractPersonalInfo(text) {
        const info = {};
        
        // Extraction du nom
        for (const pattern of this.name_patterns) {
            const match = text.match(pattern);
            if (match && match[1]) {
                info.name = match[1].trim();
                break;
            }
        }
        
        // Email
        const emailMatch = text.match(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/);
        if (emailMatch) {
            info.email = emailMatch[1];
        }
        
        // Téléphone
        const phoneMatch = text.match(/(\+33\s?[0-9\s.-]{8,}|0[0-9\s.-]{8,})/);
        if (phoneMatch) {
            info.phone = phoneMatch[1].replace(/\s+/g, ' ').trim();
        }
        
        return info;
    }

    /**
     * Extrait l'expérience professionnelle avec missions détaillées
     */
    extractProfessionalExperience(text) {
        const experiences = [];
        
        // Pattern pour détecter les expériences
        const expPatterns = [
            /(?:EXPÉRIENCE|EXPERIENCE|PARCOURS)\s+PROFESSIONNELLE?\s*:?\s*(.*?)(?=FORMATION|ÉTUDES|COMPÉTENCES|LANGUES|$)/gis,
            /(?:Expérience|Experience)\s*(.*?)(?=Formation|Études|Compétences|Langues|$)/gis
        ];
        
        let experienceText = '';
        for (const pattern of expPatterns) {
            const match = text.match(pattern);
            if (match && match[1]) {
                experienceText = match[1];
                break;
            }
        }
        
        if (!experienceText) {
            // Fallback: chercher des patterns de dates et postes
            experienceText = text;
        }
        
        // Extraction des postes avec dates
        const jobPattern = /(?:(\d{4}[-\s]*\d{4}|\d{4}\s*[-–]\s*(?:\d{4}|Aujourd'hui|Present))\s*[:\-]?\s*)?([A-Z][^0-9\n]{10,80})(?:\n|\r\n?)((?:[^0-9\n][^\n]*\n?){1,10})/gi;
        
        let match;
        while ((match = jobPattern.exec(experienceText)) !== null) {
            const [, duration, position, description] = match;
            
            if (position && description) {
                const missions = this.extractMissions(description);
                
                if (missions.length > 0) {
                    experiences.push({
                        position: position.trim(),
                        company: this.extractCompany(description) || 'Entreprise précédente',
                        duration: duration ? duration.trim() : '2019-2023',
                        missions: missions
                    });
                }
            }
        }
        
        // Si aucune expérience trouvée, créer une expérience générique avec missions basées sur le texte
        if (experiences.length === 0) {
            const missions = this.extractMissions(text);
            if (missions.length > 0) {
                experiences.push({
                    position: this.guessPosition(text) || 'Poste précédent',
                    company: 'Entreprise précédente',
                    duration: '2019-2023',
                    missions: missions
                });
            }
        }
        
        return experiences;
    }

    /**
     * Extrait les missions d'un texte
     */
    extractMissions(text) {
        const missions = [];
        
        // Patterns pour identifier les missions
        const missionPatterns = [
            /[•\-\*]\s*([^•\-\*\n]{20,150})/g,
            /(?:^|\n)\s*[\-•]\s*([^\n]{15,120})/gm,
            /(?:Missions?\s*:?\s*)((?:[^\n]{20,}(?:\n|$)){1,8})/gi
        ];
        
        for (const pattern of missionPatterns) {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const mission = match[1].trim();
                if (this.isMission(mission)) {
                    missions.push(mission);
                }
            }
        }
        
        // Si peu de missions trouvées, extraire des phrases contenant des mots-clés
        if (missions.length < 3) {
            const sentences = text.split(/[.!?]\s+/);
            for (const sentence of sentences) {
                if (sentence.length > 20 && sentence.length < 150) {
                    if (this.containsMissionKeywords(sentence)) {
                        missions.push(sentence.trim());
                    }
                }
            }
        }
        
        // Dédupliquer et nettoyer
        return [...new Set(missions)]
            .filter(m => m.length > 15 && m.length < 200)
            .slice(0, 8); // Limite à 8 missions
    }

    /**
     * Vérifie si un texte est une mission
     */
    isMission(text) {
        const cleanText = text.toLowerCase();
        
        // Doit contenir au moins un mot-clé de mission
        const hasKeyword = this.mission_keywords.some(keyword => 
            cleanText.includes(keyword.toLowerCase())
        );
        
        // Ne doit pas être trop générique
        const isNotTooGeneric = !(/^(gestion|suivi|contrôle)$/.test(cleanText.trim()));
        
        return hasKeyword && isNotTooGeneric && text.length > 15;
    }

    /**
     * Vérifie si une phrase contient des mots-clés de mission
     */
    containsMissionKeywords(text) {
        const cleanText = text.toLowerCase();
        return this.mission_keywords.some(keyword => 
            cleanText.includes(keyword.toLowerCase())
        );
    }

    /**
     * Devine le poste à partir du texte
     */
    guessPosition(text) {
        const positionKeywords = {
            'assistant': ['assistant', 'assistante'],
            'responsable': ['responsable'],
            'manager': ['manager', 'manageur'],
            'commercial': ['commercial', 'vente'],
            'comptable': ['comptable', 'comptabilité'],
            'contrôleur': ['contrôleur', 'contrôle']
        };
        
        const cleanText = text.toLowerCase();
        for (const [position, keywords] of Object.entries(positionKeywords)) {
            if (keywords.some(keyword => cleanText.includes(keyword))) {
                return position.charAt(0).toUpperCase() + position.slice(1);
            }
        }
        
        return null;
    }

    /**
     * Extrait le nom de l'entreprise
     */
    extractCompany(text) {
        // Pattern simple pour entreprise
        const companyPattern = /(?:chez|Entreprise|Société|Company)\s+([A-Z][A-Za-z\s&]{2,30})/i;
        const match = text.match(companyPattern);
        return match ? match[1].trim() : null;
    }

    /**
     * Extrait les compétences
     */
    extractSkills(text) {
        const skills = [];
        
        for (const pattern of this.skill_patterns) {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const skillText = match[1];
                const skillArray = skillText.split(/[,;]/).map(s => s.trim());
                skills.push(...skillArray);
            }
        }
        
        // Compétences communes basées sur des mots-clés
        const commonSkills = ['excel', 'word', 'powerpoint', 'outlook', 'sap', 'erp', 'crm', 'salesforce'];
        const textLower = text.toLowerCase();
        
        for (const skill of commonSkills) {
            if (textLower.includes(skill)) {
                skills.push(skill);
            }
        }
        
        return [...new Set(skills)].filter(s => s.length > 1 && s.length < 30);
    }

    /**
     * Filtre les compétences techniques
     */
    filterTechnicalSkills(skills) {
        const technicalKeywords = ['excel', 'word', 'sap', 'erp', 'crm', 'sql', 'python', 'java', 'oracle', 'salesforce'];
        return skills.filter(skill => 
            technicalKeywords.some(tech => skill.toLowerCase().includes(tech.toLowerCase()))
        );
    }

    /**
     * Filtre les soft skills
     */
    filterSoftSkills(skills) {
        const softKeywords = ['communication', 'leadership', 'teamwork', 'organization', 'rigueur', 'autonomie'];
        return skills.filter(skill => 
            softKeywords.some(soft => skill.toLowerCase().includes(soft.toLowerCase()))
        );
    }

    /**
     * Extrait les langues
     */
    extractLanguages(text) {
        const languages = [];
        const languagePattern = /(?:Langues?|Languages?)\s*:?\s*([^\n\r]+)/gi;
        const commonLanguages = ['français', 'anglais', 'espagnol', 'allemand', 'italien', 'english', 'french', 'spanish'];
        
        const match = text.match(languagePattern);
        if (match && match[1]) {
            const langText = match[1].toLowerCase();
            for (const lang of commonLanguages) {
                if (langText.includes(lang)) {
                    const normalizedLang = lang === 'english' ? 'anglais' : 
                                         lang === 'french' ? 'français' : 
                                         lang === 'spanish' ? 'espagnol' : lang;
                    languages.push(normalizedLang);
                }
            }
        }
        
        return [...new Set(languages)];
    }
}

/**
 * Fonction principale d'export
 */
function parseCV(text) {
    const parser = new EnhancedMissionParser();
    return parser.parseEnhancedCVWithMissions(text);
}

// Export pour utilisation en module
module.exports = EnhancedMissionParser;

// Utilisation en ligne de commande
if (require.main === module) {
    const textFile = process.argv[2];
    if (!textFile) {
        console.error('Usage: node enhanced-mission-parser.js <text-file>');
        process.exit(1);
    }
    
    try {
        const text = fs.readFileSync(textFile, 'utf8');
        const result = parseCV(text);
        console.log(JSON.stringify(result, null, 2));
    } catch (error) {
        console.error('Erreur:', error.message);
        process.exit(1);
    }
}
