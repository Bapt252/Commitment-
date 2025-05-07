// Script pour l'analyseur de fiche de poste intégré directement
document.addEventListener('DOMContentLoaded', function() {
    // Éléments DOM
    const openParserBtn = document.getElementById('open-job-parser');
    const inlineParser = document.getElementById('inline-job-parser');
    const closeParserBtn = document.getElementById('close-inline-parser');
    const analyzeBtn = document.getElementById('analyze-job-text');
    const jobTextArea = document.getElementById('job-description-text');
    const resultsContainer = document.getElementById('inline-analysis-results');
    
    // Conteneurs d'information pour l'affichage des résultats
    const jobInfoContainer = document.getElementById('job-info-container');
    const jobTitleValue = document.getElementById('job-title-value');
    const jobSkillsValue = document.getElementById('job-skills-value');
    const jobExperienceValue = document.getElementById('job-experience-value');
    const jobContractValue = document.getElementById('job-contract-value');
    
    // Vérifier que tous les éléments nécessaires sont présents
    if (!openParserBtn || !inlineParser || !closeParserBtn || !analyzeBtn || !jobTextArea || !resultsContainer) {
        console.error('Éléments HTML manquants pour l\'analyseur de fiche de poste');
        return;
    }
    
    // Ouvrir l'analyseur
    openParserBtn.addEventListener('click', function() {
        inlineParser.style.display = 'block';
        // Pré-remplir avec un exemple si vide
        if (!jobTextArea.value.trim()) {
            jobTextArea.value = `Développeur Frontend - CDI

Notre entreprise recherche un développeur frontend expérimenté pour travailler sur nos applications web.

Compétences requises:
- JavaScript
- React
- CSS/SASS
- HTML5
- Git

Expérience: 3-5 ans d'expérience en développement frontend.

Type de contrat: CDI à temps plein
Lieu: Paris`;
        }
    });
    
    // Fermer l'analyseur
    closeParserBtn.addEventListener('click', function() {
        inlineParser.style.display = 'none';
    });
    
    // Analyser le texte
    analyzeBtn.addEventListener('click', function() {
        const text = jobTextArea.value.trim();
        if (!text) {
            alert('Veuillez saisir du texte à analyser.');
            return;
        }
        
        // Afficher un indicateur de chargement
        resultsContainer.style.display = 'block';
        resultsContainer.innerHTML = '<div style="text-align:center; padding: 20px;"><i class="fas fa-spinner fa-spin" style="font-size: 24px; color: #7C3AED;"></i><p>Analyse en cours...</p></div>';
        
        // Simuler un délai d'analyse
        setTimeout(function() {
            // Analyser le texte
            const results = analyzeJobText(text);
            
            // Afficher les résultats
            displayResults(results);
            
            // Mettre à jour le formulaire principal avec les résultats
            updateFormWithResults(results);
        }, 1500);
    });
    
    // Fonction d'analyse du texte
    function analyzeJobText(text) {
        // Texte normalisé pour l'analyse
        const normalizedText = text.toLowerCase();
        
        // Titre - première ligne ou début du texte
        let title = text.split('\n')[0].trim();
        if (title.length > 50) {
            title = title.substring(0, 50) + '...';
        }
        
        // Type de contrat
        let contract = "Non spécifié";
        if (normalizedText.includes('cdi')) {
            contract = "CDI";
        } else if (normalizedText.includes('cdd')) {
            contract = "CDD";
        } else if (normalizedText.includes('stage')) {
            contract = "Stage";
        } else if (normalizedText.includes('alternance')) {
            contract = "Alternance";
        } else if (normalizedText.includes('freelance')) {
            contract = "Freelance";
        }
        
        // Expérience
        let experience = "Non spécifiée";
        const expMatches = [
            normalizedText.match(/(\d+)[\s-]*ans? d['']expérience/i),
            normalizedText.match(/expérience .*?(\d+)[\s-]*ans?/i),
            normalizedText.match(/(\d+)[\s-]*à[\s-]*(\d+)[\s-]*ans? d['']expérience/i)
        ].filter(m => m);
        
        if (expMatches.length > 0) {
            const match = expMatches[0];
            if (match[2]) {
                experience = `${match[1]}-${match[2]} ans d'expérience`;
            } else {
                experience = `${match[1]} ans d'expérience`;
            }
        }
        
        // Compétences
        const skillKeywords = [
            "javascript", "react", "angular", "vue", "node", "python", "java", "php", "html", "css",
            "sql", "nosql", "mongodb", "git", "agile", "scrum", "devops", "aws", "docker", "kubernetes",
            "typescript", "sass", "less", "jquery", "bootstrap", "tailwind", "figma", "photoshop",
            "illustration", "sketch", "redux", "graphql", "rest", "api", "frontend", "backend", "fullstack"
        ];
        
        const skills = [];
        for (const skill of skillKeywords) {
            if (normalizedText.includes(skill)) {
                skills.push(skill.charAt(0).toUpperCase() + skill.slice(1));
            }
        }
        
        return {
            title: title,
            skills: skills.length > 0 ? skills : ["Non spécifiées"],
            experience: experience,
            contract: contract
        };
    }
    
    // Afficher les résultats dans le conteneur
    function displayResults(results) {
        let html = '<h4 style="margin-bottom: 15px; color: #7C3AED;">Informations extraites</h4>';
        
        html += `<div style="margin-bottom: 10px;"><strong>Titre du poste:</strong> ${results.title}</div>`;
        
        html += '<div style="margin-bottom: 10px;"><strong>Compétences requises:</strong> ';
        if (results.skills.length > 0) {
            html += '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin-top: 5px;">';
            results.skills.forEach(skill => {
                html += `<span style="background: rgba(124, 58, 237, 0.1); color: #5B21B6; padding: 4px 8px; border-radius: 20px; font-size: 0.9rem;">${skill}</span>`;
            });
            html += '</div>';
        } else {
            html += 'Non spécifiées';
        }
        html += '</div>';
        
        html += `<div style="margin-bottom: 10px;"><strong>Expérience:</strong> ${results.experience}</div>`;
        html += `<div style="margin-bottom: 15px;"><strong>Type de contrat:</strong> ${results.contract}</div>`;
        
        html += `<button id="apply-inline-results" style="background: #7C3AED; color: white; border: none; border-radius: 8px; padding: 8px 15px; cursor: pointer; display: flex; align-items: center; gap: 5px;">
            <i class="fas fa-check"></i> Appliquer ces informations
        </button>`;
        
        resultsContainer.innerHTML = html;
        
        // Gérer le bouton d'application des résultats
        document.getElementById('apply-inline-results').addEventListener('click', function() {
            updateFormWithResults(results);
            
            // Afficher une notification
            if (window.showNotification) {
                window.showNotification('Les informations ont été appliquées avec succès!', 'success');
            } else {
                alert('Les informations ont été appliquées avec succès!');
            }
            
            // Fermer l'analyseur après un court délai
            setTimeout(() => {
                inlineParser.style.display = 'none';
            }, 1000);
        });
    }
    
    // Mettre à jour le formulaire principal avec les résultats
    function updateFormWithResults(results) {
        // Afficher le conteneur d'informations
        if (jobInfoContainer) {
            jobInfoContainer.style.display = 'block';
        }
        
        // Mettre à jour le titre
        if (jobTitleValue) {
            jobTitleValue.textContent = results.title || '-';
        }
        
        // Mettre à jour les compétences
        if (jobSkillsValue) {
            if (results.skills && results.skills.length > 0) {
                const skillsHtml = results.skills.map(skill => 
                    `<span class="skill-tag">${skill}</span>`
                ).join(' ');
                jobSkillsValue.innerHTML = skillsHtml;
            } else {
                jobSkillsValue.textContent = '-';
            }
        }
        
        // Mettre à jour l'expérience
        if (jobExperienceValue) {
            jobExperienceValue.textContent = results.experience || '-';
        }
        
        // Mettre à jour le type de contrat
        if (jobContractValue) {
            jobContractValue.textContent = results.contract || '-';
        }
        
        // Pré-remplir d'autres champs du formulaire
        if (results.contract) {
            const contractTypeField = document.getElementById('contract-type');
            if (contractTypeField) {
                contractTypeField.value = results.contract;
            }
        }
        
        // Pré-remplir le niveau d'expérience
        if (results.experience) {
            const experienceField = document.getElementById('required-experience');
            if (experienceField) {
                const expText = results.experience.toLowerCase();
                
                if (expText.includes('junior') || expText.includes('débutant')) {
                    experienceField.value = 'junior';
                } else if (expText.includes('2') || expText.includes('3')) {
                    experienceField.value = '2-3years';
                } else if (expText.includes('5') || (expText.includes('10') && !expText.includes('10+'))) {
                    experienceField.value = '5-10years';
                } else if (expText.includes('10+') || expText.includes('senior')) {
                    experienceField.value = '10+years';
                }
            }
        }
    }
});
