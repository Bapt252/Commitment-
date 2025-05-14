// Définir l'URL de la page de recommandation de candidats
const RECOMMENDATION_URL = "candidate-recommendation.html";
const DASHBOARD_URL = "company-dashboard.html";

// Fonction pour afficher un message de debug
function showDebugMessage(message) {
    const debugSection = document.getElementById('debug-section');
    const debugContent = document.getElementById('debug-content');
    debugSection.style.display = 'block';
    
    // Ajouter le nouveau message
    const msgElement = document.createElement('p');
    msgElement.textContent = message;
    debugContent.appendChild(msgElement);
}

// Fonction pour activer le mode debug
function activateDebugMode() {
    const debugSection = document.getElementById('debug-section');
    debugSection.style.display = 'block';
    showDebugMessage('Mode debug activé');
    
    // Afficher le contenu de sessionStorage
    const parsedJobData = sessionStorage.getItem('parsedJobData');
    if (parsedJobData) {
        showDebugMessage('Données trouvées dans sessionStorage: ' + parsedJobData);
    } else {
        showDebugMessage('Aucune donnée trouvée dans sessionStorage');
    }
}

// Vérifier si un paramètre debug est présent dans l'URL
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.has('debug')) {
    activateDebugMode();
    // Ajouter un message supplémentaire pour indiquer l'URL de l'API
    showDebugMessage('URL de l\'API configurée: ' + (urlParams.get('apiUrl') || 'http://localhost:5055'));
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser l'API JOB PARSER
    const jobParserAPI = new JobParserAPI({
        debug: urlParams.has('debug'),
        enablePDFCleaning: true  // Activer le nettoyage PDF
    });
    
    // Gérer le clic sur le bouton d'aide à la configuration
    const backendHelpBtn = document.getElementById('backend-help-btn');
    if (backendHelpBtn) {
        backendHelpBtn.addEventListener('click', function() {
            // Si le panel de config est déjà affiché, le clic sur le bouton l'ouvre
            const configButton = document.getElementById('backend-config-button');
            if (configButton) {
                configButton.click();
            }
        });
    }
    
    // Mettre à jour la bannière d'état du backend
    function updateBackendStatusBanner(connected) {
        const banner = document.getElementById('backend-status-banner');
        const statusText = document.getElementById('backend-status-text');
        
        if (connected) {
            banner.className = 'backend-status-banner connected';
            statusText.textContent = 'Connecté au service d\'analyse GPT';
        } else {
            banner.className = 'backend-status-banner disconnected';
            statusText.textContent = 'Service d\'analyse GPT non disponible - Vérifiez la configuration';
        }
    }
    
    // Vérifier la connexion au backend au démarrage
    setTimeout(async function() {
        const apiBaseUrl = urlParams.get('apiUrl') || 'http://localhost:5055';
        try {
            const response = await fetch(`${apiBaseUrl}/api/health`, {
                method: 'GET',
                signal: AbortSignal.timeout(2000) // 2 secondes timeout
            });
            
            updateBackendStatusBanner(response.ok);
        } catch (error) {
            updateBackendStatusBanner(false);
        }
    }, 1000);
    
    // Gérer les sections conditionnelles
    const recruitmentYes = document.getElementById('recruitment-yes');
    const recruitmentNo = document.getElementById('recruitment-no');
    const jobParsingSection = document.getElementById('job-parsing-section');
    const noticeYes = document.getElementById('notice-yes');
    const noticeNo = document.getElementById('notice-no');
    const noticeDurationSection = document.getElementById('notice-duration-section');
    const sectorYes = document.getElementById('sector-yes');
    const sectorNo = document.getElementById('sector-no');
    const sectorListSection = document.getElementById('sector-list-section');
    
    // Gérer l'affichage conditionnel du parsing de job
    recruitmentYes.addEventListener('change', function() {
        if (this.checked) {
            jobParsingSection.classList.add('active');
            
            // Stocker la réponse dans sessionStorage
            sessionStorage.setItem('recruitmentNeeded', 'yes');
        }
    });
    
    recruitmentNo.addEventListener('change', function() {
        if (this.checked) {
            jobParsingSection.classList.remove('active');
            
            // Stocker la réponse dans sessionStorage
            sessionStorage.setItem('recruitmentNeeded', 'no');
            
            // Rediriger vers le dashboard entreprise après confirmation
            const redirect = confirm("Vous allez être redirigé vers le dashboard entreprise. Continuer?");
            if (redirect) {
                // Sauvegarder les données du formulaire avant redirection
                saveFormData();
                
                // Rediriger vers le dashboard
                window.location.href = DASHBOARD_URL;
            }
        }
    });
    
    // Gérer l'affichage conditionnel de la durée du préavis
    noticeYes.addEventListener('change', function() {
        if (this.checked) {
            noticeDurationSection.classList.add('active');
        }
    });
    
    noticeNo.addEventListener('change', function() {
        if (this.checked) {
            noticeDurationSection.classList.remove('active');
        }
    });
    
    // Gérer l'affichage conditionnel des secteurs d'activité
    sectorYes.addEventListener('change', function() {
        if (this.checked) {
            sectorListSection.classList.add('active');
        }
    });
    
    sectorNo.addEventListener('change', function() {
        if (this.checked) {
            sectorListSection.classList.remove('active');
        }
    });
    
    // Générer automatiquement une description à partir du site web
    const generateDescriptionBtn = document.getElementById('generate-description');
    const companyWebsiteInput = document.getElementById('company-website');
    const companyDescriptionInput = document.getElementById('company-description');
    
    generateDescriptionBtn.addEventListener('click', function() {
        const websiteUrl = companyWebsiteInput.value.trim();
        if (!websiteUrl) {
            alert('Veuillez d\'abord saisir l\'URL de votre site web.');
            return;
        }
        
        // Simuler un chargement
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Génération...';
        
        // Appel à l'API (à implémenter)
        setTimeout(() => {
            // Simulation de réponse (à remplacer par l'appel API réel)
            companyDescriptionInput.value = `Description automatique générée à partir du site web ${websiteUrl}. Cette fonctionnalité utilisera l'API pour extraire les informations pertinentes.`;
            
            // Réinitialiser le bouton
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-magic"></i> Auto';
        }, 1500);
    });
    
    // Fonction pour sauvegarder les données du formulaire
    function saveFormData() {
        const formData = {
            companyName: document.getElementById('company-name').value,
            companyAddress: document.getElementById('company-address').value,
            companyWebsite: document.getElementById('company-website').value,
            companyDescription: document.getElementById('company-description').value,
            companySize: document.getElementById('company-size').value,
            contactName: document.getElementById('contact-name').value,
            contactTitle: document.getElementById('contact-title').value,
            contactEmail: document.getElementById('contact-email').value,
            contactPhone: document.getElementById('contact-phone').value,
            contactPreferred: document.getElementById('contact-preferred').value,
            recruitmentNeeded: document.querySelector('input[name="recruitment-need"]:checked')?.value || 'no'
        };
        
        // Stocker les données dans sessionStorage
        sessionStorage.setItem('clientFormData', JSON.stringify(formData));
    }
    
    // Gestion de la validation de formulaire
    const form = document.getElementById('client-questionnaire-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Sauvegarder les données du formulaire
        saveFormData();
        
        // Afficher un message de succès
        showNotification('Votre demande a été envoyée avec succès!', 'success');
        
        // Vérifier la réponse à la question de recrutement
        const recruitmentNeeded = sessionStorage.getItem('recruitmentNeeded') || 'no';
        
        // Rediriger vers la page appropriée après un court délai
        setTimeout(() => {
            if (recruitmentNeeded === 'yes') {
                // Si un recrutement est nécessaire, rediriger vers la page de recommandation
                window.location.href = RECOMMENDATION_URL;
            } else {
                // Sinon, rediriger vers le dashboard
                window.location.href = DASHBOARD_URL;
            }
        }, 2000);
    });
    
    // Vérifier s'il y a des données sauvegardées et les pré-remplir
    const savedFormData = sessionStorage.getItem('clientFormData');
    if (savedFormData) {
        try {
            const data = JSON.parse(savedFormData);
            
            // Pré-remplir les champs
            document.getElementById('company-name').value = data.companyName || '';
            document.getElementById('company-address').value = data.companyAddress || '';
            document.getElementById('company-website').value = data.companyWebsite || '';
            document.getElementById('company-description').value = data.companyDescription || '';
            document.getElementById('company-size').value = data.companySize || '';
            document.getElementById('contact-name').value = data.contactName || '';
            document.getElementById('contact-title').value = data.contactTitle || '';
            document.getElementById('contact-email').value = data.contactEmail || '';
            document.getElementById('contact-phone').value = data.contactPhone || '';
            document.getElementById('contact-preferred').value = data.contactPreferred || '';
            
            // Vérifier la réponse à la question de recrutement
            if (data.recruitmentNeeded === 'yes') {
                document.getElementById('recruitment-yes').checked = true;
                jobParsingSection.classList.add('active');
            } else if (data.recruitmentNeeded === 'no') {
                document.getElementById('recruitment-no').checked = true;
            }
        } catch (error) {
            console.error('Erreur lors du chargement des données sauvegardées:', error);
        }
    }
    
    // La fonction initializeForm est dans questionnaire-navigation.js
    // Elle sera appelée automatiquement au chargement du script
});

// Fonction d'affichage des notifications
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    // Configurer le type de notification
    notification.className = 'notification ' + type;
    
    // Mettre à jour l'icône
    const icon = notification.querySelector('.notification-icon i');
    if (icon) {
        // Changer l'icône en fonction du type
        icon.className = type === 'success' 
            ? 'fas fa-check-circle' 
            : (type === 'error' ? 'fas fa-exclamation-circle' : 'fas fa-info-circle');
    }
    
    // Mettre à jour le titre
    const title = notification.querySelector('.notification-title');
    if (title) {
        title.textContent = type === 'success' 
            ? 'Succès' 
            : (type === 'error' ? 'Erreur' : 'Information');
    }
    
    // Mettre à jour le message
    const notifMessage = notification.querySelector('.notification-message');
    if (notifMessage) {
        notifMessage.textContent = message;
    }
    
    // Afficher la notification
    notification.style.display = 'flex';
    
    // Faire disparaître la notification après un délai
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
    
    // Ajouter un gestionnaire de clic pour fermer la notification
    const closeBtn = notification.querySelector('.notification-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            notification.style.display = 'none';
        });
    }
}
