// Script pour l'analyse de fiches de poste avec GPT
document.addEventListener('DOMContentLoaded', function() {
    // Trouver le champ de téléchargement de fichier
    const fileInput = document.querySelector('input[type="file"]');
    
    if (fileInput) {
        // Créer le conteneur pour le bouton (pour le style)
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
        
        // Ajouter le bouton au conteneur
        buttonContainer.appendChild(analyzeButton);
        
        // Créer un élément pour afficher le statut du traitement
        const statusElement = document.createElement('span');
        statusElement.id = 'gpt-analyze-status';
        statusElement.style.marginLeft = '10px';
        buttonContainer.appendChild(statusElement);
        
        // Insérer le conteneur après le champ de fichier
        fileInput.parentNode.insertBefore(buttonContainer, fileInput.nextSibling);
        
        // Ajouter l'écouteur d'événement au bouton
        analyzeButton.addEventListener('click', handleGptAnalysis);
    }
});

// Fonction pour gérer l'analyse GPT lorsque le bouton est cliqué
async function handleGptAnalysis() {
    const fileInput = document.querySelector('input[type="file"]');
    const statusElement = document.getElementById('gpt-analyze-status');
    
    // Vérifier si un fichier a été sélectionné
    if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        alert('Veuillez d\'abord sélectionner un fichier de fiche de poste.');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Vérifier le type de fichier
    const allowedExtensions = ['.pdf', '.docx', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
        alert(`Format de fichier non supporté. Formats acceptés: ${allowedExtensions.join(', ')}`);
        return;
    }
    
    // Préparation des données pour l'envoi
    const formData = new FormData();
    formData.append('file', file);
    
    // Récupérer l'URL de l'API à partir des paramètres d'URL ou utiliser la valeur par défaut
    const urlParams = new URLSearchParams(window.location.search);
    let apiUrl = urlParams.get('apiUrl') || 'http://localhost:5055';
    
    // S'assurer que l'URL ne se termine pas par un slash
    apiUrl = apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
    
    try {
        // Mettre à jour le statut
        statusElement.textContent = 'Analyse en cours...';
        statusElement.style.color = 'blue';
        
        // Désactiver le bouton pendant le traitement
        const analyzeButton = document.getElementById('analyze-with-gpt');
        analyzeButton.disabled = true;
        
        // Appeler l'API de parsing
        const response = await fetch(`${apiUrl}/api/parse-job-posting`, {
            method: 'POST',
            body: formData,
        });
        
        // Vérifier si la requête a réussi
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erreur lors de l\'analyse du document');
        }
        
        // Récupérer les données
        const result = await response.json();
        
        if (result.success && result.data) {
            // Remplir le formulaire avec les données extraites
            fillFormWithJobData(result.data);
            
            // Mettre à jour le statut
            statusElement.textContent = 'Analyse réussie !';
            statusElement.style.color = 'green';
        } else {
            throw new Error('Données invalides reçues du serveur');
        }
    } catch (error) {
        console.error('Erreur:', error);
        statusElement.textContent = `Erreur: ${error.message}`;
        statusElement.style.color = 'red';
    } finally {
        // Réactiver le bouton après le traitement
        const analyzeButton = document.getElementById('analyze-with-gpt');
        if (analyzeButton) {
            analyzeButton.disabled = false;
        }
    }
}

// Fonction pour remplir le formulaire avec les données extraites
function fillFormWithJobData(jobData) {
    // Mapper les champs du résultat aux champs du formulaire
    const fieldMapping = {
        'titre': 'input[name="titre"], #titre',
        'entreprise': 'input[name="entreprise"], #entreprise',
        'localisation': 'input[name="localisation"], #localisation',
        'type_contrat': 'input[name="type_contrat"], #type_contrat, select[name="type_contrat"]',
        'competences': 'textarea[name="competences"], #competences',
        'experience': 'input[name="experience"], #experience, textarea[name="experience"]',
        'formation': 'input[name="formation"], #formation, textarea[name="formation"]',
        'salaire': 'input[name="salaire"], #salaire'
    };
    
    // Pour chaque champ dans le mapping
    for (const [dataKey, selector] of Object.entries(fieldMapping)) {
        if (jobData[dataKey]) {
            // Chercher le champ dans le formulaire
            const field = document.querySelector(selector);
            
            if (field) {
                // Remplir le champ avec la valeur extraite
                if (field.tagName === 'SELECT') {
                    // Pour les select, trouver l'option qui correspond le mieux
                    setSelectOption(field, jobData[dataKey]);
                } else if (field.type === 'checkbox' || field.type === 'radio') {
                    field.checked = true;
                } else {
                    field.value = jobData[dataKey];
                    
                    // Déclencher un événement de changement pour activer d'éventuels écouteurs
                    const event = new Event('change', { bubbles: true });
                    field.dispatchEvent(event);
                }
            }
        }
    }
    
    // Afficher un message de succès
    console.log('Formulaire rempli avec les données extraites !');
}

// Fonction pour définir la valeur d'un élément select
function setSelectOption(selectElement, value) {
    // Normalisation de la valeur pour la comparaison
    const normalizedValue = value.toLowerCase().trim();
    
    // Parcourir toutes les options
    for (const option of selectElement.options) {
        const optionText = option.text.toLowerCase().trim();
        const optionValue = option.value.toLowerCase().trim();
        
        // Vérifier si l'option correspond à la valeur
        if (optionText.includes(normalizedValue) || normalizedValue.includes(optionText) || 
            optionValue.includes(normalizedValue) || normalizedValue.includes(optionValue)) {
            option.selected = true;
            
            // Déclencher un événement de changement
            const event = new Event('change', { bubbles: true });
            selectElement.dispatchEvent(event);
            
            return;
        }
    }
    
    // Si aucune correspondance n'est trouvée, sélectionner la première option
    if (selectElement.options.length > 0) {
        selectElement.options[0].selected = true;
    }
}
