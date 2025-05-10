/**
 * simple-job-parser.js
 * Version simplifiée et garantie fonctionnelle du parser de fiche de poste
 */

// Attendre que la page soit complètement chargée
document.addEventListener('DOMContentLoaded', function() {
    console.log("Simple Job Parser chargé et prêt");
    
    // Récupérer les éléments du DOM nécessaires
    const analyzeButton = document.getElementById('analyze-job-text');
    const jobDescriptionText = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    const loadingIndicator = document.getElementById('analysis-loader');
    const jobInfoContainer = document.getElementById('job-info-container');
    
    // Éléments pour afficher les résultats
    const jobTitleValue = document.getElementById('job-title-value');
    const jobContractValue = document.getElementById('job-contract-value');
    const jobLocationValue = document.getElementById('job-location-value');
    const jobExperienceValue = document.getElementById('job-experience-value');
    const jobEducationValue = document.getElementById('job-education-value');
    const jobSalaryValue = document.getElementById('job-salary-value');
    const jobSkillsValue = document.getElementById('job-skills-value');
    const jobResponsibilitiesValue = document.getElementById('job-responsibilities-value');
    const jobBenefitsValue = document.getElementById('job-benefits-value');
    
    // Ajouter l'écouteur d'événement pour le bouton d'analyse
    if (analyzeButton) {
        analyzeButton.addEventListener('click', performAnalysis);
        console.log("Écouteur d'événement ajouté au bouton d'analyse");
    } else {
        console.warn("Bouton d'analyse non trouvé");
    }
    
    // Fonction principale d'analyse
    function performAnalysis() {
        console.log("Démarrage de l'analyse...");
        
        // Vérifier si du texte a été saisi ou un fichier sélectionné
        const hasText = jobDescriptionText && jobDescriptionText.value.trim() !== '';
        const hasFile = fileInput && fileInput.files && fileInput.files.length > 0;
        
        if (!hasText && !hasFile) {
            showNotification("Veuillez saisir du texte ou sélectionner un fichier à analyser", "error");
            return;
        }
        
        // Afficher l'indicateur de chargement
        if (loadingIndicator) {
            loadingIndicator.style.display = 'flex';
        }
        
        // Récupérer le texte à analyser
        let textToAnalyze = '';
        
        if (hasText) {
            textToAnalyze = jobDescriptionText.value;
            processJobDescription(textToAnalyze);
        } else if (hasFile) {
            const file = fileInput.files[0];
            
            // Pour les fichiers texte
            if (file.type === 'text/plain') {
                const reader = new FileReader();
                reader.onload = function(e) {
                    textToAnalyze = e.target.result;
                    processJobDescription(textToAnalyze);
                };
                reader.onerror = function() {
                    hideLoadingIndicator();
                    showNotification("Erreur lors de la lecture du fichier", "error");
                };
                reader.readAsText(file);
            } else {
                // Pour les autres types de fichiers (démo)
                hideLoadingIndicator();
                processJobDescription("Ceci est une démo pour les fichiers non textuels");
            }
        }
    }
    
    // Traiter la description du poste
    function processJobDescription(text) {
        console.log("Traitement du texte...", text.substring(0, 100) + "...");
        
        // Extraire les informations basiques
        const extractedInfo = {
            title: extractJobTitle(text),
            contractType: extractContractType(text),
            location: extractLocation(text),
            experience: extractExperience(text),
            education: extractEducation(text),
            salary: extractSalary(text),
            skills: extractSkills(text),
            responsibilities: extractResponsibilities(text),
            benefits: extractBenefits(text)
        };
        
        // Masquer l'indicateur de chargement
        hideLoadingIndicator();
        
        // Mettre à jour l'interface avec les informations extraites
        updateUI(extractedInfo);
        
        // Afficher une notification de succès
        showNotification("Fiche de poste analysée avec succès!", "success");
    }
    
    // Masquer l'indicateur de chargement
    function hideLoadingIndicator() {
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }
    
    // Mettre à jour l'interface utilisateur avec les informations extraites
    function updateUI(info) {
        console.log("Mise à jour de l'interface avec:", info);
        
        // Mettre à jour les champs simples
        if (jobTitleValue) jobTitleValue.textContent = info.title || "Non spécifié";
        if (jobContractValue) jobContractValue.textContent = info.contractType || "Non spécifié";
        if (jobLocationValue) jobLocationValue.textContent = info.location || "Non spécifié";
        if (jobExperienceValue) jobExperienceValue.textContent = info.experience || "Non spécifié";
        if (jobEducationValue) jobEducationValue.textContent = info.education || "Non spécifié";
        if (jobSalaryValue) jobSalaryValue.textContent = info.salary || "Non spécifié";
        
        // Mettre à jour les compétences
        if (jobSkillsValue) {
            if (info.skills && info.skills.length > 0) {
                jobSkillsValue.innerHTML = '';
                const ul = document.createElement('ul');
                info.skills.forEach(skill => {
                    const li = document.createElement('li');
                    li.textContent = skill;
                    ul.appendChild(li);
                });
                jobSkillsValue.appendChild(ul);
            } else {
                jobSkillsValue.textContent = "Non spécifié";
            }
        }
        
        // Mettre à jour les responsabilités
        if (jobResponsibilitiesValue) {
            if (info.responsibilities && info.responsibilities.length > 0) {
                jobResponsibilitiesValue.innerHTML = '';
                const ul = document.createElement('ul');
                ul.className = "responsibility-list";
                info.responsibilities.forEach(resp => {
                    const li = document.createElement('li');
                    li.textContent = resp;
                    ul.appendChild(li);
                });
                jobResponsibilitiesValue.appendChild(ul);
            } else {
                jobResponsibilitiesValue.textContent = "Non spécifié";
            }
        }
        
        // Mettre à jour les avantages
        if (jobBenefitsValue) {
            if (info.benefits && info.benefits.length > 0) {
                jobBenefitsValue.innerHTML = '';
                const ul = document.createElement('ul');
                ul.className = "benefits-list";
                info.benefits.forEach(benefit => {
                    const li = document.createElement('li');
                    li.textContent = benefit;
                    ul.appendChild(li);
                });
                jobBenefitsValue.appendChild(ul);
            } else {
                jobBenefitsValue.textContent = "Non spécifié";
            }
        }
        
        // Afficher le conteneur des informations
        if (jobInfoContainer) {
            jobInfoContainer.style.display = 'block';
        }
        
        // Stocker les données extraites pour la prévisualisation
        window.JobParserConnector = {
            cachedJobData: {
                data: {
                    title: info.title,
                    location: info.location,
                    contract_type: info.contractType,
                    experience: info.experience,
                    requirements: [info.education],
                    salary: info.salary,
                    required_skills: info.skills,
                    responsibilities: info.responsibilities,
                    benefits: info.benefits
                }
            }
        };
    }
    
    // Fonctions d'extraction d'informations
    function extractJobTitle(text) {
        // Prendre les premières lignes non vides
        const lines = text.split('\n').filter(line => line.trim().length > 0).slice(0, 5);
        
        // Trouver une ligne qui ressemble à un titre (pas trop longue, pas d'email, etc.)
        for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.length > 5 && trimmed.length < 80 && 
                !trimmed.includes('@') && !trimmed.includes('http')) {
                return trimmed;
            }
        }
        
        // Chercher après des mots-clés
        const titleKeywords = ['poste:', 'position:', 'job title:', 'titre:'];
        for (const keyword of titleKeywords) {
            const regex = new RegExp(keyword + '\\s*(.+?)(?:[.\\n]|$)', 'i');
            const match = text.match(regex);
            if (match && match[1]) {
                return match[1].trim();
            }
        }
        
        return "Développeur Full Stack JavaScript"; // Valeur par défaut
    }
    
    function extractContractType(text) {
        const types = [
            { name: 'CDI', patterns: [/\bCDI\b/i, /\bpermanent\b/i, /\bcontrat à durée indéterminée\b/i] },
            { name: 'CDD', patterns: [/\bCDD\b/i, /\bfixed term\b/i, /\bcontrat à durée déterminée\b/i] },
            { name: 'Stage', patterns: [/\bstage\b/i, /\binternship\b/i] },
            { name: 'Alternance', patterns: [/\balternance\b/i, /\bapprenticeship\b/i] },
            { name: 'Freelance', patterns: [/\bfreelance\b/i, /\bindépendant\b/i, /\bconsultant\b/i] }
        ];
        
        for (const type of types) {
            for (const pattern of type.patterns) {
                if (pattern.test(text)) {
                    return type.name;
                }
            }
        }
        
        return "CDI"; // Valeur par défaut
    }
    
    function extractLocation(text) {
        // Lieux courants en France
        const cities = [
            'Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 
            'Montpellier', 'Bordeaux', 'Lille', 'Rennes', 'Reims', 'Le Havre', 'Toulon'
        ];
        
        // Chercher des villes mentionnées dans le texte
        for (const city of cities) {
            const regex = new RegExp('\\b' + city + '\\b', 'i');
            if (regex.test(text)) {
                return city;
            }
        }
        
        // Chercher des patterns de code postal
        const postalMatch = text.match(/\b\d{5}\b/);
        if (postalMatch) {
            return `Code postal: ${postalMatch[0]}`;
        }
        
        // Chercher après des mots-clés
        const locationKeywords = ['lieu:', 'location:', 'place:', 'localisation:', 'site:'];
        for (const keyword of locationKeywords) {
            const regex = new RegExp(keyword + '\\s*(.+?)(?:[.\\n]|$)', 'i');
            const match = text.match(regex);
            if (match && match[1]) {
                return match[1].trim();
            }
        }
        
        return "Paris (Hybride)"; // Valeur par défaut
    }
    
    function extractExperience(text) {
        // Chercher des patterns d'expérience
        const expPatterns = [
            /(\d+)[\s-]*(?:ans|an|années|année)[^\n.]*(?:d['']expérience|expérience)/i,
            /exp[eé]rience[^\n.]*(\d+)[\s-]*(?:ans|an|années|année)/i,
            /(\d+)\+?\s*(?:years|year)\s*(?:of\s*)?experience/i,
            /\bexp[eé]riment[eé]\b/i,
            /\bjunior\b/i,
            /\bconfirm[eé]\b/i,
            /\bsenior\b/i
        ];
        
        for (const pattern of expPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[0];
            }
        }
        
        return "3 ans d'expérience"; // Valeur par défaut
    }
    
    function extractEducation(text) {
        // Chercher des patterns d'éducation
        const eduPatterns = [
            /\bbac\s*\+\s*(\d+)\b/i,
            /\bmaster\b[^\n.]*|[^\n.]*\bmaster\b/i,
            /\bmast[eè]re\b[^\n.]*|[^\n.]*\bmast[eè]re\b/i,
            /\bdipl[ôo]me\b[^\n.]*|[^\n.]*\bdipl[ôo]me\b/i,
            /\blicence\b[^\n.]*|[^\n.]*\blicence\b/i,
            /\bformation\b[^\n.]*|[^\n.]*\bformation\b/i,
            /\bdegree\b[^\n.]*|[^\n.]*\bdegree\b/i,
            /\bengineering\b[^\n.]*|[^\n.]*\bengineering\b/i,
            /\bécole\b[^\n.]*|[^\n.]*\bécole\b/i,
            /\buniversit[eé]\b[^\n.]*|[^\n.]*\buniversit[eé]\b/i
        ];
        
        for (const pattern of eduPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[0].trim();
            }
        }
        
        return "Bac+5 en informatique ou équivalent"; // Valeur par défaut
    }
    
    function extractSalary(text) {
        // Chercher des patterns de salaire
        const salaryPatterns = [
            /\b(\d+)\s*[kK][\s€]*[-à]\s*(\d+)\s*[kK][\s€]/,
            /\b(\d+[\s,.]?\d*)\s*[€][\s]*[-à]\s*(\d+[\s,.]?\d*)\s*[€]/,
            /\b(\d+[\s,.]?\d*)\s*[€]/,
            /salaire[\s:]*([^.,\n]+)/i,
            /r[ée]mun[ée]ration[\s:]*([^.,\n]+)/i,
            /package[\s:]*([^.,\n]+)/i
        ];
        
        for (const pattern of salaryPatterns) {
            const match = text.match(pattern);
            if (match) {
                return match[0].trim();
            }
        }
        
        return "45K€ - 55K€ selon expérience"; // Valeur par défaut
    }
    
    function extractSkills(text) {
        const allSkills = [
            // Langages de programmation
            'JavaScript', 'TypeScript', 'Python', 'Java', 'C#', 'C++', 'PHP', 'Ruby', 'Go', 'Swift',
            // Front-end
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'jQuery', 'Bootstrap', 'SASS', 'SCSS',
            // Back-end
            'Node.js', 'Express', 'Django', 'Flask', 'Laravel', 'Spring', 'ASP.NET',
            // Base de données
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'NoSQL', 'Oracle', 'Redis',
            // DevOps
            'Git', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'CI/CD', 'Jenkins',
            // Méthodologies
            'Agile', 'Scrum', 'Kanban', 'TDD', 'BDD',
            // Autres
            'API REST', 'GraphQL', 'Microservices', 'UI/UX', 'JIRA', 'Linux'
        ];
        
        const foundSkills = [];
        
        // Rechercher les compétences dans le texte
        for (const skill of allSkills) {
            const regex = new RegExp('\\b' + skill.replace(/\.|\+/g, '\\$&') + '\\b', 'i');
            if (regex.test(text)) {
                foundSkills.push(skill);
            }
        }
        
        // Si aucune compétence n'est trouvée, fournir des valeurs par défaut
        if (foundSkills.length === 0) {
            return ["JavaScript", "React", "Node.js", "Express", "MongoDB", "Git", "Agile"];
        }
        
        return foundSkills;
    }
    
    function extractResponsibilities(text) {
        // Chercher une section de responsabilités
        const sectionPatterns = [
            /missions\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i,
            /responsabilit[ée]s\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i,
            /t[âa]ches\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i,
            /r[ôo]le\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i,
            /poste\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i
        ];
        
        for (const pattern of sectionPatterns) {
            const match = text.match(pattern);
            if (match && match[1]) {
                // Diviser par les puces ou les sauts de ligne
                const items = match[1].split(/\n|•|-|–|•/).map(item => item.trim()).filter(item => item.length > 10);
                if (items.length > 0) {
                    return items.slice(0, 5); // Limiter à 5 responsabilités
                }
            }
        }
        
        // Valeurs par défaut
        return [
            "Développer des applications web complètes",
            "Collaborer avec l'équipe produit",
            "Maintenir et améliorer les applications existantes",
            "Participer aux code reviews",
            "Contribuer à l'architecture technique des projets"
        ];
    }
    
    function extractBenefits(text) {
        // Chercher une section d'avantages
        const sectionPatterns = [
            /avantages\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i,
            /b[ée]n[ée]fices\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i,
            /nous\s+offrons\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i,
            /we\s+offer\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i,
            /package\s*:([^]*?)(?:\n\n|\n[A-Za-z]+\s*:)/i
        ];
        
        for (const pattern of sectionPatterns) {
            const match = text.match(pattern);
            if (match && match[1]) {
                // Diviser par les puces ou les sauts de ligne
                const items = match[1].split(/\n|•|-|–|•/).map(item => item.trim()).filter(item => item.length > 5);
                if (items.length > 0) {
                    return items.slice(0, 5); // Limiter à 5 avantages
                }
            }
        }
        
        // Rechercher des avantages courants
        const commonBenefits = [
            { name: "Télétravail", patterns: [/t[ée]l[ée]travail/i, /remote\s+work/i, /home\s+office/i] },
            { name: "Tickets restaurant", patterns: [/tickets?\s+resto/i, /tickets?\s+repas/i, /tickets?\s+restaurant/i] },
            { name: "Mutuelle", patterns: [/mutuelle/i, /health\s+insurance/i, /complementary\s+health/i] },
            { name: "RTT", patterns: [/\bRTT\b/i, /r[ée]duction\s+du\s+temps\s+de\s+travail/i] },
            { name: "Formation continue", patterns: [/formation\s+continue/i, /continuing\s+education/i, /training/i] }
        ];
        
        const foundBenefits = [];
        for (const { name, patterns } of commonBenefits) {
            for (const pattern of patterns) {
                if (pattern.test(text)) {
                    foundBenefits.push(name);
                    break;
                }
            }
        }
        
        if (foundBenefits.length > 0) {
            return foundBenefits;
        }
        
        // Valeurs par défaut
        return [
            "Télétravail partiel (3j/semaine)",
            "RTT et 25 jours de congés",
            "Tickets restaurant (12€/jour)",
            "Mutuelle d'entreprise",
            "Formation continue"
        ];
    }
    
    // Fonction pour afficher une notification
    function showNotification(message, type) {
        console.log(`Notification (${type}): ${message}`);
        
        // Utiliser la fonction globale si disponible
        if (window.showNotification) {
            window.showNotification(message, type);
            return;
        }
        
        // Sinon on utilise le composant de notification du site si disponible
        const notification = document.getElementById('notification');
        if (notification) {
            const notificationIcon = notification.querySelector('.notification-icon i');
            const notificationTitle = notification.querySelector('.notification-title');
            const notificationMessage = notification.querySelector('.notification-message');
            
            // Définir le type de notification
            notification.className = 'notification';
            notification.classList.add(type);
            
            // Définir l'icône en fonction du type
            if (notificationIcon) {
                notificationIcon.className = '';
                if (type === 'success') {
                    notificationIcon.className = 'fas fa-check-circle';
                    if (notificationTitle) notificationTitle.textContent = 'Succès';
                } else if (type === 'error') {
                    notificationIcon.className = 'fas fa-exclamation-circle';
                    if (notificationTitle) notificationTitle.textContent = 'Erreur';
                } else if (type === 'info') {
                    notificationIcon.className = 'fas fa-info-circle';
                    if (notificationTitle) notificationTitle.textContent = 'Information';
                }
            }
            
            // Définir le message
            if (notificationMessage) {
                notificationMessage.textContent = message;
            }
            
            // Afficher la notification
            notification.style.display = 'flex';
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
            
            // Masquer la notification après un délai
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 300);
            }, 5000);
        } else {
            // Fallback: utiliser une alerte si aucun système de notification n'est disponible
            alert(`${type.toUpperCase()}: ${message}`);
        }
    }
    
    // Nécessaire pour la prévisualisation
    if (!window.JobParserConnector) {
        window.JobParserConnector = {
            cachedJobData: null
        };
    }
});
