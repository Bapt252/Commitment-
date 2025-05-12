/**
 * Module d'intégration automatique du parsing GPT
 * Ce module s'assure que le service d'analyse GPT est toujours disponible
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 GPT Auto-Loader: Initialisation...');
    
    // Configuration par défaut pour l'API
    const DEFAULT_API_ENDPOINTS = [
        'http://localhost:5055',  // Local (priorité 1)
        'https://api.commitment-analyzer.com', // Production (priorité 2)
        'https://gpt-parser-api.onrender.com'  // Backup (priorité 3)
    ];
    
    // Fonction principale d'initialisation
    async function initGptAnalysis() {
        try {
            // 1. Récupérer l'URL de l'API depuis les paramètres ou utiliser la détection automatique
            const apiUrl = getApiUrl();
            
            // 2. Ajouter le bouton d'analyse GPT sur la page
            addGptAnalysisButton();
            
            // 3. Vérifier la disponibilité de l'API
            const isApiAvailable = await checkApiAvailability(apiUrl);
            
            // 4. Si l'API est disponible, activer le bouton
            if (isApiAvailable) {
                enableGptButton(apiUrl);
                console.log('🤖 GPT Auto-Loader: API disponible à ' + apiUrl);
            } else {
                // Si l'API principale n'est pas disponible, essayer les alternatives
                console.log('🤖 GPT Auto-Loader: API principale non disponible, tentative avec les alternatives...');
                for (const endpoint of DEFAULT_API_ENDPOINTS) {
                    if (endpoint !== apiUrl) {
                        const isAltAvailable = await checkApiAvailability(endpoint);
                        if (isAltAvailable) {
                            enableGptButton(endpoint);
                            console.log('🤖 GPT Auto-Loader: API alternative disponible à ' + endpoint);
                            break;
                        }
                    }
                }
            }
        } catch (error) {
            console.error('🤖 GPT Auto-Loader: Erreur d\'initialisation', error);
        }
    }
    
    // Récupérer l'URL de l'API depuis les paramètres ou utiliser la valeur par défaut
    function getApiUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        const apiParam = urlParams.get('apiUrl');
        
        if (apiParam) {
            return apiParam;
        }
        
        // Si pas de paramètre, utiliser la première URL par défaut
        return DEFAULT_API_ENDPOINTS[0];
    }
    
    // Ajouter le bouton d'analyse GPT
    function addGptAnalysisButton() {
        // Trouver les éléments cibles pour insérer le bouton
        const dropZone = document.getElementById('job-drop-zone');
        const fileInput = document.getElementById('job-file-input');
        const analyzeButton = document.getElementById('analyze-job-text');
        
        if (dropZone) {
            // 1. Bouton principal après la zone de dépôt
            const gptButton = createGptButton('analyze-with-gpt-main');
            
            // Si un badge de fichier existe, insérer avant
            const fileBadge = document.getElementById('file-badge');
            if (fileBadge) {
                dropZone.insertBefore(gptButton, fileBadge);
            } else {
                dropZone.appendChild(gptButton);
            }
        }
        
        // 2. Bouton à côté du bouton d'analyse texte
        if (analyzeButton) {
            const textAreaContainer = analyzeButton.closest('.textarea-container');
            if (textAreaContainer) {
                const gptTextButton = createGptButton('analyze-with-gpt-text');
                gptTextButton.classList.add('analyze-button');
                gptTextButton.style.right = '50px';
                
                textAreaContainer.appendChild(gptTextButton);
            }
        }
        
        // 3. Bouton dans la section des résultats
        const jobInfoContainer = document.getElementById('job-info-container');
        if (jobInfoContainer) {
            const actionContainer = document.createElement('div');
            actionContainer.className = 'gpt-analyze-btn-container';
            actionContainer.style.display = 'flex';
            actionContainer.style.justifyContent = 'center';
            actionContainer.style.marginTop = '20px';
            
            const gptActionButton = createGptButton('analyze-with-gpt-results');
            gptActionButton.className = 'btn btn-success';
            gptActionButton.innerHTML = '<i class="fas fa-robot"></i> Analyser avec GPT';
            gptActionButton.style.fontSize = '16px';
            gptActionButton.style.padding = '12px 24px';
            
            actionContainer.appendChild(gptActionButton);
            
            // Ajouter un élément pour afficher le statut
            const statusElement = document.createElement('span');
            statusElement.id = 'gpt-analyze-status';
            statusElement.style.marginLeft = '12px';
            statusElement.style.alignSelf = 'center';
            actionContainer.appendChild(statusElement);
            
            // Trouver l'endroit où insérer
            const jobActions = jobInfoContainer.querySelector('.job-actions');
            if (jobActions) {
                jobInfoContainer.insertBefore(actionContainer, jobActions);
            } else {
                jobInfoContainer.appendChild(actionContainer);
            }
        }
        
        console.log('🤖 GPT Auto-Loader: Boutons ajoutés');
    }
    
    // Créer un bouton d'analyse GPT
    function createGptButton(id) {
        const button = document.createElement('button');
        button.type = 'button';
        button.id = id;
        button.className = 'gpt-analyze-button';
        button.innerHTML = '<i class="fas fa-robot"></i>';
        button.title = 'Analyser avec GPT';
        button.disabled = true; // Désactivé par défaut jusqu'à ce que l'API soit vérifiée
        
        // Styles
        button.style.backgroundColor = '#10b981';
        button.style.color = 'white';
        button.style.border = 'none';
        button.style.borderRadius = '50%';
        button.style.width = '40px';
        button.style.height = '40px';
        button.style.display = 'flex';
        button.style.alignItems = 'center';
        button.style.justifyContent = 'center';
        button.style.cursor = 'pointer';
        button.style.margin = '10px auto';
        button.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
        button.style.transition = 'all 0.3s ease';
        
        return button;
    }
    
    // Vérifier la disponibilité de l'API
    async function checkApiAvailability(apiUrl) {
        try {
            // Tester d'abord avec l'endpoint de santé
            const healthEndpoint = `${apiUrl}/api/health`;
            const response = await fetch(healthEndpoint, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                signal: AbortSignal.timeout(3000) // Timeout de 3 secondes
            });
            
            if (response.ok) {
                return true;
            }
            
            // Essayer avec l'endpoint de base
            const baseEndpoint = `${apiUrl}/api`;
            const baseResponse = await fetch(baseEndpoint, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                },
                signal: AbortSignal.timeout(3000)
            });
            
            return baseResponse.ok;
        } catch (error) {
            console.log('🤖 GPT Auto-Loader: API non disponible à ' + apiUrl, error.message);
            return false;
        }
    }
    
    // Activer le bouton GPT avec l'URL de l'API
    function enableGptButton(apiUrl) {
        // Stocker l'URL de l'API dans une variable globale
        window.gptApiUrl = apiUrl;
        
        // Activer tous les boutons GPT
        document.querySelectorAll('[id^="analyze-with-gpt"]').forEach(button => {
            button.disabled = false;
            button.addEventListener('click', () => handleGptAnalysis(apiUrl));
            
            // Ajouter un effet hover
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'scale(1.1)';
                this.style.boxShadow = '0 6px 8px rgba(0, 0, 0, 0.15)';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'scale(1)';
                this.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
            });
        });
        
        // Ajouter un badge discret pour indiquer que GPT est connecté
        const header = document.querySelector('.header');
        if (header) {
            const gptBadge = document.createElement('div');
            gptBadge.className = 'gpt-connected-badge';
            gptBadge.innerHTML = '<i class="fas fa-robot"></i> GPT connecté';
            gptBadge.style.position = 'absolute';
            gptBadge.style.top = '10px';
            gptBadge.style.right = '10px';
            gptBadge.style.backgroundColor = 'rgba(16, 185, 129, 0.1)';
            gptBadge.style.color = '#10b981';
            gptBadge.style.fontSize = '12px';
            gptBadge.style.padding = '4px 8px';
            gptBadge.style.borderRadius = '4px';
            
            header.style.position = 'relative';
            header.appendChild(gptBadge);
        }
    }
    
    // Gérer l'analyse GPT
    async function handleGptAnalysis(apiUrl) {
        console.log('🤖 GPT Auto-Loader: Démarrage de l\'analyse');
        
        // Rechercher le fichier ou le texte à analyser
        const fileInput = document.getElementById('job-file-input');
        const textArea = document.getElementById('job-description-text');
        const statusElement = document.getElementById('gpt-analyze-status');
        
        // Mettre à jour le statut si l'élément existe
        const updateStatus = (message, color) => {
            if (statusElement) {
                statusElement.textContent = message;
                statusElement.style.color = color;
            }
        };
        
        // Désactiver tous les boutons pendant l'analyse
        document.querySelectorAll('[id^="analyze-with-gpt"]').forEach(btn => {
            if (btn) btn.disabled = true;
        });
        
        try {
            // Afficher le loader si disponible
            const loader = document.getElementById('analysis-loader');
            if (loader) {
                loader.style.display = 'flex';
            }
            
            // Cas 1: Fichier sélectionné
            if (fileInput && fileInput.files && fileInput.files.length > 0) {
                const file = fileInput.files[0];
                
                updateStatus('Analyse du fichier en cours...', '#7C3AED');
                
                // Préparer les données pour l'envoi
                const formData = new FormData();
                formData.append('file', file);
                
                // Appeler l'API de parsing
                const response = await fetch(`${apiUrl}/api/parse-job-posting`, {
                    method: 'POST',
                    body: formData,
                });
                
                await handleApiResponse(response, updateStatus);
            }
            // Cas 2: Texte saisi
            else if (textArea && textArea.value.trim()) {
                updateStatus('Analyse du texte en cours...', '#7C3AED');
                
                // Préparer les données pour l'envoi
                const formData = new FormData();
                formData.append('text', textArea.value.trim());
                
                // Appeler l'API de parsing
                const response = await fetch(`${apiUrl}/api/parse-job-posting`, {
                    method: 'POST',
                    body: formData,
                });
                
                await handleApiResponse(response, updateStatus);
            }
            // Aucune donnée à analyser
            else {
                throw new Error('Veuillez d\'abord sélectionner un fichier ou saisir le texte de la fiche de poste.');
            }
        } catch (error) {
            console.error('🤖 GPT Auto-Loader: Erreur d\'analyse:', error);
            updateStatus(`Erreur: ${error.message}`, 'red');
            
            // Afficher une notification d'erreur si la fonction existe
            if (typeof window.showNotification === 'function') {
                window.showNotification(error.message, 'error');
            } else {
                alert(`Erreur: ${error.message}`);
            }
        } finally {
            // Réactiver les boutons
            document.querySelectorAll('[id^="analyze-with-gpt"]').forEach(btn => {
                if (btn) btn.disabled = false;
            });
            
            // Masquer le loader
            const loader = document.getElementById('analysis-loader');
            if (loader) {
                loader.style.display = 'none';
            }
        }
    }
    
    // Traiter la réponse de l'API
    async function handleApiResponse(response, updateStatus) {
        // Vérifier si la requête a réussi
        if (!response.ok) {
            let errorMessage = 'Erreur lors de l\'analyse du document';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
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
    
    // Remplir le formulaire avec les données extraites
    function fillFormWithJobData(jobData) {
        console.log('🤖 GPT Auto-Loader: Données reçues:', jobData);
        
        // Mapping des champs
        const fieldMapping = {
            'title': { selector: '#job-title-value' },
            'titre': { selector: '#job-title-value' },
            'company': { selector: '#job-contract-value' },
            'entreprise': { selector: '#job-contract-value' },
            'location': { selector: '#job-location-value' },
            'localisation': { selector: '#job-location-value' },
            'contract_type': { selector: '#job-contract-value' },
            'type_contrat': { selector: '#job-contract-value' },
            'experience': { selector: '#job-experience-value' },
            'education': { selector: '#job-education-value' },
            'formation': { selector: '#job-education-value' },
            'salary': { selector: '#job-salary-value' },
            'salaire': { selector: '#job-salary-value' },
            'skills': { selector: '#job-skills-value', type: 'skills' },
            'competences': { selector: '#job-skills-value', type: 'skills' },
            'responsibilities': { selector: '#job-responsibilities-value', type: 'list' },
            'missions': { selector: '#job-responsibilities-value', type: 'list' },
            'benefits': { selector: '#job-benefits-value', type: 'list' },
            'avantages': { selector: '#job-benefits-value', type: 'list' }
        };
        
        // Pour chaque champ dans le mapping
        for (const [dataKey, fieldInfo] of Object.entries(fieldMapping)) {
            if (jobData[dataKey]) {
                const value = jobData[dataKey];
                const element = document.querySelector(fieldInfo.selector);
                
                if (element) {
                    if (fieldInfo.type === 'skills' && Array.isArray(value)) {
                        element.innerHTML = value.map(skill => 
                            `<span class="tag">${skill}</span>`
                        ).join('');
                    } else if (fieldInfo.type === 'list' && Array.isArray(value)) {
                        element.innerHTML = '<ul>' + 
                            value.map(item => `<li>${item}</li>`).join('') + 
                            '</ul>';
                    } else {
                        element.textContent = Array.isArray(value) ? value.join(', ') : value;
                    }
                }
            }
        }
        
        // Rendre visible le conteneur de résultats
        const jobInfoContainer = document.getElementById('job-info-container');
        if (jobInfoContainer) {
            jobInfoContainer.style.display = 'block';
        }
    }
    
    // Initialiser le module
    initGptAnalysis();
});
