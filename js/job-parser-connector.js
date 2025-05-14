/**
 * job-parser-connector.js
 * Ce script connecte l'interface frontend de client-questionnaire.html avec le service de parsing GPT
 * Il s'agit d'un middleware pour assurer la communication entre les deux composants
 */

// Configuration du connecteur
const JOB_PARSER_CONNECTOR = {
    // URL par défaut du service de parsing (peut être remplacée par paramètre URL)
    apiBaseUrl: 'http://localhost:5055',
    debug: false,
    enableLocalFallback: true
};

// Initialiser le connecteur dès le chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initJobParserConnector();
});

/**
 * Initialise le connecteur entre le frontend et le backend
 */
async function initJobParserConnector() {
    // Configurer à partir des paramètres d'URL
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.has('debug')) {
        JOB_PARSER_CONNECTOR.debug = true;
        console.log('Job Parser Connector: Debug mode enabled');
    }
    
    // Essayer de détecter automatiquement un backend local si aucun n'est spécifié
    if (!urlParams.has('apiUrl')) {
        const detectedUrl = await tryAutoDetectBackend();
        if (detectedUrl) {
            JOB_PARSER_CONNECTOR.apiBaseUrl = detectedUrl;
            if (JOB_PARSER_CONNECTOR.debug) {
                console.log('Backend détecté automatiquement:', detectedUrl);
            }
            
            // Mettre à jour l'URL pour les futurs rechargements
            updateUrlWithBackend(detectedUrl);
        }
    } else {
        JOB_PARSER_CONNECTOR.apiBaseUrl = urlParams.get('apiUrl');
    }

    // S'assurer que JobParserAPI est correctement initialisée avec nos paramètres
    if (window.JobParserAPI) {
        window.jobParserAPI = new JobParserAPI({
            apiUrl: `${JOB_PARSER_CONNECTOR.apiBaseUrl}/api/parse-job`,
            debug: JOB_PARSER_CONNECTOR.debug,
            enablePDFCleaning: true
        });
        
        if (JOB_PARSER_CONNECTOR.debug) {
            console.log('Job Parser API initialized with URL:', JOB_PARSER_CONNECTOR.apiBaseUrl);
        }
    } else {
        console.error('JobParserAPI class not found. Make sure job-parser-api.js is loaded before this script.');
    }

    // Connecter les boutons d'analyse
    connectAnalyzeButtons();
    
    // Vérifier la connexion au backend
    testBackendConnection();
}

/**
 * Tente de détecter automatiquement un backend en cours d'exécution
 * @returns {Promise<string|null>} L'URL du backend détecté ou null si aucun n'est trouvé
 */
async function tryAutoDetectBackend() {
    // Liste des URLs de backend à tester
    const potentialBackends = [
        'http://localhost:5055',  // Serveur local standard
        'http://127.0.0.1:5055',  // Alternative localhost
        'http://localhost:5056',  // Port alternatif 1
        'http://127.0.0.1:5056',  // Port alternatif 1 sur 127.0.0.1
        'http://localhost:8055',  // Port alternatif 2
        'http://localhost:3000',  // Port de développement courant
    ];
    
    // URL déjà configurée dans localStorage
    const savedUrl = localStorage.getItem('backendUrl');
    if (savedUrl) {
        // Tester d'abord l'URL sauvegardée
        try {
            const response = await fetch(`${savedUrl}/api/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(500)
            });
            
            if (response.ok) {
                return savedUrl;
            }
        } catch (error) {
            // Ignorer l'erreur et continuer avec les autres URLs
            console.log('Erreur avec l\'URL sauvegardée, test des autres options');
        }
    }
    
    // Tester chaque URL potentielle
    for (const url of potentialBackends) {
        try {
            const response = await fetch(`${url}/api/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(500) // Court timeout pour ne pas bloquer longtemps
            });
            
            if (response.ok) {
                // Sauvegarder l'URL détectée pour les prochaines visites
                localStorage.setItem('backendUrl', url);
                return url;
            }
        } catch (error) {
            // Ignorer les erreurs et essayer l'URL suivante
        }
    }
    
    // Aucun backend trouvé
    return null;
}

/**
 * Met à jour l'URL avec le paramètre du backend sans recharger la page
 * @param {string} backendUrl - L'URL du backend à ajouter aux paramètres
 */
function updateUrlWithBackend(backendUrl) {
    if (!backendUrl) return;
    
    // Créer une nouvelle URL avec les paramètres actuels
    const url = new URL(window.location.href);
    
    // Ajouter ou mettre à jour le paramètre apiUrl
    url.searchParams.set('apiUrl', backendUrl);
    
    // Mettre à jour l'URL sans recharger la page
    window.history.replaceState({}, '', url.toString());
}

/**
 * Connecte les boutons d'analyse aux fonctions correspondantes
 */
function connectAnalyzeButtons() {
    // Connecter le bouton d'analyse de texte
    const analyzeTextBtn = document.getElementById('analyze-job-text');
    if (analyzeTextBtn) {
        analyzeTextBtn.addEventListener('click', handleAnalyzeTextClick);
    } else if (JOB_PARSER_CONNECTOR.debug) {
        console.warn('Button analyze-job-text not found');
    }
    
    // Connecter le bouton d'analyse GPT
    const analyzeGptBtn = document.getElementById('analyze-with-gpt');
    if (analyzeGptBtn) {
        analyzeGptBtn.addEventListener('click', handleAnalyzeGptClick);
        
        // Activer le bouton si du texte est disponible
        const jobText = document.getElementById('job-description-text');
        if (jobText && jobText.value.trim()) {
            analyzeGptBtn.disabled = false;
        }
    } else if (JOB_PARSER_CONNECTOR.debug) {
        console.warn('Button analyze-with-gpt not found');
    }
}

/**
 * Gestionnaire pour le clic sur le bouton d'analyse de texte
 */
async function handleAnalyzeTextClick() {
    const jobText = document.getElementById('job-description-text');
    
    if (!jobText || !jobText.value.trim()) {
        showNotification('Veuillez entrer un texte à analyser', 'error');
        return;
    }
    
    // Afficher le loader
    const loader = document.getElementById('analysis-loader');
    if (loader) loader.style.display = 'flex';
    
    try {
        if (JOB_PARSER_CONNECTOR.debug) {
            console.log('Analyzing text:', jobText.value.substring(0, 100) + '...');
        }
        
        // Utiliser notre API wrapper pour analyser le texte
        const result = await window.jobParserAPI.parseJobText(jobText.value);
        
        // Sauvegarder et afficher les résultats
        sessionStorage.setItem('parsedJobData', JSON.stringify(result));
        showJobResults(result);
        
        showNotification('Analyse réussie!', 'success');
    } catch (error) {
        console.error('Error analyzing text:', error);
        showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
    } finally {
        // Cacher le loader
        if (loader) loader.style.display = 'none';
    }
}

/**
 * Gestionnaire pour le clic sur le bouton d'analyse GPT
 */
async function handleAnalyzeGptClick() {
    const jobText = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    
    if ((!jobText || !jobText.value.trim()) && (!fileInput || !fileInput.files.length)) {
        showNotification('Veuillez fournir une fiche de poste à analyser', 'error');
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
        
        // Utiliser notre API pour l'analyse avec GPT
        if (file) {
            // Envoyer le fichier à notre backend (au lieu de l'API GPT directe)
            result = await parseJobFileWithServer(file);
        } else {
            // Envoyer le texte à notre backend (au lieu de l'API GPT directe)
            result = await parseJobTextWithServer(text);
        }
        
        // Sauvegarder et afficher les résultats
        sessionStorage.setItem('parsedJobData', JSON.stringify(result));
        showJobResults(result);
        
        // Mettre à jour le statut
        if (statusElement) statusElement.textContent = 'Analyse réussie!';
        showNotification('Fiche de poste analysée avec succès!', 'success');
    } catch (error) {
        console.error('Error during GPT analysis:', error);
        
        // Mettre à jour le statut
        if (statusElement) statusElement.textContent = 'Erreur: ' + error.message;
        showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
        
        // Fallback sur l'analyse locale
        if (JOB_PARSER_CONNECTOR.enableLocalFallback && text) {
            try {
                const localResult = window.jobParserAPI.analyzeJobLocally(text);
                sessionStorage.setItem('parsedJobData', JSON.stringify(localResult));
                showJobResults(localResult);
                
                if (statusElement) statusElement.textContent = 'Analyse locale utilisée';
                showNotification('Analyse locale utilisée comme alternative', 'info');
            } catch (fallbackError) {
                console.error('Fallback analysis failed:', fallbackError);
            }
        }
    } finally {
        // Réactiver le bouton
        if (button) button.disabled = false;
        
        // Cacher le loader
        if (loader) loader.style.display = 'none';
    }
}

/**
 * Envoie un texte au serveur backend pour analyse
 * @param {string} text - Le texte à analyser
 * @returns {Promise<Object>} - Les résultats de l'analyse
 */
async function parseJobTextWithServer(text) {
    const apiUrl = `${JOB_PARSER_CONNECTOR.apiBaseUrl}/api/parse-job`;
    
    if (JOB_PARSER_CONNECTOR.debug) {
        console.log(`Sending text to ${apiUrl}`);
    }
    
    // Créer un objet FormData pour l'envoi
    const formData = new FormData();
    formData.append('text', text);
    
    // Envoyer la requête
    const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error (${response.status}): ${errorText}`);
    }
    
    // Récupérer et traiter la réponse
    const data = await response.json();
    return processServerResponse(data);
}

/**
 * Envoie un fichier au serveur backend pour analyse
 * @param {File} file - Le fichier à analyser
 * @returns {Promise<Object>} - Les résultats de l'analyse
 */
async function parseJobFileWithServer(file) {
    const apiUrl = `${JOB_PARSER_CONNECTOR.apiBaseUrl}/api/parse-job`;
    
    if (JOB_PARSER_CONNECTOR.debug) {
        console.log(`Sending file to ${apiUrl}`, file);
    }
    
    // Créer un objet FormData pour l'envoi
    const formData = new FormData();
    formData.append('file', file);
    
    // Envoyer la requête
    const response = await fetch(apiUrl, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error (${response.status}): ${errorText}`);
    }
    
    // Récupérer et traiter la réponse
    const data = await response.json();
    return processServerResponse(data);
}

/**
 * Traite la réponse du serveur backend pour la normaliser
 * @param {Object} response - La réponse du serveur
 * @returns {Object} - Les données normalisées
 */
function processServerResponse(response) {
    // Si la réponse est au format attendu par le frontend, la retourner directement
    if (response.title || response.job_title) {
        return {
            title: response.title || response.job_title || '',
            company: response.company || response.employer || '',
            location: response.location || '',
            contract_type: response.contract_type || response.contract || '',
            skills: Array.isArray(response.skills) ? response.skills : 
                (response.skills ? [response.skills] : []),
            experience: response.experience || '',
            education: response.education || '',
            salary: response.salary || response.compensation || '',
            responsibilities: Array.isArray(response.responsibilities) ? response.responsibilities : 
                (response.responsibilities ? [response.responsibilities] : []),
            benefits: Array.isArray(response.benefits) ? response.benefits : 
                (response.benefits ? [response.benefits] : [])
        };
    }
    
    // Si la réponse est au format job_info (comme job_parser_gpt_cli.py)
    if (response.job_info) {
        const jobInfo = response.job_info;
        return {
            title: jobInfo.titre_poste || jobInfo.titre || '',
            company: jobInfo.entreprise || '',
            location: jobInfo.localisation || '',
            contract_type: jobInfo.type_contrat || '',
            skills: Array.isArray(jobInfo.competences) ? jobInfo.competences : 
                (jobInfo.competences ? [jobInfo.competences] : []),
            experience: jobInfo.experience || '',
            education: jobInfo.formation || '',
            salary: jobInfo.salaire || '',
            responsibilities: jobInfo.description ? [jobInfo.description] : [],
            benefits: []
        };
    }
    
    // Si on n'a pas pu déterminer le format, retourner la réponse telle quelle
    return response;
}

/**
 * Teste la connexion au backend et met à jour l'interface en conséquence
 */
async function testBackendConnection() {
    const gptButton = document.getElementById('analyze-with-gpt');
    const statusElement = document.getElementById('gpt-analyze-status');
    const backendStatusBanner = document.getElementById('backend-status-banner');
    const backendStatusText = document.getElementById('backend-status-text');
    
    try {
        // Tester la connexion avec une requête simple
        const response = await fetch(`${JOB_PARSER_CONNECTOR.apiBaseUrl}/api/health`, {
            method: 'GET',
            // Timeout court pour ne pas bloquer l'interface
            signal: AbortSignal.timeout(2000)
        });
        
        if (response.ok) {
            // Connexion réussie
            if (JOB_PARSER_CONNECTOR.debug) {
                console.log('Backend connection successful');
            }
            
            if (statusElement) {
                statusElement.textContent = 'Connecté au service d\'analyse';
                statusElement.style.color = 'green';
            }
            
            // Mettre à jour la bannière d'état si elle existe
            if (backendStatusBanner && backendStatusText) {
                backendStatusBanner.className = 'backend-status-banner connected';
                backendStatusText.textContent = 'Connecté au service d\'analyse GPT';
            }
            
            // Activer le bouton GPT si du texte est présent
            const jobText = document.getElementById('job-description-text');
            if (gptButton && jobText && jobText.value.trim()) {
                gptButton.disabled = false;
            }
        } else {
            throw new Error(`Backend responded with ${response.status}`);
        }
    } catch (error) {
        if (JOB_PARSER_CONNECTOR.debug) {
            console.warn('Backend connection failed:', error);
        }
        
        if (statusElement) {
            statusElement.textContent = 'Service non disponible';
            statusElement.style.color = 'red';
        }
        
        // Mettre à jour la bannière d'état si elle existe
        if (backendStatusBanner && backendStatusText) {
            backendStatusBanner.className = 'backend-status-banner disconnected';
            backendStatusText.textContent = 'Service d\'analyse GPT non disponible - Vérifiez la configuration';
        }
        
        // Désactiver le bouton GPT si la connexion a échoué
        if (gptButton) {
            gptButton.disabled = true;
            gptButton.title = 'Service d\'analyse GPT non disponible';
        }
    }
}
