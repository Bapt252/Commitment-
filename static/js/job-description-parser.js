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
    
    // Gestion de la sélection de fichier
    fileInput.addEventListener('change', function(e) {
        if (fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            document.getElementById('selected-file-name').textContent = fileName;
            document.getElementById('file-info').style.display = 'block';
        }
    });
    
    // Gestion du glisser-déposer
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
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            const fileName = fileInput.files[0].name;
            document.getElementById('selected-file-name').textContent = fileName;
            document.getElementById('file-info').style.display = 'block';
        }
    });
    
    // Traitement de l'upload de fichier
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (fileInput.files.length === 0) {
            showNotification('Veuillez sélectionner un fichier', 'error');
            return;
        }
        
        const file = fileInput.files[0];
        uploadJobDescription(file);
    });
    
    // Traitement de l'analyse de texte
    analyzeTextBtn.addEventListener('click', function() {
        const text = pasteTextarea.value.trim();
        if (!text) {
            showNotification('Veuillez saisir ou coller une description de poste', 'error');
            return;
        }
        
        // Convertir le texte en objet fichier pour utiliser le même endpoint API
        const blob = new Blob([text], { type: 'text/plain' });
        const file = new File([blob], 'job-description.txt', { type: 'text/plain' });
        
        uploadJobDescription(file);
    });
    
    // Fonction pour uploader et traiter la description de poste
    function uploadJobDescription(file) {
        // Afficher l'indicateur de chargement
        loadingIndicator.style.display = 'flex';
        resultContainer.style.display = 'none';
        
        // Masquer les sections d'upload et de texte
        document.getElementById('upload-section').style.display = 'none';
        document.getElementById('paste-section').style.display = 'none';
        
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
            displayResults(data);
        })
        .catch(error => {
            // Gérer les erreurs
            console.error('Error:', error);
            showNotification('Erreur lors de l\'analyse: ' + error.message, 'error');
            loadingIndicator.style.display = 'none';
            
            // Réafficher les sections d'upload et de texte
            document.getElementById('upload-section').style.display = 'block';
            document.getElementById('paste-section').style.display = 'block';
        });
    }
    
    // Afficher les résultats de l'API
    function displayResults(data) {
        loadingIndicator.style.display = 'none';
        resultContainer.style.display = 'block';
        
        // Nettoyer les résultats précédents
        resultContainer.innerHTML = '';
        
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
                    <span class="result-value">${data.skills ? data.skills.join(', ') : 'Non détectées'}</span>
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
        
        // Gestion du bouton "Utiliser ces résultats"
        document.getElementById('use-results-btn').addEventListener('click', function() {
            // Créer l'objet de données à envoyer à la fenêtre parente
            const jobData = {
                title: data.title || '',
                skills: data.skills || [],
                experience: data.experience || '',
                contract: data.contract_type || '',
                location: data.location || '',
                salary: data.salary || '',
                responsibilities: data.responsibilities || ''
            };
            
            // Envoyer les données à la fenêtre parente
            window.parent.postMessage({
                type: 'jobParsingResult',
                jobData: jobData
            }, '*');
            
            showNotification('Informations transmises au formulaire principal', 'success');
        });
        
        // Gestion du bouton "Réessayer"
        document.getElementById('retry-btn').addEventListener('click', function() {
            resultContainer.style.display = 'none';
            document.getElementById('upload-section').style.display = 'block';
            document.getElementById('paste-section').style.display = 'block';
        });
    }
    
    // Fonction pour afficher les notifications
    function showNotification(message, type = 'success') {
        // Vérifier si la fonction de notification existe dans la fenêtre parente
        if (window.parent && window.parent.showNotification) {
            window.parent.showNotification(message, type);
        } else {
            // Solution de secours si la fonction de notification parente n'est pas disponible
            alert(message);
        }
    }
});
