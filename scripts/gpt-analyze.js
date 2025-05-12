/**
 * gpt-analyze.js
 * Script pour connecter le frontend de client-questionnaire.html avec le système de parsing GPT
 * Ce script ajoute une fonctionnalité d'analyse de fiches de poste en utilisant le modèle GPT
 */

// Configuration de base 
const GPT_ANALYZE_CONFIG = {
    // URL de l'API de parsing, à adapter selon l'environnement
    apiUrl: 'http://localhost:5055/api/parse-job', // URL par défaut, sera remplacée si configurée ailleurs
    debug: false,
    useLocalFallback: true
};

// Créer un bouton "Analyser avec GPT" dans la page
function initializeGptAnalyzeButton() {
    // Vérifier si les éléments nécessaires existent dans la page
    const jobInfoContainer = document.getElementById('job-info-container');
    const textarea = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    
    if (!jobInfoContainer || !textarea) {
        console.error('Éléments requis non trouvés dans la page');
        return;
    }
    
    // Créer le conteneur pour le bouton et le statut
    const container = document.createElement('div');
    container.className = 'gpt-analyze-btn-container';
    
    // Créer le bouton "Analyser avec GPT"
    const button = document.createElement('button');
    button.id = 'analyze-with-gpt';
    button.textContent = 'Analyser avec GPT';
    button.disabled = !(textarea.value.trim() || (fileInput && fileInput.files.length > 0));
    
    // Créer l'élément pour afficher le statut
    const status = document.createElement('span');
    status.id = 'gpt-analyze-status';
    status.textContent = '';
    
    // Ajouter les éléments au conteneur
    container.appendChild(button);
    container.appendChild(status);
    
    // Insérer le conteneur après le champ de texte de la fiche de poste
    if (textarea.parentNode) {
        textarea.parentNode.insertAdjacentElement('afterend', container);
    } else {
        jobInfoContainer.insertAdjacentElement('beforebegin', container);
    }
    
    // Activer/désactiver le bouton en fonction du contenu du textarea
    textarea.addEventListener('input', () => {
        button.disabled = !textarea.value.trim();
    });
    
    // Si un fileInput existe, surveiller les changements
    if (fileInput) {
        fileInput.addEventListener('change', () => {
            button.disabled = !(textarea.value.trim() || fileInput.files.length > 0);
        });
    }
    
    // Gérer le clic sur le bouton
    button.addEventListener('click', handleGptAnalysis);
}

// Fonction pour analyser la fiche de poste avec GPT
async function handleGptAnalysis() {
    const textarea = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    const button = document.getElementById('analyze-with-gpt');
    const status = document.getElementById('gpt-analyze-status');
    
    // Vérifier que nous avons du contenu à analyser
    if (!(textarea.value.trim() || (fileInput && fileInput.files.length > 0))) {
        showNotification ? 
            showNotification("Veuillez d'abord entrer ou télécharger une fiche de poste", "error") : 
            alert("Veuillez d'abord entrer ou télécharger une fiche de poste");
        return;
    }
    
    // Désactiver le bouton et afficher le statut
    button.disabled = true;
    status.textContent = 'Analyse en cours...';
    
    try {
        let jobText = '';
        let file = null;
        
        // Obtenir le texte de la fiche de poste
        if (textarea.value.trim()) {
            jobText = textarea.value.trim();
        } else if (fileInput && fileInput.files.length > 0) {
            file = fileInput.files[0];
            // Lire le fichier si nécessaire
            jobText = await readFileAsText(file);
        }
        
        // Afficher le loader si disponible
        const loader = document.getElementById('analysis-loader');
        if (loader) loader.style.display = 'flex';
        
        // Appel de l'API GPT pour analyser la fiche de poste
        const result = await parseJobPostingWithGpt(jobText, file);
        
        // Sauvegarder les résultats
        saveParsingResults(result);
        
        // Afficher les résultats
        displayParsingResults(result);
        
        // Notification de succès
        status.textContent = 'Analyse réussie!';
        showNotification ? 
            showNotification("Fiche de poste analysée avec succès par GPT!", "success") : 
            alert("Fiche de poste analysée avec succès!");
        
    } catch (error) {
        console.error('Erreur lors de l\'analyse GPT:', error);
        status.textContent = 'Échec de l\'analyse';
        showNotification ? 
            showNotification("Erreur lors de l'analyse par GPT: " + error.message, "error") : 
            alert("Erreur lors de l'analyse: " + error.message);
        
        // Utiliser l'analyse locale si configurée
        if (GPT_ANALYZE_CONFIG.useLocalFallback) {
            try {
                // Utiliser JobParserAPI si disponible
                if (window.jobParserAPI) {
                    const localResult = window.jobParserAPI.analyzeJobLocally(jobText);
                    saveParsingResults(localResult);
                    displayParsingResults(localResult);
                    status.textContent = 'Analyse locale utilisée';
                }
            } catch (fallbackError) {
                console.error('Échec de l\'analyse de secours:', fallbackError);
            }
        }
    } finally {
        // Réactiver le bouton
        button.disabled = false;
        
        // Masquer le loader
        const loader = document.getElementById('analysis-loader');
        if (loader) loader.style.display = 'none';
        
        // Changer le texte du statut après 3 secondes
        setTimeout(() => {
            if (status.textContent !== 'Échec de l\'analyse') {
                status.textContent = '';
            }
        }, 3000);
    }
}

// Fonction pour lire un fichier et le convertir en texte
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = event => resolve(event.target.result);
        reader.onerror = error => reject(error);
        reader.readAsText(file);
    });
}

// Fonction pour envoyer la fiche de poste à l'API de parsing GPT
async function parseJobPostingWithGpt(jobText, file = null) {
    // Vérifier si nous avons le code GPT CLI directement intégré
    if (typeof parseJobWithGptLocally === 'function') {
        // Utiliser la fonction locale si elle existe
        return parseJobWithGptLocally(jobText);
    }
    
    // Sinon, faire un appel API 
    const formData = new FormData();
    
    if (file) {
        formData.append('file', file);
    } else {
        formData.append('text', jobText);
    }
    
    // Déterminer l'URL de l'API
    const apiUrl = determineApiUrl();
    
    // Log de debug
    if (GPT_ANALYZE_CONFIG.debug) {
        console.log('Calling API:', apiUrl);
        console.log('With data:', file ? 'File: ' + file.name : 'Text length: ' + jobText.length);
    }
    
    // Appel à l'API de parsing
    const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData,
    });
    
    // Vérifier la réponse
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur ${response.status}: ${errorText}`);
    }
    
    // Analyser la réponse JSON
    const result = await response.json();
    
    // Log de debug
    if (GPT_ANALYZE_CONFIG.debug) {
        console.log('API Response:', result);
    }
    
    return result;
}

// Fonction pour déterminer l'URL de l'API
function determineApiUrl() {
    // Vérifier si l'URL est définie dans l'URL de la page
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('apiUrl')) {
        return urlParams.get('apiUrl') + '/api/parse-job';
    }
    
    // Sinon, utiliser la configuration par défaut
    return GPT_ANALYZE_CONFIG.apiUrl;
}

// Fonction pour sauvegarder les résultats du parsing
function saveParsingResults(result) {
    try {
        // Convertir le résultat en format compatible
        const formattedResult = formatParsingResult(result);
        
        // Sauvegarder dans sessionStorage
        sessionStorage.setItem('parsedJobData', JSON.stringify(formattedResult));
        
        // Backup dans localStorage si nécessaire
        localStorage.setItem('parsedJobData', JSON.stringify(formattedResult));
        
        if (GPT_ANALYZE_CONFIG.debug) {
            console.log('Saved parsing results:', formattedResult);
        }
    } catch (error) {
        console.error('Error saving parsing results:', error);
    }
}

// Fonction pour formater les résultats du parsing au format attendu par l'interface
function formatParsingResult(result) {
    // Si le résultat est déjà au bon format, le retourner directement
    if (result.job_info || result.title || result.skills) {
        return result;
    }
    
    // Si nous avons un format différent, adapter le résultat
    // Exemple: adaptateur pour job_parser_gpt_cli.py
    if (result.job_info) {
        const jobInfo = result.job_info;
        return {
            title: jobInfo.titre_poste || '',
            company: jobInfo.entreprise || '',
            location: jobInfo.localisation || '',
            contract_type: jobInfo.type_contrat || '',
            skills: Array.isArray(jobInfo.competences) ? jobInfo.competences : [jobInfo.competences].filter(Boolean),
            experience: jobInfo.experience || '',
            education: jobInfo.formation || '',
            salary: jobInfo.salaire || '',
            description: jobInfo.description || '',
            published_date: jobInfo.date_publication || '',
            
            // Ajouter des champs supplémentaires pour la compatibilité avec l'interface
            responsibilities: jobInfo.description ? [jobInfo.description] : [],
            benefits: []
        };
    }
    
    // Adapter d'autres formats si nécessaire
    return {
        title: result.title || result.titre_poste || '',
        company: result.company || result.entreprise || '',
        location: result.location || result.localisation || '',
        contract_type: result.contract_type || result.type_contrat || '',
        skills: result.skills || result.competences || [],
        experience: result.experience || '',
        education: result.education || result.formation || '',
        salary: result.salary || result.salaire || '',
        description: result.description || '',
        responsibilities: result.responsibilities || [],
        benefits: result.benefits || []
    };
}

// Fonction pour afficher les résultats du parsing
function displayParsingResults(result) {
    // Si showJobResults existe, l'utiliser
    if (typeof showJobResults === 'function') {
        showJobResults(formatParsingResult(result));
        return;
    }
    
    // Sinon, implémentation basique
    const formattedResult = formatParsingResult(result);
    
    // Afficher les résultats dans les éléments existants
    const elements = {
        'job-title-value': formattedResult.title,
        'job-contract-value': formattedResult.contract_type,
        'job-location-value': formattedResult.location,
        'job-experience-value': formattedResult.experience,
        'job-education-value': formattedResult.education || 'À déterminer',
        'job-salary-value': formattedResult.salary
    };
    
    // Mettre à jour les valeurs
    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element && value) {
            element.textContent = value;
        }
    }
    
    // Gestion des compétences (si c'est un tableau)
    if (formattedResult.skills && formattedResult.skills.length > 0) {
        const skillsElement = document.getElementById('job-skills-value');
        if (skillsElement) {
            skillsElement.innerHTML = formattedResult.skills.map(skill => 
                `<span class="tag">${skill}</span>`
            ).join('');
        }
    }
    
    // Gestion des responsabilités
    if (formattedResult.responsibilities && formattedResult.responsibilities.length > 0) {
        const respElement = document.getElementById('job-responsibilities-value');
        if (respElement) {
            respElement.innerHTML = '<ul>' + 
                formattedResult.responsibilities.map(resp => `<li>${resp}</li>`).join('') + 
                '</ul>';
        }
    }
    
    // Gestion des avantages
    if (formattedResult.benefits && formattedResult.benefits.length > 0) {
        const benefitsElement = document.getElementById('job-benefits-value');
        if (benefitsElement) {
            benefitsElement.innerHTML = '<ul>' + 
                formattedResult.benefits.map(benefit => `<li>${benefit}</li>`).join('') + 
                '</ul>';
        }
    }
    
    // Afficher le conteneur
    const container = document.getElementById('job-info-container');
    if (container) {
        container.style.display = 'block';
    }
}

// Fonction locale pour analyser une fiche de poste avec GPT (si l'API n'est pas disponible)
function parseJobWithGptLocally(jobText) {
    // Cette fonction est intentionnellement laissée vide, elle sera remplacée par l'implémentation du client
    // Si vous souhaitez implémenter une analyse locale avec JavaScript pur, faites-le ici
    console.warn('Local GPT analysis not implemented');
    throw new Error('Local GPT analysis not implemented');
}

// Initialiser l'analyse GPT lorsque la page est chargée
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le bouton d'analyse GPT
    initializeGptAnalyzeButton();
    
    // Vérifier les paramètres d'URL pour la configuration
    const urlParams = new URLSearchParams(window.location.search);
    
    // Configurer le mode debug si nécessaire
    if (urlParams.has('debug')) {
        GPT_ANALYZE_CONFIG.debug = true;
        console.log('GPT Analyze Debug Mode Enabled');
    }
    
    // Configurer l'URL de l'API si fournie
    if (urlParams.has('apiUrl')) {
        GPT_ANALYZE_CONFIG.apiUrl = urlParams.get('apiUrl');
        console.log('GPT Analyze API URL set to:', GPT_ANALYZE_CONFIG.apiUrl);
    }
    
    console.log('GPT Analyze initialized');
});