// Script de débogage pour le bouton Analyser avec GPT
console.log("Script de débogage chargé");

// Fonction pour ajouter manuellement le bouton GPT
function addGptButton() {
    console.log("Tentative d'ajout du bouton GPT");
    
    // Trouver le champ de téléchargement de fichier
    const fileInput = document.querySelector('input[type="file"]');
    console.log("Champ de fichier trouvé:", fileInput);
    
    if (fileInput) {
        // Créer le conteneur pour le bouton
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'gpt-analyze-btn-container';
        buttonContainer.style.marginTop = '10px';
        
        // Créer le bouton
        const analyzeButton = document.createElement('button');
        analyzeButton.type = 'button';
        analyzeButton.id = 'analyze-with-gpt';
        analyzeButton.className = 'btn btn-primary';
        analyzeButton.innerText = 'Analyser avec GPT';
        analyzeButton.style.marginRight = '10px';
        analyzeButton.style.padding = '8px 16px';
        analyzeButton.style.backgroundColor = '#4CAF50';
        analyzeButton.style.color = 'white';
        analyzeButton.style.border = 'none';
        analyzeButton.style.borderRadius = '4px';
        analyzeButton.style.cursor = 'pointer';
        
        // Ajouter le bouton au conteneur
        buttonContainer.appendChild(analyzeButton);
        
        // Créer un élément pour afficher le statut du traitement
        const statusElement = document.createElement('span');
        statusElement.id = 'gpt-analyze-status';
        statusElement.style.marginLeft = '10px';
        statusElement.style.fontStyle = 'italic';
        buttonContainer.appendChild(statusElement);
        
        // Insérer le conteneur après le champ de fichier
        const uploadContainer = document.querySelector('.upload-container');
        if (uploadContainer) {
            uploadContainer.appendChild(buttonContainer);
            console.log("Bouton GPT ajouté avec succès");
        } else {
            console.error("Container d'upload non trouvé");
            // Alternative: insérer après le champ de fichier
            fileInput.parentNode.insertBefore(buttonContainer, fileInput.nextSibling);
        }
        
        // Ajouter l'écouteur d'événement au bouton
        analyzeButton.addEventListener('click', function() {
            console.log("Bouton Analyser avec GPT cliqué");
            handleGptAnalysis();
        });
    } else {
        console.error("Champ de fichier non trouvé");
    }
}

// Fonction pour gérer l'analyse GPT
async function handleGptAnalysis() {
    console.log("Début de l'analyse GPT");
    const fileInput = document.querySelector('input[type="file"]');
    const statusElement = document.getElementById('gpt-analyze-status');
    
    if (statusElement) {
        statusElement.textContent = 'Analyse en cours...';
        statusElement.style.color = 'blue';
    }
    
    // Vérifier si un fichier a été sélectionné
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert('Veuillez d\'abord sélectionner un fichier de fiche de poste.');
        console.error("Aucun fichier sélectionné");
        if (statusElement) {
            statusElement.textContent = 'Erreur: Aucun fichier sélectionné';
            statusElement.style.color = 'red';
        }
        return;
    }
    
    const file = fileInput.files[0];
    console.log("Fichier sélectionné:", file.name, file.type, file.size);
    
    // Préparation des données pour l'envoi
    const formData = new FormData();
    formData.append('file', file);
    
    // Récupérer l'URL de l'API
    const urlParams = new URLSearchParams(window.location.search);
    let apiUrl = urlParams.get('apiUrl') || 'http://localhost:5055';
    apiUrl = apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
    
    console.log("URL de l'API:", apiUrl);
    
    try {
        console.log("Envoi de la requête à", `${apiUrl}/api/parse-job-posting`);
        
        // Appeler l'API de parsing
        const response = await fetch(`${apiUrl}/api/parse-job-posting`, {
            method: 'POST',
            body: formData,
            // Ajout des en-têtes CORS explicites
            mode: 'cors',
            credentials: 'include'
        });
        
        console.log("Réponse reçue:", response.status, response.statusText);
        
        // Vérifier si la requête a réussi
        if (!response.ok) {
            let errorMessage = 'Erreur lors de l\'analyse du document';
            try {
                const errorData = await response.json();
                console.error("Détails de l'erreur:", errorData);
                errorMessage = errorData.detail || errorMessage;
            } catch (e) {
                console.error("Impossible de parser l'erreur JSON:", e);
            }
            throw new Error(errorMessage);
        }
        
        // Récupérer les données
        const result = await response.json();
        console.log("Résultat de l'analyse:", result);
        
        if (result.success && result.data) {
            console.log("Données extraites avec succès:", result.data);
            
            // Afficher les données dans l'interface
            document.getElementById('job-title-value').textContent = result.data.titre || 'Non spécifié';
            document.getElementById('job-contract-value').textContent = result.data.type_contrat || 'Non spécifié';
            document.getElementById('job-location-value').textContent = result.data.localisation || 'Non spécifié';
            document.getElementById('job-experience-value').textContent = result.data.experience || 'Non spécifié';
            document.getElementById('job-education-value').textContent = result.data.formation || 'À déterminer';
            document.getElementById('job-salary-value').textContent = result.data.salaire || 'Non spécifié';
            
            // Afficher les compétences
            if (result.data.competences) {
                if (typeof result.data.competences === 'string') {
                    // Si c'est une chaîne de caractères, la diviser
                    const competences = result.data.competences.split(',').map(s => s.trim());
                    document.getElementById('job-skills-value').innerHTML = competences.map(skill => 
                        `<span class="tag">${skill}</span>`
                    ).join('');
                } else if (Array.isArray(result.data.competences)) {
                    document.getElementById('job-skills-value').innerHTML = result.data.competences.map(skill => 
                        `<span class="tag">${skill}</span>`
                    ).join('');
                }
            }
            
            // Afficher le conteneur des informations extraites
            document.getElementById('job-info-container').style.display = 'block';
            
            if (statusElement) {
                statusElement.textContent = 'Analyse réussie !';
                statusElement.style.color = 'green';
            }
        } else {
            console.error("Données invalides reçues:", result);
            throw new Error('Données invalides reçues du serveur');
        }
    } catch (error) {
        console.error('Erreur:', error.message);
        if (statusElement) {
            statusElement.textContent = `Erreur: ${error.message}`;
            statusElement.style.color = 'red';
        }
        
        // Message d'erreur détaillé
        alert(`Erreur lors de l'analyse: ${error.message}\nVérifiez que le serveur FastAPI est bien démarré sur ${apiUrl}`);
    }
}

// Attendre que la page soit complètement chargée
window.addEventListener('load', function() {
    console.log("Page chargée, ajout du bouton GPT dans 1 seconde...");
    
    // Attendre un court délai pour s'assurer que tous les éléments sont chargés
    setTimeout(function() {
        addGptButton();
        
        // Vérifier si le bouton existe déjà (ajouté par gpt-analyze.js)
        const existingButton = document.getElementById('analyze-with-gpt');
        if (existingButton) {
            console.log("Le bouton GPT existe déjà, pas besoin de l'ajouter manuellement");
        }
    }, 1000);
});
