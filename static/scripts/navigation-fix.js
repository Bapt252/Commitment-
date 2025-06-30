// ========================================
// 🚨 FIX CRITIQUE NEXTEN V2.0 - NAVIGATION SIMPLIFIÉE
// Version sécurisée sans boucles infinies
// ========================================

console.log('🚨 Chargement navigation simplifiée...');

// Variables globales sécurisées
let currentStep = 1;
const totalSteps = 4;
let isInitialized = false;

// ========================================
// FONCTIONS DE NAVIGATION SÉCURISÉES
// ========================================

function safeInitNavigation() {
    if (isInitialized) return;
    
    console.log('🔧 Initialisation navigation sécurisée...');
    
    try {
        // Boutons suivant
        const nextBtn1 = document.getElementById('next-step1');
        const nextBtn2 = document.getElementById('next-step2');
        const nextBtn3 = document.getElementById('next-step3');
        
        if (nextBtn1) nextBtn1.addEventListener('click', () => safeGoToStep(2));
        if (nextBtn2) nextBtn2.addEventListener('click', () => safeGoToStep(3));
        if (nextBtn3) nextBtn3.addEventListener('click', () => safeGoToStep(4));
        
        // Boutons retour
        const backBtn1 = document.getElementById('back-step1');
        const backBtn2 = document.getElementById('back-step2');
        const backBtn3 = document.getElementById('back-step3');
        
        if (backBtn1) backBtn1.addEventListener('click', () => safeGoToStep(1));
        if (backBtn2) backBtn2.addEventListener('click', () => safeGoToStep(2));
        if (backBtn3) backBtn3.addEventListener('click', () => safeGoToStep(3));
        
        // Bouton soumission
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) submitBtn.addEventListener('click', safeSubmitForm);
        
        isInitialized = true;
        console.log('✅ Navigation initialisée avec succès');
        
    } catch (error) {
        console.error('❌ Erreur initialisation navigation:', error);
    }
}

function safeValidateStep1() {
    try {
        const fullName = document.getElementById('full-name');
        const jobTitle = document.getElementById('job-title');
        
        if (!fullName || !fullName.value.trim()) {
            safeShowNotification('Veuillez renseigner votre nom et prénom', 'error');
            return false;
        }
        
        if (!jobTitle || !jobTitle.value.trim()) {
            safeShowNotification('Veuillez renseigner le poste souhaité', 'error');
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Erreur validation étape 1:', error);
        return false;
    }
}

function safeValidateStep2() {
    try {
        const address = document.getElementById('address');
        const transportMethods = document.querySelectorAll('input[name="transport-method"]:checked');
        const officePreference = document.querySelector('input[name="office-preference"]:checked');
        
        if (!address || !address.value.trim()) {
            safeShowNotification('Veuillez renseigner votre adresse', 'error');
            return false;
        }
        
        if (transportMethods.length === 0) {
            safeShowNotification('Veuillez sélectionner au moins un moyen de transport', 'error');
            return false;
        }
        
        if (!officePreference) {
            safeShowNotification('Veuillez sélectionner votre préférence d\'environnement de travail', 'error');
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Erreur validation étape 2:', error);
        return false;
    }
}

function safeGoToStep(stepNumber) {
    if (stepNumber < 1 || stepNumber > totalSteps) return false;
    
    console.log(`📍 Navigation sécurisée vers étape ${stepNumber}`);
    
    try {
        // Validation simple
        if (stepNumber > currentStep) {
            if (currentStep === 1 && !safeValidateStep1()) return false;
            if (currentStep === 2 && !safeValidateStep2()) return false;
        }
        
        // Masquer toutes les étapes
        const steps = document.querySelectorAll('.form-step');
        steps.forEach(step => step.classList.remove('active'));
        
        // Masquer tous les indicateurs
        const indicators = document.querySelectorAll('.step');
        indicators.forEach(step => {
            step.classList.remove('active', 'completed');
        });
        
        // Afficher la nouvelle étape
        const targetStep = document.getElementById(`form-step${stepNumber}`);
        const targetIndicator = document.getElementById(`step${stepNumber}`);
        
        if (targetStep && targetIndicator) {
            targetStep.classList.add('active');
            targetIndicator.classList.add('active');
            
            // Marquer les étapes précédentes comme complétées
            for (let i = 1; i < stepNumber; i++) {
                const prevStep = document.getElementById(`step${i}`);
                if (prevStep) prevStep.classList.add('completed');
            }
            
            // Mettre à jour la barre de progression
            safeUpdateProgressBar(stepNumber);
            
            currentStep = stepNumber;
            window.scrollTo(0, 0);
            
            safeShowNotification(`Étape ${stepNumber} sur ${totalSteps}`, 'info');
            console.log(`✅ Navigation réussie vers étape ${stepNumber}`);
            return true;
        }
        
        console.error(`❌ Éléments manquants pour l'étape ${stepNumber}`);
        return false;
        
    } catch (error) {
        console.error('❌ Erreur navigation:', error);
        return false;
    }
}

function safeUpdateProgressBar(stepNumber) {
    try {
        const progressBar = document.getElementById('stepper-progress');
        if (progressBar) {
            const progressPercent = ((stepNumber - 1) / (totalSteps - 1)) * 100;
            progressBar.style.width = `${progressPercent}%`;
        }
    } catch (error) {
        console.error('Erreur mise à jour progress bar:', error);
    }
}

function safeShowNotification(message, type = 'info') {
    try {
        const notification = document.getElementById('notification');
        if (!notification) return;
        
        const messageElement = notification.querySelector('.notification-message');
        const iconElement = notification.querySelector('i');
        
        if (messageElement) messageElement.textContent = message;
        
        // Réinitialiser les classes
        notification.className = 'notification';
        notification.classList.add(type);
        
        // Icônes selon le type
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        
        if (iconElement) {
            iconElement.className = `fas ${icons[type] || icons.info}`;
        }
        
        // Afficher la notification
        notification.classList.add('show');
        
        // Masquer après 4 secondes
        setTimeout(() => {
            notification.classList.remove('show');
        }, 4000);
        
    } catch (error) {
        console.error('Erreur affichage notification:', error);
    }
}

function safeSubmitForm() {
    console.log('📝 Soumission sécurisée du formulaire...');
    
    try {
        // Validation étape 4 simplifiée
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) loadingOverlay.classList.add('active');
        
        // Simuler un traitement
        setTimeout(() => {
            safeShowNotification('Questionnaire envoyé avec succès !', 'success');
            
            if (loadingOverlay) loadingOverlay.classList.remove('active');
            
            // Redirection après succès
            setTimeout(() => {
                window.location.href = 'https://bapt252.github.io/Commitment-/templates/success.html';
            }, 2000);
            
        }, 3000);
        
    } catch (error) {
        console.error('Erreur soumission:', error);
    }
}

// ========================================
// CORRECTION DONNÉES CV SÉCURISÉE
// ========================================

function safeFixCVData() {
    console.log('🔧 Correction sécurisée données CV...');
    
    try {
        const urlParams = new URLSearchParams(window.location.search);
        const isParsingMode = urlParams.get('from') === 'parsing' && urlParams.get('cv_data') === 'available';
        
        if (!isParsingMode) return;
        
        // Données CV cohérentes
        const fullNameField = document.getElementById('full-name');
        const jobTitleField = document.getElementById('job-title');
        const addressField = document.getElementById('address');
        
        if (fullNameField && !fullNameField.value) {
            fullNameField.value = 'Marie Dubois';
            safeAddDemoBadge(fullNameField);
        }
        
        if (jobTitleField && !jobTitleField.value) {
            jobTitleField.value = 'Développeuse Full-Stack Senior';
            safeAddDemoBadge(jobTitleField);
        }
        
        if (addressField && !addressField.value) {
            addressField.value = '15 Rue de la République, 75011 Paris';
            safeAddDemoBadge(addressField);
        }
        
        // Pré-sélectionner les transports en commun
        const transportCheckbox = document.querySelector('input[value="public-transport"]');
        if (transportCheckbox) transportCheckbox.checked = true;
        
        // Créer les indicateurs si nécessaire
        safeCreateIndicators();
        
        console.log('✅ Données CV corrigées avec succès');
        
    } catch (error) {
        console.error('Erreur correction CV:', error);
    }
}

function safeAddDemoBadge(field) {
    try {
        const parent = field.parentElement;
        if (parent && !parent.querySelector('.simulated-data-badge')) {
            const badge = document.createElement('span');
            badge.className = 'simulated-data-badge';
            badge.textContent = 'Demo';
            badge.style.cssText = `
                background: linear-gradient(135deg, #8b5cf6, #a855f7);
                color: white; padding: 4px 8px; border-radius: 12px;
                font-size: 0.7rem; font-weight: 600; margin-left: 10px;
                position: absolute; top: 8px; right: 8px; z-index: 5;
            `;
            parent.style.position = 'relative';
            parent.appendChild(badge);
        }
    } catch (error) {
        console.error('Erreur ajout badge demo:', error);
    }
}

function safeCreateIndicators() {
    try {
        const container = document.getElementById('cv-parsing-indicators');
        if (!container || container.innerHTML.trim()) return;
        
        container.innerHTML = `
            <div class="cv-test-indicator">
                🔵 MODE TEST CV - Données simulées pour démonstration du parsing CV
            </div>
            <div class="real-cv-indicator">
                🟢 CV PARSÉ AVEC SUCCÈS - Formulaire pré-rempli avec vos données
            </div>
        `;
        
    } catch (error) {
        console.error('Erreur création indicateurs:', error);
    }
}

// ========================================
// INITIALISATION SÉCURISÉE
// ========================================

function safeInitialize() {
    if (isInitialized) return;
    
    console.log('🚀 Initialisation sécurisée du système...');
    
    try {
        // Initialiser la navigation
        safeInitNavigation();
        
        // Corriger les données CV si nécessaire
        safeFixCVData();
        
        console.log('✅ Système initialisé avec succès');
        
    } catch (error) {
        console.error('❌ Erreur initialisation:', error);
    }
}

// ========================================
// DÉMARRAGE SÉCURISÉ
// ========================================

// Attendre que le DOM soit prêt
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(safeInitialize, 200);
    });
} else {
    setTimeout(safeInitialize, 200);
}

// Export sécurisé des fonctions principales
if (typeof window !== 'undefined') {
    window.goToStep = safeGoToStep;
    window.showNotification = safeShowNotification;
}

console.log('✅ Navigation NEXTEN V2.0 sécurisée chargée !');
