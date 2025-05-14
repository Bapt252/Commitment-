// Script d'intégration pour le bouton "Analyser avec GPT"
document.addEventListener('DOMContentLoaded', function() {
    // Récupérer les éléments DOM
    const dropZone = document.getElementById('job-drop-zone');
    const fileInput = document.getElementById('job-file-input');
    
    if (!dropZone || !fileInput) {
        console.warn('Les éléments nécessaires pour l\'intégration GPT n\'ont pas été trouvés');
        return;
    }
    
    // Récupérer l'URL de l'API à partir des paramètres d'URL
    const urlParams = new URLSearchParams(window.location.search);
    const apiUrl = urlParams.get('apiUrl') || 'http://localhost:5055';
    const debug = urlParams.has('debug');
    
    // Créer le client GPT Parser
    const gptParser = new GptParserClient({
        apiUrl: apiUrl,
        debug: debug
    });
    
    // Créer le conteneur pour le bouton
    const gptButtonContainer = document.createElement('div');
    gptButtonContainer.className = 'gpt-analyze-btn-container';
    
    // Créer le bouton d'analyse GPT
    const gptButton = document.createElement('button');
    gptButton.id = 'analyze-with-gpt';
    gptButton.type = 'button';
    gptButton.className = 'btn btn-success';
    gptButton.innerHTML = '<i class="fas fa-brain"></i> Analyser avec GPT';
    
    // Créer l'élément de statut
    const statusElement = document.createElement('span');
    statusElement.id = 'gpt-analyze-status';
    
    // Ajouter les éléments au conteneur
    gptButtonContainer.appendChild(gptButton);
    gptButtonContainer.appendChild(statusElement);
    
    // Ajouter le conteneur après le badge de fichier
    const fileBadge = document.getElementById('file-badge');
    if (fileBadge && fileBadge.parentNode) {
        fileBadge.parentNode.insertBefore(gptButtonContainer, fileBadge.nextSibling);
    }
    
    // Ajouter l'écouteur d'événement au bouton
    gptButton.addEventListener('click', async function() {
        // Vérifier si un fichier a été sélectionné
        if (!fileInput.files || fileInput.files.length === 0) {
            if (window.showNotification) {
                window.showNotification('Veuillez d\'abord sélectionner un fichier', 'error');
            } else {
                alert('Veuillez d\'abord sélectionner un fichier');
            }
            return;
        }
        
        const file = fileInput.files[0];
        
        // Vérifier le type de fichier
        const allowedExtensions = ['.pdf', '.doc', '.docx', '.txt'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
        
        if (!allowedExtensions.includes(fileExtension)) {
            if (window.showNotification) {
                window.showNotification(`Format de fichier non supporté. Formats acceptés: ${allowedExtensions.join(', ')}`, 'error');
            } else {
                alert(`Format de fichier non supporté. Formats acceptés: ${allowedExtensions.join(', ')}`);
            }
            return;
        }
        
        try {
            // Mettre à jour le statut
            statusElement.textContent = 'Analyse en cours...';
            statusElement.style.color = '#4CAF50';
            
            // Désactiver le bouton pendant le traitement
            gptButton.disabled = true;
            
            // Afficher le loader si présent
            const loader = document.getElementById('analysis-loader');
            if (loader) {
                loader.style.display = 'flex';
            }
            
            // Analyser le fichier avec GPT
            const result = await gptParser.analyzeFile(file);
            
            if (result.success && result.data) {
                // Remplir le formulaire avec les données extraites
                gptParser.fillFormFields(result.data);
                
                // Mettre à jour le statut
                statusElement.textContent = 'Analyse réussie !';
                
                // Afficher une notification
                if (window.showNotification) {
                    window.showNotification('Fiche de poste analysée avec GPT avec succès !', 'success');
                }
            } else {
                throw new Error('Données invalides reçues du serveur');
            }
            
        } catch (error) {
            console.error('Erreur lors de l\'analyse GPT:', error);
            statusElement.textContent = `Erreur: ${error.message}`;
            statusElement.style.color = 'red';
            
            if (window.showNotification) {
                window.showNotification(`Erreur lors de l'analyse GPT: ${error.message}`, 'error');
            }
        } finally {
            // Réactiver le bouton
            gptButton.disabled = false;
            
            // Masquer le loader si présent
            const loader = document.getElementById('analysis-loader');
            if (loader) {
                loader.style.display = 'none';
            }
        }
    });
});
