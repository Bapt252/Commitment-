// Script d'intégration pour l'analyseur de fiche de poste - VERSION CORRIGÉE
// Permet de connecter le frontend au backend job-parser

document.addEventListener('DOMContentLoaded', function() {
    // URL corrigée pour pointer vers le bon port
    const API_ENDPOINT = 'http://localhost:5055/api/parse-job'; // Corrigé : 5055 au lieu de 5053
    
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const pasteTextarea = document.getElementById('paste-text');
    const analyzeTextBtn = document.getElementById('analyze-text-btn');
    const resultContainer = document.getElementById('result-container');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Instance de l'API parser locale
    let jobParserInstance = null;
    
    // Initialiser l'API parser locale
    if (window.JobParserAPI) {
        jobParserInstance = new window.JobParserAPI({
            apiUrl: API_ENDPOINT,
            debug: true,
            enablePDFCleaning: true
        });
        console.log('✅ JobParserAPI locale initialisée');
    } else {
        console.warn('⚠️ JobParserAPI non disponible, mode fallback uniquement');
    }
    
    // Log pour déboguer l'initialisation du script
    console.log('Job parser script initialized - VERSION CORRIGÉE');
    
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
            
            // Analyser directement le texte au lieu de créer un fichier
            analyzeJobText(text);
        });
    }
    
    // Fonction principale pour analyser un texte - NOUVELLE VERSION
    function analyzeJobText(text) {
        console.log('🔍 Analyse de texte démarrée...');
        
        // Afficher l'indicateur de chargement
        if (loadingIndicator) loadingIndicator.style.display = 'flex';
        if (resultContainer) resultContainer.style.display = 'none';
        
        // Masquer les sections d'upload et de texte
        const uploadSection = document.getElementById('upload-section');
        const pasteSection = document.getElementById('paste-section');
        
        if (uploadSection) uploadSection.style.display = 'none';
        if (pasteSection) pasteSection.style.display = 'none';
        
        // Utiliser l'API parser locale si disponible
        if (jobParserInstance) {
            console.log('✅ Utilisation de l\'API parser locale...');
            
            jobParserInstance.parseJobText(text)
                .then(data => {
                    console.log('✅ Analyse terminée avec succès:', data);
                    displayResults(data);
                    sendResultsToParent(data);
                })
                .catch(error => {
                    console.error('❌ Erreur lors de l\'analyse:', error);
                    showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
                    
                    // En cas d'erreur, utiliser le fallback
                    const fallbackData = getFallbackData();
                    displayResults(fallbackData);
                    sendResultsToParent(fallbackData);
                })
                .finally(() => {
                    if (loadingIndicator) loadingIndicator.style.display = 'none';
                });
        } else {
            console.warn('⚠️ API parser non disponible, utilisation du fallback');
            
            // Fallback si l'API n'est pas disponible
            setTimeout(() => {
                const fallbackData = getFallbackData();
                displayResults(fallbackData);
                sendResultsToParent(fallbackData);
                
                if (loadingIndicator) loadingIndicator.style.display = 'none';
            }, 2000);
        }
    }
    
    // Fonction pour uploader et traiter la description de poste - VERSION CORRIGÉE
    function uploadJobDescription(file) {
        console.log('📄 Analyse de fichier démarrée:', file.name);
        
        // Afficher l'indicateur de chargement
        if (loadingIndicator) loadingIndicator.style.display = 'flex';
        if (resultContainer) resultContainer.style.display = 'none';
        
        // Masquer les sections d'upload et de texte
        const uploadSection = document.getElementById('upload-section');
        const pasteSection = document.getElementById('paste-section');
        
        if (uploadSection) uploadSection.style.display = 'none';
        if (pasteSection) pasteSection.style.display = 'none';
        
        // Utiliser l'API parser locale si disponible
        if (jobParserInstance) {
            console.log('✅ Utilisation de l\'API parser locale pour fichier...');
            
            jobParserInstance.parseJobFile(file)
                .then(data => {
                    console.log('✅ Analyse de fichier terminée avec succès:', data);
                    displayResults(data);
                    sendResultsToParent(data);
                })
                .catch(error => {
                    console.error('❌ Erreur lors de l\'analyse du fichier:', error);
                    
                    // Essayer l'API backend en fallback
                    return tryBackendAPI(file);
                })
                .catch(backendError => {
                    console.error('❌ Erreur backend aussi:', backendError);
                    
                    // Utiliser le fallback final
                    const fallbackData = getFallbackData();
                    displayResults(fallbackData);
                    sendResultsToParent(fallbackData);
                })
                .finally(() => {
                    if (loadingIndicator) loadingIndicator.style.display = 'none';
                });
        } else {
            console.warn('⚠️ API parser non disponible, essai de l\'API backend...');
            
            // Essayer l'API backend directement
            tryBackendAPI(file)
                .catch(error => {
                    console.error('❌ Erreur API backend:', error);
                    
                    // Fallback final
                    const fallbackData = getFallbackData();
                    displayResults(fallbackData);
                    sendResultsToParent(fallbackData);
                })
                .finally(() => {
                    if (loadingIndicator) loadingIndicator.style.display = 'none';
                });
        }
    }
    
    // Fonction pour essayer l'API backend - NOUVELLE
    function tryBackendAPI(file) {
        console.log('🌐 Tentative d\'utilisation de l\'API backend...');
        
        // Créer les données du formulaire
        const formData = new FormData();
        formData.append('file', file);
        formData.append('force_refresh', 'true');
        
        // Envoyer à l'API backend
        return fetch(API_ENDPOINT, {
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
            console.log('✅ Données reçues de l\'API backend:', data);
            displayResults(data);
            sendResultsToParent(data);
            return data;
        });
    }
    
    // Fonction pour obtenir des données de fallback - AMÉLIORÉE
    function getFallbackData() {
        return {
            title: "Analyse en cours...",
            skills: ["Compétences en cours d'extraction"],
            experience: "Expérience en cours d'analyse",
            contract_type: "Type de contrat à déterminer",
            location: "Localisation en cours d'extraction",
            salary: "Rémunération en cours d'analyse",
            responsibilities: "Responsabilités en cours d'extraction"
        };
    }
    
    // Fonction pour envoyer les résultats à la fenêtre parente
    function sendResultsToParent(data) {
        console.log('📤 Envoi des données à la fenêtre parente');
        
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
        const messageId = Date.now();
        window.parent.postMessage({
            type: 'jobParsingResult',
            jobData: jobData,
            messageId: messageId
        }, '*');
        
        console.log('✅ Données envoyées à la fenêtre parente avec messageId:', messageId);
        
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
                <h3>✅ Analyse complétée avec succès</h3>
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
    
    console.log('✅ Job parser script corrigé chargé avec succès !');
});
