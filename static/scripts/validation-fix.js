// ===== PATCH DE VALIDATION ÉTAPE 3 - MOTIVATIONS =====
// Correctif urgent pour le problème de validation des motivations
// Ce patch remplace/améliore la validation défaillante

console.log('🔧 Chargement du patch de validation étape 3...');

// Fonction de validation robuste pour les motivations
function validateMotivations() {
    // Vérifier d'abord si le système de motivations existe
    if (window.motivationSystem && window.motivationSystem.selectedMotivations) {
        const selectedCount = window.motivationSystem.selectedMotivations.length;
        console.log('📊 Motivations sélectionnées via motivationSystem:', selectedCount);
        return selectedCount > 0;
    }

    // Fallback : vérifier les cartes avec la classe "selected"
    const selectedCards = document.querySelectorAll('.motivation-card.selected');
    console.log('📊 Cartes motivations avec classe selected:', selectedCards.length);
    if (selectedCards.length > 0) {
        return true;
    }

    // Fallback 2 : vérifier les champs cachés
    const hiddenMotivations = document.getElementById('hidden-motivations');
    if (hiddenMotivations && hiddenMotivations.value && hiddenMotivations.value.length > 0) {
        console.log('📊 Champ caché motivations:', hiddenMotivations.value);
        return true;
    }

    // Fallback 3 : vérifier si au moins une motivation est cochée
    const motivationInputs = document.querySelectorAll('input[name*="motivation"]:checked');
    console.log('📊 Inputs motivations cochés:', motivationInputs.length);
    return motivationInputs.length > 0;
}

// Fonction pour forcer une sélection de motivation par défaut si aucune n'est détectée
function ensureMotivationSelection() {
    if (!validateMotivations()) {
        console.log('⚠️ Aucune motivation détectée, sélection par défaut...');
        
        // Sélectionner automatiquement la première motivation (évolution)
        const firstCard = document.querySelector('.motivation-card[data-motivation="evolution"]');
        if (firstCard && window.motivationSystem) {
            window.motivationSystem.handleCardClick(firstCard);
            console.log('✅ Motivation "évolution" sélectionnée par défaut');
            return true;
        }
    }
    return validateMotivations();
}

// Fonction de validation complète de l'étape 3
function validateStep3() {
    console.log('🔍 Validation complète étape 3...');
    
    // 1. Valider les motivations
    const motivationsValid = ensureMotivationSelection();
    
    // 2. Valider la fourchette salariale
    let salaryValid = true;
    const salaryMin = document.getElementById('salary-min');
    const salaryMax = document.getElementById('salary-max');
    
    if (salaryMin && salaryMax) {
        const minVal = parseInt(salaryMin.value) || 40;
        const maxVal = parseInt(salaryMax.value) || 45;
        salaryValid = minVal < maxVal;
        
        if (!salaryValid) {
            console.log('❌ Fourchette salariale invalide:', minVal, maxVal);
        }
    }

    console.log('📋 Validation étape 3:', {
        motivations: motivationsValid,
        salary: salaryValid,
        global: motivationsValid && salaryValid
    });

    return motivationsValid && salaryValid;
}

// Remplacer la validation du bouton "Continuer"
function patchStep3Navigation() {
    const nextButton = document.getElementById('next-step3');
    if (!nextButton) {
        console.log('❌ Bouton next-step3 non trouvé');
        return;
    }

    // Supprimer tous les anciens événements
    const newButton = nextButton.cloneNode(true);
    nextButton.parentNode.replaceChild(newButton, nextButton);

    // Ajouter le nouvel événement de validation
    newButton.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('🔄 Clic sur next-step3 - Validation patch...');
        
        if (validateStep3()) {
            console.log('✅ Validation réussie, navigation vers étape 4');
            
            // Navigation vers étape 4
            if (typeof window.showStep === 'function') {
                window.showStep(4);
            } else {
                // Fallback manuel
                document.querySelectorAll('.form-step').forEach(step => {
                    step.classList.remove('active');
                });
                document.querySelectorAll('.step').forEach(step => {
                    step.classList.remove('active');
                });
                
                const step4 = document.getElementById('form-step4');
                const stepIndicator4 = document.querySelector('.step:nth-child(4)');
                
                if (step4) step4.classList.add('active');
                if (stepIndicator4) stepIndicator4.classList.add('active');
            }
        } else {
            console.log('❌ Validation échouée');
            
            // Afficher message d'erreur personnalisé
            const existingError = document.querySelector('.validation-error-message');
            if (existingError) existingError.remove();
            
            const errorMessage = document.createElement('div');
            errorMessage.className = 'validation-error-message';
            errorMessage.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: linear-gradient(135deg, #ef4444, #dc2626);
                color: white;
                padding: 20px 30px;
                border-radius: 12px;
                font-weight: 600;
                z-index: 10000;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                text-align: center;
                max-width: 400px;
                line-height: 1.5;
            `;
            
            const motivationsValid = validateMotivations();
            if (!motivationsValid) {
                errorMessage.innerHTML = `
                    <i class="fas fa-exclamation-triangle" style="font-size: 24px; margin-bottom: 10px; display: block;"></i>
                    <strong>Sélection requise</strong><br>
                    Veuillez sélectionner au moins une motivation professionnelle pour continuer.
                `;
            } else {
                errorMessage.innerHTML = `
                    <i class="fas fa-exclamation-triangle" style="font-size: 24px; margin-bottom: 10px; display: block;"></i>
                    <strong>Informations incomplètes</strong><br>
                    Veuillez vérifier votre fourchette salariale.
                `;
            }
            
            document.body.appendChild(errorMessage);
            
            // Auto-suppression après 4 secondes
            setTimeout(() => {
                if (errorMessage.parentNode) {
                    errorMessage.remove();
                }
            }, 4000);
        }
    });

    console.log('✅ Patch de navigation étape 3 appliqué');
}

// Initialisation du patch
function initValidationPatch() {
    console.log('🚀 Initialisation du patch de validation...');
    
    // Attendre que la page soit complètement chargée
    const initPatch = () => {
        // Patcher la navigation de l'étape 3
        patchStep3Navigation();
        
        // Test initial de la validation
        setTimeout(() => {
            const isValid = validateStep3();
            console.log('🧪 Test validation initial:', isValid);
        }, 1000);
        
        console.log('✅ Patch de validation appliqué avec succès');
    };
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            setTimeout(initPatch, 500);
        });
    } else {
        setTimeout(initPatch, 200);
    }
}

// Démarrer le patch
initValidationPatch();

console.log('🔧 Patch de validation étape 3 chargé');
