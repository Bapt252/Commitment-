/**
 * Client JavaScript pour l'analyseur de fiche de poste
 * Ce fichier fournit une interface simple pour analyser les fiches de poste
 * en se connectant à une API simulée (pour la démo).
 */

// Namespace pour l'analyseur de poste
window.JobParser = (function() {
    console.log('Job Parser Client initialized');
    
    // Configuration (simulée pour la démo)
    const config = {
        apiEndpoint: 'https://api.example.com/job-parser',  // Simulé
        timeout: 5000
    };
    
    /**
     * Analyser un fichier de fiche de poste
     * @param {File} file - Le fichier à analyser
     * @returns {Promise} - Promesse résolue avec les données analysées
     */
    async function analyzeFile(file) {
        console.log('JobParser.analyzeFile called with:', file);
        
        // Simuler une analyse de fichier
        return new Promise((resolve) => {
            setTimeout(() => {
                // Données simulées pour la démo
                const result = {
                    data: {
                        title: "Développeur Full Stack",
                        company: "Tech Innovations",
                        location: "Paris, France",
                        contract_type: "CDI",
                        required_skills: ["JavaScript", "React", "Node.js", "MongoDB", "Git"],
                        preferred_skills: ["TypeScript", "Docker", "AWS"],
                        experience: "3-5 ans d'expérience",
                        responsibilities: [
                            "Développer des applications web responsive",
                            "Collaborer avec l'équipe de design",
                            "Maintenir les services existants"
                        ]
                    }
                };
                resolve(result);
            }, 2000); // Simuler un délai d'analyse
        });
    }
    
    /**
     * Analyser un texte de fiche de poste
     * @param {string} text - Le texte à analyser
     * @returns {Promise} - Promesse résolue avec les données analysées
     */
    async function analyzeText(text) {
        console.log('JobParser.analyzeText called with text:', text.substring(0, 50) + '...');
        
        // Extraction basique de données depuis le texte
        const result = {
            data: extractJobDataFromText(text)
        };
        
        return Promise.resolve(result);
    }
    
    /**
     * Extraction basique de données de poste depuis un texte
     * @param {string} text - Texte à analyser 
     */
    function extractJobDataFromText(text) {
        // Normalisation du texte
        const normalizedText = text.toLowerCase();
        
        // Titre du poste - première ligne ou contenu entre le début et la première ligne vide
        let title = text.split('\\n')[0].trim();
        if (title.length > 50) {
            // Si trop long, prendre les 50 premiers caractères
            title = title.substring(0, 50) + '...';
        }
        
        // Type de contrat
        let contract_type = "Non spécifié";
        if (normalizedText.includes('cdi')) {
            contract_type = "CDI";
        } else if (normalizedText.includes('cdd')) {
            contract_type = "CDD";
        } else if (normalizedText.includes('stage')) {
            contract_type = "Stage";
        } else if (normalizedText.includes('alternance')) {
            contract_type = "Alternance";
        } else if (normalizedText.includes('freelance')) {
            contract_type = "Freelance";
        }
        
        // Expérience
        let experience = "Non spécifiée";
        // Patterns pour l'expérience
        const expPatterns = [
            /(\d+)[\s-]*ans? d['']expérience/i,
            /expérience .*?(\d+)[\s-]*ans?/i,
            /(\d+)[\s-]*à[\s-]*(\d+)[\s-]*ans? d['']expérience/i
        ];
        
        for (const pattern of expPatterns) {
            const match = normalizedText.match(pattern);
            if (match) {
                if (match[2]) {
                    experience = `${match[1]}-${match[2]} ans d'expérience`;
                } else {
                    experience = `${match[1]} ans d'expérience`;
                }
                break;
            }
        }
        
        // Compétences 
        const skillKeywords = [
            "javascript", "react", "angular", "vue", "node", "python", "java", "php", "html", "css",
            "sql", "nosql", "mongodb", "git", "agile", "scrum", "devops", "aws", "docker", "kubernetes",
            "gestion de projet", "leadership", "communication", "marketing", "vente", "comptabilité",
            "finance", "rh", "ressources humaines", "support", "service client", "design"
        ];
        
        const skills = [];
        for (const skill of skillKeywords) {
            if (normalizedText.includes(skill)) {
                // Ajouter la compétence avec la première lettre en majuscule
                skills.push(skill.charAt(0).toUpperCase() + skill.slice(1));
            }
        }
        
        // Retourner les données extraites
        return {
            title: title || "Poste non spécifié",
            company: "", // Non extrait pour simplifier
            location: "", // Non extrait pour simplifier
            contract_type: contract_type,
            required_skills: skills.length > 0 ? skills : ["Compétences non spécifiées"],
            preferred_skills: [],
            experience: experience,
            responsibilities: []
        };
    }
    
    // Interface publique
    return {
        analyzeFile,
        analyzeText
    };
})();
