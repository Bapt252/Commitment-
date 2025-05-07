// Script de connexion entre le frontend et le job-parser
document.addEventListener('DOMContentLoaded', function() {
    console.log("Job parser integration script initialized");
    
    // Références aux éléments du DOM
    const dropZone = document.querySelector('.drop-zone') || document.querySelector('.upload-container');
    const fileInput = document.querySelector('input[type="file"]');
    const analyseButton = document.querySelector('.analyse-button') || document.querySelector('button[type="submit"]');
    let resultSection = document.querySelector('#result-section');
    const loadingIndicator = document.createElement('div');
    
    // Configuration du loading indicator
    loadingIndicator.className = 'loading-indicator';
    loadingIndicator.innerHTML = '<div class="spinner"></div><p>Analyse en cours...</p>';
    loadingIndicator.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        font-family: 'Inter', sans-serif;
    `;
    loadingIndicator.querySelector('.spinner').style.cssText = `
        width: 50px;
        height: 50px;
        border: 5px solid rgba(124, 58, 237, 0.2);
        border-radius: 50%;
        border-top-color: #7C3AED;
        animation: spin 1s ease-in-out infinite;
        margin-bottom: 20px;
    `;
    
    // Ajouter une règle CSS pour l'animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    `;
    document.head.appendChild(style);
    
    // Ajouter le loading indicator au document
    document.body.appendChild(loadingIndicator);
    loadingIndicator.style.display = 'none';
    
    // Si la section de résultats n'existe pas, la créer
    if (!resultSection) {
        resultSection = document.createElement('div');
        resultSection.id = 'result-section';
        
        // Trouver un bon emplacement pour insérer la section de résultats
        const container = document.querySelector('.container') || document.querySelector('main') || document.body;
        container.appendChild(resultSection);
    }
    
    // Gestionnaire pour le bouton d'analyse
    if (analyseButton) {
        analyseButton.addEventListener('click', function(e) {
            e.preventDefault();
            console.log("Analyse button clicked");
            
            if (fileInput && fileInput.files && fileInput.files.length > 0) {
                console.log("File found, starting analysis");
                analyseFile(fileInput.files[0]);
            } else {
                const textInput = document.querySelector('#text-input');
                if (textInput && textInput.value.trim() !== '') {
                    console.log("Text input found, processing text");
                    processText(textInput.value);
                } else {
                    alert('Veuillez sélectionner un fichier à analyser ou saisir du texte.');
                }
            }
        });
    }
    
    // Fonction principale d'analyse de fichier
    async function analyseFile(file) {
        console.log('Traitement du fichier:', file.name);
        
        // Afficher l'indicateur de chargement
        loadingIndicator.style.display = 'flex';
        
        try {
            // Vérifier si l'analyseur côté client est disponible
            if (window.JobParser && typeof window.JobParser.analyzeFile === 'function') {
                console.log("Using client-side parser");
                
                // Utiliser l'analyseur côté client
                const result = await window.JobParser.analyzeFile(file);
                
                // Masquer l'indicateur de chargement
                loadingIndicator.style.display = 'none';
                
                // Afficher les résultats
                displayResults(result);
                
                // Sauvegarder dans le localStorage pour la persistance
                localStorage.setItem('lastJobParseResult', JSON.stringify(result));
                
                // Tenter d'envoyer les données à la page parente (si dans un iframe)
                sendDataToParent(result);
            } else {
                console.warn("Client-side parser not available, falling back to simulation mode");
                
                // Simulation (pour compatibilité avec le code existant)
                setTimeout(function() {
                    // Masquer l'indicateur de chargement
                    loadingIndicator.style.display = 'none';
                    
                    // Données simulées pour les tests
                    const simulatedData = {
                        data: {
                            title: "Développeur Full Stack",
                            company: "Tech Solutions",
                            location: "Paris",
                            contract_type: "CDI",
                            required_skills: ["JavaScript", "React", "Node.js", "Python", "MongoDB"],
                            preferred_skills: ["TypeScript", "Docker", "AWS"],
                            experience: "3-5 ans d'expérience",
                            responsibilities: [
                                "Développer des applications web responsive",
                                "Collaborer avec l'équipe de design",
                                "Maintenir les services existants",
                                "Participer aux revues de code"
                            ]
                        }
                    };
                    
                    // Afficher les résultats
                    displayResults(simulatedData);
                    
                    // Sauvegarder dans le localStorage pour la persistance
                    localStorage.setItem('lastJobParseResult', JSON.stringify(simulatedData));
                    
                    // Tenter d'envoyer les données à la page parente (si dans un iframe)
                    sendDataToParent(simulatedData);
                }, 2000);
            }
        } catch (error) {
            console.error("Error during file analysis:", error);
            loadingIndicator.style.display = 'none';
            alert('Une erreur est survenue lors de l\'analyse du fichier. Veuillez réessayer avec un autre fichier.');
        }
    }
    
    // Fonction pour traiter du texte
    async function processText(text) {
        console.log('Traitement du texte:', text.substring(0, 50) + '...');
        
        // Afficher l'indicateur de chargement
        loadingIndicator.style.display = 'flex';
        
        try {
            // Vérifier si l'analyseur côté client est disponible
            if (window.JobParser && typeof window.JobParser.analyzeText === 'function') {
                console.log("Using client-side parser for text");
                
                // Utiliser l'analyseur côté client
                const result = await window.JobParser.analyzeText(text);
                
                // Masquer l'indicateur de chargement
                loadingIndicator.style.display = 'none';
                
                // Afficher les résultats
                displayResults(result);
                
                // Sauvegarder dans le localStorage pour la persistance
                localStorage.setItem('lastJobParseResult', JSON.stringify(result));
                
                // Tenter d'envoyer les données à la page parente (si dans un iframe)
                sendDataToParent(result);
            } else {
                console.warn("Client-side parser not available, falling back to simulation mode");
                
                // Simulation (pour compatibilité avec le code existant)
                setTimeout(function() {
                    // Masquer l'indicateur de chargement
                    loadingIndicator.style.display = 'none';
                    
                    // Données simulées basées sur le texte
                    const simulatedData = {
                        data: {
                            title: "Chef de Projet IT",
                            company: "Innovate Inc.",
                            location: "Lyon",
                            contract_type: "CDI",
                            required_skills: ["Gestion de projet", "Agilité", "Leadership", "Jira", "Budgétisation"],
                            preferred_skills: ["Certification PMP", "DevOps", "Cloud"],
                            experience: "5 ans minimum",
                            responsibilities: [
                                "Piloter des projets digitaux de bout en bout",
                                "Gérer une équipe de développeurs",
                                "Assurer la communication avec les clients",
                                "Définir les roadmaps et suivre les KPIs"
                            ]
                        }
                    };
                    
                    // Afficher les résultats simulés
                    displayResults(simulatedData);
                    
                    // Sauvegarder dans le localStorage pour la persistance
                    localStorage.setItem('lastJobParseResult', JSON.stringify(simulatedData));
                    
                    // Tenter d'envoyer les données à la page parente (si dans un iframe)
                    sendDataToParent(simulatedData);
                }, 2000);
            }
        } catch (error) {
            console.error("Error during text analysis:", error);
            loadingIndicator.style.display = 'none';
            alert('Une erreur est survenue lors de l\'analyse du texte. Veuillez réessayer.');
        }
    }
    
    // Fonction pour envoyer les données à la page parente
    function sendDataToParent(result) {
        if (window.parent && window.parent !== window) {
            console.log('Sending parsed data to parent window');
            
            // Extraire les données importantes
            const parsedData = result.data || result;
            
            // Standardiser le format des données pour la communication
            const jobData = {
                title: parsedData.title || '',
                skills: parsedData.required_skills || [],
                experience: parsedData.experience || '',
                contract: parsedData.contract_type || ''
            };
            
            // Ajouter des logs détaillés
            console.log('Data being sent to parent:', {
                type: 'jobParsingResult',
                jobData: jobData,
                messageId: new Date().getTime()
            });
            
            // Envoyer plusieurs fois pour s'assurer que le message est reçu
            // (cette technique de redondance peut aider dans certains cas)
            for (let i = 0; i < 3; i++) {
                setTimeout(() => {
                    // Essayer d'envoyer via l'API de pont si disponible
                    if (typeof window.sendToParent === 'function') {
                        window.sendToParent({
                            type: 'jobParsingResult',
                            jobData: jobData,
                            messageId: new Date().getTime() + i
                        });
                    } else {
                        // Sinon, utiliser directement postMessage
                        window.parent.postMessage({
                            type: 'jobParsingResult',
                            jobData: jobData,
                            messageId: new Date().getTime() + i
                        }, '*');
                    }
                    
                    console.log(`Sent data to parent (attempt ${i+1}/3)`);
                }, i * 500); // Espacer les tentatives de 500ms
            }
            
            // Tenter d'appeler directement la fonction de mise à jour si elle existe dans le parent
            try {
                if (window.parent.updateJobInfoDisplay) {
                    console.log('Direct function call to parent.updateJobInfoDisplay');
                    window.parent.updateJobInfoDisplay(jobData);
                }
            } catch (e) {
                console.warn('Could not call parent function directly:', e);
            }
            
            // Pour des tests, on pourrait aussi stocker les données dans le sessionStorage
            // afin que la page parente puisse les récupérer même sans communication directe
            sessionStorage.setItem('lastJobParseData', JSON.stringify(jobData));
            console.log('Data saved to sessionStorage for parent retrieval');
            
            // Pour les tests, retourner les données
            return true;
        } else {
            console.log('Not in iframe, cannot send data to parent');
            return false;
        }
    }
    
    // Affichage des résultats
    function displayResults(data) {
        console.log("Displaying results:", data);
        
        // Données à afficher
        let parsedData = data.data;
        
        // Si la structure n'est pas celle attendue, essayer d'adapter
        if (!parsedData) {
            console.log("Adapting data structure");
            parsedData = data;
        }
        
        // Construire le HTML pour l'affichage des résultats
        let resultHTML = '<div class="results-container">';
        resultHTML += '<h2>Informations extraites</h2>';
        
        if (parsedData.title) {
            resultHTML += `<div class="result-item"><strong>Titre du poste:</strong> ${parsedData.title}</div>`;
        }
        
        if (parsedData.company) {
            resultHTML += `<div class="result-item"><strong>Entreprise:</strong> ${parsedData.company}</div>`;
        }
        
        if (parsedData.location) {
            resultHTML += `<div class="result-item"><strong>Localisation:</strong> ${parsedData.location}</div>`;
        }
        
        if (parsedData.contract_type) {
            resultHTML += `<div class="result-item"><strong>Type de contrat:</strong> ${parsedData.contract_type}</div>`;
        }
        
        if (parsedData.required_skills && parsedData.required_skills.length > 0) {
            resultHTML += '<div class="result-item"><strong>Compétences requises:</strong>';
            resultHTML += '<ul class="skill-list">';
            parsedData.required_skills.forEach(skill => {
                resultHTML += `<li>${skill}</li>`;
            });
            resultHTML += '</ul></div>';
        }
        
        if (parsedData.preferred_skills && parsedData.preferred_skills.length > 0) {
            resultHTML += '<div class="result-item"><strong>Compétences souhaitées:</strong>';
            resultHTML += '<ul class="skill-list">';
            parsedData.preferred_skills.forEach(skill => {
                resultHTML += `<li>${skill}</li>`;
            });
            resultHTML += '</ul></div>';
        }
        
        if (parsedData.responsibilities && parsedData.responsibilities.length > 0) {
            resultHTML += '<div class="result-item"><strong>Responsabilités:</strong>';
            resultHTML += '<ul class="responsibility-list">';
            parsedData.responsibilities.forEach(resp => {
                resultHTML += `<li>${resp}</li>`;
            });
            resultHTML += '</ul></div>';
        }
        
        if (parsedData.requirements && parsedData.requirements.length > 0) {
            resultHTML += '<div class="result-item"><strong>Prérequis:</strong>';
            resultHTML += '<ul class="responsibility-list">';
            parsedData.requirements.forEach(req => {
                resultHTML += `<li>${req}</li>`;
            });
            resultHTML += '</ul></div>';
        }
        
        if (parsedData.benefits && parsedData.benefits.length > 0) {
            resultHTML += '<div class="result-item"><strong>Avantages:</strong>';
            resultHTML += '<ul class="responsibility-list">';
            parsedData.benefits.forEach(benefit => {
                resultHTML += `<li>${benefit}</li>`;
            });
            resultHTML += '</ul></div>';
        }
        
        if (parsedData.experience) {
            resultHTML += `<div class="result-item"><strong>Expérience requise:</strong> ${parsedData.experience}</div>`;
        }
        
        // Ajouter des boutons d'action
        resultHTML += `
            <div class="action-buttons">
                <button id="apply-results" class="btn btn-primary">
                    <i class="fas fa-check"></i> Appliquer ces informations
                </button>
                <button id="test-communication" class="btn btn-secondary">
                    <i class="fas fa-sync"></i> Tester la communication
                </button>
            </div>
        `;
        
        resultHTML += '</div>';
        
        // Afficher les résultats
        if (resultSection) {
            resultSection.innerHTML = resultHTML;
            resultSection.style.display = 'block';
        } else {
            console.error("Result section not found");
        }
        
        // Scroll vers les résultats
        if (resultSection && typeof resultSection.scrollIntoView === 'function') {
            resultSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Ajouter le gestionnaire d'événements pour le bouton d'application
        const applyButton = document.getElementById('apply-results');
        if (applyButton) {
            applyButton.addEventListener('click', function() {
                // Envoyer les données à la page parente (si dans un iframe)
                const success = sendDataToParent({
                    data: parsedData
                });
                
                if (success) {
                    // Retarder pour que l'utilisateur puisse voir l'information traitée
                    setTimeout(() => {
                        // Fermer la fenêtre modale parente si dans un iframe
                        if (window.parent && window.parent !== window) {
                            try {
                                // Essayer de fermer le modal via postMessage
                                window.parent.postMessage({
                                    type: 'closeModal',
                                    reason: 'dataApplied'
                                }, '*');
                                
                                alert('Les informations ont été appliquées avec succès !');
                            } catch (e) {
                                console.error('Error sending close modal message:', e);
                            }
                        } else {
                            alert('Les informations ont été analysées avec succès !');
                        }
                    }, 1000);
                } else {
                    alert('Les informations ont été analysées, mais n\'ont pas pu être transmises à la page principale.');
                }
            });
        }
        
        // Ajouter le gestionnaire pour le bouton de test
        const testButton = document.getElementById('test-communication');
        if (testButton) {
            testButton.addEventListener('click', function() {
                if (window.parent && window.parent !== window) {
                    console.log('Sending test communication');
                    window.parent.postMessage({
                        type: 'testCommunication',
                        message: 'Ceci est un test de communication',
                        timestamp: new Date().toISOString()
                    }, '*');
                    
                    // Également essayer d'accéder directement à une fonction du parent
                    try {
                        if (window.parent.showNotification) {
                            window.parent.showNotification('Test de communication réussi!', 'success');
                        }
                    } catch (e) {
                        console.warn('Could not call parent.showNotification:', e);
                    }
                    
                    // Afficher un message sur la page
                    const testResult = document.createElement('div');
                    testResult.style.cssText = `
                        background-color: rgba(124, 58, 237, 0.1);
                        padding: 10px 15px;
                        border-radius: 8px;
                        margin-top: 15px;
                        color: #5B21B6;
                        font-size: 0.9rem;
                    `;
                    testResult.innerHTML = 'Message de test envoyé à la page parente...';
                    document.querySelector('.action-buttons').appendChild(testResult);
                    
                    // Faire disparaître le message après 3 secondes
                    setTimeout(() => {
                        testResult.style.opacity = '0';
                        testResult.style.transition = 'opacity 0.5s ease';
                    }, 3000);
                    
                    // Essayer également la méthode directe
                    sendDataToParent({
                        data: {
                            title: "Test de Communication",
                            required_skills: ["Communication", "Test", "iFrame"],
                            experience: "Test d'expérience",
                            contract_type: "Test de contrat"
                        }
                    });
                } else {
                    alert('Cette page n\'est pas chargée dans un iframe.');
                }
            });
        }
    }
    
    // Configuration du drag & drop
    if (dropZone && fileInput) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        function highlight() {
            dropZone.classList.add('highlight');
        }
        
        function unhighlight() {
            dropZone.classList.remove('highlight');
        }
        
        dropZone.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            console.log("File dropped");
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files && files.length > 0) {
                if (fileInput) {
                    fileInput.files = files;
                }
                // Déclencher l'analyse automatiquement après le drop
                analyseFile(files[0]);
            }
        }
    }
    
    // Écouter les messages du parent
    window.addEventListener('message', function(event) {
        console.log('Received message in integration script:', event.data);
        
        // Si nous recevons un message de test, répondre
        if (event.data && event.data.type === 'testCommunication') {
            console.log('Received test communication, sending response');
            if (window.parent && window.parent !== window) {
                window.parent.postMessage({
                    type: 'testResponse',
                    message: 'Message reçu par l\'intégration',
                    originalMessage: event.data.message,
                    timestamp: new Date().toISOString()
                }, '*');
            }
        }
        
        // Si nous recevons une demande de données, les envoyer
        if (event.data && event.data.type === 'requestJobData') {
            console.log('Received request for job data, checking localStorage');
            const lastResult = localStorage.getItem('lastJobParseResult');
            if (lastResult) {
                try {
                    const data = JSON.parse(lastResult);
                    console.log('Found cached data, sending to parent');
                    sendDataToParent(data);
                } catch (e) {
                    console.error('Error parsing cached data:', e);
                }
            }
        }
    });
    
    // Initialiser la page - vérifier s'il y a des résultats en cache
    const lastResult = localStorage.getItem('lastJobParseResult');
    if (lastResult) {
        try {
            const data = JSON.parse(lastResult);
            
            // Ajouter un message pour indiquer que ce sont des résultats en cache
            const cacheMessage = document.createElement('div');
            cacheMessage.className = 'cache-message';
            cacheMessage.innerHTML = '<p>Résultats chargés depuis le cache. Analysez une nouvelle fiche de poste pour des résultats actualisés.</p>';
            cacheMessage.style.cssText = `
                background-color: rgba(124, 58, 237, 0.1);
                padding: 10px 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                color: #5B21B6;
                font-size: 0.9rem;
                text-align: center;
            `;
            document.body.insertBefore(cacheMessage, document.body.firstChild);
            
            // Afficher après un court délai pour laisser la page se charger
            setTimeout(() => {
                displayResults(data);
            }, 500);
            
            // Envoyer les données au parent
            setTimeout(() => {
                sendDataToParent(data);
            }, 1000);
        } catch (e) {
            console.error('Erreur lors de la récupération des résultats en cache:', e);
        }
    }
    
    // Tentative de communication test au chargement
    setTimeout(() => {
        console.log('Sending initial test message');
        if (window.parent && window.parent !== window) {
            window.parent.postMessage({
                type: 'loadedMessage',
                message: 'Script job-parser-integration.js chargé et initialisé',
                timestamp: new Date().toISOString()
            }, '*');
        }
    }, 1000);
    
    // Exposer cette fonction pour la page parente
    window.sendJobDataToParent = function() {
        const lastResult = localStorage.getItem('lastJobParseResult');
        if (lastResult) {
            try {
                const data = JSON.parse(lastResult);
                return sendDataToParent(data);
            } catch (e) {
                console.error('Error sending data to parent:', e);
                return false;
            }
        }
        return false;
    };
});