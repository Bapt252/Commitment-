// ===== 🎯 CORRECTION CRITIQUE ÉTAPE 3 - SYNCHRONISATION MOTIVATIONS =====
// Fichier de correction pour synchroniser les deux systèmes de motivations
// Résout le problème "veuillez sélectionner au moins une motivation"
// Version: 1.0 - Solution définitive

console.log('🎯 Chargement correction synchronisation motivations étape 3...');

// ===== SOLUTION : SYNCHRONISATION DES DEUX SYSTÈMES =====
window.motivationSyncFix = {
    init() {
        console.log('🔧 Initialisation correction synchronisation motivations...');
        
        // Attendre que les deux systèmes soient chargés
        this.waitForSystems(() => {
            this.setupSynchronization();
            this.fixValidationStep3();
            console.log('✅ Correction synchronisation motivations appliquée');
        });
    },
    
    waitForSystems(callback) {
        const checkSystems = () => {
            if (window.motivationSystem && window.nextenQuestionnaire) {
                callback();
            } else {
                console.log('⏳ Attente chargement des systèmes...');
                setTimeout(checkSystems, 200);
            }
        };
        checkSystems();
    },
    
    setupSynchronization() {
        // 🔧 FIX: Override de la méthode updateDisplay pour synchroniser
        const originalUpdateDisplay = window.motivationSystem.updateDisplay;
        window.motivationSystem.updateDisplay = function() {
            // Appeler la méthode originale
            originalUpdateDisplay.call(this);
            
            // 🎯 SYNCHRONISATION: Mettre à jour nextenQuestionnaire.selectedMotivations
            if (window.nextenQuestionnaire) {
                window.nextenQuestionnaire.selectedMotivations = [...this.selectedMotivations];
                console.log('🔄 Motivations synchronisées:', window.nextenQuestionnaire.selectedMotivations);
            }
        };
        
        // 🔧 FIX: Override de la méthode addMotivation pour synchroniser
        const originalAddMotivation = window.motivationSystem.addMotivation;
        window.motivationSystem.addMotivation = function(motivation) {
            originalAddMotivation.call(this, motivation);
            
            // Synchronisation immédiate
            if (window.nextenQuestionnaire) {
                window.nextenQuestionnaire.selectedMotivations = [...this.selectedMotivations];
                console.log('➕ Motivation ajoutée et synchronisée:', motivation);
            }
        };
        
        // 🔧 FIX: Override de la méthode removeMotivation pour synchroniser
        const originalRemoveMotivation = window.motivationSystem.removeMotivation;
        window.motivationSystem.removeMotivation = function(motivation) {
            originalRemoveMotivation.call(this, motivation);
            
            // Synchronisation immédiate
            if (window.nextenQuestionnaire) {
                window.nextenQuestionnaire.selectedMotivations = [...this.selectedMotivations];
                console.log('➖ Motivation retirée et synchronisée:', motivation);
            }
        };
        
        console.log('🔗 Synchronisation configurée entre les deux systèmes');
    },
    
    fixValidationStep3() {
        if (!window.nextenQuestionnaire) {
            console.warn('⚠️ nextenQuestionnaire non disponible pour la correction');
            return;
        }
        
        // 🎯 FIX CRITIQUE: Override de la méthode validateStep pour l'étape 3
        const originalValidateStep = window.nextenQuestionnaire.validateStep;
        window.nextenQuestionnaire.validateStep = function(step) {
            if (step === 3) {
                // 🔧 CORRECTION: Vérifier dans window.motivationSystem au lieu de this.selectedMotivations
                const actualSelectedMotivations = window.motivationSystem ? 
                    window.motivationSystem.selectedMotivations : 
                    this.selectedMotivations;
                
                console.log('🔍 Validation étape 3 - Motivations trouvées:', actualSelectedMotivations);
                
                if (!actualSelectedMotivations || actualSelectedMotivations.length === 0) {
                    this.showNotification('Veuillez sélectionner au moins une motivation', 'warning');
                    return false;
                }
                
                // 🎯 SYNCHRONISATION FINALE: S'assurer que les deux systèmes sont alignés
                this.selectedMotivations = [...actualSelectedMotivations];
                
                console.log('✅ Validation étape 3 réussie - Motivations validées:', actualSelectedMotivations);
                return true;
            }
            
            // Pour les autres étapes, utiliser la validation originale
            return originalValidateStep.call(this, step);
        };
        
        console.log('🎯 Correction validation étape 3 appliquée');
    },
    
    // 🚀 MÉTHODE DE TEST
    testSynchronization() {
        console.log('🧪 Test de synchronisation des motivations:');
        console.log('- motivationSystem.selectedMotivations:', window.motivationSystem?.selectedMotivations);
        console.log('- nextenQuestionnaire.selectedMotivations:', window.nextenQuestionnaire?.selectedMotivations);
        
        const isSync = JSON.stringify(window.motivationSystem?.selectedMotivations) === 
                      JSON.stringify(window.nextenQuestionnaire?.selectedMotivations);
        
        console.log(isSync ? '✅ Systèmes synchronisés' : '❌ Systèmes désynchronisés');
        return isSync;
    },
    
    // 🔄 MÉTHODE DE FORCE-SYNC D'URGENCE
    forceSynchronization() {
        if (window.motivationSystem && window.nextenQuestionnaire) {
            window.nextenQuestionnaire.selectedMotivations = [...window.motivationSystem.selectedMotivations];
            console.log('🔄 Force-synchronisation effectuée');
            return true;
        }
        return false;
    }
};

// ===== 🚀 CORRECTION SUPPLÉMENTAIRE : BOUTON CONTINUER ÉTAPE 3 =====
window.fixStep3Navigation = {
    init() {
        console.log('🔗 Correction navigation étape 3...');
        
        // Attendre que le bouton soit disponible
        const setupButton = () => {
            const nextStep3Button = document.getElementById('next-step3');
            if (nextStep3Button) {
                // Supprimer les anciens événements
                const newButton = nextStep3Button.cloneNode(true);
                nextStep3Button.parentNode.replaceChild(newButton, nextStep3Button);
                
                // Ajouter le nouvel événement corrigé
                newButton.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log('🎯 Clic sur Continuer étape 3 - Vérification motivations...');
                    
                    // 🔧 VALIDATION CORRIGÉE
                    const motivations = window.motivationSystem?.selectedMotivations || [];
                    console.log('🔍 Motivations trouvées:', motivations);
                    
                    if (motivations.length === 0) {
                        console.warn('⚠️ Aucune motivation sélectionnée');
                        
                        // Notification améliorée
                        this.showEnhancedWarning();
                        return false;
                    }
                    
                    // 🚀 NAVIGATION VERS ÉTAPE 4
                    console.log('✅ Validation OK - Navigation vers étape 4');
                    
                    // Force la synchronisation avant navigation
                    window.motivationSyncFix.forceSynchronization();
                    
                    // Navigation
                    if (window.nextenQuestionnaire && typeof window.nextenQuestionnaire.goToStep === 'function') {
                        window.nextenQuestionnaire.goToStep(4);
                    } else {
                        // Fallback navigation directe
                        this.navigateToStep4Fallback();
                    }
                });
                
                console.log('✅ Bouton Continuer étape 3 corrigé');
            } else {
                console.log('⏳ Bouton next-step3 non trouvé, retry...');
                setTimeout(setupButton, 300);
            }
        };
        
        setupButton();
    },
    
    showEnhancedWarning() {
        // Supprimer les anciennes notifications
        document.querySelectorAll('.motivation-warning').forEach(w => w.remove());
        
        const warning = document.createElement('div');
        warning.className = 'motivation-warning';
        warning.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            padding: 24px 32px;
            border-radius: 16px;
            font-weight: 600;
            font-size: 16px;
            z-index: 10000;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            text-align: center;
            animation: shake 0.5s ease-in-out;
        `;
        
        warning.innerHTML = `
            <div style="margin-bottom: 12px;">
                <i class="fas fa-exclamation-triangle" style="font-size: 24px;"></i>
            </div>
            <div style="font-size: 18px; margin-bottom: 8px;">Action requise</div>
            <div style="font-size: 14px; opacity: 0.9;">
                Veuillez sélectionner au moins une motivation professionnelle pour continuer
            </div>
        `;
        
        document.body.appendChild(warning);
        
        // Auto-remove
        setTimeout(() => warning.remove(), 4000);
        
        // Scroll vers les motivations
        const motivationContainer = document.querySelector('.motivation-ranking-container');
        if (motivationContainer) {
            motivationContainer.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
            
            // Effet de surbrillance
            motivationContainer.style.boxShadow = '0 0 20px rgba(245, 158, 11, 0.5)';
            setTimeout(() => {
                motivationContainer.style.boxShadow = '';
            }, 3000);
        }
    },
    
    navigateToStep4Fallback() {
        console.log('🔄 Navigation fallback vers étape 4...');
        
        // Masquer étape 3
        const step3 = document.getElementById('form-step3');
        if (step3) {
            step3.style.display = 'none';
            step3.classList.remove('active');
        }
        
        // Afficher étape 4
        const step4 = document.getElementById('form-step4');
        if (step4) {
            step4.style.display = 'block';
            step4.classList.add('active');
            
            // Scroll vers l'étape 4
            setTimeout(() => {
                step4.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);
            
            console.log('✅ Navigation fallback réussie vers étape 4');
        } else {
            console.error('❌ Étape 4 non trouvée');
        }
        
        // Mettre à jour l'indicateur d'étape si possible
        this.updateStepIndicatorFallback(4);
    },
    
    updateStepIndicatorFallback(currentStep) {
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
        const progress = ((currentStep - 1) / 3) * 100; // 4 étapes total
        const progressBar = document.getElementById('stepper-progress');
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }
};

// ===== 🚀 INITIALISATION AUTOMATIQUE =====
function initializeMotivationFix() {
    console.log('🎯 Initialisation correction motivations étape 3...');
    
    // Initialiser la synchronisation
    window.motivationSyncFix.init();
    
    // Initialiser la correction navigation
    window.fixStep3Navigation.init();
    
    // Test périodique (optionnel, pour debug)
    if (window.location.search.includes('debug=1')) {
        setInterval(() => {
            window.motivationSyncFix.testSynchronization();
        }, 5000);
    }
    
    console.log('✅ Correction motivations étape 3 initialisée');
}

// Démarrage automatique
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initializeMotivationFix, 300);
    });
} else {
    setTimeout(initializeMotivationFix, 100);
}

// Style pour l'animation shake
if (!document.querySelector('#shake-animation-style')) {
    const style = document.createElement('style');
    style.id = 'shake-animation-style';
    style.textContent = `
        @keyframes shake {
            0%, 100% { transform: translate(-50%, -50%) translateX(0); }
            25% { transform: translate(-50%, -50%) translateX(-5px); }
            75% { transform: translate(-50%, -50%) translateX(5px); }
        }
    `;
    document.head.appendChild(style);
}

console.log('✅ Correction critique étape 3 - Synchronisation motivations chargée');
