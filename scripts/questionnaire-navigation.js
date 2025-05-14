/**
 * Questionnaire Navigation Script
 * Gère la navigation entre les différentes étapes du questionnaire.
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeForm();
});

/**
 * Initialise le formulaire et la navigation entre les étapes
 */
function initializeForm() {
    // Configurer les boutons de navigation
    setupNavigationButtons();
    
    // Configurer les étapes cliquables
    setupStepsNavigation();
    
    // Initialiser la barre de progression
    updateProgressBar();
    
    // Afficher la première étape (au cas où)
    goToStep(1);
}

/**
 * Configure les boutons Précédent et Suivant pour la navigation
 */
function setupNavigationButtons() {
    // Boutons "Suivant"
    const nextButtons = document.querySelectorAll('.next-step');
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetStep = parseInt(this.getAttribute('data-step'));
            validateAndGoToStep(targetStep);
        });
    });
    
    // Boutons "Précédent"
    const prevButtons = document.querySelectorAll('.prev-step');
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetStep = parseInt(this.getAttribute('data-step'));
            goToStep(targetStep);
        });
    });
    
    // Ajouter le bouton Continuer si manquant à l'étape 1
    ensureNavigationButtons();
}

/**
 * S'assure que tous les boutons de navigation nécessaires existent
 */
function ensureNavigationButtons() {
    // Vérifier si le bouton "Continuer" existe déjà dans l'étape 1
    const step1 = document.querySelector('.form-section[data-step="1"]');
    if (!step1) return;
    
    let navSection = step1.querySelector('.form-navigation');
    
    // Si la section de navigation n'existe pas, la créer
    if (!navSection) {
        navSection = document.createElement('div');
        navSection.className = 'form-navigation';
        step1.appendChild(navSection);
        
        // Ajouter un div vide pour l'alignement flex
        const emptyDiv = document.createElement('div');
        navSection.appendChild(emptyDiv);
    }
    
    // Vérifier si le bouton "Continuer" existe déjà
    let nextButton = navSection.querySelector('.next-step');
    if (!nextButton) {
        nextButton = document.createElement('button');
        nextButton.type = 'button';
        nextButton.className = 'btn btn-primary next-step';
        nextButton.setAttribute('data-step', '2');
        nextButton.innerHTML = 'Continuer <i class="fas fa-arrow-right"></i>';
        
        // Ajouter l'événement de clic
        nextButton.addEventListener('click', function() {
            validateAndGoToStep(2);
        });
        
        navSection.appendChild(nextButton);
    }
}

/**
 * Configure les étapes du header pour être cliquables
 */
function setupStepsNavigation() {
    const steps = document.querySelectorAll('.step');
    
    steps.forEach(step => {
        step.addEventListener('click', function() {
            const targetStep = parseInt(this.getAttribute('data-step'));
            validateAndGoToStep(targetStep);
        });
        
        // Support pour navigation au clavier (accessibilité)
        step.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const targetStep = parseInt(this.getAttribute('data-step'));
                validateAndGoToStep(targetStep);
            }
        });
    });
}

/**
 * Valide l'étape actuelle avant de passer à l'étape suivante
 * @param {number} targetStep - Numéro de l'étape cible
 */
function validateAndGoToStep(targetStep) {
    const currentStep = getCurrentStep();
    
    // Vérifier si on avance ou recule
    if (targetStep <= currentStep) {
        // Si on recule ou reste sur la même étape, pas besoin de validation
        goToStep(targetStep);
        return;
    }
    
    // Valider l'étape actuelle
    if (validateStep(currentStep)) {
        goToStep(targetStep);
    }
}

/**
 * Valide le contenu de l'étape spécifiée
 * @param {number} stepNumber - Numéro de l'étape à valider
 * @returns {boolean} - true si l'étape est valide, false sinon
 */
function validateStep(stepNumber) {
    // En fonction de l'étape, effectuer des validations spécifiques
    switch(stepNumber) {
        case 1:
            // Pour l'étape 1, vérifier les champs obligatoires
            const companyName = document.getElementById('company-name');
            const companyAddress = document.getElementById('company-address');
            
            if (companyName && !companyName.value.trim()) {
                alert('Veuillez renseigner le nom de votre structure.');
                companyName.focus();
                return false;
            }
            
            if (companyAddress && !companyAddress.value.trim()) {
                alert('Veuillez renseigner l\'adresse de votre structure.');
                companyAddress.focus();
                return false;
            }
            
            return true;
            
        case 2:
            // Pour l'étape 2, validation basique des coordonnées de contact
            const contactEmail = document.getElementById('contact-email');
            if (contactEmail && contactEmail.value.trim() && !isValidEmail(contactEmail.value)) {
                alert('Veuillez saisir une adresse email valide.');
                contactEmail.focus();
                return false;
            }
            return true;
            
        case 3:
            // Pour l'étape 3, vérifier si l'utilisateur a choisi une option de recrutement
            const recruitmentYes = document.getElementById('recruitment-yes');
            const recruitmentNo = document.getElementById('recruitment-no');
            
            if ((!recruitmentYes || !recruitmentYes.checked) && (!recruitmentNo || !recruitmentNo.checked)) {
                alert('Veuillez indiquer si vous avez un poste à recruter.');
                return false;
            }
            
            // Si l'utilisateur a indiqué oui, on n'impose pas de validation supplémentaire
            // car les données peuvent être complétées plus tard
            
            return true;
            
        case 4:
            // Vérifier que les étapes précédentes ont été complétées
            return true;
            
        default:
            return true;
    }
}

/**
 * Vérifie si une adresse email est valide
 * @param {string} email - Adresse email à vérifier
 * @returns {boolean} - true si l'email est valide, false sinon
 */
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

/**
 * Change l'étape active du formulaire
 * @param {number} stepNumber - Numéro de l'étape à afficher
 */
function goToStep(stepNumber) {
    // Récupérer toutes les sections d'étape
    const sections = document.querySelectorAll('.form-section');
    const steps = document.querySelectorAll('.step');
    
    // Masquer toutes les sections
    sections.forEach(section => {
        section.classList.remove('active');
    });
    
    // Afficher la section cible
    const targetSection = document.querySelector(`.form-section[data-step="${stepNumber}"]`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Mettre à jour les indicateurs d'étape dans le header
    steps.forEach(step => {
        const stepNum = parseInt(step.getAttribute('data-step'));
        
        // Retirer les classes actives
        step.classList.remove('active', 'completed');
        
        // Ajouter les classes appropriées
        if (stepNum === stepNumber) {
            step.classList.add('active');
        } else if (stepNum < stepNumber) {
            step.classList.add('completed');
        }
    });
    
    // Mettre à jour la barre de progression
    updateProgressBar(stepNumber);
    
    // Défiler vers le haut de la page pour une meilleure expérience utilisateur
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

/**
 * Met à jour la barre de progression en fonction de l'étape actuelle
 * @param {number} [stepNumber] - Numéro de l'étape actuelle (optionnel)
 */
function updateProgressBar(stepNumber) {
    if (!stepNumber) {
        stepNumber = getCurrentStep();
    }
    
    // Calculer le pourcentage de progression
    const totalSteps = document.querySelectorAll('.step').length;
    const progressPercent = ((stepNumber - 1) / (totalSteps - 1)) * 100;
    
    // Mettre à jour la barre de progression
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        progressFill.style.width = `${progressPercent}%`;
    }
}

/**
 * Récupère le numéro de l'étape actuellement active
 * @returns {number} - Numéro de l'étape active
 */
function getCurrentStep() {
    const activeSection = document.querySelector('.form-section.active');
    if (activeSection) {
        return parseInt(activeSection.getAttribute('data-step'));
    }
    return 1; // Par défaut, retourner l'étape 1
}

/**
 * Affiche ou cache une notification
 * @param {string} message - Message à afficher
 * @param {string} type - Type de notification (success, error, info)
 */
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

// Exposer les fonctions utiles comme API publique
window.QuestionnaireNavigation = {
    goToStep,
    validateAndGoToStep,
    getCurrentStep,
    showNotification
};
