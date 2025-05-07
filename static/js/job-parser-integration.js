// Script de connexion entre le frontend et le job-parser
document.addEventListener('DOMContentLoaded', function() {
    console.log("Job parser integration script initialized");
    
    // Références aux éléments du DOM
    const dropZone = document.querySelector('.drop-zone') || document.querySelector('.upload-container');
    const fileInput = document.querySelector('input[type="file"]');
    const analyseButton = document.querySelector('.analyse-button') || document.querySelector('button[type="submit"]');
    const textInput = document.querySelector('#text-input');
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
                
                // Dispatcher un événement personnalisé pour signaler que l'analyse est terminée
                document.dispatchEvent(new CustomEvent('analysisComplete', { 
                    detail: result,
                    bubbles: true
                }));
                
            } else {
                console.warn("Client-side parser not available, falling back to simulation mode");
                simulateAnalysis();
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
                
                // Dispatcher un événement personnalisé pour signaler que l'analyse est terminée
                document.dispatchEvent(new CustomEvent('analysisComplete', { 
                    detail: result,
                    bubbles: true
                }));
                
            } else {
                console.warn("Client-side parser not available, falling back to simulation mode");
                simulateAnalysis();
            }
        } catch (error) {
            console.error("Error during text analysis:", error);
            loadingIndicator.style.display = 'none';
            alert('Une erreur est survenue lors de l\'analyse du texte. Veuillez réessayer.');
        }
    }
    
    // Fonction pour simuler une analyse (mode démo)
    function simulateAnalysis() {
        console.log("Running simulated analysis");
        
        setTimeout(function() {
            // Masquer l'indicateur de chargement
            loadingIndicator.style.display = 'none';
            
            // Données simulées basées sur le contenu de la zone de texte ou un exemple par défaut
            let simulatedTitle = "Développeur Full Stack";
            let simulatedSkills = ["JavaScript", "React", "Node.js", "MongoDB", "Git"];
            let simulatedExperience = "3-5 ans d'expérience";
            let simulatedContract = "CDI";
            
            // Si un texte est disponible, essayer d'en extraire des informations basiques
            if (textInput && textInput.value.trim()) {
                const text = textInput.value.toLowerCase();
                
                // Titre - première ligne
                const firstLine = textInput.value.split('\n')[0].trim();
                if (firstLine && firstLine.length < 100) {
                    simulatedTitle = firstLine;
                }
                
                // Contrat
                if (text.includes('cdi')) simulatedContract = "CDI";
                else if (text.includes('cdd')) simulatedContract = "CDD";
                else if (text.includes('stage')) simulatedContract = "Stage";
                else if (text.includes('freelance')) simulatedContract = "Freelance";
                
                // Expérience
                const expMatch = text.match(/(\d+)[-\s]+(\d+)?\s*ans?/);
                if (expMatch) {
                    if (expMatch[2]) {
                        simulatedExperience = `${expMatch[1]}-${expMatch[2]} ans d'expérience`;
                    } else {
                        simulatedExperience = `${expMatch[1]} ans d'expérience`;
                    }
                }
                
                // Compétences - recherche simplifiée
                const skillKeywords = {
                    "javascript": "JavaScript",
                    "react": "React",
                    "angular": "Angular",
                    "vue": "Vue.js",
                    "node": "Node.js",
                    "python": "Python",
                    "java": "Java",
                    "php": "PHP",
                    "html": "HTML5",
                    "css": "CSS3",
                    "sql": "SQL",
                    "mongodb": "MongoDB",
                    "git": "Git"
                };
                
                simulatedSkills = [];
                for (const [keyword, skill] of Object.entries(skillKeywords)) {
                    if (text.includes(keyword)) {
                        simulatedSkills.push(skill);
                    }
                }
                
                // Si aucune compétence trouvée, utiliser les valeurs par défaut
                if (simulatedSkills.length === 0) {
                    simulatedSkills = ["JavaScript", "HTML", "CSS", "Git"];
                }
            }
            
            // Créer l'objet de résultat simulé
            const simulatedData = {
                data: {
                    title: simulatedTitle,
                    company: "Entreprise",
                    location: "Paris",
                    contract_type: simulatedContract,
                    required_skills: simulatedSkills,
                    preferred_skills: [],
                    experience: simulatedExperience,
                    responsibilities: [
                        "Développer des applications web",
                        "Collaborer avec l'équipe",
                        "Maintenir les services existants"
                    ]
                }
            };
            
            // Afficher les résultats
            displayResults(simulatedData);
            
            // Sauvegarder dans le localStorage pour la persistance
            localStorage.setItem('lastJobParseResult', JSON.stringify(simulatedData));
            
            // Dispatcher un événement personnalisé pour signaler que l'analyse est terminée
            document.dispatchEvent(new CustomEvent('analysisComplete', { 
                detail: simulatedData,
                bubbles: true
            }));
            
        }, 1500); // Simulation réaliste du temps d'analyse
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
        
        if (parsedData.experience) {
            resultHTML += `<div class="result-item"><strong>Expérience requise:</strong> ${parsedData.experience}</div>`;
        }
        
        // Ajouter des boutons d'action
        resultHTML += `
            <div class="action-buttons">
                <button id="apply-results" class="btn btn-primary">
                    <i class="fas fa-check"></i> Appliquer ces informations
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
                console.log("Apply button clicked, dispatching event");
                
                // Dispatcher un événement personnalisé avec les données à appliquer
                document.dispatchEvent(new CustomEvent('applyJobData', { 
                    detail: { data: parsedData },
                    bubbles: true
                }));
                
                // Informer l'utilisateur
                alert('Les informations ont été appliquées avec succès !');
                
                // Fermer la fenêtre modale parente si dans un iframe
                if (window.parent && window.parent !== window) {
                    try {
                        // Essayer de fermer le modal via postMessage
                        window.parent.postMessage({
                            type: 'closeModal',
                            reason: 'dataApplied'
                        }, '*');
                    } catch (e) {
                        console.error('Error sending close modal message:', e);
                    }
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
    
    // Gérer l'événement "applyJobData"
    document.addEventListener('applyJobData', function(e) {
        if (e.detail && e.detail.data) {
            console.log('Apply job data event received:', e.detail.data);
            
            // Structurer les données pour la communication
            const jobData = {
                title: e.detail.data.title || '',
                skills: e.detail.data.required_skills || [],
                experience: e.detail.data.experience || '',
                contract: e.detail.data.contract_type || ''
            };
            
            // Envoyer à la page parente si dans un iframe
            if (window.parent && window.parent !== window) {
                console.log('Sending job data to parent window');
                
                // Utiliser sendToParent si disponible
                if (typeof window.sendToParent === 'function') {
                    window.sendToParent({
                        type: 'jobParsingResult',
                        jobData: jobData,
                        messageId: new Date().getTime()
                    });
                } else {
                    // Sinon utiliser directement postMessage
                    window.parent.postMessage({
                        type: 'jobParsingResult',
                        jobData: jobData,
                        messageId: new Date().getTime()
                    }, '*');
                }
            }
        }
    });
    
    // Écouter les messages du parent
    window.addEventListener('message', function(event) {
        console.log('Received message in integration script:', event.data);
    });
    
    // Notifier que le script est prêt
    console.log("Job parser integration ready");
});
