const GPT_MOCK_MODE = true; // Mode de simulation sans API externe

/**
 * GPT Analysis Script
 * Script pour analyser une fiche de poste avec GPT
 */

document.addEventListener('DOMContentLoaded', function() {
    initGPTAnalysis();
});

/**
 * Initialise l'analyse GPT
 */
function initGPTAnalysis() {
    // Connecter le bouton d'analyse GPT
    const analyzeGptBtn = document.getElementById('analyze-with-gpt');
    if (analyzeGptBtn) {
        analyzeGptBtn.addEventListener('click', handleAnalyzeWithGPT);
    } else {
        console.warn('Button analyze-with-gpt not found');
    }
    
    // Activer le bouton si du texte est disponible
    const jobText = document.getElementById('job-description-text');
    if (jobText && jobText.value.trim()) {
        if (analyzeGptBtn) analyzeGptBtn.disabled = false;
    }
    
    // Écouter les modifications du textarea pour activer/désactiver le bouton
    if (jobText && analyzeGptBtn) {
        jobText.addEventListener('input', function() {
            analyzeGptBtn.disabled = !this.value.trim();
        });
    }
}

/**
 * Gestionnaire pour le clic sur le bouton d'analyse GPT
 */
async function handleAnalyzeWithGPT() {
    const jobText = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    
    if ((!jobText || !jobText.value.trim()) && (!fileInput || !fileInput.files.length)) {
        alert('Veuillez fournir une fiche de poste à analyser');
        return;
    }
    
    // Récupérer le texte ou le fichier
    const text = jobText && jobText.value.trim() ? jobText.value.trim() : null;
    const file = fileInput && fileInput.files.length ? fileInput.files[0] : null;
    
    // Mettre à jour le statut
    const statusElement = document.getElementById('gpt-analyze-status');
    if (statusElement) statusElement.textContent = 'Analyse en cours...';
    
    // Désactiver le bouton pendant l'analyse
    const button = document.getElementById('analyze-with-gpt');
    if (button) button.disabled = true;
    
    // Afficher le loader
    const loader = document.getElementById('analysis-loader');
    if (loader) loader.style.display = 'flex';
    
    try {
        let result;
        
        if (GPT_MOCK_MODE) {
            // Mode de simulation sans API externe
            console.log('Using GPT mock mode for analysis');
            result = await mockGPTAnalysis(text || 'Contenu du fichier non disponible');
        } else {
            // Utiliser l'API pour l'analyse avec GPT
            if (file) {
                result = await analyzeFileWithGPT(file);
            } else {
                result = await analyzeTextWithGPT(text);
            }
        }
        
        // Sauvegarder et afficher les résultats
        sessionStorage.setItem('parsedJobData', JSON.stringify(result));
        
        // Afficher les résultats en utilisant la fonction globale
        if (window.JobParsingUI && window.JobParsingUI.showJobResults) {
            window.JobParsingUI.showJobResults(result);
        } else if (window.showJobResults) {
            window.showJobResults(result);
        } else {
            // Fallback: afficher directement
            displayJobResults(result);
        }
        
        // Mettre à jour le statut
        if (statusElement) statusElement.textContent = 'Analyse réussie!';
        showNotification('Fiche de poste analysée avec succès!', 'success');
    } catch (error) {
        console.error('Error during GPT analysis:', error);
        
        // Mettre à jour le statut
        if (statusElement) statusElement.textContent = 'Erreur: ' + error.message;
        showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
    } finally {
        // Réactiver le bouton
        if (button) button.disabled = false;
        
        // Cacher le loader
        if (loader) loader.style.display = 'none';
    }
}

/**
 * Simule une analyse GPT (pour le développement sans API)
 * @param {string} text - Le texte à analyser
 * @returns {Promise<Object>} - Les résultats simulés
 */
async function mockGPTAnalysis(text) {
    // Simuler un délai d'API
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Créer un résultat simulé
    const mockResult = {
        title: "Développeur Full Stack JavaScript H/F",
        company: "TechInnovate",
        location: "Paris, France",
        contract_type: "CDI",
        skills: [
            "JavaScript",
            "React",
            "Node.js",
            "TypeScript",
            "Git",
            "Agile",
            "MongoDB",
            "AWS"
        ],
        experience: "3-5 ans",
        education: "Bac+5 en informatique ou équivalent",
        salary: "45K€ - 60K€ selon expérience",
        responsibilities: [
            "Développer des applications web modernes avec React et Node.js",
            "Participer à la conception des architectures logicielles",
            "Collaborer avec l'équipe UX/UI pour implémenter des interfaces utilisateur",
            "Optimiser les performances des applications",
            "Participer aux phases de tests et de déploiement"
        ],
        benefits: [
            "Télétravail 3 jours par semaine",
            "RTT",
            "Mutuelle d'entreprise",
            "Plan d'épargne entreprise",
            "Budget formation",
            "Tickets restaurant"
        ]
    };
    
    // Si du texte est fourni, essayer d'extraire certaines informations pour le rendre plus réaliste
    if (text && typeof text === 'string') {
        // Extraire le titre
        const titleMatch = text.match(/(?:poste|recrute|recherche).*?([\w\s]+\b(?:développeur|ingénieur|technicien|consultant|architecte|designer|chef de projet|manager|directeur)[\w\s]+)/i);
        if (titleMatch && titleMatch[1]) {
            mockResult.title = titleMatch[1].trim();
        }
        
        // Extraire la localisation
        const locationMatch = text.match(/(?:lieu|localisation|situé à|basé à).*?([\w\s]+\b(?:Paris|Lyon|Marseille|Toulouse|Bordeaux|Lille|Nantes|Strasbourg|Nancy)[\w\s,]*)/i);
        if (locationMatch && locationMatch[1]) {
            mockResult.location = locationMatch[1].trim();
        }
        
        // Extraire le type de contrat
        const contractMatch = text.match(/\b(CDI|CDD|intérim|stage|alternance|apprentissage|freelance)\b/i);
        if (contractMatch && contractMatch[1]) {
            mockResult.contract_type = contractMatch[1].toUpperCase();
        }
    }
    
    return mockResult;
}

/**
 * Analyse un texte avec GPT via une API
 * @param {string} text - Le texte à analyser
 * @returns {Promise<Object>} - Les résultats de l'analyse
 */
async function analyzeTextWithGPT(text) {
    // Appel API réel (à implémenter selon votre backend)
    const apiUrl = 'https://api.votre-service.com/analyze-job';
    
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            throw new Error(`API Error (${response.status}): ${await response.text()}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error calling GPT API:', error);
        throw error;
    }
}

/**
 * Analyse un fichier avec GPT via une API
 * @param {File} file - Le fichier à analyser
 * @returns {Promise<Object>} - Les résultats de l'analyse
 */
async function analyzeFileWithGPT(file) {
    // Appel API réel (à implémenter selon votre backend)
    const apiUrl = 'https://api.votre-service.com/analyze-job-file';
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(apiUrl, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`API Error (${response.status}): ${await response.text()}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error calling GPT API for file:', error);
        throw error;
    }
}

/**
 * Affiche les résultats d'analyse dans l'interface (fallback)
 * @param {Object} data - Les résultats de l'analyse
 */
function displayJobResults(data) {
    console.log('Displaying job analysis results:', data);
    
    // Éléments cibles pour afficher les résultats
    const jobTitleValue = document.getElementById('job-title-value');
    const jobContractValue = document.getElementById('job-contract-value');
    const jobLocationValue = document.getElementById('job-location-value');
    const jobExperienceValue = document.getElementById('job-experience-value');
    const jobEducationValue = document.getElementById('job-education-value');
    const jobSalaryValue = document.getElementById('job-salary-value');
    const jobSkillsValue = document.getElementById('job-skills-value');
    const jobResponsibilitiesValue = document.getElementById('job-responsibilities-value');
    const jobBenefitsValue = document.getElementById('job-benefits-value');
    
    // Afficher le conteneur principal
    const jobInfoContainer = document.getElementById('job-info-container');
    if (jobInfoContainer) jobInfoContainer.style.display = 'block';
    
    // Mettre à jour les valeurs avec les résultats de l'analyse
    if (jobTitleValue) jobTitleValue.textContent = data.title || 'Non spécifié';
    if (jobContractValue) jobContractValue.textContent = data.contract_type || 'Non spécifié';
    if (jobLocationValue) jobLocationValue.textContent = data.location || 'Non spécifié';
    if (jobExperienceValue) jobExperienceValue.textContent = data.experience || 'Non spécifié';
    if (jobEducationValue) jobEducationValue.textContent = data.education || 'Non spécifié';
    if (jobSalaryValue) jobSalaryValue.textContent = data.salary || 'Non spécifié';
    
    // Afficher les compétences sous forme de tags
    if (jobSkillsValue) {
        if (Array.isArray(data.skills) && data.skills.length > 0) {
            jobSkillsValue.innerHTML = '';
            data.skills.forEach(skill => {
                const skillTag = document.createElement('span');
                skillTag.className = 'tag';
                skillTag.textContent = skill;
                jobSkillsValue.appendChild(skillTag);
            });
        } else {
            jobSkillsValue.textContent = 'Non spécifié';
        }
    }
    
    // Afficher les responsabilités
    if (jobResponsibilitiesValue) {
        if (Array.isArray(data.responsibilities) && data.responsibilities.length > 0) {
            jobResponsibilitiesValue.innerHTML = '';
            const ul = document.createElement('ul');
            data.responsibilities.forEach(resp => {
                const li = document.createElement('li');
                li.textContent = resp;
                ul.appendChild(li);
            });
            jobResponsibilitiesValue.appendChild(ul);
        } else if (typeof data.responsibilities === 'string' && data.responsibilities) {
            jobResponsibilitiesValue.textContent = data.responsibilities;
        } else {
            jobResponsibilitiesValue.textContent = 'Non spécifié';
        }
    }
    
    // Afficher les avantages
    if (jobBenefitsValue) {
        if (Array.isArray(data.benefits) && data.benefits.length > 0) {
            jobBenefitsValue.innerHTML = '';
            const ul = document.createElement('ul');
            data.benefits.forEach(benefit => {
                const li = document.createElement('li');
                li.textContent = benefit;
                ul.appendChild(li);
            });
            jobBenefitsValue.appendChild(ul);
        } else if (typeof data.benefits === 'string' && data.benefits) {
            jobBenefitsValue.textContent = data.benefits;
        } else {
            jobBenefitsValue.textContent = 'Non spécifié';
        }
    }
}

/**
 * Affiche une notification (fallback)
 * @param {string} message - Message à afficher
 * @param {string} type - Type de notification (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Utiliser la fonction de notification globale si disponible
    if (window.QuestionnaireNavigation && window.QuestionnaireNavigation.showNotification) {
        window.QuestionnaireNavigation.showNotification(message, type);
    } else {
        console.log(`Notification (${type}): ${message}`);
        alert(message);
    }
}
