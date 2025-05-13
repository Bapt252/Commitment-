/**
 * gpt-analyze.js
 * Script pour connecter le frontend de client-questionnaire.html avec le système de parsing GPT
 * Ce script ajoute une fonctionnalité d'analyse de fiches de poste en utilisant le modèle GPT
 */

// Configuration de base 
const GPT_ANALYZE_CONFIG = {
    // URL de l'API de parsing, à adapter selon l'environnement
    apiUrl: 'https://api.openai.com/v1/chat/completions',
    apiKey: '', // Laissé vide intentionnellement, sera fourni via paramètre URL ou config
    model: 'gpt-3.5-turbo', // Modèle GPT à utiliser
    debug: false,
    useLocalFallback: true
};

// Fonction pour afficher une notification si non disponible globalement
function showNotificationLocal(message, type = 'info') {
    if (typeof window.showNotification === 'function') {
        window.showNotification(message, type);
        return;
    }
    
    // Créer une notification temporaire
    const notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.padding = '10px 15px';
    notification.style.borderRadius = '4px';
    notification.style.color = 'white';
    notification.style.zIndex = '10000';
    notification.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
    
    if (type === 'error') {
        notification.style.backgroundColor = '#ef4444';
    } else if (type === 'success') {
        notification.style.backgroundColor = '#10b981';
    } else {
        notification.style.backgroundColor = '#3b82f6';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.5s';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 500);
    }, 3000);
}

// Créer un bouton "Analyser avec GPT" dans la page
function initializeGptAnalyzeButton() {
    // Vérifier si les éléments nécessaires existent dans la page
    const jobInfoContainer = document.getElementById('job-info-container');
    const textarea = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    
    if (!textarea) {
        console.error('Textarea non trouvé dans la page');
        return;
    }
    
    // Créer le conteneur pour le bouton et le statut
    const container = document.createElement('div');
    container.className = 'gpt-analyze-btn-container';
    
    // Créer le bouton "Analyser avec GPT"
    const button = document.createElement('button');
    button.id = 'analyze-with-gpt';
    button.className = 'btn btn-success';
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
    } else if (jobInfoContainer) {
        jobInfoContainer.insertAdjacentElement('beforebegin', container);
    } else {
        // Tenter de trouver un autre endroit pour insérer le bouton
        const possibleParents = [
            document.querySelector('.textarea-container'),
            document.querySelector('.form-section[data-step="3"]')
        ];
        
        for (const parent of possibleParents) {
            if (parent) {
                parent.appendChild(container);
                break;
            }
        }
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
    
    console.log('GPT Analyze Button initialized');
}

// Fonction pour analyser la fiche de poste avec GPT
async function handleGptAnalysis() {
    console.log('handleGptAnalysis called');
    
    const textarea = document.getElementById('job-description-text');
    const fileInput = document.getElementById('job-file-input');
    const button = document.getElementById('analyze-with-gpt');
    const status = document.getElementById('gpt-analyze-status');
    
    // Vérifier si la fonction est bien appelée
    if (!textarea) {
        console.error('Textarea non trouvé lors de l\'analyse');
        return;
    }
    
    // Vérifier que nous avons du contenu à analyser
    if (!(textarea.value.trim() || (fileInput && fileInput.files.length > 0))) {
        showNotificationLocal("Veuillez d'abord entrer ou télécharger une fiche de poste", "error");
        return;
    }
    
    // Vérifier la configuration du backend
    const apiUrl = determineApiUrl();
    if (!apiUrl || (!getApiKey() && apiUrl.includes('api.openai.com'))) {
        // Afficher un message indiquant que la configuration est nécessaire
        showNotificationLocal("Veuillez configurer l'API en cliquant sur le bouton de configuration en bas à droite", "error");
        
        // Assurer que le bouton de configuration est visible
        const configButton = document.getElementById('backend-config-button');
        if (configButton) {
            configButton.style.display = 'flex';
            configButton.style.opacity = '1';
            configButton.style.zIndex = '9999';
            
            // Animer pour attirer l'attention
            configButton.style.animation = 'pulse 1s infinite';
            if (!configButton.style.cssText.includes('@keyframes pulse')) {
                const style = document.createElement('style');
                style.textContent = `
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.1); }
                        100% { transform: scale(1); }
                    }
                `;
                document.head.appendChild(style);
            }
        }
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
        showNotificationLocal("Fiche de poste analysée avec succès par GPT!", "success");
        
    } catch (error) {
        console.error('Erreur lors de l\'analyse GPT:', error);
        status.textContent = 'Échec de l\'analyse';
        showNotificationLocal("Erreur lors de l'analyse par GPT: " + error.message, "error");
        
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
    console.log('Parsing job posting with GPT');
    
    // Création d'un prompt pour analyser la fiche de poste
    const prompt = `Extrais les informations clés de cette fiche de poste pour un parser automatique. 
    Pour chaque champ, cherche les informations pertinentes et les retourne au format précis.
    
    Voici la fiche de poste à analyser:
    ${jobText}
    
    Retourne les informations au format JSON suivant:
    {
        "title": "Titre du poste",
        "company": "Nom de l'entreprise",
        "location": "Localisation du poste",
        "contract_type": "Type de contrat (CDI, CDD, etc.)",
        "skills": ["Compétence 1", "Compétence 2", ...],
        "experience": "Niveau d'expérience requis",
        "education": "Formation requise",
        "salary": "Salaire proposé",
        "responsibilities": ["Responsabilité 1", "Responsabilité 2", ...],
        "benefits": ["Avantage 1", "Avantage 2", ...]
    }
    
    Si certaines informations ne sont pas trouvées, utilise une valeur par défaut comme une chaîne vide ou un tableau vide.
    Réponds uniquement avec le JSON, sans aucun texte supplémentaire.`;
    
    try {
        // Vérifier si nous utilisons l'API OpenAI directement ou un backend personnalisé
        const apiKey = getApiKey();
        const isCustomBackend = isUsingCustomBackend();
        
        console.log('Using custom backend:', isCustomBackend);
        
        if (!apiKey && !isCustomBackend) {
            throw new Error("Clé API non configurée. Veuillez fournir une clé API via les paramètres d'URL (apiKey=...) ou utiliser un backend personnalisé");
        }
        
        // Déterminer l'URL de l'API à utiliser
        const apiUrl = determineApiUrl();
        console.log('API URL:', apiUrl);
        
        // Log de debug
        if (GPT_ANALYZE_CONFIG.debug) {
            console.log('Calling API:', apiUrl);
            console.log('Model:', GPT_ANALYZE_CONFIG.model);
        }
        
        // Si nous utilisons un backend personnalisé, envoyer une requête différente
        if (isCustomBackend) {
            return await callCustomBackend(apiUrl, jobText, file);
        }
        
        // Construction de la requête pour l'API OpenAI
        const requestBody = {
            model: GPT_ANALYZE_CONFIG.model,
            messages: [
                { role: "system", content: "Tu es un assistant spécialisé dans l'analyse de fiches de poste. Tu réponds uniquement au format JSON." },
                { role: "user", content: prompt }
            ],
            temperature: 0.2 // Réduire la créativité pour des résultats plus précis
        };
        
        // Options de la requête
        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify(requestBody)
        };
        
        // Appel à l'API OpenAI
        const response = await fetch(apiUrl, requestOptions);
        
        // Vérifier la réponse
        if (!response.ok) {
            const errorResponse = await response.json();
            throw new Error(`Erreur API (${response.status}): ${errorResponse.error?.message || 'Erreur inconnue'}`);
        }
        
        // Récupérer la réponse
        const responseData = await response.json();
        
        // Extraire le contenu JSON de la réponse
        let parsedResult;
        try {
            // Vérifier si la réponse de l'API est déjà au format JSON
            if (responseData.choices && responseData.choices.length > 0) {
                const contentText = responseData.choices[0].message.content;
                
                // Tenter d'extraire un JSON valide du texte
                const jsonMatch = contentText.match(/\{[\s\S]*\}/);
                if (jsonMatch) {
                    parsedResult = JSON.parse(jsonMatch[0]);
                } else {
                    parsedResult = JSON.parse(contentText); // Essayer de parser tout le contenu
                }
            } else if (responseData.result) {
                // Format d'API personnalisée qui renvoie directement un résultat
                parsedResult = responseData.result;
            } else {
                // En dernier recours, supposer que la réponse entière est le JSON
                parsedResult = responseData;
            }
        } catch (error) {
            console.error('Erreur lors du parsing du JSON:', error);
            throw new Error('Le résultat de l\'analyse GPT n\'est pas au format JSON attendu');
        }
        
        if (GPT_ANALYZE_CONFIG.debug) {
            console.log('Parsed result:', parsedResult);
        }
        
        return parsedResult;
    } catch (error) {
        console.error('Erreur lors de l\'analyse avec GPT:', error);
        throw error;
    }
}

// Fonction pour déterminer si on utilise un backend personnalisé
function isUsingCustomBackend() {
    // Vérifier si l'URL contient un chemin d'API personnalisé
    const apiUrl = determineApiUrl();
    return !apiUrl.includes('api.openai.com');
}

// Fonction pour appeler un backend personnalisé
async function callCustomBackend(apiUrl, jobText, file) {
    console.log('Calling custom backend:', apiUrl);
    
    // Créer un objet FormData pour l'envoi de données
    const formData = new FormData();
    
    if (file) {
        formData.append('file', file);
    } else {
        formData.append('text', jobText);
    }
    
    // Options de la requête
    const requestOptions = {
        method: 'POST',
        body: formData
    };
    
    // Log de debug
    if (GPT_ANALYZE_CONFIG.debug) {
        console.log('Calling custom backend:', apiUrl);
    }
    
    // Appel au backend
    const response = await fetch(apiUrl, requestOptions);
    
    // Vérifier la réponse
    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Erreur backend (${response.status}): ${errorText}`);
    }
    
    // Récupérer la réponse
    return await response.json();
}

// Fonction pour récupérer la clé API à partir des paramètres ou de la configuration
function getApiKey() {
    // Vérifier dans localStorage (sauvegarde par le panneau de configuration)
    const savedKey = localStorage.getItem('openaiKey');
    if (savedKey) {
        return savedKey;
    }
    
    // Vérifier dans les paramètres d'URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('apiKey')) {
        return urlParams.get('apiKey');
    }
    
    // Sinon, utiliser la clé configurée
    return GPT_ANALYZE_CONFIG.apiKey;
}

// Fonction pour déterminer l'URL de l'API
function determineApiUrl() {
    // Vérifier d'abord dans localStorage (sauvegarde par le panneau de configuration)
    const savedUrl = localStorage.getItem('backendUrl');
    if (savedUrl) {
        return savedUrl.endsWith('/api/parse-job') ? savedUrl : `${savedUrl}/api/parse-job`;
    }
    
    // Vérifier si l'URL est définie dans l'URL de la page
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('apiUrl')) {
        // Si c'est une URL complète, l'utiliser directement
        const apiUrlParam = urlParams.get('apiUrl');
        if (apiUrlParam.startsWith('http')) {
            return apiUrlParam.endsWith('/api/parse-job') ? apiUrlParam : `${apiUrlParam}/api/parse-job`;
        }
        return `http://${apiUrlParam}/api/parse-job`;
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
    if (result.title || result.skills) {
        return result;
    }
    
    // Si nous avons un format différent, adapter le résultat
    // Exemple: adaptateur pour job_parser_gpt_cli.py
    if (result.job_info) {
        const jobInfo = result.job_info;
        return {
            title: jobInfo.titre_poste || jobInfo.titre || '',
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
        title: result.title || result.titre_poste || result.titre || '',
        company: result.company || result.entreprise || '',
        location: result.location || result.localisation || '',
        contract_type: result.contract_type || result.type_contrat || '',
        skills: (result.skills || result.competences || []).filter(Boolean),
        experience: result.experience || '',
        education: result.education || result.formation || '',
        salary: result.salary || result.salaire || '',
        description: result.description || '',
        responsibilities: (result.responsibilities || []).filter(Boolean),
        benefits: (result.benefits || []).filter(Boolean)
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

// Initialiser l'analyse GPT lorsque la page est chargée
document.addEventListener('DOMContentLoaded', function() {
    console.log('GPT Analyze script loaded');
    
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
        // Ne pas modifier l'URL directement ici, utiliser determineApiUrl() pour l'obtenir
        console.log('GPT Analyze API URL set from URL parameters');
    }
    
    // Configurer la clé API si fournie
    if (urlParams.has('apiKey')) {
        GPT_ANALYZE_CONFIG.apiKey = urlParams.get('apiKey');
        console.log('GPT Analyze API Key set from URL parameters');
    }
    
    // Configurer le modèle si fourni
    if (urlParams.has('model')) {
        GPT_ANALYZE_CONFIG.model = urlParams.get('model');
        console.log('GPT Analyze Model set to:', GPT_ANALYZE_CONFIG.model);
    }
    
    console.log('GPT Analyze initialized');
});

// Fonction pour forcer la réinitialisation des éléments après le chargement complet
window.addEventListener('load', function() {
    setTimeout(function() {
        // Réinitialiser le bouton GPT
        if (!document.getElementById('analyze-with-gpt')) {
            console.log('Réinitialisation du bouton GPT');
            initializeGptAnalyzeButton();
        }
        
        // Vérifier si le bouton de configuration est visible
        const configButton = document.getElementById('backend-config-button');
        if (configButton) {
            configButton.style.display = 'flex';
            configButton.style.opacity = '1';
            configButton.style.visibility = 'visible';
            configButton.style.zIndex = '9999';
        }
    }, 2000);
});
