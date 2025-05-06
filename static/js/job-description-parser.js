// Script d'intégration pour l'analyseur de fiche de poste
// Permet de connecter le frontend au backend job-parser

document.addEventListener('DOMContentLoaded', function() {
    const API_ENDPOINT = 'http://localhost:5053/api/parse-job'; // URL du service job-parser
    
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const pasteTextarea = document.getElementById('paste-text');
    const analyzeTextBtn = document.getElementById('analyze-text-btn');
    const resultContainer = document.getElementById('result-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Log pour déboguer l'initialisation du script
    console.log('Job parser script initialized');
    
    // Gestion de la sélection de fichier
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            console.log('File selected:', fileInput.files[0]?.name);
            if (fileInput.files.length > 0) {
                const fileName = fileInput.files[0].name;
                document.getElementById('selected-file-name').textContent = fileName;
                document.getElementById('file-info').style.display = 'block';
            }
        });
    }
    
    // Gestion du glisser-déposer
    if (dropZone) {
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', function() {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            console.log('File dropped');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                const fileName = fileInput.files[0].name;
                document.getElementById('selected-file-name').textContent = fileName;
                document.getElementById('file-info').style.display = 'block';
            }
        });
    }
    
    // Traitement de l'upload de fichier
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submitted');
            
            if (fileInput.files.length === 0) {
                showNotification('Veuillez sélectionner un fichier', 'error');
                return;
            }
            
            const file = fileInput.files[0];
            uploadJobDescription(file);
        });
    }
    
    // Traitement de l'analyse de texte
    if (analyzeTextBtn) {
        analyzeTextBtn.addEventListener('click', function() {
            const text = pasteTextarea.value.trim();
            console.log('Text analysis requested, length:', text.length);
            
            if (!text) {
                showNotification('Veuillez saisir ou coller une description de poste', 'error');
                return;
            }
            
            // Convertir le texte en objet fichier pour utiliser le même endpoint API
            const blob = new Blob([text], { type: 'text/plain' });
            const file = new File([blob], 'job-description.txt', { type: 'text/plain' });
            
            uploadJobDescription(file);
        });
    }
    
    // Fonction pour simuler une réponse API en attendant que le backend soit prêt
    function simulateApiResponse() {
        console.log('Simulating API response due to backend unavailability');
        return {
            title: "Comptable Auxiliaire",
            skills: ["Excel", "SAP", "Comptabilité générale", "Analyse financière", "Saisie comptable"],
            experience: "2-3 ans d'expérience en comptabilité",
            contract_type: "CDI",
            location: "Paris",
            salary: "30-35K€ selon expérience",
            responsibilities: "Participation à la clôture mensuelle, saisie des factures, rapprochements bancaires, suivi des immobilisations"
        };
    }
    
    // Fonction pour uploader et traiter la description de poste
    function uploadJobDescription(file) {
        // Afficher l'indicateur de chargement
        if (loadingIndicator) loadingIndicator.style.display = 'flex';
        if (resultContainer) resultContainer.style.display = 'none';
        
        // Masquer les sections d'upload et de texte
        const uploadSection = document.getElementById('upload-section');
        const pasteSection = document.getElementById('paste-section');
        
        if (uploadSection) uploadSection.style.display = 'none';
        if (pasteSection) pasteSection.style.display = 'none';
        
        console.log('Processing file:', file.name);
        
        // Utiliser un délai simulé pour montrer le chargement (3 secondes)
        setTimeout(() => {
            // Simuler une réponse API pour le test
            const data = simulateApiResponse();
            console.log('Received data from API (simulated):', data);
            displayResults(data);
            
            // Essayer également d'envoyer à la fenêtre parente
            sendResultsToParent(data);
        }, 3000);
        
        // Code commenté pour l'appel API réel
        /*
        // Créer les données du formulaire
        const formData = new FormData();
        formData.append('file', file);
        formData.append('force_refresh', 'true');
        
        // Envoyer à l'API
        fetch(API_ENDPOINT, {
            method: 'POST',
            body: formData,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de l\'analyse: ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            // Traiter la réponse réussie
            console.log('Received data from API:', data);
            displayResults(data);
            
            // Envoyer les résultats à la fenêtre parente
            sendResultsToParent(data);
        })
        .catch(error => {
            // Gérer les erreurs
            console.error('Error:', error);
            showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
            
            if (loadingIndicator) loadingIndicator.style.display = 'none';
            
            // Réafficher les sections d'upload et de texte
            if (uploadSection) uploadSection.style.display = 'block';
            if (pasteSection) pasteSection.style.display = 'block';
            
            // En cas d'erreur, utiliser des données simulées pour le test
            const simulatedData = simulateApiResponse();
            displayResults(simulatedData);
            sendResultsToParent(simulatedData);
        });
        */
    }
    
    // Fonction pour envoyer les résultats à la fenêtre parente
    function sendResultsToParent(data) {
        console.log('Attempting to send data to parent window');
        
        // Créer l'objet de données à envoyer
        const jobData = {
            title: data.title || '',
            skills: data.skills || [],
            experience: data.experience || '',
            contract: data.contract_type || '',
            location: data.location || '',
            salary: data.salary || '',
            responsibilities: data.responsibilities || ''
        };
        
        // Envoyer les données à la fenêtre parente avec un ID pour le débogage
        window.parent.postMessage({
            type: 'jobParsingResult',
            jobData: jobData,
            messageId: Date.now() // Ajouter un ID unique pour le débogage
        }, '*');
        
        console.log('Data sent to parent window with messageId:', Date.now());
        
        // Afficher un message si nous sommes en mode débogage
        showNotification('Les informations ont été envoyées au formulaire principal', 'success');
    }
    
    // Afficher les résultats de l'API
    function displayResults(data) {
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (resultContainer) resultContainer.style.display = 'block';
        
        if (!resultContainer) {
            console.error('Result container not found in DOM');
            return;
        }
        
        // Nettoyer les résultats précédents
        resultContainer.innerHTML = '';
        
        // Formater les compétences avec des balises individuelles
        let skillsHtml = 'Non détectées';
        if (data.skills && data.skills.length > 0) {
            skillsHtml = data.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join(' ');
        }
        
        // Créer le HTML des résultats
        const resultHTML = `
            <div class="result-header">
                <h3>Analyse complétée avec succès</h3>
            </div>
            <div class="result-content">
                <div class="result-item">
                    <span class="result-label">Intitulé du poste:</span>
                    <span class="result-value">${data.title || 'Non détecté'}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Compétences requises:</span>
                    <span class="result-value">${skillsHtml}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Expérience:</span>
                    <span class="result-value">${data.experience || 'Non détectée'}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Type de contrat:</span>
                    <span class="result-value">${data.contract_type || 'Non détecté'}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Lieu:</span>
                    <span class="result-value">${data.location || 'Non détecté'}</span>
                </div>
                <div class="result-item">
                    <span class="result-label">Salaire:</span>
                    <span class="result-value">${data.salary || 'Non détecté'}</span>
                </div>
                <div class="result-item result-full">
                    <span class="result-label">Responsabilités:</span>
                    <span class="result-value">${data.responsibilities || 'Non détectées'}</span>
                </div>
            </div>
            <div class="result-actions">
                <button id="use-results-btn" class="btn btn-primary">Utiliser ces informations</button>
                <button id="retry-btn" class="btn btn-secondary">Réessayer</button>
            </div>
        `;
        
        resultContainer.innerHTML = resultHTML;
        
        // Ajouter une classe de style aux skill tags
        document.querySelectorAll('.skill-tag').forEach(tag => {
            tag.style.display = 'inline-block';
            tag.style.margin = '2px';
            tag.style.padding = '4px 10px';
            tag.style.background = 'rgba(124, 58, 237, 0.1)';
            tag.style.color = '#5B21B6';
            tag.style.borderRadius = '20px';
            tag.style.fontSize = '0.85rem';
        });
        
        // Gestion du bouton "Utiliser ces résultats"
        const useResultsBtn = document.getElementById('use-results-btn');
        if (useResultsBtn) {
            useResultsBtn.addEventListener('click', function() {
                // Envoyer à nouveau les données à la fenêtre parente
                sendResultsToParent(data);
            });
        }
        
        // Gestion du bouton "Réessayer"
        const retryBtn = document.getElementById('retry-btn');
        if (retryBtn) {
            retryBtn.addEventListener('click', function() {
                resultContainer.style.display = 'none';
                const uploadSection = document.getElementById('upload-section');
                const pasteSection = document.getElementById('paste-section');
                
                if (uploadSection) uploadSection.style.display = 'block';
                if (pasteSection) pasteSection.style.display = 'block';
            });
        }
    }
    
    // Fonction pour afficher les notifications
    function showNotification(message, type = 'success') {
        console.log('Notification:', message, type);
        
        // Vérifier si la fonction de notification existe dans la fenêtre parente
        if (window.parent && window.parent.showNotification) {
            window.parent.showNotification(message, type);
        } else {
            // Créer notre propre notification
            const notifContainer = document.createElement('div');
            notifContainer.style.position = 'fixed';
            notifContainer.style.bottom = '20px';
            notifContainer.style.right = '20px';
            notifContainer.style.padding = '15px 20px';
            notifContainer.style.backgroundColor = type === 'success' ? 'rgba(16, 185, 129, 0.9)' : 'rgba(239, 68, 68, 0.9)';
            notifContainer.style.color = 'white';
            notifContainer.style.borderRadius = '8px';
            notifContainer.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
            notifContainer.style.zIndex = '9999';
            notifContainer.textContent = message;
            
            document.body.appendChild(notifContainer);
            
            setTimeout(() => {
                notifContainer.style.opacity = '0';
                notifContainer.style.transition = 'opacity 0.5s ease';
                
                setTimeout(() => {
                    document.body.removeChild(notifContainer);
                }, 500);
            }, 4000);
        }
    }
    
    // Support des onglets pour l'interface
    const tabs = document.querySelectorAll('.tab');
    if (tabs.length > 0) {
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');
                
                // Supprimer la classe active de tous les onglets et contenus
                tabs.forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                // Ajouter la classe active à l'onglet et au contenu sélectionnés
                this.classList.add('active');
                const tabContent = document.getElementById(tabId + '-section');
                if (tabContent) tabContent.classList.add('active');
            });
        });
    }
    
    // Trigger immédiat pour simuler l'analyse d'un fichier au chargement (pour débogage)
    // setTimeout(() => {
    //    if (fileInput && fileInput.files.length > 0) {
    //        uploadJobDescription(fileInput.files[0]);
    //    }
    // }, 1000);
});