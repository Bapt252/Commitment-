/**
 * CORRECTION CRITIQUE : Fix validation étape 3 - Motivations professionnelles
 * Problème: Conflit entre deux systèmes de gestion des motivations
 * Solution: Synchronisation et validation corrigée
 */

console.log('🔧 Chargement correction validation étape 3...');

// Fonction de correction de la validation
function fixStep3Validation() {
    console.log('🎯 Application du fix validation étape 3...');

    // 1. Corriger la méthode validateStep dans NextenQuestionnaire
    if (window.nextenQuestionnaire && window.nextenQuestionnaire.validateStep) {
        const originalValidateStep = window.nextenQuestionnaire.validateStep.bind(window.nextenQuestionnaire);
        
        window.nextenQuestionnaire.validateStep = function(step) {
            if (step === 3) {
                console.log('🔍 Validation étape 3 avec fix appliqué...');
                
                // Vérifier les motivations via le système motivationSystem
                const motivationSystemExists = window.motivationSystem && window.motivationSystem.selectedMotivations;
                const selectedMotivations = motivationSystemExists ? window.motivationSystem.selectedMotivations : [];
                
                console.log('📊 Motivations détectées:', selectedMotivations);
                
                if (selectedMotivations.length === 0) {
                    this.showNotification('Veuillez sélectionner au moins une motivation professionnelle', 'warning');
                    console.log('❌ Validation échouée: aucune motivation sélectionnée');
                    return false;
                }
                
                // Synchroniser avec this.selectedMotivations pour éviter les conflits futurs
                this.selectedMotivations = [...selectedMotivations];
                
                console.log('✅ Validation étape 3 réussie');
                return true;
            }
            
            // Utiliser la validation originale pour les autres étapes
            return originalValidateStep(step);
        };
        
        console.log('✅ Méthode validateStep corrigée');
    }

    // 2. Ajouter une validation alternative sur le bouton Continuer
    const nextStep3Button = document.getElementById('next-step3');
    if (nextStep3Button) {
        // Supprimer les anciens listeners pour éviter les doublons
        const newButton = nextStep3Button.cloneNode(true);
        nextStep3Button.parentNode.replaceChild(newButton, nextStep3Button);
        
        // Ajouter le nouveau listener corrigé
        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            console.log('🚀 Clic sur Continuer étape 3 avec validation corrigée...');
            
            // Validation directe des motivations
            const motivationSystemExists = window.motivationSystem && window.motivationSystem.selectedMotivations;
            const selectedMotivations = motivationSystemExists ? window.motivationSystem.selectedMotivations : [];
            
            console.log('📊 Validation motivations:', {
                systemExists: motivationSystemExists,
                selectedCount: selectedMotivations.length,
                motivations: selectedMotivations
            });
            
            if (selectedMotivations.length === 0) {
                showValidationError('Veuillez sélectionner au moins une motivation professionnelle');
                return false;
            }
            
            // Vérification optionnelle des secteurs (non bloquante)
            const sectorsSystemExists = window.sectorsSystem && window.sectorsSystem.selectedSectors;
            const selectedSectors = sectorsSystemExists ? window.sectorsSystem.selectedSectors : [];
            console.log('🏭 Secteurs sélectionnés:', selectedSectors.length);
            
            // Vérification optionnelle de la fourchette salariale (non bloquante)
            const salarySystemExists = window.salarySystem;
            if (salarySystemExists) {
                console.log('💰 Fourchette salariale:', `${window.salarySystem.min}K - ${window.salarySystem.max}K`);
            }
            
            // Si tout est valide, naviguer vers l'étape 4
            console.log('✅ Toutes les validations sont passées, navigation vers étape 4');
            
            if (window.nextenQuestionnaire && window.nextenQuestionnaire.goToStep) {
                window.nextenQuestionnaire.goToStep(4);
            } else {
                // Fallback manuel
                document.querySelectorAll('.form-step').forEach(step => {
                    step.style.display = 'none';
                    step.classList.remove('active');
                });
                
                const step4 = document.getElementById('form-step4');
                if (step4) {
                    step4.style.display = 'block';
                    step4.classList.add('active');
                    step4.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    console.log('✅ Navigation manuelle vers étape 4 réussie');
                } else {
                    console.error('❌ Impossible de trouver l\'étape 4');
                }
            }
        });
        
        console.log('✅ Event listener corrigé ajouté au bouton Continuer');
    }

    // 3. Mise à jour des indicateurs d'étapes
    updateStepIndicators(4);
}

// Fonction d'affichage d'erreur de validation
function showValidationError(message) {
    console.log('⚠️ Erreur de validation:', message);
    
    // Supprimer les anciens messages d'erreur
    document.querySelectorAll('.step3-validation-error').forEach(error => error.remove());
    
    // Créer le message d'erreur
    const errorDiv = document.createElement('div');
    errorDiv.className = 'step3-validation-error';
    errorDiv.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 20px 30px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 10000;
        text-align: center;
        max-width: 400px;
        animation: errorPulse 0.5s ease-in-out;
    `;
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle" style="margin-right: 10px; font-size: 18px;"></i>
        <div>${message}</div>
        <div style="margin-top: 10px; font-size: 14px; opacity: 0.9;">
            Sélectionnez vos motivations pour continuer
        </div>
    `;
    
    // Ajouter l'animation CSS
    if (!document.getElementById('step3-error-styles')) {
        const style = document.createElement('style');
        style.id = 'step3-error-styles';
        style.textContent = `
            @keyframes errorPulse {
                0% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
                50% { transform: translate(-50%, -50%) scale(1.05); }
                100% { opacity: 1; transform: translate(-50%, -50%) scale(1); }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(errorDiv);
    
    // Supprimer automatiquement après 4 secondes
    setTimeout(() => {
        errorDiv.style.opacity = '0';
        errorDiv.style.transform = 'translate(-50%, -50%) scale(0.8)';
        setTimeout(() => errorDiv.remove(), 300);
    }, 4000);
    
    // Scroller vers les motivations pour aider l'utilisateur
    const motivationContainer = document.querySelector('.motivation-ranking-container');
    if (motivationContainer) {
        motivationContainer.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
        
        // Ajouter un effet visuel temporaire
        motivationContainer.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.5)';
        setTimeout(() => {
            motivationContainer.style.boxShadow = '';
        }, 2000);
    }
}

// Fonction de mise à jour des indicateurs d'étapes
function updateStepIndicators(currentStep) {
    try {
        document.querySelectorAll('.step').forEach((step, index) => {
            const stepNum = index + 1;
            step.classList.remove('active', 'completed');
            
            if (stepNum < currentStep) {
                step.classList.add('completed');
            } else if (stepNum === currentStep) {
                step.classList.add('active');
            }
        });

        // Mise à jour de la barre de progression
        const progress = ((currentStep - 1) / 3) * 100; // 4 étapes au total
        const progressBar = document.getElementById('stepper-progress');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
        
        console.log(`📊 Indicateurs mis à jour pour l'étape ${currentStep}`);
    } catch (error) {
        console.error('❌ Erreur mise à jour indicateurs:', error);
    }
}

// Fonction d'initialisation avec vérifications multiples
function initializeStep3Fix() {
    console.log('🚀 Initialisation du fix étape 3...');
    
    // Vérifier que les éléments nécessaires sont présents
    const checkAndApplyFix = () => {
        const nextButton = document.getElementById('next-step3');
        const motivationCards = document.querySelectorAll('.motivation-card');
        
        if (nextButton && motivationCards.length > 0) {
            fixStep3Validation();
            console.log('✅ Fix étape 3 appliqué avec succès');
            return true;
        } else {
            console.log('⏳ Éléments pas encore disponibles, nouvelle tentative...');
            return false;
        }
    };
    
    // Tentatives multiples d'initialisation
    if (!checkAndApplyFix()) {
        setTimeout(() => {
            if (!checkAndApplyFix()) {
                setTimeout(() => {
                    if (!checkAndApplyFix()) {
                        console.warn('⚠️ Fix étape 3 non appliqué après plusieurs tentatives');
                    }
                }, 1000);
            }
        }, 500);
    }
}

// Démarrage automatique
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initializeStep3Fix, 300);
    });
} else {
    setTimeout(initializeStep3Fix, 100);
}

// Fallback d'urgence pour les cas où le fix n'est pas appliqué
setTimeout(() => {
    const nextButton = document.getElementById('next-step3');
    if (nextButton && !nextButton.hasAttribute('data-fix-applied')) {
        console.log('🆘 Application du fallback d\'urgence...');
        initializeStep3Fix();
    }
}, 2000);

console.log('✅ Script de correction validation étape 3 chargé');
