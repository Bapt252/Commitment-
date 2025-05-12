/**
 * Script pour l'analyse de fiches de poste avec GPT
 * Version améliorée avec meilleure intégration dans l'interface
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('[GPT-Analyze] Initializing...');
    
    // Ajouter le bouton d'analyse GPT dans la section appropriée
    const jobInfoContainer = document.getElementById('job-info-container');
    const fileDropZone = document.getElementById('job-drop-zone');
    
    if (jobInfoContainer && fileDropZone) {
        // Créer le conteneur pour le bouton GPT
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'gpt-analyze-btn-container';
        buttonContainer.style.marginTop = '20px';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.justifyContent = 'center';
        
        // Créer le bouton
        const analyzeButton = document.createElement('button');
        analyzeButton.type = 'button';
        analyzeButton.id = 'analyze-with-gpt';
        analyzeButton.className = 'btn btn-primary';
        analyzeButton.innerHTML = '<i class="fas fa-robot"></i> Analyser avec GPT';
        analyzeButton.style.marginRight = '10px';
        
        // Ajouter le bouton au conteneur
        buttonContainer.appendChild(analyzeButton);
        
        // Créer un élément pour afficher le statut du traitement
        const statusElement = document.createElement('span');
        statusElement.id = 'gpt-analyze-status';
        statusElement.style.marginLeft = '10px';
        statusElement.style.alignSelf = 'center';
        buttonContainer.appendChild(statusElement);
        
        // Insérer le conteneur avant les boutons d'action dans la section de résultats
        const jobActions = jobInfoContainer.querySelector('.job-actions');
        if (jobActions) {
            jobInfoContainer.insertBefore(buttonContainer, jobActions);
        } else {
            // Fallback: ajouter à la fin du conteneur
            jobInfoContainer.appendChild(buttonContainer);
        }
        
        // Également ajouter le bouton après la zone de dépôt de fichier comme alternative
        const fileBadge = document.getElementById('file-badge');
        if (fileBadge) {
            const altButtonContainer = buttonContainer.cloneNode(true);
            const altAnalyzeButton = altButtonContainer.querySelector('#analyze-with-gpt');
            if (altAnalyzeButton) {
                altAnalyzeButton.id = 'analyze-with-gpt-alt';
            }
            fileDropZone.appendChild(altButtonContainer);
        }
        
        // Ajouter l'écouteur d'événement aux boutons
        document.querySelectorAll('#analyze-with-gpt, #analyze-with-gpt-alt').forEach(button => {
            button.addEventListener('click', handleGptAnalysis);
        });
        
        console.log('[GPT-Analyze] Buttons added successfully');
    } else {
        console.warn('[GPT-Analyze] Required containers not found');
    }
});

// Fonction pour gérer l'analyse GPT lorsque le bouton est cliqué
async function handleGptAnalysis() {
    console.log('[GPT-Analyze] Button clicked');
    
    // Trouver le fichier soit depuis l'input de fichier, soit depuis le texte
    const fileInput = document.getElementById('job-file-input');
    const textArea = document.getElementById('job-description-text');
    const statusElements = document.querySelectorAll('#gpt-analyze-status');
    
    // Mettre à jour tous les éléments de statut
    const updateStatus = (message, color) => {
        statusElements.forEach(element => {
            if (element) {
                element.textContent = message;
                element.style.color = color;
            }
        });
    };
    
    // Désactiver tous les boutons d'analyse
    const analyzeButtons = document.querySelectorAll('#analyze-with-gpt, #analyze-with-gpt-alt');
    analyzeButtons.forEach(button => {
        if (button) button.disabled = true;
    });
    
    try {
        // Récupérer l'URL de l'API à partir des paramètres d'URL ou utiliser la valeur par défaut
        const urlParams = new URLSearchParams(window.location.search);
        let apiUrl = urlParams.get('apiUrl') || 'http://localhost:5055';
        
        // S'assurer que l'URL ne se termine pas par un slash
        apiUrl = apiUrl.endsWith('/') ? apiUrl.slice(0, -1) : apiUrl;
        
        // Cas 1: Fichier sélectionné
        if (fileInput && fileInput.files && fileInput.files.length > 0) {
            const file = fileInput.files[0];
            
            // Vérifier le type de fichier
            const allowedExtensions = ['.pdf', '.docx', '.doc', '.txt'];
            const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
            
            if (!allowedExtensions.includes(fileExtension)) {
                throw new Error(`Format de fichier non supporté. Formats acceptés: ${allowedExtensions.join(', ')}`);
            }
            
            updateStatus('Analyse du fichier en cours...', 'blue');
            
            // Préparer les données pour l'envoi
            const formData = new FormData();
            formData.append('file', file);
            
            // Appeler l'API de parsing
            const response = await fetch(`${apiUrl}/api/parse-job-posting`, {
                method: 'POST',
                body: formData,
            });
            
            handleApiResponse(response, updateStatus);
        }
        // Cas 2: Texte saisi
        else if (textArea && textArea.value.trim()) {
            updateStatus('Analyse du texte en cours...', 'blue');
            
            // Préparer les données pour l'envoi
            const formData = new FormData();
            formData.append('text', textArea.value.trim());
            
            // Appeler l'API de parsing
            const response = await fetch(`${apiUrl}/api/parse-job-posting`, {
                method: 'POST',
                body: formData,
            });
            
            handleApiResponse(response, updateStatus);
        }
        // Aucune donnée à analyser
        else {
            throw new Error('Veuillez d\'abord sélectionner un fichier ou saisir le texte de la fiche de poste.');
        }
    } catch (error) {
        console.error('[GPT-Analyze] Error:', error);
        updateStatus(`Erreur: ${error.message}`, 'red');
        
        // Afficher une notification d'erreur si la fonction existe
        if (typeof window.showNotification === 'function') {
            window.showNotification(error.message, 'error');
        } else {
            alert(`Erreur: ${error.message}`);
        }
    } finally {
        // Réactiver les boutons après le traitement
        analyzeButtons.forEach(button => {
            if (button) button.disabled = false;
        });
    }
}

// Fonction pour gérer la réponse de l'API
async function handleApiResponse(response, updateStatus) {
    // Vérifier si la requête a réussi
    if (!response.ok) {
        let errorMessage = 'Erreur lors de l\'analyse du document';
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
        } catch (e) {
            // Ignorer les erreurs de parsing JSON
        }
        throw new Error(errorMessage);
    }
    
    // Récupérer les données
    const result = await response.json();
    
    if (result.success && result.data) {
        // Remplir le formulaire avec les données extraites
        fillFormWithJobData(result.data);
        
        // Mettre à jour le statut
        updateStatus('Analyse réussie !', 'green');
        
        // Afficher une notification de succès si la fonction existe
        if (typeof window.showNotification === 'function') {
            window.showNotification('Fiche de poste analysée avec succès par GPT !', 'success');
        }
    } else {
        throw new Error(result.error || 'Données invalides reçues du serveur');
    }
}

// Fonction pour remplir le formulaire avec les données extraites
function fillFormWithJobData(jobData) {
    console.log('[GPT-Analyze] Filling form with data:', jobData);
    
    // Remplir les champs d'informations extraites dans l'UI
    const fieldMapping = {
        'title': { 
            selector: '#job-title-value', 
            fallbackSelectors: ['#titre', 'input[name="titre"]']
        },
        'titre': { 
            selector: '#job-title-value', 
            fallbackSelectors: ['#titre', 'input[name="titre"]']
        },
        'company': { 
            selector: '#company-name', 
            fallbackSelectors: ['input[name="company-name"]', '#entreprise', 'input[name="entreprise"]']
        },
        'entreprise': { 
            selector: '#company-name', 
            fallbackSelectors: ['input[name="company-name"]', '#entreprise', 'input[name="entreprise"]']
        },
        'location': { 
            selector: '#job-location-value', 
            fallbackSelectors: ['#localisation', 'input[name="localisation"]']
        },
        'localisation': { 
            selector: '#job-location-value', 
            fallbackSelectors: ['#localisation', 'input[name="localisation"]']
        },
        'contract_type': { 
            selector: '#job-contract-value', 
            fallbackSelectors: ['#contract-type', '#type_contrat', 'select[name="contract-type"]']
        },
        'type_contrat': { 
            selector: '#job-contract-value', 
            fallbackSelectors: ['#contract-type', '#type_contrat', 'select[name="contract-type"]']
        },
        'experience': { 
            selector: '#job-experience-value', 
            fallbackSelectors: ['#experience', 'input[name="experience"]', 'select[name="experience-required"]']
        },
        'skills': { 
            selector: '#job-skills-value', 
            type: 'skills',
            fallbackSelectors: ['#competences', 'textarea[name="competences"]']
        },
        'competences': { 
            selector: '#job-skills-value', 
            type: 'skills',
            fallbackSelectors: ['#competences', 'textarea[name="competences"]']
        },
        'responsibilities': { 
            selector: '#job-responsibilities-value', 
            type: 'list',
            fallbackSelectors: ['#responsibilities', 'textarea[name="responsibilities"]']
        },
        'missions': { 
            selector: '#job-responsibilities-value', 
            type: 'list',
            fallbackSelectors: ['#responsibilities', 'textarea[name="responsibilities"]']
        },
        'benefits': { 
            selector: '#job-benefits-value', 
            type: 'list',
            fallbackSelectors: ['#benefits', 'textarea[name="benefits"]']
        },
        'avantages': { 
            selector: '#job-benefits-value', 
            type: 'list',
            fallbackSelectors: ['#benefits', 'textarea[name="benefits"]']
        },
        'salary': { 
            selector: '#job-salary-value', 
            fallbackSelectors: ['#salary', 'input[name="salary"]', '#salaire', 'input[name="salaire"]']
        },
        'salaire': { 
            selector: '#job-salary-value', 
            fallbackSelectors: ['#salary', 'input[name="salary"]', '#salaire', 'input[name="salaire"]']
        },
        'education': { 
            selector: '#job-education-value', 
            fallbackSelectors: ['#education', 'input[name="education"]', '#formation', 'input[name="formation"]']
        },
        'formation': { 
            selector: '#job-education-value', 
            fallbackSelectors: ['#education', 'input[name="education"]', '#formation', 'input[name="formation"]']
        }
    };
    
    // Pour chaque champ dans le mapping
    for (const [dataKey, fieldInfo] of Object.entries(fieldMapping)) {
        if (jobData[dataKey]) {
            const value = jobData[dataKey];
            
            // Chercher le champ principal dans le document
            const element = document.querySelector(fieldInfo.selector);
            
            if (element) {
                fillElement(element, value, fieldInfo.type);
                console.log(`[GPT-Analyze] Filled ${dataKey} into ${fieldInfo.selector}`);
            } else {
                // Essayer les sélecteurs de fallback
                for (const fallbackSelector of fieldInfo.fallbackSelectors || []) {
                    const fallbackElement = document.querySelector(fallbackSelector);
                    if (fallbackElement) {
                        fillElement(fallbackElement, value, fieldInfo.type);
                        console.log(`[GPT-Analyze] Filled ${dataKey} into fallback ${fallbackSelector}`);
                        break;
                    }
                }
            }
        }
    }
    
    // Rendre le conteneur de résultats visible
    const jobInfoContainer = document.getElementById('job-info-container');
    if (jobInfoContainer) {
        jobInfoContainer.style.display = 'block';
    }
    
    // Si nous avons la fonction d'ajout de tags pour les avantages, l'utiliser
    if (typeof window.addBenefitTag === 'function' && Array.isArray(jobData.benefits)) {
        jobData.benefits.forEach(benefit => {
            window.addBenefitTag(benefit);
        });
    } else if (typeof window.addBenefitTag === 'function' && Array.isArray(jobData.avantages)) {
        jobData.avantages.forEach(avantage => {
            window.addBenefitTag(avantage);
        });
    }
}

// Fonction pour remplir un élément selon son type
function fillElement(element, value, type) {
    // Vérifier si la valeur est définie
    if (!value || (Array.isArray(value) && value.length === 0)) {
        return;
    }
    
    // Traiter selon le type d'élément
    if (element.tagName === 'SELECT') {
        setSelectOption(element, value);
    } else if (element.tagName === 'INPUT') {
        if (element.type === 'checkbox' || element.type === 'radio') {
            element.checked = true;
        } else {
            element.value = Array.isArray(value) ? value.join(', ') : value;
        }
    } else if (element.tagName === 'TEXTAREA') {
        element.value = Array.isArray(value) ? value.join('\n') : value;
    } else {
        // Pour les éléments div, span, etc.
        if (type === 'skills' && Array.isArray(value)) {
            element.innerHTML = value.map(skill => 
                `<span class="tag">${skill}</span>`
            ).join('');
        } else if (type === 'list' && Array.isArray(value)) {
            element.innerHTML = '<ul>' + 
                value.map(item => `<li>${item}</li>`).join('') + 
                '</ul>';
        } else {
            element.textContent = Array.isArray(value) ? value.join(', ') : value;
        }
    }
    
    // Déclencher un événement de changement pour activer d'éventuels écouteurs
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(element.tagName)) {
        const event = new Event('change', { bubbles: true });
        element.dispatchEvent(event);
    }
}

// Fonction pour définir la valeur d'un élément select
function setSelectOption(selectElement, value) {
    // Si la valeur est un tableau, prendre la première
    const valueToMatch = Array.isArray(value) ? value[0] : value;
    
    // Normalisation de la valeur pour la comparaison
    const normalizedValue = String(valueToMatch).toLowerCase().trim();
    
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
