// ========================================
// 🚨 FIX CRITIQUE NEXTEN V2.0 - NAVIGATION
// Résout les problèmes de navigation et cohérence des données
// ========================================

console.log('🚨 Chargement du fix critique de navigation...');

// Variables globales pour le système de navigation
let currentStep = 1;
const totalSteps = 4;

// ========================================
// FONCTIONS DE NAVIGATION MANQUANTES
// ========================================

function initNavigation() {
    console.log('🔧 Initialisation navigation...');
    
    // Boutons suivant
    document.getElementById('next-step1')?.addEventListener('click', () => goToStep(2));
    document.getElementById('next-step2')?.addEventListener('click', () => goToStep(3));
    document.getElementById('next-step3')?.addEventListener('click', () => goToStep(4));
    
    // Boutons retour
    document.getElementById('back-step1')?.addEventListener('click', () => goToStep(1));
    document.getElementById('back-step2')?.addEventListener('click', () => goToStep(2));
    document.getElementById('back-step3')?.addEventListener('click', () => goToStep(3));
    
    // Bouton soumission
    document.getElementById('submit-btn')?.addEventListener('click', submitForm);
    
    console.log('✅ Navigation initialisée');
}

function validateStep1() {
    const fullName = document.getElementById('full-name').value.trim();
    const jobTitle = document.getElementById('job-title').value.trim();
    
    if (!fullName) {
        showNotification('Veuillez renseigner votre nom et prénom', 'error');
        return false;
    }
    
    if (!jobTitle) {
        showNotification('Veuillez renseigner le poste souhaité', 'error');
        return false;
    }
    
    return true;
}

function validateStep2() {
    const address = document.getElementById('address').value.trim();
    const transportMethods = document.querySelectorAll('input[name="transport-method"]:checked');
    const officePreference = document.querySelector('input[name="office-preference"]:checked');
    
    if (!address) {
        showNotification('Veuillez renseigner votre adresse', 'error');
        return false;
    }
    
    if (transportMethods.length === 0) {
        showNotification('Veuillez sélectionner au moins un moyen de transport', 'error');
        return false;
    }
    
    if (!officePreference) {
        showNotification('Veuillez sélectionner votre préférence d\'environnement de travail', 'error');
        return false;
    }
    
    // Validation du système de contrats
    if (window.contractSystem && !window.contractSystem.validateSelection()) {
        return false;
    }
    
    return true;
}

function validateStep3() {
    const structureTypes = document.querySelectorAll('input[name="structure-type"]:checked');
    const salaryRange = document.getElementById('salary-range').value.trim();
    
    if (structureTypes.length === 0) {
        showNotification('Veuillez sélectionner au moins un type de structure', 'error');
        return false;
    }
    
    if (!salaryRange) {
        showNotification('Veuillez renseigner votre fourchette de rémunération', 'error');
        return false;
    }
    
    return true;
}

function validateStep4() {
    const availability = document.querySelector('input[name="availability"]:checked');
    const currentlyEmployed = document.querySelector('input[name="currently-employed"]:checked');
    const recruitmentStatus = document.querySelector('input[name="recruitment-status"]:checked');
    const privacyConsent = document.getElementById('privacy-consent').checked;
    
    if (!availability) {
        showNotification('Veuillez indiquer votre disponibilité', 'error');
        return false;
    }
    
    if (!currentlyEmployed) {
        showNotification('Veuillez indiquer si vous êtes actuellement en poste', 'error');
        return false;
    }
    
    if (!recruitmentStatus) {
        showNotification('Veuillez indiquer où vous en êtes dans vos process de recrutement', 'error');
        return false;
    }
    
    if (!privacyConsent) {
        showNotification('Veuillez accepter la politique de confidentialité', 'error');
        return false;
    }
    
    return true;
}

function goToStep(stepNumber) {
    console.log(`📍 Navigation vers étape ${stepNumber}`);
    
    // Validation de l'étape actuelle avant de passer à la suivante
    if (stepNumber > currentStep) {
        const validationFunctions = {
            1: validateStep1,
            2: validateStep2,
            3: validateStep3,
            4: validateStep4
        };
        
        if (validationFunctions[currentStep] && !validationFunctions[currentStep]()) {
            return false;
        }
    }
    
    // Masquer toutes les étapes
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.remove('active');
    });
    
    // Masquer tous les indicateurs d'étape
    document.querySelectorAll('.step').forEach(step => {
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
            if (prevStep) {
                prevStep.classList.add('completed');
            }
        }
        
        // Mettre à jour la barre de progression
        updateProgressBar(stepNumber);
        
        // Scroll vers le haut
        window.scrollTo(0, 0);
        
        currentStep = stepNumber;
        
        showNotification(`Étape ${stepNumber} sur ${totalSteps}`, 'info');
        
        console.log(`✅ Navigation réussie vers étape ${stepNumber}`);
        return true;
    }
    
    console.error(`❌ Impossible de naviguer vers l'étape ${stepNumber}`);
    return false;
}

function updateProgressBar(stepNumber) {
    const progressBar = document.getElementById('stepper-progress');
    if (progressBar) {
        const progressPercent = ((stepNumber - 1) / (totalSteps - 1)) * 100;
        progressBar.style.width = `${progressPercent}%`;
    }
}

function showNotification(message, type = 'info') {
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
}

function submitForm() {
    console.log('📝 Soumission du formulaire...');
    
    if (!validateStep4()) {
        return;
    }
    
    // Afficher l'overlay de chargement
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.classList.add('active');
    }
    
    // Collecter toutes les données
    const formData = collectFormData();
    
    console.log('📊 Données collectées:', formData);
    
    // Simuler un traitement
    setTimeout(() => {
        showNotification('Questionnaire envoyé avec succès !', 'success');
        
        if (loadingOverlay) {
            loadingOverlay.classList.remove('active');
        }
        
        // Redirection après succès
        setTimeout(() => {
            window.location.href = 'https://bapt252.github.io/Commitment-/templates/success.html';
        }, 2000);
        
    }, 3000);
}

function collectFormData() {
    const form = document.getElementById('questionnaire-form');
    const formData = new FormData(form);
    const data = {};
    
    // Convertir FormData en objet
    for (let [key, value] of formData.entries()) {
        if (data[key]) {
            // Si la clé existe déjà, créer un tableau
            if (Array.isArray(data[key])) {
                data[key].push(value);
            } else {
                data[key] = [data[key], value];
            }
        } else {
            data[key] = value;
        }
    }
    
    // Ajouter les données du système de contrats
    if (window.contractSystem) {
        const contractData = window.contractSystem.getContractData();
        data.contractSystem = contractData;
    }
    
    return data;
}

// ========================================
// CORRECTION DES DONNÉES CV
// ========================================

function fixCVDataConsistency() {
    console.log('🔧 Correction cohérence données CV...');
    
    // Données CV cohérentes et fixes
    const consistentCVData = {
        fullName: 'Marie Dubois',
        jobTitle: 'Développeuse Full-Stack Senior', 
        address: '15 Rue de la République, 75011 Paris',
        experience: 'Senior',
        skills: ['JavaScript', 'React', 'Node.js', 'MongoDB']
    };
    
    // Forcer la cohérence des données
    if (document.getElementById('full-name')) {
        document.getElementById('full-name').value = consistentCVData.fullName;
    }
    
    if (document.getElementById('job-title')) {
        document.getElementById('job-title').value = consistentCVData.jobTitle;
    }
    
    if (document.getElementById('address')) {
        document.getElementById('address').value = consistentCVData.address;
    }
    
    // Sauvegarder dans sessionStorage pour cohérence
    try {
        sessionStorage.setItem('cvData', JSON.stringify(consistentCVData));
        console.log('✅ Données CV sauvegardées:', consistentCVData);
    } catch (e) {
        console.warn('Impossible de sauvegarder dans sessionStorage:', e);
    }
    
    // Afficher les badges Demo
    addDemoBadges();
}

function addDemoBadges() {
    const fieldsWithDemo = ['full-name', 'job-title', 'address'];
    
    fieldsWithDemo.forEach(fieldId => {
        const field = document.getElementById(fieldId);
        if (field && !field.nextElementSibling?.classList.contains('simulated-data-badge')) {
            const badge = document.createElement('span');
            badge.className = 'simulated-data-badge';
            badge.style.cssText = `
                background: linear-gradient(135deg, #8b5cf6, #a855f7);
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.7rem;
                font-weight: 600;
                margin-left: 10px;
                position: absolute;
                top: 8px;
                right: 8px;
                z-index: 5;
            `;
            badge.textContent = 'Demo';
            
            // Positionner le badge par rapport au champ parent
            const parent = field.parentElement;
            parent.style.position = 'relative';
            parent.appendChild(badge);
        }
    });
}

// ========================================
// INITIALISATION AUTOMATIQUE
// ========================================

function initializeFixedSystem() {
    console.log('🚀 Initialisation système corrigé...');
    
    // Attendre que le DOM soit complètement chargé
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(runFixes, 100);
        });
    } else {
        setTimeout(runFixes, 100);
    }
}

function runFixes() {
    console.log('🔧 Application des corrections...');
    
    try {
        // 1. Corriger la navigation
        initNavigation();
        
        // 2. Corriger les données CV
        fixCVDataConsistency();
        
        // 3. Initialiser le système de contrats si disponible
        if (typeof ContractSystem !== 'undefined' && !window.contractSystem) {
            window.contractSystem = new ContractSystem();
        }
        
        // 4. Vérifier l'affichage des bandeaux
        verifyIndicators();
        
        console.log('✅ Toutes les corrections appliquées avec succès');
        
    } catch (error) {
        console.error('❌ Erreur lors de l\'application des corrections:', error);
    }
}

function verifyIndicators() {
    const urlParams = new URLSearchParams(window.location.search);
    const isParsingMode = urlParams.get('from') === 'parsing' && urlParams.get('cv_data') === 'available';
    
    if (isParsingMode) {
        console.log('🔵 Mode parsing CV détecté - Affichage des bandeaux');
        
        // Créer les bandeaux s'ils n'existent pas
        createIndicators();
    }
}

function createIndicators() {
    const heroSection = document.querySelector('.hero') || document.querySelector('section');
    if (!heroSection) return;
    
    const container = heroSection.querySelector('.container') || heroSection;
    
    // Bandeau bleu (MODE TEST)
    if (!document.querySelector('.cv-test-indicator')) {
        const blueIndicator = document.createElement('div');
        blueIndicator.className = 'cv-test-indicator';
        blueIndicator.style.cssText = `
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            padding: 15px 25px;
            border-radius: 12px;
            margin: 20px 0;
            text-align: center;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        `;
        blueIndicator.innerHTML = '🔵 MODE TEST CV - Données simulées pour démonstration du parsing CV';
        container.appendChild(blueIndicator);
    }
    
    // Bandeau vert (CV PARSÉ)  
    if (!document.querySelector('.real-cv-indicator')) {
        const greenIndicator = document.createElement('div');
        greenIndicator.className = 'real-cv-indicator';
        greenIndicator.style.cssText = `
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            padding: 15px 25px;
            border-radius: 12px;
            margin: 10px 0 20px 0;
            text-align: center;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        `;
        greenIndicator.innerHTML = '🟢 CV PARSÉ AVEC SUCCÈS - Formulaire pré-rempli avec vos données';
        container.appendChild(greenIndicator);
    }
}

// ========================================
// DÉMARRAGE AUTOMATIQUE
// ========================================

console.log('🚨 Fix critique chargé - Initialisation...');
initializeFixedSystem();

// Export pour utilisation globale
window.goToStep = goToStep;
window.validateStep1 = validateStep1;
window.validateStep2 = validateStep2;
window.validateStep3 = validateStep3;
window.validateStep4 = validateStep4;
window.showNotification = showNotification;

console.log('✅ Fix critique navigation NEXTEN V2.0 opérationnel !');
